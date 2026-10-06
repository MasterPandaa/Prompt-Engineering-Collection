import pygame
import random
import sys

# Konfigurasi grid
S_WIDTH = 800
S_HEIGHT = 700
PLAY_WIDTH = 300   # 10 kolom * 30 px
PLAY_HEIGHT = 600  # 20 baris * 30 px
BLOCK_SIZE = 30

TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT - 50

# Bentuk-bentuk Tetris (format 4x4 untuk tiap rotasi)
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
# Warna-warna untuk setiap shape
SHAPE_COLORS = [
    (80, 227, 230),  # S - cyan-like
    (234, 177, 133), # Z - peach
    (48, 99, 142),   # I - blue dark
    (237, 234, 85),  # O - yellow
    (109, 104, 117), # J - gray
    (87, 166, 57),   # L - green
    (238, 130, 238)  # T - violet
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
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, col in enumerate(row):
            if col == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for (_, y) in positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
                         TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(len(grid)):
        pygame.draw.line(surface, (40, 40, 40), (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (40, 40, 40), (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))


def clear_rows(grid, locked):
    # Menghapus baris penuh dan menggeser turun
    cleared = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            cleared += 1
            # hapus semua posisi locked pada baris i
            for j in range(10):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
    if cleared > 0:
        # geser semua posisi di atasnya turun sesuai jumlah cleared
        # mulai dari baris paling atas hingga bawah
        for key in sorted(list(locked), key=lambda x: x[1]):
            x, y = key
            shift = 0
            for i in range(y + 1, 20):
                # hitung berapa banyak baris penuh di bawah key ini
                row = grid[i]
                if (0, 0, 0) not in row:
                    shift += 1
            if shift > 0:
                color = locked.pop((x, y))
                locked[(x, y + shift)] = color
    return cleared


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('arial', 24)
    label = font.render('Next:', True, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 30
    sy = TOP_LEFT_Y + 120

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    surface.blit(label, (sx, sy - 40))

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, col in enumerate(row):
            if col == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * 20, sy + i * 20, 20, 20), 0, border_radius=4)


def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((15, 15, 20))

    # Title
    font = pygame.font.SysFont('arial', 48, bold=True)
    label = font.render('TETRIS', True, (255, 255, 255))

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 20))

    # Score
    font = pygame.font.SysFont('arial', 24)
    score_label = font.render(f'Score: {score}', True, (200, 200, 200))
    hi_label = font.render(f'High: {high_score}', True, (200, 200, 200))

    surface.blit(score_label, (TOP_LEFT_X - 200, TOP_LEFT_Y + 100))
    surface.blit(hi_label, (TOP_LEFT_X - 200, TOP_LEFT_Y + 140))

    # Play area border
    pygame.draw.rect(surface, (180, 180, 180), (TOP_LEFT_X - 4, TOP_LEFT_Y - 4, PLAY_WIDTH + 8, PLAY_HEIGHT + 8), 2, border_radius=6)

    # Draw grid blocks
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != (0, 0, 0):
                pygame.draw.rect(surface, color, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0, border_radius=6)

    # Grid lines
    draw_grid(surface, grid)


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per turunan otomatis
    level_time = 0
    score = 0
    high_score = 0

    # coba baca high score dari file
    try:
        with open('highscore.txt', 'r') as f:
            high_score = int(f.read().strip() or '0')
    except Exception:
        high_score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime() / 1000.0
        level_time += clock.get_rawtime() / 1000.0
        clock.tick()

        # naikkan kesulitan setiap 60 detik
        if level_time > 60:
            level_time = 0
            fall_speed = max(0.1, fall_speed - 0.05)

        # turun otomatis
        if fall_time > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # input
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
                    # soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    # rotate
                    prev_rotation = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # coba nudge ke kiri/kanan agar muat (wall kick sederhana)
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                # batal rotasi
                                current_piece.x += 1
                                current_piece.rotation = prev_rotation
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

        shape_pos = convert_shape_format(current_piece)

        # tambahkan current piece ke grid sementara untuk render
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # jika piece sudah harus diganti
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            cleared = clear_rows(grid, locked_positions)
            if cleared:
                score += (cleared ** 2) * 100

        draw_window(win, grid, score, max(score, high_score))
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            # simpan high score
            high_score = max(high_score, score)
            try:
                with open('highscore.txt', 'w') as f:
                    f.write(str(high_score))
            except Exception:
                pass
            draw_text_middle(win, 'GAME OVER', 48, (255, 80, 80))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False


def main_menu():
    pygame.init()
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')
    clock = pygame.time.Clock()

    while True:
        win.fill((15, 15, 20))
        draw_text_middle(win, 'Tekan ENTER untuk mulai', 32, (220, 220, 220))
        draw_text_middle(win, 'Panah: Gerak, Atas: Rotasi, Spasi: Hard Drop', 20, (160, 160, 160))
        pygame.display.update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    main(win)


if __name__ == '__main__':
    main_menu()
