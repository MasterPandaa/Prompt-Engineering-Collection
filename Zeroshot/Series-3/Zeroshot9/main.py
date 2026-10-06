import sys
import math
import random
import pygame

# ----------------------------
# Config & Constants
# ----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 20
GRID_W = WIDTH // TILE  # 40
GRID_H = HEIGHT // TILE  # 30

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
YELLOW = (255, 210, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
FRIGHT_BLUE = (50, 100, 255)

# Game settings
PACMAN_SPEED = 3.0  # pixels per frame
GHOST_SPEED = 2.6
FRIGHT_SPEED = 2.0
EATEN_SPEED = 3.2
POWER_DURATION = 6.0  # seconds
LIVES_START = 3

# Maze tile values
WALL = 1
EMPTY = 0
DOT = 2
POWER = 3
GHOST_GATE = 4  # gate in front of ghost house (passable for Pacman, limited for ghosts)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)
DIRS = [UP, LEFT, DOWN, RIGHT]


# ----------------------------
# Maze definition (40 x 30)
# 1=Wall, 0=Path, 2=Dot, 3=Power, 4=Gate
# ----------------------------
# Layout derived roughly from classic style, simplified to fit 40x30 grid.
# Ensure outer walls are 1.
MAZE_LAYOUT = [
    # 40 columns per row
    "1111111111111111111111111111111111111111",
    "1000000000000000000000000000000000000001",
    "1011111111110111111111111011111111111101",
    "1020000000010200000000010200000000000301",
    "1010111111010111111101010111111111011101",
    "1010100001010100000101010100000010010101",
    "1010101111010101110101010111111011010101",
    "1010101000010101000101010100001010010101",
    "1010101011110101011101010111101011010101",
    "1020101010000101000101000100001010010301",
    "1110101010111110111101111101111011011101",
    "1000101000100000100010000010000010000001",
    "1011101111101111101110111101111101111101",
    "1010001000001000001000100001000001000101",
    "1010111011111011111010111110111110110101",
    "1010000010000010000010000010000010000101",
    "1011111010111110111110111110111110111101",
    "1020000010100000100000100000100000100301",
    "1011111010101111101111101111101110101101",
    "1010000010101000000000000000100010100001",
    "1010111110101011111111111110101110111101",
    "1010000000101010000000000010100000000101",
    "1011111111101010111111111010111111110101",
    "1000000000001010000022220010100000000001",
    "1111111111101010111114111010111111111101",
    "1000000000101000100000000010000000000001",
    "1011111110101110111111111110111111111101",
    "1020000000100000100000000010000000000301",
    "1000000000000000000000000000000000000001",
    "1111111111111111111111111111111111111111",
]
# Notes:
# - Row 24 has "...00222200..." to place a few extra dots in a hallway.
# - Row 25 contains ghost house with gate "4" in the center ("...11114111...")
# - Four power pellets placed on rows 4, 10, 18, 28 near corners as "3".

assert len(MAZE_LAYOUT) == GRID_H, "Maze rows must equal GRID_H"
for r in MAZE_LAYOUT:
    assert len(r) == GRID_W, "Maze cols must equal GRID_W"


# ----------------------------
# Utility functions
# ----------------------------

def add(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])


