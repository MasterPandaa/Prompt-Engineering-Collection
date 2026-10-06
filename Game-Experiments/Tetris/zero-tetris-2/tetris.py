import pygame
import random
import sys
from typing import List, Tuple, Dict, Optional

# ==========================================
# Constants and Configuration
# ==========================================
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
FPS = 60

# Impeccable Style: Sleek Dark Mode Colors
COLOR_BG = (18, 18, 18)
COLOR_GRID = (40, 40, 40)
COLOR_TEXT = (240, 240, 240)
COLOR_BOARD_BG = (10, 10, 10)
COLOR_BORDER = (100, 100, 100)

COLORS = {
    'I': (0, 229, 255),    # Cyan
    'J': (41, 121, 255),   # Blue
    'L': (255, 145, 0),    # Orange
    'O': (255, 234, 0),    # Yellow
    'S': (0, 230, 118),    # Green
    'T': (213, 0, 249),    # Purple
    'Z': (255, 23, 68),    # Red
}

SHAPES: Dict[str, List[List[int]]] = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}

# ==========================================
# Game Classes
# ==========================================

class Tetromino:
    """
    Represents a Tetris piece, holding its shape matrix, position, and rotation logic.
    """
    def __init__(self, name: str, matrix: List[List[int]], color: Tuple[int, int, int]):
        self.name = name
        self.matrix = [row[:] for row in matrix]
        self.color = color
        self.x = BOARD_WIDTH // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self) -> None:
        """Rotates the matrix 90 degrees clockwise."""
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]

    def rotate_back(self) -> None:
        """Reverts rotation (counter-clockwise)."""
        self.matrix = [list(row) for row in zip(*self.matrix)][::-1]

