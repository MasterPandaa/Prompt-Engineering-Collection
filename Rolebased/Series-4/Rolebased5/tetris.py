import sys
import random
import pygame
from pygame import Rect

# Configuration
COLS, ROWS = 10, 20
TILE = 32
BORDER = 2
W = COLS * TILE
H = ROWS * TILE
FPS = 60

# Colors
BLACK = (18, 18, 18)
GRID = (28, 28, 28)
WHITE = (245, 245, 245)
SHADOW = (120, 120, 120)

# Tetrimino definitions (4x4) and colors
# Using SRS-like shapes (no full wall kicks, but simple shifts)
TETROMINOES = {
    'I': [
        [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
        ],
    ],
    'J': [
        [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        [
            [0, 1, 1],
            [0, 1, 0],
            [0, 1, 0],
        ],
        [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 1],
        ],
        [
            [0, 1, 0],
            [0, 1, 0],
            [1, 1, 0],
        ],
    ],
    'L': [
        [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ],
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 1],
        ],
        [
            [0, 0, 0],
            [1, 1, 1],
            [1, 0, 0],
        ],
        [
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
    ],
    'O': [
        [
            [1, 1],
            [1, 1],
        ],
    ],
    'S': [
        [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0],
        ],
        [
            [0, 1, 0],
            [0, 1, 1],
            [0, 0, 1],
        ],
    ],
    'T': [
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        [
            [0, 1, 0],
            [0, 1, 1],
            [0, 1, 0],
        ],
        [
            [0, 0, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        [
            [0, 1, 0],
            [1, 1, 0],
            [0, 1, 0],
        ],
    ],
    'Z': [
        [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0],
        ],
        [
            [0, 0, 1],
            [0, 1, 1],
            [0, 1, 0],
        ],
    ],
}

COLORS = {
    'I': (0, 186, 249),
    'J': (0, 101, 189),
    'L': (255, 140, 0),
    'O': (255, 213, 0),
    'S': (120, 190, 33),
    'T': (149, 45, 137),
    'Z': (226, 37, 48),
}


def rotate_matrix(mat):
    """Rotate 2D matrix clockwise."""
    return [list(row) for row in zip(*mat[::-1])]


class Piece:
    """Represent a falling tetromino piece."""
    def __init__(self, kind: str):
        self.kind = kind
        self.color = COLORS[kind]
        self.rotations = [shape for shape in TETROMINOES[kind]]
        # Ensure we have all 4 rotations where applicable
        if len(self.rotations) == 1:
            # O piece stays same
            pass
        else:
            # Build up to 4 rotations by rotating
            while len(self.rotations) < 4:
                self.rotations.append(rotate_matrix(self.rotations[-1]))
        self.rotation = 0
        # Position: top center
        self.x = COLS // 2 - len(self.matrix()[0]) // 2
        self.y = -self.spawn_offset()

    def spawn_offset(self):
        # Lift spawn to keep top hidden rows above grid
        return 2

    def matrix(self):
        return self.rotations[self.rotation % len(self.rotations)]

    def cells(self, at_x=None, at_y=None, rot=None):
        mat = self.rotations[(rot if rot is not None else self.rotation) % len(self.rotations)]
        x0 = self.x if at_x is None else at_x
        y0 = self.y if at_y is None else at_y
        for r, row in enumerate(mat):
            for c, v in enumerate(row):
                if v:
                    yield x0 + c, y0 + r

    def rotated(self, dr=1):
        np = Piece(self.kind)
        np.rotations = self.rotations
        np.rotation = (self.rotation + dr) % len(self.rotations)
        np.x, np.y = self.x, self.y
        np.color = self.color
        return np


