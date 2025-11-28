import sys
import random
import pygame
from typing import List, Tuple, Optional

# -----------------------------
# Config & Constants
# -----------------------------
CELL_SIZE = 32
COLUMNS = 10
ROWS = 20
SIDE_PANEL_WIDTH = 200
FPS = 60

# Timers (in milliseconds)
GRAVITY_INITIAL_MS = 800  # drop interval at level 1
GRAVITY_MIN_MS = 80
LOCK_DELAY_MS = 500
SOFT_DROP_MULTIPLIER = 0.15
LEVEL_UP_LINES = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)

# Tetromino colors
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
}

# Tetromino rotation definitions as offsets (x, y) per rotation
# Each list entry is a rotation state. Each rotation state is a list of 4 (x,y) offsets
# relative to piece's (x, y) position which refers to top-left of a 4x4 box anchor.
# The definitions align to a simple SRS-like layout suitable for grid tests.
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # ----
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # | vertical
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
}

# Wall kick tests (simple)
KICK_TESTS = [(0, 0), (1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0)]


class Piece:
    def __init__(self, kind: str):
        self.kind = kind
        self.color = COLORS[kind]
        self.rotation = 0
        # Start near top-center; x,y reference is top-left of 4x4 box
        self.x = COLUMNS // 2 - 2
        self.y = -2  # allow spawn above visible grid

    def cells(self, rotation: Optional[int] = None, offset: Tuple[int, int] = (0, 0)) -> List[Tuple[int, int]]:
        r = self.rotation if rotation is None else rotation
        ox, oy = offset
        result = []
        for dx, dy in SHAPES[self.kind][r]:
            result.append((self.x + dx + ox, self.y + dy + oy))
        return result

    def rotate(self, dr: int):
        self.rotation = (self.rotation + dr) % 4


class Board:
    def __init__(self, columns: int, rows: int):
        self.columns = columns
        self.rows = rows
        # Grid holds RGB tuples or None
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(columns)] for _ in range(rows)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

        self.current: Piece = self._new_piece()
        self.next_queue: List[Piece] = self._bag()
        self.hold: Optional[Piece] = None
        self.can_hold = True

        self.gravity_ms = GRAVITY_INITIAL_MS
        self.last_fall_time = 0
        self.lock_timer_start: Optional[int] = None

    def _bag(self) -> List[Piece]:
        kinds = list(SHAPES.keys())
        random.shuffle(kinds)
        return [Piece(k) for k in kinds]

    def _new_piece(self) -> Piece:
        kinds = list(SHAPES.keys())
        return Piece(random.choice(kinds))

    def spawn_next(self):
        if not self.next_queue:
            self.next_queue = self._bag()
        self.current = self.next_queue.pop(0)
        self.can_hold = True
        self.lock_timer_start = None

        # If spawn overlaps, game over will be detected by immediate invalid state after gravity tick

    def valid(self, cells: List[Tuple[int, int]]) -> bool:
        for x, y in cells:
            if x < 0 or x >= self.columns or y >= self.rows:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def move(self, dx: int, dy: int) -> bool:
        new_cells = self.current.cells(offset=(dx, dy))
        if self.valid(new_cells):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self, dr: int) -> bool:
        new_r = (self.current.rotation + dr) % 4
        for kx, ky in KICK_TESTS:
            new_cells = self.current.cells(rotation=new_r, offset=(kx, ky))
            if self.valid(new_cells):
                self.current.rotation = new_r
                self.current.x += kx
                self.current.y += ky
                return True
        return False

    def hard_drop_distance(self) -> int:
        dy = 0
        while True:
            test_cells = self.current.cells(offset=(0, dy + 1))
            if self.valid(test_cells):
                dy += 1
            else:
                break
        return dy

    def hard_drop(self) -> int:
        dy = self.hard_drop_distance()
        self.current.y += dy
        self.lock_piece()
        return dy

    def start_lock_timer(self, now_ms: int):
        if self.lock_timer_start is None:
            self.lock_timer_start = now_ms

    def reset_lock_timer(self):
        self.lock_timer_start = None

    def tick_gravity(self, now_ms: int, soft: bool = False) -> bool:
        interval = int(self.gravity_ms * (SOFT_DROP_MULTIPLIER if soft else 1.0))
        if now_ms - self.last_fall_time >= max(interval, 10):
            if not self.move(0, 1):
                self.start_lock_timer(now_ms)
            else:
                self.reset_lock_timer()
            self.last_fall_time = now_ms
            return True
        return False

    def lock_piece(self):
        for x, y in self.current.cells():
            if y >= 0:
                self.grid[y][x] = self.current.color
        cleared = self.clear_lines()
        self.update_level_and_speed(cleared)
        self.spawn_next()

    def clear_lines(self) -> int:
        # Efficient line clearing
        new_rows: List[List[Optional[Tuple[int, int, int]]]] = []
        cleared = 0
        for row in self.grid:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_rows.append(row)
        for _ in range(cleared):
            new_rows.insert(0, [None for _ in range(self.columns)])
        if cleared:
            self.grid = new_rows
            self.lines_cleared += cleared
            # Basic scoring: 100, 300, 500, 800 per 1,2,3,4 lines times level
            score_map = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += score_map.get(cleared, 1000) * self.level
        return cleared

    def update_level_and_speed(self, cleared: int):
        if cleared <= 0:
            return
        level_before = self.level
        while self.lines_cleared // LEVEL_UP_LINES + 1 > self.level:
            self.level += 1
        if self.level != level_before:
            # Speed up; ensure a floor so it never becomes 0
            self.gravity_ms = max(int(GRAVITY_INITIAL_MS * (0.85 ** (self.level - 1))), GRAVITY_MIN_MS)

    def hold_piece(self):
        if not self.can_hold:
            return
        if self.hold is None:
            self.hold = Piece(self.current.kind)
            self.spawn_next()
        else:
            self.hold, self.current = Piece(self.current.kind), self.hold
            # reset position/rotation for swapped-in piece
            self.current.x = COLUMNS // 2 - 2
            self.current.y = -2
            self.current.rotation = 0
        self.can_hold = False
        self.lock_timer_start = None

    def game_over(self) -> bool:
        # If any cell of spawn collides immediately after spawn/move down blocked above grid
        for x, y in self.current.cells():
            if y < 0:
                # Check if can't move down because blocked already -> treat as game over condition
                if not self.valid(self.current.cells(offset=(0, 1))):
                    return True
        return False

    def ghost_cells(self) -> List[Tuple[int, int]]:
        drop = self.hard_drop_distance()
        return self.current.cells(offset=(0, drop))


