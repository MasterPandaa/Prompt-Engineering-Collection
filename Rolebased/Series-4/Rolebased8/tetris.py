import sys
import random
import pygame
from pygame import Rect

# ========== Konfigurasi ==========
WINDOW_TITLE = "Tetris - OOP (Python + Pygame)"
CELL_SIZE = 30
COLS, ROWS = 10, 20
SIDE_PANEL_WIDTH = 7  # kolom untuk panel samping (next, score)
BORDER = 20
FPS = 60

# Warna
BLACK = (0, 0, 0)
GRAY_DARK = (30, 30, 30)
GRAY = (60, 60, 60)
WHITE = (220, 220, 220)

# Warna masing-masing piece
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
}

# Bentuk Tetris: representasi rotasi dalam grid string
SHAPES = {
    'I': [
        [
            "....",
            "....",
            "####",
            "....",
        ],
        [
            "..#.",
            "..#.",
            "..#.",
            "..#.",
        ],
        [
            "....",
            "....",
            "####",
            "....",
        ],
        [
            ".#..",
            ".#..",
            ".#..",
            ".#..",
        ],
    ],
    'J': [
        [
            "#..",
            "###",
            "...",
        ],
        [
            ".##",
            ".#.",
            ".#.",
        ],
        [
            "...",
            "###",
            "..#",
        ],
        [
            ".#.",
            ".#.",
            "##.",
        ],
    ],
    'L': [
        [
            "..#",
            "###",
            "...",
        ],
        [
            ".#.",
            ".#.",
            ".##",
        ],
        [
            "...",
            "###",
            "#..",
        ],
        [
            "##.",
            ".#.",
            ".#.",
        ],
    ],
    'O': [
        [
            ".##.",
            ".##.",
            "....",
            "....",
        ],
        [
            ".##.",
            ".##.",
            "....",
            "....",
        ],
        [
            ".##.",
            ".##.",
            "....",
            "....",
        ],
        [
            ".##.",
            ".##.",
            "....",
            "....",
        ],
    ],
    'S': [
        [
            ".##",
            "##.",
            "...",
        ],
        [
            ".#.",
            ".##",
            "..#",
        ],
        [
            "...",
            ".##",
            "##.",
        ],
        [
            "#..",
            "##.",
            ".#.",
        ],
    ],
    'T': [
        [
            ".#.",
            "###",
            "...",
        ],
        [
            ".#.",
            ".##",
            ".#.",
        ],
        [
            "...",
            "###",
            ".#.",
        ],
        [
            ".#.",
            "##.",
            ".#.",
        ],
    ],
    'Z': [
        [
            "##.",
            ".##",
            "...",
        ],
        [
            "..#",
            ".##",
            ".#.",
        ],
        [
            "...",
            "##.",
            ".##",
        ],
        [
            ".#.",
            "##.",
            "#..",
        ],
    ],
}

# Ukuran box visual untuk spawn/preview
SHAPE_BOX_SIZE = {
    'I': 4,
    'O': 4,
    'J': 3,
    'L': 3,
    'S': 3,
    'T': 3,
    'Z': 3,
}

# Skor
SCORES = {
    1: 100,
    2: 300,
    3: 500,
    4: 800,  # Tetris
}

SOFT_DROP_BONUS = 1      # per cell
HARD_DROP_BONUS = 2      # per cell

LINES_PER_LEVEL = 10


# ========== Kelas Piece ==========
class Piece:
    def __init__(self, kind: str, x: int, y: int):
        self.kind = kind
        self.x = x  # posisi kolom pada board
        self.y = y  # posisi baris pada board
        self.rot = 0
        self.color = COLORS[kind]

    def get_cells(self):
        """
        Mengembalikan daftar koordinat sel (x, y) pada board untuk rotasi saat ini.
        """
        pattern = SHAPES[self.kind][self.rot % len(SHAPES[self.kind])]
        cells = []
        for r in range(len(pattern)):
            row = pattern[r]
            for c in range(len(row)):
                if row[c] == '#':
                    cells.append((self.x + c, self.y + r))
        return cells

    def rotated(self, delta_rot: int):
        """
        Menghasilkan objek Piece baru dengan rotasi yang ditambah delta_rot.
        """
        p = Piece(self.kind, self.x, self.y)
        p.rot = (self.rot + delta_rot) % len(SHAPES[self.kind])
        return p

    def moved(self, dx: int, dy: int):
        """
        Menghasilkan objek Piece baru dengan translasi posisi.
        """
        p = Piece(self.kind, self.x + dx, self.y + dy)
        p.rot = self.rot
        return p


