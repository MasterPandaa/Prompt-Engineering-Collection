import pygame
import random
import sys

# Game configuration
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
PLAY_WIDTH = 300   # 10 columns * 30px
PLAY_HEIGHT = 600  # 20 rows * 30px
BLOCK_SIZE = 30

TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT - 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Tetromino definitions using relative coordinates from pivot (0,0)
# Shapes will be rotated by transform (x, y) -> (-y, x)
SHAPES = {
    'S': [(0, 0), (1, 0), (0, -1), (-1, -1)],
    'Z': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'I': [(0, 0), (-1, 0), (1, 0), (2, 0)],
    'O': [(0, 0), (1, 0), (0, -1), (1, -1)],
    'J': [(0, 0), (-1, 0), (1, 0), (-1, -1)],
    'L': [(0, 0), (-1, 0), (1, 0), (1, -1)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
}

# Assign distinct colors to shapes
SHAPE_COLORS = {
    'S': (80, 220, 100),
    'Z': (220, 80, 80),
    'I': (80, 210, 220),
    'O': (220, 220, 80),
    'J': (80, 80, 220),
    'L': (220, 140, 80),
    'T': (160, 80, 220),
}

COLUMNS = 10
ROWS = 20

class Piece:
    def __init__(self, x, y, shape_key):
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.cells = SHAPES[shape_key][:]
        self.color = SHAPE_COLORS[shape_key]
        self.rotation = 0  # 0..3

    def rotated_cells(self, rotation=None):
        # Compute rotated offsets using 90-degree rotation
        if rotation is None:
            r = self.rotation
        else:
            r = rotation
        cells = self.cells
        for _ in range(r % 4):
            cells = [(-y, x) for (x, y) in cells]
        return cells

    def positions(self, rotation=None):
        # Convert to grid positions
        pos = []
        for (cx, cy) in self.rotated_cells(rotation):
            pos.append((self.x + cx, self.y + cy))
        return pos


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLUMNS:
            grid[y][x] = color
    return grid


def valid_space(piece, grid, rotation=None):
    accepted_positions = [(x, y) for y in range(ROWS) for x in range(COLUMNS) if grid[y][x] == BLACK]
    for (x, y) in piece.positions(rotation):
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if y >= 0 and (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    # If any locked block is above the top (y < 0)
    for (_, y) in locked_positions.keys():
        if y < 0:
            return True
    return False


def get_shape():
    key = random.choice(list(SHAPES.keys()))
    # Spawn at top center. y is negative to allow entry
    return Piece(COLUMNS // 2, 1, key)


def draw_grid_lines(surface):
    # Vertical lines
    for i in range(COLUMNS + 1):
        x = TOP_LEFT_X + i * BLOCK_SIZE
        pygame.draw.line(surface, GREY, (x, TOP_LEFT_Y), (x, TOP_LEFT_Y + PLAY_HEIGHT))
    # Horizontal lines
    for j in range(ROWS + 1):
        y = TOP_LEFT_Y + j * BLOCK_SIZE
        pygame.draw.line(surface, GREY, (TOP_LEFT_X, y), (TOP_LEFT_X + PLAY_WIDTH, y))


def clear_rows(grid, locked_positions):
    # Start from bottom up
    rows_to_clear = []
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            rows_to_clear.append(y)
    if not rows_to_clear:
        return 0

    # Remove from locked positions
    for y in rows_to_clear:
        for x in range(COLUMNS):
            try:
                del locked_positions[(x, y)]
            except KeyError:
                pass

    # Shift rows down by the number of cleared rows below each block
    rows_to_clear_set = set(rows_to_clear)
    # Process from bottom to top so moves don't overwrite
    for (x, y) in sorted(list(locked_positions.keys()), key=lambda p: p[1], reverse=True):
        # Count how many cleared rows are strictly below this y
        shift = sum(1 for r in rows_to_clear_set if r > y)
        if shift > 0:
            color = locked_positions[(x, y)]
            del locked_positions[(x, y)]
            locked_positions[(x, y + shift)] = color
    return len(rows_to_clear)


def draw_window(surface, grid, score=0, lines=0, level=1):
    surface.fill((18, 18, 18))

    # Title
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('Tetris', True, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2, 10))

    # Play field
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), 2)

    # Draw blocks
    for y in range(ROWS):
        for x in range(COLUMNS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )
                pygame.draw.rect(
                    surface,
                    (30, 30, 30),
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1,
                )

    draw_grid_lines(surface)

    # Score panel
    font_small = pygame.font.SysFont('arial', 20)
    sx = TOP_LEFT_X + PLAY_WIDTH + 30
    sy = TOP_LEFT_Y + 50
    score_label = font_small.render(f'Score: {score}', True, WHITE)
    lines_label = font_small.render(f'Lines: {lines}', True, WHITE)
    level_label = font_small.render(f'Level: {level}', True, WHITE)
    surface.blit(score_label, (sx, sy))
    surface.blit(lines_label, (sx, sy + 30))
    surface.blit(level_label, (sx, sy + 60))


