import pygame
import random
import sys

# ----- Konstanta Game -----
WIN_COLS = 10
WIN_ROWS = 20
BLOCK_SIZE = 30
PLAY_WIDTH = WIN_COLS * BLOCK_SIZE
PLAY_HEIGHT = WIN_ROWS * BLOCK_SIZE
SIDE_PANEL = 200
TOP_MARGIN = 60

WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL
WINDOW_HEIGHT = PLAY_HEIGHT + TOP_MARGIN

# Kecepatan jatuh (detik per sel)
INITIAL_FALL_SPEED = 0.6
SOFT_DROP_MULTIPLIER = 8.0  # panah bawah mempercepat jatuh

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (120, 120, 120)

# Warna untuk setiap bentuk
COLORS = {
    'I': (0, 240, 240),     # Cyan
    'O': (240, 240, 0),     # Yellow
    'T': (160, 0, 240),     # Purple
    'S': (0, 240, 0),       # Green
    'Z': (240, 0, 0),       # Red
    'J': (0, 0, 240),       # Blue
    'L': (240, 160, 0),     # Orange
}

# Definisi bentuk (dalam grid 4x4, tiap rotasi)
# Menggunakan format list string 4 baris x 4 kolom, '0' = blok, '.' = kosong
SHAPES = {
    'S': [
        ['.0..', '.00.', '..0.', '....'],
        ['..00', '.00.', '....', '....'],
        ['.0..', '.00.', '..0.', '....'],
        ['..00', '.00.', '....', '....'],
    ],
    'Z': [
        ['..0.', '.00.', '.0..', '....'],
        ['.00.', '..00', '....', '....'],
        ['..0.', '.00.', '.0..', '....'],
        ['.00.', '..00', '....', '....'],
    ],
    'I': [
        ['....', '0000', '....', '....'],
        ['..0.', '..0.', '..0.', '..0.'],
        ['....', '0000', '....', '....'],
        ['..0.', '..0.', '..0.', '..0.'],
    ],
    'O': [
        ['.00.', '.00.', '....', '....'],
        ['.00.', '.00.', '....', '....'],
        ['.00.', '.00.', '....', '....'],
        ['.00.', '.00.', '....', '....'],
    ],
    'J': [
        ['0...', '000.', '....', '....'],
        ['.00.', '.0..', '.0..', '....'],
        ['....', '000.', '..0.', '....'],
        ['.0..', '.0..', '00..', '....'],
    ],
    'L': [
        ['..0.', '000.', '....', '....'],
        ['.0..', '.0..', '.00.', '....'],
        ['....', '000.', '0...', '....'],
        ['00..', '.0..', '.0..', '....'],
    ],
    'T': [
        ['.0..', '000.', '....', '....'],
        ['.0..', '.00.', '.0..', '....'],
        ['....', '000.', '.0..', '....'],
        ['.0..', '00..', '.0..', '....'],
    ],
}

PIECES = list(SHAPES.keys())

class Piece:
    def __init__(self, x, y, shape_key):
        self.x = x  # kolom grid
        self.y = y  # baris grid
        self.shape_key = shape_key
        self.rotation = 0
        self.color = COLORS[shape_key]

    @property
    def shape(self):
        return SHAPES[self.shape_key][self.rotation % len(SHAPES[self.shape_key])]


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(WIN_COLS)] for _ in range(WIN_ROWS)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape_matrix = piece.shape
    for i in range(4):
        for j in range(4):
            if shape_matrix[i][j] == '0':
                positions.append((piece.x + j - 1, piece.y + i - 2))
    return positions


def valid_space(piece, grid):
    accepted_positions = {(j, i) for i in range(WIN_ROWS) for j in range(WIN_COLS) if grid[i][j] == BLACK}
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        if x < 0 or x >= WIN_COLS or y >= WIN_ROWS:
            return False
        if y >= 0 and (x, y) not in accepted_positions:
            return False
    return True


def check_lost(positions):
    for (_, y) in positions:
        if y < 0:
            return True
    return False


