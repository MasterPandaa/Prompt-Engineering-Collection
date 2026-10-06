# tetris.py
# Tetris Clone with OOP Structure (Piece, Board), Ghost Piece, Efficient Line Clearing
# Dependencies: pygame (pip install pygame)

import sys
import random
import pygame

# ------------- CONFIG -------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 720
PLAY_WIDTH = 300             # 10 blocks wide
PLAY_HEIGHT = 600            # 20 blocks tall
BLOCK_SIZE = PLAY_WIDTH // 10

GRID_COLS = 10
GRID_ROWS = 20

TOP_MARGIN = 60
SIDE_MARGIN = (SCREEN_WIDTH - PLAY_WIDTH) // 2

DROP_START_SPEED = 0.8       # seconds per tile drop at level 1
SPEEDUP_PER_LEVEL = 0.07     # decrease seconds per level
LINES_PER_LEVEL = 10

BG_COLOR = (16, 18, 24)
GRID_COLOR = (38, 42, 56)
TEXT_COLOR = (230, 235, 245)
GHOST_COLOR = (255, 255, 255)  # used with alpha
OUTLINE_COLOR = (255, 255, 255)

# ------------- SHAPES -------------
# Tetromino rotation states (0..3): each as 4x4 matrix
# 1 values indicate filled; 0 empty
TETROMINOES = {
    'I': {
        'color': (80, 200, 255),
        'rotations': [
            [
                [0,0,0,0],
                [1,1,1,1],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,0,1,0],
                [0,0,1,0],
                [0,0,1,0],
                [0,0,1,0],
            ],
            [
                [0,0,0,0],
                [0,0,0,0],
                [1,1,1,1],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [0,1,0,0],
                [0,1,0,0],
                [0,1,0,0],
            ],
        ]
    },
    'O': {
        'color': (255, 220, 80),
        'rotations': [
            [
                [0,1,1,0],
                [0,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,1,0],
                [0,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,1,0],
                [0,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,1,0],
                [0,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
        ]
    },
    'T': {
        'color': (196, 112, 245),
        'rotations': [
            [
                [0,1,0,0],
                [1,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [0,1,1,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
            [
                [0,0,0,0],
                [1,1,1,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
        ]
    },
    'S': {
        'color': (120, 230, 100),
        'rotations': [
            [
                [0,1,1,0],
                [1,1,0,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,0,0],
            ],
            [
                [0,0,0,0],
                [0,1,1,0],
                [1,1,0,0],
                [0,0,0,0],
            ],
            [
                [1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
        ]
    },
    'Z': {
        'color': (240, 90, 90),
        'rotations': [
            [
                [1,1,0,0],
                [0,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,0,1,0],
                [0,1,1,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
            [
                [0,0,0,0],
                [1,1,0,0],
                [0,1,1,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [1,1,0,0],
                [1,0,0,0],
                [0,0,0,0],
            ],
        ]
    },
    'J': {
        'color': (100, 140, 255),
        'rotations': [
            [
                [1,0,0,0],
                [1,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,1,0],
                [0,1,0,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
            [
                [0,0,0,0],
                [1,1,1,0],
                [0,0,1,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [0,1,0,0],
                [1,1,0,0],
                [0,0,0,0],
            ],
        ]
    },
    'L': {
        'color': (255, 170, 70),
        'rotations': [
            [
                [0,0,1,0],
                [1,1,1,0],
                [0,0,0,0],
                [0,0,0,0],
            ],
            [
                [0,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,0,0],
            ],
            [
                [0,0,0,0],
                [1,1,1,0],
                [1,0,0,0],
                [0,0,0,0],
            ],
            [
                [1,1,0,0],
                [0,1,0,0],
                [0,1,0,0],
                [0,0,0,0],
            ],
        ]
    },
}

PIECE_TYPES = list(TETROMINOES.keys())

# ------------- UTILS -------------
def rotate_matrix_cw(matrix):
    # rotate 4x4 clockwise
    return [list(reversed(col)) for col in zip(*matrix)]

def matrix_cells(matrix):
    for r in range(4):
        for c in range(4):
            if matrix[r][c]:
                yield r, c

# ------------- CLASSES -------------

class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.rot_index = 0
        self.rotations = TETROMINOES[kind]['rotations']
        self.color = TETROMINOES[kind]['color']
        # Spawn near top center: x is grid column, y is grid row
        # Position refers to top-left of 4x4 bounding box
        self.x = GRID_COLS // 2 - 2
        self.y = -2  # start above visible grid to allow entry

    def current_matrix(self):
        return self.rotations[self.rot_index % 4]

    def get_cells(self, x=None, y=None, rot_index=None):
        """Return absolute grid positions occupied by this piece."""
        if x is None: x = self.x
        if y is None: y = self.y
        if rot_index is None: rot_index = self.rot_index
        mat = self.rotations[rot_index % 4]
        for r, c in matrix_cells(mat):
            yield (y + r, x + c)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotated_with_kicks(self, board, dir=1):
        """Try rotate with simple wall kicks: offsets in x direction."""
        if self.kind == 'O':
            # O rotation doesn't change shape; still try for collision correction if needed
            new_rot = self.rot_index
        else:
            new_rot = (self.rot_index + dir) % 4

        kicks = [0, -1, 1, -2, 2]
        for k in kicks:
            if not board.collides(self, x=self.x + k, y=self.y, rot_index=new_rot):
                self.x += k
                self.rot_index = new_rot
                return True
        return False


class Board:
    def __init__(self, rows=GRID_ROWS, cols=GRID_COLS):
        self.rows = rows
        self.cols = cols
        # grid stores (r,g,b) color tuples or None for empty
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

    def in_bounds(self, x, y):
        return 0 <= x < self.cols and y < self.rows

    def collides(self, piece: Piece, x=None, y=None, rot_index=None):
        for ry, rx in piece.get_cells(x=x, y=y, rot_index=rot_index):
            if rx < 0 or rx >= self.cols or ry >= self.rows:
                return True
            if ry >= 0 and self.grid[ry][rx] is not None:
                return True
        return False

    def lock_piece(self, piece: Piece):
        for ry, rx in piece.get_cells():
            if ry < 0:
                # piece locked above top -> game over
                self.game_over = True
            else:
                self.grid[ry][rx] = piece.color
        if not self.game_over:
            lines = self.clear_lines_efficient()
            self.update_score(lines)

    def clear_lines_efficient(self):
        # Build a new grid keeping only non-full rows, then pad with empty rows at the top.
        new_rows = []
        cleared = 0
        for r in range(self.rows):
            if all(self.grid[r][c] is not None for c in range(self.cols)):
                cleared += 1
            else:
                new_rows.append(self.grid[r])
        if cleared > 0:
            empty_row = [None for _ in range(self.cols)]
            self.grid = [empty_row[:] for _ in range(cleared)] + new_rows
        return cleared

    def update_score(self, lines):
        if lines == 0:
            return
        # Standard-ish tetris line clear points
        line_points = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_points.get(lines, 0) * self.level
        self.lines_cleared += lines
        if self.lines_cleared // LINES_PER_LEVEL + 1 > self.level:
            self.level += 1

    def hard_drop_distance(self, piece: Piece):
        dist = 0
        while not self.collides(piece, x=piece.x, y=piece.y + dist + 1, rot_index=piece.rot_index):
            dist += 1
        return dist

    def draw(self, surface, font, current_piece: Piece, next_piece: Piece):
        # Background playfield
        play_rect = pygame.Rect(SIDE_MARGIN, TOP_MARGIN, PLAY_WIDTH, PLAY_HEIGHT)
        pygame.draw.rect(surface, (25, 28, 38), play_rect, border_radius=8)

        # Draw static grid
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    SIDE_MARGIN + c * BLOCK_SIZE,
                    TOP_MARGIN + r * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE
                )
                # grid lines
                pygame.draw.rect(surface, GRID_COLOR, rect, width=1)
                # filled blocks
                color = self.grid[r][c]
                if color:
                    pygame.draw.rect(surface, color, rect.inflate(-2, -2), border_radius=5)

        # Draw ghost piece
        if current_piece and not self.game_over:
            ghost_y_offset = self.hard_drop_distance(current_piece)
            for ry, rx in current_piece.get_cells(y=current_piece.y + ghost_y_offset):
                if ry < 0:
                    continue
                rect = pygame.Rect(
                    SIDE_MARGIN + rx * BLOCK_SIZE,
                    TOP_MARGIN + ry * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE
                )
                ghost_surface = pygame.Surface((BLOCK_SIZE-2, BLOCK_SIZE-2), pygame.SRCALPHA)
                ghost_surface.fill((GHOST_COLOR[0], GHOST_COLOR[1], GHOST_COLOR[2], 55))
                surface.blit(ghost_surface, rect.move(1,1))
                pygame.draw.rect(surface, (255,255,255,90), rect.inflate(-2, -2), width=2, border_radius=5)

        # Draw current falling piece
        if current_piece and not self.game_over:
            for ry, rx in current_piece.get_cells():
                if ry < 0:
                    continue
                rect = pygame.Rect(
                    SIDE_MARGIN + rx * BLOCK_SIZE,
                    TOP_MARGIN + ry * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE
                )
                pygame.draw.rect(surface, current_piece.color, rect.inflate(-2, -2), border_radius=5)
                # outline
                pygame.draw.rect(surface, OUTLINE_COLOR, rect.inflate(-2, -2), width=1, border_radius=5)

        # Sidebar UI
        self.draw_sidebar(surface, font, next_piece)

    def draw_sidebar(self, surface, font, next_piece: Piece):
        # Title
        title = font.render("TETRIS", True, TEXT_COLOR)
        surface.blit(title, (SIDE_MARGIN, 12))

        # Score and Level
        y = TOP_MARGIN
        lines_surf = font.render(f"Lines: {self.lines_cleared}", True, TEXT_COLOR)
        score_surf = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lvl_surf = font.render(f"Level: {self.level}", True, TEXT_COLOR)

        surface.blit(lines_surf, (SIDE_MARGIN + PLAY_WIDTH + 24, y))
        surface.blit(score_surf, (SIDE_MARGIN + PLAY_WIDTH + 24, y + 32))
        surface.blit(lvl_surf, (SIDE_MARGIN + PLAY_WIDTH + 24, y + 64))

        # Next piece preview
        next_surf = font.render("Next:", True, TEXT_COLOR)
        surface.blit(next_surf, (SIDE_MARGIN + PLAY_WIDTH + 24, y + 110))

        preview_top_left = (SIDE_MARGIN + PLAY_WIDTH + 24, y + 140)
        self.draw_preview(surface, next_piece, preview_top_left)

    def draw_preview(self, surface, piece: Piece, top_left):
        if not piece:
            return
        mat = piece.current_matrix()
        # compute bounding box of non-empty cells to center preview
        cells = [(r, c) for r, c in matrix_cells(mat)]
        if not cells:
            return
        min_r = min(r for r, _ in cells)
        max_r = max(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        max_c = max(c for _, c in cells)

        width = (max_c - min_c + 1) * BLOCK_SIZE
        height = (max_r - min_r + 1) * BLOCK_SIZE
        start_x = top_left[0] + (BLOCK_SIZE * 4 - width) // 2
        start_y = top_left[1] + (BLOCK_SIZE * 4 - height) // 2

        preview_rect = pygame.Rect(top_left[0], top_left[1], BLOCK_SIZE * 4, BLOCK_SIZE * 4)
        pygame.draw.rect(surface, (25, 28, 38), preview_rect, border_radius=8)
        for r, c in cells:
            px = start_x + (c - min_c) * BLOCK_SIZE
            py = start_y + (r - min_r) * BLOCK_SIZE
            rect = pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, piece.color, rect.inflate(-2, -2), border_radius=5)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect.inflate(-2, -2), width=1, border_radius=5)


# ------------- GAME CONTROL -------------

class BagGenerator:
    """7-bag randomizer for fair tetromino distribution."""
    def __init__(self):
        self.bag = []

    def next(self):
        if not self.bag:
            self.bag = PIECE_TYPES[:]
            random.shuffle(self.bag)
        return self.bag.pop()

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris (OOP, Ghost, Efficient Clear)")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22)

        self.board = Board()
        self.rng = BagGenerator()

        self.current = Piece(self.rng.next())
        self.next_piece = Piece(self.rng.next())

        self.drop_timer = 0.0
        self.fast_drop = False

        # simple DAS/ARR for horizontal movement
        self.move_dir = 0
        self.move_hold_time = 0.0
        self.move_repeat_delay = 0.14
        self.move_initial_delay = 0.20

    def reset(self):
        self.board = Board()
        self.current = Piece(self.rng.next())
        self.next_piece = Piece(self.rng.next())
        self.drop_timer = 0.0
        self.fast_drop = False
        self.move_dir = 0
        self.move_hold_time = 0.0

    def spawn_new_piece(self):
        self.current = self.next_piece
        self.next_piece = Piece(self.rng.next())
        # If spawn collides -> game over
        if self.board.collides(self.current, x=self.current.x, y=self.current.y, rot_index=self.current.rot_index):
            self.board.game_over = True

    def soft_drop_speed(self):
        base = max(0.05, DROP_START_SPEED - (self.board.level - 1) * SPEEDUP_PER_LEVEL)
        return base / 6.0  # faster during soft drop

    def gravity_speed(self):
        return max(0.05, DROP_START_SPEED - (self.board.level - 1) * SPEEDUP_PER_LEVEL)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()

        # Continuous left/right with DAS/ARR
        dir_now = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dir_now = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dir_now = 1

        if dir_now != 0:
            if self.move_dir != dir_now:
                # direction changed or started fresh -> move once and reset timer
                if not self.board.collides(self.current, x=self.current.x + dir_now, y=self.current.y, rot_index=self.current.rot_index):
                    self.current.move(dir_now, 0)
                self.move_dir = dir_now
                self.move_hold_time = 0.0
            else:
                # hold
                self.move_hold_time += dt
                threshold = self.move_initial_delay if self.move_hold_time < self.move_initial_delay else self.move_repeat_delay
                # step multiple times if dt large
                while self.move_hold_time >= threshold:
                    self.move_hold_time -= threshold
                    if not self.board.collides(self.current, x=self.current.x + dir_now, y=self.current.y, rot_index=self.current.rot_index):
                        self.current.move(dir_now, 0)
                    threshold = self.move_repeat_delay
        else:
            self.move_dir = 0
            self.move_hold_time = 0.0

        # Fast drop toggle
        self.fast_drop = keys[pygame.K_DOWN] or keys[pygame.K_s]

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit()
                    sys.exit(0)
                if self.board.game_over:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                    continue

                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_x):
                    # Rotate CW with kicks
                    self.current.rotated_with_kicks(self.board, dir=1)
                elif event.key in (pygame.K_z,):
                    # Rotate CCW with kicks
                    self.current.rotated_with_kicks(self.board, dir=-1)
                elif event.key in (pygame.K_SPACE,):
                    # Hard drop
                    dy = self.board.hard_drop_distance(self.current)
                    self.current.move(0, dy)
                    self.board.lock_piece(self.current)
                    if not self.board.game_over:
                        self.spawn_new_piece()

    def update(self, dt):
        if self.board.game_over:
            return

        self.handle_input(dt)

        # Gravity
        self.drop_timer += dt
        interval = self.soft_drop_speed() if self.fast_drop else self.gravity_speed()
        while self.drop_timer >= interval:
            self.drop_timer -= interval
            if not self.board.collides(self.current, x=self.current.x, y=self.current.y + 1, rot_index=self.current.rot_index):
                self.current.move(0, 1)
            else:
                # lock
                self.board.lock_piece(self.current)
                if not self.board.game_over:
                    self.spawn_new_piece()

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.board.draw(self.screen, self.font, self.current, self.next_piece)

        if self.board.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0,0))

        big_font = pygame.font.SysFont("consolas", 42, bold=True)
        small_font = pygame.font.SysFont("consolas", 24)

        text1 = big_font.render("GAME OVER", True, (255, 110, 110))
        text2 = small_font.render("Press Enter or Space to Restart", True, TEXT_COLOR)
        text3 = small_font.render(f"Score: {self.board.score}   Lines: {self.board.lines_cleared}   Level: {self.board.level}", True, TEXT_COLOR)

        self.screen.blit(text1, (SCREEN_WIDTH//2 - text1.get_width()//2, SCREEN_HEIGHT//2 - 90))
        self.screen.blit(text3, (SCREEN_WIDTH//2 - text3.get_width()//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, SCREEN_HEIGHT//2 + 5))

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            self.process_events()
            self.update(dt)
            self.draw()


# ------------- MAIN -------------
if __name__ == "__main__":
    Game().run()
