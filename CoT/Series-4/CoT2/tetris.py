import pygame
import random
import sys
from typing import Dict, List, Tuple

# -----------------------------
# Konfigurasi Game
# -----------------------------
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 32  # px per kotak grid

PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

FPS = 60

# Warna-warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (30, 30, 30)

# Tujuh bentuk Tetris: S, Z, I, O, J, L, T
# Representasi setiap rotasi sebagai grid 4x4 menggunakan string '0' untuk blok terisi
S = [
    [
        "..00",
        ".00.",
        "....",
        "....",
    ],
    [
        ".0..",
        ".00.",
        "..0.",
        "....",
    ],
]

Z = [
    [
        ".00.",
        "..00",
        "....",
        "....",
    ],
    [
        "..0.",
        ".00.",
        ".0..",
        "....",
    ],
]

I = [
    [
        "....",
        "0000",
        "....",
        "....",
    ],
    [
        "..0.",
        "..0.",
        "..0.",
        "..0.",
    ],
]

O = [
    [
        ".00.",
        ".00.",
        "....",
        "....",
    ],
]

J = [
    [
        "0...",
        "000.",
        "....",
        "....",
    ],
    [
        ".00.",
        ".0..",
        ".0..",
        "....",
    ],
    [
        "....",
        "000.",
        "..0.",
        "....",
    ],
    [
        "..0.",
        "..0.",
        ".00.",
        "....",
    ],
]

L = [
    [
        "..0.",
        "000.",
        "....",
        "....",
    ],
    [
        ".0..",
        ".0..",
        ".00.",
        "....",
    ],
    [
        "....",
        "000.",
        "0...",
        "....",
    ],
    [
        ".00.",
        "..0.",
        "..0.",
        "....",
    ],
]

