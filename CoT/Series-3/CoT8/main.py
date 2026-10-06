import sys
import random
import math
import pygame
from enum import Enum, auto

# -----------------------------
# Config & Constants
# -----------------------------
TILE_SIZE = 24
FPS = 60
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
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
YELLOW = (255, 207, 0)
WHITE = (255, 255, 255)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREY = (120, 120, 120)

# Game parameters
POWER_DURATION = 6.0  # seconds
PACMAN_SPEED = 1.8    # tiles per second
GHOST_SPEED = 1.6     # tiles per second
FRIGHT_SPEED = 1.2    # tiles per second
LIVES = 3


# -----------------------------
# Helpers
# -----------------------------

def grid_to_pixel(col, row):
    return int(col * TILE_SIZE + TILE_SIZE / 2), int(row * TILE_SIZE + TILE_SIZE / 2)


def pixel_to_grid(x, y):
    return int(x // TILE_SIZE), int(y // TILE_SIZE)


def opposite(direction):
    return (-direction[0], -direction[1])


# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]


class GameMode(Enum):
    NORMAL = auto()
    POWER = auto()
    GAME_OVER = auto()
    WIN = auto()


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.pacman_starts = []
        self.ghost_starts = []
        self._parse_layout()

    def _parse_layout(self):
        for r, line in enumerate(self.layout):
            for c, ch in enumerate(line):
                if ch == '#':
                    self.walls.add((c, r))
                elif ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power_pellets.add((c, r))
                elif ch == 'P':
                    self.pacman_starts.append((c, r))
                elif ch == 'G':
                    self.ghost_starts.append((c, r))

    def is_wall(self, cell):
        c, r = cell
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return True
        return (c, r) in self.walls

    def draw(self, surface):
        # Fill background
        surface.fill(BLACK)
        # Draw walls
        for (c, r) in self.walls:
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            pygame.draw.rect(surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE), border_radius=4)
        # Draw pellets
        for (c, r) in self.pellets:
            x, y = grid_to_pixel(c, r)
            pygame.draw.circle(surface, WHITE, (x, y), 3)
        # Draw power pellets
        for (c, r) in self.power_pellets:
            x, y = grid_to_pixel(c, r)
            pygame.draw.circle(surface, WHITE, (x, y), 6)


class Entity:
    def __init__(self, maze: Maze, start_cell, color, speed_tiles_per_sec):
        self.maze = maze
        self.color = color
        self.start_cell = start_cell
        self.speed = speed_tiles_per_sec * TILE_SIZE  # pixels per second
        self.reset()

    def reset(self):
        cx, cy = grid_to_pixel(*self.start_cell)
        self.x = float(cx)
        self.y = float(cy)
        self.dir = STOP
        self.next_dir = STOP

    @property
    def pos(self):
        return self.x, self.y

    @property
    def cell(self):
        return pixel_to_grid(self.x, self.y)

    def can_move(self, direction):
        c, r = self.cell
        dc, dr = direction
        next_cell = (c + dc, r + dr)
        return not self.maze.is_wall(next_cell)

    def at_center_of_cell(self):
        cx, cy = grid_to_pixel(*self.cell)
        return abs(self.x - cx) < 2 and abs(self.y - cy) < 2

    def move(self, dt):
        # dt in seconds
        self.x += self.dir[0] * self.speed * dt
        self.y += self.dir[1] * self.speed * dt

    def draw(self, surface, radius=10):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class Pacman(Entity):
    def __init__(self, maze, start_cell):
        super().__init__(maze, start_cell, YELLOW, PACMAN_SPEED)
        self.mouth_angle = 0
        self.mouth_dir = 1

    def update(self, dt):
        # Handle turning at cell centers if possible
        if self.next_dir != self.dir and self.at_center_of_cell():
            if self.can_move(self.next_dir):
                self.dir = self.next_dir
        # Stop if hit a wall in current direction
        if not self.can_move(self.dir) and self.at_center_of_cell():
            self.dir = STOP
        self.move(dt)
        # Animate mouth
        self.mouth_angle += self.mouth_dir * 360 * dt
        if self.mouth_angle > 45:
            self.mouth_angle = 45
            self.mouth_dir = -1
        elif self.mouth_angle < 0:
            self.mouth_angle = 0
            self.mouth_dir = 1

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.next_dir = LEFT
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.next_dir = RIGHT
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.next_dir = UP
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.next_dir = DOWN

    def draw(self, surface, radius=10):
        # Draw Pacman with mouth animation
        center = (int(self.x), int(self.y))
        angle = self.mouth_angle
        # Convert to radians
        start_angle = math.radians(angle)
        end_angle = math.radians(360 - angle)
        pygame.draw.circle(surface, YELLOW, center, radius)
        # Draw mouth as a black polygon wedge
        dir_angle = 0
        if self.dir == RIGHT:
            dir_angle = 0
        elif self.dir == LEFT:
            dir_angle = math.pi
        elif self.dir == UP:
            dir_angle = -math.pi / 2
        elif self.dir == DOWN:
            dir_angle = math.pi / 2
        a1 = dir_angle - start_angle
        a2 = dir_angle + start_angle
        mouth_points = [
            center,
            (int(center[0] + radius * math.cos(a1)), int(center[1] + radius * math.sin(a1))),
            (int(center[0] + radius * math.cos(a2)), int(center[1] + radius * math.sin(a2))),
        ]
        pygame.draw.polygon(surface, BLACK, mouth_points)


