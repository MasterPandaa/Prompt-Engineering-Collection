import pygame
import sys
import random
from typing import List, Tuple, Optional

# -----------------------------
# Konfigurasi permainan
# -----------------------------
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # piksel per blok
GRID_WIDTH = COLS * BLOCK_SIZE
GRID_HEIGHT = ROWS * BLOCK_SIZE

PANEL_WIDTH = 200  # panel samping untuk skor & next piece
WINDOW_WIDTH = GRID_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT

FPS = 60

# Kecepatan jatuh (detik per sel)
GRAVITY = 0.6
SOFT_DROP_MULTIPLIER = 0.1  # soft drop membuat jatuh 10x lebih cepat (0.6 * 0.1 = 0.06 detik per sel)

# Skor per jumlah garis yang dibersihkan sekaligus
LINE_CLEAR_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# Warna-warna
WHITE = (240, 240, 240)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (35, 35, 35)
BLACK = (15, 15, 15)

# Tetromino Colors (I, O, T, S, Z, J, L)
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0)
}

# Definisi bentuk dalam rotasi (matriks 4x4)
# Setiap bentuk direpresentasikan sebagai daftar rotasi, masing-masing rotasi adalah daftar koordinat (x, y) relatif 4 blok.
# Koordinat referensi adalah pivot pada bentuk (menggunakan definisi sederhana yang umum dipakai dalam implementasi tetris dasar)
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # ---- horizontal
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # | vertical
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
    ],
    'T': [
        [(1, 1), (0, 1), (2, 1), (1, 2)],
        [(1, 1), (1, 0), (1, 2), (2, 1)],
        [(1, 1), (0, 1), (2, 1), (1, 0)],
        [(1, 1), (1, 0), (1, 2), (0, 1)],
    ],
    'S': [
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'Z': [
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    'J': [
        [(0, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# Posisi spawn pusat (x, y) di grid
SPAWN_X = COLS // 2 - 2  # kebanyakan shape 4x4, ini menempatkan kira-kira di tengah
SPAWN_Y = -2  # mulai sedikit di atas grid agar ada ruang muncul


class Piece:
    def __init__(self, shape_key: str):
        self.shape_key = shape_key
        self.rot = 0
        self.x = SPAWN_X
        self.y = SPAWN_Y
        self.cells = SHAPES[shape_key]  # list rotasi
        self.color = COLORS[shape_key]

    def get_coords(self, rot: Optional[int] = None, pos: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        r = self.rot if rot is None else rot
        px, py = (self.x, self.y) if pos is None else pos
        return [(px + cx, py + cy) for (cx, cy) in self.cells[r % 4]]


class Board:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        # grid berisi None atau tuple warna (r, g, b)
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(cols)] for _ in range(rows)]
        self.score = 0

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and y < self.rows

    def is_occupied(self, x: int, y: int) -> bool:
        if y < 0:
            return False  # di atas papan dianggap tidak terisi
        return self.grid[y][x] is not None

    def valid_position(self, piece: Piece, rot: Optional[int] = None, pos: Optional[Tuple[int, int]] = None) -> bool:
        for (x, y) in piece.get_coords(rot, pos):
            if x < 0 or x >= self.cols:
                return False
            if y >= self.rows:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, piece: Piece):
        # tempelkan piece ke grid
        for (x, y) in piece.get_coords():
            if 0 <= y < self.rows:
                self.grid[y][x] = piece.color
        # bersihkan garis
        cleared = self.clear_lines()
        if cleared > 0:
            self.score += LINE_CLEAR_SCORES.get(cleared, cleared * 100)

    def clear_lines(self) -> int:
        new_grid: List[List[Optional[Tuple[int, int, int]]]] = []
        cleared = 0
        for y in range(self.rows):
            if all(self.grid[y][x] is not None for x in range(self.cols)):
                cleared += 1
            else:
                new_grid.append(self.grid[y])
        # tambahkan baris kosong di atas sebanyak yang di-clear
        while len(new_grid) < self.rows:
            new_grid.insert(0, [None for _ in range(self.cols)])
        self.grid = new_grid
        return cleared

    def is_game_over(self) -> bool:
        # game over jika ada blok pada baris y < 0 saat spawn/lock
        # atau lebih praktis: jika ada blok di baris 0 dan piece baru tidak bisa ditempatkan
        # Di implementasi ini, kita cek baris 0 apakah terisi di saat mencoba spawn.
        return any(self.grid[0][x] is not None for x in range(self.cols))


def draw_grid(surface, board: Board):
    # latar grid
    surface.fill(BLACK)
    # garis kotak
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, DARK_GREY, rect, 1)
            color = board.grid[y][x]
            if color is not None:
                inner = rect.inflate(-2, -2)
                pygame.draw.rect(surface, color, inner)


def draw_piece(surface, piece: Piece):
    for (x, y) in piece.get_coords():
        if y >= 0:
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            inner = rect.inflate(-2, -2)
            pygame.draw.rect(surface, piece.color, inner)


def draw_panel(surface, board: Board, next_piece: Piece, font_small, font_big):
    surface.fill((20, 20, 30))

    # Judul
    title = font_big.render("TETRIS", True, WHITE)
    surface.blit(title, (20, 20))

    # Skor
    score_label = font_small.render("Skor", True, LIGHT_GREY)
    surface.blit(score_label, (20, 90))
    score_val = font_big.render(str(board.score), True, WHITE)
    surface.blit(score_val, (20, 115))

    # Next Piece
    next_label = font_small.render("Berikutnya", True, LIGHT_GREY)
    surface.blit(next_label, (20, 190))

    # Gambar next piece dengan skala grid kecil
    preview_scale = BLOCK_SIZE // 1
    offset_x = 20
    offset_y = 215
    # lakukan perataan ke tengah area 4x4
    coords = next_piece.get_coords(rot=0, pos=(0, 0))
    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = (max_x - min_x + 1) * preview_scale
    height = (max_y - min_y + 1) * preview_scale
    base_x = offset_x + (PANEL_WIDTH - 2 * 20 - width) // 2
    base_y = offset_y + (150 - height) // 2

    for (x, y) in SHAPES[next_piece.shape_key][0]:
        rect = pygame.Rect(base_x + (x - min_x) * preview_scale, base_y + (y - min_y) * preview_scale,
                           preview_scale, preview_scale)
        inner = rect.inflate(-2, -2)
        pygame.draw.rect(surface, next_piece.color, inner)

    # Kontrol
    controls_y = offset_y + 170
    control_lines = [
        "Kontrol:",
        "Panah Kiri/Kanan: Geser",
        "Panah Atas: Rotasi",
        "Panah Bawah: Soft drop",
        "SPACE: Hard drop",
        "Esc: Keluar",
        "R: Restart",
    ]
    for i, line in enumerate(control_lines):
        color = LIGHT_GREY if i == 0 else WHITE
        txt = font_small.render(line, True, color)
        surface.blit(txt, (20, controls_y + i * 22))


def get_bag_queue() -> List[str]:
    # 7-bag randomizer, untuk distribusi tetromino yang seimbang
    bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
    random.shuffle(bag)
    return bag


def spawn_piece(queue: List[str]) -> Tuple[Piece, List[str]]:
    if not queue:
        queue = get_bag_queue()
    shape_key = queue.pop(0)
    piece = Piece(shape_key)
    return piece, queue


def try_rotate(board: Board, piece: Piece, direction: int) -> None:
    # direction: +1 searah jarum jam, -1 berlawanan
    new_rot = (piece.rot + direction) % 4
    # coba rotasi in place
    if board.valid_position(piece, rot=new_rot, pos=(piece.x, piece.y)):
        piece.rot = new_rot
        return
    # coba wall kick sederhana: geser -1, +1, -2, +2
    for dx in (-1, 1, -2, 2):
        if board.valid_position(piece, rot=new_rot, pos=(piece.x + dx, piece.y)):
            piece.x += dx
            piece.rot = new_rot
            return
    # Untuk I piece, coba kick vertikal kecil jika menabrak lantai
    if piece.shape_key == 'I':
        for dy in (-1, 1):
            if board.valid_position(piece, rot=new_rot, pos=(piece.x, piece.y + dy)):
                piece.y += dy
                piece.rot = new_rot
                return


def hard_drop(board: Board, piece: Piece) -> int:
    distance = 0
    while board.valid_position(piece, pos=(piece.x, piece.y + 1)):
        piece.y += 1
        distance += 1
    return distance


def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    grid_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    panel_surface = pygame.Surface((PANEL_WIDTH, WINDOW_HEIGHT))

    font_small = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 32, bold=True)

    clock = pygame.time.Clock()

    def start_game():
        board = Board(COLS, ROWS)
        queue = get_bag_queue()
        current, queue = spawn_piece(queue)
        next_piece, queue = spawn_piece(queue)
        return board, current, next_piece, queue

    board, current, next_piece, queue = start_game()

    fall_timer = 0.0
    gravity = GRAVITY

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # detik
        fall_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    board, current, next_piece, queue = start_game()
                    fall_timer = 0.0
                elif event.key == pygame.K_LEFT:
                    if board.valid_position(current, pos=(current.x - 1, current.y)):
                        current.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if board.valid_position(current, pos=(current.x + 1, current.y)):
                        current.x += 1
                elif event.key == pygame.K_UP:
                    try_rotate(board, current, +1)
                elif event.key == pygame.K_SPACE:
                    hard_drop(board, current)
                    # lock segera
                    board.lock_piece(current)
                    # spawn berikutnya
                    current = next_piece
                    next_piece, queue = spawn_piece(queue)
                    # jika langsung invalid => game over
                    if not board.valid_position(current):
                        # freeze and show game over overlay
                        show_game_over(screen, board, font_big, font_small)
                        board, current, next_piece, queue = start_game()
                        fall_timer = 0.0

        # Soft drop dengan menahan panah bawah
        keys = pygame.key.get_pressed()
        current_gravity = gravity * (SOFT_DROP_MULTIPLIER if keys[pygame.K_DOWN] else 1.0)

        # Turunkan piece sesuai timer
        if fall_timer >= current_gravity:
            fall_timer -= current_gravity
            if board.valid_position(current, pos=(current.x, current.y + 1)):
                current.y += 1
            else:
                # lock
                board.lock_piece(current)
                # piece baru
                current = next_piece
                next_piece, queue = spawn_piece(queue)
                # cek valid spawn
                if not board.valid_position(current):
                    show_game_over(screen, board, font_big, font_small)
                    board, current, next_piece, queue = start_game()
                    fall_timer = 0.0

        # Gambar
        draw_grid(grid_surface, board)
        draw_piece(grid_surface, current)
        draw_panel(panel_surface, board, next_piece, font_small, font_big)

        screen.blit(grid_surface, (0, 0))
        screen.blit(panel_surface, (GRID_WIDTH, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def show_game_over(screen, board: Board, font_big, font_small):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    text = font_big.render("GAME OVER", True, WHITE)
    score_text = font_small.render(f"Skor: {board.score}", True, WHITE)
    info_text = font_small.render("Tekan R untuk restart atau Esc untuk keluar", True, WHITE)

    # Posisikan di tengah layar
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
    info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))

    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    screen.blit(info_text, info_rect)
    pygame.display.flip()

    # Tunggu sampai user menekan R atau Esc atau menutup window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    waiting = False
        pygame.time.delay(10)


if __name__ == "__main__":
    main()
