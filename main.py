import sys
import math
import random
import pygame
from typing import List, Tuple

# ============ Konfigurasi Utama ============
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 25  # 32 kolom x 24 baris -> 800x600 tepat
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE  # 32 x 24

# Warna
BLACK = (0, 0, 0)
NAVY = (10, 10, 40)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
PINK = (255, 105, 180)
RED = (255, 60, 60)
ORANGE = (255, 165, 0)
CYAN = (100, 200, 255)  # frightened color
GREY = (180, 180, 180)

# Skor
DOT_SCORE = 10
POWER_SCORE = 50
GHOST_SCORE = 200

# Durasi frightened (detik)
FRIGHTENED_DURATION = 6.0

# Kecepatan
PACMAN_SPEED = 3  # px/frame
GHOST_SPEED = 2.5
FRIGHTENED_SPEED = 1.8

# Tile codes: '1'=wall, '0'=path, '2'=dot, '3'=power pellet, '4'=ghost house gate, '5'=empty path (no pellets)
# Ukuran map 24 baris x 32 kolom
MAZE_LAYOUT = [
    "11111111111111111111111111111111",
    "12222222222211112222222222222221",
    "12111121111211112111121111211121",
    "13111121111211112111121111211131",
    "12000020000200002000020000200021",
    "12111121111211112111121111211121",
    "12222222222222222222222222222221",
    "12111121111111111111111121111121",
    "12222222222241114222222222222221",
    "11111121111111111111111121111111",
    "50000020000000000000000020000005",
    "11111121111115551111111121111111",
    "12222222222215551222222222222221",
    "12111121111211112111121111211121",
    "12000020000200002000020000200021",
    "12111121111211112111121111211121",
    "12222222222241114222222222222221",
    "12111121111111111111111121111121",
    "12222222222222222222222222222221",
    "12111121111211112111121111211121",
    "13000020000200002000020000200031",
    "12111121111211112111121111211121",
    "12222222222211112222222222222221",
    "11111111111111111111111111111111",
]

# Validasi dimensi
assert len(MAZE_LAYOUT) == ROWS, f"Rows must be {ROWS}"
for r in MAZE_LAYOUT:
    assert len(r) == COLS, f"Cols must be {COLS}"


def grid_to_px(col: int, row: int) -> Tuple[int, int]:
    return col * TILE_SIZE, row * TILE_SIZE


def center_in_tile(col: int, row: int) -> Tuple[int, int]:
    x, y = grid_to_px(col, row)
    return x + TILE_SIZE // 2, y + TILE_SIZE // 2


