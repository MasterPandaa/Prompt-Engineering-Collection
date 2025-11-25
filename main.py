import sys
import random
import pygame
from pygame import Rect

# ------------------------------
# Konfigurasi Umum
# ------------------------------
TITLE = "Pacman (Pygame)"
FPS = 60
TILE_SIZE = 24
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
    "      .   # P  o #   .      ",
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
]
# Karakter di peta:
# '#' = dinding, '.' = pelet, 'o' = power pellet, 'G' = ghost, 'P' = pacman, ' ' = kosong

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

# Warna
BLACK = (0, 0, 0)
BLUE = (33, 33, 222)
YELLOW = (255, 215, 0)
WHITE = (240, 240, 240)
PINK = (255, 105, 180)
RED = (220, 20, 60)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (180, 180, 180)

# ------------------------------
# Utilitas
# ------------------------------
def grid_to_pix(grid_pos):
    gx, gy = grid_pos
    return int(gx * TILE_SIZE + TILE_SIZE // 2), int(gy * TILE_SIZE + TILE_SIZE // 2)


def pix_to_grid(px, py):
    return int(px // TILE_SIZE), int(py // TILE_SIZE)


# ------------------------------
# Maze
# ------------------------------
class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.ghost_starts = []
        self.pacman_start = None
        self._parse_layout()

    def _parse_layout(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))
                elif ch == 'G':
                    self.ghost_starts.append((x, y))
                elif ch == 'P':
                    self.pacman_start = (x, y)
        # Safety fallback
        if self.pacman_start is None:
            self.pacman_start = (1, 1)

    def draw(self, surf):
        # Draw walls
        for (x, y) in self.walls:
            r = Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, BLUE, r)

        # Draw pellets
        for (x, y) in self.pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)

        # Draw power pellets
        for (x, y) in self.power_pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, WHITE, (cx, cy), 6)

    def is_wall(self, grid_pos):
        return grid_pos in self.walls

    def wrap_if_tunnel(self, pix_pos):
        # Implementasi tunnel horizontal: bila keluar layar di kiri/kanan, muncul di sisi lain
        x, y = pix_pos
        if x < 0:
            x = WIDTH - 1
        elif x >= WIDTH:
            x = 0
        return x, y


