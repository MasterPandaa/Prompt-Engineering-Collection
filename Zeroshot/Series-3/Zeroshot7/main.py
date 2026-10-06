import pygame
import sys
import random
import math
from collections import deque

# Konfigurasi dasar
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 20  # 40x30 grid
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
FPS = 60

# Kode tile:
# '1' = dinding, '0' = jalur kosong, '2' = pelet, '3' = power-pellet

# Maze 40x30 (baris x kolom). Pastikan setiap baris memiliki 40 karakter.
# Desain simpel namun bisa dimainkan. Koridor luar adalah dinding.
MAZE_LAYOUT = [
    "1111111111111111111111111111111111111111",
    "1222222222221111222222222222111122222221",
    "1211112111121111211112111122111121111121",
    "1211112111121111211112111122111121111121",
    "1232222222222222222222222222222222222321",
    "1211112111111111111111111111111121111121",
    "1211112111111111111111111111111121111121",
    "1222222222221111222222222222111122222221",
    "1111112111121111211112111122111121111111",
    "1000032111121111211112111122111123000001",
    "1222222222222222222222222222222222222221",
    "1211112111111111111111111111111121111121",
    "1211112111111111111111111111111121111121",
    "1222222222221111222222222222111122222221",
    "1111112111121111211112111122111121111111",
    "1000022111121111211112111122111122000001",
    "1222222222222222222222222222222222222221",
    "1211112111111111111111111111111121111121",
    "1211112111111111111111111111111121111121",
    "1232222222221111222222222222111122222321",
    "1211112111121111211112111122111121111121",
    "1211112111121111211112111122111121111121",
    "1222222222222222222222222222222222222221",
    "1111112111111111111111111111111121111111",
    "1000002000001111200000000002111120000001",
    "1222222222222222222222222222222222222221",
    "1211112111111111111111111111111121111121",
    "1232222222221111222222222222111122222321",
    "1222222222222222222222222222222222222221",
    "1111111111111111111111111111111111111111",
]

# Validasi dimensi maze
assert len(MAZE_LAYOUT) == ROWS, f"Maze harus {ROWS} baris"
for row in MAZE_LAYOUT:
    assert len(row) == COLS, f"Setiap baris maze harus {COLS} kolom"

# Warna
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (70, 70, 70)

# Utility grid

def grid_to_px(col, row):
    return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2


def px_to_grid(x, y):
    return x // TILE_SIZE, y // TILE_SIZE


def is_wall(col, row):
    if 0 <= row < ROWS and 0 <= col < COLS:
        return MAZE_LAYOUT[row][col] == '1'
    return True


def is_intersection(col, row):
    # Persimpangan jika ada >= 3 arah bebas
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    free = 0
    for dx, dy in dirs:
        nc, nr = col+dx, row+dy
        if not is_wall(nc, nr):
            free += 1
    return free >= 3


def available_dirs(col, row, forbid=None):
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    cand = []
    for d in dirs:
        if forbid and (-d[0], -d[1]) == forbid:
            # jangan langsung balik arah kecuali buntu
            continue
        nc, nr = col + d[0], row + d[1]
        if not is_wall(nc, nr):
            cand.append(d)
    if not cand and forbid:
        # jika buntu, boleh balik
        nc, nr = col - forbid[0], row - forbid[1]
        if not is_wall(nc, nr):
            cand.append((-forbid[0], -forbid[1]))
    return cand


