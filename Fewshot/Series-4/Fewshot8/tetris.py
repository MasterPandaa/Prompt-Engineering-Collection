import pygame
import random
from typing import Dict, List, Tuple

# ------------------------------
# Konfigurasi Game
# ------------------------------
pygame.init()

# Ukuran grid Tetris
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30  # ukuran setiap kotak piksel

# Ukuran window
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

# Posisi area permainan (kiri-atas)
TOP_LEFT_X = 0
TOP_LEFT_Y = 0

# Warna-warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (30, 30, 30)

# Warna untuk masing-masing tetromino
COLORS = [
    (0, 255, 255),   # I - cyan
    (0, 0, 255),     # J - blue
    (255, 165, 0),   # L - orange
    (255, 255, 0),   # O - yellow
    (0, 255, 0),     # S - green
    (128, 0, 128),   # T - purple
    (255, 0, 0)      # Z - red
]

# ------------------------------
# Representasi Bentuk (Tetromino)
# ------------------------------
# Menggunakan format 5x5 string untuk mempermudah rotasi.
# Setiap bentuk adalah list dari rotasi-rotasinya.
# Karakter '0' berarti blok terisi, '.' kosong.

S = [
    [
        ".....",
        ".....",
        "..00.",
        ".00..",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..00.",
        "...0.",
        ".....",
    ],
]

Z = [
    [
        ".....",
        ".....",
        ".00..",
        "..00.",
        ".....",
    ],
    [
        ".....",
        "..0..",
        ".00..",
        ".0...",
        ".....",
    ],
]

I = [
    [
        "..0..",
        "..0..",
        "..0..",
        "..0..",
        ".....",
    ],
    [
        ".....",
        "0000.",
        ".....",
        ".....",
        ".....",
    ],
]

O = [
    [
        ".....",
        ".....",
        " .00.",
        " .00.",
        ".....",
    ],
]
# Perbaiki spasi di O agar valid
O = [
    [
        ".....",
        ".....",
        "..00.",
        "..00.",
        ".....",
    ],
]

J = [
    [
        ".....",
        ".0...",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..00.",
        "..0..",
        "..0..",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        "...0.",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..0..",
        ".00..",
        ".....",
    ],
]

L = [
    [
        ".....",
        "...0.",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..0..",
        "..00.",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        ".0...",
        ".....",
    ],
    [
        ".....",
        ".00..",
        "..0..",
        "..0..",
        ".....",
    ],
]

T = [
    [
        ".....",
        "..0..",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..00.",
        "..0..",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        "..0..",
        ".....",
    ],
    [
        ".....",
        "..0..",
        ".00..",
        "..0..",
        ".....",
    ],
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = COLORS  # 1:1 indeks

# ------------------------------
# Kelas Piece (bidak)
# ------------------------------
class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0  # index dari list rotasi

# ------------------------------
# Utilitas Grid
# ------------------------------

def create_grid(locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked:
                grid[y][x] = locked[(x, y)]
    return grid


def convert_shape_format(piece: Piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 2))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]):
    accepted_pos = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == BLACK] for y in range(GRID_HEIGHT)]
    accepted_pos = [x for sub in accepted_pos for x in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    for x, y in locked_positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(GRID_WIDTH // 2, 0, random.choice(SHAPES))

# ------------------------------
# Menggambar
# ------------------------------

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        pygame.draw.line(surface, GREY, (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE))
    for x in range(GRID_WIDTH):
        pygame.draw.line(surface, GREY, (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    removed_rows = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[y]:
            removed_rows += 1
            # hapus semua posisi pada baris ini
            for x in range(GRID_WIDTH):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # geser ke bawah baris di atasnya
            for (lx, ly) in sorted(list(locked.keys()), key=lambda p: p[1]):
                if ly < y:
                    color = locked[(lx, ly)]
                    del locked[(lx, ly)]
                    locked[(lx, ly + 1)] = color
    return removed_rows


def draw_window(surface, grid, score=0):
    surface.fill(DARK_GREY)

    # Judul
    font = pygame.font.SysFont('arial', 30, bold=True)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH + 20, 20))

    # Score
    font_small = pygame.font.SysFont('arial', 22)
    score_label = font_small.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 20, 70))

    # Area board
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(
                surface,
                grid[y][x],
                (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

    draw_grid(surface, grid)

    # Batas area bermain
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont('arial', 22)
    label = font.render('Next:', True, WHITE)

    sx = TOP_LEFT_X + PLAY_WIDTH + 20
    sy = 120

    surface.blit(label, (sx, sy))

    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (sx + j * 20, sy + 30 + i * 20, 20, 20),
                )

# ------------------------------
# Game Loop
# ------------------------------

def main(surface):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per satu langkah turun
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt
        level_time += dt

        # Percepat sedikit setiap 30 detik sampai batas
        if level_time > 30:
            level_time = 0
            fall_speed = max(0.12, fall_speed - 0.02)

        # Turun otomatis
        if fall_time > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
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
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # simple wall kick: coba geser kiri/kanan 1 sel
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                # gagal, kembalikan
                                current_piece.x += 1
                                current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Tambahkan ke grid untuk menggambar
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Jika bidak sudah mendarat
        if change_piece:
            for x, y in shape_pos:
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            rows_cleared = clear_rows(grid, locked_positions)
            if rows_cleared:
                # Skor sederhana: 100 per baris, bonus sedikit untuk combo
                score += 100 * rows_cleared + (rows_cleared - 1) * 50

        draw_window(surface, grid, score)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    # Layar Game Over
    surface.fill(DARK_GREY)
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('Game Over', True, WHITE)
    surface.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, PLAY_HEIGHT // 2 - label.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')

    run = True
    clock = pygame.time.Clock()
    while run:
        surface.fill(DARK_GREY)
        title_font = pygame.font.SysFont('arial', 36, bold=True)
        title_label = title_font.render('Press Any Key to Play', True, WHITE)
        surface.blit(title_label, (PLAY_WIDTH // 2 - title_label.get_width() // 2, PLAY_HEIGHT // 2 - title_label.get_height() // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(surface)
    pygame.quit()


if __name__ == '__main__':
    main_menu()
