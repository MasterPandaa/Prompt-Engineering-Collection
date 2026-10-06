import pygame
import random
import sys
from typing import Dict, List, Tuple

# Game configuration
s_width = 600
s_height = 700
play_width = 300   # 10 blocks wide
play_height = 600  # 20 blocks tall
block_size = 30

# Top-left position of the play field
play_x = (s_width - play_width) // 2
play_y = s_height - play_height - 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Tetromino colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Shapes represented as rotations of relative offsets around a pivot (0,0)
# Each shape is a list of rotations; each rotation is a list of (x, y) offsets
# Coordinate system: x increases to right, y increases downward

# I shape (cyan): pivot near second block
I_SHAPE = [
    [(-1, 0), (0, 0), (1, 0), (2, 0)],  # Horizontal
    [(1, -1), (1, 0), (1, 1), (1, 2)],  # Vertical
]

# O shape (yellow): 2x2 square, rotations identical
O_SHAPE = [
    [(0, 0), (1, 0), (0, 1), (1, 1)],
]

# T shape (purple/magenta)
T_SHAPE = [
    [(-1, 0), (0, 0), (1, 0), (0, -1)],  # Up
    [(0, -1), (0, 0), (0, 1), (1, 0)],   # Right
    [(-1, 0), (0, 0), (1, 0), (0, 1)],   # Down
    [(0, -1), (0, 0), (0, 1), (-1, 0)],  # Left
]

# S shape (green)
S_SHAPE = [
    [(-1, 0), (0, 0), (0, -1), (1, -1)],  # Horizontal
    [(0, -1), (0, 0), (1, 0), (1, 1)],    # Vertical
]

# Z shape (red)
Z_SHAPE = [
    [(-1, -1), (0, -1), (0, 0), (1, 0)],  # Horizontal
    [(1, -1), (1, 0), (0, 0), (0, 1)],    # Vertical
]

# J shape (blue)
J_SHAPE = [
    [(-1, -1), (-1, 0), (0, 0), (1, 0)],   # Up
    [(0, -1), (1, -1), (0, 0), (0, 1)],    # Right
    [(-1, 0), (0, 0), (1, 0), (1, 1)],     # Down
    [(0, -1), (0, 0), (-1, 1), (0, 1)],    # Left
]

# L shape (orange)
L_SHAPE = [
    [(1, -1), (-1, 0), (0, 0), (1, 0)],    # Up
    [(0, -1), (0, 0), (0, 1), (1, 1)],     # Right
    [(-1, 0), (0, 0), (1, 0), (-1, 1)],    # Down
    [(-1, -1), (0, -1), (0, 0), (0, 1)],   # Left
]

