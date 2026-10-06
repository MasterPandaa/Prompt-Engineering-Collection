import pygame
import random
import sys

# -----------------------------
# Konstanta permainan
# -----------------------------
SCREEN_WIDTH = 300  # 10 kolom * 30px
SCREEN_HEIGHT = 600  # 20 baris * 30px
PLAY_WIDTH = 300  # area permainan (10 * 30)
PLAY_HEIGHT = 600  # area permainan (20 * 30)
BLOCK_SIZE = 30
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

# Grid 10x20
COLS = 10
ROWS = 20

# Warna dasar
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Definisi bentuk Tetromino dalam matriks 4x4 untuk tiap state rotasi
# Menggunakan representasi 0/1 agar mudah dipetakan ke koordinat grid
# Urutan: S, Z, I, O, J, L, T
S = [
    [
        "..00",
        ".00.",
        "....",
        "....",
    ],
    [
        ".0..",
        ".00.",
        "..0.",
        "....",
    ],
]

Z = [
    [
        ".00.",
        "..00",
        "....",
        "....",
    ],
    [
        "..0.",
        ".00.",
        ".0..",
        "....",
    ],
]

I = [
    [
        "0000",
        "....",
        "....",
        "....",
    ],
    [
        "..0.",
        "..0.",
        "..0.",
        "..0.",
    ],
]

O = [
    [
        ".00.",
        ".00.",
        "....",
        "....",
    ],
]

J = [
    [
        "0...",
        "000.",
        "....",
        "....",
    ],
    [
        ".00.",
        ".0..",
        ".0..",
        "....",
    ],
    [
        "....",
        "000.",
        "...0",
        "....",
    ],
    [
        "..0.",
        "..0.",
        ".00.",
        "....",
    ],
]

L = [
    [
        "...0",
        "000.",
        "....",
        "....",
    ],
    [
        ".0..",
        ".0..",
        ".00.",
        "....",
    ],
    [
        "....",
        "000.",
        "0...",
        "....",
    ],
    [
        ".00.",
        "..0.",
        "..0.",
        "....",
    ],
]

T = [
    [
        "..0.",
        ".000",
        "....",
        "....",
    ],
    [
        "..0.",
        "..00",
        "..0.",
        "....",
    ],
    [
        "....",
        ".000",
        "..0.",
        "....",
    ],
    [
        "..0.",
        ".00.",
        "..0.",
        "....",
    ],
]

SHAPES = [S, Z, I, O, J, L, T]
# Warna untuk masing-masing shape
SHAPE_COLORS = [
    (48, 226, 133),   # S - hijau
    (226, 48, 83),    # Z - merah
    (48, 168, 226),   # I - cyan
    (226, 205, 48),   # O - kuning
    (48, 83, 226),    # J - biru
    (226, 143, 48),   # L - oranye
    (162, 48, 226),   # T - ungu
]


class Piece:
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0  # index dari state rotasi


# -----------------------------
# Utility Grid dan Game Logic
# -----------------------------

def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    rotation_pattern = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(rotation_pattern):
        for j, char in enumerate(line):
            if char == '0':
                positions.append((piece.x + j, piece.y + i))

    # offset kecil (karena tetromino didefinisikan di 4x4)
    return positions


def valid_space(piece, grid):
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:  # mengabaikan posisi di atas layar
                return False
    return True


def check_lost(positions):
    # Kalah bila ada blok terkunci di baris y < 1 (masuk ke area spawn)
    for (x, y) in positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(COLS // 2 - 2, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (
            TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
            TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2,
        ),
    )


def clear_rows(grid, locked):
    # Hapus baris penuh dan geser ke bawah
    cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            # hapus semua kunci pada baris i
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            # Geser semua baris di atas turun satu
            for key in sorted(list(locked), key=lambda x: x[1]):
                x, y = key
                if y < i:
                    color = locked.pop(key)
                    locked[(x, y + 1)] = color
    return cleared


def draw_grid(surface, grid):
    # Gambar kotak-kotak grid
    for i in range(ROWS):
        pygame.draw.line(
            surface, GREY, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE)
        )
    for j in range(COLS):
        pygame.draw.line(
            surface, GREY, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT)
        )


def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((18, 18, 18))

    # Judul
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, 10))

    # Skor
    small_font = pygame.font.SysFont('arial', 20)
    score_label = small_font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (10, 10))

    high_label = small_font.render(f'High: {high_score}', True, WHITE)
    surface.blit(high_label, (10, 35))

    # Area permainan
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), 2)

    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                0,
            )

    draw_grid(surface, grid)


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('arial', 20, bold=True)
    label = font.render('Next:', True, WHITE)

    sx = TOP_LEFT_X + PLAY_WIDTH + 10
    sy = TOP_LEFT_Y + 60

    surface.blit(label, (sx, TOP_LEFT_Y + 20))

    rotation_pattern = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(rotation_pattern):
        for j, char in enumerate(line):
            if char == '0':
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (sx + j * BLOCK_SIZE // 2, sy + i * BLOCK_SIZE // 2, BLOCK_SIZE // 2, BLOCK_SIZE // 2),
                    0,
                )


def rotate_with_kicks(piece, grid, direction=1):
    # Rotasi CW (direction=+1) atau CCW (direction=-1) dengan wall kick sederhana
    original_rotation = piece.rotation
    original_x, original_y = piece.x, piece.y
    piece.rotation = (piece.rotation + direction) % len(piece.shape)

    if valid_space(piece, grid):
        return True

    kicks = [(-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
    for dx, dy in kicks:
        piece.x += dx
        piece.y += dy
        if valid_space(piece, grid):
            return True
        piece.x -= dx
        piece.y -= dy

    # Tidak berhasil, batalkan rotasi dan posisi
    piece.rotation = original_rotation
    piece.x, piece.y = original_x, original_y
    return False


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per turun satu baris
    level_speedup_every = 10
    piece_count = 0

    score = 0
    high_score = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Turun otomatis sesuai fall_speed
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
                    # Soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    # Rotate CW dengan wall kick sederhana
                    rotate_with_kicks(current_piece, grid, direction=1)
                elif event.key == pygame.K_z:
                    # Rotate CCW
                    rotate_with_kicks(current_piece, grid, direction=-1)
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Tambahkan ke grid sementara untuk menggambar current piece
        for x, y in shape_pos:
            if y > -1 and 0 <= x < COLS and 0 <= y < ROWS:
                grid[y][x] = current_piece.color

        # Jika piece sudah tidak bisa turun lagi, kunci ke locked_positions
        if change_piece:
            for pos in shape_pos:
                x, y = pos
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            piece_count += 1

            # Clear rows dan hitung skor
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                # Skor sederhana: 100, 300, 500, 800 untuk 1-4 baris
                score_add = {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 100 * cleared)
                score += score_add
                high_score = max(high_score, score)

            # Percepat sedikit per beberapa piece
            if piece_count % level_speedup_every == 0 and fall_speed > 0.1:
                fall_speed = max(0.1, fall_speed - 0.05)

        draw_window(win, grid, score, high_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Cek kalah
        if check_lost(locked_positions):
            run = False

    # Layar Game Over
    draw_window(win, grid, score, high_score)
    draw_text_middle(win, 'Game Over', 40, WHITE)
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')

    running = True
    while running:
        win.fill((18, 18, 18))
        draw_text_middle(win, 'Tekan ENTER untuk mulai', 24, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(win)

    pygame.quit()


if __name__ == '__main__':
    main_menu()
