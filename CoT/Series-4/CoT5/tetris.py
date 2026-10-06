import pygame
import random
import sys

# Konfigurasi dasar
pygame.init()

# Ukuran grid Tetris standar: 10 kolom x 20 baris
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # ukuran satu kotak piksel

# Area permainan (playfield) akan digambar di tengah
PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE

# Dimensi jendela keseluruhan (tambahkan panel samping untuk next/score)
SIDE_PANEL_WIDTH = 200
TOP_MARGIN = 50
WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
HEIGHT = PLAY_HEIGHT + TOP_MARGIN

# Posisi top-left area permainan
PLAY_X = 20
PLAY_Y = TOP_MARGIN

# Warna-warna
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (60, 60, 60)
LIGHT_GRAY = (100, 100, 100)

# Bentuk-bentuk Tetris (Tetrimino) dalam bentuk matrix string 4x4
# Setiap bentuk memiliki daftar rotasi.
S = [['.S..',
      '.S..',
      'SS..',
      '....'],
     ['S...',
      'SS..',
      '.S..',
      '....']]

Z = [['.Z..',
      '.Z..',
      'ZZ..',
      '....'],
     ['.Z..',
      'ZZ..',
      'Z...',
      '....']]

I = [['.I..',
      '.I..',
      '.I..',
      '.I..'],
     ['IIII',
      '....',
      '....',
      '....']]

O = [['OO..',
      'OO..',
      '....',
      '....']]

J = [['J...',
      'JJJ.',
      '....',
      '....'],
     ['.JJ.',
      '.J..',
      '.J..',
      '....'],
     ['....',
      'JJJ.',
      '..J.',
      '....'],
     ['.J..',
      '.J..',
      'JJ..',
      '....']]

L = [['..L.',
      'LLL.',
      '....',
      '....'],
     ['.L..',
      '.L..',
      '.LL.',
      '....'],
     ['....',
      'LLL.',
      'L...',
      '....'],
     ['LL..',
      '.L..',
      '.L..',
      '....']]

T = [['.T..',
      'TTT.',
      '....',
      '....'],
     ['.T..',
      '.TT.',
      '.T..',
      '....'],
     ['....',
      'TTT.',
      '.T..',
      '....'],
     ['.T..',
      'TT..',
      '.T..',
      '....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = {
    'S': (48, 190, 120),
    'Z': (220, 60, 80),
    'I': (80, 200, 220),
    'O': (240, 200, 80),
    'J': (80, 120, 220),
    'L': (240, 160, 60),
    'T': (180, 80, 190),
}

FONT_NAME = pygame.font.get_default_font()
FONT_SMALL = pygame.font.SysFont(FONT_NAME, 18)
FONT_MED = pygame.font.SysFont(FONT_NAME, 24, bold=True)
FONT_BIG = pygame.font.SysFont(FONT_NAME, 36, bold=True)


class Piece:
    """Class yang merepresentasikan bidak yang sedang jatuh."""
    def __init__(self, x, y, shape):
        self.x = x  # posisi dalam koordinat grid (kolom)
        self.y = y  # posisi dalam koordinat grid (baris)
        self.shape = shape  # salah satu dari SHAPES (list rotasi)
        self.rotation = 0  # indeks rotasi saat ini
        # Tentukan huruf dari bentuk dengan melihat rotasi pertama
        self.kind = self._detect_kind()
        self.color = SHAPE_COLORS[self.kind]

    def _detect_kind(self):
        # Ambil karakter huruf pertama yang bukan '.' dari rotasi awal
        for row in self.shape[0]:
            for ch in row:
                if ch != '.' and ch != ' ':
                    return ch
        return 'X'

    def image(self):
        """Kembalikan matriks string 4x4 dari rotasi saat ini."""
        return self.shape[self.rotation % len(self.shape)]

    def rotated(self):
        """Kembalikan objek Piece baru dengan rotasi +1 (tidak memodifikasi state)."""
        new = Piece(self.x, self.y, self.shape)
        new.rotation = (self.rotation + 1) % len(self.shape)
        return new


def create_grid(locked_positions):
    """Buat grid warna untuk rendering; None berarti kosong."""
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    """Ubah matriks 4x4 shape menjadi daftar posisi (x, y) di grid relatif ke piece.x/y."""
    positions = []
    image = piece.image()
    for i, row in enumerate(image):
        for j, ch in enumerate(row):
            if ch != '.' and ch != ' ':
                positions.append((piece.x + j, piece.y + i))
    return positions


def valid_space(piece, locked):
    """Cek apakah semua sel piece berada di dalam grid dan tidak bertabrakan dengan yang terkunci."""
    accepted_positions = [(x, y) for y in range(ROWS) for x in range(COLS) if (x, y) not in locked]
    for (x, y) in convert_shape_format(piece):
        if y < 0:
            # di atas layar masih dianggap valid (spawn)
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked_positions):
    """Kalah jika ada blok terkunci di atas baris 0 (y < 1)."""
    for (x, y) in locked_positions.keys():
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(3, -2, random.choice(SHAPES))


