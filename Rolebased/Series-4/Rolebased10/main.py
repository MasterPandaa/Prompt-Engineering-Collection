# Tetris Clone in Python + Pygame
# OOP design with Piece and Board, ghost piece, efficient line clearing.
# Controls:
#   Left/Right: move
#   Down: soft drop
#   Z / Up: rotate CCW / CW (Up = CW)
#   X: rotate CW
#   Space: hard drop
#   P: pause
#   Esc: quit

import sys
import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

import pygame

# ----------------------------------
# Game constants
# ----------------------------------
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
HIDDEN_ROWS = 2  # hidden spawn rows above the visible board
CELL_SIZE = 32
BORDER = 16
SIDEBAR_WIDTH = 200
WINDOW_WIDTH = BORDER * 2 + BOARD_WIDTH * CELL_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BORDER * 2 + BOARD_HEIGHT * CELL_SIZE
FPS = 60

# Gravity speeds by level (frames per cell move). Smaller is faster.
# Alternatively could be seconds per cell; using frames keeps it in sync with FPS.
LEVEL_SPEED_FRAMES = {
    1: 48, 2: 43, 3: 38, 4: 33, 5: 28,
    6: 23, 7: 18, 8: 13, 9: 8,
    10: 6, 11: 5, 12: 5, 13: 4, 14: 4, 15: 4,
}

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
LIGHT_GRAY = (120, 120, 120)

# Tetromino colors (approx Tetris guideline)
COLORS = {
    'I': (0, 240, 240),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
    'O': (240, 240, 0),
    'S': (0, 240, 0),
    'T': (160, 0, 240),
    'Z': (240, 0, 0),
}

# Tetromino rotation states using 4x4 matrices (list of coords per rotation)
# Each rotation is a list of (x,y) block offsets for that piece rotation.
# Origin at top-left of the 4x4 box; piece x,y refers to this 4x4 box position.
TETROMINO_SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # 0
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # 90
        [(0, 2), (1, 2), (2, 2), (3, 2)],  # 180
        [(1, 0), (1, 1), (1, 2), (1, 3)],  # 270
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

# Basic wall kick tests: try these offsets in order when rotating
# This is a simplified wall-kick set (not full SRS but works well)
WALL_KICKS = [
    (0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0), (0, -1), (0, 1)
]


@dataclass
class Piece:
    kind: str
    rotation: int
    x: int
    y: int  # y can be negative (spawning above visible board)
    color: Tuple[int, int, int]

    @property
    def cells(self) -> List[Tuple[int, int]]:
        return TETROMINO_SHAPES[self.kind][self.rotation]

    def rotated(self, dr: int) -> 'Piece':
        return Piece(self.kind, (self.rotation + dr) % 4, self.x, self.y, self.color)

    def moved(self, dx: int, dy: int) -> 'Piece':
        return Piece(self.kind, self.rotation, self.x + dx, self.y + dy, self.color)

    def get_world_cells(self) -> List[Tuple[int, int]]:
        return [(self.x + cx, self.y + cy) for (cx, cy) in self.cells]


