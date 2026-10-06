import pygame
import random
import sys

# Game configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 10 columns * 30px
PLAY_HEIGHT = 600  # 20 rows * 30px
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Grid size
COLS = 10
ROWS = 20

# Tetromino definitions using relative coordinates per rotation (around pivot at (0,0))
# For each shape, provide rotations [0, 90, 180, 270]
# Coordinates are tuples (dx, dy) where y increases downward

# I shape: ----
I_ROT = [
    [( -2, 0), (-1, 0), (0, 0), (1, 0)],   # 0 degrees (horizontal)
    [( 0, -2), (0, -1), (0, 0), (0, 1)],   # 90 degrees (vertical)
    [( -2, 0), (-1, 0), (0, 0), (1, 0)],   # 180
    [( 0, -2), (0, -1), (0, 0), (0, 1)],   # 270
]

# O shape: square
O_ROT = [
    [ (0, 0), (1, 0), (0, -1), (1, -1)],
    [ (0, 0), (1, 0), (0, -1), (1, -1)],
    [ (0, 0), (1, 0), (0, -1), (1, -1)],
    [ (0, 0), (1, 0), (0, -1), (1, -1)],
]

# T shape
T_ROT = [
    [(0, 0), (-1, 0), (1, 0), (0, -1)],     # ⊥
    [(0, 0), (0, -1), (0, 1), (1, 0)],      # ⟂ right
    [(0, 0), (-1, 0), (1, 0), (0, 1)],      # T upside down
    [(0, 0), (0, -1), (0, 1), (-1, 0)],     # ⟂ left
]

# S shape
S_ROT = [
    [(0, 0), (1, 0), (0, -1), (-1, -1)],    # horizontal
    [(0, 0), (0, -1), (1, 0), (1, 1)],      # vertical
    [(0, 0), (1, 0), (0, -1), (-1, -1)],
    [(0, 0), (0, -1), (1, 0), (1, 1)],
]

# Z shape
Z_ROT = [
    [(0, 0), (-1, 0), (0, -1), (1, -1)],    # horizontal
    [(0, 0), (0, -1), (-1, 0), (-1, 1)],    # vertical
    [(0, 0), (-1, 0), (0, -1), (1, -1)],
    [(0, 0), (0, -1), (-1, 0), (-1, 1)],
]

# J shape
J_ROT = [
    [(0, 0), (-1, 0), (1, 0), (-1, -1)],    # └─
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (-1, 0), (1, 0), (1, 1)],
    [(0, 0), (0, -1), (0, 1), (-1, 1)],
]

# L shape
L_ROT = [
    [(0, 0), (-1, 0), (1, 0), (1, -1)],     # ┘
    [(0, 0), (0, -1), (0, 1), (1, 1)],
    [(0, 0), (-1, 0), (1, 0), (-1, 1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
]

SHAPES = [I_ROT, O_ROT, T_ROT, S_ROT, Z_ROT, J_ROT, L_ROT]
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

class Piece:
    def __init__(self, x, y, shape_index):
        self.x = x  # grid x
        self.y = y  # grid y
        self.shape_index = shape_index
        self.rotation = 0  # 0..3
        self.color = SHAPE_COLORS[shape_index]

    @property
    def blocks(self):
        # Return absolute grid coordinates of blocks for current rotation
        rot = SHAPES[self.shape_index][self.rotation % 4]
        return [(self.x + dx, self.y + dy) for (dx, dy) in rot]

    def rotated(self, dir=1):
        # dir=1 clockwise, -1 counter-clockwise
        p = Piece(self.x, self.y, self.shape_index)
        p.rotation = (self.rotation + dir) % 4
        return p


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def valid_space(piece, grid):
    for (x, y) in piece.blocks:
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True


def check_lost(locked_positions):
    for (x, y) in locked_positions:
        if y < 0:
            return True
    return False


def get_shape():
    idx = random.randrange(len(SHAPES))
    # spawn near top; y starts negative to allow entry
    return Piece(COLS // 2, -1, idx)


def clear_rows(grid, locked):
    # Return number of cleared lines
    rows_to_clear = []
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            rows_to_clear.append(y)
    if not rows_to_clear:
        return 0

    # Remove from locked and move rows down
    for y in rows_to_clear:
        for x in range(COLS):
            if (x, y) in locked:
                del locked[(x, y)]
    # Shift down
    rows_to_clear.sort()
    for (x, y) in sorted(list(locked.keys()), key=lambda t: t[1]):
        shift = sum(1 for ry in rows_to_clear if y < ry)
        if shift > 0:
            color = locked.pop((x, y))
            locked[(x, y + shift)] = color
    return len(rows_to_clear)


def draw_grid(surface, grid):
    # fill background playfield
    pygame.draw.rect(surface, DARK_GRAY, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT))

    # draw locked and current grid
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            rect = (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, color, rect)
            # grid lines
            pygame.draw.rect(surface, GRAY, rect, 1)

    # border
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2,
                         TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))


