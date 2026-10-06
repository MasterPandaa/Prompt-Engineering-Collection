import sys
import random
import pygame
from typing import Dict, List, Tuple

# -----------------------------
# Konstanta Game
# -----------------------------
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
PLAY_WIDTH = 300   # 10 blok * 30 px
PLAY_HEIGHT = 600  # 20 blok * 30 px
BLOCK_SIZE = 30

GRID_COLS = 10
GRID_ROWS = 20

TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT - 50

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (30, 30, 30)
RED = (200, 30, 30)
GREEN = (30, 200, 30)
BLUE = (30, 30, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)

# Bentuk Tetromino (format rotasi)
# Representasi: tiap bentuk adalah list dari rotasi; setiap rotasi list 4 string 4x4
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
        "0000",
        "....",
        "....",
        "....",
    ],
    [
        "0...",
        "0...",
        "0...",
        "0...",
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
        ".0..",
        ".0..",
        "00..",
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
        "00..",
        ".0..",
        ".0..",
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
SHAPE_COLORS = [GREEN, RED, CYAN, YELLOW, BLUE, ORANGE, MAGENTA]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x  # posisi grid x
        self.y = y  # posisi grid y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0  # indeks rotasi

    def get_formatted_positions(self) -> List[Tuple[int, int]]:
        positions = []
        rotation_pattern = self.shape[self.rotation % len(self.shape)]
        for i, line in enumerate(rotation_pattern):
            for j, char in enumerate(line):
                if char == '0':
                    positions.append((self.x + j, self.y + i))
        return positions


def create_grid(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    for (x, y), color in locked.items():
        if 0 <= y < GRID_ROWS and 0 <= x < GRID_COLS:
            grid[y][x] = color
    return grid


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = set(
        (x, y)
        for y in range(GRID_ROWS)
        for x in range(GRID_COLS)
        if grid[y][x] == BLACK
    )
    for (x, y) in piece.get_formatted_positions():
        if y < 0:
            # di atas layar masih dianggap valid untuk spawn
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def out_of_bounds(piece: Piece) -> bool:
    for (x, y) in piece.get_formatted_positions():
        if x < 0 or x >= GRID_COLS or y >= GRID_ROWS:
            return True
    return False


def check_lost(locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    for (x, y) in locked.keys():
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    shape = random.choice(SHAPES)
    # spawn di dekat tengah atas grid
    return Piece(x=GRID_COLS // 2 - 2, y=-2, shape=shape)


def clear_rows(grid, locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    rows_cleared = 0
    for y in range(GRID_ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            rows_cleared += 1
            # hapus semua posisi di baris ini dari locked
            for x in range(GRID_COLS):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
            # geser semua sel di atasnya turun 1
            for (x, y2) in sorted(list(locked.keys()), key=lambda p: p[1]):
                if y2 < y:
                    locked[(x, y2 + 1)] = locked.pop((x, y2))
    return rows_cleared


def draw_grid_lines(surface):
    # garis grid tipis
    for i in range(GRID_ROWS + 1):
        pygame.draw.line(
            surface,
            DARK_GREY,
            (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
            (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE),
            1,
        )
    for j in range(GRID_COLS + 1):
        pygame.draw.line(
            surface,
            DARK_GREY,
            (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
            (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT),
            1,
        )


def draw_window(surface, grid, score: int, level: int, lines: int, next_piece: Piece, paused: bool, game_over: bool):
    surface.fill((20, 20, 30))

    # Judul
    font = pygame.font.SysFont('consolas', 36, bold=True)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2, 10))

    # Info panel
    small = pygame.font.SysFont('consolas', 20)
    info_x = TOP_LEFT_X + PLAY_WIDTH + 20
    surface.blit(small.render(f'Score: {score}', True, WHITE), (info_x, TOP_LEFT_Y))
    surface.blit(small.render(f'Level: {level}', True, WHITE), (info_x, TOP_LEFT_Y + 28))
    surface.blit(small.render(f'Lines: {lines}', True, WHITE), (info_x, TOP_LEFT_Y + 56))
    surface.blit(small.render('Next:', True, WHITE), (info_x, TOP_LEFT_Y + 100))

    # Background playfield
    pygame.draw.rect(
        surface,
        GREY,
        (TOP_LEFT_X - 4, TOP_LEFT_Y - 4, PLAY_WIDTH + 8, PLAY_HEIGHT + 8),
        4,
    )

    # Gambar blok pada grid
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (
                        TOP_LEFT_X + x * BLOCK_SIZE + 1,
                        TOP_LEFT_Y + y * BLOCK_SIZE + 1,
                        BLOCK_SIZE - 2,
                        BLOCK_SIZE - 2,
                    ),
                    border_radius=4,
                )

    # Grid lines
    draw_grid_lines(surface)

    # Next piece preview
    preview_grid = create_grid({})
    ghost = Piece(0, 0, next_piece.shape)
    ghost.rotation = next_piece.rotation
    for (px, py) in ghost.get_formatted_positions():
        gx = px - ghost.x
        gy = py - ghost.y
        if 0 <= gx < 4 and 0 <= gy < 4:
            preview_grid[gy][gx] = next_piece.color
    # gambar preview 4x4
    cell = 22
    prev_x = info_x
    prev_y = TOP_LEFT_Y + 130
    pygame.draw.rect(surface, DARK_GREY, (prev_x, prev_y, cell * 4 + 4, cell * 4 + 4), border_radius=6)
    for gy in range(4):
        for gx in range(4):
            c = preview_grid[gy][gx]
            if c != BLACK:
                pygame.draw.rect(
                    surface,
                    c,
                    (prev_x + gx * cell + 2, prev_y + gy * cell + 2, cell - 4, cell - 4),
                    border_radius=4,
                )

    if paused and not game_over:
        pause_lbl = font.render('PAUSED', True, YELLOW)
        surface.blit(
            pause_lbl,
            (TOP_LEFT_X + PLAY_WIDTH // 2 - pause_lbl.get_width() // 2, TOP_LEFT_Y + PLAY_HEIGHT // 2 - 20),
        )

    if game_over:
        over_lbl = font.render('GAME OVER', True, RED)
        tip_lbl = small.render('Press R to Restart or ESC to Quit', True, WHITE)
        surface.blit(
            over_lbl,
            (TOP_LEFT_X + PLAY_WIDTH // 2 - over_lbl.get_width() // 2, TOP_LEFT_Y + PLAY_HEIGHT // 2 - 40),
        )
        surface.blit(
            tip_lbl,
            (TOP_LEFT_X + PLAY_WIDTH // 2 - tip_lbl.get_width() // 2, TOP_LEFT_Y + PLAY_HEIGHT // 2),
        )

    pygame.display.update()


def hard_drop(piece: Piece, grid, locked):
    # Jatuhkan sampai mentok
    while True:
        piece.y += 1
        if out_of_bounds(piece) or not valid_space(piece, grid):
            piece.y -= 1
            break


def main(window):
    locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True

    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()

    score = 0
    lines_cleared_total = 0
    level = 1

    fall_time = 0
    fall_delay = 0.6  # detik antar jatuh 1 sel

    move_cooldown = 0
    move_delay = 0.1

    paused = False
    game_over = False

    while run:
        dt = clock.tick(60) / 1000.0  # detik per frame
        if not paused and not game_over:
            fall_time += dt
            move_cooldown = max(0.0, move_cooldown - dt)

        grid = create_grid(locked_positions)

        # Gerakan jatuh otomatis
        if not paused and not game_over and fall_time >= fall_delay:
            fall_time = 0
            current_piece.y += 1
            if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                if game_over:
                    if event.key == pygame.K_r:
                        return  # restart dari main_menu

                if paused or game_over:
                    continue

                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    # soft drop
                    current_piece.y += 1
                    if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    # rotate CW
                    prev = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                        # coba wall kick sederhana: geser -1, +1
                        kicked = False
                        for dx in (-1, 1, -2, 2):
                            current_piece.x += dx
                            if not out_of_bounds(current_piece) and valid_space(current_piece, grid):
                                kicked = True
                                break
                            current_piece.x -= dx
                        if not kicked:
                            current_piece.rotation = prev
                elif event.key == pygame.K_z:
                    # rotate CCW
                    prev = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                    if out_of_bounds(current_piece) or not valid_space(current_piece, grid):
                        kicked = False
                        for dx in (-1, 1, -2, 2):
                            current_piece.x += dx
                            if not out_of_bounds(current_piece) and valid_space(current_piece, grid):
                                kicked = True
                                break
                            current_piece.x -= dx
                        if not kicked:
                            current_piece.rotation = prev
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    hard_drop(current_piece, grid, locked_positions)
                    change_piece = True

        # render current piece into grid view only (tidak mengunci)
        for (x, y) in current_piece.get_formatted_positions():
            if y >= 0:
                if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS:
                    grid[y][x] = current_piece.color

        # Jika perlu mengunci piece
        if change_piece and not paused and not game_over:
            change_piece = False
            for (x, y) in current_piece.get_formatted_positions():
                if y >= 0:
                    locked_positions[(x, y)] = current_piece.color
            # spawn baru
            current_piece = next_piece
            next_piece = get_shape()
            # clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                # Skor sederhana: 40/100/300/1200 * level (mirip Tetris)
                score_map = {1: 40, 2: 100, 3: 300, 4: 1200}
                score += score_map.get(cleared, 50 * cleared) * max(1, level)
                lines_cleared_total += cleared
                # tingkatkan level setiap 10 lines
                level = lines_cleared_total // 10 + 1
                # percepat fall delay (batas bawah)
                fall_delay = max(0.08, 0.6 - (level - 1) * 0.05)

            if check_lost(locked_positions):
                game_over = True

        draw_window(window, grid, score, level, lines_cleared_total, next_piece, paused, game_over)

    pygame.quit()
    sys.exit(0)


def main_menu():
    pygame.init()
    pygame.display.set_caption('Tetris - Pygame')
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('consolas', 48, bold=True)
    tip_font = pygame.font.SysFont('consolas', 22)

    running = True
    while running:
        dt = clock.tick(60)
        window.fill((15, 15, 25))
        title = title_font.render('TETRIS', True, WHITE)
        tip = tip_font.render('Press ENTER to Play  |  ESC to Quit', True, WHITE)
        control_lines = [
            'Controls:',
            'Left/Right = Move',
            'Up/X = Rotate CW  |  Z = Rotate CCW',
            'Down = Soft Drop  |  Space = Hard Drop',
            'P = Pause  |  R = Restart (when over)',
        ]
        window.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))
        window.blit(tip, (WINDOW_WIDTH // 2 - tip.get_width() // 2, 190))

        small = pygame.font.SysFont('consolas', 20)
        for i, line in enumerate(control_lines):
            txt = small.render(line, True, (220, 220, 230))
            window.blit(txt, (WINDOW_WIDTH // 2 - 200, 250 + i * 26))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN:
                    # Mulai game
                    main(window)

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main_menu()
