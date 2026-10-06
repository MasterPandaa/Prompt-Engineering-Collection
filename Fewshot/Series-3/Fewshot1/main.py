import math
import random
import sys
from dataclasses import dataclass

import pygame

# ------------------------------------
# Config & Maze Layout (Grid-based)
# 1 = Wall, 0 = Empty, 2 = Pellet, 3 = Power Pellet
# ------------------------------------
maze_layout = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1],
]

ROWS = len(maze_layout)
COLS = len(maze_layout[0])
TILE_SIZE = 48  # size of one tile in pixels
MAZE_WIDTH = COLS * TILE_SIZE
MAZE_HEIGHT = ROWS * TILE_SIZE
HUD_HEIGHT = 80
SCREEN_WIDTH = MAZE_WIDTH
SCREEN_HEIGHT = MAZE_HEIGHT + HUD_HEIGHT

FPS = 60
PACMAN_SPEED = 140  # px/sec
GHOST_SPEED = 120   # px/sec
FRIGHTENED_DURATION = 6.0  # seconds
RESPAWN_DELAY = 1.2  # seconds after death or eat ghost

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
WALL_BLUE = (0, 80, 200)
PELLET_COLOR = (255, 200, 50)
POWER_COLOR = (255, 80, 80)
PACMAN_YELLOW = (255, 255, 0)
GHOST_RED = (255, 0, 0)
GHOST_PINK = (255, 105, 180)
FRIGHTENED_BLUE = (30, 144, 255)

# Directions as vectors
DIR_VECTORS = {
    'STOP': (0, 0),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
}
ALL_DIRS = ['LEFT', 'RIGHT', 'UP', 'DOWN']


def grid_to_px(cell):
    cx, cy = cell
    return cx * TILE_SIZE + TILE_SIZE // 2, cy * TILE_SIZE + TILE_SIZE // 2


def px_to_grid(pos):
    x, y = pos
    return int(x // TILE_SIZE), int(y // TILE_SIZE)


def is_wall(cell):
    x, y = cell
    if 0 <= y < ROWS and 0 <= x < COLS:
        return maze_layout[y][x] == 1
    return True


def is_walkable(cell):
    return not is_wall(cell)


def at_center_of_cell(pos):
    gx, gy = px_to_grid(pos)
    cx, cy = grid_to_px((gx, gy))
    # Allow small threshold to treat as centered
    return abs(pos[0] - cx) < 2 and abs(pos[1] - cy) < 2


def clamp_to_cell_center(pos):
    gx, gy = px_to_grid(pos)
    return list(grid_to_px((gx, gy)))


@dataclass
class Entity:
    x: float
    y: float
    speed: float
    direction: str

    def pos(self):
        return [self.x, self.y]

    def set_pos(self, p):
        self.x, self.y = p[0], p[1]

    def move(self, dt):
        vx, vy = DIR_VECTORS[self.direction]
        self.x += vx * self.speed * dt
        self.y += vy * self.speed * dt


class Pacman(Entity):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed, 'STOP')
        self.next_direction = 'STOP'
        self.radius = TILE_SIZE // 2 - 4

    def update(self, dt):
        # Try to turn when centered and path ahead is valid
        if at_center_of_cell(self.pos()):
            if self.next_direction != self.direction:
                if self.can_move(self.next_direction):
                    self.set_pos(clamp_to_cell_center(self.pos()))
                    self.direction = self.next_direction
            # If current dir blocked, stop
            if not self.can_move(self.direction):
                self.direction = 'STOP'
        self.move(dt)
        # Prevent entering walls due to overshoot
        if is_wall(next_cell(self.pos(), self.direction)):
            # Clamp back to cell center when hitting a wall
            if not is_wall(px_to_grid(self.pos())):
                if not self.can_move(self.direction):
                    self.set_pos(clamp_to_cell_center(self.pos()))

    def can_move(self, direction):
        if direction == 'STOP':
            return True
        nx, ny = next_cell(self.pos(), direction)
        return is_walkable((nx, ny))


