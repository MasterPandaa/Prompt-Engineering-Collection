import pygame
import random
import sys
from typing import Dict, List, Tuple

# Game configuration
# Grid 10x20, each block 30px, with margins for UI
BLOCK_SIZE = 30
COLS = 10
ROWS = 20
PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE
SIDEBAR_WIDTH = 200
TOP_MARGIN = 60

S_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH
S_HEIGHT = PLAY_HEIGHT + TOP_MARGIN

# Colors
BLACK = (0, 0, 0)
GRAY = (35, 35, 35)
DARK_GRAY = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (255, 85, 85)
GREEN = (100, 255, 100)
BLUE = (85, 85, 255)
YELLOW = (255, 255, 85)
CYAN = (85, 255, 255)
MAGENTA = (255, 85, 255)
ORANGE = (255, 170, 0)

# 7 Tetrominoes shapes defined as rotation states of (x,y) relative offsets around pivot (0,0)
# Rotation is clockwise by cycling the states in the list
# Each state is a list of four (x, y) tuples
# Coordinate system: x to the right, y downward
SHAPES: Dict[str, List[List[Tuple[int, int]]]] = {
    # I shape
    'I': [
        [( -1, 0), (0, 0), (1, 0), (2, 0)],  # ----
        [( 0, -1), (0, 0), (0, 1), (0, 2)],
        [( -1, 1), (0, 1), (1, 1), (2, 1)],
        [( 1, -1), (1, 0), (1, 1), (1, 2)],
    ],
    # O shape (rotation invariant)
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    # T shape
    'T': [
        [(0, 0), (-1, 0), (1, 0), (0, -1)],
        [(0, 0), (0, -1), (0, 1), (1, 0)],
        [(0, 0), (-1, 0), (1, 0), (0, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, 0)],
    ],
    # S shape
    'S': [
        [(0, 0), (1, 0), (0, -1), (-1, -1)],
        [(0, 0), (0, -1), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (-1, 1)],
        [(0, 0), (0, -1), (-1, 0), (-1, 1)],
    ],
    # Z shape
    'Z': [
        [(0, 0), (-1, 0), (0, -1), (1, -1)],
        [(0, 0), (0, -1), (-1, 0), (-1, 1)],
        [(0, 0), (-1, 0), (0, 1), (1, 1)],
        [(0, 0), (0, -1), (1, 0), (1, 1)],
    ],
    # J shape
    'J': [
        [(0, 0), (-1, 0), (1, 0), (-1, -1)],
        [(0, 0), (0, -1), (0, 1), (1, -1)],
        [(0, 0), (-1, 0), (1, 0), (1, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, 1)],
    ],
    # L shape
    'L': [
        [(0, 0), (-1, 0), (1, 0), (1, -1)],
        [(0, 0), (0, -1), (0, 1), (1, 1)],
        [(0, 0), (-1, 0), (1, 0), (-1, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, -1)],
    ],
}

SHAPE_COLORS: Dict[str, Tuple[int, int, int]] = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE,
}

class Piece:
    def __init__(self, x: int, y: int, shape_key: str):
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.rotation = 0
        self.color = SHAPE_COLORS[shape_key]

    @property
    def shape(self) -> List[Tuple[int, int]]:
        return SHAPES[self.shape_key][self.rotation % 4]


def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    positions = []
    for dx, dy in piece.shape:
        positions.append((piece.x + dx, piece.y + dy))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = {(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == BLACK}
    formatted = convert_shape_format(piece)
    for (x, y) in formatted:
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    for (x, y) in locked_positions.keys():
        if y < 0:
            return True
    return False


def get_bag_sequence() -> List[str]:
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag


class PieceQueue:
    def __init__(self):
        self.queue: List[str] = []
        self.refill()

    def refill(self):
        while len(self.queue) < 7:
            self.queue.extend(get_bag_sequence())

    def next(self) -> str:
        self.refill()
        return self.queue.pop(0)

    def peek(self, n=3) -> List[str]:
        self.refill()
        return self.queue[:n]


def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            # remove locked positions in this row
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # shift rows above down by one
            for key in sorted(list(locked.keys()), key=lambda k: k[1]):
                x, ky = key
                if ky < y:
                    locked[(x, ky + 1)] = locked.pop((x, ky))
    return cleared


def draw_grid(surface):
    # Playfield origin
    px = 0
    py = TOP_MARGIN
    # Grid lines
    for y in range(ROWS + 1):
        pygame.draw.line(surface, DARK_GRAY, (px, py + y * BLOCK_SIZE), (px + PLAY_WIDTH, py + y * BLOCK_SIZE))
    for x in range(COLS + 1):
        pygame.draw.line(surface, DARK_GRAY, (px + x * BLOCK_SIZE, py), (px + x * BLOCK_SIZE, py + PLAY_HEIGHT))


def draw_window(surface, grid, score, level, next_shapes):
    surface.fill(GRAY)
    title_font = pygame.font.SysFont('arial', 32, bold=True)
    label = title_font.render('TETRIS', True, WHITE)
    surface.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, 10))

    # Draw play area background
    pygame.draw.rect(surface, (15, 15, 15), (0, TOP_MARGIN, PLAY_WIDTH, PLAY_HEIGHT))

    # Draw grid blocks
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (x * BLOCK_SIZE, TOP_MARGIN + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    border_radius=4,
                )

    # Sidebar
    sidebar_x = PLAY_WIDTH + 10
    font = pygame.font.SysFont('consolas', 20)

    score_label = font.render(f'Score: {score}', True, WHITE)
    level_label = font.render(f'Level: {level}', True, WHITE)
    surface.blit(score_label, (sidebar_x, TOP_MARGIN))
    surface.blit(level_label, (sidebar_x, TOP_MARGIN + 28))

    # Next preview
    next_label = font.render('Next:', True, WHITE)
    surface.blit(next_label, (sidebar_x, TOP_MARGIN + 70))
    preview_y = TOP_MARGIN + 100
    for i, key in enumerate(next_shapes):
        draw_mini_shape(surface, key, sidebar_x + 10, preview_y + i * 70)

    # Border around play area
    pygame.draw.rect(surface, WHITE, (0, TOP_MARGIN, PLAY_WIDTH, PLAY_HEIGHT), 2)

    draw_grid(surface)


