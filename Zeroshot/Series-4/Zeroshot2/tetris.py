import pygame
import random
import sys

# -------------------------
# Konstanta permainan
# -------------------------
COLS = 10
ROWS = 20
BLOCK_SIZE = 30
PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE

SIDE_PANEL_WIDTH = 200
MARGIN = 20
WIN_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH + MARGIN * 3
WIN_HEIGHT = PLAY_HEIGHT + MARGIN * 2

# Warna
BLACK = (20, 20, 20)
GRAY = (60, 60, 60)
WHITE = (230, 230, 230)

# Bentuk Tetromino menggunakan representasi 4x4
# '0' menandakan blok yang terisi, '.' kosong
S = [
    ['.....',
     '.....',
     '..00.',
     '.00..',
     '.....'],
    ['.....',
     '..0..',
     '..00.',
     '...0.',
     '.....']
]

Z = [
    ['.....',
     '.....',
     '.00..',
     '..00.',
     '.....'],
    ['.....',
     '..0..',
     '.00..',
     '.0...',
     '.....']
]

I = [
    ['..0..',
     '..0..',
     '..0..',
     '..0..',
     '.....'],
    ['.....',
     '0000.',
     '.....',
     '.....',
     '.....']
]

O = [
    ['.....',
     '.....',
     '.00..',
     '.00..',
     '.....']
]

J = [
    ['.....',
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
     '.....']
]

L = [
    ['.....',
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
     '.....']
]

T = [
    ['.....',
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
     '.....']
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = {
    id(S): (80, 220, 100),   # S - hijau
    id(Z): (220, 60, 60),    # Z - merah
    id(I): (60, 200, 220),   # I - cyan
    id(O): (240, 220, 90),   # O - kuning
    id(J): (80, 80, 220),    # J - biru
    id(L): (220, 150, 60),   # L - oranye
    id(T): (170, 80, 200),   # T - ungu
}


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[id(shape)]
        self.rotation = 0


def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    rotation = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(rotation):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 2))
    return positions


def valid_space(piece, grid):
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if (x, y) not in accepted_positions and y >= 0:
            return False
    return True


