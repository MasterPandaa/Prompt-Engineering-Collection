import pygame
import random
import sys
from typing import List, Tuple, Dict

# ----------------------
# Game Configuration
# ----------------------
WIN_WIDTH = 600
WIN_HEIGHT = 740
PLAY_WIDTH = 300   # 10 columns * 30 px
PLAY_HEIGHT = 600  # 20 rows * 30 px
BLOCK_SIZE = 30

# Top-left of playfield
TOP_LEFT_X = (WIN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# ----------------------
# Tetromino Definitions
# Using relative coordinates around a pivot (0,0).
# Rotation by 90 degrees clockwise uses (x, y) -> (y, -x)
# ----------------------
# Official 7 tetrominoes: I, O, T, S, Z, J, L

# Each shape is defined as a list of (x, y) relative coordinates including pivot at (0,0)
I_SHAPE = [(0, 0), (-1, 0), (1, 0), (2, 0)]
O_SHAPE = [(0, 0), (1, 0), (0, 1), (1, 1)]
T_SHAPE = [(0, 0), (-1, 0), (1, 0), (0, -1)]
S_SHAPE = [(0, 0), (-1, 0), (0, -1), (1, -1)]
Z_SHAPE = [(0, 0), (1, 0), (0, -1), (-1, -1)]
J_SHAPE = [(0, 0), (-1, 0), (1, 0), (-1, -1)]
L_SHAPE = [(0, 0), (-1, 0), (1, 0), (1, -1)]

SHAPES = [I_SHAPE, O_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, J_SHAPE, L_SHAPE]
SHAPE_COLORS = {
    tuple(I_SHAPE): CYAN,
    tuple(O_SHAPE): YELLOW,
    tuple(T_SHAPE): MAGENTA,
    tuple(S_SHAPE): GREEN,
    tuple(Z_SHAPE): RED,
    tuple(J_SHAPE): BLUE,
    tuple(L_SHAPE): ORANGE,
}

# Grid size
COLS = 10
ROWS = 20

# ----------------------
# Helper classes and functions
# ----------------------
class Piece:
    def __init__(self, x: int, y: int, shape: List[Tuple[int, int]], color: Tuple[int, int, int]):
        # Grid coordinates for pivot
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # number of 90-degree clockwise rotations

    def rotated_offsets(self) -> List[Tuple[int, int]]:
        # Apply rotation matrix (x, y) -> (y, -x) rotation times
        offsets = self.shape
        r = self.rotation % 4
        if self.shape is O_SHAPE:
            # O shape does not change on rotation, but keep list copy
            return list(offsets)
        result = []
        for (x, y) in offsets:
            rx, ry = x, y
            for _ in range(r):
                rx, ry = ry, -rx
            result.append((rx, ry))
        return result

    def block_positions(self) -> List[Tuple[int, int]]:
        # Convert to grid positions
        positions = []
        for (dx, dy) in self.rotated_offsets():
            positions.append((self.x + dx, self.y + dy))
        return positions


def create_grid(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = {(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == BLACK}
    for (x, y) in piece.block_positions():
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    for (x, y) in locked:
        if y < 0 or y == 0:
            return True
    return False


def get_random_piece() -> Piece:
    shape = random.choice(SHAPES)
    color = SHAPE_COLORS[tuple(shape)]
    # Spawn near top center, pivot at column 5 (index 5 -> 0..9)
    spawn_x = COLS // 2
    spawn_y = 1  # a bit down to allow negative offsets
    p = Piece(spawn_x, spawn_y, shape, color)
    # Nudge spawn for I piece that might extend right
    if shape is I_SHAPE:
        p.y = 0
    return p


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    return piece.block_positions()


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            # Row y is full
            cleared += 1
            # Remove locked blocks in this row
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # Shift every locked block above down by 1
            new_locked = {}
            for (x, yy), color in locked.items():
                if yy < y:
                    new_locked[(x, yy + 1)] = color
                else:
                    new_locked[(x, yy)] = color
            locked.clear()
            locked.update(new_locked)
    return cleared


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
         TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2),
    )


def draw_grid_lines(surface):
    # Draw grid lines over playfield
    for y in range(ROWS + 1):
        pygame.draw.line(
            surface,
            GREY,
            (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE),
            (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE),
        )
    for x in range(COLS + 1):
        pygame.draw.line(
            surface,
            GREY,
            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y),
            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT),
        )


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont("comicsans", 28)
    label = font.render("Next", True, WHITE)

    sx = TOP_LEFT_X + PLAY_WIDTH + 30
    sy = TOP_LEFT_Y + 60
    surface.blit(label, (sx, sy - 40))

    # Draw the shape in a small box
    for (dx, dy) in piece.rotated_offsets():
        x = sx + (dx + 1) * BLOCK_SIZE
        y = sy + (dy + 1) * BLOCK_SIZE
        pygame.draw.rect(surface, piece.color, (x, y, BLOCK_SIZE, BLOCK_SIZE), 0)
        pygame.draw.rect(surface, GREY, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_window(surface, grid, score, lines_cleared):
    surface.fill((20, 20, 20))

    # Title
    font = pygame.font.SysFont("comicsans", 48)
    label = font.render("TETRIS", True, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 30))

    # Score
    font_small = pygame.font.SysFont("comicsans", 28)
    score_label = font_small.render(f"Score: {score}", True, WHITE)
    lines_label = font_small.render(f"Lines: {lines_cleared}", True, WHITE)
    surface.blit(score_label, (TOP_LEFT_X - 170, TOP_LEFT_Y))
    surface.blit(lines_label, (TOP_LEFT_X - 170, TOP_LEFT_Y + 40))

    # Playfield frame
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 3)

    # Draw blocks
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                )
                pygame.draw.rect(
                    surface,
                    GREY,
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1,
                )

    draw_grid_lines(surface)


