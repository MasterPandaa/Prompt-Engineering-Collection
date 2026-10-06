import pygame
import random
import sys
from typing import Dict, List, Tuple

# ------------------------------
# Konfigurasi
# ------------------------------

# Ukuran grid
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # piksel per blok

# Dimensi jendela
PLAY_WIDTH = COLS * BLOCK_SIZE  # 300
PLAY_HEIGHT = ROWS * BLOCK_SIZE  # 600
SIDE_PANEL_WIDTH = 220
TOP_OFFSET = 60
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT + TOP_OFFSET

# Kecepatan jatuh dasar (detik per langkah)
FALL_TIME_INITIAL = 0.5

# Warna RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (80, 80, 80)

# Warna unik untuk setiap tetromino
COLOR_I = (0, 240, 240)   # Cyan
COLOR_O = (240, 240, 0)   # Yellow
COLOR_T = (160, 0, 240)   # Purple
COLOR_S = (0, 240, 0)     # Green
COLOR_Z = (240, 0, 0)     # Red
COLOR_J = (0, 0, 240)     # Blue
COLOR_L = (240, 160, 0)   # Orange

# Bentuk tetromino dalam matriks 5x5 (seperti tradisional template)
S = [
    [".....",
     ".....",
     "..00.",
     ".00..",
     "....."],
    [".....",
     "..0..",
     "..00.",
     "...0.",
     "....."],
]

Z = [
    [".....",
     ".....",
     ".00..",
     "..00.",
     "....."],
    [".....",
     "..0..",
     ".00..",
     ".0...",
     "....."],
]

I = [
    ["..0..",
     "..0..",
     "..0..",
     "..0..",
     "....."],
    [".....",
     "0000.",
     ".....",
     ".....",
     "....."],
]

O = [
    [".....",
     ".....",
     "..00.",
     "..00.",
     "....."],
]

J = [
    [".....",
     ".0...",
     ".000.",
     ".....",
     "....."],
    [".....",
     "..00.",
     "..0..",
     "..0..",
     "....."],
    [".....",
     ".....",
     ".000.",
     "...0.",
     "....."],
    [".....",
     "..0..",
     "..0..",
     ".00..",
     "....."],
]

L = [
    [".....",
     "...0.",
     ".000.",
     ".....",
     "....."],
    [".....",
     "..0..",
     "..0..",
     "..00.",
     "....."],
    [".....",
     ".....",
     ".000.",
     ".0...",
     "....."],
    [".....",
     ".00..",
     "..0..",
     "..0..",
     "....."],
]

T = [
    [".....",
     "..0..",
     ".000.",
     ".....",
     "....."],
    [".....",
     "..0..",
     "..00.",
     "..0..",
     "....."],
    [".....",
     ".....",
     ".000.",
     "..0..",
     "....."],
    [".....",
     "..0..",
     ".00..",
     "..0..",
     "....."],
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [COLOR_S, COLOR_Z, COLOR_I, COLOR_O, COLOR_J, COLOR_L, COLOR_T]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]], color: Tuple[int, int, int]):
        # posisi dalam grid (dalam satuan blok)
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # index rotasi


# ------------------------------
# Utilitas grid & bentuk
# ------------------------------

def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]):
    accepted_positions = [(x, y)
                          for y in range(ROWS)
                          for x in range(COLS)
                          if grid[y][x] == BLACK]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if y < 0:
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Game over jika ada blok di atas grid (y < 0) setelah penguncian
    for (_, y) in positions.keys():
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    idx = random.randrange(0, len(SHAPES))
    shape = SHAPES[idx]
    color = SHAPE_COLORS[idx]
    # spawn di tengah atas
    x = COLS // 2
    y = 0
    return Piece(x, y, shape, color)


# ------------------------------
# Mekanisme inti: menghapus baris
# ------------------------------

def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Menghapus baris penuh dan geser ke bawah
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            # hapus posisi yang ada di baris y
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    continue
            # geser posisi di atasnya turun 1
            for (x, yy) in sorted(list(locked.keys()), key=lambda k: k[1]):
                if yy < y:
                    color = locked[(x, yy)]
                    del locked[(x, yy)]
                    locked[(x, yy + 1)] = color
    return cleared


# ------------------------------
# Gambar UI
# ------------------------------

def draw_grid(surface):
    # garis grid pada area permainan
    sx = 0
    sy = TOP_OFFSET
    for y in range(ROWS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (sx, sy + y * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + y * BLOCK_SIZE))
    for x in range(COLS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (sx + x * BLOCK_SIZE, sy), (sx + x * BLOCK_SIZE, sy + PLAY_HEIGHT))


