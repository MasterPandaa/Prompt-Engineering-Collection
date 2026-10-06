import pygame
import random
import sys
from typing import Dict, List, Tuple

# Window and grid settings
s_width = 800
s_height = 700
play_width = 300   # 10 blocks wide
play_height = 600  # 20 blocks tall
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
LIGHT_GREY = (180, 180, 180)

# Shape formats (5x5 templates)
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (80, 220, 100),   # S - green
    (220, 60, 80),    # Z - red
    (60, 200, 240),   # I - cyan
    (240, 240, 70),   # O - yellow
    (60, 120, 220),   # J - blue
    (240, 160, 60),   # L - orange
    (180, 70, 200)    # T - purple
]

# Type aliases
Grid = List[List[Tuple[int, int, int]]]
LockedPositions = Dict[Tuple[int, int], Tuple[int, int, int]]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # index of rotation state

    def clone(self) -> 'Piece':
        p = Piece(self.x, self.y, self.shape)
        p.rotation = self.rotation
        return p


def create_grid(locked: LockedPositions) -> Grid:
    grid: Grid = [[BLACK for _ in range(10)] for _ in range(20)]

    for (x, y), color in locked.items():
        if 0 <= y < 20 and 0 <= x < 10:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece: Piece, grid: Grid) -> bool:
    accepted_positions = [(j, i) for i in range(20) for j in range(10) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        x, y = pos
        if y < 0:
            continue
        if (x, y) not in accepted_positions:
            return False
    return True


def check_lost(locked: LockedPositions) -> bool:
    for (_, y) in locked.keys():
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('segoeui', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2),
                         top_left_y + play_height/2 - label.get_height()/2))


def draw_grid_lines(surface):
    # draw grid border
    pygame.draw.rect(surface, WHITE, (top_left_x - 2, top_left_y - 2, play_width + 4, play_height + 4), 2)
    # draw internal lines
    for i in range(20):
        pygame.draw.line(surface, LIGHT_GREY, (top_left_x, top_left_y + i*block_size),
                         (top_left_x + play_width, top_left_y + i*block_size))
    for j in range(10):
        pygame.draw.line(surface, LIGHT_GREY, (top_left_x + j*block_size, top_left_y),
                         (top_left_x + j*block_size, top_left_y + play_height))


def draw_window(surface, grid: Grid, score: int, level: int, lines: int):
    surface.fill((20, 20, 25))

    # Title
    font = pygame.font.SysFont('segoeui', 48, bold=True)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2, 30))

    # Score box
    font_small = pygame.font.SysFont('segoeui', 22)
    stats_x = top_left_x + play_width + 40
    stats_y = top_left_y
    lines_surf = font_small.render(f'Lines: {lines}', True, WHITE)
    level_surf = font_small.render(f'Level: {level}', True, WHITE)
    score_surf = font_small.render(f'Score: {score}', True, WHITE)

    surface.blit(lines_surf, (stats_x, stats_y))
    surface.blit(level_surf, (stats_x, stats_y + 28))
    surface.blit(score_surf, (stats_x, stats_y + 56))

    # Draw grid cells
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != BLACK:
                pygame.draw.rect(surface, color, (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), border_radius=4)
            else:
                # draw subtle background squares
                pygame.draw.rect(surface, (30, 30, 38), (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size))

    draw_grid_lines(surface)


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont('segoeui', 24, bold=True)
    label = font.render('Next', True, WHITE)

    sx = top_left_x - 150
    sy = top_left_y + 80

    surface.blit(label, (sx + 50 - label.get_width()/2, sy - 40))

    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (sx + j*20, sy + i*20, 20, 20), border_radius=3)


def draw_ghost(piece: Piece, grid: Grid, surface):
    ghost = piece.clone()
    while True:
        ghost.y += 1
        if not valid_space(ghost, grid):
            ghost.y -= 1
            break
    for (x, y) in convert_shape_format(ghost):
        if y >= 0:
            rect = pygame.Rect(top_left_x + x*block_size, top_left_y + y*block_size, block_size, block_size)
            pygame.draw.rect(surface, (200, 200, 200), rect, width=2, border_radius=4)


