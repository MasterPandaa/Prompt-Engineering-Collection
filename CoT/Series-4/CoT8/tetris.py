import pygame
import random
import sys

# Konfigurasi dasar
pygame.init()

# Ukuran grid Tetris
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30  # ukuran pixel per kotak

# Dimensi jendela permainan
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

# Posisi offset area permainan (kiri-atas)
TOP_LEFT_X = 0
TOP_LEFT_Y = 0

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
LIGHT_GREY = (180, 180, 180)

# Bentuk Tetris (format 4x4 per rotasi)
# Masing-masing bentuk direpresentasikan sebagai list string 4 baris,
# '0' menandakan blok aktif, '.' kosong
S = [['.00.',
      '00..',
      '....',
      '....'],
     ['.0..',
      '.00.',
      '..0.',
      '....']]

Z = [['00..',
      '.00.',
      '....',
      '....'],
     ['.0..',
      '00..',
      '0...',
      '....']]

I = [['....',
      '0000',
      '....',
      '....'],
     ['..0.',
      '..0.',
      '..0.',
      '..0.']]

O = [['.00.',
      '.00.',
      '....',
      '....']]

J = [['0...',
      '000.',
      '....',
      '....'],
     ['.00.',
      '.0..',
      '.0..',
      '....'],
     ['....',
      '000.',
      '..0.',
      '....'],
     ['.0..',
      '.0..',
      '00..',
      '....']]

L = [['..0.',
      '000.',
      '....',
      '....'],
     ['.0..',
      '.0..',
      '.00.',
      '....'],
     ['....',
      '000.',
      '0...',
      '....'],
     ['00..',
      '.0..',
      '.0..',
      '....']]

