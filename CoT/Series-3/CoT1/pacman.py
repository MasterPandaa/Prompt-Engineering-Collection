import sys
import math
import random
import pygame
from pygame import Rect

# -----------------------------
# Config & Constants
# -----------------------------
TILE_SIZE = 24
MAZE_ROWS = 23
MAZE_COLS = 28
WIDTH = MAZE_COLS * TILE_SIZE
HEIGHT = (MAZE_ROWS + 2) * TILE_SIZE  # extra space for HUD
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (10, 10, 40)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
RED = (255, 50, 50)
GREY = (180, 180, 180)

# Gameplay
PACMAN_SPEED = 2.0  # pixels per frame
GHOST_SPEED = 1.8
FRIGHTENED_SPEED = 1.2
POWER_DURATION = 6.0  # seconds
LIVES_START = 3
PELLET_SCORE = 10
POWER_SCORE = 50
GHOST_EAT_SCORE = 200

# -----------------------------
# Maze Layout (28 x 23)
# Legend: '#': wall, '.': pellet, 'o': power pellet, ' ': empty, 'P': pacman, 'G': ghost
# -----------------------------
MAZE_MAP = [
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
    "######.##          ##.######",
    "######.## ###GG### ##.######",
    "######.## #      # ##.######",
    "      .   # PPPP #   .      ",
    "######.## #      # ##.######",
    "######.## ######## ##.######",
    "######.##          ##.######",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "############################",
]

# Normalize rows: replace spaces outside bounds with walls for collision but allow tunnel spaces
assert len(MAZE_MAP) == MAZE_ROWS + 1  # We actually have 24 rows; adjust rows
# Fix: Use actual length dynamically
MAZE_ROWS = len(MAZE_MAP)
MAZE_COLS = len(MAZE_MAP[0])
WIDTH = MAZE_COLS * TILE_SIZE
HEIGHT = (MAZE_ROWS + 2) * TILE_SIZE


def grid_to_pixel(col, row):
    return int(col * TILE_SIZE + TILE_SIZE / 2), int((row + 2) * TILE_SIZE + TILE_SIZE / 2)