# ========== Kelas Board ==========
class Board:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]  # None atau (r, g, b)
        self.score = 0
        self.lines_cleared = 0
        self.level = 1

    def valid(self, piece: Piece):
        for x, y in piece.get_cells():
            if x < 0 or x >= self.cols:
                return False
            if y >= self.rows:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, piece: Piece):
        for x, y in piece.get_cells():
            if 0 <= y < self.rows:
                self.grid[y][x] = piece.color
        cleared = self.clear_lines()
        if cleared > 0:
            self.score += SCORES.get(cleared, 0) * self.level
            self.lines_cleared += cleared
            self.level = 1 + self.lines_cleared // LINES_PER_LEVEL
        return cleared

    def clear_lines(self):
        """
        Membersihkan baris penuh. Efisien: scan sekali dan rebuild grid.
        """
        new_grid = []
        cleared = 0
        for r in range(self.rows):
            if all(self.grid[r][c] is not None for c in range(self.cols)):
                cleared += 1
            else:
                new_grid.append(self.grid[r])
        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(self.cols)])
        self.grid = new_grid
        return cleared

    def game_over(self):
        return any(self.grid[0][c] is not None for c in range(self.cols))

    def hard_drop_distance(self, piece: Piece):
        dist = 0
        p = piece
        while True:
            p_next = p.moved(0, 1)
            if self.valid(p_next):
                dist += 1
                p = p_next
            else:
                break
        return dist

    def try_rotate_with_kicks(self, piece: Piece, delta_rot: int):
        cand = piece.rotated(delta_rot)
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]
        for dx, dy in kicks:
            p = Piece(cand.kind, cand.x + dx, cand.y + dy)
            p.rot = cand.rot
            if self.valid(p):
                return p
        return None


# ========== Game Utility ==========
class BagGenerator:
    """
    7-bag random generator agar distribusi adil.
    """
    def __init__(self):
        self.bag = []

    def next_piece_kind(self):
        if not self.bag:
            self.bag = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
            random.shuffle(self.bag)
        return self.bag.pop()


def get_fall_interval_ms(level: int):
    base = 900
    step = 60
    interval = max(70, base - (level - 1) * step)
    return interval


# ========== Rendering ==========
def draw_cell(surface, x, y, color, outline=True):
    rect = Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    if outline:
        pygame.draw.rect(surface, GRAY_DARK, rect, 1)


