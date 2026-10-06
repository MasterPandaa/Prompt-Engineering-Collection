import pygame
import random
import sys
from typing import Dict, List, Tuple

# ============================
# Game Constants
# ============================
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
PLAY_WIDTH = GRID_WIDTH * CELL_SIZE
PLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE

SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

TOP_LEFT_X = 20
TOP_LEFT_Y = 20
PLAY_TOP_LEFT_X = TOP_LEFT_X
PLAY_TOP_LEFT_Y = TOP_LEFT_Y

FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
LIGHT_GRAY = (80, 80, 80)

# Tetromino colors
COLORS = {
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Yellow
    'T': (128, 0, 128),   # Purple
    'S': (0, 255, 0),     # Green
    'Z': (255, 0, 0),     # Red
    'J': (0, 0, 255),     # Blue
    'L': (255, 165, 0),   # Orange
}

# ============================
# Tetromino Definitions
# Each shape is defined as a list of (x, y) offsets relative to a pivot at (0,0)
# Rotation (clockwise) will apply: (x, y) -> (y, -x)
# ============================
T_SHAPE = [(0, 0), (-1, 0), (1, 0), (0, -1)]
L_SHAPE = [(0, 0), (-1, 0), (1, 0), (1, -1)]
J_SHAPE = [(0, 0), (-1, -1), (-1, 0), (1, 0)]
S_SHAPE = [(0, 0), (1, 0), (0, -1), (-1, -1)]
Z_SHAPE = [(0, 0), (-1, 0), (0, -1), (1, -1)]
I_SHAPE = [(0, 0), (-1, 0), (1, 0), (2, 0)]  # pivot on second block from left
O_SHAPE = [(0, 0), (1, 0), (0, -1), (1, -1)]

SHAPES: Dict[str, List[Tuple[int, int]]] = {
    'I': I_SHAPE,
    'O': O_SHAPE,
    'T': T_SHAPE,
    'S': S_SHAPE,
    'Z': Z_SHAPE,
    'J': J_SHAPE,
    'L': L_SHAPE,
}

# ============================
# Helper Data Structures
# ============================
class Piece:
    def __init__(self, shape_key: str, grid_x: int, grid_y: int):
        self.shape_key = shape_key
        self.cells = SHAPES[shape_key][:]  # list of relative (x,y)
        self.color = COLORS[shape_key]
        self.x = grid_x  # pivot grid x
        self.y = grid_y  # pivot grid y
        self.rotation = 0  # 0..3

    def rotated_cells(self, rotation: int = None) -> List[Tuple[int, int]]:
        # Return rotated cells with rotation count (clockwise 90 deg per step)
        if rotation is None:
            rotation = self.rotation
        cells = self.cells
        for _ in range(rotation % 4):
            # rotate clockwise: (x, y) -> (y, -x)
            cells = [(y, -x) for (x, y) in cells]
        # O piece does not effectively rotate (but above also maintains square)
        if self.shape_key == 'O':
            return O_SHAPE[:]
        return cells

    def absolute_positions(self, rotation: int = None, dx: int = 0, dy: int = 0) -> List[Tuple[int, int]]:
        cells = self.rotated_cells(rotation)
        return [(self.x + dx + cx, self.y + dy + cy) for (cx, cy) in cells]


def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def valid_space(grid: List[List[Tuple[int, int, int]]], positions: List[Tuple[int, int]]) -> bool:
    for (x, y) in positions:
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0:
            if grid[y][x] != BLACK:
                return False
    return True


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    # If any locked block is above the visible grid (y < 0) or at y==0 covered on spawn area
    for (_, y) in locked_positions.keys():
        if y < 0:
            return True
    return False