def pixel_to_grid(x, y):
    row = int((y - 2 * TILE_SIZE) // TILE_SIZE)
    col = int(x // TILE_SIZE)
    return col, row


def opposite(dir_vec):
    return (-dir_vec[0], -dir_vec[1])


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.walls = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.pellets = set()
        self.power_pellets = set()
        self.pacman_start = (1, 1)
        self.ghost_starts = []
        # Parse layout
        for r, line in enumerate(layout):
            for c, ch in enumerate(line):
                if ch == '#':
                    self.walls[r][c] = True
                elif ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power_pellets.add((c, r))
                elif ch == 'P':
                    self.pacman_start = (c, r)
                elif ch == 'G':
                    self.ghost_starts.append((c, r))
        # Precompute wall rects for drawing
        self.wall_rects = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.walls[r][c]:
                    x = c * TILE_SIZE
                    y = (r + 2) * TILE_SIZE
                    self.wall_rects.append(Rect(x, y, TILE_SIZE, TILE_SIZE))

    def is_wall(self, c, r):
        if r < 0 or r >= self.rows:
            return True
        # Tunnels: allow horizontal wrap if not a wall in wrapped cell
        c_wrapped = c % self.cols
        return self.walls[r][c_wrapped]

    def draw(self, surface):
        # Fill background
        surface.fill(NAVY)
        # Draw walls as rounded rectangles
        for rect in self.wall_rects:
            pygame.draw.rect(surface, BLUE, rect, border_radius=6)
        # Draw pellets
        for (c, r) in self.pellets:
            x, y = grid_to_pixel(c, r)
            pygame.draw.circle(surface, WHITE, (x, y), 3)
        for (c, r) in self.power_pellets:
            x, y = grid_to_pixel(c, r)
            pygame.draw.circle(surface, WHITE, (x, y), 6, width=2)


class Pacman:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.grid_c, self.grid_r = maze.pacman_start
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.speed = PACMAN_SPEED
        self.radius = TILE_SIZE // 2 - 2
        self.mouth_angle = 0
        self.mouth_opening = True
        self.power_timer = 0.0

    def reset_position(self):
        self.grid_c, self.grid_r = self.maze.pacman_start
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.dir = (0, 0)
        self.next_dir = (0, 0)

    def set_next_dir(self, dir_vec):
        self.next_dir = dir_vec

    def can_move(self, dir_vec):
        # Check collision a bit ahead
        new_x = self.x + dir_vec[0]
        new_y = self.y + dir_vec[1]
        c, r = pixel_to_grid(new_x, new_y)
        return not self.maze.is_wall(c, r)

    def update(self, dt):
        # Try to turn if possible
        if self.next_dir != self.dir and self.can_move((self.next_dir[0] * self.speed, self.next_dir[1] * self.speed)):
            self.dir = self.next_dir
        # Move if possible
        move_vec = (self.dir[0] * self.speed, self.dir[1] * self.speed)
        if self.can_move(move_vec):
            self.x += move_vec[0]
            self.y += move_vec[1]
            # Wrap horizontally
            if self.x < -TILE_SIZE / 2:
                self.x = WIDTH + TILE_SIZE / 2
            elif self.x > WIDTH + TILE_SIZE / 2:
                self.x = -TILE_SIZE / 2
        else:
            # Snap to center of current cell to improve turning
            c, r = pixel_to_grid(self.x, self.y)
            cx, cy = grid_to_pixel(c, r)
            self.x = cx
            self.y = cy
        # Eat pellets
        c, r = pixel_to_grid(self.x, self.y)
        ate = None
        if (c, r) in self.maze.pellets:
            self.maze.pellets.remove((c, r))
            ate = 'pellet'
        elif (c, r) in self.maze.power_pellets:
            self.maze.power_pellets.remove((c, r))
            ate = 'power'
            self.power_timer = POWER_DURATION
        # Power timer
        if self.power_timer > 0:
            self.power_timer = max(0.0, self.power_timer - dt)
        # Animate mouth
        self._animate_mouth()
        return ate

    def _animate_mouth(self):
        # Simple open/close cycle
        if self.mouth_opening:
            self.mouth_angle += 5
            if self.mouth_angle >= 45:
                self.mouth_angle = 45
                self.mouth_opening = False
        else:
            self.mouth_angle -= 5
            if self.mouth_angle <= 5:
                self.mouth_angle = 5
                self.mouth_opening = True

    def draw(self, surface):
        # Draw Pacman as a pie (arc mouth)
        center = (int(self.x), int(self.y))
        pygame.draw.circle(surface, YELLOW, center, self.radius)
        # Mouth direction based on movement
        angle_map = {
            (1, 0): 0,
            (-1, 0): 180,
            (0, -1): 90,
            (0, 1): 270,
            (0, 0): 0,
        }
        base_angle = angle_map.get(self.dir, 0)
        start_angle = math.radians(base_angle - self.mouth_angle)
        end_angle = math.radians(base_angle + self.mouth_angle)
        # Draw mouth by overlaying background triangle
        mouth_radius = self.radius
        p1 = center
        p2 = (int(self.x + mouth_radius * math.cos(start_angle)), int(self.y - mouth_radius * math.sin(start_angle)))
        p3 = (int(self.x + mouth_radius * math.cos(end_angle)), int(self.y - mouth_radius * math.sin(end_angle)))
        pygame.draw.polygon(surface, NAVY, [p1, p2, p3])


class Ghost:
    COLORS = [RED, PINK, CYAN, ORANGE]

    def __init__(self, maze: Maze, idx: int, start):
        self.maze = maze
        self.color = Ghost.COLORS[idx % len(Ghost.COLORS)]
        self.home_c, self.home_r = start
        self.reset()

    def reset(self):
        self.grid_c, self.grid_r = self.home_c, self.home_r
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.frightened = False
        self.dead = False

    def set_frightened(self, active: bool):
        if active and not self.dead:
            self.frightened = True
        elif not active:
            self.frightened = False

    def update(self, dt):
        speed = FRIGHTENED_SPEED if self.frightened and not self.dead else GHOST_SPEED
        # Decide direction at intersections
        if self._at_cell_center():
            self._choose_direction()
        # Move
        self.x += self.dir[0] * speed
        self.y += self.dir[1] * speed
        # Wrap horizontally
        if self.x < -TILE_SIZE / 2:
            self.x = WIDTH + TILE_SIZE / 2
        elif self.x > WIDTH + TILE_SIZE / 2:
            self.x = -TILE_SIZE / 2

    def _at_cell_center(self):
        c, r = pixel_to_grid(self.x, self.y)
        cx, cy = grid_to_pixel(c, r)
        return abs(self.x - cx) < 1.0 and abs(self.y - cy) < 1.0

    def _valid_dirs(self):
        candidates = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if d == opposite(self.dir):
                continue  # avoid immediate reversal
            c, r = pixel_to_grid(self.x + d[0] * TILE_SIZE * 0.6, self.y + d[1] * TILE_SIZE * 0.6)
            if not self.maze.is_wall(c, r):
                candidates.append(d)
        if not candidates:
            # If stuck, allow reversal
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                c, r = pixel_to_grid(self.x + d[0] * TILE_SIZE * 0.6, self.y + d[1] * TILE_SIZE * 0.6)
                if not self.maze.is_wall(c, r):
                    candidates.append(d)
        return candidates

    def _choose_direction(self):
        options = self._valid_dirs()
        if not options:
            return
        # Simple AI: random at intersections; when frightened, bias away from Pacman if visible
        choice = random.choice(options)
        self.dir = choice

    def draw(self, surface):
        center = (int(self.x), int(self.y))
        color = GREY if self.dead else (WHITE if self.frightened else self.color)
        body_radius = TILE_SIZE // 2 - 2
        pygame.draw.circle(surface, color, (center[0], center[1] - body_radius // 2), body_radius)
        rect = Rect(center[0] - body_radius, center[1] - body_radius // 2, body_radius * 2, body_radius)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        # eyes
        eye_color = NAVY if self.frightened else WHITE
        pygame.draw.circle(surface, eye_color, (center[0] - 6, center[1] - 4), 3)
        pygame.draw.circle(surface, eye_color, (center[0] + 6, center[1] - 4), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 32, bold=True)

        self.maze = Maze(MAZE_MAP)
        self.pacman = Pacman(self.maze)
        if self.maze.ghost_starts:
            self.ghosts = [Ghost(self.maze, i, start) for i, start in enumerate(self.maze.ghost_starts)]
        else:
            # Fallback: spawn 4 ghosts near center
            self.ghosts = [Ghost(self.maze, i, (self.maze.cols // 2 + i - 2, self.maze.rows // 2)) for i in range(4)]

        self.score = 0
        self.lives = LIVES_START
        self.state = 'playing'  # 'playing', 'gameover'
        self._reset_round()

    def _reset_round(self):
        self.pacman.reset_position()
        for g in self.ghosts:
            g.reset()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.state == 'gameover' and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # restart
                    self.__init__()
                # Control Pacman
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.pacman.set_next_dir((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.pacman.set_next_dir((1, 0))
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pacman.set_next_dir((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pacman.set_next_dir((0, 1))

    def update(self, dt):
        if self.state != 'playing':
            return
        ate = self.pacman.update(dt)
        if ate == 'pellet':
            self.score += PELLET_SCORE
        elif ate == 'power':
            self.score += POWER_SCORE
            for g in self.ghosts:
                g.set_frightened(True)
        # Update ghosts and collisions
        frightened_active = self.pacman.power_timer > 0
        if not frightened_active:
            for g in self.ghosts:
                g.set_frightened(False)
        for g in self.ghosts:
            g.update(dt)
        # Check collisions Pacman-Ghost
        p_rect = Rect(int(self.pacman.x - 10), int(self.pacman.y - 10), 20, 20)
        for g in self.ghosts:
            g_rect = Rect(int(g.x - 10), int(g.y - 10), 20, 20)
            if p_rect.colliderect(g_rect):
                if g.frightened and not g.dead:
                    g.dead = True
                    self.score += GHOST_EAT_SCORE
                    # send ghost back home
                    g.grid_c, g.grid_r = g.home_c, g.home_r
                    g.x, g.y = grid_to_pixel(g.grid_c, g.grid_r)
                    g.frightened = False
                    g.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                elif not g.dead and self.pacman.power_timer <= 0:
                    # Pacman dies
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = 'gameover'
                    self._reset_round()
                    break
        # Win condition: all pellets eaten
        if not self.maze.pellets and not self.maze.power_pellets:
            # New level: reset pellets and increase speed slightly
            self._next_level()

    def _next_level(self):
        # Rebuild maze pellets from layout
        self.maze = Maze(MAZE_MAP)
        self.pacman.maze = self.maze
        self.pacman.reset_position()
        for g in self.ghosts:
            g.maze = self.maze
            g.reset()
        # Slight speed up
        self.pacman.speed = min(self.pacman.speed + 0.1, 3.2)
        for g in self.ghosts:
            pass

    def draw_hud(self):
        # HUD area is the top two tile rows
        pygame.draw.rect(self.screen, BLACK, Rect(0, 0, WIDTH, 2 * TILE_SIZE))
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (10, 8))
        self.screen.blit(lives_surf, (WIDTH - 120, 8))
        if self.state == 'gameover':
            msg = self.big_font.render("GAME OVER - Press Enter", True, YELLOW)
            rect = msg.get_rect(center=(WIDTH // 2, TILE_SIZE))
            self.screen.blit(msg, rect)

    def draw(self):
        self.maze.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
