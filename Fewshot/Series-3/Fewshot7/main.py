import sys
import math
import random
import pygame
from typing import List, Tuple

# -------------------------------
# Configuration and Constants
# -------------------------------
SCREEN_WIDTH = 840
SCREEN_HEIGHT = 840
FPS = 60

TILE_SIZE = 40  # Size of one grid tile in pixels
WALL_COLOR = (0, 70, 200)
BG_COLOR = (0, 0, 0)
PELLET_COLOR = (255, 200, 50)
POWER_PELLET_COLOR = (255, 255, 255)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLORS = [(255, 100, 100), (100, 255, 255)]  # two ghosts
GHOST_FRIGHTENED_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)

PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
GHOST_EAT_SCORE = 200

POWER_DURATION = 7.0  # seconds
PACMAN_SPEED = 3  # pixels per frame
GHOST_SPEED = 2

# 1 = Wall, 0 = Empty, 2 = Pellet, 3 = Power Pellet
MAZE_LAYOUT: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 2, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 3, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])

SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE

# -------------------------------
# Helper functions
# -------------------------------

def grid_to_pixel(cell: Tuple[int, int]) -> Tuple[int, int]:
    r, c = cell
    return c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2


def pixel_to_grid(pos: Tuple[float, float]) -> Tuple[int, int]:
    x, y = pos
    return int(y // TILE_SIZE), int(x // TILE_SIZE)


def is_wall(r: int, c: int) -> bool:
    if r < 0 or c < 0 or r >= ROWS or c >= COLS:
        return True
    return MAZE_LAYOUT[r][c] == 1


def is_walkable(r: int, c: int) -> bool:
    if r < 0 or c < 0 or r >= ROWS or c >= COLS:
        return False
    return MAZE_LAYOUT[r][c] != 1


def at_cell_center(x: float, y: float) -> bool:
    cx = (int(x) // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
    cy = (int(y) // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
    return abs(x - cx) <= PACMAN_SPEED and abs(y - cy) <= PACMAN_SPEED


# Directions: (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRS = [UP, DOWN, LEFT, RIGHT]


def opposite_dir(d: Tuple[int, int]) -> Tuple[int, int]:
    return (-d[0], -d[1])


# -------------------------------
# Game Entities
# -------------------------------
class Pacman:
    def __init__(self, start_cell: Tuple[int, int]):
        self.start_pos = grid_to_pixel(start_cell)
        self.x, self.y = self.start_pos
        self.radius = TILE_SIZE // 2 - 4
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.lives = 3
        self.score = 0
        self.power_time_left = 0.0

    @property
    def cell(self) -> Tuple[int, int]:
        return pixel_to_grid((self.x, self.y))

    def set_next_dir(self, d: Tuple[int, int]):
        self.next_dir = d

    def update(self, dt: float):
        # Attempt to turn at cell centers
        if at_cell_center(self.x, self.y) and self.next_dir != self.dir:
            r, c = self.cell
            ndx, ndy = self.next_dir
            nr, nc = r + ndy, c + ndx
            if is_walkable(nr, nc):
                # snap to center before turning
                self.x, self.y = grid_to_pixel((r, c))
                self.dir = self.next_dir

        # Move forward if path is clear
        dx, dy = self.dir
        if dx != 0 or dy != 0:
            nx = self.x + dx * PACMAN_SPEED
            ny = self.y + dy * PACMAN_SPEED
            # check collision ahead based on next position center mapping
            r, c = pixel_to_grid((nx, ny))
            if is_walkable(r, c):
                self.x, self.y = nx, ny
            else:
                # snap to center when hitting wall
                cr, cc = self.cell
                self.x, self.y = grid_to_pixel((cr, cc))

        # Decrease power timer
        if self.power_time_left > 0:
            self.power_time_left = max(0.0, self.power_time_left - dt)

    def eat(self):
        r, c = self.cell
        tile = MAZE_LAYOUT[r][c]
        if tile == 2:
            MAZE_LAYOUT[r][c] = 0
            self.score += PELLET_SCORE
        elif tile == 3:
            MAZE_LAYOUT[r][c] = 0
            self.score += POWER_PELLET_SCORE
            self.power_time_left = POWER_DURATION

    def draw(self, surf: pygame.Surface):
        # Draw Pacman as a circle with simple mouth animation towards current dir
        center = (int(self.x), int(self.y))
        angle_open = 30
        direction_angle = 0
        if self.dir == RIGHT:
            direction_angle = 0
        elif self.dir == LEFT:
            direction_angle = 180
        elif self.dir == UP:
            direction_angle = 90
        elif self.dir == DOWN:
            direction_angle = 270
        else:
            # idle
            pygame.draw.circle(surf, PACMAN_COLOR, center, self.radius)
            return
        start_angle = math.radians(direction_angle - angle_open)
        end_angle = math.radians(direction_angle + angle_open)
        pygame.draw.circle(surf, PACMAN_COLOR, center, self.radius)
        # draw mouth as triangle (fill black)
        mouth_points = [
            center,
            (
                int(self.x + math.cos(start_angle) * self.radius),
                int(self.y - math.sin(start_angle) * self.radius),
            ),
            (
                int(self.x + math.cos(end_angle) * self.radius),
                int(self.y - math.sin(end_angle) * self.radius),
            ),
        ]
        pygame.draw.polygon(surf, BG_COLOR, mouth_points)

    def reset_position(self):
        self.x, self.y = self.start_pos
        self.dir = (0, 0)
        self.next_dir = (0, 0)


class Ghost:
    def __init__(self, start_cell: Tuple[int, int], color: Tuple[int, int, int]):
        self.start_cell = start_cell
        self.x, self.y = grid_to_pixel(start_cell)
        self.color = color
        self.radius = TILE_SIZE // 2 - 6
        self.dir = random.choice(DIRS)

    @property
    def cell(self) -> Tuple[int, int]:
        return pixel_to_grid((self.x, self.y))

    def update(self, dt: float, frightened: bool):
        speed = GHOST_SPEED if not frightened else max(1, GHOST_SPEED - 1)
        # choose new direction at cell centers
        if at_cell_center(self.x, self.y):
            r, c = self.cell
            options = []
            for d in DIRS:
                if d == opposite_dir(self.dir):
                    continue
                dx, dy = d
                nr, nc = r + dy, c + dx
                if is_walkable(nr, nc):
                    options.append(d)
            if not options:
                # dead end, can go back
                back = opposite_dir(self.dir)
                dx, dy = back
                nr, nc = r + dy, c + dx
                if is_walkable(nr, nc):
                    options = [back]
            if options:
                # random choice; if frightened, bias to avoid Pacman later in main loop (handled by not here)
                self.dir = random.choice(options)
                # snap to center
                self.x, self.y = grid_to_pixel((r, c))
        # move
        dx, dy = self.dir
        nx = self.x + dx * speed
        ny = self.y + dy * speed
        r, c = pixel_to_grid((nx, ny))
        if is_walkable(r, c):
            self.x, self.y = nx, ny
        else:
            # snap to center
            cr, cc = self.cell
            self.x, self.y = grid_to_pixel((cr, cc))

    def draw(self, surf: pygame.Surface, frightened: bool):
        center = (int(self.x), int(self.y))
        body_color = GHOST_FRIGHTENED_COLOR if frightened else self.color
        pygame.draw.circle(surf, body_color, center, self.radius)
        # Add simple eyes
        eye_offset = self.radius // 3
        eye_radius = max(2, self.radius // 5)
        pygame.draw.circle(surf, (255, 255, 255), (center[0] - eye_offset, center[1] - eye_offset), eye_radius)
        pygame.draw.circle(surf, (255, 255, 255), (center[0] + eye_offset, center[1] - eye_offset), eye_radius)

    def reset_position(self):
        self.x, self.y = grid_to_pixel(self.start_cell)
        self.dir = random.choice(DIRS)


# -------------------------------
# Drawing helpers
# -------------------------------

def draw_maze(surf: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            tile = MAZE_LAYOUT[r][c]
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            if tile == 1:
                pygame.draw.rect(surf, WALL_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == 2:
                pygame.draw.circle(
                    surf,
                    PELLET_COLOR,
                    (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                    max(3, TILE_SIZE // 10),
                )
            elif tile == 3:
                pygame.draw.circle(
                    surf,
                    POWER_PELLET_COLOR,
                    (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                    max(6, TILE_SIZE // 6),
                )


def remaining_pellets() -> int:
    count = 0
    for row in MAZE_LAYOUT:
        for t in row:
            if t in (2, 3):
                count += 1
    return count


# -------------------------------
# Game State Management
# -------------------------------

def reset_board(original_layout: List[List[int]]):
    for r in range(ROWS):
        for c in range(COLS):
            MAZE_LAYOUT[r][c] = original_layout[r][c]


# -------------------------------
# Main Game Loop
# -------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pacman Pygame - Contoh")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # Preserve original layout for resets
    original_layout = [row.copy() for row in MAZE_LAYOUT]

    # Spawn positions (grid coords)
    pac_start = (1, 1)
    ghost_starts = [(5, 10), (3, 14)]

    pacman = Pacman(pac_start)
    ghosts = [Ghost(ghost_starts[0], GHOST_COLORS[0]), Ghost(ghost_starts[1], GHOST_COLORS[1])]

    running = True
    game_over = False
    win = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over or win:
                    if event.key == pygame.K_r:
                        # Reset game
                        reset_board(original_layout)
                        pacman = Pacman(pac_start)
                        ghosts = [Ghost(ghost_starts[0], GHOST_COLORS[0]), Ghost(ghost_starts[1], GHOST_COLORS[1])]
                        game_over = False
                        win = False
                else:
                    if event.key == pygame.K_UP:
                        pacman.set_next_dir(UP)
                    elif event.key == pygame.K_DOWN:
                        pacman.set_next_dir(DOWN)
                    elif event.key == pygame.K_LEFT:
                        pacman.set_next_dir(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        pacman.set_next_dir(RIGHT)

        if not (game_over or win):
            # Update logic
            pacman.update(dt)
            pacman.eat()

            frightened = pacman.power_time_left > 0
            for g in ghosts:
                # Optional: simple avoidance when frightened
                if frightened and at_cell_center(g.x, g.y):
                    gr, gc = g.cell
                    pr, pc = pacman.cell
                    # pick option that increases distance from Pacman if possible
                    options = []
                    for d in DIRS:
                        if d == opposite_dir(g.dir):
                            continue
                        dx, dy = d
                        nr, nc = gr + dy, gc + dx
                        if is_walkable(nr, nc):
                            dist = (nr - pr) ** 2 + (nc - pc) ** 2
                            options.append((dist, d))
                    if options:
                        options.sort(reverse=True)  # prefer farther
                        g.dir = options[0][1]
                        g.x, g.y = grid_to_pixel((gr, gc))
                g.update(dt, frightened)

            # Collisions
            pac_rect = pygame.Rect(int(pacman.x - pacman.radius), int(pacman.y - pacman.radius), pacman.radius * 2, pacman.radius * 2)
            new_ghosts = []
            for g in ghosts:
                ghost_rect = pygame.Rect(int(g.x - g.radius), int(g.y - g.radius), g.radius * 2, g.radius * 2)
                if pac_rect.colliderect(ghost_rect):
                    if frightened:
                        pacman.score += GHOST_EAT_SCORE
                        g.reset_position()
                    else:
                        # lose life and reset positions
                        pacman.lives -= 1
                        pacman.reset_position()
                        for gg in ghosts:
                            gg.reset_position()
                        if pacman.lives <= 0:
                            game_over = True
                        break
                new_ghosts.append(g)

            # Win condition
            if remaining_pellets() == 0 and not game_over:
                win = True

        # Draw
        screen.fill(BG_COLOR)
        draw_maze(screen)
        frightened = pacman.power_time_left > 0
        for g in ghosts:
            g.draw(screen, frightened)
        pacman.draw(screen)

        # HUD
        hud_lines = [
            f"Skor: {pacman.score}",
            f"Nyawa: {pacman.lives}",
        ]
        if pacman.power_time_left > 0:
            hud_lines.append(f"Power: {pacman.power_time_left:0.1f}s")
        if game_over:
            hud_lines.append("GAME OVER - Tekan R untuk reset")
        if win:
            hud_lines.append("MENANG! - Tekan R untuk reset")
        for i, text in enumerate(hud_lines):
            surf = font.render(text, True, TEXT_COLOR)
            screen.blit(surf, (10, 10 + i * 24))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
