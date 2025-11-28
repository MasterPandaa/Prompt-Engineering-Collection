# tetris.py
# Tetris Clone using Python and Pygame
# Requirements: pip install pygame

import sys
import random
import pygame
from pygame import Rect

# ----------------------------
# Config and Constants
# ----------------------------

CELL_SIZE = 32
COLS = 10
ROWS = 20
SIDE_PANEL_WIDTH = 6  # columns for side UI area
FPS = 60

# Gravity config (frames between falls). Speeds up with level.
GRAVITY_FRAMES_BY_LEVEL = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 2, 2]  # len>=20
SOFT_DROP_FACTOR = 8  # faster than gravity

# Scoring (classic-ish)
SCORE_PER_LINE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800
}
SCORE_SOFT_DROP = 1
SCORE_HARD_DROP = 2

# Colors
COLOR_BG = (18, 18, 18)
COLOR_GRID = (40, 40, 40)
COLOR_TEXT = (230, 230, 230)
COLOR_GHOST_ALPHA = 60  # not using alpha surfaces; we draw outline; kept for reference

# Tetromino colors
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
}

# Tetromino rotation states (4x4 matrices)
# 1 indicates filled cell, 0 is empty. Rotation index cycles 0..3.
SHAPES = {
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
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
        ],
    ],
    'O': [
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        # O rotation is the same for all 4
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'T': [
        [
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'S': [
        [
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'Z': [
        [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'J': [
        [
            [1, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
    'L': [
        [
            [0, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
        ],
    ],
}

TETROMINO_KEYS = list(SHAPES.keys())

# ----------------------------
# Utility
# ----------------------------

def get_shape_cells(shape_matrix):
    cells = []
    for r in range(4):
        for c in range(4):
            if shape_matrix[r][c]:
                cells.append((r, c))
    return cells

# Precompute shape cells per rotation for efficiency
SHAPE_CELLS = {
    k: [get_shape_cells(rot) for rot in rotations]
    for k, rotations in SHAPES.items()
}

# ----------------------------
# Piece Class
# ----------------------------

class Piece:
    def __init__(self, key, x, y):
        self.key = key
        self.rotation = 0
        self.x = x  # grid col
        self.y = y  # grid row
        self.color = COLORS[key]

    def get_cells(self, rotation=None, offset=None):
        rot = self.rotation if rotation is None else rotation
        cells = SHAPE_CELLS[self.key][rot]
        offx, offy = (0, 0) if offset is None else offset
        return [(self.y + r + offy, self.x + c + offx) for (r, c) in cells]

    def rotate_cw(self, board):
        old_rot = self.rotation
        new_rot = (self.rotation + 1) % 4
        # Try simple wall kicks
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
        for dx, dy in kicks:
            if board.valid_position(self, rotation=new_rot, offset=(dx, dy)):
                self.rotation = new_rot
                self.x += dx
                self.y += dy
                return True
        # fail -> no rotation
        self.rotation = old_rot
        return False

    def rotate_ccw(self, board):
        old_rot = self.rotation
        new_rot = (self.rotation - 1) % 4
        kicks = [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0), (0, -1)]
        for dx, dy in kicks:
            if board.valid_position(self, rotation=new_rot, offset=(dx, dy)):
                self.rotation = new_rot
                self.x += dx
                self.y += dy
                return True
        self.rotation = old_rot
        return False

    def move(self, board, dx, dy):
        if board.valid_position(self, offset=(dx, dy)):
            self.x += dx
            self.y += dy
            return True
        return False

# ----------------------------
# Board Class
# ----------------------------

class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # grid: 0 empty, else (r,g,b)
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.cleared_lines_total = 0

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cleared_lines_total = 0

    def inside(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def cell_empty(self, row, col):
        return self.grid[row][col] == 0

    def valid_position(self, piece, rotation=None, offset=None):
        for (r, c) in piece.get_cells(rotation=rotation, offset=offset):
            if r < 0:
                # allow above top but cannot collide with existing cells
                # We check collision only if within bounds and not empty
                # If r < 0: treat as pass unless outside horizontally
                if not (0 <= c < self.cols):
                    return False
                # above top is okay
                continue
            if not self.inside(r, c):
                return False
            if not self.cell_empty(r, c):
                return False
        return True

    def lock_piece(self, piece):
        for (r, c) in piece.get_cells():
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = piece.color

    def clear_full_lines(self):
        # Efficient line clearing: filter rows that are not full, count removed, then rebuild
        new_rows = []
        lines_cleared = 0
        for r in range(self.rows):
            if all(self.grid[r][c] != 0 for c in range(self.cols)):
                lines_cleared += 1
            else:
                new_rows.append(self.grid[r])
        # Add empty rows on top
        while len(new_rows) < self.rows:
            new_rows.insert(0, [0 for _ in range(self.cols)])
        self.grid = new_rows
        self.cleared_lines_total += lines_cleared
        return lines_cleared

    def get_ghost_drop_y(self, piece):
        # Simulate drop to final y
        ghost_y = piece.y
        while True:
            test_cells = [(r + 1, c) for (r, c) in piece.get_cells()]
            valid = True
            for (r, c) in test_cells:
                if r < 0:
                    # cell above top moving down is fine unless out of bounds horizontally
                    if not (0 <= c < self.cols):
                        valid = False
                        break
                    continue
                if not self.inside(r, c) or not self.cell_empty(r, c):
                    valid = False
                    break
            if valid:
                ghost_y += 1
            else:
                break
        return ghost_y

# ----------------------------
# Bag Randomizer
# ----------------------------

class SevenBag:
    def __init__(self):
        self.bag = []

    def next(self):
        if not self.bag:
            self.bag = TETROMINO_KEYS[:]
            random.shuffle(self.bag)
        return self.bag.pop()

# ----------------------------
# Game Class
# ----------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris - OOP with Ghost Piece")
        self.font_small = pygame.font.SysFont("consolas", 18)
        self.font_large = pygame.font.SysFont("consolas", 28, bold=True)

        self.board = Board(ROWS, COLS)
        self.bag = SevenBag()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

        self.current = self.spawn_piece()
        self.next_piece_key = self.bag.next()
        self.game_over = False
        self.paused = False

        # Input repeat control
        self.move_cooldown = 0
        self.move_delay = 5  # frames between repeats when holding

        # Gravity timers
        self.gravity_counter = 0
        self.soft_drop = False

        # Window size
        self.play_width = COLS * CELL_SIZE
        self.play_height = ROWS * CELL_SIZE
        self.side_width = SIDE_PANEL_WIDTH * CELL_SIZE
        w = self.play_width + self.side_width
        h = self.play_height
        self.screen = pygame.display.set_mode((w, h))
        self.clock = pygame.time.Clock()

    def spawn_piece(self):
        key = self.bag.next()
        # Spawn at top-middle (x col so that 4x4 matrices can fit)
        piece = Piece(key, x=COLS // 2 - 2, y=-2)
        if not self.board.valid_position(piece):
            # immediate collision means game over
            self.game_over = True
        return piece

    def promote_next_piece(self):
        self.current = Piece(self.next_piece_key, x=COLS // 2 - 2, y=-2)
        self.next_piece_key = self.bag.next()
        if not self.board.valid_position(self.current):
            self.game_over = True

    def calculate_gravity_frames(self):
        idx = min(self.level - 1, len(GRAVITY_FRAMES_BY_LEVEL) - 1)
        return GRAVITY_FRAMES_BY_LEVEL[idx]

    def hard_drop(self):
        drop_distance = 0
        while self.current.move(self.board, 0, 1):
            drop_distance += 1
        self.score += SCORE_HARD_DROP * drop_distance
        self.lock_and_next()

    def lock_and_next(self):
        self.board.lock_piece(self.current)
        cleared = self.board.clear_full_lines()
        if cleared > 0:
            self.lines_cleared += cleared
            self.score += SCORE_PER_LINE.get(cleared, 0) * self.level
            # Level up every 10 lines
            while self.lines_cleared >= self.level * 10:
                self.level += 1
        self.promote_next_piece()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.move_cooldown == 0:
                self.current.move(self.board, -1, 0)
                self.move_cooldown = self.move_delay
        elif keys[pygame.K_RIGHT]:
            if self.move_cooldown == 0:
                self.current.move(self.board, 1, 0)
                self.move_cooldown = self.move_delay
        else:
            self.move_cooldown = 0

        self.soft_drop = keys[pygame.K_DOWN]
        if self.soft_drop:
            # Soft drop scoring occurs per step in update()
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key in (pygame.K_UP, pygame.K_x):
                    self.current.rotate_cw(self.board)
                elif event.key == pygame.K_z:
                    self.current.rotate_ccw(self.board)
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()

    def update(self):
        if self.game_over or self.paused:
            return

        self.handle_input()

        # Gravity
        gravity_frames = self.calculate_gravity_frames()
        if self.soft_drop:
            step = max(1, gravity_frames // SOFT_DROP_FACTOR)
        else:
            step = gravity_frames

        self.gravity_counter += 1
        if self.gravity_counter >= step:
            self.gravity_counter = 0
            moved = self.current.move(self.board, 0, 1)
            if moved:
                if self.soft_drop:
                    self.score += SCORE_SOFT_DROP
            else:
                # lock piece
                self.lock_and_next()

    def draw_cell(self, surface, row, col, color, border=True, alpha=False):
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        rect = Rect(x, y, CELL_SIZE, CELL_SIZE)
        if not alpha:
            pygame.draw.rect(surface, color, rect)
        else:
            # Ghost: draw as outline and a faint fill using darker color
            faint = tuple(max(0, min(255, int(c * 0.35))) for c in color)
            pygame.draw.rect(surface, faint, rect)
        if border:
            pygame.draw.rect(surface, (30, 30, 30), rect, 1)

    def draw_board(self, surface):
        # Background
        surface.fill(COLOR_BG)
        # Grid lines
        for r in range(ROWS):
            for c in range(COLS):
                rect = Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, COLOR_GRID, rect, 1)

        # Locked cells
        for r in range(ROWS):
            for c in range(COLS):
                if self.board.grid[r][c]:
                    self.draw_cell(surface, r, c, self.board.grid[r][c])

    def draw_piece(self, surface, piece):
        for (r, c) in piece.get_cells():
            if r >= 0:
                self.draw_cell(surface, r, c, piece.color)

    def draw_ghost(self, surface, piece):
        ghost_y = self.board.get_ghost_drop_y(piece)
        for (r, c) in piece.get_cells():
            gr = r - piece.y + ghost_y
            if gr >= 0:
                # draw faint colored fill with border as ghost
                self.draw_cell(surface, gr, c, piece.color, border=True, alpha=True)

    def draw_side_panel(self, surface):
        # Side panel background
        panel_rect = Rect(self.play_width, 0, self.side_width, self.play_height)
        pygame.draw.rect(surface, (25, 25, 25), panel_rect)

        # Text helper
        def render_text(text, y, big=False):
            font = self.font_large if big else self.font_small
            img = font.render(text, True, COLOR_TEXT)
            surface.blit(img, (self.play_width + 12, y))

        y_cursor = 16
        render_text("TETRIS", y_cursor, big=True)
        y_cursor += 36
        render_text(f"Score: {self.score}", y_cursor); y_cursor += 24
        render_text(f"Level: {self.level}", y_cursor); y_cursor += 24
        render_text(f"Lines: {self.lines_cleared}", y_cursor); y_cursor += 32

        render_text("Next:", y_cursor); y_cursor += 8
        self.draw_next_preview(surface, y_cursor)
        y_cursor += 6 * CELL_SIZE

        render_text("Controls:", y_cursor); y_cursor += 22
        for line in [
            "Arrows: Move",
            "Up/X: Rotate CW",
            "Z: Rotate CCW",
            "Space: Hard Drop",
            "Down: Soft Drop",
            "P: Pause",
            "Esc: Quit",
        ]:
            render_text(line, y_cursor)
            y_cursor += 18

        if self.paused:
            pause_img = self.font_large.render("PAUSED", True, (255, 220, 0))
            surface.blit(pause_img, (self.play_width + 12, self.play_height - 60))

        if self.game_over:
            over_img = self.font_large.render("GAME OVER", True, (255, 80, 80))
            surface.blit(over_img, (self.play_width + 12, self.play_height - 100))
            hint_img = self.font_small.render("Press Esc to exit", True, COLOR_TEXT)
            surface.blit(hint_img, (self.play_width + 12, self.play_height - 70))

    def draw_next_preview(self, surface, y_top):
        # Draw next piece in a small matrix at side
        start_x = self.play_width + 12
        start_y = y_top + 12
        # Use rotation 0 center-ish
        temp = Piece(self.next_piece_key, x=0, y=0)
        cells = SHAPE_CELLS[temp.key][0]
        min_r = min(r for (r, c) in cells)
        min_c = min(c for (r, c) in cells)
        # Normalize to top-left at (0,0)
        norm_cells = [(r - min_r, c - min_c) for (r, c) in cells]
        # Determine block size for preview
        for (nr, nc) in norm_cells:
            r_pix = start_y + nr * (CELL_SIZE // 2)
            c_pix = start_x + nc * (CELL_SIZE // 2)
            rect = Rect(c_pix, r_pix, CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.rect(surface, temp.color, rect)
            pygame.draw.rect(surface, (30, 30, 30), rect, 1)

    def render(self):
        # Create playfield surface for easier drawing
        play_surface = pygame.Surface((self.play_width, self.play_height))
        self.draw_board(play_surface)
        if self.current and not self.game_over:
            self.draw_ghost(play_surface, self.current)
            self.draw_piece(play_surface, self.current)
        self.screen.blit(play_surface, (0, 0))

        # Side UI
        side_surface = pygame.Surface((self.side_width, self.play_height))
        # We'll draw directly on main screen for text; use side_surface for potential expansions
        self.draw_side_panel(self.screen)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()

# ----------------------------
# Entry Point
# ----------------------------

if __name__ == "__main__":
    Game().run()
