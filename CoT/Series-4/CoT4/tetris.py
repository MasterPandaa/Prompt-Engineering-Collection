import pygame
import random
import sys

# Game configuration
BLOCK_SIZE = 30
COLS = 10
ROWS = 20
PLAY_WIDTH = COLS * BLOCK_SIZE    # 300
PLAY_HEIGHT = ROWS * BLOCK_SIZE   # 600

# Window includes side panel for next/score
SCREEN_WIDTH = PLAY_WIDTH + 200   # 500
SCREEN_HEIGHT = PLAY_HEIGHT + 100 # 700

# Playfield top-left
TOP_LEFT_X = 20
TOP_LEFT_Y = 50

# Shapes are defined as a list of rotations, each rotation is a list of strings (5x5)
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

SHAPES = [S, Z, I, O, J, L, T]
# Colors for each shape
SHAPE_COLORS = [
    (80, 220, 100),  # S - green
    (220, 60, 70),   # Z - red
    (80, 200, 220),  # I - cyan
    (240, 230, 90),  # O - yellow
    (70, 80, 200),   # J - blue
    (240, 160, 60),  # L - orange
    (180, 80, 200),  # T - purple
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[(30, 30, 30) for _ in range(COLS)] for _ in range(ROWS)]

    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 2))

    return positions


def valid_space(piece, grid, locked):
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == (30, 30, 30)]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if y < 0:
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    for (_, y) in locked_positions.keys():
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('segoeui', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2,
                         TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(ROWS):
        pygame.draw.line(surface, (50, 50, 50), (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
        for j in range(COLS):
            pygame.draw.line(surface, (50, 50, 50), (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))


def clear_rows(grid, locked):
    # Find full rows from bottom to top
    full_rows = []
    for y in range(ROWS - 1, -1, -1):
        if (30, 30, 30) not in grid[y]:
            full_rows.append(y)

    if not full_rows:
        return 0

    # Remove blocks in cleared rows
    for y in full_rows:
        for x in range(COLS):
            locked.pop((x, y), None)

    # Move all remaining blocks down by the number of cleared rows strictly below them
    cleared_sorted = sorted(full_rows)  # ascending indices (top to bottom)
    full_rows_set = set(full_rows)
    new_locked = {}
    for (x, y), color in locked.items():
        if y in full_rows_set:
            continue
        drop = sum(1 for r in cleared_sorted if y < r)
        new_y = y + drop
        new_locked[(x, new_y)] = color

    locked.clear()
    locked.update(new_locked)
    return len(full_rows)


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('segoeui', 20)
    label = font.render('Next:', True, (230, 230, 230))

    sx = TOP_LEFT_X + PLAY_WIDTH + 20
    sy = TOP_LEFT_Y + 80
    surface.blit(label, (sx, sy - 30))

    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * 20 - 40, sy + i * 20 - 40, 20, 20), 0)


def draw_window(surface, grid, score=0):
    surface.fill((18, 18, 18))

    # Title
    font = pygame.font.SysFont('segoeui', 36, bold=True)
    label = font.render('TETRIS', True, (240, 240, 240))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2, 10))

    # Score
    font = pygame.font.SysFont('segoeui', 20)
    score_label = font.render(f'Score: {score}', True, (220, 220, 220))
    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y))

    # Playfield background
    pygame.draw.rect(surface, (25, 25, 25), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT))

    # Draw blocks
    for i in range(ROWS):
        for j in range(COLS):
            color = grid[i][j]
            if color != (30, 30, 30):
                pygame.draw.rect(surface, color,
                                 (TOP_LEFT_X + j * BLOCK_SIZE,
                                  TOP_LEFT_Y + i * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 0)

    draw_grid(surface, grid)

    pygame.draw.rect(surface, (200, 200, 200), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)


def main():
    pygame.init()
    pygame.display.set_caption('Tetris')
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.5  # seconds per fall step
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase speed over time
        if level_time / 1000 > 30:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.02

        # Piece falls automatically
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid, locked_positions) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    # rotate
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid, locked_positions):
                        # simple wall kick attempts
                        current_piece.x += 1
                        if not valid_space(current_piece, grid, locked_positions):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid, locked_positions):
                                # revert
                                current_piece.x += 1
                                current_piece.rotation = prev_rot
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_space(current_piece, grid, locked_positions):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for (x, y) in shape_pos:
            if y >= 0:
                if 0 <= x < COLS and 0 <= y < ROWS:
                    grid[y][x] = current_piece.color

        # if piece hit the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                if p[1] < 0:
                    run = False
                    break
                locked_positions[p] = current_piece.color
            # spawn next
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # clear rows
            rows_cleared = clear_rows(grid, locked_positions)
            if rows_cleared:
                score += (rows_cleared ** 2) * 100

        draw_window(window, grid, score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    # Game Over
    window.fill((18, 18, 18))
    draw_text_middle(window, 'Game Over', 40, (220, 80, 80))
    draw_text_middle(window, f'Score: {score}', 24, (230, 230, 230))
    pygame.display.update()
    pygame.time.delay(2500)
    pygame.quit()


if __name__ == '__main__':
    main()
