import pygame
import random
import sys
from typing import List, Tuple, Optional

# ===============================
# Config & Constants
# ===============================
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 32
BORDER_WIDTH = 4

PLAYFIELD_W = GRID_WIDTH * BLOCK_SIZE
PLAYFIELD_H = GRID_HEIGHT * BLOCK_SIZE

SIDE_PANEL_W = 200
WINDOW_W = PLAYFIELD_W + SIDE_PANEL_W
WINDOW_H = PLAYFIELD_H

FPS = 60

# Gravity (gravity unit per second -> rows per second)
# Will be applied as a timer-based fall, not frame-dependent
INITIAL_GRAVITY = 1.0  # rows/sec
SOFT_DROP_GRAVITY = 20.0  # rows/sec when holding Down

# Colors
COLOR_BG = (20, 20, 28)
COLOR_GRID = (40, 45, 55)
COLOR_TEXT = (230, 230, 230)
COLOR_BORDER = (90, 90, 120)
COLOR_GHOST_MUL = 0.35  # multiply base color for ghost piece

# Tetromino definitions (SRS-like shape sets; simple wall-kick)
# Each shape is list of 4 rotations; each rotation is list of (x, y) offsets for the 4 blocks
TETROMINOES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

TETROMINO_COLORS = {
    "I": (0, 220, 220),
    "O": (220, 220, 0),
    "T": (160, 0, 200),
    "S": (0, 200, 70),
    "Z": (220, 30, 40),
    "J": (0, 70, 200),
    "L": (255, 140, 0),
}


# ===============================
# Utility
# ===============================
def mul_color(color: Tuple[int, int, int], k: float) -> Tuple[int, int, int]:
    return (int(color[0] * k), int(color[1] * k), int(color[2] * k))


# ===============================
# Piece Class
# ===============================
class Piece:
    def __init__(self, name: str):
        self.name = name
        self.rot_index = 0
        self.x = 3  # spawn column
        self.y = -2  # spawn row (above visible)
        self.color = TETROMINO_COLORS[name]

    @property
    def shape(self) -> List[List[Tuple[int, int]]]:
        return TETROMINOES[self.name]

    def get_cells(self, rot: Optional[int] = None, dx: int = 0, dy: int = 0) -> List[Tuple[int, int]]:
        r = self.rot_index if rot is None else rot
        coords = []
        for (ox, oy) in self.shape[r]:
            coords.append((self.x + ox + dx, self.y + oy + dy))
        return coords

    def rotate(self, dir_cw: bool = True) -> int:
        """Return next rotation index without applying."""
        if dir_cw:
            return (self.rot_index + 1) % 4
        else:
            return (self.rot_index - 1) % 4


