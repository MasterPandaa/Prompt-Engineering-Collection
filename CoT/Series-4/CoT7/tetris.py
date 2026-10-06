import pygame
import random
import sys
from typing import Dict, List, Tuple

# -----------------------------
# Konstanta Game
# -----------------------------
pygame.init()

s_width = 600
s_height = 700
play_width = 300   # 10 kolom * 30 px
play_height = 600  # 20 baris * 30 px
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Bentuk Tetris (Rotasi berupa daftar 4x4 grid)
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
# Warna per bentuk (R, G, B)
shape_colors = [
    (80, 227, 230),   # S - cyan-ish
    (226, 116, 113),  # Z - red-ish
    (69, 177, 232),   # I - blue
    (246, 227, 90),   # O - yellow
    (62, 76, 163),    # J - indigo
    (240, 178, 122),  # L - orange
    (144, 86, 180)    # T - purple
]

# -----------------------------
# Class Piece
# -----------------------------
class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # index rotasi

# -----------------------------
# Utilitas Grid
# -----------------------------
def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}) -> List[List[Tuple[int, int, int]]]:
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if x < 0 or x >= 10 or y >= 20:
            return False
        if y >= 0 and (x, y) not in accepted_pos:
            return False
    return True


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    for (x, y) in locked_positions:
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    return Piece(5, 0, random.choice(shapes))

# -----------------------------
# Render
# -----------------------------

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2),
                         top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    for i in range(len(grid)):
        pygame.draw.line(surface, (40, 40, 40), (top_left_x, top_left_y + i*block_size),
                         (top_left_x + play_width, top_left_y + i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (40, 40, 40), (top_left_x + j*block_size, top_left_y),
                             (top_left_x + j*block_size, top_left_y + play_height))


def clear_rows(grid, locked):
    # Menghapus baris penuh dan menggeser turun
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # hapus setiap posisi di baris ini
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except KeyError:
                    continue
    if inc > 0:
        # geser baris di atasnya turun
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < 20:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 24)
    label = font.render('Next:', True, (255, 255, 255))

    sx = top_left_x + play_width + 30
    sy = top_left_y + 50
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j*20, sy + i*20, 20, 20), 0, border_radius=3)

    surface.blit(label, (sx, sy - 30))


def draw_window(surface, grid, score=0, lines=0):
    surface.fill((18, 18, 18))

    # Title
    font = pygame.font.SysFont('comicsans', 44, bold=True)
    label = font.render('TETRIS', True, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - label.get_width()/2, 10))

    # Score
    font = pygame.font.SysFont('comicsans', 24)
    score_label = font.render(f'Score: {score}', True, (230, 230, 230))
    lines_label = font.render(f'Lines: {lines}', True, (200, 200, 200))
    surface.blit(score_label, (top_left_x - 180, top_left_y + 100))
    surface.blit(lines_label, (top_left_x - 180, top_left_y + 130))

    # Border playfield
    pygame.draw.rect(surface, (200, 200, 200), (top_left_x - 2, top_left_y - 2, play_width + 4, play_height + 4), 2, border_radius=4)

    # Draw grid squares
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color == (0, 0, 0):
                # cell kosong
                pygame.draw.rect(surface, (28, 28, 28), (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size))
            else:
                pygame.draw.rect(surface, color, (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), border_radius=4)

    draw_grid(surface, grid)

# -----------------------------
# Game Loop
# -----------------------------

def main(surface):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per turun
    level_time = 0

    score = 0
    lines_cleared = 0

    key_down_move_delay = 0
    move_repeat_rate = 60  # ms

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60)
        fall_time += dt / 1000.0
        level_time += dt

        # percepat sedikit seiring waktu
        if level_time / 1000 > 30:
            level_time = 0
            if fall_speed > 0.1:
                fall_speed -= 0.02

        # input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit()
                    sys.exit(0)
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    # soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key in (pygame.K_UP, pygame.K_w):
                    # rotate
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # coba nudge ke kiri/kanan (wall kick sederhana)
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                # gagal, revert
                                current_piece.x += 1
                                current_piece.rotation = prev_rot
                if event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        # auto fall
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Tambahkan warna piece ke grid sementara
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Kunci piece jika sudah mendarat
        if change_piece:
            for x, y in shape_pos:
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                lines_cleared += cleared
                # Skor sederhana: 100, 300, 500, 800 untuk 1-4 baris
                score_table = {1: 100, 2: 300, 3: 500, 4: 800}
                score += score_table.get(cleared, cleared * 200)

        draw_window(surface, grid, score, lines_cleared)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

        # Cek kalah
        if check_lost(locked_positions):
            draw_text_middle(surface, 'GAME OVER', 48, (255, 60, 60))
            pygame.display.update()
            pygame.time.delay(2000)
            return  # kembali ke menu


def main_menu(surface):
    run = True
    while run:
        surface.fill((18, 18, 18))
        draw_text_middle(surface, 'Tekan ENTER untuk mulai', 36, (255, 255, 255))
        draw_text_middle(surface, 'ESC untuk keluar', 22, (180, 180, 180))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(surface)
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.quit()


if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris - Pygame')
    main_menu(win)
