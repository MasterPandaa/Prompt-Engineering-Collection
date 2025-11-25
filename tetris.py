import pygame
import random
import sys

# -------------------------
# Konfigurasi dasar
# -------------------------
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # ukuran pixel per blok

PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE

SIDE_PANEL_WIDTH = 200
TOP_MARGIN = 0

WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT + TOP_MARGIN

# Kecepatan jatuh (dalam detik per satu langkah ke bawah)
INITIAL_FALL_SPEED = 0.6
SOFT_DROP_MULTIPLIER = 10  # soft drop lebih cepat ~10x

# Skor untuk garis yang dibersihkan
SCORE_TABLE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800,
}

# Warna
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (220, 220, 220)
BORDER = (80, 80, 80)

# Definisi bentuk Tetromino (dalam grid 4x4) per rotasi
# Koordinat blok aktif ditandai dengan '1'
# Masing-masing bentuk memiliki daftar rotasi
SHAPES = {
    'I': [
        [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
        ],
    ],
    'O': [
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'T': [
        [
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'S': [
        [
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'Z': [
        [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'J': [
        [
            [1, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'L': [
        [
            [0, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
}

# Warna unik untuk setiap shape
SHAPE_COLORS = {
    'I': (0, 240, 240),   # Cyan
    'O': (240, 240, 0),   # Yellow
    'T': (160, 0, 240),   # Purple
    'S': (0, 240, 0),     # Green
    'Z': (240, 0, 0),     # Red
    'J': (0, 0, 240),     # Blue
    'L': (240, 160, 0),   # Orange
}

ALL_SHAPES = list(SHAPES.keys())

class Piece:
    def __init__(self, x, y, shape_key):
        self.x = x  # kolom pada grid
        self.y = y  # baris pada grid
        self.shape_key = shape_key
        self.rot = 0  # indeks rotasi
        self.color = SHAPE_COLORS[shape_key]

    @property
    def shape(self):
        return SHAPES[self.shape_key][self.rot % len(SHAPES[self.shape_key])]


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape = piece.shape
    for i in range(4):
        for j in range(4):
            if shape[i][j] == 1:
                positions.append((piece.x + j, piece.y + i))
    return positions


def valid_space(piece, grid):
    accepted_positions = {(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == BLACK}
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    for (_, y) in locked_positions:
        if y < 1:
            return True
    return False


def get_new_piece():
    shape_key = random.choice(ALL_SHAPES)
    # Spawn di atas tengah: x = tengah - 2 (karena grid 4x4)
    x = COLS // 2 - 2
    y = 0
    return Piece(x, y, shape_key)


def clear_rows(grid, locked):
    lines_cleared = 0
    # dari bawah ke atas
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            lines_cleared += 1
            # Hapus tiap posisi pada baris ini dari locked
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            # Turunkan semua posisi di atas
            locked_copy = sorted(list(locked), key=lambda x: x[1])
            for x, y in locked_copy[::-1]:
                if y < i:
                    color = locked[(x, y)]
                    del locked[(x, y)]
                    locked[(x, y + 1)] = color
    return lines_cleared


def draw_grid_lines(surface):
    # Garis vertikal
    for x in range(COLS + 1):
        pygame.draw.line(surface, BORDER, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, PLAY_HEIGHT))
    # Garis horizontal
    for y in range(ROWS + 1):
        pygame.draw.line(surface, BORDER, (0, y * BLOCK_SIZE), (PLAY_WIDTH, y * BLOCK_SIZE))


def draw_window(surface, grid, score, next_piece):
    surface.fill(GRAY)

    # Area permainan (grid)
    play_surface = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT))
    play_surface.fill(BLACK)

    # Gambar blok di grid
    for i in range(ROWS):
        for j in range(COLS):
            color = grid[i][j]
            if color != BLACK:
                pygame.draw.rect(play_surface, color, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                # outline tipis
                pygame.draw.rect(play_surface, (30, 30, 30), (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    draw_grid_lines(play_surface)
    surface.blit(play_surface, (0, TOP_MARGIN))

    # Panel samping
    panel_x = PLAY_WIDTH + 10
    panel_y = 10
    font = pygame.font.SysFont('consolas', 22)
    title = font.render('Next:', True, WHITE)
    surface.blit(title, (panel_x, panel_y))

    # Gambar next piece
    draw_next(surface, next_piece, panel_x, panel_y + 30)

    # Score
    score_text = font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_text, (panel_x, panel_y + 150))

    # Bantuan kontrol
    small = pygame.font.SysFont('consolas', 16)
    controls = [
        'Controls:',
        'Left/Right: Move',
        'Up: Rotate',
        'Down: Soft drop',
        'Space: Hard drop',
        'Esc: Quit'
    ]
    for idx, line in enumerate(controls):
        txt = small.render(line, True, WHITE)
        surface.blit(txt, (panel_x, panel_y + 200 + idx * 20))


def draw_next(surface, piece, x, y):
    if not piece:
        return
    shape = SHAPES[piece.shape_key][0]  # tampilkan rotasi awal
    # Cari bounding box aktif agar bisa di-center
    min_x = min_y = 10
    max_x = max_y = -1
    for i in range(4):
        for j in range(4):
            if shape[i][j] == 1:
                min_y = min(min_y, i)
                min_x = min(min_x, j)
                max_y = max(max_y, i)
                max_x = max(max_x, j)
    width = (max_x - min_x + 1) * BLOCK_SIZE
    height = (max_y - min_y + 1) * BLOCK_SIZE

    offset_x = x + (SIDE_PANEL_WIDTH - 20 - width) // 2
    offset_y = y + (120 - height) // 2

    # background box
    pygame.draw.rect(surface, (20, 20, 20), (x - 5, y - 5, SIDE_PANEL_WIDTH - 20, 130), border_radius=8)

    for i in range(4):
        for j in range(4):
            if shape[i][j] == 1:
                pygame.draw.rect(surface, piece.color,
                                  (offset_x + (j - min_x) * BLOCK_SIZE,
                                   offset_y + (i - min_y) * BLOCK_SIZE,
                                   BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, (30, 30, 30),
                                  (offset_x + (j - min_x) * BLOCK_SIZE,
                                   offset_y + (i - min_y) * BLOCK_SIZE,
                                   BLOCK_SIZE, BLOCK_SIZE), 1)


def hard_drop(piece, grid, locked):
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break
    # lock
    for x, y in convert_shape_format(piece):
        if y >= 0:
            locked[(x, y)] = piece.color
    return True  # menandakan sudah di-lock


def lock_piece(piece, grid, locked):
    for x, y in convert_shape_format(piece):
        if y >= 0:
            locked[(x, y)] = piece.color


def rotate_piece(piece, grid):
    old_rot = piece.rot
    piece.rot = (piece.rot + 1) % len(SHAPES[piece.shape_key])
    if not valid_space(piece, grid):
        # coba wall kick sederhana: geser kiri/kanan 1 kolom
        piece.x += 1
        if not valid_space(piece, grid):
            piece.x -= 2
            if not valid_space(piece, grid):
                # gagal, revert
                piece.x += 1
                piece.rot = old_rot


def main():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    fall_time = 0.0
    fall_speed = INITIAL_FALL_SPEED

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_piece()
    next_piece = get_new_piece()

    score = 0
    running = True
    game_over = False

    # Timer berbasis waktu nyata
    last_fall_update = pygame.time.get_ticks() / 1000.0

    while running:
        dt = clock.tick(60) / 1000.0  # detik/frame
        current_time = pygame.time.get_ticks() / 1000.0

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        # soft drop satu langkah
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        rotate_piece(current_piece, grid)
                    elif event.key == pygame.K_SPACE:
                        # hard drop
                        hard_drop(current_piece, grid, locked_positions)
                        # generate piece baru
                        lines = clear_rows(grid, locked_positions)
                        if lines > 0:
                            score += SCORE_TABLE.get(lines, 0)
                        current_piece = next_piece
                        next_piece = get_new_piece()
                        if not valid_space(current_piece, grid):
                            game_over = True

        if game_over:
            # Tampilkan Game Over
            draw_window(screen, grid, score, next_piece)
            font = pygame.font.SysFont('consolas', 36)
            text = font.render('GAME OVER', True, WHITE)
            screen.blit(text, (PLAY_WIDTH // 2 - text.get_width() // 2, PLAY_HEIGHT // 2 - 60))
            small = pygame.font.SysFont('consolas', 20)
            hint = small.render('Press Esc to quit', True, WHITE)
            screen.blit(hint, (PLAY_WIDTH // 2 - hint.get_width() // 2, PLAY_HEIGHT // 2 - 20))
            pygame.display.flip()
            continue

        # Perbarui jatuh otomatis
        # Soft drop ketika tombol bawah ditekan dan ditahan
        keys = pygame.key.get_pressed()
        multiplier = SOFT_DROP_MULTIPLIER if keys[pygame.K_DOWN] else 1
        fall_interval = fall_speed / multiplier

        if (current_time - last_fall_update) > fall_interval:
            last_fall_update = current_time
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                # lock piece
                lock_piece(current_piece, grid, locked_positions)
                # generate piece baru
                lines = clear_rows(grid, locked_positions)
                if lines > 0:
                    score += SCORE_TABLE.get(lines, 0)
                current_piece = next_piece
                next_piece = get_new_piece()
                # cek game over
                if not valid_space(current_piece, grid):
                    game_over = True

        grid = create_grid(locked_positions)
        # Gambar current piece di grid sementara
        for x, y in convert_shape_format(current_piece):
            if y >= 0:
                if 0 <= x < COLS and 0 <= y < ROWS:
                    grid[y][x] = current_piece.color

        # Render
        draw_window(screen, grid, score, next_piece)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
