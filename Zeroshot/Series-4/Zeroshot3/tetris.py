import pygame
import random
import sys

# ============================================
# Konfigurasi Game
# ============================================
COLS = 10
ROWS = 20
BLOCK_SIZE = 30
PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE
SIDEBAR_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT
FPS = 60

# Skor line clear (SESUAi Tetris guideline sederhana)
LINE_CLEAR_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (30, 30, 30)
LIGHT_GREY = (80, 80, 80)

# Warna untuk 7 tetromino (I, O, T, S, Z, J, L)
COLORS = {
    'I': (0, 240, 240),   # Cyan
    'O': (240, 240, 0),   # Yellow
    'T': (160, 0, 240),   # Purple
    'S': (0, 240, 0),     # Green
    'Z': (240, 0, 0),     # Red
    'J': (0, 0, 240),     # Blue
    'L': (240, 160, 0),   # Orange
}

# Bentuk tetromino ditulis sebagai rotasi 4x4 grid (string)
# Menggunakan representasi umum: '.' kosong, 'X' terisi
SHAPES = {
    'S': [
        [
            '....',
            '..XX',
            '.XX.',
            '....',
        ],
        [
            '....',
            '.X..',
            '.XX.',
            '..X.',
        ],
    ],
    'Z': [
        [
            '....',
            '.XX.',
            '..XX',
            '....',
        ],
        [
            '....',
            '..X.',
            '.XX.',
            '.X..',
        ],
    ],
    'I': [
        [
            '....',
            'XXXX',
            '....',
            '....',
        ],
        [
            '..X.',
            '..X.',
            '..X.',
            '..X.',
        ],
    ],
    'O': [
        [
            '....',
            '.XX.',
            '.XX.',
            '....',
        ],
    ],
    'T': [
        [
            '....',
            '.XXX',
            '..X.',
            '....',
        ],
        [
            '....',
            '..X.',
            '.XX.',
            '..X.',
        ],
        [
            '....',
            '..X.',
            '.XXX',
            '....',
        ],
        [
            '....',
            '..X.',
            '..XX',
            '..X.',
        ],
    ],
    'J': [
        [
            '....',
            '.XXX',
            '.X..',
            '....',
        ],
        [
            '....',
            '.XX.',
            '..X.',
            '..X.',
        ],
        [
            '....',
            '..X.',
            '.XXX',
            '....',
        ],
        [
            '....',
            '..X.',
            '..X.',
            '.XX.',
        ],
    ],
    'L': [
        [
            '....',
            '.XXX',
            '...X',
            '....',
        ],
        [
            '....',
            '..X.',
            '..X.',
            '.XX.',
        ],
        [
            '....',
            '.X..',
            '.XXX',
            '....',
        ],
        [
            '....',
            '.XX.',
            '.X..',
            '.X..',
        ],
    ],
}

class Piece:
    def __init__(self, x, y, shape_key):
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.shape = SHAPES[shape_key]
        self.color = COLORS[shape_key]
        self.rotation = 0  # index rotasi

    def get_formatted_coords(self):
        # Konversi bentuk string 4x4 ke koordinat grid berdasarkan x,y saat ini
        positions = []
        format = self.shape[self.rotation % len(self.shape)]
        for i, line in enumerate(format):
            for j, char in enumerate(line):
                if char == 'X':
                    positions.append((self.x + j - 1, self.y + i - 2))
        return positions