class Board:
    """Game board state and logic: collision, lock, clearing, ghost."""
    def __init__(self):
        # grid[r][c] is color or None
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1

    def in_bounds(self, x, y):
        return 0 <= x < COLS and y < ROWS

    def valid(self, piece: Piece):
        for x, y in piece.cells():
            if y < 0:
                # allow above top
                continue
            if not self.in_bounds(x, y):
                return False
            if self.grid[y][x] is not None:
                return False
        return True

    def try_move(self, piece: Piece, dx=0, dy=0, dr=0):
        np = piece.rotated(dr) if dr else piece
        nx, ny = (np.x + dx, np.y + dy)
        if self.valid_at(np, nx, ny):
            piece.x, piece.y = nx, ny
            if dr:
                piece.rotation = np.rotation
            return True
        return False

    def valid_at(self, piece: Piece, x, y, rot=None):
        for cx, cy in piece.cells(at_x=x, at_y=y, rot=rot):
            if cy < 0:
                continue
            if not self.in_bounds(cx, cy) or self.grid[cy][cx] is not None:
                return False
        return True

    def rotate_with_kicks(self, piece: Piece, dr=1):
        # Simple wall kicks: try in place, then shifts
        cand = piece.rotated(dr)
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
        for dx, dy in kicks:
            if self.valid_at(cand, piece.x + dx, piece.y + dy):
                piece.rotation = cand.rotation
                piece.x += dx
                piece.y += dy
                return True
        return False

    def lock(self, piece: Piece):
        for x, y in piece.cells():
            if y < 0:
                # Top out
                raise RuntimeError("Game Over")
            self.grid[y][x] = piece.color
        cleared = self.clear_lines()
        return cleared

    def clear_lines(self):
        # Efficient compaction: keep rows that are not full and count full rows
        new_rows = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(new_rows)
        if cleared:
            for _ in range(cleared):
                new_rows.insert(0, [None for _ in range(COLS)])
            self.grid = new_rows
            self.lines += cleared
            self.score += [0, 100, 300, 500, 800][cleared] * self.level
            # Increase level every 10 lines
            self.level = 1 + self.lines // 10
        return cleared

    def hard_drop_y(self, piece: Piece):
        y = piece.y
        while True:
            if self.valid_at(piece, piece.x, y + 1):
                y += 1
            else:
                break
        return y

    def draw(self, surf, current: Piece, ghost_y: int):
        surf.fill(BLACK)
        # draw grid background
        for r in range(ROWS):
            for c in range(COLS):
                rect = Rect(c * TILE, r * TILE, TILE, TILE)
                pygame.draw.rect(surf, GRID, rect, 1)
                if self.grid[r][c] is not None:
                    self.draw_tile(surf, c, r, self.grid[r][c])

        # draw ghost piece
        if current is not None:
            for x, y in current.cells(at_y=ghost_y):
                if y >= 0:
                    self.draw_tile(surf, x, y, SHADOW, ghost=True)
            # draw current piece
            for x, y in current.cells():
                if y >= 0:
                    self.draw_tile(surf, x, y, current.color)

        # Side info
        self.draw_sidebar(surf)

    def draw_tile(self, surf, x, y, color, ghost=False):
        px = x * TILE
        py = y * TILE
        inner = TILE - BORDER * 2
        rect = Rect(px + BORDER, py + BORDER, inner, inner)
        if ghost:
            s = pygame.Surface((inner, inner), pygame.SRCALPHA)
            s.fill((*color, 80))
            surf.blit(s, (px + BORDER, py + BORDER))
        else:
            pygame.draw.rect(surf, color, rect, border_radius=4)
            # simple shading
            pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=4)

    def draw_sidebar(self, surf):
        # Draw score, lines, level at top-left overlay
        font = pygame.font.SysFont("consolas", 18)
        text = f"Score: {self.score}  Lines: {self.lines}  Lv: {self.level}"
        img = font.render(text, True, WHITE)
        surf.blit(img, (8, 6))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris - OOP, Ghost, Efficient Clear")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.bag = []
        self.current = self.next_piece()
        self.drop_timer = 0.0
        self.drop_interval = self.compute_drop_interval()
        self.lock_delay = 0.5
        self.lock_timer = 0.0
        self.game_over = False

    def compute_drop_interval(self):
        # Faster with higher level
        base = 0.9
        factor = 0.85 ** (self.board.level - 1)
        return max(0.05, base * factor)

    def next_piece(self):
        if not self.bag:
            self.bag = list(TETROMINOES.keys())
            random.shuffle(self.bag)
        return Piece(self.bag.pop())

    def spawn_piece(self):
        self.current = self.next_piece()
        if not self.board.valid(self.current):
            self.game_over = True

    def hard_drop(self):
        if self.current is None:
            return
        y = self.board.hard_drop_y(self.current)
        self.current.y = y
        try:
            cleared = self.board.lock(self.current)
        except RuntimeError:
            self.game_over = True
            return
        self.board.score += 2  # small bonus for hard drop
        self.drop_timer = 0
        self.lock_timer = 0
        self.drop_interval = self.compute_drop_interval()
        self.spawn_piece()

    def update(self, dt):
        if self.game_over:
            return
        self.drop_interval = self.compute_drop_interval()
        self.drop_timer += dt
        # Soft drop: holding down makes piece fall faster, but we manage via input
        if self.drop_timer >= self.drop_interval:
            self.drop_timer -= self.drop_interval
            if not self.board.try_move(self.current, dy=1):
                # start/advance lock delay
                self.lock_timer += self.drop_interval
                if self.lock_timer >= self.lock_delay:
                    try:
                        self.board.lock(self.current)
                    except RuntimeError:
                        self.game_over = True
                        return
                    self.spawn_piece()
                    self.lock_timer = 0

    def process_input(self):
        keys = pygame.key.get_pressed()
        # Continuous soft drop
        if keys[pygame.K_DOWN]:
            # Try faster fall; reward slightly
            moved = self.board.try_move(self.current, dy=1)
            if moved:
                self.board.score += 1
                self.lock_timer = 0

    def handle_event(self, e):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif e.key == pygame.K_LEFT:
                if self.board.try_move(self.current, dx=-1):
                    self.lock_timer = 0
            elif e.key == pygame.K_RIGHT:
                if self.board.try_move(self.current, dx=1):
                    self.lock_timer = 0
            elif e.key == pygame.K_UP:
                if self.board.rotate_with_kicks(self.current, dr=1):
                    self.lock_timer = 0
            elif e.key == pygame.K_z:
                if self.board.rotate_with_kicks(self.current, dr=-1):
                    self.lock_timer = 0
            elif e.key == pygame.K_SPACE:
                self.hard_drop()
            elif e.key == pygame.K_c:
                # quick reset
                self.__init__()

    def draw(self):
        if self.game_over:
            self.screen.fill(BLACK)
            font1 = pygame.font.SysFont("consolas", 36)
            font2 = pygame.font.SysFont("consolas", 20)
            msg = font1.render("GAME OVER", True, WHITE)
            sub = font2.render("Press C to restart or ESC to quit", True, WHITE)
            self.screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 40))
            self.screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 4))
            pygame.display.flip()
            return

        ghost_y = self.board.hard_drop_y(self.current)
        self.board.draw(self.screen, self.current, ghost_y)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                self.handle_event(e)
            self.process_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
