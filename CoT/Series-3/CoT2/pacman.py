import sys
import math
import random
import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_a, K_d, K_w, K_s, K_ESCAPE, QUIT, KEYDOWN

# =============================
# Config & Constants
# =============================
TILE_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (70, 70, 70)
YELLOW = (255, 205, 0)
BLUE = (50, 50, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 200, 0)
NAVY = (0, 0, 100)

# Game States
STATE_PLAYING = "playing"
STATE_POWER = "power"
STATE_GAMEOVER = "gameover"

POWER_DURATION = 8.0  # seconds

# =============================
# Static Maze Definition
# Legend:
#   # = wall
#   . = pellet
#   o = power pellet
#     = empty path
#   P = player start
#   G = ghost start
# =============================
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

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 60  # space for HUD

# Utility

def grid_to_px(col, row):
    return col * TILE_SIZE, row * TILE_SIZE


def px_center_of_cell(col, row):
    x, y = grid_to_px(col, row)
    return x + TILE_SIZE // 2, y + TILE_SIZE // 2


def is_wall(col, row):
    if 0 <= row < ROWS and 0 <= col < COLS:
        return MAZE_LAYOUT[row][col] == '#'
    return True


def valid_cell(col, row):
    return 0 <= row < ROWS and 0 <= col < COLS and not is_wall(col, row)


