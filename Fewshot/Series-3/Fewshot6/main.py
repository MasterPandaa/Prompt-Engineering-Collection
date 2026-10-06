import sys
import random
import pygame
from typing import List, Tuple

# -----------------------------
# Config & Constants
# -----------------------------

# Colors
BLUE = (0, 82, 204)
NAVY = (0, 40, 90)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
RED = (230, 30, 30)
PINK = (255, 100, 180)
GREY = (40, 40, 40)

# Tile definitions
WALL = 1
PELLET = 2
POWER = 3
EMPTY = 0

# Game config
CELL_SIZE = 48  # pixels per grid cell
HUD_HEIGHT = 64
PACMAN_SPEED = 3  # pixels per frame
GHOST_SPEED = 2   # pixels per frame
POWER_DURATION_MS = 6000  # duration of power mode
FPS = 60

# Provided Maze Layout (Grid-based)
# 1 = Dinding, 0 = Jalur Kosong, 2 = Pelet Kecil, 3 = Power Pellet
MAZE_LAYOUT: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + HUD_HEIGHT

Vec2 = Tuple[int, int]

# -----------------------------
# Utility Functions
# -----------------------------

def grid_to_px(cell: Vec2) -> Vec2:
    cx, cy = cell
    return int(cx * CELL_SIZE + CELL_SIZE // 2), int(HUD_HEIGHT + cy * CELL_SIZE + CELL_SIZE // 2)


def px_to_grid(px: Vec2) -> Vec2:
    x, y = px
    grid_x = (x) // CELL_SIZE
    grid_y = (y - HUD_HEIGHT) // CELL_SIZE
    return int(grid_x), int(grid_y)


def is_wall(maze: List[List[int]], cell: Vec2) -> bool:
    x, y = cell
    if x < 0 or y < 0 or x >= COLS or y >= ROWS:
        return True
    return maze[y][x] == WALL


def valid_dirs(maze: List[List[int]], cell: Vec2) -> List[Vec2]:
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    res = []
    for dx, dy in dirs:
        nx, ny = cell[0] + dx, cell[1] + dy
        if not is_wall(maze, (nx, ny)):
            res.append((dx, dy))
    return res


def opposite_dir(d: Vec2) -> Vec2:
    return (-d[0], -d[1])


def at_tile_center(px_pos: Tuple[float, float]) -> bool:
    x, y = px_pos
    # Center when close to cell center within a small epsilon.
    cx = (x - CELL_SIZE // 2) % CELL_SIZE
    cy = ((y - HUD_HEIGHT) - CELL_SIZE // 2) % CELL_SIZE
    return abs(cx) < 1.5 and abs(cy) < 1.5


# -----------------------------
# Entities
# -----------------------------

class Pacman:
    def __init__(self, start_cell: Vec2):
        self.start_cell = start_cell
        self.pos_x, self.pos_y = grid_to_px(start_cell)
        self.dir: Vec2 = (0, 0)
        self.next_dir: Vec2 = (0, 0)
        self.radius = CELL_SIZE // 2 - 4
        self.alive = True
        self.score = 0
        self.lives = 3
        self.power = False
        self.power_end_time = 0

    def reset_position(self):
        self.pos_x, self.pos_y = grid_to_px(self.start_cell)
        self.dir = (0, 0)
        self.next_dir = (0, 0)

    def set_dir(self, d: Vec2):
        self.next_dir = d

    def update(self, maze: List[List[int]], now_ms: int):
        # Handle power timeout
        if self.power and now_ms >= self.power_end_time:
            self.power = False

        # Attempt to turn into next_dir when centered in a tile
        if self.next_dir != self.dir and at_tile_center((self.pos_x, self.pos_y)):
            gx, gy = px_to_grid((self.pos_x, self.pos_y))
            ndx, ndy = self.next_dir
            if not is_wall(maze, (gx + ndx, gy + ndy)):
                self.dir = self.next_dir

        # If currently blocked, stop movement
        if at_tile_center((self.pos_x, self.pos_y)):
            gx, gy = px_to_grid((self.pos_x, self.pos_y))
            dx, dy = self.dir
            if is_wall(maze, (gx + dx, gy + dy)):
                self.dir = (0, 0)

        # Move
        self.pos_x += self.dir[0] * PACMAN_SPEED
        self.pos_y += self.dir[1] * PACMAN_SPEED

        # Clamp inside bounds (safety)
        self.pos_x = max(CELL_SIZE // 2, min(WIDTH - CELL_SIZE // 2, self.pos_x))
        self.pos_y = max(HUD_HEIGHT + CELL_SIZE // 2, min(HUD_HEIGHT + ROWS * CELL_SIZE - CELL_SIZE // 2, self.pos_y))

        # Eat pellets
        gx, gy = px_to_grid((self.pos_x, self.pos_y))
        if 0 <= gx < COLS and 0 <= gy < ROWS:
            tile = maze[gy][gx]
            if tile == PELLET:
                self.score += 10
                maze[gy][gx] = EMPTY
            elif tile == POWER:
                self.score += 50
                maze[gy][gx] = EMPTY
                self.power = True
                self.power_end_time = now_ms + POWER_DURATION_MS

    def draw(self, surf: pygame.Surface):
        color = YELLOW if not self.power else (255, 255, 120)
        pygame.draw.circle(surf, color, (int(self.pos_x), int(self.pos_y)), self.radius)
        # Simple mouth direction indicator
        mx = int(self.pos_x)
        my = int(self.pos_y)
        d = self.dir
        if d != (0, 0):
            eye_offset = 8
            if d == (1, 0):
                eye_pos = (mx + 8, my - 10)
            elif d == (-1, 0):
                eye_pos = (mx - 8, my - 10)
            elif d == (0, 1):
                eye_pos = (mx - 10, my + 8)
            else:
                eye_pos = (mx - 10, my - 8)
            pygame.draw.circle(surf, BLACK, eye_pos, 4)


class Ghost:
    def __init__(self, start_cell: Vec2, color: Tuple[int, int, int]):
        self.start_cell = start_cell
        self.pos_x, self.pos_y = grid_to_px(start_cell)
        self.dir: Vec2 = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = color
        self.radius = CELL_SIZE // 2 - 6
        self.frightened = False

    def reset(self):
        self.pos_x, self.pos_y = grid_to_px(self.start_cell)
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.frightened = False

    def update(self, maze: List[List[int]], pacman_power: bool):
        self.frightened = pacman_power

        # When centered on tile, possibly change direction.
        if at_tile_center((self.pos_x, self.pos_y)):
            gx, gy = px_to_grid((self.pos_x, self.pos_y))
            options = valid_dirs(maze, (gx, gy))
            # Avoid reversing unless no other option
            reverse = opposite_dir(self.dir)
            if len(options) > 1 and reverse in options:
                options.remove(reverse)
            if options:
                # In frightened mode, bias away from Pacman would be more advanced; here random.
                self.dir = random.choice(options)

        # Move
        speed = GHOST_SPEED - 1 if self.frightened else GHOST_SPEED
        self.pos_x += self.dir[0] * speed
        self.pos_y += self.dir[1] * speed

        # Clamp
        self.pos_x = max(CELL_SIZE // 2, min(WIDTH - CELL_SIZE // 2, self.pos_x))
        self.pos_y = max(HUD_HEIGHT + CELL_SIZE // 2, min(HUD_HEIGHT + ROWS * CELL_SIZE - CELL_SIZE // 2, self.pos_y))

    def draw(self, surf: pygame.Surface):
        color = (80, 80, 255) if self.frightened else self.color
        x, y = int(self.pos_x), int(self.pos_y)
        # Body
        pygame.draw.circle(surf, color, (x, y - self.radius // 3), self.radius)
        pygame.draw.rect(surf, color, (x - self.radius, y - self.radius // 3, self.radius * 2, self.radius))
        # Eyes
        pygame.draw.circle(surf, WHITE, (x - 8, y - 4), 6)
        pygame.draw.circle(surf, WHITE, (x + 8, y - 4), 6)
        pygame.draw.circle(surf, BLACK, (x - 8, y - 4), 3)
        pygame.draw.circle(surf, BLACK, (x + 8, y - 4), 3)


# -----------------------------
# Drawing
# -----------------------------

def draw_hud(surf: pygame.Surface, font: pygame.font.Font, score: int, lives: int, power: bool, time_left_ms: int):
    pygame.draw.rect(surf, GREY, (0, 0, WIDTH, HUD_HEIGHT))
    text = font.render(f"Skor: {score}", True, WHITE)
    surf.blit(text, (16, 16))
    lives_text = font.render(f"Nyawa: {lives}", True, WHITE)
    surf.blit(lives_text, (WIDTH // 2 - 60, 16))
    if power:
        secs = max(0, time_left_ms // 1000)
        p_text = font.render(f"POWER {secs}s", True, YELLOW)
        surf.blit(p_text, (WIDTH - 160, 16))


def draw_maze(surf: pygame.Surface, maze: List[List[int]]):
    # Background for maze area
    pygame.draw.rect(surf, BLACK, (0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT))

    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, HUD_HEIGHT + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            tile = maze[y][x]
            if tile == WALL:
                pygame.draw.rect(surf, NAVY, rect)
                pygame.draw.rect(surf, BLUE, rect, width=4)
            elif tile == PELLET:
                cx, cy = grid_to_px((x, y))
                pygame.draw.circle(surf, WHITE, (cx, cy), 5)
            elif tile == POWER:
                cx, cy = grid_to_px((x, y))
                pygame.draw.circle(surf, WHITE, (cx, cy), 10)
            # EMPTY -> nothing


# -----------------------------
# Game Logic
# -----------------------------

def check_collision_circle(a_pos: Tuple[float, float], a_r: int, b_pos: Tuple[float, float], b_r: int) -> bool:
    dx = a_pos[0] - b_pos[0]
    dy = a_pos[1] - b_pos[1]
    return dx * dx + dy * dy <= (a_r + b_r) * (a_r + b_r)


def remaining_pellets(maze: List[List[int]]) -> int:
    count = 0
    for row in maze:
        for t in row:
            if t == PELLET or t == POWER:
                count += 1
    return count


def clone_maze(layout: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in layout]


# -----------------------------
# Main Loop
# -----------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pacman - Pygame')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('consolas', 24)

    maze = clone_maze(MAZE_LAYOUT)

    # Spawn positions: choose a walkable cell for Pacman and ghosts
    pac_start = (1, 1)
    ghost1_start = (COLS - 2, 1)
    ghost2_start = (COLS - 2, ROWS - 2)

    pacman = Pacman(pac_start)
    ghosts = [
        Ghost(ghost1_start, RED),
        Ghost(ghost2_start, PINK),
    ]

    running = True
    game_over = False
    win = False

    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over or win:
                    if event.key == pygame.K_r:
                        # reset game
                        maze = clone_maze(MAZE_LAYOUT)
                        pacman = Pacman(pac_start)
                        ghosts = [Ghost(ghost1_start, RED), Ghost(ghost2_start, PINK)]
                        game_over = False
                        win = False
                    continue
                if event.key == pygame.K_LEFT:
                    pacman.set_dir((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    pacman.set_dir((1, 0))
                elif event.key == pygame.K_UP:
                    pacman.set_dir((0, -1))
                elif event.key == pygame.K_DOWN:
                    pacman.set_dir((0, 1))

        if not (game_over or win):
            # Update entities
            pacman.update(maze, now)
            for g in ghosts:
                g.update(maze, pacman.power)

            # Collisions Pacman vs Ghosts
            for g in ghosts:
                if check_collision_circle((pacman.pos_x, pacman.pos_y), pacman.radius,
                                          (g.pos_x, g.pos_y), g.radius):
                    if pacman.power:
                        pacman.score += 200
                        g.reset()
                    else:
                        pacman.lives -= 1
                        pacman.reset_position()
                        for gg in ghosts:
                            gg.reset()
                        if pacman.lives <= 0:
                            game_over = True
                        break

            # Win condition
            if remaining_pellets(maze) == 0:
                win = True

        # Draw
        screen.fill(BLACK)
        draw_hud(screen, font, pacman.score, pacman.lives, pacman.power, max(0, pacman.power_end_time - now))
        draw_maze(screen, maze)
        pacman.draw(screen)
        for g in ghosts:
            g.draw(screen)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            text1 = font.render("Game Over! Tekan R untuk restart", True, WHITE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 20))
        elif win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            text1 = font.render("Menang! Tekan R untuk restart", True, WHITE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