class Ghost(Entity):
    def __init__(self, x, y, speed, color):
        super().__init__(x, y, speed, random.choice(ALL_DIRS))
        self.color = color
        self.spawn = (x, y)
        self.radius = TILE_SIZE // 2 - 6
        self.respawn_timer = 0.0

    def reset_to_spawn(self):
        self.set_pos([self.spawn[0], self.spawn[1]])
        self.direction = random.choice(ALL_DIRS)
        self.respawn_timer = 0.0

    def update(self, dt, frightened=False):
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            return
        # When at cell center, consider turning
        if at_center_of_cell(self.pos()):
            self.set_pos(clamp_to_cell_center(self.pos()))
            self.direction = choose_random_direction(self.pos(), self.direction)
        self.move(dt)
        # Avoid entering walls: clamp and choose another direction
        if is_wall(next_cell(self.pos(), self.direction)):
            if not is_wall(px_to_grid(self.pos())):
                self.set_pos(clamp_to_cell_center(self.pos()))
                self.direction = choose_random_direction(self.pos(), opp_dir(self.direction))


# Utilities for movement

def next_cell(pos, direction):
    vx, vy = DIR_VECTORS[direction]
    gx, gy = px_to_grid(pos)
    return gx + vx, gy + vy


def opp_dir(direction):
    if direction == 'LEFT':
        return 'RIGHT'
    if direction == 'RIGHT':
        return 'LEFT'
    if direction == 'UP':
        return 'DOWN'
    if direction == 'DOWN':
        return 'UP'
    return 'STOP'


def available_dirs_from(pos):
    gx, gy = px_to_grid(pos)
    dirs = []
    for d in ALL_DIRS:
        vx, vy = DIR_VECTORS[d]
        nx, ny = gx + vx, gy + vy
        if is_walkable((nx, ny)):
            dirs.append(d)
    return dirs


def choose_random_direction(pos, exclude_direction=None):
    options = available_dirs_from(pos)
    # Avoid reversing unless it's a dead end
    if exclude_direction and opp_dir(exclude_direction) in options and len(options) > 1:
        options.remove(opp_dir(exclude_direction))
    if not options:
        return opp_dir(exclude_direction) if exclude_direction else 'STOP'
    return random.choice(options)


