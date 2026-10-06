import sys
import random
import pygame

# -----------------------------
# Config & Constants
# -----------------------------
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 32
BORDER = 4
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDE_PANEL_WIDTH = 220
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH + BORDER * 3
WINDOW_HEIGHT = PLAY_HEIGHT + BORDER * 2
FPS = 60

# Speeds (seconds per grid cell fall)
START_FALL_SPEED = 0.8
MIN_FALL_SPEED = 0.05
LEVEL_UP_LINES = 10

# Colors
BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)
LIGHT_GRAY = (120, 120, 120)

# Tetromino colors (I, O, T, S, Z, J, L)
PIECE_COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
}

# Tetromino rotation states (SRS-like orientation, simple kicks later)
SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],

        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]],
    ],
    'O': [
        [[0, 1, 1, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]]
    ] * 4,
    'T': [
        [[0, 1, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 0, 0],
         [1, 1, 1, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [1, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],
    ],
    'S': [
        [[0, 1, 1, 0],
         [1, 1, 0, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 0]],

        [[0, 0, 0, 0],
         [0, 1, 1, 0],
         [1, 1, 0, 0],
         [0, 0, 0, 0]],

        [[1, 0, 0, 0],
         [1, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],
    ],
    'Z': [
        [[1, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 1, 0],
         [0, 1, 1, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 0, 0],
         [1, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [1, 1, 0, 0],
         [1, 0, 0, 0],
         [0, 0, 0, 0]],
    ],
    'J': [
        [[1, 0, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 1, 1, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [1, 1, 0, 0],
         [0, 0, 0, 0]],
    ],
    'L': [
        [[0, 0, 1, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0]],

        [[0, 0, 0, 0],
         [1, 1, 1, 0],
         [1, 0, 0, 0],
         [0, 0, 0, 0]],

        [[1, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 0]],
    ],
}

WALL_KICK_OFFSETS = [
    (0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)
]

# -----------------------------
# Model Classes
# -----------------------------
class Piece:
    def __init__(self, kind: str):
        self.kind = kind
        self.rot = 0
        self.shape_states = SHAPES[kind]
        self.color = PIECE_COLORS[kind]
        # Spawn position (x,y) in grid coords
        # Centered horizontally; y negative to allow spawn space
        self.x = GRID_WIDTH // 2 - 2
        self.y = -2

    def get_cells(self, rot=None, x=None, y=None):
        """Return list of (cx, cy) occupied by the piece for a state."""
        r = self.rot if rot is None else rot
        ox = self.x if x is None else x
        oy = self.y if y is None else y
        cells = []
        m = self.shape_states[r % 4]
        for j in range(4):
            for i in range(4):
                if m[j][i]:
                    cells.append((ox + i, oy + j))
        return cells

    def rotate(self, dir: int):
        self.rot = (self.rot + dir) % 4


class Board:
    def __init__(self):
        # grid[y][x] = (r,g,b) or None
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_speed = START_FALL_SPEED
        self.current = None
        self.next_queue = self._generate_bag()
        self.game_over = False

    def _generate_bag(self):
        bag = list(SHAPES.keys())
        random.shuffle(bag)
        return [Piece(k) for k in bag]

    def spawn_new_piece(self):
        if not self.next_queue:
            self.next_queue = self._generate_bag()
        self.current = self.next_queue.pop(0)
        # Adjust spawn so piece is within width
        # If collision at spawn -> game over
        if not self.is_valid_position(self.current, self.current.x, self.current.y, self.current.rot):
            self.game_over = True

    def is_valid_position(self, piece: Piece, x: int, y: int, rot: int) -> bool:
        for cx, cy in piece.get_cells(rot=rot, x=x, y=y):
            if cx < 0 or cx >= GRID_WIDTH or cy >= GRID_HEIGHT:
                return False
            if cy >= 0 and self.grid[cy][cx] is not None:
                return False
        return True

    def lock_piece(self, piece: Piece):
        for cx, cy in piece.get_cells():
            if 0 <= cy < GRID_HEIGHT and 0 <= cx < GRID_WIDTH:
                self.grid[cy][cx] = piece.color
        cleared = self.clear_lines()
        self.update_score(cleared)

    def clear_lines(self) -> int:
        # Efficient line clear: filter rows not full and prepend empty rows
        new_rows = []
        cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                cleared += 1
            else:
                new_rows.append(self.grid[y])
        if cleared:
            # add empty rows on top
            for _ in range(cleared):
                new_rows.insert(0, [None for _ in range(GRID_WIDTH)])
            self.grid = new_rows
        return cleared

    def update_score(self, cleared: int):
        line_scores = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores.get(cleared, 0) * self.level
        self.lines += cleared
        # Level up each LEVEL_UP_LINES lines
        self.level = max(1, self.lines // LEVEL_UP_LINES + 1)
        # Speed up with level
        self.fall_speed = max(MIN_FALL_SPEED, START_FALL_SPEED * (0.85 ** (self.level - 1)))

    def try_move(self, dx: int, dy: int) -> bool:
        if self.current is None:
            return False
        nx = self.current.x + dx
        ny = self.current.y + dy
        if self.is_valid_position(self.current, nx, ny, self.current.rot):
            self.current.x = nx
            self.current.y = ny
            return True
        return False

    def hard_drop(self):
        if self.current is None:
            return
        while self.try_move(0, 1):
            pass
        self.lock_piece(self.current)
        self.spawn_new_piece()

    def rotate_current(self, dir: int):
        if self.current is None:
            return
        old_rot = self.current.rot
        new_rot = (old_rot + dir) % 4
        # Try wall kicks
        for ox, oy in WALL_KICK_OFFSETS:
            nx = self.current.x + ox
            ny = self.current.y + oy
            if self.is_valid_position(self.current, nx, ny, new_rot):
                self.current.rot = new_rot
                self.current.x = nx
                self.current.y = ny
                return
        # if all fails, keep old rot

    def tick_gravity(self) -> bool:
        """Advance one gravity step. Returns True if piece locked."""
        if self.current is None:
            return False
        if not self.try_move(0, 1):
            # lock
            self.lock_piece(self.current)
            self.spawn_new_piece()
            return True
        return False

    def compute_ghost_y(self) -> int:
        if self.current is None:
            return 0
        ghost_y = self.current.y
        while self.is_valid_position(self.current, self.current.x, ghost_y + 1, self.current.rot):
            ghost_y += 1
        return ghost_y


# -----------------------------
# Rendering
# -----------------------------

def blend_color(color, factor=0.5, bg=WHITE):
    r = int(color[0] * (1 - factor) + bg[0] * factor)
    g = int(color[1] * (1 - factor) + bg[1] * factor)
    b = int(color[2] * (1 - factor) + bg[2] * factor)
    return (r, g, b)


def draw_block(surface, x, y, color, alpha=255, outline=True):
    rect = pygame.Rect(BORDER + x * BLOCK_SIZE, BORDER + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    if alpha < 255:
        # draw with a temporary surface for alpha
        temp = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        temp.fill((*color, alpha))
        surface.blit(temp, rect.topleft)
    else:
        pygame.draw.rect(surface, color, rect)
    if outline:
        pygame.draw.rect(surface, GRAY, rect, 1)


def draw_board(surface, board: Board):
    # Playfield background
    pygame.draw.rect(surface, BLACK, (BORDER, BORDER, PLAY_WIDTH, PLAY_HEIGHT))

    # Locked blocks
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            c = board.grid[y][x]
            if c:
                draw_block(surface, x, y, c)

    # Ghost piece
    if board.current and not board.game_over:
        gy = board.compute_ghost_y()
        for cx, cy in board.current.get_cells(y=gy):
            if cy >= 0:
                # lighter color, semi-transparent
                c = blend_color(board.current.color, factor=0.7, bg=WHITE)
                draw_block(surface, cx, cy, c, alpha=120, outline=True)

    # Current piece
    if board.current and not board.game_over:
        for cx, cy in board.current.get_cells():
            if cy >= 0:
                draw_block(surface, cx, cy, board.current.color)

    # Grid lines (optional subtle)
    for x in range(GRID_WIDTH + 1):
        px = BORDER + x * BLOCK_SIZE
        pygame.draw.line(surface, (30, 30, 30), (px, BORDER), (px, BORDER + PLAY_HEIGHT))
    for y in range(GRID_HEIGHT + 1):
        py = BORDER + y * BLOCK_SIZE
        pygame.draw.line(surface, (30, 30, 30), (BORDER, py), (BORDER + PLAY_WIDTH, py))


def draw_side_panel(surface, board: Board, font):
    panel_x = BORDER * 2 + PLAY_WIDTH
    panel_rect = pygame.Rect(panel_x, BORDER, SIDE_PANEL_WIDTH, PLAY_HEIGHT)
    pygame.draw.rect(surface, (20, 20, 20), panel_rect)

    def text(label, y, big=False):
        f = font[1] if big else font[0]
        s = f.render(label, True, WHITE)
        surface.blit(s, (panel_x + 12, y))

    text("TETRIS OOP", panel_rect.top + 10, big=True)
    text(f"Score: {board.score}", panel_rect.top + 70)
    text(f"Lines: {board.lines}", panel_rect.top + 100)
    text(f"Level: {board.level}", panel_rect.top + 130)

    text("Next:", panel_rect.top + 180)
    # Draw next 3
    nx = panel_x + 12
    ny = panel_rect.top + 210
    preview_size = 20
    for i in range(min(3, len(board.next_queue))):
        p = board.next_queue[i]
        for j in range(4):
            for k in range(4):
                if p.shape_states[0][j][k]:
                    rx = nx + k * preview_size + i * 80
                    ry = ny + j * preview_size
                    pygame.draw.rect(surface, p.color, (rx, ry, preview_size, preview_size))
                    pygame.draw.rect(surface, LIGHT_GRAY, (rx, ry, preview_size, preview_size), 1)

    text("Controls:", panel_rect.top + 340)
    controls = [
        "Left/Right: Move",
        "Down: Soft drop",
        "Up/Z: Rotate",
        "Space: Hard drop",
        "P: Pause  R: Restart",
        "Esc: Quit",
    ]
    ty = panel_rect.top + 365
    for s in controls:
        text(s, ty)
        ty += 24

    if board.game_over:
        over = font[1].render("GAME OVER", True, (255, 80, 80))
        surface.blit(over, (panel_x + 12, panel_rect.top + 540))


# -----------------------------
# Game Loop
# -----------------------------

def main():
    pygame.init()
    pygame.display.set_caption("Tetris OOP with Ghost Piece")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    small_font = pygame.font.SysFont("consolas", 18)
    big_font = pygame.font.SysFont("consolas", 28, bold=True)

    board = Board()
    board.spawn_new_piece()

    fall_timer = 0.0
    paused = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    # restart
                    board = Board()
                    board.spawn_new_piece()
                    paused = False
                    fall_timer = 0
                if board.game_over:
                    continue
                if not paused:
                    if event.key == pygame.K_LEFT:
                        board.try_move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        board.try_move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        # soft drop also increments score slightly
                        moved = board.try_move(0, 1)
                        if moved:
                            board.score += 1
                    elif event.key == pygame.K_SPACE:
                        board.hard_drop()
                    elif event.key == pygame.K_UP:
                        board.rotate_current(1)
                    elif event.key == pygame.K_z:
                        board.rotate_current(-1)

        if not paused and not board.game_over:
            fall_timer += dt
            while fall_timer >= board.fall_speed:
                fall_timer -= board.fall_speed
                locked = board.tick_gravity()
                if locked:
                    # after lock, a new piece may spawn; if game over, stop
                    if board.game_over:
                        break

        # Render
        screen.fill((24, 24, 28))
        draw_board(screen, board)
        draw_side_panel(screen, board, (small_font, big_font))

        # Border around play area
        pygame.draw.rect(screen, LIGHT_GRAY, (BORDER-1, BORDER-1, PLAY_WIDTH+2, PLAY_HEIGHT+2), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
