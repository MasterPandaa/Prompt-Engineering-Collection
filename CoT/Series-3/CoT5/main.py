import sys
import math
import random
import pygame
from pygame import Rect

# =============================
# Konstanta dan Konfigurasi
# =============================
TILE_SIZE = 24
COLS = 28
ROWS = 31
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE
FPS = 60

# Kecepatan (px/detik)
PACMAN_SPEED = 110
GHOST_SPEED = 90
FRIGHTENED_SPEED = 60

# Warna
BLACK = (0, 0, 0)
NAVY = (12, 6, 40)
BLUE = (33, 33, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 216, 0)
RED = (255, 0, 0)
PINK = (255, 128, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 170, 0)
GREY = (120, 120, 120)

# Durasi power-up (detik)
POWER_DURATION = 8.0

# Simbol Maze
# '#': dinding, '.': pellet, 'o': power pellet, ' ': kosong, 'G': ghost spawn, 'P': player spawn
MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###GG### ##.#     ",
    "######.## #      # ##.######",
    "      .   # PPPP #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
    "                            ",
    "############################",
]

# Catatan: Baris ke-28 (index 27) adalah koridor kosong untuk efek "tunnel" wrapping


def grid_to_px(col, row):
    return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2


def px_to_grid(x, y):
    return int(x // TILE_SIZE), int(y // TILE_SIZE)


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.walls = []  # list of Rect
        self.pellets = set()
        self.power_pellets = set()
        self.ghost_starts = []
        self.player_start = None
        self._parse_layout()

    def _parse_layout(self):
        for r, line in enumerate(self.layout):
            for c, ch in enumerate(line):
                if ch == '#':
                    self.walls.append(Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power_pellets.add((c, r))
                elif ch == 'G':
                    self.ghost_starts.append((c, r))
                elif ch == 'P':
                    # gunakan salah satu P sebagai start, yang lain tetap lantai
                    if self.player_start is None:
                        self.player_start = (c, r)
        # fallback jika tidak ditemukan P
        if self.player_start is None:
            self.player_start = (13, 23)
        if not self.ghost_starts:
            self.ghost_starts = [(13, 14), (14, 14), (12, 14), (15, 14)]

    def is_wall(self, col, row):
        if col < 0 or row < 0 or col >= COLS or row >= ROWS:
            return True
        return self.layout[row][col] == '#'

    def draw(self, surf):
        # Latar
        surf.fill(NAVY)
        # Dinding sederhana sebagai blok
        for wall in self.walls:
            pygame.draw.rect(surf, BLUE, wall)
        # Pelet
        for (c, r) in self.pellets:
            cx, cy = grid_to_px(c, r)
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)
        # Power pelet
        for (c, r) in self.power_pellets:
            cx, cy = grid_to_px(c, r)
            pygame.draw.circle(surf, WHITE, (cx, cy), 6, 1)


class Movable:
    def __init__(self, x, y, speed):
        self.pos = pygame.Vector2(x, y)
        self.dir = pygame.Vector2(0, 0)
        self.next_dir = pygame.Vector2(0, 0)
        self.speed = speed
        self.radius = TILE_SIZE // 2 - 2

    def at_tile_center(self):
        # true jika cukup dekat ke pusat tile saat ini
        cx, cy = grid_to_px(*px_to_grid(self.pos.x, self.pos.y))
        return abs(self.pos.x - cx) < 2 and abs(self.pos.y - cy) < 2

    def snap_to_center(self):
        col, row = px_to_grid(self.pos.x, self.pos.y)
        cx, cy = grid_to_px(col, row)
        self.pos.update(cx, cy)

    def can_move_dir(self, maze: Maze, dvec: pygame.Vector2):
        # cek satu langkah kecil ke depan terhadap dinding
        if dvec.length_squared() == 0:
            return False
        d = dvec.normalize() * 1
        new_x = self.pos.x + d.x
        new_y = self.pos.y + d.y
        # buat rect kecil
        rect = Rect(0, 0, TILE_SIZE - 4, TILE_SIZE - 4)
        rect.center = (new_x, new_y)
        # deteksi terhadap grid
        col0, row0 = px_to_grid(rect.left, rect.top)
        col1, row1 = px_to_grid(rect.right, rect.bottom)
        for r in range(row0, row1 + 1):
            for c in range(col0, col1 + 1):
                if maze.is_wall(c, r):
                    wall_rect = Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return False
        return True

    def move(self, maze: Maze, dt):
        # wrap tunnel horizontal
        if self.pos.x < -TILE_SIZE * 0.5:
            self.pos.x = WIDTH + TILE_SIZE * 0.5
        elif self.pos.x > WIDTH + TILE_SIZE * 0.5:
            self.pos.x = -TILE_SIZE * 0.5

        # jika ada next_dir dan berada di center tile, coba belok
        if self.next_dir.length_squared() > 0 and self.at_tile_center():
            if self.can_move_dir(maze, self.next_dir):
                self.snap_to_center()
                self.dir = self.next_dir
                self.next_dir = pygame.Vector2(0, 0)

        # jika arah saat ini mentok, berhenti di center
        if self.dir.length_squared() > 0 and not self.can_move_dir(maze, self.dir):
            if self.at_tile_center():
                self.dir.update(0, 0)
            else:
                # bergerak menuju center agar tidak tersangkut
                self.snap_to_center()
                self.dir.update(0, 0)
        else:
            # gerak normal
            if self.dir.length_squared() > 0:
                step = self.dir.normalize() * self.speed * dt
                self.pos += step


class Player(Movable):
    def __init__(self, x, y):
        super().__init__(x, y, PACMAN_SPEED)
        self.lives = 3
        self.score = 0
        self.mouth_time = 0.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        desired = None
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            desired = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            desired = pygame.Vector2(0, 1)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            desired = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            desired = pygame.Vector2(1, 0)
        if desired is not None:
            # jika bisa langsung belok, lakukan; kalau tidak, antre
            if self.at_tile_center():
                self.next_dir = desired
            else:
                self.next_dir = desired

    def eat_pellet(self, maze: Maze):
        col, row = px_to_grid(self.pos.x, self.pos.y)
        ate_power = False
        if (col, row) in maze.pellets:
            maze.pellets.remove((col, row))
            self.score += 10
        if (col, row) in maze.power_pellets:
            maze.power_pellets.remove((col, row))
            self.score += 50
            ate_power = True
        return ate_power

    def draw(self, surf):
        # animasi mulut
        self.mouth_time += 0.1
        mouth_angle = (math.sin(self.mouth_time) * 0.25 + 0.25) * math.pi
        x, y = int(self.pos.x), int(self.pos.y)
        radius = TILE_SIZE // 2 - 2
        if self.dir.length_squared() == 0:
            pygame.draw.circle(surf, YELLOW, (x, y), radius)
        else:
            angle_offset = 0
            if self.dir.y < 0:
                angle_offset = -math.pi / 2
            elif self.dir.y > 0:
                angle_offset = math.pi / 2
            elif self.dir.x < 0:
                angle_offset = math.pi
            start_angle = angle_offset + mouth_angle
            end_angle = angle_offset - mouth_angle
            pygame.draw.circle(surf, YELLOW, (x, y), radius)
            pygame.draw.polygon(
                surf,
                BLACK,
                [
                    (x, y),
                    (x + radius * math.cos(start_angle), y + radius * math.sin(start_angle)),
                    (x + radius * math.cos(end_angle), y + radius * math.sin(end_angle)),
                ],
            )


class Ghost(Movable):
    def __init__(self, x, y, color, home):
        super().__init__(x, y, GHOST_SPEED)
        self.color = color
        self.base_speed = GHOST_SPEED
        self.state = 'normal'  # normal, frightened, eaten
        self.fright_timer = 0.0
        self.home = pygame.Vector2(*grid_to_px(*home))
        # mulai gerak ke kiri/kanan acak
        self.dir = random.choice([pygame.Vector2(1, 0), pygame.Vector2(-1, 0)])

    def set_frightened(self):
        if self.state != 'eaten':
            self.state = 'frightened'
            self.fright_timer = POWER_DURATION
            self.speed = FRIGHTENED_SPEED

    def update_logic(self, maze: Maze, dt, player_pos):
        # update timer frightened
        if self.state == 'frightened':
            self.fright_timer -= dt
            if self.fright_timer <= 0:
                self.state = 'normal'
                self.speed = self.base_speed
        elif self.state == 'eaten':
            # menuju home, jika sampai center tile home, kembali normal
            to_home = self.home - self.pos
            if to_home.length() < 3:
                self.state = 'normal'
                self.speed = self.base_speed
            else:
                # arahkan ke rumah secara langsung
                self.dir = to_home.normalize()
                self.move(maze, dt)
                return

        # di persimpangan (pusat tile), pilih arah
        if self.at_tile_center():
            self.snap_to_center()
            options = []
            for d in [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]:
                # hindari balik arah kecuali buntu
                if self.dir.length_squared() > 0 and d == -self.dir.normalize():
                    continue
                if self.can_move_dir(maze, d):
                    options.append(d)
            if not options:
                # terpaksa balik
                self.dir = -self.dir
            else:
                if self.state == 'frightened':
                    # pilih arah yang menjauh dari player
                    best_d = None
                    best_dist = -1
                    for d in options:
                        test_pos = pygame.Vector2(self.pos) + d * TILE_SIZE
                        dist = (test_pos - player_pos).length_squared()
                        if dist > best_dist:
                            best_dist = dist
                            best_d = d
                    self.dir = best_d
                else:
                    # normal: acak, tetapi sedikit prefer ke arah mendekati player
                    if random.random() < 0.7:
                        best_d = None
                        best_dist = 1e9
                        for d in options:
                            test_pos = pygame.Vector2(self.pos) + d * TILE_SIZE
                            dist = (test_pos - player_pos).length_squared()
                            if dist < best_dist:
                                best_dist = dist
                                best_d = d
                        self.dir = best_d
                    else:
                        self.dir = random.choice(options)

        # gerakkan
        self.move(maze, dt)

    def draw(self, surf):
        x, y = int(self.pos.x), int(self.pos.y)
        body_rect = Rect(0, 0, TILE_SIZE - 4, TILE_SIZE - 2)
        body_rect.center = (x, y)
        if self.state == 'frightened':
            color = BLUE
        elif self.state == 'eaten':
            color = GREY
        else:
            color = self.color
        pygame.draw.ellipse(surf, color, body_rect)
        # mata sederhana
        eye_offset = 4
        pygame.draw.circle(surf, WHITE, (x - eye_offset, y - 2), 3)
        pygame.draw.circle(surf, WHITE, (x + eye_offset, y - 2), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman (Pygame)')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 18)

        self.maze = Maze(MAZE_LAYOUT)
        psx, psy = grid_to_px(*self.maze.player_start)
        self.player = Player(psx, psy)

        ghost_starts = self.maze.ghost_starts
        colors = [RED, PINK, CYAN, ORANGE]
        self.ghosts = []
        for i, start in enumerate(ghost_starts[:4]):
            gx, gy = grid_to_px(*start)
            self.ghosts.append(Ghost(gx, gy, colors[i % len(colors)], home=start))

        self.state = 'running'  # running, gameover, win
        self.power_timer = 0.0

    def reset_positions(self):
        psx, psy = grid_to_px(*self.maze.player_start)
        self.player.pos.update(psx, psy)
        self.player.dir.update(0, 0)
        for i, g in enumerate(self.ghosts):
            gx, gy = grid_to_px(*self.maze.ghost_starts[i % len(self.maze.ghost_starts)])
            g.pos.update(gx, gy)
            g.dir = random.choice([pygame.Vector2(1, 0), pygame.Vector2(-1, 0)])
            g.state = 'normal'
            g.speed = g.base_speed

    def update(self, dt):
        if self.state not in ('running',):
            return

        # input
        self.player.handle_input()

        # gerak dan makan pellet
        self.player.move(self.maze, dt)
        ate_power = self.player.eat_pellet(self.maze)
        if ate_power:
            self.power_timer = POWER_DURATION
            for g in self.ghosts:
                g.set_frightened()

        # update ghosts
        for g in self.ghosts:
            g.update_logic(self.maze, dt, pygame.Vector2(self.player.pos))

        # power timer
        if self.power_timer > 0:
            self.power_timer -= dt

        # deteksi collision player-ghost
        player_rect = Rect(0, 0, TILE_SIZE - 6, TILE_SIZE - 6)
        player_rect.center = (int(self.player.pos.x), int(self.player.pos.y))
        for g in self.ghosts:
            ghost_rect = Rect(0, 0, TILE_SIZE - 6, TILE_SIZE - 6)
            ghost_rect.center = (int(g.pos.x), int(g.pos.y))
            if player_rect.colliderect(ghost_rect):
                if g.state == 'frightened':
                    # makan ghost
                    self.player.score += 200
                    g.state = 'eaten'
                    g.speed = self.base_ghost_speed_for(g)
                elif g.state == 'normal':
                    # kehilangan nyawa
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = 'gameover'
                    self.reset_positions()
                    break

        # menang jika semua pelet habis
        if not self.maze.pellets and not self.maze.power_pellets:
            self.state = 'win'

    def base_ghost_speed_for(self, g: Ghost):
        return g.base_speed

    def draw_hud(self):
        score_s = self.font.render(f"SCORE: {self.player.score}", True, WHITE)
        lives_s = self.font.render(f"LIVES: {self.player.lives}", True, WHITE)
        self.screen.blit(score_s, (8, HEIGHT - 24))
        self.screen.blit(lives_s, (WIDTH - 120, HEIGHT - 24))

    def draw(self):
        self.maze.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()

        if self.state == 'gameover':
            txt = self.font.render('GAME OVER - Press R to Restart', True, WHITE)
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
        elif self.state == 'win':
            txt = self.font.render('YOU WIN! - Press R to Restart', True, WHITE)
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                    if event.key == pygame.K_r and self.state in ('gameover', 'win'):
                        # reset seluruh permainan: reload maze pellets
                        self.__init__()

            if self.state == 'running':
                self.update(dt)

            self.draw()
            pygame.display.flip()


if __name__ == '__main__':
    Game().run()
