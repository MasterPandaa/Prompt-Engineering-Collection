import sys
import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Optional

# --- Config ---
WIDTH, HEIGHT = 480, 720
GRID_COLS, GRID_ROWS = 10, 20
CELL = 32
PLAYFIELD_WIDTH = GRID_COLS * CELL
PLAYFIELD_HEIGHT = GRID_ROWS * CELL
MARGIN_LEFT = 40
MARGIN_TOP = 40
FPS = 60

# Gravity timing (seconds per row) by level
GRAVITY_TABLE = [
    0.8, 0.716, 0.633, 0.55, 0.466, 0.383, 0.3, 0.216, 0.133, 0.1,
    0.083, 0.066, 0.05, 0.033, 0.016
]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)

# Tetromino colors
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0)
}

# Shapes defined as rotation states: list of list of (x, y) cell offsets
SHAPES = {
    'I': [
        [( -1, 0), (0, 0), (1, 0), (2, 0)],
        [( 1, -1), (1, 0), (1, 1), (1, 2)],
        [( -1, 1), (0, 1), (1, 1), (2, 1)],
        [( 0, -1), (0, 0), (0, 1), (0, 2)],
    ],
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    'T': [
        [(0, 0), (-1, 0), (1, 0), (0, -1)],
        [(0, 0), (0, -1), (0, 1), (1, 0)],
        [(0, 0), (-1, 0), (1, 0), (0, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, 0)],
    ],
    'S': [
        [(0, 0), (1, 0), (0, -1), (-1, -1)],
        [(0, 0), (0, -1), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (-1, 1)],
        [(0, 0), (-1, 0), (-1, -1), (0, 1)],
    ],
    'Z': [
        [(0, 0), (-1, 0), (0, -1), (1, -1)],
        [(0, 0), (0, -1), (-1, 0), (-1, 1)],
        [(0, 0), (-1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (1, -1), (0, 1)],
    ],
    'J': [
        [(0, 0), (-1, 0), (1, 0), (-1, -1)],
        [(0, 0), (0, -1), (0, 1), (1, -1)],
        [(0, 0), (-1, 0), (1, 0), (1, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, 1)],
    ],
    'L': [
        [(0, 0), (-1, 0), (1, 0), (1, -1)],
        [(0, 0), (0, -1), (0, 1), (1, 1)],
        [(0, 0), (-1, 0), (1, 0), (-1, 1)],
        [(0, 0), (0, -1), (0, 1), (-1, -1)],
    ],
}

# Basic wall-kick tests (not full SRS but effective)
KICK_TESTS = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]


@dataclass
class Piece:
    kind: str
    x: int
    y: int
    rotation: int = 0

    def cells(self) -> List[Tuple[int, int]]:
        offsets = SHAPES[self.kind][self.rotation]
        return [(self.x + dx, self.y + dy) for dx, dy in offsets]

    @property
    def color(self) -> Tuple[int, int, int]:
        return COLORS[self.kind]

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def rotated(self, dr: int) -> 'Piece':
        return Piece(self.kind, self.x, self.y, (self.rotation + dr) % 4)