SHAPES = [I_SHAPE, O_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, J_SHAPE, L_SHAPE]
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[Tuple[int, int]]], color: Tuple[int, int, int]):
        # Position is pivot position in grid coordinates
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # index of current rotation

    def current_cells(self) -> List[Tuple[int, int]]:
        # Return absolute positions of blocks of current rotation
        rotation = self.shape[self.rotation % len(self.shape)]
        return [(self.x + dx, self.y + dy) for (dx, dy) in rotation]

    def rotate(self, grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
        # Try rotate with simple wall kicks: attempt center, then offsets
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(self.shape)
        if not valid_space(self, grid):
            # Simple kicks
            for kick in [(-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]:
                self.x += kick[0]
                self.y += kick[1]
                if valid_space(self, grid):
                    return
                self.x -= kick[0]
                self.y -= kick[1]
            self.rotation = old_rotation


def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(10)] for _ in range(20)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < 20 and 0 <= x < 10:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    return piece.current_cells()


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = [(j, i) for i in range(20) for j in range(10) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        # Enforce horizontal bounds always
        if x < 0 or x >= 10:
            return False
        # Allow blocks above the visible top (y < 0)
        if y < 0:
            continue
        # Enforce bottom bound
        if y >= 20:
            return False
        # Check occupancy only for visible cells
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    for (x, y) in locked_positions.keys():
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    index = random.randrange(0, len(SHAPES))
    shape = SHAPES[index]
    color = SHAPE_COLORS[index]
    # Spawn near top center; y = 1 to allow S/Z spawn
    return Piece(5, 1, shape, color)


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (
            play_x + play_width / 2 - label.get_width() / 2,
            play_y + play_height / 2 - label.get_height() / 2,
        ),
    )


def draw_grid(surface, grid):
    # Draw grid lines
    sx = play_x
    sy = play_y
    for i in range(len(grid)):
        pygame.draw.line(
            surface, GREY, (sx, sy + i * block_size), (sx + play_width, sy + i * block_size)
        )
        for j in range(len(grid[i])):
            pygame.draw.line(
                surface, GREY, (sx + j * block_size, sy), (sx + j * block_size, sy + play_height)
            )


def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Returns number of cleared rows
    rows_to_clear = []
    for i in range(len(grid) - 1, -1, -1):
        if BLACK not in grid[i]:
            rows_to_clear.append(i)
    if not rows_to_clear:
        return 0

    for row in rows_to_clear:
        # Remove locked positions in the cleared row
        for j in range(10):
            try:
                del locked[(j, row)]
            except KeyError:
                continue
        # Move every locked cell above this row down by 1
        new_locked = {}
        for (x, y), color in locked.items():
            if y < row:
                new_locked[(x, y + 1)] = color
            else:
                new_locked[(x, y)] = color
        locked.clear()
        locked.update(new_locked)
        # After shifting once, continue to next row index (note: indices in rows_to_clear are original)

    return len(rows_to_clear)


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont("comicsans", 24)
    label = font.render("Next:", True, WHITE)

    sx = play_x + play_width + 30
    sy = play_y + 60

    shape_cells = piece.shape[0]
    # Determine bounding box to center preview
    min_x = min([x for x, _ in shape_cells])
    max_x = max([x for x, _ in shape_cells])
    min_y = min([y for _, y in shape_cells])
    max_y = max([y for _, y in shape_cells])
    width = (max_x - min_x + 1) * block_size
    height = (max_y - min_y + 1) * block_size

    surface.blit(label, (sx, sy - 30))
    preview_rect = pygame.Rect(sx, sy, width + 20, height + 20)
    pygame.draw.rect(surface, GREY, preview_rect, width=2)

    for (dx, dy) in shape_cells:
        x = sx + 10 + (dx - min_x) * block_size
        y = sy + 10 + (dy - min_y) * block_size
        pygame.draw.rect(surface, piece.color, (x, y, block_size, block_size), border_radius=5)
        pygame.draw.rect(surface, BLACK, (x, y, block_size, block_size), 2, border_radius=5)


def draw_window(surface, grid, score=0, lines=0, level=1):
    surface.fill((20, 20, 30))

    # Title
    font = pygame.font.SysFont("comicsans", 48, bold=True)
    label = font.render("TETRIS", True, WHITE)

    surface.blit(label, (play_x + play_width / 2 - label.get_width() / 2, 10))

    # Score and info
    info_font = pygame.font.SysFont("comicsans", 24)
    score_label = info_font.render(f"Score: {score}", True, WHITE)
    lines_label = info_font.render(f"Lines: {lines}", True, WHITE)
    level_label = info_font.render(f"Level: {level}", True, WHITE)
    surface.blit(score_label, (play_x - 180, play_y + 60))
    surface.blit(lines_label, (play_x - 180, play_y + 90))
    surface.blit(level_label, (play_x - 180, play_y + 120))

    # Draw play area border
    pygame.draw.rect(surface, WHITE, (play_x, play_y, play_width, play_height), width=4)

    # Draw grid cells
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != BLACK:
                x = play_x + j * block_size
                y = play_y + i * block_size
                pygame.draw.rect(surface, color, (x, y, block_size, block_size), border_radius=5)
                pygame.draw.rect(surface, BLACK, (x, y, block_size, block_size), 2, border_radius=5)

    draw_grid(surface, grid)


def hard_drop(piece: Piece, grid, locked):
    # Drop until collision
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def main(surface):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()

    fall_time = 0
    fall_speed = 0.5  # seconds per fall step
    level = 1
    score = 0
    lines_cleared_total = 0

    move_delay = 0  # for soft drop repeat

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0  # seconds
        fall_time += dt
        move_delay += dt

        # Increase speed each 10 lines
        level = max(1, 1 + lines_cleared_total // 10)
        fall_speed = max(0.08, 0.5 - (level - 1) * 0.04)

        # Piece falling
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
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
                elif event.key == pygame.K_UP:
                    current_piece.rotate(grid, locked_positions)
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid, locked_positions)
                    change_piece = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

        # Update grid with current piece
        for (x, y) in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color

        draw_window(surface, grid, score=score, lines=lines_cleared_total, level=level)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

        # Lock piece if landed
        if change_piece:
            change_piece = False
            for (x, y) in convert_shape_format(current_piece):
                locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()

            # Clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                lines_cleared_total += cleared
                # Scoring (simple): 1->100, 2->300, 3->500, 4->800 then * level
                score_table = {1: 100, 2: 300, 3: 500, 4: 800}
                score += score_table.get(cleared, cleared * 200) * level

            # Check loss
            if check_lost(locked_positions):
                draw_text_middle(surface, "Game Over", 64, WHITE)
                pygame.display.update()
                pygame.time.delay(1500)
                run = False


def main_menu(surface):
    run = True
    while run:
        surface.fill((20, 20, 30))
        draw_text_middle(surface, "Press Any Key to Play", 36, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                main(surface)
                run = False


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    win = pygame.display.set_mode((s_width, s_height))
    main_menu(win)