def draw_next_shape(surface, piece):
    font = pygame.font.SysFont('arial', 24)
    label = font.render('Next:', True, WHITE)

    sx = TOP_LEFT_X + PLAY_WIDTH + 40
    sy = TOP_LEFT_Y + 60
    surface.blit(label, (sx, sy - 40))

    for (dx, dy) in SHAPES[piece.shape_index][piece.rotation % 4]:
        x = sx + (dx + 2) * BLOCK_SIZE
        y = sy + (dy + 2) * BLOCK_SIZE
        pygame.draw.rect(surface, piece.color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(surface, GRAY, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_score(surface, score):
    font = pygame.font.SysFont('arial', 24)
    label = font.render(f'Score: {score}', True, WHITE)
    sx = TOP_LEFT_X - 180
    sy = TOP_LEFT_Y + 60
    surface.blit(label, (sx, sy))


def try_kick(piece, grid, dir):
    # Simple wall kicks: try shifting left/right/up to make rotation fit
    candidates = [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0), (0, -1)]
    rotated = piece.rotated(dir)
    for (kx, ky) in candidates:
        test = Piece(rotated.x + kx, rotated.y + ky, rotated.shape_index)
        test.rotation = rotated.rotation
        if valid_space(test, grid):
            return test
    return None


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # seconds per cell at start
    level_lines = 0
    score = 0

    move_down_pressed = False

    while run:
        dt = clock.tick(60) / 1000.0
        fall_time += dt
        grid = create_grid(locked_positions)

        # Increase speed with lines cleared
        speed_cap = 0.08
        fall_speed = max(0.5 - (level_lines // 10) * 0.05, speed_cap)

        # piece falling
        if fall_time >= fall_speed or move_down_pressed:
            fall_time = 0
            test_piece = Piece(current_piece.x, current_piece.y + 1, current_piece.shape_index)
            test_piece.rotation = current_piece.rotation
            if valid_space(test_piece, grid):
                current_piece = test_piece
            else:
                # lock piece
                for (x, y) in current_piece.blocks:
                    locked_positions[(x, y)] = current_piece.color
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    test_piece = Piece(current_piece.x - 1, current_piece.y, current_piece.shape_index)
                    test_piece.rotation = current_piece.rotation
                    if valid_space(test_piece, grid):
                        current_piece = test_piece
                elif event.key == pygame.K_RIGHT:
                    test_piece = Piece(current_piece.x + 1, current_piece.y, current_piece.shape_index)
                    test_piece.rotation = current_piece.rotation
                    if valid_space(test_piece, grid):
                        current_piece = test_piece
                elif event.key == pygame.K_DOWN:
                    move_down_pressed = True
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    kicked = try_kick(current_piece, grid, dir=1)
                    if kicked:
                        current_piece = kicked
                elif event.key == pygame.K_z:
                    kicked = try_kick(current_piece, grid, dir=-1)
                    if kicked:
                        current_piece = kicked
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while True:
                        test_piece = Piece(current_piece.x, current_piece.y + 1, current_piece.shape_index)
                        test_piece.rotation = current_piece.rotation
                        if valid_space(test_piece, grid):
                            current_piece = test_piece
                        else:
                            break
                    # lock immediately
                    for (x, y) in current_piece.blocks:
                        locked_positions[(x, y)] = current_piece.color
                    change_piece = True
                elif event.key == pygame.K_p:
                    # pause
                    paused = True
                    font = pygame.font.SysFont('arial', 36, bold=True)
                    pause_label = font.render('PAUSED - Press P to Resume', True, WHITE)
                    while paused:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit(0)
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                                paused = False
                        win.fill(BLACK)
                        draw_grid(win, grid)
                        win.blit(pause_label, (SCREEN_WIDTH/2 - pause_label.get_width()/2, 30))
                        pygame.display.update()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    move_down_pressed = False

        shape_pos = current_piece.blocks
        for (x, y) in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        # Draw
        win.fill(BLACK)
        draw_grid(win, grid)
        draw_next_shape(win, next_piece)
        draw_score(win, score)
        title_font = pygame.font.SysFont('arial', 36, bold=True)
        title_label = title_font.render('TETRIS', True, WHITE)
        win.blit(title_label, (SCREEN_WIDTH/2 - title_label.get_width()/2, 20))
        pygame.display.update()

        # If piece locked, generate new and clear rows
        if change_piece:
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                level_lines += cleared
                score += (cleared ** 2) * 100
            current_piece = next_piece
            next_piece = get_shape()
            # If new piece overlaps locked (y < 0 after locking), game over
            if not valid_space(current_piece, grid):
                run = False

    # Game over screen
    win.fill(BLACK)
    draw_grid(win, grid)
    draw_text_middle(win, 'GAME OVER', 48, WHITE)
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    run = True
    while run:
        win.fill(BLACK)
        draw_text_middle(win, 'Press Any Key To Play', 40, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


if __name__ == '__main__':
    main_menu()
