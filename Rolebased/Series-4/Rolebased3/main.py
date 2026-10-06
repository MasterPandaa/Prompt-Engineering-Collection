import sys
import math
import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

# =============================
# TETRIS CONFIGURATION CONSTANTS
# =============================
WINDOW_TITLE = "Tetris - OOP, Ghost Piece, Efficient Line Clear"
CELL_SIZE = 30  # Pixel size per grid cell
COLUMNS = 10
ROWS = 20
SIDE_PANEL_WIDTH = 6  # columns width for side panel rendering
FPS = 60

# Gravity speeds (in seconds per row) per level, roughly following NES pace but simplified
LEVEL_SPEEDS = [
    0.80, 0.72, 0.63, 0.55, 0.47, 0.38, 0.30, 0.22, 0.13, 0.10,
    0.09, 0.08, 0.07, 0.06, 0.05
]

# Colors
BLACK   = (10, 10, 12)
GRAY    = (40, 40, 46)
LIGHT   = (200, 200, 208)
WHITE   = (240, 240, 248)
BORDER  = (70, 70, 78)
GHOST   = (180, 180, 190)

COLORS = {
    'I': (0, 240, 240),   # Cyan
    'J': (0, 0, 240),     # Blue
    'L': (240, 160, 0),   # Orange
    'O': (240, 240, 0),   # Yellow
    'S': (0, 240, 0),     # Green
    'T': (160, 0, 240),   # Purple
    'Z': (240, 0, 0),     # Red
}

# Tetromino rotation states (0..3) with 4x4 matrices
# Using right-handed (clockwise) rotation. Shapes are defined in state 0.
TETROMINO_SHAPES: Dict[str, List[List[Tuple[int, int]]]] = {}

# Helper to construct shape from 4x4 strings into cell coordinate lists per rotation

def shape_from_grid(grid: List[str]) -> List[Tuple[int, int]]:
    coords = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == 'X':
                coords.append((x, y))
    return coords

# Base definitions for rotation state 0 (within a 4x4 box)
SHAPE_DEFS = {
    'I': [
        "....",
        "XXXX",
        "....",
        "....",
    ],
    'J': [
        "X..",
        "XXX",
        "...",
        "...",
    ],
    'L': [
        "..X",
        "XXX",
        "...",
        "...",
    ],
    'O': [
        ".XX.",
        ".XX.",
        "....",
        "....",
    ],
    'S': [
        ".XX",
        "XX.",
        "...",
        "...",
    ],
    'T': [
        ".X.",
        "XXX",
        "...",
        "...",
    ],
    'Z': [
        "XX.",
        ".XX",
        "...",
        "...",
    ],
}

# Precompute rotation states by rotating around the 4x4 box center
for name, grid in SHAPE_DEFS.items():
    base = shape_from_grid(grid)

    def rotate_point(px: int, py: int) -> Tuple[int, int]:
        # rotate 90 deg CW within 4x4: (x, y) -> (3 - y, x)
        return (3 - py, px)

    states = []
    cur = base
    for r in range(4):
        states.append(cur)
        # rotate each cell
        cur = [rotate_point(x, y) for (x, y) in cur]
    TETROMINO_SHAPES[name] = states

# Super simple wall-kick data (not full SRS), but good enough for robust play
# Order of kicks to try when rotating CW or CCW
WALL_KICKS = [
    (0, 0), (1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0)
]


@dataclass
class Piece:
    kind: str
    x: int
    y: int
    rotation: int = 0

    @property
    def color(self) -> Tuple[int, int, int]:
        return COLORS[self.kind]

    def cells(self, rot: Optional[int] = None) -> List[Tuple[int, int]]:
        r = self.rotation if rot is None else rot % 4
        return [(self.x + cx, self.y + cy) for (cx, cy) in TETROMINO_SHAPES[self.kind][r]]

    def rotated(self, dr: int) -> 'Piece':
        return Piece(self.kind, self.x, self.y, (self.rotation + dr) % 4)


