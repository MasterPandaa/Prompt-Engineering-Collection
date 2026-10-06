import sys
import math
import random
import time
from dataclasses import dataclass

import pygame

# -----------------------------
# Config & Constants
# -----------------------------
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
    "######.## ###GG### ##.######",
    "          # G  G #          ",
    "######.## ######## ##.######",
    "     #.##          ##.#     ",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#......##....##....##......#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#..........................#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#............##............#",
    "############################",
]

# Legend:
# '#': wall
# '.': pellet
# 'o': power pellet
# ' ': empty / tunnel space
# 'G': ghost house gate (treat like wall for Pacman/ghosts, except respawning ghosts can pass)
# NOTE: Lines 10-16 create a central ghost house; spaces allow movement.

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 48  # extra space for HUD
FPS = 60
POWER_DURATION = 7.0  # seconds
GHOST_RESPAWN_TIME = 3.0  # seconds after being eaten
PACMAN_SPEED = 4  # pixels per frame
GHOST_SPEED = 3
FRIGHTENED_SPEED = 2

BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (120, 120, 120)

WALL_COLOR = (0, 51, 153)
PELLET_COLOR = (255, 255, 180)
POWER_COLOR = (255, 180, 180)
FRIGHTENED_COLOR = (33, 33, 255)


@dataclass
class Vec2:
    x: int
    y: int

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: int):
        return Vec2(self.x * scalar, self.y * scalar)

    def to_tuple(self):
        return (self.x, self.y)


DIRS = {
    'UP': Vec2(0, -1),
    'DOWN': Vec2(0, 1),
    'LEFT': Vec2(-1, 0),
    'RIGHT': Vec2(1, 0),
}
DIR_LIST = [DIRS['UP'], DIRS['DOWN'], DIRS['LEFT'], DIRS['RIGHT']]