def tile_center(tx, ty):
    return (tx * TILE + TILE // 2, ty * TILE + TILE // 2)


def is_wall(tx, ty):
    if tx < 0 or ty < 0 or tx >= GRID_W or ty >= GRID_H:
        return True
    return int(MAZE_LAYOUT[ty][tx]) == WALL


def is_gate(tx, ty):
    if tx < 0 or ty < 0 or tx >= GRID_W or ty >= GRID_H:
        return False
    return int(MAZE_LAYOUT[ty][tx]) == GHOST_GATE


def can_pass(tx, ty):
    if tx < 0 or ty < 0 or tx >= GRID_W or ty >= GRID_H:
        return False
    v = int(MAZE_LAYOUT[ty][tx])
    return v in (EMPTY, DOT, POWER, GHOST_GATE)


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ----------------------------
# Entity Classes
# ----------------------------
class Pacman:
    def __init__(self, start_tile):
        self.spawn_tile = start_tile
        cx, cy = tile_center(*start_tile)
        self.x = float(cx)
        self.y = float(cy)
        self.dir = STOP
        self.next_dir = STOP
        self.speed = PACMAN_SPEED
        self.radius = TILE // 2 - 2
        self.alive = True

    def reset(self):
        cx, cy = tile_center(*self.spawn_tile)
        self.x, self.y = float(cx), float(cy)
        self.dir = STOP
        self.next_dir = STOP
        self.alive = True

    @property
    def tile(self):
        return int(self.x // TILE), int(self.y // TILE)

    def at_center_of_tile(self):
        tx, ty = self.tile
        cx, cy = tile_center(tx, ty)
        return abs(self.x - cx) <= 1.0 and abs(self.y - cy) <= 1.0

    def set_direction(self, d):
        self.next_dir = d

    def can_move_dir(self, d):
        tx, ty = self.tile
        ntx, nty = tx + d[0], ty + d[1]
        return can_pass(ntx, nty) and not is_wall(ntx, nty)

    def update(self, dt):
        # Direction change only at tile center
        if self.at_center_of_tile():
            if self.next_dir != self.dir and self.can_move_dir(self.next_dir):
                # snap to center before turning
                tx, ty = self.tile
                cx, cy = tile_center(tx, ty)
                self.x, self.y = float(cx), float(cy)
                self.dir = self.next_dir
            if self.dir == STOP and self.next_dir != STOP and self.can_move_dir(self.next_dir):
                self.dir = self.next_dir

        # Try forward movement; stop if wall ahead
        if self.dir != STOP:
            tx, ty = self.tile
            forward_tx, forward_ty = tx + self.dir[0], ty + self.dir[1]
            # Allow leaving the tile if not heading into a wall
            if not is_wall(forward_tx, forward_ty):
                self.x += self.dir[0] * self.speed
                self.y += self.dir[1] * self.speed
            else:
                # Snap to center if blocked
                cx, cy = tile_center(tx, ty)
                self.x, self.y = float(cx), float(cy)
                self.dir = STOP

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.radius)


class Ghost:
    NORMAL = 0
    FRIGHT = 1
    EATEN = 2

    def __init__(self, color, start_tile, home_tile):
        self.color = color
        self.spawn_tile = start_tile
        self.home_tile = home_tile  # center of ghost house to return when eaten
        cx, cy = tile_center(*start_tile)
        self.x = float(cx)
        self.y = float(cy)
        self.dir = random.choice(DIRS)
        self.state = Ghost.NORMAL
        self.speed = GHOST_SPEED
        self.radius = TILE // 2 - 3

    def reset(self):
        cx, cy = tile_center(*self.spawn_tile)
        self.x, self.y = float(cx), float(cy)
        self.dir = random.choice(DIRS)
        self.state = Ghost.NORMAL
        self.speed = GHOST_SPEED

    @property
    def tile(self):
        return int(self.x // TILE), int(self.y // TILE)

    def at_center_of_tile(self):
        tx, ty = self.tile
        cx, cy = tile_center(tx, ty)
        return abs(self.x - cx) <= 1.0 and abs(self.y - cy) <= 1.0

    def legal_dirs(self):
        tx, ty = self.tile
        dirs = []
        for d in DIRS:
            if (-d[0], -d[1]) == self.dir and self.dir != STOP:
                # avoid reversing unless no other option
                continue
            ntx, nty = tx + d[0], ty + d[1]
            if not is_wall(ntx, nty):
                # Simple rule: try to avoid leaving the house through outer walls; gate is allowed.
                dirs.append(d)
        if not dirs:
            # If blocked, allow reversing
            for d in DIRS:
                ntx, nty = tx + d[0], ty + d[1]
                if not is_wall(ntx, nty):
                    dirs.append(d)
        return dirs

    def choose_dir(self, pac_tile):
        choices = self.legal_dirs()
        if not choices:
            return STOP
        tx, ty = self.tile
        if self.state == Ghost.FRIGHT:
            # Run away: maximize distance
            best_d = None
            best_dist = -1
            for d in choices:
                p = (tx + d[0], ty + d[1])
                dist = (pac_tile[0] - p[0]) ** 2 + (pac_tile[1] - p[1]) ** 2
                if dist > best_dist:
                    best_dist = dist
                    best_d = d
            # With some randomness
            if random.random() < 0.3:
                best_d = random.choice(choices)
            return best_d
        elif self.state == Ghost.EATEN:
            # Head back to home tile (ghost house center)
            target = self.home_tile
        else:
            # Normal: chase Pacman with slight randomness
            if random.random() < 0.15:
                return random.choice(choices)
            target = pac_tile

        # Choose direction that minimizes distance to target
        best_d = None
        best = 1e9
        for d in choices:
            p = (tx + d[0], ty + d[1])
            dist = (target[0] - p[0]) ** 2 + (target[1] - p[1]) ** 2
            if dist < best:
                best = dist
                best_d = d
        return best_d

    def update(self, dt, pac_tile):
        # Adjust speed based on state
        self.speed = {
            Ghost.NORMAL: GHOST_SPEED,
            Ghost.FRIGHT: FRIGHT_SPEED,
            Ghost.EATEN: EATEN_SPEED,
        }[self.state]

        if self.at_center_of_tile():
            self.dir = self.choose_dir(pac_tile)

        if self.dir != STOP:
            tx, ty = self.tile
            ntx, nty = tx + self.dir[0], ty + self.dir[1]
            if not is_wall(ntx, nty):
                self.x += self.dir[0] * self.speed
                self.y += self.dir[1] * self.speed
            else:
                # pick a new dir if blocked unexpectedly
                self.dir = random.choice(DIRS)

    def draw(self, surf):
        col = FRIGHT_BLUE if self.state == Ghost.FRIGHT else self.color
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), self.radius)
        # Eyes for normal/eaten
        eye_col = WHITE if self.state != Ghost.FRIGHT else WHITE
        pygame.draw.circle(surf, eye_col, (int(self.x) - 4, int(self.y) - 2), 3)
        pygame.draw.circle(surf, eye_col, (int(self.x) + 4, int(self.y) - 2), 3)