def clear_rows(grid, locked):
    """Hapus baris penuh dan turunkan baris di atasnya. Kembalikan jumlah baris yang dihapus."""
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if all(grid[y][x] is not None for x in range(COLS)):
            cleared += 1
            # hapus semua posisi pada baris y
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # Turunkan baris di atas
            for (lx, ly) in sorted(list(locked.keys()), key=lambda k: k[1]):
                if ly < y:
                    color = locked[(lx, ly)]
                    del locked[(lx, ly)]
                    locked[(lx, ly + 1)] = color
            # setelah menurunkan satu baris, cek baris ini lagi pada loop berikutnya
    return cleared


def draw_grid(surface, grid):
    # background playfield
    pygame.draw.rect(surface, BLACK, (PLAY_X - 2, PLAY_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), border_radius=6)
    pygame.draw.rect(surface, GRAY, (PLAY_X, PLAY_Y, PLAY_WIDTH, PLAY_HEIGHT))

    # gambar blok
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color:
                rect = (PLAY_X + x * BLOCK_SIZE, PLAY_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, 2)

    # garis grid tipis
    for x in range(COLS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (PLAY_X + x * BLOCK_SIZE, PLAY_Y), (PLAY_X + x * BLOCK_SIZE, PLAY_Y + PLAY_HEIGHT), 1)
    for y in range(ROWS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (PLAY_X, PLAY_Y + y * BLOCK_SIZE), (PLAY_X + PLAY_WIDTH, PLAY_Y + y * BLOCK_SIZE), 1)


def draw_next(surface, piece):
    label = FONT_MED.render('Next', True, WHITE)
    surface.blit(label, (PLAY_X + PLAY_WIDTH + 20, PLAY_Y))

    image = piece.image()
    # Gambar di area samping
    start_x = PLAY_X + PLAY_WIDTH + 20
    start_y = PLAY_Y + 40
    for i, row in enumerate(image):
        for j, ch in enumerate(row):
            if ch != '.' and ch != ' ':
                rect = (start_x + j * BLOCK_SIZE, start_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 2)


def draw_text_right(surface, text, y):
    label = FONT_SMALL.render(text, True, WHITE)
    surface.blit(label, (PLAY_X + PLAY_WIDTH + 20, y))