def get_shape() -> Piece:
    key = random.choice(list(SHAPES.keys()))
    # start near the middle top; pivot y at 1 to allow some negative cell offsets
    start_x = GRID_WIDTH // 2
    start_y = 1
    return Piece(key, start_x, start_y)


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Remove full rows and shift everything above down
    lines_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[y]:
            lines_cleared += 1
            # remove all locked positions in this row
            for x in range(GRID_WIDTH):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # shift down rows above
            keys = sorted(list(locked.keys()), key=lambda k: k[1])
            for xk, yk in keys[::-1]:
                if yk < y:
                    color = locked[(xk, yk)]
                    del locked[(xk, yk)]
                    locked[(xk, yk + 1)] = color
    return lines_cleared


# ============================
# Rendering
# ============================

def draw_grid_lines(surface):
    # Draw the grid lines on playfield
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, LIGHT_GRAY,
                         (PLAY_TOP_LEFT_X, PLAY_TOP_LEFT_Y + y * CELL_SIZE),
                         (PLAY_TOP_LEFT_X + PLAY_WIDTH, PLAY_TOP_LEFT_Y + y * CELL_SIZE), 1)
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, LIGHT_GRAY,
                         (PLAY_TOP_LEFT_X + x * CELL_SIZE, PLAY_TOP_LEFT_Y),
                         (PLAY_TOP_LEFT_X + x * CELL_SIZE, PLAY_TOP_LEFT_Y + PLAY_HEIGHT), 1)


