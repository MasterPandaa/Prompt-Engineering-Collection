import pygame
import sys
import math
import random
from collections import deque

# -----------------------------
# Configuration and Constants
# -----------------------------
CELL_SIZE = 24
COLS = 28
ROWS = 31
SCREEN_WIDTH = COLS * CELL_SIZE
SCREEN_HEIGHT = ROWS * CELL_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (6, 6, 45)
WHITE = (255, 255, 255)
YELLOW = (255, 206, 0)
BLUE = (33, 33, 255)
PINK = (255, 105, 180)
RED = (255, 60, 60)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (200, 200, 200)

# Maze tiles
WALL = '#'
DOT = '.'
POWER = 'o'
EMPTY = ' '
GHOST_GATE = '='  # gate in front of the ghost house

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT, STOP: STOP}

# Ghost states
GHOST_NORMAL = 'normal'
GHOST_VULNERABLE = 'vulnerable'
GHOST_EYES = 'eyes'

# -----------------------------
# Maze Layout (28x31)
# Legend: '#' wall, '.' dot, 'o' power pellet, ' ' empty, '=' ghost gate
# -----------------------------
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
    "     #.## ###==### ##.#     ",
    "######.## #      # ##.######",
    "      .   # G  G #   .      ",
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
    "#.####.#####.##.#####.####.#",
    "#o........................o#",
    "############################",
    "                            ",
]
# Row 30 is dummy padding for wrap logic "tunnels" alignment

# Replace spaces outside with walls except the tunnel entrances
# For simplicity the layout is already well-formed to 28x31 visible rows.

# -----------------------------
# Utility functions
# -----------------------------

def grid_to_pix(cell):
    x, y = cell
    return int(x * CELL_SIZE + CELL_SIZE / 2), int(y * CELL_SIZE + CELL_SIZE / 2)