def try_rotate_with_kicks(current_piece: Piece, grid) -> None:
    # Attempt rotation; if invalid, try simple wall kicks: shift by -1, +1, -2, +2
    original_rotation = current_piece.rotation
    original_x = current_piece.x

    current_piece.rotation = (current_piece.rotation + 1) % 4
    if valid_space(current_piece, grid):
        return

    for shift in [-1, 1, -2, 2]:
        current_piece.x = original_x + shift
        if valid_space(current_piece, grid):
            return

    # Revert if all fail
    current_piece.rotation = original_rotation
    current_piece.x = original_x


def main(win):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_random_piece()
    next_piece = get_random_piece()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # seconds per cell drop
    score = 0
    lines_cleared_total = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Piece falls automatically
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        change_piece = True
                elif event.key == pygame.K_UP:
                    try_rotate_with_kicks(current_piece, grid)
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                elif event.key == pygame.K_r:
                    # reset
                    return True

        shape_pos = convert_shape_format(current_piece)

        # Add piece to grid for drawing
        for (x, y) in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        # If piece locked
        if change_piece:
            for (x, y) in shape_pos:
                if y < 0:
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                # Scoring: 100, 300, 500, 800 for 1..4 lines
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 300
                elif cleared == 3:
                    score += 500
                else:
                    score += 800
                lines_cleared_total += cleared

            current_piece = next_piece
            next_piece = get_random_piece()
            change_piece = False

            # Speed up slightly over time
            fall_speed = max(0.1, 0.5 - (lines_cleared_total // 10) * 0.05)

        draw_window(win, grid, score, lines_cleared_total)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    # Game over screen
    draw_window(win, grid, score, lines_cleared_total)
    draw_text_middle(win, "GAME OVER", 48, WHITE)
    pygame.display.update()

    # Wait for R to restart or Q/ESC to quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    waiting = False
                    return True


def main_menu():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    running = True
    while running:
        win.fill((20, 20, 20))
        draw_text_middle(win, "Press any key to play", 36, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                # Start game loop; if returns True, restart menu
                while main(win):
                    pass

    pygame.quit()


if __name__ == "__main__":
    main_menu()
