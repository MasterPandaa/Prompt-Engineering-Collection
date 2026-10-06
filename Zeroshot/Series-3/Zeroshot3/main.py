import sys
import math
import random
import pygame
from pygame import Rect

# ----------------------------
# Config & Constants
# ----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (12, 12, 64)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (150, 150, 150)

# Maze legend:
# 1 = wall, 0 = path (no dot), 2 = dot, 3 = power pellet
# This layout is compact and symmetrical. You can tweak it freely.
MAZE_LAYOUT = [
    # 28 columns x 21 rows
    "1111111111111111111111111111",
    "1222222221111111222222222221",
    "1211111121111111211111112121",
    "1311111122222222211111112121",
    "1211111111111111111111112121",
    "1222222212222221222222222221",
    "1111111211111111211111111121",
    "1000011212222221212000011121",
    "1111011211110111211111011121",
    "1222011222000002212220012221",
    "1111011111111111111111011121",
    "1000012222222222222222011121",
    "1111111211111111211111111121",
    "1222221212000001212222222221",
    "1211111211111111211111111121",
    "1211111222222222211111111121",
    "1211111111111111111111111121",
    "1222222222222222222222222221",
    "1211111111111111111111111121",
    "1222222222222222222222222221",
    "1111111111111111111111111111",
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])