def grid_to_pixel(grid_pos: Vec2) -> Vec2:
    return Vec2(grid_pos.x * TILE_SIZE + TILE_SIZE // 2, grid_pos.y * TILE_SIZE + TILE_SIZE // 2)


def pixel_to_grid(pixel_pos: Vec2) -> Vec2:
    return Vec2(pixel_pos.x // TILE_SIZE, pixel_pos.y // TILE_SIZE)


def is_wall(gx, gy):
    if 0 <= gy < ROWS and 0 <= gx < COLS:
        return MAZE_LAYOUT[gy][gx] == '#'
    return True


def is_gate(gx, gy):
    if 0 <= gy < ROWS and 0 <= gx < COLS:
        return MAZE_LAYOUT[gy][gx] == 'G'
    return False


def is_walkable(gx, gy, allow_gate=False):
    if 0 <= gy < ROWS and 0 <= gx < COLS:
        c = MAZE_LAYOUT[gy][gx]
        if c == '#':
            return False
        if c == 'G' and not allow_gate:
            return False
        return True
    return False


def initial_pellets():
    pellets = set()
    power = set()
    for y, row in enumerate(MAZE_LAYOUT):
        for x, ch in enumerate(row):
            if ch == '.':
                pellets.add((x, y))
            elif ch == 'o':
                power.add((x, y))
    return pellets, power


class Player:
    def __init__(self, start_pos: Vec2):
        self.grid_pos = Vec2(start_pos.x, start_pos.y)
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = Vec2(0, 0)
        self.request_dir = Vec2(0, 0)
        self.radius = TILE_SIZE // 2 - 2
        self.lives = 3
        self.score = 0

    def reset(self, start_pos: Vec2):
        self.grid_pos = Vec2(start_pos.x, start_pos.y)
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = Vec2(0, 0)
        self.request_dir = Vec2(0, 0)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.request_dir = DIRS['UP']
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.request_dir = DIRS['DOWN']
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.request_dir = DIRS['LEFT']
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.request_dir = DIRS['RIGHT']

    def can_move(self, dir_vec: Vec2) -> bool:
        next_pixel = Vec2(self.pixel_pos.x + dir_vec.x * PACMAN_SPEED,
                          self.pixel_pos.y + dir_vec.y * PACMAN_SPEED)
        next_grid = pixel_to_grid(next_pixel)
        return is_walkable(next_grid.x, next_grid.y)

    def update(self, pellets, power_pellets):
        # Teleport through tunnels (wrap horizontally)
        if self.pixel_pos.x < 0:
            self.pixel_pos.x = WIDTH - 1
        elif self.pixel_pos.x >= WIDTH:
            self.pixel_pos.x = 0

        # Try to turn into requested direction when centered on grid cell
        if (self.pixel_pos.x - TILE_SIZE // 2) % TILE_SIZE == 0 and (self.pixel_pos.y - TILE_SIZE // 2) % TILE_SIZE == 0:
            self.grid_pos = pixel_to_grid(self.pixel_pos)
            if self.request_dir != self.dir and is_walkable(self.grid_pos.x + self.request_dir.x, self.grid_pos.y + self.request_dir.y):
                self.dir = Vec2(self.request_dir.x, self.request_dir.y)

        # Move if possible
        if self.dir.x != 0 or self.dir.y != 0:
            next_pixel = Vec2(self.pixel_pos.x + self.dir.x * PACMAN_SPEED,
                              self.pixel_pos.y + self.dir.y * PACMAN_SPEED)
            next_grid = pixel_to_grid(next_pixel)
            # Allow movement only if next grid is walkable
            if is_walkable(next_grid.x, next_grid.y):
                self.pixel_pos = next_pixel
                self.grid_pos = pixel_to_grid(self.pixel_pos)
            else:
                # Snap to center to avoid jitter when hitting walls
                self.pixel_pos = grid_to_pixel(self.grid_pos)

        # Eat pellets
        gp = (self.grid_pos.x, self.grid_pos.y)
        ate_power = False
        if gp in pellets:
            pellets.remove(gp)
            self.score += 10
        if gp in power_pellets:
            power_pellets.remove(gp)
            self.score += 50
            ate_power = True
        return ate_power

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (self.pixel_pos.x, self.pixel_pos.y), self.radius)


class Ghost:
    def __init__(self, name, start_grid: Vec2, color, home_grid: Vec2):
        self.name = name
        self.color = color
        self.start_grid = Vec2(start_grid.x, start_grid.y)
        self.grid_pos = Vec2(start_grid.x, start_grid.y)
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = random.choice(DIR_LIST)
        self.radius = TILE_SIZE // 2 - 3
        self.home_grid = Vec2(home_grid.x, home_grid.y)  # respawn target
        self.state = 'chase'  # 'chase' or 'frightened' or 'eaten'
        self.frightened_until = 0.0
        self.eaten_respawn_at = 0.0

    def reset(self):
        self.grid_pos = Vec2(self.start_grid.x, self.start_grid.y)
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = random.choice(DIR_LIST)
        self.state = 'chase'
        self.frightened_until = 0.0
        self.eaten_respawn_at = 0.0

    def speed(self):
        if self.state == 'frightened':
            return FRIGHTENED_SPEED
        elif self.state == 'eaten':
            return GHOST_SPEED + 1
        return GHOST_SPEED

    def set_frightened(self, now):
        if self.state != 'eaten':
            self.state = 'frightened'
            self.frightened_until = now + POWER_DURATION

    def is_intersection(self):
        options = 0
        for d in DIR_LIST:
            nx, ny = self.grid_pos.x + d.x, self.grid_pos.y + d.y
            if is_walkable(nx, ny):
                options += 1
        return options >= 3

    def choose_dir(self, pacman_grid: Vec2):
        # Valid directions excluding reverse
        reverse = Vec2(-self.dir.x, -self.dir.y)
        candidates = []
        for d in DIR_LIST:
            if d.x == reverse.x and d.y == reverse.y:
                continue
            nx, ny = self.grid_pos.x + d.x, self.grid_pos.y + d.y
            if is_walkable(nx, ny):
                candidates.append(d)
        if not candidates:
            # forced to reverse if dead-end
            self.dir = reverse
            return

        if self.state == 'frightened':
            # Move away from Pacman (simple heuristic): pick dir maximizing distance
            best = None
            best_dist = -1
            for d in candidates:
                nx, ny = self.grid_pos.x + d.x, self.grid_pos.y + d.y
                dist = (nx - pacman_grid.x) ** 2 + (ny - pacman_grid.y) ** 2
                if dist > best_dist:
                    best_dist = dist
                    best = d
            self.dir = best
        elif self.state == 'eaten':
            # Head back to home_grid (simple greedy)
            best = None
            best_dist = 1e9
            for d in candidates:
                nx, ny = self.grid_pos.x + d.x, self.grid_pos.y + d.y
                dist = (nx - self.home_grid.x) ** 2 + (ny - self.home_grid.y) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best = d
            self.dir = best
        else:
            # Chase: random at intersections, otherwise keep direction if possible
            if self.is_intersection():
                self.dir = random.choice(candidates)
            else:
                # keep direction if still valid, else pick random
                nx, ny = self.grid_pos.x + self.dir.x, self.grid_pos.y + self.dir.y
                if not is_walkable(nx, ny):
                    self.dir = random.choice(candidates)

    def update(self, now, pacman_grid: Vec2):
        # Handle frightened expiration
        if self.state == 'frightened' and now > self.frightened_until:
            self.state = 'chase'

        # Handle eaten respawn timer
        if self.state == 'eaten' and now > self.eaten_respawn_at and (self.grid_pos.x, self.grid_pos.y) == (self.home_grid.x, self.home_grid.y):
            self.state = 'chase'

        # Move: change direction only when aligned to grid
        if (self.pixel_pos.x - TILE_SIZE // 2) % TILE_SIZE == 0 and (self.pixel_pos.y - TILE_SIZE // 2) % TILE_SIZE == 0:
            self.grid_pos = pixel_to_grid(self.pixel_pos)
            self.choose_dir(pacman_grid)

        spd = self.speed()
        next_pixel = Vec2(self.pixel_pos.x + self.dir.x * spd, self.pixel_pos.y + self.dir.y * spd)
        next_grid = pixel_to_grid(next_pixel)

        allow_gate = (self.state == 'eaten')  # only eaten ghosts can pass gate
        if is_walkable(next_grid.x, next_grid.y, allow_gate=allow_gate):
            self.pixel_pos = next_pixel
            self.grid_pos = pixel_to_grid(self.pixel_pos)
        else:
            # Stop at wall and pick new direction next tick
            self.pixel_pos = grid_to_pixel(self.grid_pos)

        # wrap tunnels horizontally
        if self.pixel_pos.x < 0:
            self.pixel_pos.x = WIDTH - 1
        elif self.pixel_pos.x >= WIDTH:
            self.pixel_pos.x = 0

    def draw(self, surface):
        if self.state == 'frightened':
            color = FRIGHTENED_COLOR
        elif self.state == 'eaten':
            color = GREY
        else:
            color = self.color
        pygame.draw.circle(surface, color, (self.pixel_pos.x, self.pixel_pos.y), self.radius)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 20)

        # Prepare maze content sets
        self.pellets, self.power_pellets = initial_pellets()

        # Find starting positions: use fixed positions near bottom center for Pacman, and center for ghosts
        self.pacman_start = Vec2(13, 20)
        self.ghost_home = Vec2(13, 13)
        self.ghost_starts = [Vec2(11, 13), Vec2(13, 13), Vec2(15, 13), Vec2(13, 11)]

        self.player = Player(self.pacman_start)
        self.ghosts = [
            Ghost('Blinky', self.ghost_starts[0], (255, 0, 0), self.ghost_home),
            Ghost('Pinky', self.ghost_starts[1], PINK, self.ghost_home),
            Ghost('Inky', self.ghost_starts[2], CYAN, self.ghost_home),
            Ghost('Clyde', self.ghost_starts[3], ORANGE, self.ghost_home),
        ]

        self.state = 'playing'  # 'playing', 'win', 'gameover'
        self.power_active_until = 0.0

    def reset_positions(self, lose_life=False):
        if lose_life:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.state = 'gameover'
        self.player.reset(self.pacman_start)
        for g in self.ghosts:
            g.reset()
        self.power_active_until = 0.0

    def activate_power(self):
        now = time.time()
        self.power_active_until = now + POWER_DURATION
        for g in self.ghosts:
            g.set_frightened(now)

    def update(self):
        if self.state not in ('playing',):
            return

        self.player.handle_input()
        ate_power = self.player.update(self.pellets, self.power_pellets)
        if ate_power:
            self.activate_power()

        now = time.time()
        for g in self.ghosts:
            g.update(now, self.player.grid_pos)

        # Handle collisions between Pacman and ghosts
        for g in self.ghosts:
            if self.collision(self.player, g):
                if g.state == 'frightened':
                    # eat ghost
                    self.player.score += 200
                    g.state = 'eaten'
                    g.eaten_respawn_at = now + GHOST_RESPAWN_TIME
                    # teleport ghost directly to home grid center to simplify
                    g.grid_pos = Vec2(self.ghost_home.x, self.ghost_home.y)
                    g.pixel_pos = grid_to_pixel(g.grid_pos)
                    g.dir = random.choice(DIR_LIST)
                elif g.state != 'eaten':
                    # Pacman loses a life and reset
                    self.reset_positions(lose_life=True)
                    break

        # Check win condition
        if not self.pellets and not self.power_pellets:
            self.state = 'win'

    def collision(self, player: Player, ghost: Ghost) -> bool:
        dx = player.pixel_pos.x - ghost.pixel_pos.x
        dy = player.pixel_pos.y - ghost.pixel_pos.y
        dist = math.hypot(dx, dy)
        return dist < (player.radius + ghost.radius - 4)

    def draw_maze(self, surface):
        surface.fill(BLACK)
        for y, row in enumerate(MAZE_LAYOUT):
            for x, ch in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if ch == '#':
                    pygame.draw.rect(surface, WALL_COLOR, rect)
                elif ch == 'G':
                    pygame.draw.rect(surface, (40, 40, 40), rect)
        # Draw pellets
        for (x, y) in self.pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, PELLET_COLOR, (cx, cy), 3)
        blink = (int(time.time() * 2) % 2) == 0
        for (x, y) in self.power_pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            r = 6 if blink else 4
            pygame.draw.circle(surface, POWER_COLOR, (cx, cy), r)

    def draw_hud(self, surface):
        hud_rect = pygame.Rect(0, ROWS * TILE_SIZE, WIDTH, HEIGHT - ROWS * TILE_SIZE)
        pygame.draw.rect(surface, (20, 20, 20), hud_rect)
        text = self.font.render(f"Score: {self.player.score}   Lives: {self.player.lives}", True, WHITE)
        surface.blit(text, (8, ROWS * TILE_SIZE + 12))
        if self.state == 'win':
            msg = self.font.render("YOU WIN! Press R to restart", True, YELLOW)
            surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, ROWS * TILE_SIZE + 12))
        elif self.state == 'gameover':
            msg = self.font.render("GAME OVER! Press R to restart", True, YELLOW)
            surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, ROWS * TILE_SIZE + 12))

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
                    if event.key == pygame.K_r and self.state in ('win', 'gameover'):
                        # full reset
                        self.player = Player(self.pacman_start)
                        self.ghosts = [
                            Ghost('Blinky', self.ghost_starts[0], (255, 0, 0), self.ghost_home),
                            Ghost('Pinky', self.ghost_starts[1], PINK, self.ghost_home),
                            Ghost('Inky', self.ghost_starts[2], CYAN, self.ghost_home),
                            Ghost('Clyde', self.ghost_starts[3], ORANGE, self.ghost_home),
                        ]
                        self.pellets, self.power_pellets = initial_pellets()
                        self.state = 'playing'

            if self.state == 'playing':
                self.update()

            self.draw_maze(self.screen)
            self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_hud(self.screen)

            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    try:
        Game().run()
    except Exception as e:
        pygame.quit()
        print("Error:", e)
        sys.exit(1)
