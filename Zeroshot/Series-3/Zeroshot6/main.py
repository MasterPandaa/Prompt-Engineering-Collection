import sys
import math
import random
import pygame
from typing import List, Tuple

# Game constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 25  # 32 x 24 grid
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 222)
YELLOW = (255, 204, 0)
RED = (220, 20, 60)
PINK = (255, 100, 150)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 200, 0)
GREY = (120, 120, 120)
DARK_BLUE = (15, 15, 90)
FRIGHTENED_BLUE = (30, 144, 255)

# Maze cell types
WALL = 1
PATH = 0
DOT = 2
POWER = 3

# Scoring
SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST = 200

# Timings
POWER_TIME = 8.0  # seconds frightened
GHOST_RESPAWN_TIME = 3.0

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)
DIRECTIONS = [UP, LEFT, DOWN, RIGHT]


def load_maze() -> List[List[int]]:
    """
    Create a 32x24 maze layout.
    Legend: 1: wall, 0: path (no dot), 2: dot, 3: power pellet
    The outer border is walls. Dots fill most paths.
    """
    # Start with all dots (2)
    maze = [[DOT for _ in range(COLS)] for _ in range(ROWS)]

    # Set borders to walls
    for x in range(COLS):
        maze[0][x] = WALL
        maze[ROWS - 1][x] = WALL
    for y in range(ROWS):
        maze[y][0] = WALL
        maze[y][COLS - 1] = WALL

    # Internal walls (simple classic-like pattern)
    def vline(x, y1, y2):
        for y in range(y1, y2 + 1):
            maze[y][x] = WALL
    def hline(x1, x2, y):
        for x in range(x1, x2 + 1):
            maze[y][x] = WALL

    # Central box for ghost house
    hline(11, 20, 11)
    hline(11, 20, 13)
    vline(11, 11, 13)
    vline(20, 11, 13)
    # Door (path) at center bottom
    maze[13][15] = PATH
    maze[13][16] = PATH

    # Some symmetric walls
    for offset in range(0, 5):
        hline(2, 8, 3 + offset * 3)
        hline(COLS - 9, COLS - 3, 3 + offset * 3)
    vline(6, 2, ROWS - 3)
    vline(COLS - 7, 2, ROWS - 3)

    # Corridors
    for y in [6, 9, 15, 18]:
        hline(2, COLS - 3, y)
    for x in [9, 22]:
        vline(x, 2, ROWS - 3)

    # Clear dots from walls
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == WALL:
                continue
            # ensure paths are dots by default
            if maze[y][x] not in (PATH, POWER):
                maze[y][x] = DOT

    # Make some empty paths (no dot) around ghost house
    for y in range(10, 15):
        for x in range(12, 19):
            if maze[y][x] != WALL:
                maze[y][x] = PATH

    # Place power pellets at corners
    power_positions = [(1, 1), (COLS - 2, 1), (1, ROWS - 2), (COLS - 2, ROWS - 2)]
    for (px, py) in power_positions:
        maze[py][px] = POWER

    return maze


def grid_to_pixel(gx: int, gy: int) -> Tuple[int, int]:
    return gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2