def pix_to_grid(pos):
    x, y = pos
    return int(x // CELL_SIZE), int(y // CELL_SIZE)


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# -----------------------------
# Maze Class
# -----------------------------
class Maze:
    def __init__(self):
        self.grid = [list(row) for row in MAZE_LAYOUT[:ROWS]]
        self.dots_total = sum(row.count(DOT) for row in self.grid) + sum(row.count(POWER) for row in self.grid)
        # Precompute wall rects for drawing
        self.wall_rects = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == WALL:
                    self.wall_rects.append(pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def is_wall(self, cell):
        x, y = cell
        if x < 0:
            x = COLS - 1
        elif x >= COLS:
            x = 0
        if y < 0 or y >= ROWS:
            return True
        return self.grid[y][x] == WALL

    def is_gate(self, cell):
        x, y = cell
        if 0 <= y < ROWS and 0 <= x < COLS:
            return self.grid[y][x] == GHOST_GATE
        return False

    def eat(self, cell):
        x, y = cell
        if 0 <= x < COLS and 0 <= y < ROWS:
            if self.grid[y][x] == DOT:
                self.grid[y][x] = EMPTY
                self.dots_total -= 1
                return 'dot'
            elif self.grid[y][x] == POWER:
                self.grid[y][x] = EMPTY
                self.dots_total -= 1
                return 'power'
        return None

    def remaining_pellets(self):
        return self.dots_total

    def draw(self, surface):
        # Background
        surface.fill(NAVY)
        # Walls
        for rect in self.wall_rects:
            pygame.draw.rect(surface, BLUE, rect, border_radius=4)
        # Dots and power pellets
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                cx, cy = grid_to_pix((x, y))
                if cell == DOT:
                    pygame.draw.circle(surface, GREY, (cx, cy), 3)
                elif cell == POWER:
                    pygame.draw.circle(surface, WHITE, (cx, cy), 6)


# -----------------------------
# Player Class
# -----------------------------
class Player:
    def __init__(self, start_cell):
        self.start_cell = start_cell
        self.reset()

    def reset(self):
        self.cell = self.start_cell
        self.pos = list(grid_to_pix(self.cell))
        self.direction = STOP
        self.next_direction = STOP
        self.speed = 2.0
        self.radius = CELL_SIZE // 2 - 2
        self.alive = True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = RIGHT

    def can_move(self, maze, cell, direction):
        nx = cell[0] + direction[0]
        ny = cell[1] + direction[1]
        # Wrap horizontally through tunnels
        if nx < 0:
            nx = COLS - 1
        elif nx >= COLS:
            nx = 0
        if maze.is_wall((nx, ny)) or maze.is_gate((nx, ny)):
            return False
        return True

    def at_center_of_cell(self):
        cx, cy = grid_to_pix(self.cell)
        return abs(self.pos[0] - cx) < 2 and abs(self.pos[1] - cy) < 2

    def update(self, maze):
        # Input first
        self.handle_input()
        # Snap to center when close
        if self.at_center_of_cell():
            self.pos = list(grid_to_pix(self.cell))
            # If there is a pending turn and it is valid, do it now
            if self.next_direction != self.direction and self.can_move(maze, self.cell, self.next_direction):
                self.direction = self.next_direction
            # If blocked ahead, stop
            if not self.can_move(maze, self.cell, self.direction):
                self.direction = STOP
            # Move to next cell center if moving
            if self.direction != STOP:
                nx = self.cell[0] + self.direction[0]
                ny = self.cell[1] + self.direction[1]
                if nx < 0:
                    nx = COLS - 1
                elif nx >= COLS:
                    nx = 0
                self.cell = (nx, ny)
        # Move position toward the center of current cell
        target = grid_to_pix(self.cell)
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = min(self.speed, dist)
            self.pos[0] += dx / dist * step
            self.pos[1] += dy / dist * step

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), CELL_SIZE // 2 - 2)


# -----------------------------
# Ghost Class
# -----------------------------
class Ghost:
    def __init__(self, name, color, start_cell, ghost_type='chaser'):
        self.name = name
        self.color = color
        self.start_cell = start_cell
        self.ghost_type = ghost_type  # 'chaser' or 'random'
        self.reset()

    def reset(self):
        self.cell = self.start_cell
        self.pos = list(grid_to_pix(self.cell))
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = 1.8
        self.state = GHOST_NORMAL
        self.vulnerable_timer = 0
        self.home_cell = self.start_cell

    def set_vulnerable(self, duration_ms):
        if self.state == GHOST_EYES:
            return
        self.state = GHOST_VULNERABLE
        self.vulnerable_timer = duration_ms

    def eaten(self):
        self.state = GHOST_EYES
        self.speed = 2.4

    def revive_if_at_home(self):
        if self.state == GHOST_EYES and self.cell == self.home_cell:
            self.state = GHOST_NORMAL
            self.speed = 1.8
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def can_move(self, maze, cell, direction):
        nx = cell[0] + direction[0]
        ny = cell[1] + direction[1]
        if nx < 0:
            nx = COLS - 1
        elif nx >= COLS:
            nx = 0
        if ny < 0 or ny >= ROWS:
            return False
        if maze.is_wall((nx, ny)):
            return False
        # Allow ghosts to pass gate only when eyes (returning home)
        if maze.is_gate((nx, ny)) and self.state != GHOST_EYES:
            return False
        return True

    def at_center_of_cell(self):
        cx, cy = grid_to_pix(self.cell)
        return abs(self.pos[0] - cx) < 2 and abs(self.pos[1] - cy) < 2

    def choose_direction(self, maze, target_cell):
        # At intersections choose next direction
        valid_dirs = []
        for d in [UP, DOWN, LEFT, RIGHT]:
            if d == OPPOSITE.get(self.direction):
                continue  # avoid reversing unless dead-end
            if self.can_move(maze, self.cell, d):
                valid_dirs.append(d)
        if not valid_dirs:
            # must reverse
            rev = OPPOSITE.get(self.direction, STOP)
            if self.can_move(maze, self.cell, rev):
                return rev
            # else pick any possible
            for d in [UP, DOWN, LEFT, RIGHT]:
                if self.can_move(maze, self.cell, d):
                    return d
            return STOP

        if self.state == GHOST_VULNERABLE and self.ghost_type == 'chaser':
            # When vulnerable, chaser prefers to flee (maximize distance)
            best = max(valid_dirs, key=lambda d: self._heuristic(self._next_cell(self.cell, d), target_cell))
            return best

        if self.ghost_type == 'random':
            return random.choice(valid_dirs)

        # chaser minimizes distance heuristic
        best = min(valid_dirs, key=lambda d: self._heuristic(self._next_cell(self.cell, d), target_cell))
        return best

    def _heuristic(self, a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _next_cell(self, cell, direction):
        nx = cell[0] + direction[0]
        ny = cell[1] + direction[1]
        if nx < 0:
            nx = COLS - 1
        elif nx >= COLS:
            nx = 0
        return (nx, ny)

    def update(self, maze, player_cell, dt_ms):
        # Update vulnerable timer
        if self.state == GHOST_VULNERABLE:
            self.vulnerable_timer -= dt_ms
            if self.vulnerable_timer <= 0:
                self.state = GHOST_NORMAL
                self.speed = 1.8

        # Decide direction at cell centers
        if self.at_center_of_cell():
            self.pos = list(grid_to_pix(self.cell))
            target = player_cell
            if self.state == GHOST_EYES:
                target = self.home_cell
            self.direction = self.choose_direction(maze, target)
            if self.direction != STOP and self.can_move(maze, self.cell, self.direction):
                self.cell = self._next_cell(self.cell, self.direction)
        # Move toward center
        target_pix = grid_to_pix(self.cell)
        dx = target_pix[0] - self.pos[0]
        dy = target_pix[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        speed = self.speed * (0.6 if self.state == GHOST_VULNERABLE else 1.0)
        if dist > 0:
            step = min(speed, dist)
            self.pos[0] += dx / dist * step
            self.pos[1] += dy / dist * step

        # Revive when eyes reach home
        self.revive_if_at_home()

    def draw(self, surface):
        cx, cy = int(self.pos[0]), int(self.pos[1])
        if self.state == GHOST_EYES:
            color = WHITE
        elif self.state == GHOST_VULNERABLE:
            color = CYAN
        else:
            color = self.color
        pygame.draw.circle(surface, color, (cx, cy), CELL_SIZE // 2 - 2)


# -----------------------------
# Game Class
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman - Simple OOP Clone')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)

        self.maze = Maze()

        # Define start positions (grid)
        self.player_start = (13, 23)
        self.player = Player(self.player_start)

        # Ghosts in house area
        self.ghosts = [
            Ghost('Blinky', RED, (13, 14), 'chaser'),
            Ghost('Pinky', PINK, (14, 14), 'random'),
        ]

        self.score = 0
        self.lives = 3
        self.level = 1
        self.power_duration_ms = 6000
        self.ghost_score_base = 200
        self.ghost_combo = 0
        self.game_over = False

    def reset_positions(self):
        self.player.reset()
        for g in self.ghosts:
            g.reset()

    def next_level(self):
        # Rebuild maze with pellets
        self.maze = Maze()
        self.level += 1
        self.reset_positions()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt_ms):
        if self.game_over:
            return
        self.player.update(self.maze)
        for g in self.ghosts:
            g.update(self.maze, self.player.cell, dt_ms)

        # Eat pellets
        ate = self.maze.eat(self.player.cell)
        if ate == 'dot':
            self.score += 10
        elif ate == 'power':
            self.score += 50
            self.ghost_combo = 0
            for g in self.ghosts:
                g.set_vulnerable(self.power_duration_ms)

        # Collisions with ghosts
        for g in self.ghosts:
            if distance(self.player.pos, g.pos) < CELL_SIZE * 0.6:
                if g.state == GHOST_VULNERABLE:
                    g.eaten()
                    self.ghost_combo += 1
                    self.score += self.ghost_score_base * (2 ** (self.ghost_combo - 1))
                elif g.state == GHOST_NORMAL:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_positions()
                    break

        # Level complete
        if self.maze.remaining_pellets() <= 0:
            self.next_level()

    def draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_surf = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_surf, (8, SCREEN_HEIGHT - 24))
        self.screen.blit(lives_surf, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT - 24))
        self.screen.blit(level_surf, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 24))

    def draw(self):
        self.maze.draw(self.screen)
        # Draw gate
        for y, row in enumerate(self.maze.grid):
            for x, c in enumerate(row):
                if c == GHOST_GATE:
                    pygame.draw.rect(self.screen, WHITE, (x * CELL_SIZE + 4, y * CELL_SIZE + CELL_SIZE//2 - 2, CELL_SIZE - 8, 4))
        # Draw actors
        self.player.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_hud()

        if self.game_over:
            over = self.font.render("GAME OVER - Press R to Restart", True, WHITE)
            self.screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def handle_restart(self):
        keys = pygame.key.get_pressed()
        if self.game_over and keys[pygame.K_r]:
            self.__init__()

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt_ms)
            self.draw()
            self.handle_restart()


if __name__ == '__main__':
    Game().run()