def draw_window(surface, grid, score: int):
    surface.fill(GRAY)

    # Judul
    font = pygame.font.SysFont('arial', 28, bold=True)
    label = font.render('Tetris', True, WHITE)
    surface.blit(label, (10, 10))

    # Skor
    font_small = pygame.font.SysFont('consolas', 22, bold=True)
    score_label = font_small.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (PLAY_WIDTH + 20, TOP_OFFSET))

    # Bingkai area permainan
    pygame.draw.rect(surface, LIGHT_GRAY, (0, TOP_OFFSET, PLAY_WIDTH, PLAY_HEIGHT), 2)

    # Gambar blok yang sudah terkunci/aktif
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(surface, color,
                                 (x * BLOCK_SIZE, TOP_OFFSET + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                # outline
                pygame.draw.rect(surface, (30, 30, 30),
                                 (x * BLOCK_SIZE, TOP_OFFSET + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    draw_grid(surface)


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont('arial', 22, bold=True)
    label = font.render('Next:', True, WHITE)

    sx = PLAY_WIDTH + 20
    sy = TOP_OFFSET + 60

    surface.blit(label, (sx, sy - 30))

    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == '0':
                x = sx + (j - 2) * BLOCK_SIZE
                y = sy + (i - 2) * BLOCK_SIZE
                pygame.draw.rect(surface, piece.color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, (30, 30, 30), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


# ------------------------------
# Game Loop
# ------------------------------

def hard_drop(piece: Piece, grid, locked):
    temp = Piece(piece.x, piece.y, piece.shape, piece.color)
    temp.rotation = piece.rotation
    while True:
        temp.y += 1
        if not valid_space(temp, grid):
            temp.y -= 1
            break
    # kunci pada posisi terakhir valid
    piece.y = temp.y
    positions = convert_shape_format(piece)
    for x, y in positions:
        if y > -1:
            locked[(x, y)] = piece.color
    return True  # menandakan terkunci


def rotate_with_kick(piece: Piece, grid):
    # Rotasi sederhana dengan wall-kick minimal: coba posisi x offset [-1, 1, -2, 2]
    original_rotation = piece.rotation
    piece.rotation = (piece.rotation + 1) % len(piece.shape)
    if valid_space(piece, grid):
        return True
    # coba geser
    for dx in (-1, 1, -2, 2):
        piece.x += dx
        if valid_space(piece, grid):
            return True
        piece.x -= dx
    # gagal, kembalikan
    piece.rotation = original_rotation
    return False


def main():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    clock = pygame.time.Clock()

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    fall_time = 0.0
    fall_speed = FALL_TIME_INITIAL

    score = 0

    # kontrol soft drop
    soft_drop = False

    while run:
        dt_ms = clock.tick(60)  # 60 FPS target
        dt = dt_ms / 1000.0
        fall_time += dt

        grid = create_grid(locked_positions)

        # Jatuh otomatis
        # Soft drop mempercepat jatuh (mis. 8x lebih cepat)
        target_fall = fall_speed / (8 if soft_drop else 1)
        if fall_time > target_fall:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Event handler
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
                    soft_drop = True
                elif event.key == pygame.K_UP:
                    rotate_with_kick(current_piece, grid)
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    hard_drop(current_piece, grid, locked_positions)
                    change_piece = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop = False

        shape_pos = convert_shape_format(current_piece)

        # Tambahkan piece saat ini ke grid agar tampak
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Jika piece harus diganti (terkunci)
        if change_piece:
            for x, y in shape_pos:
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Hapus baris penuh dan update skor
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                # Skor klasik sederhana: 1:100, 2:300, 3:500, 4:800
                add_scores = {1: 100, 2: 300, 3: 500, 4: 800}
                score += add_scores.get(cleared, 100 * cleared)

            # Cek game over
            if check_lost(locked_positions):
                run = False

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

    # Game Over layar sederhana
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('Game Over', True, WHITE)
    sub = pygame.font.SysFont('arial', 24).render('Press Enter to Restart or Esc to Quit', True, WHITE)
    win.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, TOP_OFFSET + PLAY_HEIGHT // 2 - 40))
    win.blit(sub, (PLAY_WIDTH // 2 - sub.get_width() // 2, TOP_OFFSET + PLAY_HEIGHT // 2 + 10))
    pygame.display.update()

    # Tunggu input
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
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    pygame.quit()
                    sys.exit(0)


if __name__ == '__main__':
    main()