def pixel_to_grid(px: float, py: float) -> Tuple[int, int]:
    return int(px // TILE_SIZE), int(py // TILE_SIZE)


class Entity:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.grid_x = x
        self.grid_y = y
        self.x, self.y = grid_to_pixel(x, y)
        self.dir = STOP
        self.next_dir = STOP
        self.speed = 2.0  # pixels per frame
        self.color = color
        self.radius = TILE_SIZE // 2 - 2

    def set_dir(self, d: Tuple[int, int]):
        self.next_dir = d

    def update_position(self, maze: List[List[int]]):
        # Attempt to turn if at center of tile
        cx, cy = grid_to_pixel(self.grid_x, self.grid_y)
        at_center = abs(self.x - cx) < 1.0 and abs(self.y - cy) < 1.0

        if at_center and self.next_dir != self.dir:
            nx = self.grid_x + self.next_dir[0]
            ny = self.grid_y + self.next_dir[1]
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != WALL:
                self.dir = self.next_dir

        # If heading into wall, stop at center
        nx = self.grid_x + self.dir[0]
        ny = self.grid_y + self.dir[1]
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == WALL and at_center:
            self.dir = STOP

        # Move
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

        # Warp to center on small deviations to keep grid alignment
        if at_center and self.dir != STOP:
            self.x, self.y = cx + self.dir[0] * self.speed, cy + self.dir[1] * self.speed

        # Update grid position
        self.grid_x, self.grid_y = pixel_to_grid(self.x, self.y)

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


class Pacman(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, YELLOW)
        self.speed = 3.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.set_dir(UP)
        elif keys[pygame.K_DOWN]:
            self.set_dir(DOWN)
        elif keys[pygame.K_LEFT]:
            self.set_dir(LEFT)
        elif keys[pygame.K_RIGHT]:
            self.set_dir(RIGHT)

    def draw(self, surf: pygame.Surface):
        # Simple circle for Pacman
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


class Ghost(Entity):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], name: str):
        super().__init__(x, y, color)
        self.base_color = color
        self.name = name
        self.speed = 2.2
        self.state = 'normal'  # normal, frightened, eaten
        self.fright_timer = 0.0
        self.respawn_timer = 0.0
        self.home = (x, y)

    def is_at_center(self):
        cx, cy = grid_to_pixel(self.grid_x, self.grid_y)
        return abs(self.x - cx) < 1.0 and abs(self.y - cy) < 1.0

    def available_dirs(self, maze: List[List[int]]):
        dirs = []
        for d in DIRECTIONS:
            nx = self.grid_x + d[0]
            ny = self.grid_y + d[1]
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != WALL:
                # Disallow reversing unless forced (optional, keep allowed for simplicity)
                dirs.append(d)
        return dirs

    def choose_dir(self, maze: List[List[int]], pac_pos: Tuple[int, int]):
        if not self.is_at_center():
            return  # only choose at center

        choices = self.available_dirs(maze)
        if not choices:
            self.dir = STOP
            return

        # Prevent immediate reversal to avoid jitter, unless dead end
        reverse = (-self.dir[0], -self.dir[1])
        non_reverse = [d for d in choices if d != reverse]
        if non_reverse:
            choices = non_reverse

        if self.state == 'frightened':
            # Random movement with slight bias away from Pacman
            def score(d):
                tx, ty = self.grid_x + d[0], self.grid_y + d[1]
                return random.random() + 0.5 * manhattan((tx, ty), pac_pos)
            self.dir = max(choices, key=score)
        elif self.state == 'eaten':
            # Go back to home using greedy
            def score(d):
                tx, ty = self.grid_x + d[0], self.grid_y + d[1]
                return -manhattan((tx, ty), self.home)
            self.dir = max(choices, key=score)
        else:
            # normal: bias toward Pacman with some randomness
            def score(d):
                tx, ty = self.grid_x + d[0], self.grid_y + d[1]
                return -manhattan((tx, ty), pac_pos) + random.uniform(-0.2, 0.2)
            self.dir = max(choices, key=score)

    def update(self, maze: List[List[int]], pac_pos: Tuple[int, int], dt: float):
        # Update timers and state
        if self.state == 'frightened':
            self.fright_timer -= dt
            self.color = FRIGHTENED_BLUE if int(self.fright_timer * 4) % 2 == 0 else WHITE
            spd = 1.6
            if self.fright_timer <= 0:
                self.state = 'normal'
                self.color = self.base_color
        elif self.state == 'eaten':
            self.color = GREY
            spd = 3.0
            if (self.grid_x, self.grid_y) == self.home:
                self.respawn_timer -= dt
                if self.respawn_timer <= 0:
                    self.state = 'normal'
                    self.color = self.base_color
        else:
            self.color = self.base_color
            spd = 2.2

        old_speed = self.speed
        self.speed = spd
        self.choose_dir(maze, pac_pos)
        self.update_position(maze)
        self.speed = old_speed  # do not persist speed changes outside state

    def frighten(self):
        if self.state == 'eaten':
            return
        self.state = 'frightened'
        self.fright_timer = POWER_TIME

    def eaten(self):
        self.state = 'eaten'
        self.respawn_timer = GHOST_RESPAWN_TIME


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman - Pygame')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)

        self.maze = load_maze()
        # Count dots for win condition
        self.total_dots = sum(1 for row in self.maze for c in row if c in (DOT, POWER))

        # Starting positions
        self.pac_start = (16, 17)
        self.ghost_starts = [(15, 12), (16, 12), (17, 12), (15, 10)]

        self.reset()

    def reset(self):
        self.pacman = Pacman(*self.pac_start)
        colors = [RED, PINK, CYAN, ORANGE]
        names = ['blinky', 'pinky', 'inky', 'clyde']
        self.ghosts: List[Ghost] = []
        for i, pos in enumerate(self.ghost_starts):
            if i >= 4:
                break
            g = Ghost(pos[0], pos[1], colors[i % len(colors)], names[i % len(names)])
            self.ghosts.append(g)
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

    def restart_round(self):
        # Restore Pacman and ghosts to start positions for a life loss
        self.pacman = Pacman(*self.pac_start)
        for i, g in enumerate(self.ghosts):
            pos = self.ghost_starts[i % len(self.ghost_starts)]
            g.grid_x, g.grid_y = pos
            g.x, g.y = grid_to_pixel(*pos)
            g.dir = STOP
            g.next_dir = STOP
            g.state = 'normal'
            g.color = g.base_color
            g.fright_timer = 0.0
            g.respawn_timer = 0.0

    def handle_collisions(self, dt: float):
        gx, gy = self.pacman.grid_x, self.pacman.grid_y
        cell = self.maze[gy][gx]
        if cell == DOT:
            self.maze[gy][gx] = PATH
            self.score += SCORE_DOT
            self.total_dots -= 1
        elif cell == POWER:
            self.maze[gy][gx] = PATH
            self.score += SCORE_POWER
            self.total_dots -= 1
            for g in self.ghosts:
                g.frighten()

        # Ghost collisions
        for g in self.ghosts:
            if manhattan((gx, gy), (g.grid_x, g.grid_y)) <= 0:
                # close enough on grid; also check pixel distance
                if math.hypot(self.pacman.x - g.x, self.pacman.y - g.y) < TILE_SIZE * 0.6:
                    if g.state == 'frightened':
                        g.eaten()
                        self.score += SCORE_GHOST
                    elif g.state != 'eaten':
                        # Lose life
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_over = True
                        else:
                            self.restart_round()
                        break

        if self.total_dots <= 0:
            self.win = True
            self.game_over = True

    def draw_maze(self):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.maze[y][x] == WALL:
                    pygame.draw.rect(self.screen, BLUE, rect)
                else:
                    # draw paths subtly
                    pygame.draw.rect(self.screen, DARK_BLUE, rect)
                    if self.maze[y][x] == DOT:
                        cx, cy = grid_to_pixel(x, y)
                        pygame.draw.circle(self.screen, WHITE, (cx, cy), 3)
                    elif self.maze[y][x] == POWER:
                        cx, cy = grid_to_pixel(x, y)
                        pygame.draw.circle(self.screen, WHITE, (cx, cy), 6)

    def draw_hud(self):
        # Score and lives
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 5))
        # Lives as small circles
        for i in range(self.lives):
            pygame.draw.circle(self.screen, YELLOW, (WIDTH - 20 - i * 20, 15), 8)

    def draw_game_over(self):
        msg = 'YOU WIN!' if self.win else 'GAME OVER'
        text = self.font.render(msg + ' - Press R to Restart or ESC to Quit', True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, rect)

    def update(self, dt: float):
        if self.game_over:
            return
        self.pacman.handle_input()
        self.pacman.update_position(self.maze)
        for g in self.ghosts:
            g.update(self.maze, (self.pacman.grid_x, self.pacman.grid_y), dt)
        self.handle_collisions(dt)

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)
        self.draw_hud()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if self.game_over and event.key == pygame.K_r:
                        # Reset maze and state
                        self.maze = load_maze()
                        self.total_dots = sum(1 for row in self.maze for c in row if c in (DOT, POWER))
                        self.reset()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