def check_lost(locked_positions):
    # Kalah jika ada blok terkunci di atas (y < 1)
    for (_, y) in locked_positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(COLS // 2, 0, random.choice(SHAPES))


def draw_grid_lines(surface):
    # Garis grid di area permainan
    sx = MARGIN
    sy = MARGIN
    for i in range(ROWS + 1):
        pygame.draw.line(surface, GRAY, (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
    for j in range(COLS + 1):
        pygame.draw.line(surface, GRAY, (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))


def clear_rows(grid, locked):
    # Menghapus baris penuh dan menggeser turun
    lines_cleared = 0
    for i in range(ROWS - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            lines_cleared += 1
            # Hapus posisi terkunci di baris ini
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            # Geser baris di atasnya turun
            new_locked = {}
            for (x, y), color in locked.items():
                if y < i:
                    new_locked[(x, y + 1)] = color
                else:
                    new_locked[(x, y)] = color
            locked.clear()
            locked.update(new_locked)
            # Setelah menggeser, perlu cek baris yang sama lagi
            # karena semua baris di atas turun satu tingkat
            # dan mungkin baris i sekarang juga penuh.
            # Jadi lanjutkan loop i tanpa mengubah indeks.
            # grid akan dibuat ulang di pemanggil.
    return lines_cleared


def draw_text_center(surface, text, size, color, center):
    font = pygame.font.SysFont('consolas', size, bold=True)
    label = font.render(text, True, color)
    rect = label.get_rect(center=center)
    surface.blit(label, rect)


def draw_window(surface, grid, score=0, next_piece=None):
    surface.fill((10, 10, 10))

    # Judul
    title_font = pygame.font.SysFont('consolas', 28, bold=True)
    title_label = title_font.render('TETRIS', True, WHITE)
    surface.blit(title_label, (MARGIN, 2))

    # Area permainan
    pygame.draw.rect(surface, (30, 30, 30), (MARGIN, MARGIN, PLAY_WIDTH, PLAY_HEIGHT))

    # Gambar blok-blok pada grid
    for i in range(ROWS):
        for j in range(COLS):
            color = grid[i][j]
            if color != BLACK:
                pygame.draw.rect(surface, color,
                                 (MARGIN + j * BLOCK_SIZE, MARGIN + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                # Inner shade
                pygame.draw.rect(surface, (0, 0, 0),
                                 (MARGIN + j * BLOCK_SIZE, MARGIN + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    draw_grid_lines(surface)

    # Panel samping
    panel_x = MARGIN * 2 + PLAY_WIDTH
    panel_y = MARGIN
    # Skor
    score_font = pygame.font.SysFont('consolas', 22)
    score_label = score_font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (panel_x, panel_y))

    # Next piece
    if next_piece:
        np_label = score_font.render('Next:', True, WHITE)
        surface.blit(np_label, (panel_x, panel_y + 40))
        fmt = convert_shape_format(next_piece)
        min_x = min([x for x, _ in fmt])
        min_y = min([y for _, y in fmt])
        # Normalisasi ke (0,0)
        norm = [(x - min_x, y - min_y) for x, y in fmt]
        for (x, y) in norm:
            pygame.draw.rect(surface, next_piece.color,
                             (panel_x + x * (BLOCK_SIZE // 1) + 10,
                              panel_y + 70 + y * (BLOCK_SIZE // 1) + 10,
                              BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(surface, (0, 0, 0),
                             (panel_x + x * (BLOCK_SIZE // 1) + 10,
                              panel_y + 70 + y * (BLOCK_SIZE // 1) + 10,
                              BLOCK_SIZE, BLOCK_SIZE), 1)

    # Bingkai
    pygame.draw.rect(surface, WHITE, (MARGIN, MARGIN, PLAY_WIDTH, PLAY_HEIGHT), 2)


def hard_drop(piece, grid):
    # Turunkan sampai mentok
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def main():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.6  # detik per jatuh 1 blok
    level_time = 0
    score = 0

    key_down_pressed = False

    while run:
        dt = clock.tick(60) / 1000.0
        fall_time += dt
        level_time += dt

        # Sedikit percepatan seiring waktu (opsional)
        if level_time > 30:
            level_time = 0
            fall_speed = max(0.1, fall_speed - 0.05)

        # Gravity jatuh
        if fall_time >= (fall_speed / (4 if key_down_pressed else 1)):
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
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
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    key_down_pressed = True
                    # Soft drop step-by-step
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        change_piece = True
                elif event.key == pygame.K_UP:
                    old_rotation = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # Simple wall kick mencoba geser kiri/kanan
                        kicked = False
                        for dx in (-1, 1, -2, 2):
                            current_piece.x += dx
                            if valid_space(current_piece, grid):
                                kicked = True
                                break
                            current_piece.x -= dx
                        if not kicked:
                            current_piece.rotation = old_rotation
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    hard_drop(current_piece, grid)
                    change_piece = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    key_down_pressed = False

        grid = create_grid(locked_positions)
        # Gambar current piece ke grid sementara
        for (x, y) in convert_shape_format(current_piece):
            if y >= 0 and 0 <= x < COLS and 0 <= y < ROWS:
                grid[y][x] = current_piece.color

        if change_piece:
            for (x, y) in convert_shape_format(current_piece):
                if y < 0:
                    # Muncul langsung tabrakan => game over
                    run = False
                    break
                if 0 <= x < COLS and 0 <= y < ROWS:
                    locked_positions[(x, y)] = current_piece.color
            if not run:
                break
            lines = clear_rows(grid, locked_positions)
            if lines > 0:
                # Skor standar Tetris (sederhana)
                if lines == 1:
                    score += 100
                elif lines == 2:
                    score += 300
                elif lines == 3:
                    score += 500
                elif lines >= 4:
                    score += 800
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

        draw_window(win, grid, score, next_piece)
        pygame.display.update()

    # Game Over Screen
    over_font = pygame.font.SysFont('consolas', 36, bold=True)
    small_font = pygame.font.SysFont('consolas', 22)
    win.fill((10, 10, 10))
    draw_text_center(win, 'GAME OVER', 48, WHITE, (WIN_WIDTH // 2, WIN_HEIGHT // 2 - 30))
    score_text = small_font.render(f'Final Score: {score}', True, WHITE)
    score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 10))
    win.blit(score_text, score_rect)
    hint_text = small_font.render('Press Enter to play again or Esc to quit', True, WHITE)
    hint_rect = hint_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 40))
    win.blit(hint_text, hint_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
                    return
                elif event.key == pygame.K_ESCAPE:
                    waiting = False
                    pygame.quit()
                    sys.exit(0)


if __name__ == '__main__':
    main()