class Board:
    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT, hidden_rows: int = HIDDEN_ROWS):
        self.width = width
        self.height = height
        self.hidden_rows = hidden_rows
        # grid[y][x] stores color tuple or None. y in [0, height-1]
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.score = 0
        self.level = 1
        self.lines_cleared_total = 0

    # ------------- Collision & bounds -------------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def collides(self, piece: Piece) -> bool:
        for (wx, wy) in piece.get_world_cells():
            if wx < 0 or wx >= self.width:
                return True
            if wy >= self.height:
                return True
            if wy >= 0 and self.grid[wy][wx] is not None:
                return True
        return False

    # ------------- Locking & clearing -------------
    def lock_piece(self, piece: Piece) -> None:
        for (wx, wy) in piece.get_world_cells():
            if 0 <= wy < self.height:
                self.grid[wy][wx] = piece.color
        cleared = self.clear_lines()
        self.update_score_and_level(cleared)

    def clear_lines(self) -> int:
        # Efficient line clearing: filter out full rows and count them, then add empty rows on top
        new_rows = []
        cleared = 0
        for y in range(self.height):
            if all(self.grid[y][x] is not None for x in range(self.width)):
                cleared += 1
            else:
                new_rows.append(self.grid[y])
        if cleared > 0:
            empty_row = [None] * self.width
            self.grid = [[None] * self.width for _ in range(cleared)] + new_rows
        return cleared

    def update_score_and_level(self, cleared: int) -> None:
        # Standard-ish Tetris scoring (no tspin): 1/2/3/4 lines = 100/300/500/800 * level
        if cleared == 1:
            self.score += 100 * self.level
        elif cleared == 2:
            self.score += 300 * self.level
        elif cleared == 3:
            self.score += 500 * self.level
        elif cleared == 4:
            self.score += 800 * self.level
        self.lines_cleared_total += cleared
        # Increase level every 10 lines
        self.level = max(1, 1 + self.lines_cleared_total // 10)

    def game_over(self) -> bool:
        # Any block in hidden spawn rows means game over after lock
        for y in range(0, self.hidden_rows):
            if any(self.grid[y][x] is not None for x in range(self.width)):
                return True
        return False


class BagRandomizer:
    def __init__(self):
        self.bag: List[str] = []
        self._refill()

    def _refill(self):
        pieces = list(TETROMINO_SHAPES.keys())
        random.shuffle(pieces)
        self.bag.extend(pieces)

    def next(self) -> str:
        if not self.bag:
            self._refill()
        kind = self.bag.pop()
        return kind


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris - OOP Pygame")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font_small = pygame.font.SysFont("consolas", 18)
        self.font_big = pygame.font.SysFont("consolas", 28, bold=True)

        self.board = Board()
        self.bag = BagRandomizer()
        self.next_queue: List[str] = [self.bag.next() for _ in range(5)]

        self.current: Piece = self._spawn_piece()
        self.drop_timer = 0  # frames elapsed for gravity
        self.paused = False
        self.game_over_flag = False

        # Input handling (simple DAS/ARR could be added later)
        self.move_cooldown = 0
        self.soft_drop = False

    # ----------- Piece spawning and ghost projection -----------
    def _spawn_piece(self) -> Piece:
        kind = self.next_queue.pop(0)
        self.next_queue.append(self.bag.next())
        color = COLORS[kind]
        # Spawn near middle; y negative to spawn in hidden rows
        x = (self.board.width // 2) - 2
        y = -self.board.hidden_rows
        piece = Piece(kind, 0, x, y, color)
        # If collides immediately, it's game over state on lock; we still return piece
        return piece

    def _project_ghost(self, piece: Piece) -> Piece:
        ghost = Piece(piece.kind, piece.rotation, piece.x, piece.y, piece.color)
        while not self.board.collides(ghost.moved(0, 1)):
            ghost = ghost.moved(0, 1)
        return ghost

    # -------------------- Input handling -----------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if self.paused or self.game_over_flag:
                    continue
                if event.key == pygame.K_LEFT:
                    self._try_move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self._try_move(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = True
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()
                elif event.key == pygame.K_UP:
                    self._try_rotate(1)  # CW
                elif event.key == pygame.K_x:
                    self._try_rotate(1)  # CW duplicate
                elif event.key == pygame.K_z:
                    self._try_rotate(-1)  # CCW
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.soft_drop = False

    def _try_move(self, dx: int, dy: int) -> bool:
        moved = self.current.moved(dx, dy)
        if not self.board.collides(moved):
            self.current = moved
            return True
        return False

    def _try_rotate(self, dr: int) -> bool:
        rotated = self.current.rotated(dr)
        for (ox, oy) in WALL_KICKS:
            candidate = Piece(rotated.kind, rotated.rotation, rotated.x + ox, rotated.y + oy, rotated.color)
            if not self.board.collides(candidate):
                self.current = candidate
                return True
        return False

    def _hard_drop(self):
        # Move down until collides, then step back 1 and lock
        while not self.board.collides(self.current.moved(0, 1)):
            self.current = self.current.moved(0, 1)
        self._lock_current()

    # -------------------- Update logic -------------------------
    def update(self):
        if self.paused or self.game_over_flag:
            return

        frames_per_cell = LEVEL_SPEED_FRAMES.get(self.board.level, 4)
        speed = max(1, frames_per_cell)
        # Soft drop faster (every 2 frames)
        if self.soft_drop:
            speed = min(speed, 2)

        self.drop_timer += 1
        if self.drop_timer >= speed:
            self.drop_timer = 0
            if not self._try_move(0, 1):
                # cannot move down -> lock
                self._lock_current()

    def _lock_current(self):
        self.board.lock_piece(self.current)
        if self.board.game_over():
            self.game_over_flag = True
            return
        self.current = self._spawn_piece()

    # -------------------- Rendering ----------------------------
    def draw(self):
        self.screen.fill(BLACK)
        # Draw playfield background
        px = BORDER
        py = BORDER
        pw = BOARD_WIDTH * CELL_SIZE
        ph = BOARD_HEIGHT * CELL_SIZE
        pygame.draw.rect(self.screen, GRAY, (px - 2, py - 2, pw + 4, ph + 4), 2)

        # Draw grid cells
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                rect = (px + x * CELL_SIZE, py + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.board.grid[y][x]
                if cell is not None:
                    pygame.draw.rect(self.screen, cell, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
                else:
                    # faint grid lines
                    pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)

        # Draw ghost piece
        ghost = self._project_ghost(self.current)
        self._draw_piece_outline(ghost, (200, 200, 200))

        # Draw current piece
        self._draw_piece_filled(self.current)

        # Sidebar
        sx = px + pw + 20
        sy = py
        self._draw_text(self.font_big, f"Score: {self.board.score}", (sx, sy), WHITE)
        self._draw_text(self.font_big, f"Level: {self.board.level}", (sx, sy + 36), WHITE)
        self._draw_text(self.font_big, f"Lines: {self.board.lines_cleared_total}", (sx, sy + 72), WHITE)

        self._draw_text(self.font_big, "Next:", (sx, sy + 120), WHITE)
        self._draw_next_queue(sx, sy + 160)

        if self.paused:
            self._center_message("Paused")
        if self.game_over_flag:
            self._center_message("Game Over")

        pygame.display.flip()

    def _draw_piece_filled(self, piece: Piece):
        px = BORDER
        py = BORDER
        for (wx, wy) in piece.get_world_cells():
            if wy < 0:
                continue
            rect = (px + wx * CELL_SIZE, py + wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, piece.color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def _draw_piece_outline(self, piece: Piece, color: Tuple[int, int, int]):
        px = BORDER
        py = BORDER
        for (wx, wy) in piece.get_world_cells():
            if wy < 0:
                continue
            rect = (px + wx * CELL_SIZE, py + wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect, 2)

    def _draw_text(self, font: pygame.font.Font, text: str, pos: Tuple[int, int], color: Tuple[int, int, int]):
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def _center_message(self, text: str):
        surf = self.font_big.render(text, True, WHITE)
        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        shadow = self.font_big.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(WINDOW_WIDTH // 2 + 2, WINDOW_HEIGHT // 2 + 2))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(surf, rect)

    def _draw_next_queue(self, sx: int, sy: int):
        # Draw next 5 pieces as small previews
        box_size = 80
        gap = 8
        for i, kind in enumerate(self.next_queue[:5]):
            bx = sx
            by = sy + i * (box_size + gap)
            pygame.draw.rect(self.screen, LIGHT_GRAY, (bx, by, box_size, box_size), 2)
            # Draw miniature piece in the box, centered
            cells = TETROMINO_SHAPES[kind][0]
            color = COLORS[kind]
            # Normalize to min x,y
            minx = min(c[0] for c in cells)
            maxx = max(c[0] for c in cells)
            miny = min(c[1] for c in cells)
            maxy = max(c[1] for c in cells)
            w = maxx - minx + 1
            h = maxy - miny + 1
            cell = 16
            offset_x = bx + (box_size - w * cell) // 2
            offset_y = by + (box_size - h * cell) // 2
            for (cx, cy) in cells:
                rx = offset_x + (cx - minx) * cell
                ry = offset_y + (cy - miny) * cell
                pygame.draw.rect(self.screen, color, (rx, ry, cell, cell))
                pygame.draw.rect(self.screen, BLACK, (rx, ry, cell, cell), 1)

    # -------------------- Main loop ----------------------------
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


def main():
    Game().run()


if __name__ == "__main__":
    main()