class Maze:
    def __init__(self):
        self.pellets = set()
        self.power_pellets = set()
        self.player_start = None
        self.ghost_starts = []
        for r, line in enumerate(MAZE_LAYOUT):
            for c, ch in enumerate(line):
                if ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power_pellets.add((c, r))
                elif ch == 'P' and self.player_start is None:
                    self.player_start = (c, r)
                elif ch == 'G':
                    self.ghost_starts.append((c, r))
        # Fallbacks
        if self.player_start is None:
            # center
            self.player_start = (COLS // 2, ROWS // 2)
        if not self.ghost_starts:
            self.ghost_starts = [(COLS // 2 - 1, ROWS // 2), (COLS // 2 + 1, ROWS // 2)]

    def draw(self, surf):
        # Draw walls
        for r, line in enumerate(MAZE_LAYOUT):
            for c, ch in enumerate(line):
                if ch == '#':
                    x, y = grid_to_px(c, r)
                    pygame.draw.rect(surf, NAVY, (x, y, TILE_SIZE, TILE_SIZE))
                    # inner outline for classic look
                    pygame.draw.rect(surf, BLUE, (x+4, y+4, TILE_SIZE-8, TILE_SIZE-8), 2)
        # Draw pellets
        for (c, r) in self.pellets:
            x, y = px_center_of_cell(c, r)
            pygame.draw.circle(surf, WHITE, (x, y), 3)
        # Draw power pellets
        for (c, r) in self.power_pellets:
            x, y = px_center_of_cell(c, r)
            pygame.draw.circle(surf, WHITE, (x, y), 6)


class Entity:
    def __init__(self, col, row, speed):
        self.col = float(col)
        self.row = float(row)
        self.dir = (0, 0)  # dx, dy in grid steps
        self.speed = speed  # cells per second

    @property
    def pos(self):
        return (self.col, self.row)

    def cell_centered(self):
        # Check if near the center of a cell to allow turning
        cx = round(self.col)
        cy = round(self.row)
        return abs(self.col - cx) < 0.1 and abs(self.row - cy) < 0.1

    def set_dir_if_valid(self, d):
        dx, dy = d
        ncol = int(round(self.col + dx))
        nrow = int(round(self.row + dy))
        if valid_cell(ncol, nrow):
            self.dir = d
            # snap to center to avoid drift
            self.col = round(self.col)
            self.row = round(self.row)

    def update_move(self, dt):
        # Wrap tunnels horizontally
        next_col = self.col + self.dir[0] * self.speed * dt
        next_row = self.row + self.dir[1] * self.speed * dt
        # Check collision against walls with small steps for robustness
        steps = max(1, int(max(abs(next_col - self.col), abs(next_row - self.row)) * 4))
        for i in range(steps):
            t = (i + 1) / steps
            pcol = self.col + (next_col - self.col) * t
            prow = self.row + (next_row - self.row) * t
            # tunnel wrap
            if pcol < 0:
                pcol = COLS - 1
            elif pcol >= COLS:
                pcol = 0
            ic = int(round(pcol))
            ir = int(round(prow))
            if is_wall(ic, ir):
                # stop before wall
                return
        self.col = next_col
        self.row = next_row
        if self.col < 0:
            self.col = COLS - 1
        elif self.col >= COLS:
            self.col = 0


class Player(Entity):
    def __init__(self, col, row):
        super().__init__(col, row, speed=8.0)  # cells per second
        self.next_dir = (0, 0)
        self.lives = 3
        self.score = 0

    def handle_input(self, pressed):
        nd = self.next_dir
        if pressed[K_LEFT] or pressed[K_a]:
            nd = (-1, 0)
        elif pressed[K_RIGHT] or pressed[K_d]:
            nd = (1, 0)
        elif pressed[K_UP] or pressed[K_w]:
            nd = (0, -1)
        elif pressed[K_DOWN] or pressed[K_s]:
            nd = (0, 1)
        self.next_dir = nd

    def update(self, maze: Maze, dt):
        # Try to apply next_dir when centered
        if self.cell_centered() and self.next_dir != self.dir:
            self.set_dir_if_valid(self.next_dir)
        # Move
        prev_col, prev_row = int(round(self.col)), int(round(self.row))
        super().update_move(dt)
        c, r = int(round(self.col)), int(round(self.row))
        # Eat pellets
        if (c, r) in maze.pellets:
            maze.pellets.remove((c, r))
            self.score += 10
        if (c, r) in maze.power_pellets:
            maze.power_pellets.remove((c, r))
            self.score += 50
            return 'power'
        return None

    def draw(self, surf):
        x, y = px_center_of_cell(int(self.col), int(self.row))
        pygame.draw.circle(surf, YELLOW, (x, y), TILE_SIZE // 2 - 2)


class Ghost(Entity):
    def __init__(self, col, row, color):
        super().__init__(col, row, speed=6.0)
        self.color = color
        self.base_speed = 6.0
        self.frightened = False
        self.eaten = False
        self.home = (col, row)

    def available_dirs(self):
        options = []
        for d in [(-1,0),(1,0),(0,-1),(0,1)]:
            ncol = int(round(self.col + d[0]))
            nrow = int(round(self.row + d[1]))
            if valid_cell(ncol, nrow):
                options.append(d)
        return options

    def choose_dir(self):
        options = self.available_dirs()
        # Avoid 180 turn if possible
        opposite = (-self.dir[0], -self.dir[1])
        if len(options) > 1 and opposite in options:
            options.remove(opposite)
        if not options:
            return opposite
        return random.choice(options)

    def update(self, dt, player_pos):
        # Adjust speed based on frightened/eaten
        if self.eaten:
            self.speed = self.base_speed * 1.2
        elif self.frightened:
            self.speed = self.base_speed * 0.6
        else:
            self.speed = self.base_speed

        # Decide new dir at intersections (near center)
        if self.cell_centered():
            # Simple AI: if frightened, move away from player; if normal, random with bias towards player
            options = self.available_dirs()
            opposite = (-self.dir[0], -self.dir[1])
            if len(options) > 1 and opposite in options:
                options.remove(opposite)

            def dist_sq_after_dir(d):
                nx = round(self.col) + d[0]
                ny = round(self.row) + d[1]
                px, py = player_pos
                return (nx - px) ** 2 + (ny - py) ** 2

            if options:
                if self.eaten:
                    # Head home: choose direction minimizing distance to home
                    hx, hy = self.home
                    options.sort(key=lambda d: (round(self.col)+d[0]-hx)**2 + (round(self.row)+d[1]-hy)**2)
                    self.dir = options[0]
                elif self.frightened:
                    # Maximize distance from player
                    options.sort(key=lambda d: -dist_sq_after_dir(d))
                    self.dir = options[0]
                else:
                    # Minimize distance to player, with some randomness
                    random.shuffle(options)
                    options.sort(key=lambda d: dist_sq_after_dir(d))
                    self.dir = options[0]
        # Move
        super().update_move(dt)

    def draw(self, surf):
        x, y = px_center_of_cell(int(self.col), int(self.row))
        color = BLUE if self.frightened and not self.eaten else self.color
        body_rect = pygame.Rect(0, 0, TILE_SIZE - 4, TILE_SIZE - 4)
        body_rect.center = (x, y)
        pygame.draw.rect(surf, color, body_rect, border_radius=8)
        # eyes
        eye_color = WHITE if not self.frightened or self.eaten else WHITE
        pygame.draw.circle(surf, eye_color, (x - 4, y - 2), 3)
        pygame.draw.circle(surf, eye_color, (x + 4, y - 2), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.reset_level(full_reset=True)

    def reset_level(self, full_reset=False):
        self.maze = Maze()
        ps = self.maze.player_start
        self.player = Player(ps[0], ps[1])
        self.ghosts = []
        colors = [RED, PINK, CYAN, ORANGE]
        starts = self.maze.ghost_starts
        for i in range(min(4, len(starts))):
            c = starts[i]
            self.ghosts.append(Ghost(c[0], c[1], colors[i % len(colors)]))
        if not full_reset:
            # keep score and lives
            pass
        self.state = STATE_PLAYING
        self.power_timer = 0.0

    def set_power_mode(self):
        self.state = STATE_POWER
        self.power_timer = POWER_DURATION
        for g in self.ghosts:
            if not g.eaten:
                g.frightened = True

    def update_power_timer(self, dt):
        if self.state == STATE_POWER:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.state = STATE_PLAYING
                for g in self.ghosts:
                    g.frightened = False
                    g.eaten = False if g.eaten else g.eaten

    def lose_life_and_reset_positions(self):
        self.player.lives -= 1
        ps = self.maze.player_start
        self.player.col, self.player.row = float(ps[0]), float(ps[1])
        self.player.dir = (0, 0)
        for i, g in enumerate(self.ghosts):
            gs = self.maze.ghost_starts[i % len(self.maze.ghost_starts)]
            g.col, g.row = float(gs[0]), float(gs[1])
            g.dir = (0, 0)
            g.frightened = False
            g.eaten = False
        self.state = STATE_PLAYING
        self.power_timer = 0.0

    def handle_collisions(self):
        pc, pr = int(round(self.player.col)), int(round(self.player.row))
        for g in self.ghosts:
            gc, gr = int(round(g.col)), int(round(g.row))
            if pc == gc and pr == gr:
                if g.frightened and not g.eaten:
                    # eat ghost
                    self.player.score += 200
                    g.eaten = True
                    g.frightened = False
                elif not g.eaten:
                    # player hit
                    self.lose_life_and_reset_positions()
                    break
        # If eaten ghosts reach home, revive
        for g in self.ghosts:
            if g.eaten and int(round(g.col)) == g.home[0] and int(round(g.row)) == g.home[1]:
                g.eaten = False
                g.frightened = False

    def update(self, dt):
        pressed = pygame.key.get_pressed()
        self.player.handle_input(pressed)
        power_trigger = self.player.update(self.maze, dt)
        if power_trigger == 'power':
            self.set_power_mode()
        # Update ghosts
        ppos = (int(round(self.player.col)), int(round(self.player.row)))
        for g in self.ghosts:
            g.update(dt, ppos)
        # Collisions
        self.handle_collisions()
        # Check win/level clear
        if not self.maze.pellets and not self.maze.power_pellets:
            # Simple: reset level, keep score/lives
            old_score = self.player.score
            old_lives = self.player.lives
            self.reset_level(full_reset=False)
            self.player.score = old_score
            self.player.lives = old_lives
        # Check game over
        if self.player.lives <= 0:
            self.state = STATE_GAMEOVER
        # Update power timer
        self.update_power_timer(dt)

    def draw_hud(self, surf):
        hud_rect = pygame.Rect(0, ROWS * TILE_SIZE, WIDTH, 60)
        pygame.draw.rect(surf, BLACK, hud_rect)
        pygame.draw.line(surf, GRAY, (0, ROWS * TILE_SIZE), (WIDTH, ROWS * TILE_SIZE), 2)
        score_s = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_s = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        state_s = self.font.render(f"Mode: {self.state}", True, WHITE)
        surf.blit(score_s, (10, ROWS * TILE_SIZE + 10))
        surf.blit(lives_s, (170, ROWS * TILE_SIZE + 10))
        surf.blit(state_s, (310, ROWS * TILE_SIZE + 10))
        if self.state == STATE_POWER:
            tleft = max(0, self.power_timer)
            timer_s = self.font.render(f"Power: {tleft:0.1f}s", True, WHITE)
            surf.blit(timer_s, (480, ROWS * TILE_SIZE + 10))
        if self.state == STATE_GAMEOVER:
            over = self.big_font.render("GAME OVER - Press R to Restart", True, WHITE)
            rect = over.get_rect(center=(WIDTH//2, ROWS * TILE_SIZE + 35))
            surf.blit(over, rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud(self.screen)
        pygame.display.flip()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                if self.state == STATE_GAMEOVER and event.unicode.lower() == 'r':
                    # restart
                    old_score = 0
                    self.reset_level(full_reset=True)
        return True

    def run(self):
        while True:
            if not self.process_events():
                break
            dt = self.clock.tick(FPS) / 1000.0
            if self.state != STATE_GAMEOVER:
                self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