class Board:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]
        self.current: Optional[Piece] = None
        self.next_queue: List[str] = []
        self.lines_cleared = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self._refill_bag()

    # --- Piece management ---
    def _refill_bag(self):
        bag = list(SHAPES.keys())
        random.shuffle(bag)
        self.next_queue.extend(bag)

    def spawn_piece(self):
        if len(self.next_queue) < 7:
            self._refill_bag()
        kind = self.next_queue.pop(0)
        # spawn near top center
        spawn_x = self.cols // 2
        spawn_y = 1 if kind == 'I' else 0
        piece = Piece(kind, spawn_x, spawn_y, 0)
        # Adjust x for centered shapes (since shapes use local origin)
        # Try small offsets to fit at spawn
        for dx in [0, -1, -2, 1, 2]:
            test = Piece(kind, spawn_x + dx, spawn_y, 0)
            if self.is_valid_position(test):
                self.current = test
                return
        # If cannot place, game over
        self.current = piece
        if not self.is_valid_position(piece):
            self.game_over = True

    # --- Validation and collision ---
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and y < self.rows

    def is_cell_free(self, x: int, y: int) -> bool:
        if y < 0:
            return True  # allow above the top
        return self.in_bounds(x, y) and self.grid[y][x] is None

    def is_valid_position(self, piece: Piece) -> bool:
        for x, y in piece.cells():
            if not self.is_cell_free(x, y):
                return False
        return True

    # --- Movement ---
    def try_move(self, dx: int, dy: int) -> bool:
        if not self.current:
            return False
        test = Piece(self.current.kind, self.current.x + dx, self.current.y + dy, self.current.rotation)
        if self.is_valid_position(test):
            self.current = test
            return True
        return False

    def try_rotate(self, dr: int) -> bool:
        if not self.current:
            return False
        rotated = self.current.rotated(dr)
        for kx, ky in KICK_TESTS:
            test = Piece(rotated.kind, rotated.x + kx, rotated.y + ky, rotated.rotation)
            if self.is_valid_position(test):
                self.current = test
                return True
        return False

    # --- Locking and line clear ---
    def lock_piece(self):
        if not self.current:
            return
        for x, y in self.current.cells():
            if y < 0:
                self.game_over = True
                continue
            if 0 <= y < self.rows and 0 <= x < self.cols:
                self.grid[y][x] = self.current.color
        cleared = self.clear_lines()
        self.update_score(cleared)
        self.current = None

    def clear_lines(self) -> int:
        # Efficient single pass: build new rows list skipping full ones
        new_rows: List[List[Optional[Tuple[int, int, int]]]] = []
        cleared = 0
        for y in range(self.rows):
            if all(self.grid[y][x] is not None for x in range(self.cols)):
                cleared += 1
            else:
                new_rows.append(self.grid[y])
        # add empty rows on top
        for _ in range(cleared):
            new_rows.insert(0, [None for _ in range(self.cols)])
        if cleared:
            self.grid = new_rows
            self.lines_cleared += cleared
        return cleared

    def update_score(self, cleared: int):
        # Basic scoring similar to classic
        scores = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += scores.get(cleared, 0) * max(1, self.level)
        # Increase level every 10 lines
        self.level = 1 + self.lines_cleared // 10

    # --- Ghost piece ---
    def ghost_position(self) -> Optional[Piece]:
        if not self.current:
            return None
        ghost = Piece(self.current.kind, self.current.x, self.current.y, self.current.rotation)
        while True:
            test = Piece(ghost.kind, ghost.x, ghost.y + 1, ghost.rotation)
            if self.is_valid_position(test):
                ghost = test
            else:
                break
        return ghost

    # --- Hard drop ---
    def hard_drop(self):
        if not self.current:
            return 0
        dist = 0
        while self.try_move(0, 1):
            dist += 1
        self.lock_piece()
        return dist

    # --- Rendering ---
    def draw_cell(self, surf: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        px = MARGIN_LEFT + x * CELL
        py = MARGIN_TOP + y * CELL
        rect = pygame.Rect(px, py, CELL, CELL)
        pygame.draw.rect(surf, color, rect)
        pygame.draw.rect(surf, DARK_GRAY, rect, 2)

    def draw_grid(self, surf: pygame.Surface):
        # background grid
        for y in range(self.rows):
            for x in range(self.cols):
                col = self.grid[y][x]
                if col is None:
                    # draw empty cell outline
                    px = MARGIN_LEFT + x * CELL
                    py = MARGIN_TOP + y * CELL
                    rect = pygame.Rect(px, py, CELL, CELL)
                    pygame.draw.rect(surf, (28, 28, 28), rect)
                    pygame.draw.rect(surf, (55, 55, 55), rect, 1)
                else:
                    self.draw_cell(surf, x, y, col)

        # ghost
        ghost = self.ghost_position()
        if ghost:
            for x, y in ghost.cells():
                if y < 0:
                    continue
                px = MARGIN_LEFT + x * CELL
                py = MARGIN_TOP + y * CELL
                rect = pygame.Rect(px, py, CELL, CELL)
                # ghost as outline
                pygame.draw.rect(surf, GRAY, rect, 2)

        # current
        if self.current:
            for x, y in self.current.cells():
                if y < 0:
                    continue
                self.draw_cell(surf, x, y, self.current.color)

        # border
        border_rect = pygame.Rect(MARGIN_LEFT, MARGIN_TOP, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT)
        pygame.draw.rect(surf, WHITE, border_rect, 2)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris - OOP with Ghost Piece")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board(GRID_COLS, GRID_ROWS)
        self.board.spawn_piece()
        self.drop_timer = 0.0
        self.soft_drop = False
        self.paused = False

        # Fonts
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 32, bold=True)

    def gravity_interval(self) -> float:
        idx = min(self.board.level - 1, len(GRAVITY_TABLE) - 1)
        base = GRAVITY_TABLE[idx]
        return 0.02 if self.soft_drop else base

    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Continuous soft drop
        self.soft_drop = keys[pygame.K_DOWN]

    def process_event(self, e: pygame.event.Event):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            if e.key == pygame.K_p:
                self.paused = not self.paused
            if self.board.game_over:
                if e.key == pygame.K_r:
                    self.__init__()  # restart
                return
            if e.key == pygame.K_LEFT:
                self.board.try_move(-1, 0)
            elif e.key == pygame.K_RIGHT:
                self.board.try_move(1, 0)
            elif e.key == pygame.K_UP:
                self.board.try_rotate(1)
            elif e.key == pygame.K_z:
                self.board.try_rotate(-1)
            elif e.key == pygame.K_SPACE:
                self.board.hard_drop()
                self.board.spawn_piece()

    def update(self, dt: float):
        if self.paused or self.board.game_over:
            return
        self.drop_timer += dt
        interval = self.gravity_interval()
        while self.drop_timer >= interval:
            self.drop_timer -= interval
            if not self.board.try_move(0, 1):
                # lock and spawn next
                self.board.lock_piece()
                self.board.spawn_piece()

    def draw_text(self, surface, text: str, x: int, y: int, color=WHITE, font=None):
        font = font or self.font
        img = font.render(text, True, color)
        surface.blit(img, (x, y))

    def draw_sidebar(self, surf: pygame.Surface):
        x0 = MARGIN_LEFT + PLAYFIELD_WIDTH + 20
        y0 = MARGIN_TOP
        self.draw_text(surf, "Score", x0, y0)
        self.draw_text(surf, f"{self.board.score}", x0, y0 + 24)
        self.draw_text(surf, "Lines", x0, y0 + 60)
        self.draw_text(surf, f"{self.board.lines_cleared}", x0, y0 + 84)
        self.draw_text(surf, "Level", x0, y0 + 120)
        self.draw_text(surf, f"{self.board.level}", x0, y0 + 144)
        self.draw_text(surf, "Controls", x0, y0 + 200)
        controls = [
            "Left/Right: Move",
            "Up/Z: Rotate",
            "Down: Soft drop",
            "Space: Hard drop",
            "P: Pause, R: Restart",
        ]
        for i, t in enumerate(controls):
            self.draw_text(surf, t, x0, y0 + 224 + i * 20, color=GRAY)

    def draw(self):
        self.screen.fill(BLACK)
        self.board.draw_grid(self.screen)
        self.draw_sidebar(self.screen)
        if self.paused:
            self.draw_text(self.screen, "PAUSED", WIDTH//2 - 60, 8, color=WHITE, font=self.big_font)
        if self.board.game_over:
            self.draw_text(self.screen, "GAME OVER - Press R", WIDTH//2 - 140, HEIGHT//2 - 20, color=WHITE, font=self.big_font)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                self.process_event(e)
            self.handle_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
