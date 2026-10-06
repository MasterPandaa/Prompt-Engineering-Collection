import pygame
import sys
import random
from typing import List, Tuple, Optional

# -----------------------------
# Config
# -----------------------------
COLS = 10
ROWS = 20
BLOCK = 30  # pixel size per block
BORDER = 2  # grid line thickness
SIDE_PANEL = 180  # side area for score/next piece
MARGIN = 10

WIDTH = COLS * BLOCK + SIDE_PANEL
HEIGHT = ROWS * BLOCK
FPS = 60

# Fall timings (seconds per cell)
INITIAL_FALL_SPEED = 0.6
SOFT_DROP_MULTIPLIER = 0.05  # soft drop is faster

# Scoring per number of lines cleared at once
SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# Colors
BLACK = (18, 18, 18)
GRID_COLOR = (40, 40, 40)
WHITE = (230, 230, 230)
TEXT_COLOR = (220, 220, 220)

# Tetromino colors
COL_I = (0, 240, 240)
COL_O = (240, 240, 0)
COL_T = (160, 0, 240)
COL_S = (0, 240, 0)
COL_Z = (240, 0, 0)
COL_J = (0, 0, 240)
COL_L = (240, 160, 0)

# Shape definitions using rotation states as 4x4 matrices
# Each state is list of (x, y) offsets relative to a pivot in a 4x4
TETROMINOES = {
    'I': {
        'color': COL_I,
        'rotations': [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
        ],
        'pivot': (1.5, 1.5)
    },
    'O': {
        'color': COL_O,
        'rotations': [
            [(1, 1), (2, 1), (1, 2), (2, 2)],
        ],
        'pivot': (1.5, 1.5)
    },
    'T': {
        'color': COL_T,
        'rotations': [
            [(1, 1), (0, 1), (2, 1), (1, 2)],
            [(1, 1), (1, 0), (1, 2), (2, 1)],
            [(1, 1), (0, 1), (2, 1), (1, 0)],
            [(1, 1), (1, 0), (1, 2), (0, 1)],
        ],
        'pivot': (1.5, 1.5)
    },
    'S': {
        'color': COL_S,
        'rotations': [
            [(1, 1), (2, 1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
        ],
        'pivot': (1.5, 1.5)
    },
    'Z': {
        'color': COL_Z,
        'rotations': [
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(2, 0), (2, 1), (1, 1), (1, 2)],
        ],
        'pivot': (1.5, 1.5)
    },
    'J': {
        'color': COL_J,
        'rotations': [
            [(0, 1), (0, 2), (1, 2), (2, 2)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (0, 2), (1, 2)],
        ],
        'pivot': (1.5, 1.5)
    },
    'L': {
        'color': COL_L,
        'rotations': [
            [(2, 1), (0, 2), (1, 2), (2, 2)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
        'pivot': (1.5, 1.5)
    },
}

# 7-bag generator for fair randomness
class SevenBag:
    def __init__(self):
        self.bag: List[str] = []

    def next(self) -> str:
        if not self.bag:
            self.bag = list(TETROMINOES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()

# Piece class
class Piece:
    def __init__(self, kind: str):
        self.kind = kind
        self.rotation = 0
        # spawn roughly centered: x is column index, y row index
        # We use top-left origin of the 4x4 box placed so that its (x,y) refers to grid cell
        self.x = COLS // 2 - 2
        self.y = -2  # start above visible grid

    @property
    def color(self):
        return TETROMINOES[self.kind]['color']

    def cells(self, rot: Optional[int] = None) -> List[Tuple[int, int]]:
        r = self.rotation if rot is None else rot
        states = TETROMINOES[self.kind]['rotations']
        pattern = states[r % len(states)]
        # translate 4x4 coordinates into grid positions
        return [(self.x + cx, self.y + cy) for (cx, cy) in pattern]

    def rotate(self, direction: int, grid: List[List[Optional[Tuple[int,int,int]]]]) -> bool:
        # direction: +1 clockwise, -1 counterclockwise (we only use +1 here)
        new_rot = (self.rotation + direction) % len(TETROMINOES[self.kind]['rotations'])
        # simple wall kicks: try original, then small horizontal offsets
        for dx in (0, -1, 1, -2, 2):
            if not collides(self.x + dx, self.y, self.cells(new_rot), grid):
                self.x += dx
                self.rotation = new_rot
                return True
        return False


def create_grid() -> List[List[Optional[Tuple[int, int, int]]]]:
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def collides(px: int, py: int, cells: List[Tuple[int, int]], grid) -> bool:
    for (x, y) in cells:
        gx, gy = x, y
        if gx < 0 or gx >= COLS or gy >= ROWS:
            return True
        if gy >= 0 and grid[gy][gx] is not None:
            return True
    return False


def lock_piece(piece: Piece, grid) -> None:
    for (x, y) in piece.cells():
        if 0 <= y < ROWS:
            grid[y][x] = piece.color


def clear_lines(grid) -> int:
    full_rows = [i for i in range(ROWS) if all(grid[i][c] is not None for c in range(COLS))]
    for r in full_rows:
        del grid[r]
        grid.insert(0, [None for _ in range(COLS)])
    return len(full_rows)


def hard_drop(piece: Piece, grid) -> int:
    drop = 0
    while True:
        # test if we can move 1 down
        next_cells = [(x, y + 1) for (x, y) in piece.cells()]
        if collides(piece.x, piece.y + 1, next_cells, grid):
            break
        piece.y += 1
        drop += 1
    return drop


def draw_grid(surface):
    for r in range(ROWS + 1):
        y = r * BLOCK
        pygame.draw.line(surface, GRID_COLOR, (0, y), (COLS * BLOCK, y), 1)
    for c in range(COLS + 1):
        x = c * BLOCK
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, ROWS * BLOCK), 1)


def draw_board(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color is not None:
                rect = pygame.Rect(x * BLOCK + BORDER, y * BLOCK + BORDER, BLOCK - 2 * BORDER, BLOCK - 2 * BORDER)
                pygame.draw.rect(surface, color, rect, border_radius=4)


def draw_piece(surface, piece: Piece):
    for (x, y) in piece.cells():
        if y < 0:
            continue
        rect = pygame.Rect(x * BLOCK + BORDER, y * BLOCK + BORDER, BLOCK - 2 * BORDER, BLOCK - 2 * BORDER)
        pygame.draw.rect(surface, piece.color, rect, border_radius=4)


def draw_next(surface, font, next_kind: str):
    label = font.render("NEXT", True, TEXT_COLOR)
    surface.blit(label, (COLS * BLOCK + MARGIN, MARGIN))

    states = TETROMINOES[next_kind]['rotations']
    shape = states[0]
    # center in a 4x4 box in side panel
    offx = COLS * BLOCK + MARGIN
    offy = 40
    # compute bounding box
    minx = min(x for x, _ in shape)
    maxx = max(x for x, _ in shape)
    miny = min(y for _, y in shape)
    maxy = max(y for _, y in shape)
    w = (maxx - minx + 1) * BLOCK
    h = (maxy - miny + 1) * BLOCK
    startx = offx + (SIDE_PANEL - 2 * MARGIN - w) // 2
    starty = offy + (4 * BLOCK - h) // 2

    for (x, y) in shape:
        rx = startx + (x - minx) * BLOCK + BORDER
        ry = starty + (y - miny) * BLOCK + BORDER
        rect = pygame.Rect(rx, ry, BLOCK - 2 * BORDER, BLOCK - 2 * BORDER)
        pygame.draw.rect(surface, TETROMINOES[next_kind]['color'], rect, border_radius=4)


def draw_sidebar(surface, font, score: int, level: int, lines: int, next_kind: str):
    # separator
    pygame.draw.line(surface, GRID_COLOR, (COLS * BLOCK, 0), (COLS * BLOCK, HEIGHT), 2)

    # score/level/lines
    texts = [
        f"Score: {score}",
        f"Level: {level}",
        f"Lines: {lines}",
    ]
    y = 140
    for t in texts:
        label = font.render(t, True, TEXT_COLOR)
        surface.blit(label, (COLS * BLOCK + MARGIN, y))
        y += 30

    draw_next(surface, font, next_kind)


def game_over_screen(surface, font_big, font_small, score):
    overlay = pygame.Surface((COLS * BLOCK, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    msg = font_big.render("GAME OVER", True, (240, 80, 80))
    rect = msg.get_rect(center=(COLS * BLOCK // 2, HEIGHT // 2 - 30))
    surface.blit(msg, rect)

    sc = font_small.render(f"Score: {score}", True, TEXT_COLOR)
    rect2 = sc.get_rect(center=(COLS * BLOCK // 2, HEIGHT // 2 + 10))
    surface.blit(sc, rect2)

    hint = font_small.render("Press R to Restart or ESC to Quit", True, TEXT_COLOR)
    rect3 = hint.get_rect(center=(COLS * BLOCK // 2, HEIGHT // 2 + 40))
    surface.blit(hint, rect3)


def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 20)
    font_big = pygame.font.SysFont("consolas", 42, bold=True)

    grid = create_grid()
    bag = SevenBag()

    current = Piece(bag.next())
    next_kind = bag.next()

    score = 0
    lines_cleared_total = 0
    level = 1

    fall_speed = INITIAL_FALL_SPEED
    fall_timer = 0.0

    running = True
    game_over = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over:
                    if event.key == pygame.K_r:
                        # restart
                        grid = create_grid()
                        bag = SevenBag()
                        current = Piece(bag.next())
                        next_kind = bag.next()
                        score = 0
                        lines_cleared_total = 0
                        level = 1
                        fall_speed = INITIAL_FALL_SPEED
                        fall_timer = 0
                        game_over = False
                    continue

                if event.key == pygame.K_LEFT:
                    next_cells = [(x - 1, y) for (x, y) in current.cells()]
                    if not collides(current.x - 1, current.y, next_cells, grid):
                        current.x -= 1
                elif event.key == pygame.K_RIGHT:
                    next_cells = [(x + 1, y) for (x, y) in current.cells()]
                    if not collides(current.x + 1, current.y, next_cells, grid):
                        current.x += 1
                elif event.key == pygame.K_UP:
                    current.rotate(+1, grid)
                elif event.key == pygame.K_SPACE:
                    gained = hard_drop(current, grid)
                    score += gained * 2  # little reward for hard drop distance
                    # lock immediately after hard drop
                    lock_piece(current, grid)
                    cleared = clear_lines(grid)
                    if cleared:
                        score += SCORES.get(cleared, cleared * 100)
                        lines_cleared_total += cleared
                        # level rises every 10 lines
                        level = 1 + lines_cleared_total // 10
                        fall_speed = max(0.05, INITIAL_FALL_SPEED * (0.85 ** (level - 1)))
                    current = Piece(next_kind)
                    next_kind = bag.next()
                    # check game over
                    if collides(current.x, current.y, current.cells(), grid):
                        game_over = True

        if not game_over:
            keys = pygame.key.get_pressed()
            speed = fall_speed
            if keys[pygame.K_DOWN]:
                speed = max(0.01, fall_speed * SOFT_DROP_MULTIPLIER)

            fall_timer += dt
            if fall_timer >= speed:
                fall_timer -= speed
                # try to move down by 1, otherwise lock
                next_cells = [(x, y + 1) for (x, y) in current.cells()]
                if not collides(current.x, current.y + 1, next_cells, grid):
                    current.y += 1
                else:
                    # lock
                    lock_piece(current, grid)
                    cleared = clear_lines(grid)
                    if cleared:
                        score += SCORES.get(cleared, cleared * 100)
                        lines_cleared_total += cleared
                        level = 1 + lines_cleared_total // 10
                        fall_speed = max(0.05, INITIAL_FALL_SPEED * (0.85 ** (level - 1)))
                    # spawn new
                    current = Piece(next_kind)
                    next_kind = bag.next()
                    # if collides immediately -> game over
                    if collides(current.x, current.y, current.cells(), grid):
                        game_over = True

        # draw
        screen.fill(BLACK)
        # playfield area
        playfield_surface = pygame.Surface((COLS * BLOCK, HEIGHT))
        playfield_surface.fill(BLACK)
        draw_board(playfield_surface, grid)
        if not game_over:
            draw_piece(playfield_surface, current)
        draw_grid(playfield_surface)
        screen.blit(playfield_surface, (0, 0))

        draw_sidebar(screen, font, score, level, lines_cleared_total, next_kind)

        if game_over:
            game_over_screen(screen, font_big, font, score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