def draw_board(surface, board: Board, origin_x, origin_y):
    for r in range(board.rows):
        for c in range(board.cols):
            cell_x = origin_x + c * CELL_SIZE
            cell_y = origin_y + r * CELL_SIZE
            col = board.grid[r][c]
            if col is None:
                pygame.draw.rect(surface, GRAY, (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)
            else:
                draw_cell(surface, cell_x, cell_y, col, outline=True)


def draw_piece(surface, piece: Piece, ox, oy, alpha: int = 255):
    temp_surface = None
    if alpha < 255:
        temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    for x, y in piece.get_cells():
        if y < 0:
            continue
        px = ox + x * CELL_SIZE
        py = oy + y * CELL_SIZE
        color = piece.color
        if alpha < 255:
            temp_surface.fill((*color, alpha))
            surface.blit(temp_surface, (px, py))
            pygame.draw.rect(surface, GRAY_DARK, (px, py, CELL_SIZE, CELL_SIZE), 1)
        else:
            draw_cell(surface, px, py, color, outline=True)


def draw_ghost_piece(surface, board: Board, active: Piece, ox, oy):
    dist = board.hard_drop_distance(active)
    ghost = active.moved(0, dist)
    draw_piece(surface, ghost, ox, oy, alpha=80)


def draw_next_queue(surface, queue, font, base_x, base_y):
    label = font.render("Next", True, WHITE)
    surface.blit(label, (base_x, base_y))
    y = base_y + 28
    for i, k in enumerate(queue[:5]):
        draw_mini_shape(surface, k, base_x, y + i * 80)


def draw_mini_shape(surface, kind, x, y):
    color = COLORS[kind]
    pattern = SHAPES[kind][0]
    cell = max(12, CELL_SIZE // 2)
    for r in range(len(pattern)):
        for c in range(len(pattern[r])):
            if pattern[r][c] == '#':
                px = x + c * cell
                py = y + r * cell
                rect = Rect(px, py, cell, cell)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, GRAY_DARK, rect, 1)


def draw_ui(surface, font, big_font, board: Board, base_x, base_y, elapsed_ms, paused, game_over):
    y = base_y
    title = big_font.render("TETRIS", True, WHITE)
    surface.blit(title, (base_x, y))
    y += 45
    surface.blit(font.render(f"Score: {board.score}", True, WHITE), (base_x, y)); y += 24
    surface.blit(font.render(f"Lines: {board.lines_cleared}", True, WHITE), (base_x, y)); y += 24
    surface.blit(font.render(f"Level: {board.level}", True, WHITE), (base_x, y)); y += 24

    y += 10
    surface.blit(font.render("[Left/Right] Move", True, WHITE), (base_x, y)); y += 20
    surface.blit(font.render("[Down] Soft Drop", True, WHITE), (base_x, y)); y += 20
    surface.blit(font.render("[Space] Hard Drop", True, WHITE), (base_x, y)); y += 20
    surface.blit(font.render("[Z/X/Up] Rotate", True, WHITE), (base_x, y)); y += 20
    surface.blit(font.render("[P] Pause, [R] Restart", True, WHITE), (base_x, y)); y += 20
    surface.blit(font.render("[Esc] Quit", True, WHITE), (base_x, y)); y += 20

    if paused and not game_over:
        msg = big_font.render("PAUSED", True, (255, 220, 80))
        surface.blit(msg, (base_x, y + 20))
    if game_over:
        msg = big_font.render("GAME OVER", True, (255, 80, 80))
        surface.blit(msg, (base_x - 5, y + 20))


# ========== Game Loop ==========
def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    board_px_w = COLS * CELL_SIZE
    board_px_h = ROWS * CELL_SIZE
    side_px_w = SIDE_PANEL_WIDTH * CELL_SIZE

    win_w = BORDER * 3 + board_px_w + side_px_w
    win_h = BORDER * 2 + board_px_h

    screen = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    big_font = pygame.font.SysFont("consolas", 28, bold=True)

    board = Board(COLS, ROWS)
    bag = BagGenerator()

    # queue next pieces (pre-buffer 5)
    next_queue = [bag.next_piece_kind() for _ in range(5)]

    def spawn_new_piece():
        kind = next_queue.pop(0)
        next_queue.append(bag.next_piece_kind())
        p = Piece(kind, x=(COLS - SHAPE_BOX_SIZE[kind]) // 2, y=-2)
        if not board.valid(p):
            return p, False
        return p, True

    active, ok = spawn_new_piece()

    fall_timer = 0
    lock_delay_ms = 500
    lock_timer = 0
    on_ground = False
    paused = False
    game_over = False

    soft_drop = False
    elapsed_total = 0

    # cooldown state for rotation and hard drop
    rot_cooldown = 0
    drop_cooldown = 0

    while True:
        dt = clock.tick(FPS)
        elapsed_total += dt
        rot_cooldown = max(0, rot_cooldown - dt)
        drop_cooldown = max(0, drop_cooldown - dt)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_p:
                    if not game_over:
                        paused = not paused
                if event.key == pygame.K_r:
                    # restart
                    board = Board(COLS, ROWS)
                    bag = BagGenerator()
                    next_queue = [bag.next_piece_kind() for _ in range(5)]
                    active, _ = spawn_new_piece()
                    paused = False
                    game_over = False
                    fall_timer = 0
                    lock_timer = 0
                    on_ground = False
                    soft_drop = False
                    rot_cooldown = 0
                    drop_cooldown = 0

        if paused or game_over:
            render(screen, board, active, next_queue, font, big_font, elapsed_total, paused, game_over)
            continue

        keys = pygame.key.get_pressed()
        moved_this_frame = False

        # Horizontal move (single-step per frame)
        move_dx = 0
        if keys[pygame.K_LEFT]:
            move_dx = -1
        elif keys[pygame.K_RIGHT]:
            move_dx = 1
        if move_dx != 0:
            p2 = active.moved(move_dx, 0)
            if board.valid(p2):
                active = p2
                moved_this_frame = True

        # Rotation with simple cooldown
        if rot_cooldown == 0:
            if keys[pygame.K_z]:
                cand = board.try_rotate_with_kicks(active, -1)
                if cand:
                    active = cand
                    moved_this_frame = True
                rot_cooldown = 120
            elif keys[pygame.K_x] or keys[pygame.K_UP]:
                cand = board.try_rotate_with_kicks(active, +1)
                if cand:
                    active = cand
                    moved_this_frame = True
                rot_cooldown = 120

        # Soft drop
        soft_drop = bool(keys[pygame.K_DOWN])

        # Hard drop (Space) dengan cooldown
        if drop_cooldown == 0 and keys[pygame.K_SPACE]:
            dist = board.hard_drop_distance(active)
            if dist > 0:
                board.score += dist * HARD_DROP_BONUS
            active = active.moved(0, dist)
            board.lock_piece(active)
            active, ok = spawn_new_piece()
            if not ok or board.game_over():
                game_over = True
            fall_timer = 0
            lock_timer = 0
            on_ground = False
            drop_cooldown = 150

        # Gravity
        fall_interval = get_fall_interval_ms(board.level)
        gravity_ms = 30 if soft_drop else fall_interval

        fall_timer += dt

        # Ground contact check
        if board.valid(active.moved(0, 1)):
            on_ground = False
            lock_timer = 0
        else:
            if not on_ground:
                on_ground = True
                lock_timer = 0
            else:
                lock_timer += dt

        # Turun otomatis
        while fall_timer >= gravity_ms:
            fall_timer -= gravity_ms
            p2 = active.moved(0, 1)
            if board.valid(p2):
                active = p2
                if soft_drop:
                    board.score += SOFT_DROP_BONUS
            else:
                on_ground = True
                break

        # Lock delay
        if on_ground and lock_timer >= lock_delay_ms:
            board.lock_piece(active)
            active, ok = spawn_new_piece()
            if not ok or board.game_over():
                game_over = True
            fall_timer = 0
            lock_timer = 0
            on_ground = False

        render(screen, board, active, next_queue, font, big_font, elapsed_total, paused, game_over)


def render(screen, board, active, next_queue, font, big_font, elapsed_ms, paused, game_over):
    screen.fill(GRAY_DARK)

    board_px_w = COLS * CELL_SIZE
    board_px_h = ROWS * CELL_SIZE
    side_px_w = SIDE_PANEL_WIDTH * CELL_SIZE

    board_ox = BORDER
    board_oy = BORDER
    side_ox = BORDER * 2 + board_px_w
    side_oy = BORDER

    # Board panel background
    pygame.draw.rect(screen, GRAY, (board_ox - 2, board_oy - 2, board_px_w + 4, board_px_h + 4), 2)

    draw_board(screen, board, board_ox, board_oy)

    # Ghost
    if active is not None and not game_over:
        draw_ghost_piece(screen, board, active, board_ox, board_oy)

    # Active
    if active is not None:
        draw_piece(screen, active, board_ox, board_oy, alpha=255)

    # Side panel
    pygame.draw.rect(screen, GRAY, (side_ox - 2, side_oy - 2, side_px_w + 4, board_px_h + 4), 2)
    draw_ui(screen, font, big_font, board, side_ox + 10, side_oy + 10, elapsed_ms, paused, game_over)

    # Next queue
    draw_next_queue(screen, next_queue, font, side_ox + 10, side_oy + 200)

    pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pygame.quit()
        raise
