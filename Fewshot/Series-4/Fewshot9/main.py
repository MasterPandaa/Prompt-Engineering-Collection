import pygame
import random
import sys
from typing import Dict, List, Tuple

# -----------------------------
# Konfigurasi dasar
# -----------------------------
pygame.init()

# Ukuran grid
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # pixel per blok

PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE
SIDE_PANEL_WIDTH = 200

WIN_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WIN_HEIGHT = PLAY_HEIGHT

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Font
pygame.font.init()
FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MED = pygame.font.SysFont("consolas", 24)
FONT_BIG = pygame.font.SysFont("consolas", 36)

# -----------------------------
# Definisi Tetromino
# Menggunakan koordinat relatif terhadap pivot (0,0)
# Rotasi searah jarum jam: (x, y) -> (y, -x)
# -----------------------------

# 7 bentuk: I, O, T, S, Z, J, L
# Tiap bentuk didefinisikan sebagai: (list[kordinat], warna RGB)
I_SHAPE = ([(0, 0), (-1, 0), (1, 0), (2, 0)], (0, 255, 255))  # cyan
O_SHAPE = ([(0, 0), (1, 0), (0, 1), (1, 1)], (255, 255, 0))   # yellow
T_SHAPE = ([(0, 0), (-1, 0), (1, 0), (0, -1)], (128, 0, 128)) # purple
S_SHAPE = ([(0, 0), (1, 0), (0, -1), (-1, -1)], (0, 255, 0))  # green
Z_SHAPE = ([(0, 0), (-1, 0), (0, -1), (1, -1)], (255, 0, 0))  # red
J_SHAPE = ([(0, 0), (-1, 0), (1, 0), (-1, -1)], (0, 0, 255))  # blue
L_SHAPE = ([(0, 0), (-1, 0), (1, 0), (1, -1)], (255, 165, 0)) # orange

SHAPES = [I_SHAPE, O_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, J_SHAPE, L_SHAPE]

class Piece:
    def __init__(self, column: int, row: int, shape: Tuple[List[Tuple[int, int]], Tuple[int, int, int]]):
        # posisi pivot (x, y) di grid
        self.x = column
        self.y = row
        self.cells = shape[0][:]  # koordinat relatif
        self.color = shape[1]
        self.rotation = 0  # 0..3

    def rotated_cells(self) -> List[Tuple[int, int]]:
        # Rotasi searah jarum jam berdasarkan self.rotation
        def rotate_point(pt):
            x, y = pt
            return (y, -x)

        pts = self.cells[:]
        for _ in range(self.rotation % 4):
            pts = [rotate_point(p) for p in pts]
        return pts

    def absolute_positions(self) -> List[Tuple[int, int]]:
        # Konversi dari koordinat relatif ke posisi grid absolut
        return [(self.x + px, self.y + py) for (px, py) in self.rotated_cells()]


def create_grid(locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    for (x, y) in piece.absolute_positions():
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0:  # di atas layar (spawn) boleh y < 0
            if grid[y][x] != BLACK:
                return False
    return True


def check_lost(locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Kalah jika ada blok terkunci yang naik ke atas (y < 0)
    for (_, y) in locked.keys():
        if y < 0:
            return True
    return False


def get_shape() -> Piece:
    shape = random.choice(SHAPES)
    # Spawn di atas tengah grid
    # Banyak tetromino punya blok dengan py = -1 (di atas board) untuk spawn natural
    return Piece(COLS // 2, -1, shape)


def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]):
    # Hapus baris penuh dan geser blok di atasnya turun sejumlah baris yang dibersihkan
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            # baris penuh
            cleared += 1
            for x in range(COLS):
                locked.pop((x, y), None)
        elif cleared > 0:
            # geser baris ini turun 'cleared' langkah
            for x in range(COLS):
                if (x, y) in locked:
                    color = locked.pop((x, y))
                    locked[(x, y + cleared)] = color
    return cleared


def draw_grid_lines(surface):
    # Garis grid di area permainan
    for y in range(ROWS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (0, y * BLOCK_SIZE), (PLAY_WIDTH, y * BLOCK_SIZE), 1)
    for x in range(COLS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, PLAY_HEIGHT), 1)


