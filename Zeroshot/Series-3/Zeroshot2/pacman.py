import pygame
import random
import math
import sys

# ==========================
# Konfigurasi Utama
# ==========================
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 20  # 40x30 grid untuk 800x600
GRID_COLS = WIDTH // TILE_SIZE  # 40
GRID_ROWS = HEIGHT // TILE_SIZE  # 30
FPS = 60

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 255)
NAVY = (0, 0, 128)
YELLOW = (255, 210, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (120, 120, 120)
VULNERABLE_COLOR = (0, 0, 255)

# Maze tile legend
# '1' = wall, '0' = path kosong, '2' = dot kecil, '3' = power pellet

# ==========================
# Maze Layout (40x30)
# ==========================
# Desain sederhana terinspirasi Pacman klasik. Jalur utama + dots dan power pellets di 4 pojok area dalam.
# Baris harus berjumlah 30, kolom 40 karakter tiap baris.
MAZE_LAYOUT = [
    "1111111111111111111111111111111111111111",
    "1222222222221111111122222222222211111121",
    "1231112111221000000122111211112011111121",
    "1201112111221111111122111211112011111121",
    "1200000000221111111122000011112000000021",
    "1211111111221111111122111111112111111121",
    "1211111110222222222222000011112000000021",
    "1211111110111111111111112011112111111121",
    "1200000110000000000000012000000120000021",
    "1111100111111111111110012111111120111121",
    "1111100111111111111110012111111120111121",
    "1200000000000000000000002000000000000021",
    "1211111111111011111111112111111111111121",
    "1200000000001010000000002000000000000021",
    "1111111111101010111111112111111111111121",
    "1000000000101010100000012000000000000021",
    "1011111110101010110111112111111111111121",
    "1030000010101010100100002000000000000021",
    "1110111110101010110101112111111111111121",
    "1200100000101000100100012000000000000021",
    "1210101111101011110111012111111111111121",
    "1200101000001000000100012000000000000021",
    "1211101011111111111101112111111111111121",
    "1200001000000000000000012000000000000321",
    "1211111111111111111111112111111111111121",
    "1200000000000002000000002000000000000021",
    "1211111111111112111111112111111111111121",
    "1222222222222222000000002000000000000021",
    "1211111111111111111111112111111111111121",
    "1111111111111111111111111111111111111111",
]

# Validasi ukuran maze
if len(MAZE_LAYOUT) != GRID_ROWS or any(len(row) != GRID_COLS for row in MAZE_LAYOUT):
    print("Maze layout size mismatch. Expected 40x30 grid of characters for 800x600 with TILE_SIZE=20.")
    sys.exit(1)

# ==========================
# Utilitas Grid
# ==========================

def grid_to_pixel(col, row):
    return col * TILE_SIZE, row * TILE_SIZE


def pixel_to_grid(x, y):
    return x // TILE_SIZE, y // TILE_SIZE


def is_wall(col, row):
    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        return MAZE_LAYOUT[row][col] == '1'
    return True


def is_path(col, row):
    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        return MAZE_LAYOUT[row][col] in ('0', '2', '3')
    return False


def is_intersection(col, row):
    # Persimpangan jika lebih dari 2 arah valid
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    count = 0
    for dx, dy in dirs:
        nc, nr = col + dx, row + dy
        if is_path(nc, nr):
            count += 1
    return count >= 3

# ==========================
# Game Entities
# ==========================
class Pacman:
    def __init__(self, start_col, start_row):
        self.start_col = start_col
        self.start_row = start_row
        self.reset()
        self.color = YELLOW
        self.radius = TILE_SIZE // 2 - 2
        self.speed = 3  # pixel per frame
        self.target_dir = (0, 0)

    def reset(self):
        self.col = self.start_col
        self.row = self.start_row
        self.x, self.y = grid_to_pixel(self.col, self.row)
        self.dir = (0, 0)
        self.target_dir = (0, 0)

    def set_direction(self, dx, dy):
        self.target_dir = (dx, dy)

    def at_cell_center(self):
        return self.x % TILE_SIZE == 0 and self.y % TILE_SIZE == 0

    def update(self):
        # Coba terapkan target_dir saat di tengah sel
        if self.at_cell_center():
            col, row = pixel_to_grid(self.x, self.y)
            tx, ty = self.target_dir
            nx, ny = col + tx, row + ty
            if is_path(nx, ny):
                self.dir = self.target_dir
            else:
                # Pastikan tidak menabrak dinding saat lanjut
                cx, cy = self.dir
                nx, ny = col + cx, row + cy
                if not is_path(nx, ny):
                    self.dir = (0, 0)
        # Gerak
        dx, dy = self.dir
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        # Cegah nembus dinding: clamp saat akan masuk dinding
        self.x, self.y = self._move_with_collision(self.x, self.y, new_x, new_y, dx, dy)
        self.col, self.row = pixel_to_grid(self.x, self.y)

    def _move_with_collision(self, old_x, old_y, new_x, new_y, dx, dy):
        if dx != 0:
            # Horizontal move
            next_edge = new_x + (TILE_SIZE - 1 if dx > 0 else 0)
            next_col = next_edge // TILE_SIZE
            row = old_y // TILE_SIZE
            if is_wall(next_col, row):
                # snap ke tepi sel
                if dx > 0:
                    new_x = next_col * TILE_SIZE - (TILE_SIZE)
                else:
                    new_x = next_col * TILE_SIZE
                dx = 0
        if dy != 0:
            # Vertical move
            next_edge = new_y + (TILE_SIZE - 1 if dy > 0 else 0)
            next_row = next_edge // TILE_SIZE
            col = new_x // TILE_SIZE
            if is_wall(col, next_row):
                if dy > 0:
                    new_y = next_row * TILE_SIZE - (TILE_SIZE)
                else:
                    new_y = next_row * TILE_SIZE
                dy = 0
        return new_x, new_y

    def draw(self, surface):
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2
        pygame.draw.circle(surface, self.color, (cx, cy), self.radius)


class Ghost:
    def __init__(self, name, color, start_col, start_row, speed=2.5):
        self.name = name
        self.base_color = color
        self.color = color
        self.start_col = start_col
        self.start_row = start_row
        self.speed = speed
        self.radius = TILE_SIZE // 2 - 2
        self.vulnerable = False
        self.dead = False
        self.reset()

    def reset(self):
        self.col = self.start_col
        self.row = self.start_row
        self.x, self.y = grid_to_pixel(self.col, self.row)
        self.dir = (0, 0)

    def set_vulnerable(self, v):
        self.vulnerable = v
        self.color = VULNERABLE_COLOR if v else self.base_color

    def at_cell_center(self):
        return self.x % TILE_SIZE == 0 and self.y % TILE_SIZE == 0

    def valid_dirs(self):
        col, row = pixel_to_grid(self.x, self.y)
        options = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nc, nr = col + dx, row + dy
            if is_path(nc, nr):
                options.append((dx, dy))
        return options

    def choose_dir(self, pac_col, pac_row):
        # AI sederhana: Saat di persimpangan atau buntu, pilih arah yang mendekati Pacman.
        options = self.valid_dirs()
        # Hindari balik arah kecuali buntu
        if self.dir and len(options) > 1:
            opp = (-self.dir[0], -self.dir[1])
            options = [o for o in options if o != opp]
        if not options:
            return (0, 0)
        # Pilih yang meminimalkan jarak grid ke Pacman
        col, row = pixel_to_grid(self.x, self.y)
        best = None
        best_d = 1e9
        for dx, dy in options:
            nc, nr = col + dx, row + dy
            d = abs(nc - pac_col) + abs(nr - pac_row)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        # Sesekali lakukan random agar tidak terlalu deterministik
        if random.random() < 0.1:
            best = random.choice(options)
        return best

    def update(self, pac_col, pac_row):
        if self.at_cell_center():
            desired = self.choose_dir(pac_col, pac_row)
            # Jika jalan buntu, bisa diam sejenak
            self.dir = desired
        dx, dy = self.dir
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        # Collision dengan dinding
        self.x, self.y = self._move_with_collision(self.x, self.y, new_x, new_y, dx, dy)
        self.col, self.row = pixel_to_grid(self.x, self.y)

    def _move_with_collision(self, old_x, old_y, new_x, new_y, dx, dy):
        if dx != 0:
            next_edge = new_x + (TILE_SIZE - 1 if dx > 0 else 0)
            next_col = int(next_edge // TILE_SIZE)
            row = int(old_y // TILE_SIZE)
            if is_wall(next_col, row):
                if dx > 0:
                    new_x = next_col * TILE_SIZE - (TILE_SIZE)
                else:
                    new_x = next_col * TILE_SIZE
                dx = 0
        if dy != 0:
            next_edge = new_y + (TILE_SIZE - 1 if dy > 0 else 0)
            next_row = int(next_edge // TILE_SIZE)
            col = int(new_x // TILE_SIZE)
            if is_wall(col, next_row):
                if dy > 0:
                    new_y = next_row * TILE_SIZE - (TILE_SIZE)
                else:
                    new_y = next_row * TILE_SIZE
                dy = 0
        return new_x, new_y

    def draw(self, surface):
        cx = int(self.x + TILE_SIZE // 2)
        cy = int(self.y + TILE_SIZE // 2)
        pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
        # mata sederhana
        eye_offset = 4
        pygame.draw.circle(surface, WHITE, (cx - eye_offset, cy - eye_offset), 3)
        pygame.draw.circle(surface, WHITE, (cx + eye_offset, cy - eye_offset), 3)


# ==========================
# Game State dan Mekanik
# ==========================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.bigfont = pygame.font.SysFont("arial", 48, bold=True)

        # Build dot map dari MAZE_LAYOUT
        self.dots = set()
        self.power_pellets = set()
        for r, row in enumerate(MAZE_LAYOUT):
            for c, ch in enumerate(row):
                if ch == '2':
                    self.dots.add((c, r))
                elif ch == '3':
                    self.power_pellets.add((c, r))
        self.total_dots = len(self.dots) + len(self.power_pellets)

        # Posisi mulai Pacman dan Ghosts
        self.pacman_start = (1, 1)
        # letakkan ghost di dekat tengah
        self.ghost_home = (GRID_COLS // 2, GRID_ROWS // 2)
        self.ghost_starts = [
            (self.ghost_home[0], self.ghost_home[1]),
            (self.ghost_home[0] - 1, self.ghost_home[1]),
            (self.ghost_home[0] + 1, self.ghost_home[1]),
            (self.ghost_home[0], self.ghost_home[1] + 1),
        ]

        # Pastikan posisi start berada di path
        pc, pr = self.pacman_start
        if not is_path(pc, pr):
            # cari path terdekat
            self.pacman_start = self._find_nearest_path(pc, pr)
        self.pacman = Pacman(*self.pacman_start)

        colors = [RED, PINK, CYAN, ORANGE]
        speeds = [2.6, 2.5, 2.7, 2.4]
        self.ghosts = []
        for i in range(4):
            gc, gr = self.ghost_starts[i]
            if not is_path(gc, gr):
                gc, gr = self._find_nearest_path(gc, gr)
            self.ghosts.append(Ghost(f"G{i+1}", colors[i], gc, gr, speed=speeds[i]))

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.power_timer = 0
        self.power_duration_ms = 7000

    def _find_nearest_path(self, c, r):
        # BFS kecil untuk cari path terdekat
        from collections import deque
        q = deque()
        q.append((c, r))
        seen = set([(c, r)])
        while q:
            cc, rr = q.popleft()
            if is_path(cc, rr):
                return (cc, rr)
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nc, nr = cc + dx, rr + dy
                if 0 <= nc < GRID_COLS and 0 <= nr < GRID_ROWS and (nc, nr) not in seen:
                    seen.add((nc, nr))
                    q.append((nc, nr))
        return (1, 1)

    def reset_after_life_lost(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()
            g.set_vulnerable(False)
        self.power_timer = 0

    def eat_at(self, col, row):
        ate = False
        if (col, row) in self.dots:
            self.dots.remove((col, row))
            self.score += 10
            ate = True
        if (col, row) in self.power_pellets:
            self.power_pellets.remove((col, row))
            self.score += 50
            self.power_timer = pygame.time.get_ticks()
            for g in self.ghosts:
                g.set_vulnerable(True)
            ate = True
        if ate and len(self.dots) + len(self.power_pellets) == 0:
            self.win = True
            self.game_over = True

    def update(self):
        if self.game_over:
            return

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman.set_direction(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.pacman.set_direction(1, 0)
        elif keys[pygame.K_UP]:
            self.pacman.set_direction(0, -1)
        elif keys[pygame.K_DOWN]:
            self.pacman.set_direction(0, 1)

        # Update power state
        if self.power_timer:
            elapsed = pygame.time.get_ticks() - self.power_timer
            if elapsed >= self.power_duration_ms:
                # Matikan vulnerable
                for g in self.ghosts:
                    g.set_vulnerable(False)
                self.power_timer = 0

        # Update Pacman
        self.pacman.update()
        # Makan dot/power
        self.eat_at(self.pacman.col, self.pacman.row)

        # Update Ghosts
        for g in self.ghosts:
            g.update(self.pacman.col, self.pacman.row)

        # Cek tabrakan Pacman-Ghost
        for g in self.ghosts:
            if self._collide(self.pacman, g):
                if g.vulnerable:
                    # Makan ghost
                    self.score += 200
                    g.reset()
                    g.set_vulnerable(False)
                else:
                    # Kehilangan nyawa
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self.win = False
                    else:
                        self.reset_after_life_lost()
                    break

    def _collide(self, a, b):
        ax = a.x + TILE_SIZE // 2
        ay = a.y + TILE_SIZE // 2
        bx = b.x + TILE_SIZE // 2
        by = b.y + TILE_SIZE // 2
        dist2 = (ax - bx) ** 2 + (ay - by) ** 2
        r = a.radius + b.radius - 2
        return dist2 <= r * r

    def draw_maze(self, surface):
        # Gambar dinding dan jalur
        for r, row in enumerate(MAZE_LAYOUT):
            for c, ch in enumerate(row):
                x, y = grid_to_pixel(c, r)
                if ch == '1':
                    pygame.draw.rect(surface, NAVY, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(surface, BLUE, (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4), 2)
                else:
                    # jalur
                    pygame.draw.rect(surface, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                # dots dan power akan digambar terpisah

        # Dots
        for (c, r) in self.dots:
            x, y = grid_to_pixel(c, r)
            cx = x + TILE_SIZE // 2
            cy = y + TILE_SIZE // 2
            pygame.draw.circle(surface, WHITE, (cx, cy), 3)
        # Power pellets
        for (c, r) in self.power_pellets:
            x, y = grid_to_pixel(c, r)
            cx = x + TILE_SIZE // 2
            cy = y + TILE_SIZE // 2
            pygame.draw.circle(surface, WHITE, (cx, cy), 6)

    def draw_ui(self, surface):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        surface.blit(score_text, (10, HEIGHT - 24))
        surface.blit(lives_text, (WIDTH - 110, HEIGHT - 24))

    def draw_overlay(self, surface):
        if self.game_over:
            message = "YOU WIN!" if self.win else "GAME OVER"
            txt = self.bigfont.render(message, True, WHITE)
            hint = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 10))

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
                    if self.game_over and event.key == pygame.K_r:
                        self.__init__()  # restart game

            if not self.game_over:
                self.update()

            # Render
            self.screen.fill(BLACK)
            self.draw_maze(self.screen)
            self.pacman.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_ui(self.screen)
            self.draw_overlay(self.screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