def draw_next_shape(surface, piece):
    font = pygame.font.SysFont('arial', 24)
    label = font.render('Next:', True, WHITE)
    sx = TOP_LEFT_X - 150
    sy = TOP_LEFT_Y + 50
    surface.blit(label, (sx, sy))

    for (cx, cy) in piece.rotated_cells(0):
        x = sx + 60 + (cx + 2) * BLOCK_SIZE
        y = sy + 40 + (cy + 2) * BLOCK_SIZE
        pygame.draw.rect(surface, piece.color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(surface, (30, 30, 30), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def hard_drop(piece, grid):
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def try_rotate_with_kick(current_piece, grid):
    new_rot = (current_piece.rotation + 1) % 4
    # Try rotate in place
    if valid_space(current_piece, grid, rotation=new_rot):
        current_piece.rotation = new_rot
        return
    # Wall kicks: try small offsets
    for dx in [1, -1, 2, -2]:
        if valid_space(current_piece, grid, rotation=new_rot):
            current_piece.rotation = new_rot
            return
        current_piece.x += dx
        if valid_space(current_piece, grid, rotation=new_rot):
            current_piece.rotation = new_rot
            return
        current_piece.x -= dx


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.6  # seconds per cell at level 1

    score = 0
    total_lines = 0
    level = 1

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Increase difficulty every 10 lines
        level = total_lines // 10 + 1
        fall_speed = max(0.6 - (level - 1) * 0.05, 0.1)

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
                    # Soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    try_rotate_with_kick(current_piece, grid)
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid)
                    change_piece = True
                elif event.key == pygame.K_r:
                    # Restart
                    return

        # Update grid with current piece
        for (x, y) in current_piece.positions():
            if y >= 0:
                try:
                    grid[y][x] = current_piece.color
                except IndexError:
                    pass

        # If piece should lock
        if change_piece:
            for (x, y) in current_piece.positions():
                if y < 0:
                    # Piece locked above the visible area -> game over
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                total_lines += cleared
                # Tetris scoring: 1->100, 2->300, 3->500, 4->800 scaled by level
                if cleared == 1:
                    score += 100 * level
                elif cleared == 2:
                    score += 300 * level
                elif cleared == 3:
                    score += 500 * level
                else:
                    score += 800 * level

        draw_window(win, grid, score, total_lines, level)
        draw_next_shape(win, next_piece)
        pygame.display.update()

    # Game over screen
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('Game Over - Press R to Restart or ESC to Quit', True, WHITE)
    win.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    waiting = False


def main_menu():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont('arial', 44, bold=True)
    info_font = pygame.font.SysFont('arial', 22)

    while True:
        win.fill((18, 18, 18))
        title = title_font.render('Press ENTER to Play', True, WHITE)
        info1 = info_font.render('Controls: Left/Right to move, Up to rotate, Down to drop,', True, WHITE)
        info2 = info_font.render('Space for hard drop, R to restart, ESC to quit', True, WHITE)
        win.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        win.blit(info1, (WINDOW_WIDTH // 2 - info1.get_width() // 2, 280))
        win.blit(info2, (WINDOW_WIDTH // 2 - info2.get_width() // 2, 310))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(win)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        clock.tick(60)


if __name__ == '__main__':
    main_menu()