def draw_window(surface, grid, score, high_score):
    surface.fill(GRAY)

    # Area permainan
    play_rect = pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT)
    pygame.draw.rect(surface, BLACK, play_rect)

    # Gambar blok-blok dari grid
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(surface, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                # outline tipis
                pygame.draw.rect(surface, (30, 30, 30), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    draw_grid_lines(surface)

    # Panel samping
    panel_x = PLAY_WIDTH + 10
    title = FONT_BIG.render("TETRIS", True, WHITE)
    surface.blit(title, (PLAY_WIDTH + (SIDE_PANEL_WIDTH - title.get_width()) // 2, 10))

    score_label = FONT_MED.render(f"Score: {score}", True, WHITE)
    surface.blit(score_label, (panel_x, 70))

    hs_label = FONT_MED.render(f"High: {high_score}", True, WHITE)
    surface.blit(hs_label, (panel_x, 100))

    controls = [
        "Controls:",
        "Left/Right: Move",
        "Up: Rotate",
        "Down: Soft drop",
        "Space: Hard drop",
        "P: Pause",
        "Esc: Quit",
    ]
    for i, text in enumerate(controls):
        label = FONT_SMALL.render(text, True, WHITE)
        surface.blit(label, (panel_x, 150 + i * 20))


def draw_next_shape(surface, piece: Piece):
    label = FONT_MED.render("Next:", True, WHITE)
    surface.blit(label, (PLAY_WIDTH + 10, 300))

    # Render bentuk berikutnya dalam grid kecil
    preview_grid = [[BLACK for _ in range(6)] for _ in range(6)]

    # Normalisasi posisi: pindahkan agar terlihat di tengah preview
    cells = piece.rotated_cells()
    min_x = min(c[0] for c in cells)
    max_x = max(c[0] for c in cells)
    min_y = min(c[1] for c in cells)
    max_y = max(c[1] for c in cells)

    offset_x = 3 - (min_x + max_x) // 2
    offset_y = 3 - (min_y + max_y) // 2

    for (px, py) in cells:
        x = px + offset_x
        y = py + offset_y
        if 0 <= x < 6 and 0 <= y < 6:
            preview_grid[y][x] = piece.color

    start_x = PLAY_WIDTH + 10
    start_y = 330

    for y in range(6):
        for x in range(6):
            color = preview_grid[y][x]
            rect = pygame.Rect(start_x + x * 20, start_y + y * 20, 20, 20)
            pygame.draw.rect(surface, color if color != BLACK else (25, 25, 25), rect)
            pygame.draw.rect(surface, (60, 60, 60), rect, 1)


def hard_drop(piece: Piece, grid, locked):
    # Turunkan hingga tidak valid lagi, lalu naikkan 1
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break
    # Kunci piece ke locked
    for (x, y) in piece.absolute_positions():
        locked[(x, y)] = piece.color


def lock_piece(piece: Piece, locked):
    for (x, y) in piece.absolute_positions():
        locked[(x, y)] = piece.color


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Tetris - Pygame")

    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # detik per langkah turun otomatis

    level_time = 0

    score = 0
    high_score = 0

    paused = False
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        if not paused:
            fall_time += dt
            level_time += dt

            # percepat sedikit demi sedikit
            if level_time > 30:
                level_time = 0
                fall_speed = max(0.05, fall_speed - 0.05)

            if fall_time >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    # kunci
                    lock_piece(current_piece, locked_positions)
                    # spawn baru
                    current_piece = next_piece
                    next_piece = get_shape()
                    # bersihkan baris
                    grid = create_grid(locked_positions)
                    cleared = clear_rows(grid, locked_positions)
                    if cleared > 0:
                        score += (cleared ** 2) * 100
                    grid = create_grid(locked_positions)

                    if check_lost(locked_positions):
                        running = False

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        # Rotasi CW
                        old_rot = current_piece.rotation
                        current_piece.rotation = (current_piece.rotation + 1) % 4
                        # Sederhana: coba wall kick kecil
                        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1)]
                        valid = False
                        for dx, dy in kicks:
                            current_piece.x += dx
                            current_piece.y += dy
                            if valid_space(current_piece, grid):
                                valid = True
                                break
                            current_piece.x -= dx
                            current_piece.y -= dy
                        if not valid:
                            current_piece.rotation = old_rot
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        hard_drop(current_piece, grid, locked_positions)
                        # spawn baru
                        current_piece = next_piece
                        next_piece = get_shape()
                        grid = create_grid(locked_positions)
                        cleared = clear_rows(grid, locked_positions)
                        if cleared > 0:
                            score += (cleared ** 2) * 100
                        grid = create_grid(locked_positions)
                        if check_lost(locked_positions):
                            running = False

        # Update grid dari locked + current_piece
        grid = create_grid(locked_positions)
        for (x, y) in current_piece.absolute_positions():
            if y >= 0:
                if 0 <= x < COLS and 0 <= y < ROWS:
                    grid[y][x] = current_piece.color

        # Gambar ke layar
        draw_window(win, grid, score, high_score)
        draw_next_shape(win, next_piece)
        pygame.display.update()

    # Game Over
    high_score = max(high_score, score)
    game_over_screen(win, score)


def game_over_screen(surface, score):
    overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    text1 = FONT_BIG.render("GAME OVER", True, WHITE)
    text2 = FONT_MED.render(f"Score: {score}", True, WHITE)
    text3 = FONT_SMALL.render("Press Enter to Play Again or Esc to Quit", True, WHITE)

    surface.blit(text1, ((WIN_WIDTH - text1.get_width()) // 2, WIN_HEIGHT // 2 - 60))
    surface.blit(text2, ((WIN_WIDTH - text2.get_width()) // 2, WIN_HEIGHT // 2 - 20))
    surface.blit(text3, ((WIN_WIDTH - text3.get_width()) // 2, WIN_HEIGHT // 2 + 20))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_RETURN:
                    waiting = False
    main()


if __name__ == "__main__":
    main()
