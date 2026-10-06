import sys
import math
import random
import pygame
from typing import List, Tuple, Set

# ------------------------------
# Config & Constants
# ------------------------------
# Tile definitions:
# 1 = Wall, 0 = Empty, 2 = Pellet, 3 = Power Pellet
maze_layout: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

TILE_SIZE = 64  # Scales the board. 64x64 px per tile = 448x448 window for 7x7
MAZE_ROWS = len(maze_layout)
MAZE_COLS = len(maze_layout[0])
WIDTH = MAZE_COLS * TILE_SIZE
HEIGHT = MAZE_ROWS * TILE_SIZE + 64  # extra space for UI (score bar)
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
NAVY = (0, 30, 80)
YELLOW = (255, 210, 0)
WHITE = (255, 255, 255)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)
GREEN = (50, 220, 120)
RED = (255, 60, 60)
GREY = (100, 100, 100)

# Gameplay
PACMAN_SPEED = 3.0
GHOST_SPEED = 2.6
POWER_DURATION_MS = 6000
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
GHOST_EAT_SCORE = 200

UI_HEIGHT = 64
FONT_NAME = None  # default system font

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)


# ------------------------------
# Helper Functions
# ------------------------------

def add_tuple(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return (a[0] + b[0], a[1] + b[1])


def opposite(dir_: Tuple[int, int]) -> Tuple[int, int]:
    return (-dir_[0], -dir_[1])


def grid_to_pixel(cell: Tuple[int, int]) -> Tuple[float, float]:
    c, r = cell
    x = c * TILE_SIZE + TILE_SIZE / 2
    y = r * TILE_SIZE + TILE_SIZE / 2 + UI_HEIGHT
    return (x, y)


def pixel_to_grid(pos: Tuple[float, float]) -> Tuple[int, int]:
    x, y = pos
    y -= UI_HEIGHT
    c = int(x // TILE_SIZE)
    r = int(y // TILE_SIZE)
    return (c, r)


def is_centered(pos: Tuple[float, float]) -> bool:
    x, y = pos
    gx = (x - TILE_SIZE / 2) % TILE_SIZE
    gy = (y - UI_HEIGHT - TILE_SIZE / 2) % TILE_SIZE
    return abs(gx) < 0.5 and abs(gy) < 0.5


# ------------------------------
# Maze
# ------------------------------
class Maze:
    def __init__(self, layout: List[List[int]]):
        self.layout = [row[:] for row in layout]
        self.rows = len(self.layout)
        self.cols = len(self.layout[0])
        self.pellets: Set[Tuple[int, int]] = set()
        self.power_pellets: Set[Tuple[int, int]] = set()
        self._scan_pellets()

    def _scan_pellets(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == 2:
                    self.pellets.add((c, r))
                elif self.layout[r][c] == 3:
                    self.power_pellets.add((c, r))

    def in_bounds(self, cell: Tuple[int, int]) -> bool:
        c, r = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_wall(self, cell: Tuple[int, int]) -> bool:
        if not self.in_bounds(cell):
            return True
        c, r = cell
        return self.layout[r][c] == 1

    def eat_at(self, cell: Tuple[int, int]) -> int:
        """
        Returns score gained by eating at this cell.
        """
        if cell in self.pellets:
            self.pellets.remove(cell)
            self.layout[cell[1]][cell[0]] = 0
            return PELLET_SCORE
        if cell in self.power_pellets:
            self.power_pellets.remove(cell)
            self.layout[cell[1]][cell[0]] = 0
            return POWER_PELLET_SCORE
        return 0

    def remaining_dots(self) -> int:
        return len(self.pellets) + len(self.power_pellets)

    def neighbors_open(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        c, r = cell
        candidates = [(c+1, r), (c-1, r), (c, r+1), (c, r-1)]
        return [p for p in candidates if not self.is_wall(p)]

    def draw(self, screen: pygame.Surface):
        # Background playfield
        screen.fill(BLACK)
        pygame.draw.rect(screen, NAVY, (0, UI_HEIGHT, WIDTH, HEIGHT - UI_HEIGHT))

        # Walls
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == 1:
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE + UI_HEIGHT
                    pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))

        # Pellets
        for (c, r) in self.pellets:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT
            pygame.draw.circle(screen, WHITE, (cx, cy), max(4, TILE_SIZE // 12))

        # Power pellets (pulse)
        pulse = 2 + int(2 * math.sin(pygame.time.get_ticks() / 150.0))
        for (c, r) in self.power_pellets:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT
            pygame.draw.circle(screen, ORANGE, (cx, cy), max(8, TILE_SIZE // 6) + pulse)


# ------------------------------
# Actors
# ------------------------------
class Actor:
    def __init__(self, maze: Maze, cell: Tuple[int, int], color: Tuple[int, int, int], speed: float):
        self.maze = maze
        self.pos = list(grid_to_pixel(cell))  # [x, y] in pixels
        self.color = color
        self.dir = STOP
        self.speed = speed
        self.radius = TILE_SIZE * 0.35

    def current_cell(self) -> Tuple[int, int]:
        return pixel_to_grid(tuple(self.pos))

    def set_dir(self, new_dir: Tuple[int, int]):
        self.dir = new_dir

    def can_move_dir(self, dir_: Tuple[int, int]) -> bool:
        # Check next tile in direction from current pixel position.
        x, y = self.pos
        nx = x + dir_[0]
        ny = y + dir_[1]
        next_cell = pixel_to_grid((nx, ny))
        # Also check the cell ahead by a tile when aligned to center to prevent clipping
        ahead_cell = add_tuple(self.current_cell(), dir_)
        if is_centered(tuple(self.pos)) and self.maze.is_wall(ahead_cell):
            return False
        return not self.maze.is_wall(next_cell)

    def move(self):
        if self.dir == STOP:
            return
        # Move pixel-wise but constrain by walls
        for _ in range(int(self.speed)):
            if self.can_move_dir(self.dir):
                self.pos[0] += self.dir[0]
                self.pos[1] += self.dir[1]
            else:
                break
        # handle fractional speed
        frac = self.speed - int(self.speed)
        if frac > 0:
            if self.can_move_dir(self.dir):
                self.pos[0] += self.dir[0] * frac
                self.pos[1] += self.dir[1] * frac

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.radius))


class Pacman(Actor):
    def __init__(self, maze: Maze, cell: Tuple[int, int]):
        super().__init__(maze, cell, YELLOW, PACMAN_SPEED)
        self.pending_dir = STOP

    def update(self):
        # Attempt to turn when centered
        if self.pending_dir != STOP and is_centered(tuple(self.pos)):
            ahead_cell = add_tuple(self.current_cell(), self.pending_dir)
            if not self.maze.is_wall(ahead_cell):
                self.set_dir(self.pending_dir)
        self.move()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.pending_dir = LEFT
            elif event.key == pygame.K_RIGHT:
                self.pending_dir = RIGHT
            elif event.key == pygame.K_UP:
                self.pending_dir = UP
            elif event.key == pygame.K_DOWN:
                self.pending_dir = DOWN


class Ghost(Actor):
    def __init__(self, maze: Maze, cell: Tuple[int, int], color: Tuple[int, int, int]):
        super().__init__(maze, cell, color, GHOST_SPEED)
        self.set_dir(random.choice([UP, DOWN, LEFT, RIGHT]))
        self.frightened = False
        self.respawn_cell = cell
        self.alive = True

    def available_dirs(self) -> List[Tuple[int, int]]:
        # Consider 4 dirs but remove walls and prevent reversing unless needed
        dirs = [UP, DOWN, LEFT, RIGHT]
        valid = []
        for d in dirs:
            if self.maze.is_wall(add_tuple(self.current_cell(), d)):
                continue
            # Avoid reversing unless no choice
            if d == opposite(self.dir) and not is_centered(tuple(self.pos)):
                continue
            valid.append(d)
        if not valid:
            valid = [opposite(self.dir)]
        return valid

    def update(self):
        # Change direction when centered at intersections
        if is_centered(tuple(self.pos)):
            options = self.available_dirs()
            # Prefer not to reverse; if multiple options, pick random
            if len(options) > 1 and opposite(self.dir) in options:
                options.remove(opposite(self.dir))
            self.set_dir(random.choice(options))
        self.move()

    def reset_to_spawn(self):
        self.pos = list(grid_to_pixel(self.respawn_cell))
        self.set_dir(random.choice([UP, DOWN, LEFT, RIGHT]))
        self.alive = True
        self.frightened = False


# ------------------------------
# Game
# ------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pacman (Pygame)')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 28)
        self.big_font = pygame.font.Font(FONT_NAME, 40)

        self.maze = Maze(maze_layout)
        # Start positions in open spaces
        self.pacman = Pacman(self.maze, (3, 3))
        self.ghosts = [
            Ghost(self.maze, (3, 1), PINK),
            Ghost(self.maze, (3, 5), CYAN),
        ]

        self.score = 0
        self.lives = 3
        self.power_expires_at = 0  # ms timestamp
        self.running = True
        self.win = False
        self.game_over = False

    def set_power_mode(self):
        self.power_expires_at = pygame.time.get_ticks() + POWER_DURATION_MS
        for g in self.ghosts:
            if g.alive:
                g.frightened = True

    def update_power_mode(self):
        if self.power_expires_at and pygame.time.get_ticks() > self.power_expires_at:
            self.power_expires_at = 0
            for g in self.ghosts:
                g.frightened = False

    def eat_logic(self):
        cell = self.pacman.current_cell()
        gained = self.maze.eat_at(cell)
        if gained:
            self.score += gained
            if gained == POWER_PELLET_SCORE:
                self.set_power_mode()

    def collision_logic(self):
        for g in self.ghosts:
            if not g.alive:
                continue
            dist = math.hypot(self.pacman.pos[0] - g.pos[0], self.pacman.pos[1] - g.pos[1])
            if dist < TILE_SIZE * 0.6:
                if g.frightened:
                    # Eat ghost
                    g.alive = False
                    self.score += GHOST_EAT_SCORE
                    # Respawn ghost after delay
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1500, loops=1)
                    g.frightened = False
                else:
                    # Pacman loses a life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_round()
                    return

    def reset_round(self):
        # Reset positions without resetting score/pellets
        self.pacman = Pacman(self.maze, (3, 3))
        for g in self.ghosts:
            g.reset_to_spawn()
        self.power_expires_at = 0

    def check_win(self):
        if self.maze.remaining_dots() == 0:
            self.win = True
            self.game_over = True

    def draw_ui(self):
        # UI bar
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, UI_HEIGHT))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (16, 16))
        self.screen.blit(lives_text, (WIDTH - 16 - lives_text.get_width(), 16))

        if self.power_expires_at:
            remaining = max(0, (self.power_expires_at - pygame.time.get_ticks()) // 1000)
            ptext = self.font.render(f"Power: {remaining}s", True, ORANGE)
            self.screen.blit(ptext, (WIDTH // 2 - ptext.get_width() // 2, 16))

    def draw_end_screen(self):
        msg = "YOU WIN!" if self.win else "GAME OVER"
        color = GREEN if self.win else RED
        surf = self.big_font.render(msg, True, color)
        sub = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - 40))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if self.game_over and event.key == pygame.K_r:
                        # Reset game
                        self.__init__()
                elif event.type == pygame.USEREVENT + 1:
                    # Respawn ghosts that were eaten
                    for g in self.ghosts:
                        if not g.alive:
                            g.reset_to_spawn()

                # Pass controls to Pacman when game not over
                if not self.game_over:
                    self.pacman.handle_event(event)

            if not self.game_over:
                # Updates
                self.pacman.update()
                for g in self.ghosts:
                    g.update()
                self.update_power_mode()
                self.eat_logic()
                self.collision_logic()
                self.check_win()

            # Drawing
            self.maze.draw(self.screen)
            if not self.game_over:
                # Draw ghosts (blue when frightened, grey when dead)
                for g in self.ghosts:
                    if g.alive:
                        color = GREY if not g.frightened else BLUE
                        pygame.draw.circle(self.screen, color, (int(g.pos[0]), int(g.pos[1])), int(g.radius))
                    else:
                        # Draw small eyes marker at spawn
                        sx, sy = grid_to_pixel(g.respawn_cell)
                        pygame.draw.circle(self.screen, WHITE, (int(sx), int(sy)), int(TILE_SIZE * 0.15))
                # Draw Pacman on top
                self.pacman.draw(self.screen)
            else:
                # Dim playfield
                overlay = pygame.Surface((WIDTH, HEIGHT - UI_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, UI_HEIGHT))
                self.draw_end_screen()

            # UI last
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
