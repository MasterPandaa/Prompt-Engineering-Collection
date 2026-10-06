import pygame
import random
import sys
from typing import Dict, List, Tuple

# -----------------------------
# Game Constants
# -----------------------------
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30  # pixel size of a single block
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT
TOP_LEFT_X = 0
TOP_LEFT_Y = 0

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# -----------------------------
# Tetromino Definitions (7 pieces)
# Each shape is a list of rotations, where a rotation is a list of (x, y) offsets
# relative to a pivot located at (piece.x, piece.y).
# -----------------------------

# Colors per shape
COLOR_I = (0, 240, 240)
COLOR_O = (240, 240, 0)
COLOR_T = (160, 0, 240)
COLOR_S = (0, 240, 0)
COLOR_Z = (240, 0, 0)
COLOR_J = (0, 0, 240)
COLOR_L = (240, 160, 0)

# Helper for rotations: define all 4 rotation states explicitly for clarity and control
SHAPES: List[List[List[Tuple[int, int]]]] = []
SHAPE_COLORS: List[Tuple[int, int, int]] = []

# I piece
I = [
    [(0, 0), (-1, 0), (1, 0), (2, 0)],     # horizontal
    [(0, 0), (0, -1), (0, 1), (0, 2)],     # vertical
    [(0, 0), (-1, 0), (1, 0), (2, 0)],     # horizontal
    [(0, 0), (0, -1), (0, 1), (0, 2)],     # vertical
]
# O piece (square) - rotation states are identical
O = [
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
]
# T piece
T = [
    [(0, 0), (-1, 0), (1, 0), (0, -1)],
    [(0, 0), (0, -1), (0, 1), (1, 0)],
    [(0, 0), (-1, 0), (1, 0), (0, 1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)],
]
# S piece
S = [
    [(0, 0), (-1, 0), (0, -1), (1, -1)],
    [(0, 0), (0, -1), (1, 0), (1, 1)],
    [(0, 0), (-1, 0), (0, -1), (1, -1)],
    [(0, 0), (0, -1), (1, 0), (1, 1)],
]
# Z piece
Z = [
    [(0, 0), (1, 0), (0, -1), (-1, -1)],
    [(0, 0), (0, -1), (-1, 0), (-1, 1)],
    [(0, 0), (1, 0), (0, -1), (-1, -1)],
    [(0, 0), (0, -1), (-1, 0), (-1, 1)],
]
# J piece
J = [
    [(0, 0), (-1, 0), (1, 0), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (-1, 0), (1, 0), (1, 1)],
    [(0, 0), (0, -1), (0, 1), (-1, 1)],
]
# L piece
L = [
    [(0, 0), (-1, 0), (1, 0), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, 1)],
    [(0, 0), (-1, 0), (1, 0), (-1, 1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
]

SHAPES = [I, O, T, S, Z, J, L]
SHAPE_COLORS = [COLOR_I, COLOR_O, COLOR_T, COLOR_S, COLOR_Z, COLOR_J, COLOR_L]


class Piece:\n    def __init__(self, x: int, y: int, shape_index: int):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.shape = SHAPES[shape_index]
        self.color = SHAPE_COLORS[shape_index]
        self.rotation = 0  # 0..3

    def get_cells(self) -> List[Tuple[int, int]]:
        # Convert current rotation to absolute grid positions
        offsets = self.shape[self.rotation % 4]
        return [(self.x + dx, self.y + dy) for (dx, dy) in offsets]


# -----------------------------
# Grid and Game Logic Helpers
# -----------------------------

def create_grid(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if grid[y][x] == BLACK]
    for (x, y) in piece.get_cells():
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and (x, y) not in accepted:
            return False
    return True


def in_bounds(piece: Piece) -> bool:
    for (x, y) in piece.get_cells():
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
    return True


def lock_piece(piece: Piece, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    for pos in piece.get_cells():
        locked[pos] = piece.color


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    rows_to_clear = []
    for y in range(GRID_HEIGHT):
        if BLACK not in grid[y]:
            rows_to_clear.append(y)

    if not rows_to_clear:
        return 0

    # Clear rows and shift everything above down
    for y in rows_to_clear:
        for x in range(GRID_WIDTH):
            try:
                del locked[(x, y)]
            except KeyError:
                pass

    # Move rows above down
    rows_cleared = 0
    for key in sorted(list(locked.keys()), key=lambda p: p[1], reverse=True):
        x, y = key
        shift = sum(1 for row in rows_to_clear if y < row)
        if shift > 0:
            color = locked.pop(key)
            locked[(x, y + shift)] = color
            rows_cleared = max(rows_cleared, shift)

    return len(rows_to_clear)


def check_lost(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    # If any locked block is above the top (y < 0) or in the top visible row (y < 1) it's game over
    for (_, y) in locked.keys():
        if y < 1:
            return True
    return False


def get_new_piece() -> Piece:
    idx = random.randrange(len(SHAPES))
    # Spawn near the top center; y starts slightly above visible to allow entry
    return Piece(GRID_WIDTH // 2, 0, idx)


# -----------------------------
# Drawing Helpers
# -----------------------------

def draw_grid_lines(surface: pygame.Surface):
    # Draw vertical lines
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(
            surface,
            GREY,
            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y),
            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT),
            1,
        )
    # Draw horizontal lines
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(
            surface,
            GREY,
            (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE),
            (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE),
            1,
        )


def draw_window(surface: pygame.Surface, grid: List[List[Tuple[int, int, int]]], score: int, next_piece: Piece):
    surface.fill((20, 20, 20))

    # Title
    font = pygame.font.SysFont("arial", 28, bold=True)
    label = font.render("TETRIS", True, WHITE)
    surface.blit(label, (PLAY_WIDTH + 20, 20))

    # Score
    small_font = pygame.font.SysFont("arial", 20)
    score_lbl = small_font.render(f"Skor: {score}", True, WHITE)
    surface.blit(score_lbl, (PLAY_WIDTH + 20, 60))

    # Next piece preview
    preview_lbl = small_font.render("Berikutnya:", True, WHITE)
    surface.blit(preview_lbl, (PLAY_WIDTH + 20, 100))

    for (x, y) in next_piece.shape[next_piece.rotation % 4]:
        px = PLAY_WIDTH + 60 + x * BLOCK_SIZE
        py = 140 + y * BLOCK_SIZE
        pygame.draw.rect(surface, next_piece.color, (px, py, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(surface, (40, 40, 40), (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

    # Draw play area
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)

    # Draw grid blocks
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                )
                pygame.draw.rect(
                    surface,
                    (40, 40, 40),
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1,
                )

    draw_grid_lines(surface)


def try_rotate_with_kicks(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    # Attempt rotation with simple wall kicks: [0, +1, -1, +2, -2]
    prev_rot = piece.rotation
    piece.rotation = (piece.rotation + 1) % 4

    if valid_space(piece, grid):
        return True

    kicks = [1, -1, 2, -2]
    for dx in kicks:
        old_x = piece.x
        piece.x += dx
        if valid_space(piece, grid):
            return True
        piece.x = old_x

    # Revert if no valid rotation
    piece.rotation = prev_rot
    return False


# -----------------------------
# Main Game Loop
# -----------------------------

def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    fall_time = 0
    fall_speed = 0.5  # seconds per row
    move_cooldown = 0
    move_delay = 0.08  # seconds between repeats when holding arrows
    score = 0

    while run:
        dt = clock.tick(60) / 1000.0
        fall_time += dt
        move_cooldown += dt

        # Gravity
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            grid = create_grid(locked_positions)
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    sys.exit(0)

        # Continuous key presses
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT] and move_cooldown >= move_delay:
            current_piece.x -= 1
            if not valid_space(current_piece, create_grid(locked_positions)):
                current_piece.x += 1
            else:
                moved = True
        if keys[pygame.K_RIGHT] and move_cooldown >= move_delay:
            current_piece.x += 1
            if not valid_space(current_piece, create_grid(locked_positions)):
                current_piece.x -= 1
            else:
                moved = True
        if keys[pygame.K_DOWN] and move_cooldown >= move_delay:
            current_piece.y += 1
            if not valid_space(current_piece, create_grid(locked_positions)):
                current_piece.y -= 1
            else:
                moved = True
        if keys[pygame.K_UP] and move_cooldown >= move_delay:
            if try_rotate_with_kicks(current_piece, create_grid(locked_positions)):
                moved = True
        if keys[pygame.K_SPACE] and move_cooldown >= move_delay:
            # Hard drop
            while valid_space(current_piece, create_grid(locked_positions)):
                current_piece.y += 1
            current_piece.y -= 1
            change_piece = True
            moved = True

        if moved:
            move_cooldown = 0

        grid = create_grid(locked_positions)
        for (x, y) in current_piece.get_cells():
            if y >= 0:
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    grid[y][x] = current_piece.color

        draw_window(win, grid, score, next_piece)
        pygame.display.update()

        # Piece has landed
        if change_piece:
            lock_piece(current_piece, locked_positions)
            cleared = clear_rows(grid, locked_positions)
            if cleared == 1:
                score += 100
            elif cleared == 2:
                score += 300
            elif cleared == 3:
                score += 500
            elif cleared >= 4:
                score += 800

            current_piece = next_piece
            next_piece = get_new_piece()
            change_piece = False

            # Speed up slightly over time
            fall_speed = max(0.08, fall_speed * 0.995)

            if check_lost(locked_positions):
                run = False

    # Game Over Screen
    game_over(win, score)


def game_over(surface: pygame.Surface, score: int):
    font = pygame.font.SysFont("arial", 36, bold=True)
    small = pygame.font.SysFont("arial", 22)

    surface.fill((10, 10, 10))
    text = font.render("Game Over", True, WHITE)
    score_lbl = small.render(f"Skor: {score}", True, WHITE)
    hint = small.render("Tekan Enter untuk main lagi atau Esc untuk keluar", True, WHITE)

    surface.blit(text, (PLAY_WIDTH // 2 - text.get_width() // 2, PLAY_HEIGHT // 3))
    surface.blit(score_lbl, (PLAY_WIDTH // 2 - score_lbl.get_width() // 2, PLAY_HEIGHT // 3 + 50))
    surface.blit(hint, (PLAY_WIDTH // 2 - hint.get_width() // 2, PLAY_HEIGHT // 3 + 100))
    pygame.display.update()

    waiting = True
    clock = pygame.time.Clock()
    while waiting:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
                    return
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    pygame.quit()
                    sys.exit(0)


if __name__ == "__main__":
    main()
