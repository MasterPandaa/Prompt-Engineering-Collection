import pygame
import random
import sys

# Game configuration
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Shapes (Tetriminos) represented as 5x5 grids per rotation
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

shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (80, 230, 150),  # S - greenish
    (230, 90, 90),   # Z - red
    (90, 200, 255),  # I - cyan
    (240, 240, 120), # O - yellow
    (100, 140, 230), # J - blue
    (255, 170, 70),  # L - orange
    (190, 100, 220)  # T - purple
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))

    return positions


def valid_space(piece, grid):
    accepted_positions = [(j, i) for i in range(20) for j in range(10) if grid[i][j] == (0, 0, 0)]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if x < 0 or x >= 10 or y >= 20:
            return False
        if y > -1 and (x, y) not in accepted_positions:
            return False
    return True


def check_lost(positions):
    for (x, y) in positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2,
                         top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (40, 40, 40), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (40, 40, 40), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    cleared_rows = []
    # Identify full rows and remove them from locked
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            cleared_rows.append(i)
            for j in range(len(row)):
                locked.pop((j, i), None)

    if not cleared_rows:
        return 0

    # For each remaining locked block, compute how many cleared rows are below it
    cleared_rows_set = set(cleared_rows)
    cleared_rows_sorted = sorted(cleared_rows)
    new_locked = {}
    for (x, y), color in sorted(locked.items(), key=lambda kv: kv[0][1], reverse=True):
        # Count how many cleared rows have index > y (i.e., below this block)
        shift = 0
        for r in cleared_rows_sorted:
            if r > y:
                shift += 1
        new_locked[(x, y + shift)] = color

    locked.clear()
    locked.update(new_locked)
    return len(cleared_rows)


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('arial', 24)
    label = font.render('Next', True, (255, 255, 255))

    sx = top_left_x + play_width + 30
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 10, sy - 30))

    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)
    # Outline
    outline_rect = pygame.Rect(sx, sy, 5 * block_size, 5 * block_size)
    pygame.draw.rect(surface, (200, 200, 200), outline_rect, 2)


def draw_window(surface, grid, score=0):
    surface.fill((15, 15, 20))

    # Title
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('TETRIS', True, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 20))

    # Current score
    font = pygame.font.SysFont('arial', 24)
    label = font.render(f'Score: {score}', True, (255, 255, 255))

    sx = top_left_x + play_width + 30
    sy = top_left_y + play_height / 2 - 160

    surface.blit(label, (sx, sy - 60))

    # Draw play area
    pygame.draw.rect(surface, (200, 200, 200), (top_left_x, top_left_y, play_width, play_height), 4)

    # Draw grid blocks
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != (0, 0, 0):
                pygame.draw.rect(surface, color,
                                 (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface, grid)


def hard_drop(piece, grid):
    # Move piece down until it cannot move further
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def main(surface):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # seconds per step; will adjust slightly with score
    score = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Increase speed slightly over time/score
        speed = max(0.1, fall_speed - min(0.4, score * 0.002))

        # Auto fall
        if fall_time >= speed:
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
                elif event.key == pygame.K_UP:
                    # rotate
                    prev_rotation = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # Try simple wall kicks (shift left or right by 1)
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                # revert
                                current_piece.x += 1
                                current_piece.rotation = prev_rotation
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid)
                    change_piece = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

        shape_pos = convert_shape_format(current_piece)

        # Add piece to grid for drawing
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # If piece hit the ground/locked, lock it in place
        if change_piece:
            for pos in shape_pos:
                x, y = pos
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                # Tetris scoring heuristic
                score += [0, 100, 300, 500, 800][cleared]

        draw_window(surface, grid, score)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_window(surface, grid, score)
            draw_text_middle(surface, 'GAME OVER', 48, (255, 80, 80))
            pygame.display.update()
            pygame.time.delay(1800)
            run = False


def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris - Pygame')

    run = True
    while run:
        surface.fill((15, 15, 20))
        draw_text_middle(surface, 'Tekan ENTER untuk mulai', 36, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(surface)
    pygame.quit()


if __name__ == '__main__':
    main_menu()