class Board:
    def __init__(self, cols: int = COLUMNS, rows: int = ROWS):
        self.cols = cols
        self.rows = rows
        # grid[y][x] -> None or color tuple
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]
        self.current: Optional[Piece] = None
        self.hold: Optional[str] = None
        self.can_hold: bool = True
        self.bag: List[str] = []
        self.next_queue: List[str] = []
        self.score: int = 0
        self.lines_cleared: int = 0
        self.level: int = 1
        self.game_over: bool = False
        # Pre-fill next queue
        for _ in range(5):
            self.next_queue.append(self._next_from_bag())

    # ---------- Piece Spawning and Bag ----------
    def _refill_bag(self):
        self.bag = list(SHAPE_DEFS.keys())
        random.shuffle(self.bag)

    def _next_from_bag(self) -> str:
        if not self.bag:
            self._refill_bag()
        return self.bag.pop()

    def spawn(self):
        if not self.next_queue:
            self.next_queue.append(self._next_from_bag())
        kind = self.next_queue.pop(0)
        self.next_queue.append(self._next_from_bag())
        # Spawn near top center
        spawn_x = self.cols // 2 - 2
        spawn_y = 0
        piece = Piece(kind, spawn_x, spawn_y, 0)
        # Small vertical tweak for some pieces to start slightly above
        if kind == 'I':
            piece.y = -1
        if not self._valid(piece):
            self.game_over = True
        else:
            self.current = piece
            self.can_hold = True

    def hold_piece(self):
        if not self.can_hold or not self.current:
            return
        cur_kind = self.current.kind
        if self.hold is None:
            self.hold = cur_kind
            self.spawn()
        else:
            self.current = Piece(self.hold, self.cols // 2 - 2, 0, 0)
            self.hold = cur_kind
            if not self._valid(self.current):
                self.game_over = True
        self.can_hold = False

    # ---------- Validation and Movement ----------
    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and y < self.rows

    def _valid(self, piece: Piece) -> bool:
        for (x, y) in piece.cells():
            if y < 0:
                # allow spawn above visible board
                if not (0 <= x < self.cols):
                    return False
                continue
            if not self._in_bounds(x, y) or self.grid[y][x] is not None:
                return False
        return True

    def try_move(self, dx: int, dy: int) -> bool:
        if not self.current:
            return False
        moved = Piece(self.current.kind, self.current.x + dx, self.current.y + dy, self.current.rotation)
        if self._valid(moved):
            self.current = moved
            return True
        return False

    def try_rotate(self, dr: int) -> bool:
        if not self.current:
            return False
        rotated = self.current.rotated(dr)
        # Try wall kicks
        for (kx, ky) in WALL_KICKS:
            candidate = Piece(rotated.kind, rotated.x + kx, rotated.y + ky, rotated.rotation)
            if self._valid(candidate):
                self.current = candidate
                return True
        return False

    # ---------- Locking and Line Clearing ----------
    def hard_drop_distance(self) -> int:
        if not self.current:
            return 0
        dist = 0
        tmp = Piece(self.current.kind, self.current.x, self.current.y, self.current.rotation)
        while True:
            nxt = Piece(tmp.kind, tmp.x, tmp.y + 1, tmp.rotation)
            if self._valid(nxt):
                tmp = nxt
                dist += 1
            else:
                break
        return dist

    def hard_drop(self):
        if not self.current:
            return
        drop = self.hard_drop_distance()
        self.current = Piece(self.current.kind, self.current.x, self.current.y + drop, self.current.rotation)
        self.lock_piece()
        # reward instant drop
        self.score += 2 * drop

    def soft_drop(self) -> bool:
        moved = self.try_move(0, 1)
        if moved:
            self.score += 1
        return moved

    def lock_piece(self):
        if not self.current:
            return
        for (x, y) in self.current.cells():
            if y < 0:
                # Locked above board -> game over
                self.game_over = True
                continue
            self.grid[y][x] = self.current.color
        self.current = None
        self._clear_lines_efficient()
        self.spawn()

    def _clear_lines_efficient(self):
        # Keep rows that are not full; count cleared lines, then add empty rows at top.
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = self.rows - len(new_grid)
        if cleared > 0:
            empty_rows = [[None for _ in range(self.cols)] for _ in range(cleared)]
            self.grid = empty_rows + new_grid
            self._apply_scoring(cleared)

    def _apply_scoring(self, cleared: int):
        # Simple Tetris scoring
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores.get(cleared, 0) * self.level
        self.lines_cleared += cleared
        self.level = 1 + self.lines_cleared // 10

    # ---------- Ghost Piece ----------
    def ghost_cells(self) -> List[Tuple[int, int]]:
        if not self.current:
            return []
        dist = self.hard_drop_distance()
        return [(x, y + dist) for (x, y) in self.current.cells()]


class Game:
    def __init__(self):
        pygame.init()
        panel_px = SIDE_PANEL_WIDTH * CELL_SIZE
        self.width = COLUMNS * CELL_SIZE + panel_px
        self.height = ROWS * CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 18)
        self.font_medium = pygame.font.SysFont("consolas", 22)
        self.font_big = pygame.font.SysFont("consolas", 32)
        self.board = Board(COLUMNS, ROWS)
        self.board.spawn()
        self.time_since_gravity = 0.0

    # ---------- Rendering ----------
    def draw_cell(self, x: int, y: int, color: Tuple[int, int, int], alpha: int = 255):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if alpha == 255:
            pygame.draw.rect(self.screen, color, rect)
        else:
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surface.fill((*color, alpha))
            self.screen.blit(surface, rect.topleft)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

    def render_board(self):
        # Background
        playfield_rect = pygame.Rect(0, 0, COLUMNS * CELL_SIZE, ROWS * CELL_SIZE)
        self.screen.fill(GRAY, playfield_rect)
        # Locked cells
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                color = self.board.grid[y][x]
                if color is not None:
                    self.draw_cell(x, y, color)
        # Ghost piece
        if self.board.current:
            for (x, y) in self.board.ghost_cells():
                if y >= 0:
                    self.draw_cell(x, y, GHOST, alpha=100)
        # Current piece
        if self.board.current:
            for (x, y) in self.board.current.cells():
                if y >= 0:
                    self.draw_cell(x, y, self.board.current.color)

    def render_panel(self):
        start_x = COLUMNS * CELL_SIZE
        panel_rect = pygame.Rect(start_x, 0, self.width - start_x, self.height)
        self.screen.fill(BLACK, panel_rect)
        pad = 10
        x = start_x + pad
        y = pad

        # Title
        title = self.font_big.render("TETRIS", True, WHITE)
        self.screen.blit(title, (x, y))
        y += 50

        # Score/Level/Lines
        stats = [
            ("Score", str(self.board.score)),
            ("Level", str(self.board.level)),
            ("Lines", str(self.board.lines_cleared)),
        ]
        for label, value in stats:
            t1 = self.font_medium.render(label + ":", True, LIGHT)
            t2 = self.font_medium.render(value, True, WHITE)
            self.screen.blit(t1, (x, y))
            self.screen.blit(t2, (x + 90, y))
            y += 28

        y += 10
        # Next queue preview
        nxt_label = self.font_medium.render("Next:", True, LIGHT)
        self.screen.blit(nxt_label, (x, y))
        y += 24
        self.draw_preview_list(self.board.next_queue[:5], x, y)

        # Hold piece
        y += 5 * CELL_SIZE + 20
        hold_label = self.font_medium.render("Hold:", True, LIGHT)
        self.screen.blit(hold_label, (x, y))
        y += 24
        if self.board.hold:
            self.draw_preview_piece(self.board.hold, x, y)

        # Controls
        y = self.height - 160
        controls = [
            "←/→: Move",
            "↑/Z/X: Rotate",
            "↓: Soft drop",
            "Space: Hard drop",
            "C: Hold",
            "Esc: Quit",
        ]
        for c in controls:
            t = self.font_small.render(c, True, LIGHT)
            self.screen.blit(t, (x, y))
            y += 20

    def draw_preview_list(self, kinds: List[str], x: int, y: int):
        for i, k in enumerate(kinds):
            self.draw_preview_piece(k, x, y + i * CELL_SIZE)

    def draw_preview_piece(self, kind: str, x: int, y: int):
        # Draw on a small 4x3 area
        preview_surface = pygame.Surface((4 * CELL_SIZE, 3 * CELL_SIZE), pygame.SRCALPHA)
        preview_surface.fill((0, 0, 0, 0))
        color = COLORS[kind]
        # Place piece centered in preview
        cells = TETROMINO_SHAPES[kind][0]
        min_x = min(cx for cx, _ in cells)
        max_x = max(cx for cx, _ in cells)
        min_y = min(cy for _, cy in cells)
        max_y = max(cy for _, cy in cells)
        width = (max_x - min_x + 1)
        height = (max_y - min_y + 1)
        offset_x = (4 - width) // 2 - min_x
        offset_y = (3 - height) // 2 - min_y
        for (cx, cy) in cells:
            rx = (cx + offset_x) * CELL_SIZE
            ry = (cy + offset_y) * CELL_SIZE
            rect = pygame.Rect(rx, ry, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(preview_surface, color, rect)
            pygame.draw.rect(preview_surface, BORDER, rect, 1)
        self.screen.blit(preview_surface, (x, y))

    # ---------- Input & Update ----------
    def handle_input(self, dt: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.board.game_over:
                    continue
                if event.key == pygame.K_LEFT:
                    self.board.try_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.board.try_move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.board.soft_drop()
                elif event.key in (pygame.K_UP, pygame.K_x):
                    self.board.try_rotate(1)  # CW
                elif event.key == pygame.K_z:
                    self.board.try_rotate(-1)  # CCW
                elif event.key == pygame.K_SPACE:
                    self.board.hard_drop()
                elif event.key == pygame.K_c:
                    self.board.hold_piece()

        # Simple DAS/ARR handling (held keys) for smooth movement
        keys = pygame.key.get_pressed()
        if not self.board.game_over:
            if keys[pygame.K_LEFT]:
                # move left gradually
                self._repeat_move(-1)
            elif keys[pygame.K_RIGHT]:
                self._repeat_move(1)

    def _repeat_move(self, dx: int):
        # Minimalist key repeat using time mod; avoids storing extra timers
        # This provides a gentle continuous move if key held
        if not hasattr(self, '_move_accum'):
            self._move_accum = 0.0
        self._move_accum += self.clock.get_time() / 1000.0
        # Move every ~0.10s when key held
        if self._move_accum > 0.10:
            self.board.try_move(dx, 0)
            self._move_accum = 0.0

    def gravity_interval(self) -> float:
        idx = min(self.board.level - 1, len(LEVEL_SPEEDS) - 1)
        return LEVEL_SPEEDS[idx]

    def update(self, dt: float):
        if self.board.game_over:
            return
        self.time_since_gravity += dt
        interval = self.gravity_interval()
        while self.time_since_gravity >= interval:
            self.time_since_gravity -= interval
            moved = self.board.try_move(0, 1)
            if not moved:
                self.board.lock_piece()
                break

    # ---------- Game Loop ----------
    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            self.handle_input(dt)
            self.update(dt)

            # Draw
            self.screen.fill(BLACK)
            self.render_board()
            self.render_panel()

            if self.board.game_over:
                self.draw_game_over()

            pygame.display.flip()

    def draw_game_over(self):
        overlay = pygame.Surface((COLUMNS * CELL_SIZE, ROWS * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((20, 20, 24, 170))
        self.screen.blit(overlay, (0, 0))
        msg = self.font_big.render("GAME OVER", True, WHITE)
        sub = self.font_medium.render("Press ESC to quit", True, LIGHT)
        cx = (COLUMNS * CELL_SIZE) // 2
        cy = (ROWS * CELL_SIZE) // 2
        self.screen.blit(msg, (cx - msg.get_width() // 2, cy - 30))
        self.screen.blit(sub, (cx - sub.get_width() // 2, cy + 10))


if __name__ == "__main__":
    Game().run()