# ===============================
# Board Class
# ===============================
class Board:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        # grid[y][x] -> None or (r,g,b)
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(w)] for _ in range(h)
        ]

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and y < self.h  # allow negative y (above top)

    def collision(self, cells: List[Tuple[int, int]]) -> bool:
        for (x, y) in cells:
            if x < 0 or x >= self.w or y >= self.h:
                return True
            if y >= 0 and self.grid[y][x] is not None:
                return True
        return False

    def can_place(self, piece: Piece, rot: Optional[int] = None, dx: int = 0, dy: int = 0) -> bool:
        return not self.collision(piece.get_cells(rot=rot, dx=dx, dy=dy))

    def lock_piece(self, piece: Piece) -> None:
        for (x, y) in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color

    def clear_full_lines(self) -> int:
        """Effisien: filter baris penuh, rebuild dari atas."""
        new_rows = []
        cleared = 0
        for y in range(self.h):
            if all(self.grid[y][x] is not None for x in range(self.w)):
                cleared += 1
            else:
                new_rows.append(self.grid[y])
        while len(new_rows) < self.h:
            new_rows.insert(0, [None for _ in range(self.w)])
        self.grid = new_rows
        return cleared

    def get_ghost_drop_y(self, piece: Piece) -> int:
        """Return dy (relative) sampai menyentuh dasar/terkunci."""
        dy = 0
        while True:
            if self.can_place(piece, dy=dy + 1):
                dy += 1
            else:
                return dy

    def draw(self, surf: pygame.Surface, ox: int, oy: int) -> None:
        # Border
        pygame.draw.rect(surf, COLOR_BORDER, (ox - BORDER_WIDTH, oy - BORDER_WIDTH, PLAYFIELD_W + 2 * BORDER_WIDTH, PLAYFIELD_H + 2 * BORDER_WIDTH), BORDER_WIDTH)

        # Grid bg
        pygame.draw.rect(surf, COLOR_BG, (ox, oy, PLAYFIELD_W, PLAYFIELD_H))

        # Grid lines
        for x in range(self.w + 1):
            xpix = ox + x * BLOCK_SIZE
            pygame.draw.line(surf, COLOR_GRID, (xpix, oy), (xpix, oy + PLAYFIELD_H))
        for y in range(self.h + 1):
            ypix = oy + y * BLOCK_SIZE
            pygame.draw.line(surf, COLOR_GRID, (ox, ypix), (ox + PLAYFIELD_W, ypix))

        # Locked blocks
        for y in range(self.h):
            for x in range(self.w):
                col = self.grid[y][x]
                if col:
                    self._draw_block(surf, ox, oy, x, y, col)

    def draw_piece(self, surf: pygame.Surface, ox: int, oy: int, piece: Piece, ghost: bool = False) -> None:
        color = mul_color(piece.color, COLOR_GHOST_MUL) if ghost else piece.color
        for (x, y) in piece.get_cells():
            if y >= 0:
                self._draw_block(surf, ox, oy, x, y, color, ghost=ghost)

    def _draw_block(self, surf: pygame.Surface, ox: int, oy: int, x: int, y: int, color: Tuple[int, int, int], ghost: bool = False) -> None:
        rect = pygame.Rect(ox + x * BLOCK_SIZE, oy + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        if ghost:
            # Outline for ghost + light fill
            pygame.draw.rect(surf, color, rect, 1)
            inset = rect.inflate(-6, -6)
            pygame.draw.rect(surf, color, inset, 1)
        else:
            pygame.draw.rect(surf, color, rect)
            # Shading
            pygame.draw.rect(surf, (0, 0, 0), rect, 2)


# ===============================
# Bag Randomizer
# ===============================
class Bag:
    def __init__(self):
        self.bag: List[str] = []
        self._refill()

    def _refill(self):
        pieces = list(TETROMINOES.keys())
        random.shuffle(pieces)
        self.bag.extend(pieces)

    def next(self) -> str:
        if not self.bag:
            self._refill()
        return self.bag.pop(0)


# ===============================
# Game Class
# ===============================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris (OOP) with Ghost")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)

        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.bag = Bag()
        self.next_queue: List[str] = [self.bag.next() for _ in range(5)]
        self.current = Piece(self.bag.next())
        self.gravity = INITIAL_GRAVITY
        self.drop_accumulator = 0.0
        self.soft_drop = False

        self.score = 0
        self.lines_cleared_total = 0
        self.game_over = False

        # Movement auto-repeat
        self.move_delay = 150  # ms before repeat
        self.move_repeat = 40  # ms per step
        self.move_state = {"left": {"held": False, "t": 0}, "right": {"held": False, "t": 0}}

    def reset(self):
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.bag = Bag()
        self.next_queue = [self.bag.next() for _ in range(5)]
        self.current = Piece(self.bag.next())
        self.gravity = INITIAL_GRAVITY
        self.drop_accumulator = 0.0
        self.soft_drop = False
        self.score = 0
        self.lines_cleared_total = 0
        self.game_over = False
        self.move_state = {"left": {"held": False, "t": 0}, "right": {"held": False, "t": 0}}

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0  # seconds
            self.handle_events(dt)
            if not self.game_over:
                self.update(dt)
            self.draw()

    # ---------------------------
    # Input
    # ---------------------------
    def handle_events(self, dt: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    continue

                if event.key == pygame.K_LEFT:
                    self._tap_move(-1)
                    self.move_state["left"]["held"] = True
                    self.move_state["left"]["t"] = self.move_delay
                elif event.key == pygame.K_RIGHT:
                    self._tap_move(1)
                    self.move_state["right"]["held"] = True
                    self.move_state["right"]["t"] = self.move_delay
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = True
                elif event.key in (pygame.K_UP, pygame.K_x):
                    self._rotate(True)
                elif event.key == pygame.K_z:
                    self._rotate(False)
                elif event.key == pygame.K_SPACE:
                    self._hard_drop()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.move_state["left"]["held"] = False
                elif event.key == pygame.K_RIGHT:
                    self.move_state["right"]["held"] = False
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = False

        # Handle movement auto-repeat
        for dir_key, direction in (("left", -1), ("right", 1)):
            state = self.move_state[dir_key]
            if state["held"]:
                state["t"] -= dt * 1000.0
                while state["t"] <= 0:
                    if not self.game_over and self._move(direction):
                        pass
                    state["t"] += self.move_repeat

    def _tap_move(self, dx: int):
        self._move(dx)

    def _move(self, dx: int) -> bool:
        if self.board.can_place(self.current, dx=dx):
            self.current.x += dx
            return True
        return False

    def _rotate(self, cw: bool):
        new_rot = self.current.rotate(cw)
        # Simple wall-kicks: try offsets
        for kick_x in (0, -1, 1, -2, 2):
            if self.board.can_place(self.current, rot=new_rot, dx=kick_x):
                self.current.rot_index = new_rot
                self.current.x += kick_x
                return

    def _hard_drop(self):
        dy = self.board.get_ghost_drop_y(self.current)
        self.current.y += dy
        self._lock_and_spawn()

    # ---------------------------
    # Update
    # ---------------------------
    def update(self, dt: float):
        gravity = SOFT_DROP_GRAVITY if self.soft_drop else self.gravity
        self.drop_accumulator += gravity * dt
        while self.drop_accumulator >= 1.0:
            self.drop_accumulator -= 1.0
            if self.board.can_place(self.current, dy=1):
                self.current.y += 1
            else:
                self._lock_and_spawn()
                break

    def _lock_and_spawn(self):
        self.board.lock_piece(self.current)
        cleared = self.board.clear_full_lines()
        if cleared > 0:
            self._add_score(cleared)
            self.lines_cleared_total += cleared
            # Optional: increase gravity a bit over time
            self.gravity = min(10.0, INITIAL_GRAVITY + self.lines_cleared_total * 0.02)

        # Spawn next
        if len(self.next_queue) < 5:
            self.next_queue.append(self.bag.next())
        self.current = Piece(self.next_queue.pop(0))

        # Game over check: cannot place new piece at spawn
        if not self.board.can_place(self.current):
            self.game_over = True

    def _add_score(self, lines: int):
        if lines == 1:
            self.score += 100
        elif lines == 2:
            self.score += 300
        elif lines == 3:
            self.score += 500
        elif lines == 4:
            self.score += 800

    # ---------------------------
    # Draw
    # ---------------------------
    def draw_text(self, surf: pygame.Surface, text: str, x: int, y: int, color=COLOR_TEXT, font=None):
        if font is None:
            font = self.font
        img = font.render(text, True, color)
        surf.blit(img, (x, y))

    def draw_next_queue(self, surf: pygame.Surface, ox: int, oy: int):
        self.draw_text(surf, "NEXT", ox, oy)
        yoff = oy + 28
        for i, name in enumerate(self.next_queue[:5]):
            self._draw_mini_piece(surf, ox, yoff + i * 64, name)

    def _draw_mini_piece(self, surf: pygame.Surface, x: int, y: int, name: str):
        scale = 20
        color = TETROMINO_COLORS[name]
        rotations = TETROMINOES[name][0]
        # Center within a 4x4 mini-grid
        minigrid = 4 * scale
        surf_rect = pygame.Rect(x, y, minigrid, minigrid)
        pygame.draw.rect(surf, (30, 30, 40), surf_rect)
        pygame.draw.rect(surf, COLOR_GRID, surf_rect, 1)
        for (ox, oy) in rotations:
            rx = x + ox * scale
            ry = y + oy * scale
            rect = pygame.Rect(rx, ry, scale, scale)
            pygame.draw.rect(surf, color, rect)
            pygame.draw.rect(surf, (0, 0, 0), rect, 1)

    def draw_hud(self, surf: pygame.Surface, ox: int, oy: int):
        self.draw_text(surf, f"Score: {self.score}", ox, oy)
        self.draw_text(surf, f"Lines: {self.lines_cleared_total}", ox, oy + 24)
        self.draw_text(surf, f"Gravity: {self.gravity:.2f}", ox, oy + 48)
        self.draw_text(surf, "Controls:", ox, oy + 88)
        self.draw_text(surf, "\u2190/\u2192 Move", ox, oy + 110)
        self.draw_text(surf, "\u2193 Soft Drop", ox, oy + 130)
        self.draw_text(surf, "Space Hard Drop", ox, oy + 150)
        self.draw_text(surf, "Z/X/\u2191 Rotate", ox, oy + 170)
        self.draw_text(surf, "R Restart", ox, oy + 190)
        self.draw_text(surf, "Esc Quit", ox, oy + 210)

    def draw(self):
        self.screen.fill(COLOR_BG)

        pf_ox, pf_oy = 20, 20
        side_ox = PLAYFIELD_W + 40
        side_oy = 20

        # Board and locked cells
        self.board.draw(self.screen, pf_ox, pf_oy)

        # Ghost piece
        if not self.game_over:
            dy = self.board.get_ghost_drop_y(self.current)
            ghost_piece = Piece(self.current.name)
            ghost_piece.x = self.current.x
            ghost_piece.y = self.current.y + dy
            ghost_piece.rot_index = self.current.rot_index
            self.board.draw_piece(self.screen, pf_ox, pf_oy, ghost_piece, ghost=True)

            # Current piece
            self.board.draw_piece(self.screen, pf_ox, pf_oy, self.current, ghost=False)

        # Side panel
        self.draw_hud(self.screen, side_ox, side_oy)
        self.draw_next_queue(self.screen, side_ox, side_oy + 250)

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((PLAYFIELD_W, PLAYFIELD_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (pf_ox, pf_oy))
            text = "GAME OVER"
            timg = self.big_font.render(text, True, (255, 80, 80))
            self.screen.blit(timg, (pf_ox + (PLAYFIELD_W - timg.get_width()) // 2, pf_oy + 140))
            self.draw_text(self.screen, "Press R to Restart", pf_ox + 60, pf_oy + 200)

        pygame.display.flip()


def main():
    random.seed()
    Game().run()


if __name__ == "__main__":
    main()