T = [['.0..',
      '000.',
      '....',
      '....'],
     ['.0..',
      '.00.',
      '.0..',
      '....'],
     ['....',
      '000.',
      '.0..',
      '....'],
     ['.0..',
      '00..',
      '.0..',
      '....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [
    (80, 220, 100),   # S - hijau
    (220, 80, 80),    # Z - merah
    (80, 210, 220),   # I - cyan
    (220, 220, 80),   # O - kuning
    (80, 80, 220),    # J - biru
    (220, 150, 80),   # L - oranye
    (200, 80, 200)    # T - ungu
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0  # indeks rotasi aktif

    def cells(self):
        # Mengembalikan daftar koordinat (x, y) dari blok aktif berdasarkan rotasi & posisi
        positions = []
        rotation_pattern = self.shape[self.rotation % len(self.shape)]
        for i, line in enumerate(rotation_pattern):
            for j, char in enumerate(line):
                if char == '0':
                    positions.append((self.x + j - 1, self.y + i - 2))
        return positions


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def valid_space(piece, grid):
    accepted_positions = [(j, i) for i in range(GRID_HEIGHT) for j in range(GRID_WIDTH) if grid[i][j] == BLACK]
    formatted = piece.cells()
    for pos in formatted:
        x, y = pos
        if y < 0:
            # baris di atas layar masih boleh
            continue
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    # Jika ada blok terkunci di atas layar (y < 1), game over
    for (_, y) in locked_positions.keys():
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(GRID_WIDTH // 2 - 1, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2,
                         TOP_LEFT_Y + PLAY_HEIGHT // 2 - label.get_height() // 2))


def draw_gridlines(surface, grid):
    # Garis grid
    for i in range(GRID_HEIGHT):
        pygame.draw.line(surface, GREY, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
    for j in range(GRID_WIDTH):
        pygame.draw.line(surface, GREY, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
                         (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    # Cek dari bawah ke atas untuk baris penuh
    cleared_rows_idx = []
    for i in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared_rows_idx.append(i)
    if not cleared_rows_idx:
        return 0

    # Hapus blok di baris yang penuh
    for row in cleared_rows_idx:
        for j in range(GRID_WIDTH):
            try:
                del locked[(j, row)]
            except KeyError:
                pass

    # Geser turun blok di atas baris yang dihapus
    # Hitung berapa banyak baris terhapus di bawah setiap posisi
    cleared_set = set(cleared_rows_idx)
    new_locked = {}
    for (x, y), color in locked.items():
        # berapa baris yang dihapus dengan indeks > y? (di bawahnya)
        drop = sum(1 for r in cleared_rows_idx if r > y)
        new_locked[(x, y + drop)] = color

    locked.clear()
    locked.update(new_locked)

    return len(cleared_rows_idx)


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('arial', 24, bold=True)
    label = font.render('Next:', True, WHITE)

    sx = PLAY_WIDTH + 20
    sy = 40
    surface.blit(label, (sx, sy))

    pattern = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(pattern):
        for j, char in enumerate(line):
            if char == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * BLOCK_SIZE, sy + 30 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(surface, LIGHT_GREY,
                                 (sx + j * BLOCK_SIZE, sy + 30 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_window(surface, grid, score=0, high_score=0):
    surface.fill((25, 25, 30))

    # Judul
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, 10))

    # Skor
    font_small = pygame.font.SysFont('arial', 20)
    score_label = font_small.render(f'Score: {score}', True, WHITE)
    hi_label = font_small.render(f'High: {high_score}', True, WHITE)
    surface.blit(score_label, (PLAY_WIDTH + 20, 160))
    surface.blit(hi_label, (PLAY_WIDTH + 20, 190))

    # Gambar grid kotak
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            color = grid[i][j]
            pygame.draw.rect(surface, color,
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            # outline
            pygame.draw.rect(surface, (40, 40, 50),
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    # Garis grid
    draw_gridlines(surface, grid)

    # Batas kanan panel
    pygame.draw.line(surface, GREY, (PLAY_WIDTH, 0), (PLAY_WIDTH, WINDOW_HEIGHT), 2)


def main(window):
    locked_positions = {}  # (x, y) -> color
    grid = create_grid(locked_positions)

    change_piece = False
    run = True

    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per turun 1 langkah

    level_up_every = 10  # setiap 10 baris clear, percepat
    lines_cleared_since_speed = 0

    score = 0
    high_score = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Bidak turun otomatis
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Event input
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
                    # soft drop
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        change_piece = True
                elif event.key == pygame.K_UP:
                    # rotate
                    old_rotation = current_piece.rotation
                    old_x = current_piece.x
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # coba wall kick sederhana: geser kiri/kanan
                        kicked = False
                        for dx in (-1, 1, -2, 2):
                            current_piece.x = old_x + dx
                            if valid_space(current_piece, grid):
                                kicked = True
                                break
                        if not kicked:
                            current_piece.rotation = old_rotation
                            current_piece.x = old_x
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

        # Tempel current piece ke grid untuk render sementara
        for x, y in current_piece.cells():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                grid[y][x] = current_piece.color

        draw_window(window, grid, score, high_score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        # Kunci piece jika perlu
        if change_piece:
            for pos in current_piece.cells():
                x, y = pos
                if y < 0:
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Clear lines
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                # skor standar Tetris sederhana
                points_map = {1: 40, 2: 100, 3: 300, 4: 1200}
                score += points_map.get(cleared, cleared * 50)
                lines_cleared_since_speed += cleared
                # percepat
                if lines_cleared_since_speed >= level_up_every:
                    fall_speed = max(0.1, fall_speed * 0.9)
                    lines_cleared_since_speed -= level_up_every

            if score > high_score:
                high_score = score

            # Cek kalah
            if check_lost(locked_positions):
                run = False

    # Game over render
    draw_window(window, grid, score, high_score)
    draw_text_middle(window, 'GAME OVER', 48, WHITE)
    pygame.display.update()
    pygame.time.delay(1500)


def main_menu():
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')

    run = True
    clock = pygame.time.Clock()
    blink_time = 0

    while run:
        window.fill((25, 25, 30))
        draw_text_middle(window, 'TETRIS', 64, WHITE)
        font = pygame.font.SysFont('arial', 22)
        label = font.render('Press ENTER to Start | ESC to Quit', True, WHITE)
        window.blit(label, (PLAY_WIDTH // 2 - label.get_width() // 2, PLAY_HEIGHT // 2 + 60))

        blink_time += clock.tick(60) / 1000.0
        if int(blink_time * 2) % 2 == 0:
            small = pygame.font.SysFont('arial', 18)
            tip = small.render('Controls: Arrow Keys / Space / Esc', True, LIGHT_GREY)
            window.blit(tip, (PLAY_WIDTH // 2 - tip.get_width() // 2, PLAY_HEIGHT // 2 + 100))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(window)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)


if __name__ == '__main__':
    main_menu()