class Pacman:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.x, self.y = grid_to_px(col, row)
        self.speed = 2.5  # pixels per frame
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True

    def set_dir(self, d):
        self.next_dir = d

    def can_move(self, d):
        # cek tile tujuan saat berada dekat center tile
        cx, cy = grid_to_px(self.col, self.row)
        if abs(self.x - cx) < 2 and abs(self.y - cy) < 2:
            nc, nr = self.col + d[0], self.row + d[1]
            return not is_wall(nc, nr)
        return True

    def update(self):
        # snap ke center tile jika dekat agar gerakan halus
        cx, cy = grid_to_px(self.col, self.row)
        if abs(self.x - cx) < 2:
            self.x = cx
        if abs(self.y - cy) < 2:
            self.y = cy

        # ubah arah jika memungkinkan
        if self.next_dir != self.dir and self.can_move(self.next_dir):
            # hanya ganti arah saat center tile
            if self.x == cx and self.y == cy:
                self.dir = self.next_dir

        # jika arah saat ini mentok dinding, berhenti di center
        if not self.can_move(self.dir):
            if self.x == cx and self.y == cy:
                self.dir = (0, 0)

        # gerakkan
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

        # perbarui grid pos
        self.col, self.row = px_to_grid(int(self.x), int(self.y))

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.radius)