def draw_mini_shape(surface, shape_key: str, x: int, y: int):
    # Draw shape centered in a 4x4 area
    color = SHAPE_COLORS[shape_key]
    unit = BLOCK_SIZE // 2
    # Take rotation 0 for preview
    cells = SHAPES[shape_key][0]
    # Normalize to min x,y to visualize nicely
    min_x = min(c[0] for c in cells)
    min_y = min(c[1] for c in cells)
    norm = [(cx - min_x, cy - min_y) for (cx, cy) in cells]
    for (cx, cy) in norm:
        pygame.draw.rect(
            surface,
            color,
            (x + cx * unit, y + cy * unit, unit - 2, unit - 2),
            border_radius=3,
        )


def hard_drop(piece: Piece, grid):
    # Move piece down until collision
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def lock_piece(piece: Piece, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    for x, y in convert_shape_format(piece):
        if 0 <= y < ROWS:
            locked[(x, y)] = piece.color
        else:
            # If locking above top, still store to trigger game over check
            locked[(x, y)] = piece.color


def main():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    clock = pygame.time.Clock()

    fall_time = 0
    fall_speed = 0.5  # seconds per row at level 1
    level = 1
    score = 0

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    queue = PieceQueue()
    current_piece = Piece(COLS // 2, -1, queue.next())
    next_piece_key = queue.next()

    running = True
    fast_drop = False

    while running:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Dynamic speed based on level
        current_fall_speed = max(0.05, fall_speed - (level - 1) * 0.04)

        # Handle falling
        if fall_time >= current_fall_speed or fast_drop:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                # lock and spawn next
                lock_piece(current_piece, locked_positions)
                lines = clear_rows(grid, locked_positions)
                if lines > 0:
                    # Basic scoring: 100, 300, 500, 800 per 1-4 lines; multiply by level
                    line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
                    score += line_scores.get(lines, 0) * level
                    # Increase level every 10 lines cleared total? Here: per score threshold
                    level = 1 + score // 1500
                current_piece = Piece(COLS // 2, -1, next_piece_key)
                next_piece_key = queue.next()
                fast_drop = False
                if check_lost(locked_positions):
                    running = False

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    # soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    # rotate clockwise
                    old_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % 4
                    # basic wall kick attempts: try shift -1, +1 if collision
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 2
                            if not valid_space(current_piece, grid):
                                current_piece.x -= 1
                                current_piece.rotation = old_rot
                elif event.key == pygame.K_z:
                    # rotate counter-clockwise
                    old_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation - 1) % 4
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 2
                            if not valid_space(current_piece, grid):
                                current_piece.x -= 1
                                current_piece.rotation = old_rot
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    hard_drop(current_piece, grid)
                    # lock immediately
                    lock_piece(current_piece, locked_positions)
                    lines = clear_rows(grid, locked_positions)
                    if lines > 0:
                        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
                        score += line_scores.get(lines, 0) * level
                        level = 1 + score // 1500
                    current_piece = Piece(COLS // 2, -1, next_piece_key)
                    next_piece_key = queue.next()
                    fast_drop = False
                    if check_lost(locked_positions):
                        running = False
                elif event.key == pygame.K_c:
                    # toggle fast drop (gravity accelerated)
                    fast_drop = not fast_drop

        # Render current piece onto grid for drawing
        for x, y in convert_shape_format(current_piece):
            if 0 <= y < ROWS and 0 <= x < COLS:
                grid[y][x] = current_piece.color

        draw_window(win, grid, score, level, queue.peek(3))
        pygame.display.update()

    # Game over screen
    game_over(win, score)


def game_over(surface, score):
    font_big = pygame.font.SysFont('arial', 48, bold=True)
    font_small = pygame.font.SysFont('arial', 24)

    overlay = pygame.Surface((S_WIDTH, S_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    text1 = font_big.render('GAME OVER', True, WHITE)
    text2 = font_small.render(f'Score: {score}', True, WHITE)
    text3 = font_small.render('Press R to Restart or ESC to Quit', True, WHITE)

    surface.blit(overlay, (0, 0))
    surface.blit(text1, (S_WIDTH // 2 - text1.get_width() // 2, S_HEIGHT // 2 - 80))
    surface.blit(text2, (S_WIDTH // 2 - text2.get_width() // 2, S_HEIGHT // 2 - 30))
    surface.blit(text3, (S_WIDTH // 2 - text3.get_width() // 2, S_HEIGHT // 2 + 10))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    main()
                    return


if __name__ == '__main__':
    main()