def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def valid_space(piece, grid):
    accepted_positions = [(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == BLACK]
    formatted = piece.get_formatted_coords()
    for x, y in formatted:
        if y < 0:
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    for (x, y) in locked_positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(COLS // 2 - 2, 0, random.choice(list(SHAPES.keys())))


def draw_grid(surface, grid):
    # area permainan
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, grid[y][x], rect)
            pygame.draw.rect(surface, LIGHT_GREY, rect, 1)


def clear_rows(grid, locked):
    # Menghapus baris penuh dan geser turun
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            # Hapus posisi pada baris y
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # Geser turun baris di atas y
            for (x, y2) in sorted(list(locked.keys()), key=lambda p: p[1]):
                if y2 < y:
                    color = locked.pop((x, y2))
                    locked[(x, y2 + 1)] = color
    return cleared


def draw_next_piece(surface, piece, font):
    label = font.render('Next:', True, WHITE)
    surface.blit(label, (PLAY_WIDTH + 20, 20))
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == 'X':
                rect = pygame.Rect(PLAY_WIDTH + 20 + j * 20, 60 + i * 20, 20, 20)
                pygame.draw.rect(surface, piece.color, rect)
                pygame.draw.rect(surface, LIGHT_GREY, rect, 1)


def draw_text_right(surface, text, y, font, color=WHITE):
    label = font.render(text, True, color)
    surface.blit(label, (PLAY_WIDTH + 20, y))


def hard_drop(piece, grid):
    # Mengembalikan langkah turun yang dilakukan
    steps = 0
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break
        steps += 1
    return steps


def draw_window(surface, grid, score, high_score, next_piece):
    surface.fill(GREY)
    # area permainan background
    play_rect = pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT)
    pygame.draw.rect(surface, BLACK, play_rect)

    draw_grid(surface, grid)

    # Sidebar info
    font_title = pygame.font.SysFont('arial', 28, bold=True)
    font_info = pygame.font.SysFont('arial', 22)

    title = font_title.render('TETRIS', True, WHITE)
    surface.blit(title, (PLAY_WIDTH + 20, WINDOW_HEIGHT - 50))

    draw_text_right(surface, f'Score: {score}', 220, font_info)
    draw_text_right(surface, f'High:  {high_score}', 250, font_info)

    draw_next_piece(surface, next_piece, font_info)

    # border
    pygame.draw.rect(surface, LIGHT_GREY, play_rect, 2)


def main():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    locked_positions = {}  # (x,y) -> color
    grid = create_grid(locked_positions)

    change_piece = False
    run = True

    current_piece = get_shape()
    next_piece = get_shape()

    fall_time = 0
    fall_speed = 0.5  # detik per langkah jatuh
    level_time = 0

    score = 0
    high_score = 0

    soft_drop_active = False

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt
        level_time += dt

        # Tingkatkan kecepatan seiring waktu (opsional sederhana)
        if level_time > 60:
            level_time = 0
            fall_speed = max(0.1, fall_speed - 0.05)

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
                    # soft drop satu langkah dan aktifkan percepatan
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                    soft_drop_active = True
                elif event.key == pygame.K_UP:
                    # rotasi
                    prev_rotation = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # coba wall-kick sederhana: geser kiri/kanan 1
                        kicked = False
                        for dx in (-1, 1, -2, 2):
                            current_piece.x += dx
                            if valid_space(current_piece, grid):
                                kicked = True
                                break
                            current_piece.x -= dx
                        if not kicked:
                            current_piece.rotation = prev_rotation
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    hard_drop(current_piece, grid)
                    change_piece = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop_active = False

        # Otomatis jatuh
        speed = fall_speed * (0.25 if soft_drop_active else 1.0)
        if fall_time > speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Tambahkan piece ke grid jika terkunci
        shape_pos = current_piece.get_formatted_coords()
        for x, y in shape_pos:
            if y >= 0:
                try:
                    grid[y][x] = current_piece.color
                except IndexError:
                    # Out of bounds: akan ditangani oleh valid_space saat change_piece
                    pass

        if change_piece:
            for x, y in shape_pos:
                if y < 0:
                    # langsung game over
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                score += LINE_CLEAR_SCORES.get(cleared, 0)
                high_score = max(high_score, score)
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Cek lost
            if check_lost(locked_positions):
                run = False

        draw_window(surface, grid, score, high_score, next_piece)
        pygame.display.update()

    game_over(surface, score)


def game_over(surface, score):
    font_big = pygame.font.SysFont('arial', 42, bold=True)
    font_small = pygame.font.SysFont('arial', 24)
    surface.fill(BLACK)
    over_text = font_big.render('GAME OVER', True, WHITE)
    score_text = font_small.render(f'Score: {score}', True, WHITE)
    info_text = font_small.render('Press R to Restart or Q to Quit', True, WHITE)

    surface.blit(over_text, (PLAY_WIDTH // 2 - over_text.get_width() // 2, PLAY_HEIGHT // 2 - 80))
    surface.blit(score_text, (PLAY_WIDTH // 2 - score_text.get_width() // 2, PLAY_HEIGHT // 2 - 20))
    surface.blit(info_text, (PLAY_WIDTH // 2 - info_text.get_width() // 2, PLAY_HEIGHT // 2 + 30))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    waiting = False
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    waiting = False
                    main()
        pygame.time.wait(100)


if __name__ == '__main__':
    main()