# Tile size and margins to center the maze
TILE_SIZE = min(WIDTH // COLS, HEIGHT // ROWS)
MAZE_W = TILE_SIZE * COLS
MAZE_H = TILE_SIZE * ROWS
OFFSET_X = (WIDTH - MAZE_W) // 2
OFFSET_Y = (HEIGHT - MAZE_H) // 2

# Gameplay constants
PACMAN_SPEED = 2.0
GHOST_SPEED = 1.8
FRIGHTENED_SPEED = 1.2
POWER_DURATION = 8.0  # seconds
DOT_SCORE = 10
POWER_DOT_SCORE = 50
GHOST_EAT_SCORE = 200
START_LIVES = 3

# Ghost states
GHOST_NORMAL = 0
GHOST_FRIGHTENED = 1
GHOST_EATEN = 2  # returning to base

# Utility functions

def grid_to_pixel(col, row):
    x = OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
    y = OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
    return x, y


def pixel_to_grid(x, y):
    col = int((x - OFFSET_X) // TILE_SIZE)
    row = int((y - OFFSET_Y) // TILE_SIZE)
    return col, row


def is_wall(col, row):
    if col < 0 or row < 0 or col >= COLS or row >= ROWS:
        return True
    return MAZE_LAYOUT[row][col] == '1'


def has_dot(col, row):
    return MAZE_LAYOUT[row][col] == '2'


def has_power(col, row):
    return MAZE_LAYOUT[row][col] == '3'


def is_path(col, row):
    if col < 0 or row < 0 or col >= COLS or row >= ROWS:
        return False
    return MAZE_LAYOUT[row][col] in ('0', '2', '3')


class Entity:
    def __init__(self, col, row, color, speed):
        self.spawn_col = col
        self.spawn_row = row
        self.x, self.y = grid_to_pixel(col, row)
        self.dir = pygame.Vector2(0, 0)
        self.next_dir = pygame.Vector2(0, 0)
        self.color = color
        self.speed = speed
        self.radius = TILE_SIZE // 2 - 2

    def rect(self):
        return Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, surface, color=None):
        pygame.draw.circle(surface, color or self.color, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        self.x, self.y = grid_to_pixel(self.spawn_col, self.spawn_row)
        self.dir.update(0, 0)
        self.next_dir.update(0, 0)

    def at_center_of_tile(self):
        cx, cy = grid_to_pixel(*pixel_to_grid(self.x, self.y))
        return abs(self.x - cx) < 0.5 and abs(self.y - cy) < 0.5

    def snap_to_center(self):
        cx, cy = grid_to_pixel(*pixel_to_grid(self.x, self.y))
        self.x, self.y = cx, cy


class Pacman(Entity):
    def __init__(self, col, row):
        super().__init__(col, row, YELLOW, PACMAN_SPEED)
        self.mouth_angle = 0.25
        self.mouth_dir = 1

    def update(self, dt, maze):
        # handle direction changes only at tile centers
        if self.next_dir.length_squared() > 0 and self.at_center_of_tile():
            ncol, nrow = pixel_to_grid(self.x, self.y)
            if self.can_move(ncol, nrow, self.next_dir):
                self.dir = self.next_dir.copy()

        # continue in current direction if possible, else stop at center
        if self.dir.length_squared() > 0:
            col, row = pixel_to_grid(self.x, self.y)
            if self.can_move(col, row, self.dir):
                self.x += self.dir.x * self.speed
                self.y += self.dir.y * self.speed
            else:
                # if we hit a wall, snap to center and stop
                if not self.at_center_of_tile():
                    self.snap_to_center()
                self.dir.update(0, 0)

        # animate mouth
        self.mouth_angle += self.mouth_dir * dt * 2.5
        if self.mouth_angle > 0.40:
            self.mouth_angle = 0.40
            self.mouth_dir = -1
        elif self.mouth_angle < 0.05:
            self.mouth_angle = 0.05
            self.mouth_dir = 1

    def can_move(self, col, row, direction):
        target_col = col + int(direction.x)
        target_row = row + int(direction.y)
        return not is_wall(target_col, target_row)

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.next_dir = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.next_dir = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP]:
            self.next_dir = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            self.next_dir = pygame.Vector2(0, 1)

    def draw(self, surface, color=None):
        # draw pacman with an open mouth using arc
        center = (int(self.x), int(self.y))
        r = self.radius
        # compute angle based on current direction
        angle_offset = 0
        if self.dir.x < 0:
            angle_offset = math.pi
        elif self.dir.y < 0:
            angle_offset = -math.pi / 2
        elif self.dir.y > 0:
            angle_offset = math.pi / 2
        start_angle = angle_offset + self.mouth_angle * math.pi
        end_angle = angle_offset - self.mouth_angle * math.pi + 2 * math.pi
        pygame.draw.circle(surface, color or self.color, center, r)
        # draw the mouth as a filled polygon matching the arc opening
        p1 = center
        p2 = (int(self.x + math.cos(start_angle) * r), int(self.y + math.sin(start_angle) * r))
        p3 = (int(self.x + math.cos(end_angle) * r), int(self.y + math.sin(end_angle) * r))
        pygame.draw.polygon(surface, BLACK, [p1, p2, p3])


class Ghost(Entity):
    def __init__(self, col, row, color, base_col, base_row):
        super().__init__(col, row, color, GHOST_SPEED)
        self.state = GHOST_NORMAL
        self.frightened_timer = 0.0
        self.base_col = base_col
        self.base_row = base_row

    def set_frightened(self):
        if self.state != GHOST_EATEN:
            self.state = GHOST_FRIGHTENED
            self.frightened_timer = POWER_DURATION

    def update(self, dt, target_pos):
        # state handling
        if self.state == GHOST_FRIGHTENED:
            self.frightened_timer -= dt
            if self.frightened_timer <= 0:
                self.state = GHOST_NORMAL

        # speed depends on state
        spd = FRIGHTENED_SPEED if self.state == GHOST_FRIGHTENED else (GHOST_SPEED if self.state == GHOST_NORMAL else GHOST_SPEED * 1.35)

        # choose direction at tile centers
        if self.at_center_of_tile():
            self.choose_direction(target_pos)
        # move if possible
        col, row = pixel_to_grid(self.x, self.y)
        if not is_wall(col + int(self.dir.x), row + int(self.dir.y)):
            self.x += self.dir.x * spd
            self.y += self.dir.y * spd
        else:
            # blocked, pick a new direction
            self.choose_direction(target_pos)

        # if eaten, check if reached base
        if self.state == GHOST_EATEN:
            bx, by = grid_to_pixel(self.base_col, self.base_row)
            if abs(self.x - bx) < 1.0 and abs(self.y - by) < 1.0:
                self.snap_to_center()
                self.state = GHOST_NORMAL

    def choose_direction(self, target_pos):
        col, row = pixel_to_grid(self.x, self.y)
        # available directions excluding reverse
        dirs = [pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)]
        valid_dirs = []
        for d in dirs:
            # disallow reversing unless blocked or at start
            if self.dir.length_squared() > 0 and d.x == -self.dir.x and d.y == -self.dir.y:
                continue
            if not is_wall(col + int(d.x), row + int(d.y)):
                valid_dirs.append(d)
        if not valid_dirs:
            self.dir *= -1
            return

        # AI policy:
        # - NORMAL: choose direction that minimizes distance to target (pacman)
        # - FRIGHTENED: choose direction that maximizes distance (run away)
        # - EATEN: target is base
        if self.state == GHOST_EATEN:
            target = pygame.Vector2(*grid_to_pixel(self.base_col, self.base_row))
        else:
            target = pygame.Vector2(target_pos)
        best = None
        best_score = None
        for d in valid_dirs:
            nx, ny = grid_to_pixel(col + int(d.x), row + int(d.y))
            dist = pygame.Vector2(nx, ny).distance_to(target)
            # use score based on state
            score = -dist if self.state != GHOST_FRIGHTENED else dist
            if best is None or score > best_score:
                best = d
                best_score = score
        # add small randomness in frightened mode to avoid being deterministic
        if self.state == GHOST_FRIGHTENED and random.random() < 0.20:
            self.dir = random.choice(valid_dirs)
        else:
            self.dir = best

    def draw(self, surface, color=None):
        # frightened ghosts are cyan; eaten ghosts are grey (eyes)
        draw_color = color or (CYAN if self.state == GHOST_FRIGHTENED else (GREY if self.state == GHOST_EATEN else self.color))
        super().draw(surface, draw_color)
        # eyes (simple)
        eye_offset = 4
        pygame.draw.circle(surface, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
        pygame.draw.circle(surface, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)

    def got_eaten(self):
        self.state = GHOST_EATEN
        self.dir = pygame.Vector2(0, 0)

    def reset(self):
        super().reset()
        self.state = GHOST_NORMAL
        self.frightened_timer = 0.0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Python + Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)

        # Build dot/power arrays from MAZE_LAYOUT
        self.dots = set()
        self.powers = set()
        for r in range(ROWS):
            for c in range(COLS):
                if MAZE_LAYOUT[r][c] == '2':
                    self.dots.add((c, r))
                elif MAZE_LAYOUT[r][c] == '3':
                    self.powers.add((c, r))

        # Positions
        self.pacman = Pacman(1, 1)
        # Choose a ghost base on an open tile near the center (avoid walls)
        base_col, base_row = COLS // 2, 9
        self.ghosts = [
            Ghost(base_col, base_row, RED, base_col, base_row),
            Ghost(base_col - 2, base_row, PINK, base_col, base_row),
            Ghost(base_col + 2, base_row, CYAN, base_col, base_row),
            Ghost(base_col, base_row - 2, ORANGE, base_col, base_row),
        ]

        # Game state
        self.score = 0
        self.lives = START_LIVES
        self.game_over = False
        self.win = False
        self.power_timer = 0.0

    def reset_round(self, full_reset=False):
        # reset positions, keep score/lives unless full_reset
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()
        self.power_timer = 0.0
        if full_reset:
            self.score = 0
            self.lives = START_LIVES
            self.game_over = False
            self.win = False
            # rebuild dots and powers
            self.dots.clear()
            self.powers.clear()
            for r in range(ROWS):
                for c in range(COLS):
                    if MAZE_LAYOUT[r][c] == '2':
                        self.dots.add((c, r))
                    elif MAZE_LAYOUT[r][c] == '3':
                        self.powers.add((c, r))

    def set_all_ghosts_frightened(self):
        for g in self.ghosts:
            g.set_frightened()

    def update(self, dt):
        if self.game_over or self.win:
            return

        keys = pygame.key.get_pressed()
        self.pacman.handle_input(keys)
        self.pacman.update(dt, MAZE_LAYOUT)

        # Eat dots/power
        pcol, prow = pixel_to_grid(self.pacman.x, self.pacman.y)
        if (pcol, prow) in self.dots and self.pacman.at_center_of_tile():
            self.dots.remove((pcol, prow))
            self.score += DOT_SCORE
        if (pcol, prow) in self.powers and self.pacman.at_center_of_tile():
            self.powers.remove((pcol, prow))
            self.score += POWER_DOT_SCORE
            self.set_all_ghosts_frightened()

        # Win condition
        if not self.dots and not self.powers:
            self.win = True

        # Update ghosts
        target_pos = (self.pacman.x, self.pacman.y)
        for g in self.ghosts:
            g.update(dt, target_pos if g.state != GHOST_EATEN else None)

        # Collisions
        p_rect = self.pacman.rect()
        for g in self.ghosts:
            if p_rect.colliderect(g.rect()):
                if g.state == GHOST_FRIGHTENED:
                    g.got_eaten()
                    self.score += GHOST_EAT_SCORE
                elif g.state == GHOST_NORMAL:
                    # lose life and reset positions
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_round(full_reset=False)
                    break

    def draw_maze(self):
        # draw walls and tiles
        for r in range(ROWS):
            for c in range(COLS):
                x = OFFSET_X + c * TILE_SIZE
                y = OFFSET_Y + r * TILE_SIZE
                tile = MAZE_LAYOUT[r][c]
                if tile == '1':
                    pygame.draw.rect(self.screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # draw background
                    pygame.draw.rect(self.screen, NAVY, (x, y, TILE_SIZE, TILE_SIZE))
                    # draw dots/power remaining
                    if (c, r) in self.dots:
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), max(2, TILE_SIZE // 10))
                    if (c, r) in self.powers:
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), max(5, TILE_SIZE // 5))

    def draw_ui(self):
        # score and lives
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 10, 10))

        if self.game_over:
            msg = self.big_font.render("GAME OVER - Press R to Restart", True, WHITE)
            self.screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 30))
        elif self.win:
            msg = self.big_font.render("YOU WIN! - Press R to Restart", True, WHITE)
            self.screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 30))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_ui()
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
                    if event.key == pygame.K_r and (self.game_over or self.win):
                        self.reset_round(full_reset=True)

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
