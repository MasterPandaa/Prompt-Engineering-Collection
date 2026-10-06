import pygame
import random
import sys
from typing import Dict, List, Tuple

# -----------------------------
# Konstanta Game
# -----------------------------
pygame.init()

s_width = 800
s_height = 700
play_width = 300   # 10 kolom * 30px
play_height = 600  # 20 baris * 30px
block_size = 30

top_left_x = (s_width - play_width) // 2
# Sisakan ruang untuk judul di atas dan panel next di kanan
# Papan dimulai agak turun dari atas layar
margin_top = 80

# Bentuk Tetris (masing-masing sebagai daftar rotasi 4x4)
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
# Warna RGB untuk tiap bentuk (consisten urutan dengan shapes)
shape_colors = [
    (48, 227, 150),   # S - hijau
    (255, 92, 87),    # Z - merah
    (86, 197, 250),   # I - cyan
    (255, 221, 89),   # O - kuning
    (64, 115, 158),   # J - biru
    (245, 171, 53),   # L - oranye
    (170, 128, 213)   # T - ungu
]

# -----------------------------
# Kelas Piece (Bidak)
# -----------------------------
class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# -----------------------------
# Utilitas Grid & Bentuk
# -----------------------------
def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}) -> List[List[Tuple[int, int, int]]]:
    grid = [[(20, 20, 20) for _ in range(10)] for _ in range(20)]  # warna gelap bg sel
    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid


def convert_shape_format(shape: Piece) -> List[Tuple[int, int]]:
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j - 2, shape.y + i - 4))
    return positions