class Maze:
    def __init__(self, layout: List[str]):
        self.layout = [list(row) for row in layout]
        # Hitung total dot + power untuk kondisi menang
        self.total_pellets = sum(row.count('2') + row.count('3') for row in layout)
        # Cari posisi gate (tile '4') dan area rumah hantu (tile '5' sekitar tengah)
        self.ghost_house_tiles = []
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == '5':
                    self.ghost_house_tiles.append((x, y))

    def is_wall(self, col: int, row: int) -> bool:
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return True
        return self.layout[row][col] == '1'

    def is_gate(self, col: int, row: int) -> bool:
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return False
        return self.layout[row][col] == '4'

    def pellet_at(self, col: int, row: int) -> str:
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return '0'
        return self.layout[row][col]

    def eat_pellet(self, col: int, row: int) -> Tuple[int, bool]:
        # returns (score_gain, power_trigger)
        ch = self.pellet_at(col, row)
        if ch == '2':
            self.layout[row][col] = '0'
            self.total_pellets -= 1
            return DOT_SCORE, False
        elif ch == '3':
            self.layout[row][col] = '0'
            self.total_pellets -= 1
            return POWER_SCORE, True
        return 0, False

    def draw(self, surf: pygame.Surface):
        for row in range(ROWS):
            for col in range(COLS):
                ch = self.layout[row][col]
                x, y = grid_to_px(col, row)
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                if ch == '1':
                    pygame.draw.rect(surf, BLUE, rect)
                else:
                    # background path
                    pygame.draw.rect(surf, NAVY, rect)
                    # draw pellets
                    if ch == '2':
                        pygame.draw.circle(surf, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 3)
                    elif ch == '3':
                        pygame.draw.circle(surf, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 6)
                # gate as grey bar
                if ch == '4':
                    pygame.draw.rect(surf, GREY, (x + 3, y + TILE_SIZE // 2 - 2, TILE_SIZE - 6, 4))


class Entity:
    def __init__(self, col: int, row: int, color: Tuple[int, int, int], speed: float):
        self.x, self.y = center_in_tile(col, row)
        self.color = color
        self.speed = speed
        self.dir = pygame.Vector2(0, 0)
        self.next_dir = pygame.Vector2(0, 0)
        self.radius = TILE_SIZE // 2 - 2

    @property
    def col_row(self) -> Tuple[int, int]:
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def aligned_to_grid(self) -> bool:
        cx = (self.x - TILE_SIZE // 2) % TILE_SIZE
        cy = (self.y - TILE_SIZE // 2) % TILE_SIZE
        return abs(cx) < 1e-3 and abs(cy) < 1e-3

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def try_set_direction(self, maze: Maze, dx: int, dy: int):
        self.next_dir = pygame.Vector2(dx, dy)

    def can_move(self, maze: Maze, dx: int, dy: int) -> bool:
        # prediksi posisi center setelah gerak kecil
        nx = self.x + dx
        ny = self.y + dy
        # cek tile depan berdasarkan arah
        target_col = int(nx // TILE_SIZE)
        target_row = int(ny // TILE_SIZE)
        # cek empat titik di rect agar tidak tembus dinding
        half = self.radius - 2
        corners = [
            (nx - half, ny - half),
            (nx + half, ny - half),
            (nx - half, ny + half),
            (nx + half, ny + half),
        ]
        for px, py in corners:
            c = int(px // TILE_SIZE)
            r = int(py // TILE_SIZE)
            if maze.is_wall(c, r):
                return False
            if maze.is_gate(c, r):
                # Gate hanya boleh dilalui hantu dari dalam ke luar, Pacman tidak boleh
                # Default: entitas umum tidak boleh melewati gate
                return False
        # Tunnel wrap kiri/kanan
        if target_col < 0:
            nx = (COLS - 1) * TILE_SIZE + TILE_SIZE // 2
        elif target_col >= COLS:
            nx = TILE_SIZE // 2
        self.x, self.y = nx, ny
        return True

    def update_move(self, maze: Maze):
        # Coba apply next_dir ketika align grid
        if self.next_dir.length_squared() > 0 and self.aligned_to_grid():
            dx = int(self.next_dir.x)
            dy = int(self.next_dir.y)
            # Uji maju sedikit tanpa komit
            ox, oy = self.x, self.y
            if self._can_move_peek(maze, dx, dy):
                self.dir = self.next_dir
            self.x, self.y = ox, oy
        # Gerak sesuai dir
        if self.dir.length_squared() > 0:
            move_x = self.dir.x * self.speed
            move_y = self.dir.y * self.speed
            # coba langkah kecil terpisah untuk akurasi
            steps = int(max(abs(move_x), abs(move_y))) + 1
            if steps <= 0:
                return
            sx = move_x / steps
            sy = move_y / steps
            for _ in range(steps):
                if not self._step(maze, sx, sy):
                    break

    def _can_move_peek(self, maze: Maze, dx: int, dy: int) -> bool:
        nx = self.x + dx
        ny = self.y + dy
        half = self.radius - 2
        corners = [
            (nx - half, ny - half),
            (nx + half, ny - half),
            (nx - half, ny + half),
            (nx + half, ny + half),
        ]
        for px, py in corners:
            c = int(px // TILE_SIZE)
            r = int(py // TILE_SIZE)
            if maze.is_wall(c, r) or maze.is_gate(c, r):
                return False
        return True

    def _step(self, maze: Maze, sx: float, sy: float) -> bool:
        nx = self.x + sx
        ny = self.y + sy
        half = self.radius - 2
        corners = [
            (nx - half, ny - half),
            (nx + half, ny - half),
            (nx - half, ny + half),
            (nx + half, ny + half),
        ]
        for px, py in corners:
            c = int(px // TILE_SIZE)
            r = int(py // TILE_SIZE)
            if maze.is_wall(c, r) or maze.is_gate(c, r):
                return False
        # Warp horizontal
        col = int(nx // TILE_SIZE)
        if col < 0:
            nx = (COLS - 1) * TILE_SIZE + TILE_SIZE // 2
        elif col >= COLS:
            nx = TILE_SIZE // 2
        self.x, self.y = nx, ny
        return True

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


class Pacman(Entity):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, YELLOW, PACMAN_SPEED)
        self.mouth_angle = 0
        self.mouth_opening = True

    def draw(self, surf: pygame.Surface):
        # Animasi mulut sederhana
        self.mouth_angle += 0.2 if self.mouth_opening else -0.2
        if self.mouth_angle > 0.6:
            self.mouth_opening = False
        if self.mouth_angle < 0.05:
            self.mouth_opening = True
        angle = self.mouth_angle
        direction_angle = 0
        if self.dir.x > 0:
            direction_angle = 0
        elif self.dir.x < 0:
            direction_angle = math.pi
        elif self.dir.y < 0:
            direction_angle = -math.pi / 2
        elif self.dir.y > 0:
            direction_angle = math.pi / 2
        # Gambar bentuk pacman (pie)
        center = (int(self.x), int(self.y))
        radius = self.radius
        # Gunakan polygon untuk mulut terbuka
        mouth_dir1 = (math.cos(direction_angle + angle) * radius, math.sin(direction_angle + angle) * radius)
        mouth_dir2 = (math.cos(direction_angle - angle) * radius, math.sin(direction_angle - angle) * radius)
        points = [center,
                  (center[0] + mouth_dir1[0], center[1] + mouth_dir1[1]),
                  (center[0] + math.cos(direction_angle) * radius, center[1] + math.sin(direction_angle) * radius),
                  (center[0] + mouth_dir2[0], center[1] + mouth_dir2[1])]
        pygame.draw.circle(surf, self.color, center, radius)
        pygame.draw.polygon(surf, NAVY, points)


class Ghost(Entity):
    def __init__(self, col: int, row: int, color: Tuple[int, int, int], name: str):
        super().__init__(col, row, color, GHOST_SPEED)
        self.base_color = color
        self.name = name
        self.frightened = False
        self.frightened_timer = 0.0
        self.in_house = False

    def set_frightened(self):
        self.frightened = True
        self.frightened_timer = FRIGHTENED_DURATION
        self.color = CYAN
        self.speed = FRIGHTENED_SPEED

    def leave_house_if_possible(self, maze: Maze):
        # Coba keluar melalui gate '4' dari dalam rumah (tile '5')
        if not self.in_house:
            return
        c, r = self.col_row
        # Cari arah atas/bawah ke gate terdekat
        choices = []
        for dx, dy in [(0, -1), (1, 0), (-1, 0), (0, 1)]:
            nc, nr = c + dx, r + dy
            if 0 <= nc < COLS and 0 <= nr < ROWS:
                if maze.layout[nr][nc] in ('0', '2', '3', '4'):
                    choices.append((dx, dy))
        if choices:
            self.dir = pygame.Vector2(random.choice(choices))

    def update_ai(self, maze: Maze, pac_pos: Tuple[float, float]):
        # Frightened timer
        if self.frightened:
            self.frightened_timer -= 1 / FPS
            if self.frightened_timer <= 0:
                self.frightened = False
                self.color = self.base_color
                self.speed = GHOST_SPEED

        # At intersection (aligned), pilih arah
        if self.aligned_to_grid():
            c, r = self.col_row
            dirs = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                # jangan balik arah langsung kecuali buntu
                if self.dir.x == -dx and self.dir.y == -dy:
                    continue
                nc, nr = c + dx, r + dy
                if 0 <= nc < COLS and 0 <= nr < ROWS:
                    tile = maze.layout[nr][nc]
                    # Hantu boleh lewat gate dari dalam rumah (5->4->jalan), tetapi tidak sebaliknya jika di luar
                    if tile in ('0', '2', '3', '5') or (tile == '4' and self.in_house):
                        dirs.append((dx, dy))
            if not dirs:
                # boleh balik arah jika tidak ada pilihan
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nc, nr = c + dx, r + dy
                    if 0 <= nc < COLS and 0 <= nr < ROWS:
                        if maze.layout[nr][nc] in ('0', '2', '3', '5', '4'):
                            dirs.append((dx, dy))

            if dirs:
                if self.frightened:
                    choice = random.choice(dirs)
                else:
                    # pilih yang mendekatkan ke pacman (manhattan)
                    px, py = pac_pos
                    best = None
                    best_dist = 1e9
                    for dx, dy in dirs:
                        nx = (c + dx) * TILE_SIZE + TILE_SIZE // 2
                        ny = (r + dy) * TILE_SIZE + TILE_SIZE // 2
                        dist = abs(px - nx) + abs(py - ny)
                        if dist < best_dist:
                            best_dist = dist
                            best = (dx, dy)
                    choice = best if best else random.choice(dirs)
                self.dir = pygame.Vector2(choice)

        # Kecepatan sesuai state
        # Pergerakan actual diupdate pada update_move

    def draw(self, surf: pygame.Surface):
        # Kepala hantu + kaki gerigi
        body_rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)
        pygame.draw.ellipse(surf, self.color, body_rect)
        base_y = int(self.y + self.radius) - 3
        step = self.radius // 2
        for i in range(-self.radius, self.radius + 1, step):
            pygame.draw.circle(surf, self.color, (int(self.x + i), base_y), step // 2)
        # Mata
        eye_offset_x = 6
        eye_offset_y = -4
        pygame.draw.circle(surf, WHITE, (int(self.x - eye_offset_x), int(self.y + eye_offset_y)), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x + eye_offset_x), int(self.y + eye_offset_y)), 4)
        pygame.draw.circle(surf, NAVY, (int(self.x - eye_offset_x), int(self.y + eye_offset_y)), 2)
        pygame.draw.circle(surf, NAVY, (int(self.x + eye_offset_x), int(self.y + eye_offset_y)), 2)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (Python/Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.bigfont = pygame.font.SysFont("arial", 48, bold=True)

        self.maze = Maze(MAZE_LAYOUT)
        # Posisi awal
        self.pacman_start = (1, 10)
        self.ghost_starts = [(15, 11), (16, 11), (15, 12), (16, 12)]
        # Buat entitas
        self.pacman = Pacman(*self.pacman_start)
        self.ghosts = [
            Ghost(*self.ghost_starts[0], RED, "Blinky"),
            Ghost(*self.ghost_starts[1], PINK, "Pinky"),
            Ghost(*self.ghost_starts[2], ORANGE, "Clyde"),
            Ghost(*self.ghost_starts[3], BLUE, "Inky"),
        ]
        # Tandai yang mulai di rumah
        for g in self.ghosts:
            c, r = g.col_row
            if self.maze.layout[r][c] == '5':
                g.in_house = True

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.power_active_timer = 0.0

    def reset_positions(self):
        self.pacman = Pacman(*self.pacman_start)
        for i, g in enumerate(self.ghosts):
            col, row = self.ghost_starts[i % len(self.ghost_starts)]
            g.x, g.y = center_in_tile(col, row)
            g.dir = pygame.Vector2(0, 0)
            g.next_dir = pygame.Vector2(0, 0)
            g.frightened = False
            g.frightened_timer = 0
            g.color = g.base_color
            g.speed = GHOST_SPEED
            g.in_house = (self.maze.layout[row][col] == '5')
        self.power_active_timer = 0

    def activate_power(self):
        self.power_active_timer = FRIGHTENED_DURATION
        for g in self.ghosts:
            g.set_frightened()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman.try_set_direction(self.maze, -1, 0)
        elif keys[pygame.K_RIGHT]:
            self.pacman.try_set_direction(self.maze, 1, 0)
        elif keys[pygame.K_UP]:
            self.pacman.try_set_direction(self.maze, 0, -1)
        elif keys[pygame.K_DOWN]:
            self.pacman.try_set_direction(self.maze, 0, 1)

    def update(self):
        if self.game_over or self.win:
            return

        self.handle_input()

        # Update Pacman movement
        self.pacman.update_move(self.maze)

        # Makan pellet
        c, r = self.pacman.col_row
        gained, power = self.maze.eat_pellet(c, r)
        if gained:
            self.score += gained
        if power:
            self.activate_power()

        # Update ghosts AI dan movement
        for g in self.ghosts:
            # biarkan ghost yang di dalam rumah keluar
            if g.in_house:
                # ketika menyentuh gate, setelah lewat bukan di-house
                g.leave_house_if_possible(self.maze)
                # cek apakah sudah keluar (tile bukan 5 dan bukan 4)
                gc, gr = g.col_row
                if self.maze.layout[gr][gc] not in ('5', '4'):
                    g.in_house = False
            g.update_ai(self.maze, (self.pacman.x, self.pacman.y))
            # Gerak hantu. Hantu boleh melewati gate jika masih di rumah.
            # Untuk memudahkan, saat move, override gate check sementara bila in_house.
            if g.in_house:
                # Temporarily allow gate pass by treating gate as non-wall in _step
                # Implement by nudging movement and manually handling collisions similar to Entity._step
                move_x = g.dir.x * g.speed
                move_y = g.dir.y * g.speed
                steps = int(max(abs(move_x), abs(move_y))) + 1
                if steps > 0:
                    sx = move_x / steps
                    sy = move_y / steps
                    for _ in range(steps):
                        nx = g.x + sx
                        ny = g.y + sy
                        half = g.radius - 2
                        corners = [
                            (nx - half, ny - half),
                            (nx + half, ny - half),
                            (nx - half, ny + half),
                            (nx + half, ny + half),
                        ]
                        blocked = False
                        for px, py in corners:
                            c2 = int(px // TILE_SIZE)
                            r2 = int(py // TILE_SIZE)
                            if self.maze.is_wall(c2, r2):
                                blocked = True
                                break
                        if blocked:
                            break
                        # Warp
                        col = int(nx // TILE_SIZE)
                        if col < 0:
                            nx = (COLS - 1) * TILE_SIZE + TILE_SIZE // 2
                        elif col >= COLS:
                            nx = TILE_SIZE // 2
                        g.x, g.y = nx, ny
                # after move, if on gate tile, keep moving; once out, in_house may turn False in next loop
            else:
                g.update_move(self.maze)

        # Cek collision pacman vs ghosts
        p_rect = self.pacman.rect()
        for g in self.ghosts:
            if p_rect.colliderect(g.rect()):
                if g.frightened:
                    # kirim ke rumah
                    self.score += GHOST_SCORE
                    # cari salah satu tile '5' jika ada, kalau tidak, pakai start
                    if self.maze.ghost_house_tiles:
                        hx, hy = random.choice(self.maze.ghost_house_tiles)
                    else:
                        hx, hy = self.ghost_starts[0]
                    g.x, g.y = center_in_tile(hx, hy)
                    g.in_house = True
                    g.frightened = False
                    g.color = g.base_color
                    g.speed = GHOST_SPEED
                    g.dir = pygame.Vector2(0, 0)
                else:
                    # Pacman mati
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_positions()
                    break

        # Menang jika semua pellets habis
        if self.maze.total_pellets <= 0:
            self.win = True

    def draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (10, 5))
        self.screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 10, 5))

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_hud()

        if self.game_over:
            txt = self.bigfont.render("GAME OVER", True, WHITE)
            self.screen.blit(txt, ((WIDTH - txt.get_width()) // 2, (HEIGHT - txt.get_height()) // 2))
            sub = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)
            self.screen.blit(sub, ((WIDTH - sub.get_width()) // 2, (HEIGHT - sub.get_height()) // 2 + 60))
        elif self.win:
            txt = self.bigfont.render("YOU WIN!", True, WHITE)
            self.screen.blit(txt, ((WIDTH - txt.get_width()) // 2, (HEIGHT - txt.get_height()) // 2))
            sub = self.font.render("Press R to Play Again or ESC to Quit", True, WHITE)
            self.screen.blit(sub, ((WIDTH - sub.get_width()) // 2, (HEIGHT - sub.get_height()) // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r and (self.game_over or self.win):
                        # Reset game penuh
                        self.__init__()

            self.update()
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