def get_new_piece():
    shape_key = random.choice(PIECES)
    # spawn di tengah (kolom 5 kira-kira), sedikit di atas layar (y negatif agar bisa turun)
    return Piece(x=WIN_COLS // 2 - 1, y=0, shape_key=shape_key)


def clear_rows(grid, locked):
    rows_cleared = 0
    for i in range(WIN_ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            rows_cleared += 1
            # hapus semua posisi di baris ini dari locked
            for j in range(WIN_COLS):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            # geser turun yg di atasnya
            for (x, y) in sorted(list(locked.keys()), key=lambda t: t[1]):
                if y < i:
                    color = locked[(x, y)]
                    del locked[(x, y)]
                    locked[(x, y + 1)] = color
    return rows_cleared


def draw_grid_lines(surface):
    # garis vertikal
    for x in range(WIN_COLS + 1):
        pygame.draw.line(
            surface, LIGHT_GRAY,
            (x * BLOCK_SIZE, TOP_MARGIN),
            (x * BLOCK_SIZE, TOP_MARGIN + PLAY_HEIGHT), 1)
    # garis horizontal
    for y in range(WIN_ROWS + 1):
        pygame.draw.line(
            surface, LIGHT_GRAY,
            (0, TOP_MARGIN + y * BLOCK_SIZE),
            (PLAY_WIDTH, TOP_MARGIN + y * BLOCK_SIZE), 1)


def draw_window(surface, grid, score, next_piece):
    surface.fill(GRAY)

    # Judul
    font_title = pygame.font.SysFont('arial', 28, bold=True)
    label = font_title.render('TETRIS', True, WHITE)
    surface.blit(label, (10, 15))

    # Skor
    font_info = pygame.font.SysFont('arial', 20)
    score_label = font_info.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (PLAY_WIDTH + 20, TOP_MARGIN))

    # Next piece
    np_label = font_info.render('Next:', True, WHITE)
    surface.blit(np_label, (PLAY_WIDTH + 20, TOP_MARGIN + 40))

    # Gambar grid terisi
    for y in range(WIN_ROWS):
        for x in range(WIN_COLS):
            rect = pygame.Rect(x * BLOCK_SIZE, TOP_MARGIN + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, grid[y][x], rect)

    # Grid lines
    draw_grid_lines(surface)

    # Panel kanan - next piece preview
    draw_next_piece(surface, next_piece)

    # Border playfield
    pygame.draw.rect(surface, WHITE, (0, TOP_MARGIN, PLAY_WIDTH, PLAY_HEIGHT), 2)


def draw_next_piece(surface, next_piece):
    if not next_piece:
        return
    # Render di panel kanan
    offset_x = PLAY_WIDTH + 20
    offset_y = TOP_MARGIN + 70
    for i in range(4):
        for j in range(4):
            if next_piece.shape[i][j] == '0':
                rx = offset_x + (j - 1) * BLOCK_SIZE
                ry = offset_y + (i - 2) * BLOCK_SIZE
                pygame.draw.rect(surface, next_piece.color, (rx, ry, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, WHITE, (rx, ry, BLOCK_SIZE, BLOCK_SIZE), 2)


def hard_drop(piece, grid, locked):
    # Turunkan hingga tidak valid lalu naik satu
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break
    # Kunci di posisi ini
    for x, y in convert_shape_format(piece):
        if y >= 0:
            locked[(x, y)] = piece.color
    return True  # locked


def calculate_score(lines):
    # Skor sederhana: 1=100, 2=300, 3=500, 4=800
    if lines == 1:
        return 100
    if lines == 2:
        return 300
    if lines == 3:
        return 500
    if lines >= 4:
        return 800
    return 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris - Python + Pygame')

    clock = pygame.time.Clock()
    fall_speed = INITIAL_FALL_SPEED
    fall_time = 0.0

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_piece()
    next_piece = get_new_piece()

    score = 0
    running = true_game = True

    # Teks bantuan
    font_info = pygame.font.SysFont('arial', 18)

    while running:
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % 4
                    # Sederhana: wall kick ringan
                    kicked = False
                    for dx in [0, -1, 1, -2, 2]:
                        current_piece.x += dx
                        if valid_space(current_piece, grid):
                            kicked = True
                            break
                        current_piece.x -= dx
                    if not kicked:
                        current_piece.rotation = prev_rot
                elif event.key == pygame.K_DOWN:
                    # Soft drop satu langkah
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    hard_drop(current_piece, grid, locked_positions)
                    # Spawn baru
                    current_piece = next_piece
                    next_piece = get_new_piece()
                    grid = create_grid(locked_positions)
                    # Bersihkan baris dan skor
                    cleared = clear_rows(grid, locked_positions)
                    if cleared:
                        score += calculate_score(cleared)
                    # Cek game over jika bidak baru langsung tidak valid
                    grid = create_grid(locked_positions)
                    if not valid_space(current_piece, grid):
                        true_game = False

        # Gravitasi
        speed = fall_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            speed = fall_speed / SOFT_DROP_MULTIPLIER
        if fall_time >= speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                # Kunci
                for x, y in convert_shape_format(current_piece):
                    if y >= 0:
                        locked_positions[(x, y)] = current_piece.color
                # Spawn baru
                current_piece = next_piece
                next_piece = get_new_piece()
                # Update grid + clear rows
                grid = create_grid(locked_positions)
                cleared = clear_rows(grid, locked_positions)
                if cleared:
                    score += calculate_score(cleared)

                # Game over
                # Jika locked menyentuh di atas atau bidak baru langsung tidak valid
                if check_lost(locked_positions):
                    true_game = False
                else:
                    grid = create_grid(locked_positions)
                    if not valid_space(current_piece, grid):
                        true_game = False

        grid = create_grid(locked_positions)
        # Tambahkan current piece ke grid sementara untuk digambar
        for x, y in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color

        draw_window(screen, grid, score, next_piece)
        # Bantuan kontrol
        help_lines = [
            'Controls:',
            'Left/Right: Move',
            'Up: Rotate',
            'Down: Soft Drop',
            'SPACE: Hard Drop',
            'ESC: Quit'
        ]
        for i, text in enumerate(help_lines):
            lbl = font_info.render(text, True, WHITE)
            screen.blit(lbl, (PLAY_WIDTH + 20, TOP_MARGIN + 160 + i * 20))

        pygame.display.flip()

        if not true_game:
            game_over(screen, score)
            running = False

    pygame.quit()
    sys.exit(0)


def game_over(surface, score):
    surface.fill(BLACK)
    font_big = pygame.font.SysFont('arial', 42, bold=True)
    font_small = pygame.font.SysFont('arial', 24)

    over = font_big.render('GAME OVER', True, WHITE)
    s = font_small.render(f'Final Score: {score}', True, WHITE)
    info = font_small.render('Press any key to exit...', True, WHITE)

    surface.blit(over, (PLAY_WIDTH // 2 - over.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
    surface.blit(s, (PLAY_WIDTH // 2 - s.get_width() // 2, WINDOW_HEIGHT // 2 - 30))
    surface.blit(info, (PLAY_WIDTH // 2 - info.get_width() // 2, WINDOW_HEIGHT // 2 + 10))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        pygame.time.wait(10)


if __name__ == '__main__':
    main()