# ----------------------------
# Game Class
# ----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)

        # Build pellet map and power pellets from layout
        self.dots = set()
        self.power = set()
        for y in range(GRID_H):
            for x in range(GRID_W):
                v = int(MAZE_LAYOUT[y][x])
                if v == DOT:
                    self.dots.add((x, y))
                elif v == POWER:
                    self.power.add((x, y))

        # Set starting positions
        self.pac_start = self.find_first_path()
        # Ghost house roughly row 25 (index 24/25), find center near gate
        self.ghost_home = self.find_gate_center(default=(20, 24))
        ghost_starts = [
            (self.ghost_home[0] - 2, self.ghost_home[1]),
            (self.ghost_home[0] + 2, self.ghost_home[1]),
            (self.ghost_home[0], self.ghost_home[1] - 2),
            (self.ghost_home[0], self.ghost_home[1] + 2),
        ]
        colors = [RED, PINK, CYAN, ORANGE]

        self.pacman = Pacman(self.pac_start)
        self.ghosts = [Ghost(colors[i], ghost_starts[i], self.ghost_home) for i in range(4)]

        self.score = 0
        self.lives = LIVES_START
        self.power_timer = 0.0
        self.game_over = False
        self.win = False

    def find_first_path(self):
        # Start Pacman near bottom left open area
        for y in range(GRID_H - 2, 1, -1):
            for x in range(1, GRID_W - 1):
                if int(MAZE_LAYOUT[y][x]) in (EMPTY, DOT, POWER):
                    return (x, y)
        return (1, 1)

    def find_gate_center(self, default=(GRID_W // 2, GRID_H // 2)):
        # Find a tile with gate and return center tile nearby inside house
        for y in range(GRID_H):
            for x in range(GRID_W):
                if int(MAZE_LAYOUT[y][x]) == GHOST_GATE:
                    # Home just behind the gate (upwards or downwards depending wall position)
                    # Try below gate first
                    if not is_wall(x, y + 1):
                        return (x, y + 1)
                    if not is_wall(x, y - 1):
                        return (x, y - 1)
                    return (x, y)
        return default

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman.set_direction(LEFT)
        elif keys[pygame.K_RIGHT]:
            self.pacman.set_direction(RIGHT)
        elif keys[pygame.K_UP]:
            self.pacman.set_direction(UP)
        elif keys[pygame.K_DOWN]:
            self.pacman.set_direction(DOWN)

    def update(self, dt):
        if self.game_over or self.win:
            return

        self.pacman.update(dt)
        for g in self.ghosts:
            g.update(dt, self.pacman.tile)

        self.eat_pellets()
        self.handle_collisions()

        # Update power timer
        if self.power_timer > 0:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.power_timer = 0
                for g in self.ghosts:
                    if g.state == Ghost.FRIGHT:
                        g.state = Ghost.NORMAL

        if not self.dots and not self.power:
            self.win = True

    def eat_pellets(self):
        tx, ty = self.pacman.tile
        if (tx, ty) in self.dots:
            self.dots.remove((tx, ty))
            self.score += 10
        if (tx, ty) in self.power:
            self.power.remove((tx, ty))
            self.score += 50
            self.power_timer = POWER_DURATION
            for g in self.ghosts:
                if g.state != Ghost.EATEN:
                    g.state = Ghost.FRIGHT

    def reset_positions(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()

    def handle_collisions(self):
        px, py = self.pacman.x, self.pacman.y
        for g in self.ghosts:
            if distance((px, py), (g.x, g.y)) < (self.pacman.radius + g.radius - 2):
                if g.state == Ghost.FRIGHT:
                    # Eat the ghost
                    g.state = Ghost.EATEN
                    self.score += 200
                    # send toward home immediately
                    g.dir = STOP
                elif g.state == Ghost.EATEN:
                    # If reached home tile center, revive
                    if g.at_center_of_tile() and g.tile == self.ghost_home:
                        g.state = Ghost.NORMAL
                else:
                    # Pacman loses a life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_positions()
                    return

        # Revive eaten ghosts when at home tile center
        for g in self.ghosts:
            if g.state == Ghost.EATEN and g.at_center_of_tile() and g.tile == self.ghost_home:
                g.state = Ghost.NORMAL

    def draw_maze(self, surf):
        # Fill background
        surf.fill(BLACK)
        # Draw maze walls and pellets
        for y in range(GRID_H):
            for x in range(GRID_W):
                v = int(MAZE_LAYOUT[y][x])
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if v == WALL:
                    pygame.draw.rect(surf, BLUE, rect)
                elif v == GHOST_GATE:
                    pygame.draw.rect(surf, GREY, rect)

        # Draw dots
        for (x, y) in self.dots:
            cx, cy = tile_center(x, y)
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)
        # Draw power pellets
        for (x, y) in self.power:
            cx, cy = tile_center(x, y)
            pygame.draw.circle(surf, WHITE, (cx, cy), 6, width=2)

    def draw_hud(self, surf):
        text = f"Score: {self.score}   Lives: {self.lives}"
        img = self.font.render(text, True, WHITE)
        surf.blit(img, (10, HEIGHT - 24))
        if self.power_timer > 0:
            ptext = f"POWER: {self.power_timer:0.1f}s"
            pimg = self.font.render(ptext, True, FRIGHT_BLUE)
            surf.blit(pimg, (WIDTH - 150, HEIGHT - 24))
        if self.win:
            wimg = self.font.render("YOU WIN! Press Esc to exit.", True, YELLOW)
            surf.blit(wimg, (WIDTH // 2 - wimg.get_width() // 2, 10))
        if self.game_over:
            gimg = self.font.render("GAME OVER! Press Esc to exit.", True, ORANGE)
            surf.blit(gimg, (WIDTH // 2 - gimg.get_width() // 2, 10))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw_maze(self.screen)
            self.pacman.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_hud(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