def clear_rows(grid: Grid, locked: LockedPositions) -> int:
    removed = 0
    for i in range(len(grid)-1, -1, -1):
        if BLACK not in grid[i]:
            removed += 1
            # remove locked in this row
            for j in range(10):
                try:
                    del locked[(j, i)]
                except KeyError:
                    continue
            # shift rows above down
            for y in range(i-1, -1, -1):
                for x in range(10):
                    if (x, y) in locked:
                        locked[(x, y+1)] = locked[(x, y)]
                        del locked[(x, y)]
            # after shifting, re-check same row index i
            # because new content came down
            for j in range(10):
                grid[i][j] = BLACK
            # Continue loop to check next row up
    return removed


def try_rotate_with_kick(piece: Piece, grid: Grid) -> bool:
    old_rot = piece.rotation
    piece.rotation = (piece.rotation + 1) % len(piece.shape)
    # Try direct
    if valid_space(piece, grid):
        return True
    # Wall kicks: shift x by -1, +1, -2, +2
    for dx in (-1, 1, -2, 2):
        piece.x += dx
        if valid_space(piece, grid):
            return True
        piece.x -= dx
    # Revert
    piece.rotation = old_rot
    return False


def hard_drop(piece: Piece, grid: Grid):
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def calculate_score(lines_cleared: int, level: int) -> int:
    # Standard-ish Tetris scoring per number of lines
    table = {1: 40, 2: 100, 3: 300, 4: 1200}
    return table.get(lines_cleared, 0) * max(level, 1)


def main(surface):
    locked_positions: LockedPositions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.6  # seconds

    score = 0
    level = 1
    lines_cleared_total = 0

    paused = False

    while run:
        grid = create_grid(locked_positions)
        delta_ms = clock.tick(60)
        if not paused:
            fall_time += delta_ms / 1000.0

        # Auto fall
        if not paused and fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit(0)

                if event.key == pygame.K_p:
                    paused = not paused

                if paused:
                    continue

                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        change_piece = True
                elif event.key == pygame.K_UP:
                    try_rotate_with_kick(current_piece, grid)
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid)
                    change_piece = True
                elif event.key == pygame.K_r:
                    # restart
                    locked_positions.clear()
                    grid = create_grid(locked_positions)
                    current_piece = get_shape()
                    next_piece = get_shape()
                    score = 0
                    level = 1
                    lines_cleared_total = 0
                    fall_speed = 0.6

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        # Draw
        draw_window(surface, grid, score, level, lines_cleared_total)
        draw_next_shape(next_piece, surface)
        draw_ghost(current_piece, grid, surface)
        pygame.display.update()

        # If piece landed
        if change_piece and not paused:
            for pos in shape_pos:
                x, y = pos
                if y >= 0:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Clear rows
            grid = create_grid(locked_positions)
            removed = clear_rows(grid, locked_positions)
            if removed > 0:
                score += calculate_score(removed, level)
                lines_cleared_total += removed
                # Increase level every 10 lines, speed up
                new_level = 1 + lines_cleared_total // 10
                if new_level != level:
                    level = new_level
                    fall_speed = max(0.1, 0.6 - (level - 1) * 0.05)

            # Check loss
            if check_lost(locked_positions):
                draw_window(surface, grid, score, level, lines_cleared_total)
                draw_text_middle(surface, "GAME OVER", 48, WHITE)
                pygame.display.update()
                pygame.time.delay(1500)
                return  # back to menu


def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris - Pygame')

    clock = pygame.time.Clock()

    while True:
        surface.fill((20, 20, 25))
        draw_text_middle(surface, "Press ENTER to Play", 36, WHITE)
        font = pygame.font.SysFont('segoeui', 18)
        help_lines = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "P: Pause, R: Restart, Q: Quit",
        ]
        for i, t in enumerate(help_lines):
            txt = font.render(t, True, LIGHT_GREY)
            surface.blit(txt, (top_left_x + play_width + 40, top_left_y + 120 + i*22))

        pygame.display.update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(surface)
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit(0)


if __name__ == '__main__':
    main_menu()