class Board:
    """
    Manages the game board grid, collision detection, and line clears.
    """
    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT):
        self.width = width
        self.height = height
        # grid stores colors of locked pieces, None if empty
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.game_over = False

    def is_valid_position(self, piece: Tetromino, offset_x: int = 0, offset_y: int = 0) -> bool:
        """
        Checks if the piece is valid at the given offset.
        Optimized to only check active cells.
        """
        for r_idx, row in enumerate(piece.matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + c_idx + offset_x
                    y = piece.y + r_idx + offset_y
                    if x < 0 or x >= self.width or y >= self.height:
                        return False
                    if y >= 0 and self.grid[y][x] is not None:
                        return False
        return True

    def lock_piece(self, piece: Tetromino) -> None:
        """Locks the piece into the board grid."""
        for r_idx, row in enumerate(piece.matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + c_idx
                    y = piece.y + r_idx
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = piece.color
                    else:
                        self.game_over = True # Locked out of bounds (top)

    def clear_lines(self) -> int:
        """
        Clears completed lines and returns the number of lines cleared.
        Uses list comprehension to filter out full rows, then pads at the top.
        """
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = self.height - len(new_grid)
        if lines_cleared > 0:
            padding = [[None for _ in range(self.width)] for _ in range(lines_cleared)]
            self.grid = padding + new_grid
            self.score += [0, 100, 300, 500, 800][lines_cleared]
        return lines_cleared

    def place_piece_temp(self, piece: Tetromino) -> None:
        """Temporarily places a piece on the board (for AI evaluation)."""
        for r_idx, row in enumerate(piece.matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + c_idx
                    y = piece.y + r_idx
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = piece.color

    def remove_piece_temp(self, piece: Tetromino) -> None:
        """Removes a temporarily placed piece."""
        for r_idx, row in enumerate(piece.matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + c_idx
                    y = piece.y + r_idx
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = None


class TetrisAI:
    """
    AI opponent logic. Evaluates board states to choose the best move.
    """
    def __init__(self, board: Board):
        self.board = board

    def _evaluate_board(self) -> float:
        """
        Heuristic scoring function.
        Weights:
        - Aggregate height: penalty for taller stacks
        - Complete lines: reward for lines that will clear
        - Holes: severe penalty for covered empty spaces
        - Bumpiness: penalty for uneven surface
        """
        heights = [0] * self.board.width
        holes = 0
        
        for col in range(self.board.width):
            found_block = False
            for row in range(self.board.height):
                if self.board.grid[row][col] is not None:
                    if not found_block:
                        heights[col] = self.board.height - row
                        found_block = True
                elif found_block:
                    holes += 1

        aggregate_height = sum(heights)
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(self.board.width - 1))
        
        # Approximate complete lines (without modifying grid)
        complete_lines = sum(1 for row in self.board.grid if all(cell is not None for cell in row))

        return -0.51 * aggregate_height + 0.76 * complete_lines - 0.35 * holes - 0.18 * bumpiness

    def get_best_move(self, piece: Tetromino) -> Tuple[int, int]:
        """
        Finds the best rotation and x-position for the given piece.
        Returns: (best_rotation_count, best_x)
        """
        best_score = float('-inf')
        best_rotation = 0
        best_x = piece.x
        
        original_matrix = [row[:] for row in piece.matrix]
        original_x = piece.x
        original_y = piece.y

        for rotation in range(4):
            # Find leftmost and rightmost valid x for this rotation
            min_x = 0
            max_x = self.board.width - 1
            
            for x in range(-2, self.board.width + 2):
                piece.x = x
                piece.y = 0
                if self.board.is_valid_position(piece):
                    # Drop piece down
                    while self.board.is_valid_position(piece, offset_y=1):
                        piece.y += 1
                    
                    # Temporarily place and evaluate
                    self.board.place_piece_temp(piece)
                    score = self._evaluate_board()
                    self.board.remove_piece_temp(piece)

                    if score > best_score:
                        best_score = score
                        best_rotation = rotation
                        best_x = x

            piece.rotate()

        # Restore original state
        piece.matrix = original_matrix
        piece.x = original_x
        piece.y = original_y

        return best_rotation, best_x


class Renderer:
    """
    Handles all Pygame drawing operations.
    """
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font

    def draw_board(self, board: Board, offset_x: int, offset_y: int, title: str) -> None:
        """Draws the board grid, locked pieces, and border."""
        # Draw background and border
        rect = pygame.Rect(offset_x, offset_y, board.width * CELL_SIZE, board.height * CELL_SIZE)
        pygame.draw.rect(self.screen, COLOR_BOARD_BG, rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2)

        # Draw grid lines
        for i in range(board.width):
            pygame.draw.line(self.screen, COLOR_GRID, 
                             (offset_x + i * CELL_SIZE, offset_y), 
                             (offset_x + i * CELL_SIZE, offset_y + board.height * CELL_SIZE))
        for j in range(board.height):
            pygame.draw.line(self.screen, COLOR_GRID, 
                             (offset_x, offset_y + j * CELL_SIZE), 
                             (offset_x + board.width * CELL_SIZE, offset_y + j * CELL_SIZE))

        # Draw locked pieces
        for y in range(board.height):
            for x in range(board.width):
                color = board.grid[y][x]
                if color:
                    pygame.draw.rect(self.screen, color, 
                                     (offset_x + x * CELL_SIZE + 1, offset_y + y * CELL_SIZE + 1, 
                                      CELL_SIZE - 2, CELL_SIZE - 2))

        # Draw Title & Score
        title_surf = self.font.render(title, True, COLOR_TEXT)
        self.screen.blit(title_surf, (offset_x, offset_y - 40))
        score_surf = self.font.render(f"Score: {board.score}", True, COLOR_TEXT)
        self.screen.blit(score_surf, (offset_x, offset_y + board.height * CELL_SIZE + 10))
        
        if board.game_over:
            go_surf = self.font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(go_surf, (offset_x + 10, offset_y + board.height * CELL_SIZE // 2))

    def draw_piece(self, piece: Tetromino, offset_x: int, offset_y: int) -> None:
        """Draws the active falling piece."""
        for r_idx, row in enumerate(piece.matrix):
            for c_idx, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                     (offset_x + (piece.x + c_idx) * CELL_SIZE + 1, 
                                      offset_y + (piece.y + r_idx) * CELL_SIZE + 1, 
                                      CELL_SIZE - 2, CELL_SIZE - 2))


# ==========================================
# Main Game Loop function
# ==========================================

def get_random_piece() -> Tetromino:
    """Returns a new random Tetromino."""
    name = random.choice(list(SHAPES.keys()))
    return Tetromino(name, SHAPES[name], COLORS[name])

def main() -> None:
    pygame.init()
    screen_width = BOARD_WIDTH * CELL_SIZE * 2 + 150 # Space for two boards + padding
    screen_height = BOARD_HEIGHT * CELL_SIZE + 150
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris: Player vs AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Segoe UI', 24, bold=True)
    renderer = Renderer(screen, font)

    p1_board = Board()
    p2_board = Board() # AI Board
    ai = TetrisAI(p2_board)

    p1_piece = get_random_piece()
    p2_piece = get_random_piece()
    
    if not p1_board.is_valid_position(p1_piece): p1_board.game_over = True
    if not p2_board.is_valid_position(p2_piece): p2_board.game_over = True

    fall_time = 0.0
    fall_speed = 500 # ms
    
    # AI variables
    ai_target_rotation = 0
    ai_target_x = 0
    ai_moves_calculated = False
    ai_move_timer = 0.0
    ai_move_speed = 100 # ms per AI action

    running = True
    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        ai_move_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and not p1_board.game_over:
                if event.key == pygame.K_LEFT:
                    if p1_board.is_valid_position(p1_piece, offset_x=-1):
                        p1_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if p1_board.is_valid_position(p1_piece, offset_x=1):
                        p1_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if p1_board.is_valid_position(p1_piece, offset_y=1):
                        p1_piece.y += 1
                elif event.key == pygame.K_UP:
                    p1_piece.rotate()
                    if not p1_board.is_valid_position(p1_piece):
                        # Simple wall kick attempt
                        if p1_board.is_valid_position(p1_piece, offset_x=-1):
                            p1_piece.x -= 1
                        elif p1_board.is_valid_position(p1_piece, offset_x=1):
                            p1_piece.x += 1
                        else:
                            p1_piece.rotate_back()
                elif event.key == pygame.K_SPACE:
                    while p1_board.is_valid_position(p1_piece, offset_y=1):
                        p1_piece.y += 1
                    fall_time = fall_speed # force lock

        # AI Action
        if not p2_board.game_over:
            if not ai_moves_calculated:
                ai_target_rotation, ai_target_x = ai.get_best_move(p2_piece)
                ai_moves_calculated = True
            
            if ai_move_timer >= ai_move_speed:
                ai_move_timer = 0
                if ai_target_rotation > 0:
                    p2_piece.rotate()
                    if not p2_board.is_valid_position(p2_piece):
                        # Wall kick
                        if p2_board.is_valid_position(p2_piece, offset_x=-1): p2_piece.x -= 1
                        elif p2_board.is_valid_position(p2_piece, offset_x=1): p2_piece.x += 1
                        else: p2_piece.rotate_back()
                    else:
                        ai_target_rotation -= 1
                elif p2_piece.x > ai_target_x:
                    if p2_board.is_valid_position(p2_piece, offset_x=-1): p2_piece.x -= 1
                elif p2_piece.x < ai_target_x:
                    if p2_board.is_valid_position(p2_piece, offset_x=1): p2_piece.x += 1
                else:
                    # Drop
                    if p2_board.is_valid_position(p2_piece, offset_y=1):
                        p2_piece.y += 1
                    else:
                        # Lock AI piece
                        p2_board.lock_piece(p2_piece)
                        p2_board.clear_lines()
                        p2_piece = get_random_piece()
                        if not p2_board.is_valid_position(p2_piece):
                            p2_board.game_over = True
                        ai_moves_calculated = False

        # Gravity for Player 1
        if fall_time >= fall_speed:
            fall_time = 0
            if not p1_board.game_over:
                if p1_board.is_valid_position(p1_piece, offset_y=1):
                    p1_piece.y += 1
                else:
                    p1_board.lock_piece(p1_piece)
                    p1_board.clear_lines()
                    p1_piece = get_random_piece()
                    if not p1_board.is_valid_position(p1_piece):
                        p1_board.game_over = True

        # Rendering
        screen.fill(COLOR_BG)
        
        # Player 1 Render
        p1_offset_x = 50
        p1_offset_y = 50
        renderer.draw_board(p1_board, p1_offset_x, p1_offset_y, "Player 1")
        if not p1_board.game_over:
            renderer.draw_piece(p1_piece, p1_offset_x, p1_offset_y)

        # Player 2 (AI) Render
        p2_offset_x = p1_offset_x + BOARD_WIDTH * CELL_SIZE + 50
        p2_offset_y = 50
        renderer.draw_board(p2_board, p2_offset_x, p2_offset_y, "AI Opponent")
        if not p2_board.game_over:
            renderer.draw_piece(p2_piece, p2_offset_x, p2_offset_y)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