class Ghost:
    SCATTER_COLOR = GREY

    def __init__(self, col, row, color, name="ghost"):
        self.spawn = (col, row)
        self.col = col
        self.row = row
        self.x, self.y = grid_to_px(col, row)
        self.dir = (0, 0)
        self.color = color
        self.base_speed = 2.0
        self.speed = self.base_speed
        self.radius = TILE_SIZE // 2 - 3
        self.state = "normal"  # normal | frightened | eaten
        self.state_timer = 0.0
        self.name = name

    def reset(self):
        self.col, self.row = self.spawn
        self.x, self.y = grid_to_px(self.col, self.row)
        self.dir = (0, 0)
        self.state = "normal"
        self.state_timer = 0.0
        self.speed = self.base_speed

    def frighten(self, duration):
        if self.state != "eaten":
            self.state = "frightened"
            self.state_timer = duration
            self.speed = 1.6

    def eat(self):
        self.state = "eaten"
        self.speed = 2.8

    def choose_dir(self, target, avoid_back=True):
        # target: (col, row) Pacman atau base
        forbid = self.dir if avoid_back else None
        choices = available_dirs(self.col, self.row, forbid=forbid)
        if not choices:
            return self.dir

        if self.state == "frightened":
            # pilih acak di persimpangan
            return random.choice(choices)

        # normal / eaten: kejar target dengan heuristik jarak Manhattan/Euclidean
        best = None
        best_dist = math.inf
        for d in choices:
            nc, nr = self.col + d[0], self.row + d[1]
            dist = (target[0] - nc) ** 2 + (target[1] - nr) ** 2
            if dist < best_dist:
                best_dist = dist
                best = d
        return best if best else random.choice(choices)

    def update(self, pacman_colrow, dt):
        # update timer state frightened
        if self.state == "frightened":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "normal"
                self.speed = self.base_speed

        # tentukan target
        if self.state == "eaten":
            target = self.spawn
        else:
            target = pacman_colrow

        # bergerak. Ganti arah saat center tile/persimpangan
        cx, cy = grid_to_px(self.col, self.row)
        if abs(self.x - cx) < 2:
            self.x = cx
        if abs(self.y - cy) < 2:
            self.y = cy

        if self.x == cx and self.y == cy:
            d = self.choose_dir(target)
            if d:
                self.dir = d

        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

        self.col, self.row = px_to_grid(int(self.x), int(self.y))

        # jika sudah sampai base dan state eaten, kembali normal
        if self.state == "eaten" and (self.col, self.row) == self.spawn:
            self.state = "normal"
            self.speed = self.base_speed

    def draw(self, surf):
        if self.state == "frightened":
            color = CYAN
        elif self.state == "eaten":
            color = WHITE
        else:
            color = self.color
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)
        # mata
        eye_offset = 4
        pygame.draw.circle(surf, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
        pygame.draw.circle(surf, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)

        # Inisialisasi entitas
        self.reset_game(full=True)

    def find_spawn(self):
        # Tetapkan spawn manual agar cocok dengan layout
        pac_spawn = (2, 9)       # kolom, baris untuk Pacman
        ghost_spawns = [(20, 9), (19, 15), (20, 15), (21, 15)]
        return pac_spawn, ghost_spawns

    def reset_game(self, full=False):
        self.score = 0 if full else self.score
        self.lives = 3 if full else self.lives
        self.game_over = False
        self.win = False
        self.power_duration = 6.0  # detik

        self.maze = [list(row) for row in MAZE_LAYOUT]

        p_spawn, g_spawns = self.find_spawn()
        self.pacman = Pacman(*p_spawn)
        colors = [RED, PINK, ORANGE, (50, 205, 50)]  # red, pink, orange, limegreen
        self.ghosts = []
        names = ["Blinky", "Pinky", "Clyde", "Lucky"]
        for i, sp in enumerate(g_spawns[:4]):
            self.ghosts.append(Ghost(sp[0], sp[1], colors[i % len(colors)], names[i]))

        # Hitung pelet awal
        self.total_dots = sum(1 for r in self.maze for c in r if c in ('2', '3'))

    def reset_positions(self):
        # dipanggil saat Pacman mati
        p_spawn, g_spawns = self.find_spawn()
        self.pacman = Pacman(*p_spawn)
        for ghost, sp in zip(self.ghosts, g_spawns):
            ghost.col, ghost.row = sp
            ghost.x, ghost.y = grid_to_px(*sp)
            ghost.dir = (0, 0)
            if ghost.state != "eaten":
                ghost.state = "normal"
                ghost.speed = ghost.base_speed
            ghost.state_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.pacman.set_dir((0, -1))
        elif keys[pygame.K_DOWN]:
            self.pacman.set_dir((0, 1))
        elif keys[pygame.K_LEFT]:
            self.pacman.set_dir((-1, 0))
        elif keys[pygame.K_RIGHT]:
            self.pacman.set_dir((1, 0))

    def eat_at(self, col, row):
        tile = self.maze[row][col]
        if tile == '2':
            self.maze[row][col] = '0'
            self.score += 10
            self.total_dots -= 1
        elif tile == '3':
            self.maze[row][col] = '0'
            self.score += 50
            self.total_dots -= 1
            for g in self.ghosts:
                g.frighten(self.power_duration)

    def update(self, dt):
        if self.game_over or self.win:
            return

        self.handle_input()
        self.pacman.update()
        self.eat_at(self.pacman.col, self.pacman.row)

        for g in self.ghosts:
            g.update((self.pacman.col, self.pacman.row), dt)

        # Cek tabrakan
        for g in self.ghosts:
            if abs(g.x - self.pacman.x) < TILE_SIZE * 0.6 and abs(g.y - self.pacman.y) < TILE_SIZE * 0.6:
                if g.state == "frightened":
                    g.eat()
                    self.score += 200
                elif g.state == "normal":
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_positions()
                    break

        if self.total_dots <= 0:
            self.win = True

    def draw_maze(self):
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.maze[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                if tile == '1':
                    pygame.draw.rect(self.screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # lantai
                    pygame.draw.rect(self.screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                    if tile == '2':
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 3)
                    elif tile == '3':
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 6)

    def draw_ui(self):
        text = self.font.render(f"Score: {self.score}   Lives: {self.lives}", True, WHITE)
        self.screen.blit(text, (10, 5))
        if self.game_over:
            go = self.font.render("GAME OVER - Press R to Restart or ESC to Quit", True, WHITE)
            self.screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 10))
        elif self.win:
            wn = self.font.render("YOU WIN! - Press R to Restart or ESC to Quit", True, WHITE)
            self.screen.blit(wn, (WIDTH//2 - wn.get_width()//2, HEIGHT//2 - 10))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r and (self.game_over or self.win):
                        self.reset_game(full=True)

            if not self.game_over and not self.win:
                self.update(dt)

            self.screen.fill(BLACK)
            self.draw_maze()
            for g in self.ghosts:
                g.draw(self.screen)
            self.pacman.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