# Game state
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Contoh Pacman')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 22)
        self.big_font = pygame.font.SysFont('arial', 34, bold=True)

        # Initialize maze pellets copy so we can modify during play
        self.maze = [row[:] for row in maze_layout]

        # Spawn positions (grid to px)
        pac_start = grid_to_px((3, 3))
        ghost1_start = grid_to_px((1, 1))
        ghost2_start = grid_to_px((5, 5))

        self.pacman = Pacman(pac_start[0], pac_start[1], PACMAN_SPEED)
        self.ghosts = [
            Ghost(ghost1_start[0], ghost1_start[1], GHOST_SPEED, GHOST_RED),
            Ghost(ghost2_start[0], ghost2_start[1], GHOST_SPEED, GHOST_PINK),
        ]

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.frightened = False
        self.fright_timer = 0.0
        self.death_timer = 0.0

    def reset_after_life_lost(self):
        # Reset positions and timers
        pac_start = grid_to_px((3, 3))
        self.pacman.set_pos([pac_start[0], pac_start[1]])
        self.pacman.direction = 'STOP'
        self.pacman.next_direction = 'STOP'
        for g in self.ghosts:
            g.reset_to_spawn()
        self.frightened = False
        self.fright_timer = 0.0
        self.death_timer = RESPAWN_DELAY

    def restart(self):
        self.__init__()

    def update(self, dt):
        if self.game_over or self.win:
            return

        # Handle frightened timer
        if self.frightened:
            self.fright_timer -= dt
            if self.fright_timer <= 0:
                self.frightened = False
                self.fright_timer = 0.0

        # Wait during death timer
        if self.death_timer > 0:
            self.death_timer -= dt
            return

        # Update Pacman
        self.pacman.update(dt)
        self.handle_pellet_consumption()

        # Update Ghosts
        for g in self.ghosts:
            g.update(dt, frightened=self.frightened)

        # Collisions Pacman-Ghosts
        self.handle_collisions()

        # Win condition (no pellets or power pellets left)
        if not any(2 in row or 3 in row for row in self.maze):
            self.win = True

    def handle_pellet_consumption(self):
        gx, gy = px_to_grid(self.pacman.pos())
        if 0 <= gy < ROWS and 0 <= gx < COLS:
            tile = self.maze[gy][gx]
            if tile == 2:
                self.score += 10
                self.maze[gy][gx] = 0
            elif tile == 3:
                self.score += 50
                self.maze[gy][gx] = 0
                self.frightened = True
                self.fright_timer = FRIGHTENED_DURATION

    def handle_collisions(self):
        for g in self.ghosts:
            if g.respawn_timer > 0:
                continue
            if dist(self.pacman.pos(), g.pos()) < (self.pacman.radius + g.radius - 8):
                if self.frightened:
                    # Eat ghost
                    self.score += 200
                    g.respawn_timer = RESPAWN_DELAY
                    g.reset_to_spawn()
                else:
                    # Pacman loses a life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        return
                    self.reset_after_life_lost()
                    return

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r and (self.game_over or self.win):
                    self.restart()
                if event.key == pygame.K_LEFT:
                    self.pacman.next_direction = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_direction = 'RIGHT'
                elif event.key == pygame.K_UP:
                    self.pacman.next_direction = 'UP'
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_direction = 'DOWN'

    def draw(self):
        self.screen.fill(BLACK)
        # Draw maze area background
        pygame.draw.rect(self.screen, GRAY, (0, 0, MAZE_WIDTH, MAZE_HEIGHT))

        # Draw walls and pellets
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.maze[y][x]
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                if tile == 1:
                    pygame.draw.rect(self.screen, WALL_BLUE, (px, py, TILE_SIZE, TILE_SIZE), border_radius=6)
                elif tile == 2:
                    cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
                    pygame.draw.circle(self.screen, PELLET_COLOR, (cx, cy), 5)
                elif tile == 3:
                    cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
                    pygame.draw.circle(self.screen, POWER_COLOR, (cx, cy), 9)

        # Draw Pacman
        pac_color = PACMAN_YELLOW
        cx, cy = int(self.pacman.x), int(self.pacman.y)
        pygame.draw.circle(self.screen, pac_color, (cx, cy), self.pacman.radius)

        # Draw Ghosts
        for g in self.ghosts:
            if g.respawn_timer > 0:
                continue
            color = FRIGHTENED_BLUE if self.frightened else g.color
            gx, gy = int(g.x), int(g.y)
            pygame.draw.circle(self.screen, color, (gx, gy), g.radius)

        # HUD Area
        pygame.draw.rect(self.screen, BLACK, (0, MAZE_HEIGHT, SCREEN_WIDTH, HUD_HEIGHT))
        # Score and Lives
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (16, MAZE_HEIGHT + 16))
        self.screen.blit(lives_surf, (16, MAZE_HEIGHT + 44))

        # State messages
        if self.frightened:
            msg = self.font.render(f"Power-Up: {self.fright_timer:0.1f}s", True, POWER_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH - msg.get_width() - 16, MAZE_HEIGHT + 16))
        if self.game_over:
            text = self.big_font.render("GAME OVER - Press R to Restart", True, WHITE)
            self.screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, (MAZE_HEIGHT - text.get_height()) // 2))
        if self.win:
            text = self.big_font.render("YOU WIN! - Press R to Restart", True, WHITE)
            self.screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, (MAZE_HEIGHT - text.get_height()) // 2))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()


# Math helper

def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


if __name__ == '__main__':
    Game().run()