def draw_window(surface, grid, score, lines, level, next_piece):
    surface.fill((30, 30, 35))

    # Judul
    title = FONT_BIG.render('TETRIS', True, WHITE)
    surface.blit(title, (PLAY_X + PLAY_WIDTH // 2 - title.get_width() // 2, 10))

    # Playfield dan grid
    draw_grid(surface, grid)

    # Panel samping
    draw_next(surface, next_piece)
    draw_text_right(surface, f'Score: {score}', PLAY_Y + 220)
    draw_text_right(surface, f'Lines: {lines}', PLAY_Y + 250)
    draw_text_right(surface, f'Level: {level}', PLAY_Y + 280)
    draw_text_right(surface, 'Controls:', PLAY_Y + 330)
    draw_text_right(surface, '- Left/Right: Geser', PLAY_Y + 355)
    draw_text_right(surface, '- Up: Rotasi', PLAY_Y + 375)
    draw_text_right(surface, '- Down: Turun cepat', PLAY_Y + 395)
    draw_text_right(surface, '- Space: Hard drop', PLAY_Y + 415)
    draw_text_right(surface, '- P: Pause', PLAY_Y + 435)

    pygame.display.update()


def hard_drop(piece, locked):
    # Jatuhkan hingga tidak valid
    while True:
        piece.y += 1
        if not valid_space(piece, locked):
            piece.y -= 1
            break


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per langkah turun

    score = 0
    lines = 0

    run = True
    paused = False
    last_move_sideways = 0
    DAS = 0.1  # simple delay untuk input berulang kiri/kanan

    while run:
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, locked_positions):
                        current_piece.x += 1
                    last_move_sideways = 0
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, locked_positions):
                        current_piece.x -= 1
                    last_move_sideways = 0
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, locked_positions):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    rotated = current_piece.rotated()
                    # wall kick sederhana: coba offset -1, +1 jika nabrak
                    kicked = False
                    for dx in [0, -1, 1, -2, 2]:
                        test = Piece(current_piece.x + dx, current_piece.y, current_piece.shape)
                        test.rotation = rotated.rotation
                        if valid_space(test, locked_positions):
                            current_piece = test
                            kicked = True
                            break
                    if not kicked:
                        pass
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, locked_positions)

        if paused:
            # Render layar dengan teks pause
            draw_window(win, grid, score, lines, int(max(1, 1 + lines // 10)), next_piece)
            pause_label = FONT_BIG.render('PAUSED', True, WHITE)
            win.blit(pause_label, (PLAY_X + PLAY_WIDTH // 2 - pause_label.get_width() // 2,
                                   PLAY_Y + PLAY_HEIGHT // 2 - pause_label.get_height() // 2))
            pygame.display.update()
            continue

        # Input tahan kiri/kanan (auto-shift sederhana)
        keys = pygame.key.get_pressed()
        last_move_sideways += dt
        if last_move_sideways >= DAS:
            if keys[pygame.K_LEFT]:
                current_piece.x -= 1
                if not valid_space(current_piece, locked_positions):
                    current_piece.x += 1
                else:
                    last_move_sideways = 0
            elif keys[pygame.K_RIGHT]:
                current_piece.x += 1
                if not valid_space(current_piece, locked_positions):
                    current_piece.x -= 1
                else:
                    last_move_sideways = 0

        # Turun otomatis
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, locked_positions):
                current_piece.y -= 1
                change_piece = True

        # Update grid
        grid = create_grid(locked_positions)
        for (x, y) in convert_shape_format(current_piece):
            if y >= 0:
                if 0 <= x < COLS and 0 <= y < ROWS:
                    grid[y][x] = current_piece.color

        # Jika piece terkunci
        if change_piece:
            for pos in convert_shape_format(current_piece):
                x, y = pos
                if y < 0:
                    # sudah di atas layar saat terkunci -> game over
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            # Spawn piece baru dan reset
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                lines += cleared
                # Skor Tetris klasik sederhana
                score_add = {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 100 * cleared)
                score += score_add
                # Naikkan level mempengaruhi fall_speed
                level = 1 + lines // 10
                fall_speed = max(0.08, 0.5 - (level - 1) * 0.05)

        # Render
        level = 1 + lines // 10
        draw_window(win, grid, score, lines, level, next_piece)

        # Cek kalah
        if check_lost(locked_positions):
            run = False

    # Game over screen
    win.fill((30, 30, 35))
    over = FONT_BIG.render('GAME OVER', True, WHITE)
    info = FONT_MED.render('Press R to restart or ESC to quit', True, WHITE)
    win.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - over.get_height()))
    win.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()

    wait_restart = True
    while wait_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    main()
                    return


def main_menu():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris - Pygame')
    run = True
    while run:
        win.fill((30, 30, 35))
        title = FONT_BIG.render('TETRIS', True, WHITE)
        prompt = FONT_MED.render('Press any key to play', True, WHITE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        win.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main()
                run = False
                break


if __name__ == '__main__':
    main_menu()