def valid_space(shape: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = [(j, i) for i in range(20) for j in range(10) if grid[i][j] == (20, 20, 20)]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        x, y = pos
        if y < 0:
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    for (x, y) in positions:
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    return Piece(5, 0, random.choice(shapes))


# -----------------------------
# Gambar & UI
# -----------------------------
font_name = pygame.font.get_default_font()


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont(font_name, size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (top_left_x + play_width // 2 - label.get_width() // 2,
         margin_top + play_height // 2 - label.get_height() // 2)
    )


def draw_grid(surface, grid):
    sx = top_left_x
    sy = margin_top
    for i in range(len(grid)):
        pygame.draw.line(surface, (40, 40, 40), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (40, 40, 40), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    # mulai dari bawah
    cleared = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (20, 20, 20) not in row:
            cleared += 1
            # hapus baris i dari locked
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            # geser semua di atasnya turun 1
            for key in sorted(list(locked.keys()), key=lambda x: x[1]):
                x, y = key
                if y < i:
                    color = locked.pop(key)
                    locked[(x, y + 1)] = color
    return cleared


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont(font_name, 24)
    label = font.render('Next:', True, (220, 220, 220))

    sx = top_left_x + play_width + 40
    sy = margin_top + 100
    surface.blit(label, (sx, sy - 30))

    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, col in enumerate(row):
            if col == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 20, sy + i * 20, 20, 20), border_radius=3)


def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((12, 12, 12))

    # Judul
    font = pygame.font.SysFont(font_name, 36, bold=True)
    label = font.render('TETRIS', True, (240, 240, 240))
    surface.blit(label, (top_left_x + play_width // 2 - label.get_width() // 2, 20))

    # Skor
    font_small = pygame.font.SysFont(font_name, 24)
    score_label = font_small.render(f'Score: {score}', True, (220, 220, 220))
    hs_label = font_small.render(f'Best: {high_score}', True, (180, 180, 180))
    surface.blit(score_label, (top_left_x + play_width + 40, margin_top))
    surface.blit(hs_label, (top_left_x + play_width + 40, margin_top + 30))

    # Papan permainan
    pygame.draw.rect(
        surface,
        (60, 60, 60),
        (top_left_x - 4, margin_top - 4, play_width + 8, play_height + 8),
        width=4,
        border_radius=6,
    )

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != (20, 20, 20):
                pygame.draw.rect(surface, color,
                                 (top_left_x + j * block_size, margin_top + i * block_size, block_size, block_size),
                                 border_radius=4)

    draw_grid(surface, grid)


# -----------------------------
# Game Loop & Kontrol
# -----------------------------

def hard_drop(piece: Piece, grid, locked):
    # Turunkan sampai mentok, lalu kunci
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break
    # Kunci ke locked
    positions = convert_shape_format(piece)
    for x, y in positions:
        if y > -1:
            locked[(x, y)] = piece.color


def main(win):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0

    fall_speed = 0.6  # detik per jatuh 1 langkah
    level_up_every = 10  # tiap 10 line, percepat
    lines_cleared_total = 0
    score = 0
    high_score = 0

    # Coba baca HS dari file sederhana
    try:
        with open('tetris_highscore.txt', 'r') as f:
            high_score = int(f.read().strip() or 0)
    except Exception:
        high_score = 0

    # Kontrol repetisi
    move_delay = 0
    move_interval = 130  # ms untuk autorepeat kiri/kanan saat tombol ditahan

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60)  # batasi 60 FPS, dt dalam ms
        fall_time += dt / 1000.0
        move_delay += dt

        # Jatuh otomatis
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
                pygame.display.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                    move_delay = 0
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                    move_delay = 0
                elif event.key == pygame.K_DOWN:
                    # soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    # rotasi clockwise
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # coba wall kick sederhana: geser -1, +1
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                current_piece.x += 1
                                current_piece.rotation = prev_rot
                elif event.key == pygame.K_z:
                    # rotasi counter-clockwise
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                current_piece.x += 1
                                current_piece.rotation = prev_rot
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    hard_drop(current_piece, grid, locked_positions)
                    change_piece = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

        # Autorepeat kiri/kanan jika ditahan
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and move_delay >= move_interval:
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
            move_delay = 0
        if keys[pygame.K_RIGHT] and move_delay >= move_interval:
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
            move_delay = 0

        # Update grid dengan current_piece
        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Jika perlu kunci bidak
        if change_piece:
            for x, y in shape_pos:
                if y > -1:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # bersihkan baris penuh
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                lines_cleared_total += cleared
                # Skor sederhana
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 300
                elif cleared == 3:
                    score += 500
                else:
                    score += 800
                # percepat seiring progress
                fall_speed = max(0.1, 0.6 - (lines_cleared_total // level_up_every) * 0.05)

        draw_window(win, grid, score, high_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Cek kalah
        if check_lost(locked_positions):
            if score > high_score:
                high_score = score
                try:
                    with open('tetris_highscore.txt', 'w') as f:
                        f.write(str(high_score))
                except Exception:
                    pass
            draw_text_middle(win, 'GAME OVER', 48, (250, 80, 80))
            pygame.display.update()
            pygame.time.delay(1500)
            return  # kembali ke menu


def main_menu():
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris - Pygame')

    clock = pygame.time.Clock()
    running = True

    while running:
        win.fill((12, 12, 12))
        # judul dan instruksi
        font_big = pygame.font.SysFont(font_name, 48, bold=True)
        title = font_big.render('TETRIS', True, (240, 240, 240))
        win.blit(title, (top_left_x + play_width // 2 - title.get_width() // 2, 150))

        font = pygame.font.SysFont(font_name, 24)
        lines = [
            'Tekan ENTER untuk mulai',
            'Kontrol: Panah Kiri/Kanan (gerak), Bawah (soft drop),',
            'UP atau X (rotasi CW), Z (rotasi CCW), SPACE (hard drop), ESC (keluar)'
        ]
        for i, t in enumerate(lines):
            label = font.render(t, True, (200, 200, 200))
            win.blit(label, (top_left_x + play_width // 2 - label.get_width() // 2, 240 + i * 28))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(win)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        clock.tick(60)


if __name__ == '__main__':
    main_menu()