def draw_grid(surface: pygame.Surface, board: Board, offset_x: int, offset_y: int):
    # Background grid
    for y in range(ROWS):
        for x in range(COLUMNS):
            rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, DARK_GRAY, rect, 1)

    # Locked blocks
    for y in range(ROWS):
        for x in range(COLUMNS):
            color = board.grid[y][x]
            if color is not None:
                rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

    # Ghost piece (draw as outline)
    ghost = board.ghost_cells()
    for x, y in ghost:
        if y < 0:
            continue
        rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, LIGHT_GRAY, rect, 2)

    # Current piece
    for x, y in board.current.cells():
        if y < 0:
            continue
        rect = pygame.Rect(offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, board.current.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_side_panel(surface: pygame.Surface, board: Board, offset_x: int, offset_y: int, font: pygame.font.Font):
    # Text info
    texts = [
        f"Score: {board.score}",
        f"Level: {board.level}",
        f"Lines: {board.lines_cleared}",
        "",
        "Controls:",
        "Left/Right: Move",
        "Up/Z: Rotate CW/CCW",
        "Down: Soft Drop",
        "Space: Hard Drop",
        "C: Hold",
        "Esc: Quit",
    ]
    ty = offset_y
    for t in texts:
        surf = font.render(t, True, WHITE)
        surface.blit(surf, (offset_x, ty))
        ty += surf.get_height() + 6

    # Next pieces preview (show first 3)
    preview_y = ty + 10
    label = font.render("Next:", True, WHITE)
    surface.blit(label, (offset_x, preview_y))
    preview_y += label.get_height() + 6
    for i, p in enumerate(board.next_queue[:3]):
        draw_piece_preview(surface, p.kind, offset_x, preview_y + i * (CELL_SIZE * 3))

    # Hold preview
    preview_y += CELL_SIZE * 10
    label = font.render("Hold:", True, WHITE)
    surface.blit(label, (offset_x, preview_y))
    preview_y += label.get_height() + 6
    if board.hold is not None:
        draw_piece_preview(surface, board.hold.kind, offset_x, preview_y)


def draw_piece_preview(surface: pygame.Surface, kind: str, ox: int, oy: int):
    color = COLORS[kind]
    # Draw within a 4x3 box
    for dx, dy in SHAPES[kind][0]:
        rect = pygame.Rect(ox + dx * (CELL_SIZE // 1.5), oy + dy * (CELL_SIZE // 1.5), int(CELL_SIZE // 1.5), int(CELL_SIZE // 1.5))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def main():
    pygame.init()
    pygame.display.set_caption("Tetris - OOP with Ghost Piece")

    grid_w = COLUMNS * CELL_SIZE
    grid_h = ROWS * CELL_SIZE
    screen_w = grid_w + SIDE_PANEL_WIDTH
    screen_h = grid_h

    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    board = Board(COLUMNS, ROWS)

    running = True
    soft_drop = False

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    if board.move(-1, 0):
                        board.reset_lock_timer()
                elif event.key == pygame.K_RIGHT:
                    if board.move(1, 0):
                        board.reset_lock_timer()
                elif event.key == pygame.K_DOWN:
                    soft_drop = True
                elif event.key == pygame.K_UP:
                    if board.rotate(1):
                        board.reset_lock_timer()
                elif event.key == pygame.K_z:
                    if board.rotate(-1):
                        board.reset_lock_timer()
                elif event.key == pygame.K_SPACE:
                    board.hard_drop()
                elif event.key == pygame.K_c:
                    board.hold_piece()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop = False

        # Gravity tick
        board.tick_gravity(now, soft=soft_drop)

        # Lock delay handling
        if board.lock_timer_start is not None and now - board.lock_timer_start >= LOCK_DELAY_MS:
            # If still cannot move down, lock
            if not board.move(0, 1):
                board.lock_piece()
            board.reset_lock_timer()

        # Game over detection
        if board.game_over():
            running = False

        # Rendering
        screen.fill((20, 20, 30))
        draw_grid(screen, board, 0, 0)
        draw_side_panel(screen, board, grid_w + 16, 16, font)

        pygame.display.flip()
        clock.tick(FPS)

    # Game Over screen
    screen.fill((10, 10, 15))
    over_msg = font.render("Game Over - Press any key to exit", True, WHITE)
    score_msg = font.render(f"Final Score: {board.score}", True, WHITE)
    screen.blit(over_msg, (screen_w // 2 - over_msg.get_width() // 2, screen_h // 2 - 20))
    screen.blit(score_msg, (screen_w // 2 - score_msg.get_width() // 2, screen_h // 2 + 10))
    pygame.display.flip()

    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                wait = False
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