# ------------------------------
# Entity Dasar
# ------------------------------
class Entity:
    def __init__(self, maze, grid_pos, speed):
        self.maze = maze
        cx, cy = grid_to_pix(grid_pos)
        self.pos = pygame.Vector2(cx, cy)
        self.dir = pygame.Vector2(0, 0)  # arah saat ini
        self.next_dir = pygame.Vector2(0, 0)  # arah yang diinginkan
        self.speed = speed  # pixel per frame

    def grid_aligned(self):
        # True bila berada tepat di tengah tile (untuk mempermudah belok)
        gx_center = (self.pos.x - TILE_SIZE // 2) % TILE_SIZE == 0
        gy_center = (self.pos.y - TILE_SIZE // 2) % TILE_SIZE == 0
        return gx_center and gy_center

    def can_move(self, direction):
        # Cek apakah dari posisi saat ini, bergerak 1 pixel ke arah 'direction' akan menabrak dinding
        new_pos = self.pos + direction
        # Ambil posisi grid di depan berdasarkan posisi target di pusat tile
        future_center = pygame.Vector2(
            (new_pos.x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2,
            (new_pos.y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2,
        )
        grid = pix_to_grid(future_center.x, future_center.y)
        return not self.maze.is_wall(grid)

    def move(self):
        # Terapkan next_dir bila memungkinkan saat align di grid
        if self.grid_aligned() and self.next_dir.length_squared() != 0:
            if self.can_move(self.next_dir):
                self.dir = self.next_dir
        # Cegah masuk dinding; bila depan dinding, berhenti
        if not self.can_move(self.dir):
            return
        self.pos += self.dir * self.speed
        # Tunnel wrap
        self.pos.x, self.pos.y = self.maze.wrap_if_tunnel((self.pos.x, self.pos.y))


# ------------------------------
# Pacman
# ------------------------------
class Pacman(Entity):
    def __init__(self, maze, grid_pos, speed=2.0):
        super().__init__(maze, grid_pos, speed)
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True
        self.score = 0
        self.lives = 3

    def set_input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_dir = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_dir = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_dir = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_dir = pygame.Vector2(0, 1)

    def eat(self, game_state):
        grid = pix_to_grid(self.pos.x, self.pos.y)
        if grid in self.maze.pellets:
            self.maze.pellets.remove(grid)
            self.score += 10
        if grid in self.maze.power_pellets:
            self.maze.power_pellets.remove(grid)
            self.score += 50
            game_state.enter_power_mode()

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)


# ------------------------------
# Ghost
# ------------------------------
OPPOSITE = {
    (-1, 0): (1, 0),
    (1, 0): (-1, 0),
    (0, -1): (0, 1),
    (0, 1): (0, -1),
}

class Ghost(Entity):
    def __init__(self, maze, grid_pos, color, speed=1.8):
        super().__init__(maze, grid_pos, speed)
        self.color = color
        self.base_speed = speed
        self.radius = TILE_SIZE // 2 - 3
        # Mulai bergerak ke kiri sebagai default
        self.dir = pygame.Vector2(-1, 0)

    def available_directions(self):
        # Daftar arah valid dari posisi sekarang ketika berada di pusat tile
        dirs = [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]
        valid = []
        for d in dirs:
            if self.can_move(d):
                valid.append(d)
        return valid

    def choose_direction(self, target=None, frightened=False):
        # AI sederhana:
        # - Bila frightened: pilih arah random (tidak balik arah bila opsi lain ada)
        # - Bila normal: pilih arah random di persimpangan, hindari balik arah jika memungkinkan
        if not self.grid_aligned():
            return
        choices = self.available_directions()
        if not choices:
            return
        # Hindari balik arah jika ada pilihan lain
        if self.dir.length_squared() != 0:
            opposite = pygame.Vector2(OPPOSITE[(int(self.dir.x), int(self.dir.y))])
            non_back = [d for d in choices if d != opposite]
            if non_back:
                choices = non_back
        # Pilihan akhir
        self.dir = random.choice(choices)

    def set_frightened(self, frightened):
        # Atur kecepatan saat frightened
        if frightened:
            self.speed = self.base_speed * 0.6
        else:
            self.speed = self.base_speed

    def draw(self, surf, frightened=False):
        color = GREY if frightened else self.color
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)


# ------------------------------
# Game State
# ------------------------------
class GameState:
    def __init__(self):
        self.mode = "normal"  # normal | power | gameover | win
        self.power_timer = 0
        self.power_duration = 7.0  # detik

    def enter_power_mode(self):
        self.mode = "power"
        self.power_timer = self.power_duration

    def update(self, dt):
        if self.mode == "power":
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.mode = "normal"
                self.power_timer = 0

    def is_power(self):
        return self.mode == "power"

    def is_over(self):
        return self.mode in ("gameover", "win")


# ------------------------------
# Game
# ------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        self.maze = Maze(MAZE_LAYOUT)
        self.state = GameState()

        self.pacman = Pacman(self.maze, self.maze.pacman_start)
        self.ghosts = []
        ghost_colors = [RED, PINK, CYAN, ORANGE]
        starts = self.maze.ghost_starts or [(COLS // 2, ROWS // 2)] * 4
        for i in range(min(4, len(starts))):
            self.ghosts.append(Ghost(self.maze, starts[i], ghost_colors[i % len(ghost_colors)]))

    def reset_positions(self):
        self.pacman.pos = pygame.Vector2(*grid_to_pix(self.maze.pacman_start))
        self.pacman.dir = pygame.Vector2(0, 0)
        self.pacman.next_dir = pygame.Vector2(0, 0)
        for i, g in enumerate(self.ghosts):
            start = self.maze.ghost_starts[i % len(self.maze.ghost_starts)] if self.maze.ghost_starts else (COLS // 2, ROWS // 2)
            g.pos = pygame.Vector2(*grid_to_pix(start))
            g.dir = pygame.Vector2(-1, 0)

    def update(self, dt):
        if self.state.is_over():
            return

        keys = pygame.key.get_pressed()
        self.pacman.set_input(keys)
        self.pacman.move()
        self.pacman.eat(self.state)

        # Perbarui ghost
        frightened = self.state.is_power()
        for g in self.ghosts:
            g.set_frightened(frightened)
            if g.grid_aligned():
                g.choose_direction(frightened=frightened)
            g.move()

        # Cek tabrakan Pacman vs Ghost
        p_rect = Rect(int(self.pacman.pos.x) - 10, int(self.pacman.pos.y) - 10, 20, 20)
        for g in self.ghosts:
            g_rect = Rect(int(g.pos.x) - 10, int(g.pos.y) - 10, 20, 20)
            if p_rect.colliderect(g_rect):
                if frightened:
                    # Makan ghost
                    self.pacman.score += 200
                    # Kirim kembali ke start
                    idx = self.ghosts.index(g)
                    start = self.maze.ghost_starts[idx % len(self.maze.ghost_starts)] if self.maze.ghost_starts else (COLS // 2, ROWS // 2)
                    g.pos = pygame.Vector2(*grid_to_pix(start))
                    g.dir = pygame.Vector2(-1, 0)
                else:
                    # Pacman terkena
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.state.mode = "gameover"
                    else:
                        self.reset_positions()
                    break

        # Cek kemenangan
        if not self.maze.pellets and not self.maze.power_pellets and not self.state.is_over():
            self.state.mode = "win"

        # Update timer power mode
        self.state.update(dt)

    def draw_hud(self):
        text = f"Score: {self.pacman.score}   Lives: {self.pacman.lives}"
        if self.state.is_power():
            text += f"   POWER: {self.state.power_timer:0.1f}s"
        surf = self.font.render(text, True, WHITE)
        self.screen.blit(surf, (10, HEIGHT - 22))

    def draw_center_message(self, msg):
        surf = self.font.render(msg, True, WHITE)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(surf, rect)

    def render(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        frightened = self.state.is_power()
        for g in self.ghosts:
            g.draw(self.screen, frightened)
        self.pacman.draw(self.screen)
        self.draw_hud()
        if self.state.mode == "gameover":
            self.draw_center_message("GAME OVER - Press R to Restart")
        elif self.state.mode == "win":
            self.draw_center_message("YOU WIN! - Press R to Restart")
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r and self.state.is_over():
                    # Reset game
                    self.__init__()

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()


if __name__ == "__main__":
    Game().run()