T = [
    [
        ".0..",
        "000.",
        "....",
        "....",
    ],
    [
        ".0..",
        ".00.",
        ".0..",
        "....",
    ],
    [
        "....",
        "000.",
        ".0..",
        "....",
    ],
    [
        ".0..",
        "00..",
        ".0..",
        "....",
    ],
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [
    (80, 220, 100),   # S - hijau
    (220, 80, 100),   # Z - merah
    (80, 200, 220),   # I - cyan
    (220, 220, 80),   # O - kuning
    (80, 100, 220),   # J - biru
    (220, 140, 80),   # L - oranye
    (200, 80, 220),   # T - ungu
]


class Piece:
    """Class bidak yang sedang jatuh."""

    def __init__(self, x: int, y: int, shape: List[List[str]], color: Tuple[int, int, int]):
        # posisi grid
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # indeks rotasi saat ini

    def image(self) -> List[str]:
        """Mengembalikan bentuk (4x4 string) sesuai rotasi saat ini."""
        return self.shape[self.rotation % len(self.shape)]


# -----------------------------
# Utilitas Grid
# -----------------------------

def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    """Konversi bentuk 4x4 menjadi koordinat grid absolut berdasarkan x,y bidak."""
    positions = []
    template = piece.image()
    for i, line in enumerate(template):
        for j, char in enumerate(line):
            if char == '0':
                positions.append((piece.x + j - 1, piece.y + i - 2))
                # offset (-1, -2) untuk menyelaraskan spawn & rotasi standar 4x4
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = {
        (x, y)
        for y in range(GRID_HEIGHT)
        for x in range(GRID_WIDTH)
        if grid[y][x] == BLACK
    }
    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and (x, y) not in accepted_positions:
            return False
    return True


def out_of_bounds(piece: Piece) -> bool:
    for (x, y) in convert_shape_format(piece):
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return True
    return False


def check_lost(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Kalah jika ada blok terkunci di atas grid (y < 0) atau pada spawn baris awal
    for (_, y) in locked_positions.keys():
        if y < 1:
            return True
    return False


# -----------------------------
# Pembersihan Baris
# -----------------------------

def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    """Menghapus baris penuh dari bawah ke atas dan menggeser blok di atasnya turun.
    Mengembalikan jumlah baris yang dihapus."""
    rows_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[y]:
            rows_cleared += 1
            # Hapus semua blok di baris ini dari locked
            for x in range(GRID_WIDTH):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # Geser blok di atasnya turun
            for (x0, y0) in sorted(list(locked.keys()), key=lambda p: p[1]):
                if y0 < y:
                    color = locked[(x0, y0)]
                    del locked[(x0, y0)]
                    locked[(x0, y0 + 1)] = color
    return rows_cleared


# -----------------------------
# Gambar & UI
# -----------------------------

def draw_grid(surface, grid):
    # Latar belakang area permainan
    pygame.draw.rect(surface, DARK_GREY, (0, 0, PLAY_WIDTH, PLAY_HEIGHT))

    # Kotak grid & kotak terisi
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            color = grid[y][x]
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)  # garis grid tipis


def draw_side_panel(surface, next_piece: Piece, score: int, level: int, lines: int, font):
    panel_x = PLAY_WIDTH
    # Latar panel
    pygame.draw.rect(surface, (20, 20, 20), (panel_x, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT))

    # Judul
    title_text = font.render("TETRIS", True, WHITE)
    surface.blit(title_text, (panel_x + 20, 20))

    # Skor
    score_text = font.render(f"Skor: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lines_text = font.render(f"Lines: {lines}", True, WHITE)
    surface.blit(score_text, (panel_x + 20, 70))
    surface.blit(level_text, (panel_x + 20, 100))
    surface.blit(lines_text, (panel_x + 20, 130))

    # Next piece preview
    preview_text = font.render("Next:", True, WHITE)
    surface.blit(preview_text, (panel_x + 20, 180))

    template = next_piece.shape[0]
    start_x = panel_x + 20
    start_y = 210
    for i, row in enumerate(template):
        for j, char in enumerate(row):
            if char == '0':
                pygame.draw.rect(
                    surface,
                    next_piece.color,
                    (start_x + j * (BLOCK_SIZE // 1.5), start_y + i * (BLOCK_SIZE // 1.5),
                     int(BLOCK_SIZE // 1.5), int(BLOCK_SIZE // 1.5)),
                )

    controls_font = pygame.font.SysFont('consolas', 16)
    controls = [
        "Controls:",
        "Panah Kiri/Kanan: Geser",
        "Panah Atas: Rotasi",
        "Panah Bawah: Turun cepat",
        "Spasi: Hard drop",
        "P: Pause",
        "Esc: Keluar",
    ]
    y = start_y + 140
    for line in controls:
        txt = controls_font.render(line, True, (200, 200, 200))
        surface.blit(txt, (panel_x + 20, y))
        y += 22


def draw_window(surface, grid, next_piece, score, level, lines, font):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    draw_side_panel(surface, next_piece, score, level, lines, font)
    pygame.display.update()


# -----------------------------
# Mekanika Game
# -----------------------------

def get_shape() -> Piece:
    idx = random.randrange(len(SHAPES))
    shape = SHAPES[idx]
    color = SHAPE_COLORS[idx]
    # Spawn di sekitar tengah atas grid
    x = GRID_WIDTH // 2
    y = 0
    return Piece(x, y, shape, color)


def hard_drop(current_piece: Piece, grid, locked):
    # Jatuhkan sampai mentok
    while True:
        current_piece.y += 1
        if not valid_space(current_piece, grid):
            current_piece.y -= 1
            break
    # Kunci bidak
    for pos in convert_shape_format(current_piece):
        x, y = pos
        if y >= 0:
            locked[(x, y)] = current_piece.color


def add_to_locked(piece: Piece, locked):
    for (x, y) in convert_shape_format(piece):
        if y >= 0:
            locked[(x, y)] = piece.color


# -----------------------------
# Main Loop
# -----------------------------

def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', 24)

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    fall_time = 0
    fall_speed = 0.6  # detik per turun otomatis (akan makin cepat per level)

    score = 0
    level = 1
    lines_cleared_total = 0

    paused = False

    while run:
        dt = clock.tick(FPS) / 1000.0
        if not paused:
            fall_time += dt

        grid = create_grid(locked_positions)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
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
                    # rotasi searah jarum jam
                    prev_rot = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        # Sederhana: coba nudge ke kiri/kanan satu kali (wall kick sederhana)
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

        if paused:
            # Render state pause
            draw_window(win, grid, next_piece, score, level, lines_cleared_total, font)
            pause_txt = font.render("PAUSE", True, WHITE)
            win.blit(pause_txt, (PLAY_WIDTH // 2 - pause_txt.get_width() // 2, PLAY_HEIGHT // 2))
            pygame.display.update()
            continue

        # Turun otomatis berdasarkan fall_speed
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Tempelkan current_piece ke grid sementara (untuk visual)
        for (x, y) in convert_shape_format(current_piece):
            if y >= 0:
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    grid[y][x] = current_piece.color

        # Jika perlu mengunci bidak
        if change_piece:
            add_to_locked(current_piece, locked_positions)
            rows = clear_rows(grid, locked_positions)
            if rows > 0:
                lines_cleared_total += rows
                # Skor sederhana: 40/100/300/1200 seperti guideline, tapi disesuaikan level
                score_table = {1: 40, 2: 100, 3: 300, 4: 1200}
                score += score_table.get(rows, 0) * max(1, level)
                # Naik level tiap 10 lines
                level = 1 + lines_cleared_total // 10
                fall_speed = max(0.1, 0.6 - (level - 1) * 0.05)
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            if check_lost(locked_positions):
                run = False

        # Render
        draw_window(win, grid, next_piece, score, level, lines_cleared_total, font)

    # Game over screen
    game_over(win, score, font)
    pygame.quit()
    sys.exit(0)


def game_over(surface, score, font):
    surface.fill(BLACK)
    over_text = font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Skor: {score}", True, WHITE)
    info_font = pygame.font.SysFont('consolas', 18)
    info_text = info_font.render("Tekan Enter untuk keluar", True, WHITE)
    surface.blit(over_text, (PLAY_WIDTH // 2 - over_text.get_width() // 2, PLAY_HEIGHT // 2 - 40))
    surface.blit(score_text, (PLAY_WIDTH // 2 - score_text.get_width() // 2, PLAY_HEIGHT // 2))
    surface.blit(info_text, (PLAY_WIDTH // 2 - info_text.get_width() // 2, PLAY_HEIGHT // 2 + 40))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                waiting = False
                return


if __name__ == "__main__":
    main()