def draw_window(surface, grid, score, level, next_piece: Piece, paused: bool, game_over: bool, font, small_font):
    surface.fill(GRAY)

    # Title
    title_text = font.render('TETRIS', True, WHITE)
    surface.blit(title_text, (TOP_LEFT_X, 0))

    # Draw playfield background
    pygame.draw.rect(surface, (20, 20, 20), (PLAY_TOP_LEFT_X, PLAY_TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT))

    # Draw cells
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(surface, color, (
                    PLAY_TOP_LEFT_X + x * CELL_SIZE + 1,
                    PLAY_TOP_LEFT_Y + y * CELL_SIZE + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2
                ))

    draw_grid_lines(surface)

    # Side panel
    side_x = PLAY_TOP_LEFT_X + PLAY_WIDTH + 20
    side_y = PLAY_TOP_LEFT_Y

    score_text = small_font.render(f'Score: {score}', True, WHITE)
    level_text = small_font.render(f'Level: {level}', True, WHITE)
    surface.blit(score_text, (side_x, side_y))
    surface.blit(level_text, (side_x, side_y + 30))

    # Next piece
    next_text = small_font.render('Next:', True, WHITE)
    surface.blit(next_text, (side_x, side_y + 80))

    # Draw next piece at side panel
    if next_piece:
        cells = next_piece.rotated_cells(0)
        # Center in a 4x4 preview box
        preview_origin_x = side_x + 60
        preview_origin_y = side_y + 130
        for (cx, cy) in cells:
            px = preview_origin_x + (cx) * CELL_SIZE
            py = preview_origin_y + (cy) * CELL_SIZE
            pygame.draw.rect(surface, next_piece.color, (px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2))
        # Box
        pygame.draw.rect(surface, LIGHT_GRAY, (side_x + 10, side_y + 100, 150, 150), 2)

    if paused and not game_over:
        ptext = font.render('PAUSED', True, WHITE)
        surface.blit(ptext, (PLAY_TOP_LEFT_X + PLAY_WIDTH // 2 - ptext.get_width() // 2,
                             PLAY_TOP_LEFT_Y + PLAY_HEIGHT // 2 - ptext.get_height() // 2))

    if game_over:
        gtext = font.render('GAME OVER', True, WHITE)
        rtext = small_font.render('Press R to Restart', True, WHITE)
        surface.blit(gtext, (PLAY_TOP_LEFT_X + PLAY_WIDTH // 2 - gtext.get_width() // 2,
                             PLAY_TOP_LEFT_Y + PLAY_HEIGHT // 2 - gtext.get_height() // 2 - 20))
        surface.blit(rtext, (PLAY_TOP_LEFT_X + PLAY_WIDTH // 2 - rtext.get_width() // 2,
                             PLAY_TOP_LEFT_Y + PLAY_HEIGHT // 2 - rtext.get_height() // 2 + 30))


# ============================
# Game Logic
# ============================

def attempt_move(grid, piece: Piece, dx: int, dy: int) -> bool:
    new_positions = piece.absolute_positions(dx=dx, dy=dy)
    if valid_space(grid, new_positions):
        piece.x += dx
        piece.y += dy
        return True
    return False


def attempt_rotate(grid, piece: Piece, clockwise: bool = True) -> bool:
    new_rotation = (piece.rotation + (1 if clockwise else -1)) % 4
    # Wall-kick attempts: try offsets in x from -2..2
    for kick_x in [0, -1, 1, -2, 2]:
        new_positions = piece.absolute_positions(rotation=new_rotation, dx=kick_x, dy=0)
        if valid_space(grid, new_positions):
            piece.rotation = new_rotation
            piece.x += kick_x
            return True
    return False


def hard_drop(grid, piece: Piece) -> int:
    # Return drop distance
    distance = 0
    while True:
        new_positions = piece.absolute_positions(dy=distance + 1)
        if valid_space(grid, new_positions):
            distance += 1
        else:
            break
    piece.y += distance
    return distance


def lock_piece(piece: Piece, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    for (x, y) in piece.absolute_positions():
        locked[(x, y)] = piece.color


# ============================
# Main Game Loop
# ============================

def main():
    pygame.init()
    pygame.display.set_caption('Tetris (Pygame)')
    screen = pygame.display.set_mode((WINDOW_WIDTH + TOP_LEFT_X * 2, WINDOW_HEIGHT + TOP_LEFT_Y))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('arial', 36, bold=True)
    small_font = pygame.font.SysFont('arial', 22)

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    current_piece = get_shape()
    next_piece = get_shape()

    fall_time = 0
    fall_speed = 0.6  # seconds per row drop, will decrease with level
    score = 0
    level = 1
    lines_cleared_total = 0
    paused = False
    game_over = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over:
                    if event.key == pygame.K_r:
                        # restart
                        locked_positions.clear()
                        grid = create_grid(locked_positions)
                        current_piece = get_shape()
                        next_piece = get_shape()
                        fall_time = 0
                        fall_speed = 0.6
                        score = 0
                        level = 1
                        lines_cleared_total = 0
                        paused = False
                        game_over = False
                    continue
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    attempt_move(grid, current_piece, -1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    attempt_move(grid, current_piece, 1, 0)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    attempt_move(grid, current_piece, 0, 1)
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_k):
                    attempt_rotate(grid, current_piece, True)
                elif event.key == pygame.K_j:
                    attempt_rotate(grid, current_piece, False)
                elif event.key == pygame.K_SPACE:
                    hard_drop(grid, current_piece)

        if not paused and not game_over:
            if fall_time >= fall_speed:
                fall_time = 0
                if not attempt_move(grid, current_piece, 0, 1):
                    # lock piece
                    lock_piece(current_piece, locked_positions)
                    # new piece
                    current_piece = next_piece
                    next_piece = get_shape()
                    # clear rows
                    grid = create_grid(locked_positions)
                    cleared = clear_rows(grid, locked_positions)
                    if cleared > 0:
                        # basic scoring system similar to classic Tetris
                        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
                        score += line_scores.get(cleared, 100 * cleared) * level
                        lines_cleared_total += cleared
                        # level up every 10 lines
                        if lines_cleared_total // 10 + 1 > level:
                            level = lines_cleared_total // 10 + 1
                            fall_speed = max(0.1, 0.6 - (level - 1) * 0.05)
                    # check game over
                    if check_lost(locked_positions):
                        game_over = True
                else:
                    # update grid with current_piece preview
                    pass

        # Draw current state
        grid = create_grid(locked_positions)
        # place current piece on the grid preview (do not lock)
        for (x, y) in current_piece.absolute_positions():
            if y >= 0:
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    grid[y][x] = current_piece.color

        draw_window(screen, grid, score, level, next_piece, paused, game_over, font, small_font)
        pygame.display.update()

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