class GhostState(Enum):
    NORMAL = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(Entity):
    def __init__(self, maze, start_cell, color, speed_tiles_per_sec):
        super().__init__(maze, start_cell, color, speed_tiles_per_sec)
        self.state = GhostState.NORMAL
        self.base_speed = self.speed
        self.target_cell = start_cell

    def update(self, dt, pacman_cell):
        # Adjust speed by state
        if self.state == GhostState.FRIGHTENED:
            self.speed = FRIGHT_SPEED * TILE_SIZE
        else:
            self.speed = self.base_speed

        # Choose new direction at intersections or when blocked
        if self.at_center_of_cell():
            options = []
            for d in DIRECTIONS:
                if d == opposite(self.dir):
                    continue  # avoid reversing unless necessary
                if self.can_move(d):
                    options.append(d)
            if not options:
                # dead end; allow reverse
                rev = opposite(self.dir)
                if self.can_move(rev):
                    self.dir = rev
            else:
                self.dir = self.choose_direction(options, pacman_cell)
        # Move
        self.move(dt)

    def choose_direction(self, options, pacman_cell):
        # Simple strategy
        if self.state == GhostState.FRIGHTENED:
            # Bias away from Pacman
            farthest = None
            max_dist = -1
            for d in options:
                nc = (self.cell[0] + d[0], self.cell[1] + d[1])
                dist = (nc[0] - pacman_cell[0]) ** 2 + (nc[1] - pacman_cell[1]) ** 2
                if dist > max_dist:
                    max_dist = dist
                    farthest = d
            return farthest
        elif self.state == GhostState.EATEN:
            # Go back to start
            best = None
            best_dist = 1e9
            for d in options:
                nc = (self.cell[0] + d[0], self.cell[1] + d[1])
                dist = (nc[0] - self.start_cell[0]) ** 2 + (nc[1] - self.start_cell[1]) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best = d
            return best
        else:
            # Normal: random at intersections, mild bias towards Pacman sometimes
            if random.random() < 0.6:
                # move toward Pacman
                best = None
                best_dist = 1e9
                for d in options:
                    nc = (self.cell[0] + d[0], self.cell[1] + d[1])
                    dist = (nc[0] - pacman_cell[0]) ** 2 + (nc[1] - pacman_cell[1]) ** 2
                    if dist < best_dist:
                        best_dist = dist
                        best = d
                return best
            else:
                return random.choice(options)

    def draw(self, surface, radius=10):
        color = self.color
        if self.state == GhostState.FRIGHTENED:
            color = BLUE
        elif self.state == GhostState.EATEN:
            color = GREY
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        # eyes
        eye_color = WHITE
        pygame.draw.circle(surface, eye_color, (int(self.x - 4), int(self.y - 2)), 3)
        pygame.draw.circle(surface, eye_color, (int(self.x + 4), int(self.y - 2)), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.maze = Maze(MAZE_LAYOUT)
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height + 40))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        self.reset()

    def reset(self):
        # Player start: use first P if present else center-ish
        start_p = self.maze.pacman_starts[0] if self.maze.pacman_starts else (14, 15)
        self.pacman = Pacman(self.maze, start_p)
        # Ghosts
        ghost_cells = self.maze.ghost_starts or [(13, 12), (14, 12), (15, 12), (16, 12)]
        colors = [RED, PINK, CYAN, ORANGE]
        self.ghosts = [Ghost(self.maze, cell, colors[i % len(colors)], GHOST_SPEED) for i, cell in enumerate(ghost_cells)]
        self.mode = GameMode.NORMAL
        self.score = 0
        self.lives = LIVES
        self.power_timer = 0.0
        # Rebuild pellets since we may have eaten some in previous game
        self.maze = Maze(MAZE_LAYOUT)
        # Re-assign maze to entities
        self.pacman.maze = self.maze
        for g in self.ghosts:
            g.maze = self.maze

    def set_power_mode(self):
        self.mode = GameMode.POWER
        self.power_timer = POWER_DURATION
        for g in self.ghosts:
            if g.state != GhostState.EATEN:
                g.state = GhostState.FRIGHTENED

    def update(self, dt):
        if self.mode in (GameMode.GAME_OVER, GameMode.WIN):
            return

        self.pacman.update(dt)
        # Pellet eating
        c = self.pacman.cell
        if c in self.maze.pellets:
            self.maze.pellets.remove(c)
            self.score += 10
        if c in self.maze.power_pellets:
            self.maze.power_pellets.remove(c)
            self.score += 50
            self.set_power_mode()

        # Update ghosts and handle collisions
        for g in self.ghosts:
            g.update(dt, self.pacman.cell)
            if g.state == GhostState.EATEN and g.at_center_of_cell() and g.cell == g.start_cell:
                g.state = GhostState.NORMAL
            # Collision check
            if self.collide_entities(self.pacman, g):
                if g.state == GhostState.FRIGHTENED:
                    g.state = GhostState.EATEN
                    self.score += 200
                elif g.state == GhostState.NORMAL:
                    self.lose_life()
                    break

        # Power timer
        if self.mode == GameMode.POWER:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.mode = GameMode.NORMAL
                for g in self.ghosts:
                    if g.state == GhostState.FRIGHTENED:
                        g.state = GhostState.NORMAL

        # Win condition
        if not self.maze.pellets and not self.maze.power_pellets:
            self.mode = GameMode.WIN

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.mode = GameMode.GAME_OVER
        # Reset positions
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()
            g.state = GhostState.NORMAL

    @staticmethod
    def collide_entities(a: Entity, b: Entity, radius=10):
        dx = a.x - b.x
        dy = a.y - b.y
        return dx * dx + dy * dy < (radius * 2) ** 2 * 0.6  # slightly lenient

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.mode in (GameMode.GAME_OVER, GameMode.WIN):
                    self.reset()
            self.pacman.handle_input(event)

    def draw_hud(self, surface):
        # Score and lives
        hud_y = self.maze.height
        pygame.draw.rect(surface, BLACK, (0, hud_y, self.maze.width, 40))
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(text, (10, hud_y + 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        surface.blit(lives_text, (self.maze.width - 120, hud_y + 10))
        if self.mode == GameMode.POWER:
            p_text = self.font.render(f"Power: {self.power_timer:0.1f}s", True, WHITE)
            surface.blit(p_text, (self.maze.width // 2 - 60, hud_y + 10))

    def draw_overlay(self, surface):
        if self.mode == GameMode.GAME_OVER:
            msg = self.big_font.render("GAME OVER - Press R to Restart", True, WHITE)
            surface.blit(msg, (self.maze.width // 2 - msg.get_width() // 2, self.maze.height // 2 - 20))
        elif self.mode == GameMode.WIN:
            msg = self.big_font.render("YOU WIN! - Press R to Restart", True, WHITE)
            surface.blit(msg, (self.maze.width // 2 - msg.get_width() // 2, self.maze.height // 2 - 20))

    def render(self):
        self.maze.draw(self.screen)
        # Draw entities
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_hud(self.screen)
        self.draw_overlay(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()


if __name__ == "__main__":
    Game().run()
