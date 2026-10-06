"""
Tetris Game (Human vs AI) using Pygame.

This module provides a robust, two-player Tetris implementation adhering to strict SAST
standards. It separates responsibilities into classes: Tetromino, Board, TetrisAI, Renderer,
and GameManager. It avoids unsafe functions, uses type hints, follows PEP 8, and
implements efficient collision and AI evaluation logic.
"""

import pygame
import sys
import random
from typing import List, Tuple, Dict, Optional

# --- Constants ---
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
FPS = 60

# Colors (R, G, B)
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'GRAY': (50, 50, 50),
    'CYAN': (0, 255, 255),       # I
    'BLUE': (0, 0, 255),         # J
    'ORANGE': (255, 165, 0),     # L
    'YELLOW': (255, 255, 0),     # O
    'GREEN': (0, 255, 0),        # S
    'PURPLE': (128, 0, 128),     # T
    'RED': (255, 0, 0),          # Z
}

# Shapes definition
# Each shape is a list of coordinate offsets (x, y) relative to the pivot point (0,0)
SHAPES_DATA: Dict[str, Dict[str, List[Tuple[int, int]] | str]] = {
    'I': {
        'color': 'CYAN',
        'coords': [(-1, 0), (0, 0), (1, 0), (2, 0)]
    },
    'J': {
        'color': 'BLUE',
        'coords': [(-1, -1), (-1, 0), (0, 0), (1, 0)]
    },
    'L': {
        'color': 'ORANGE',
        'coords': [(1, -1), (-1, 0), (0, 0), (1, 0)]
    },
    'O': {
        'color': 'YELLOW',
        'coords': [(0, 0), (1, 0), (0, 1), (1, 1)]
    },
    'S': {
        'color': 'GREEN',
        'coords': [(0, 0), (1, 0), (-1, 1), (0, 1)]
    },
    'T': {
        'color': 'PURPLE',
        'coords': [(0, -1), (-1, 0), (0, 0), (1, 0)]
    },
    'Z': {
        'color': 'RED',
        'coords': [(-1, 0), (0, 0), (0, 1), (1, 1)]
    }
}

class Tetromino:
    """Represents a moving piece in the game."""
    def __init__(self, shape_name: str, x: int, y: int):
        """
        Initialize the Tetromino.
        
        Args:
            shape_name (str): The letter identifying the shape.
            x (int): Starting X grid position.
            y (int): Starting Y grid position.
        """
        self.shape_name = shape_name
        self.x = x
        self.y = y
        self.color = SHAPES_DATA[shape_name]['color']
        self.coords = list(SHAPES_DATA[shape_name]['coords']) # type: ignore

    def rotate(self) -> None:
        """
        Rotate the piece 90 degrees clockwise.
        The 'O' shape does not rotate.
        """
        if self.shape_name == 'O':
            return
        # Basic clockwise rotation matrix: (x, y) -> (-y, x)
        new_coords = [(-y, x) for (x, y) in self.coords]
        self.coords = new_coords

    def undo_rotate(self) -> None:
        """
        Undo rotation (counter-clockwise 90 degrees).
        Used when a rotation is invalid.
        """
        if self.shape_name == 'O':
            return
        # Counter-clockwise: (x, y) -> (y, -x)
        new_coords = [(y, -x) for (x, y) in self.coords]
        self.coords = new_coords

    def get_absolute_coords(self) -> List[Tuple[int, int]]:
        """
        Get the current grid coordinates of all blocks in the Tetromino.
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates.
        """
        return [(self.x + cx, self.y + cy) for (cx, cy) in self.coords]


class Board:
    """Manages the grid state, line clearing, and collision detection."""
    def __init__(self):
        """Initialize an empty board matrix."""
        # 0 means empty, otherwise it stores the color string
        self.grid: List[List[Optional[str]]] = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.game_over = False

    def is_valid_position(self, tetromino: Tetromino) -> bool:
        """
        Check if the tetromino's current position is within bounds and not overlapping.
        
        Args:
            tetromino (Tetromino): The piece to check.
            
        Returns:
            bool: True if position is valid, False otherwise.
        """
        for x, y in tetromino.get_absolute_coords():
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def place_tetromino(self, tetromino: Tetromino) -> None:
        """
        Lock the piece into the board grid.
        
        Args:
            tetromino (Tetromino): The piece to lock.
        """
        for x, y in tetromino.get_absolute_coords():
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                self.grid[y][x] = tetromino.color

    def clear_lines(self) -> int:
        """
        Find and clear complete lines, shifting rows down.
        
        Returns:
            int: Number of lines cleared.
        """
        lines_cleared = 0
        y = BOARD_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                lines_cleared += 1
                # Shift everything above this line down
                for row_y in range(y, 0, -1):
                    self.grid[row_y] = list(self.grid[row_y - 1])
                self.grid[0] = [None for _ in range(BOARD_WIDTH)]
            else:
                y -= 1
        
        # Basic scoring
        if lines_cleared > 0:
            self.score += [0, 40, 100, 300, 1200][lines_cleared]
        
        return lines_cleared


class TetrisAI:
    """AI opponent using heuristic evaluation."""
    def __init__(self, board: Board):
        """
        Initialize the AI with reference to its board.
        
        Args:
            board (Board): The AI's game board.
        """
        self.board = board

    def get_best_move(self, tetromino: Tetromino) -> Tuple[int, int]:
        """
        Evaluate all possible placements to find the best move.
        
        Args:
            tetromino (Tetromino): The piece to place.
            
        Returns:
            Tuple[int, int]: Optimal (target_x, rotations).
        """
        best_score = float('-inf')
        best_x = tetromino.x
        best_rotations = 0

        # Simulate rotations (0 to 3)
        for r in range(4):
            # Find bounds for x
            min_cx = min(cx for cx, cy in tetromino.coords)
            max_cx = max(cx for cx, cy in tetromino.coords)
            
            for test_x in range(-min_cx, BOARD_WIDTH - max_cx):
                # We do a lightweight drop simulation without a full deepcopy
                drop_y = tetromino.y
                # Temporary piece for testing
                test_piece = Tetromino(tetromino.shape_name, test_x, drop_y)
                test_piece.coords = list(tetromino.coords)
                
                # Drop it down
                while self.board.is_valid_position(test_piece):
                    test_piece.y += 1
                test_piece.y -= 1

                if test_piece.y >= 0:
                    score = self._evaluate_board_state(test_piece)
                    if score > best_score:
                        best_score = score
                        best_x = test_x
                        best_rotations = r
            
            tetromino.rotate()

        return best_x, best_rotations

    def _evaluate_board_state(self, piece: Tetromino) -> float:
        """
        Evaluate a potential board state based on heuristic weights.
        
        Args:
            piece (Tetromino): The piece placed in a hypothetical position.
            
        Returns:
            float: Evaluated score (higher is better).
        """
        # Create a lightweight height map array instead of deepcopying grid
        heights = [0] * BOARD_WIDTH
        holes = 0
        complete_lines = 0

        # Precompute current heights
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                if self.board.grid[y][x] is not None:
                    heights[x] = BOARD_HEIGHT - y
                    break
                    
        # Apply piece to heights and count virtual holes
        piece_coords = piece.get_absolute_coords()
        for x, y in piece_coords:
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                if BOARD_HEIGHT - y > heights[x]:
                    heights[x] = BOARD_HEIGHT - y

        aggregate_height = sum(heights)

        # Recalculate holes and bumpiness
        for x in range(BOARD_WIDTH):
            block_found = False
            for y in range(BOARD_HEIGHT):
                has_block = (self.board.grid[y][x] is not None) or ((x, y) in piece_coords)
                if has_block:
                    block_found = True
                elif block_found:
                    holes += 1

        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(BOARD_WIDTH - 1))

        # Check virtual complete lines (approximation)
        row_counts = [0] * BOARD_HEIGHT
        for y in range(BOARD_HEIGHT):
            row_counts[y] = sum(1 for x in range(BOARD_WIDTH) if self.board.grid[y][x] is not None)
        for x, y in piece_coords:
            if 0 <= y < BOARD_HEIGHT:
                row_counts[y] += 1
                
        complete_lines = sum(1 for count in row_counts if count == BOARD_WIDTH)

        # Weights: (aggregate height, complete lines, holes, bumpiness)
        score = (-0.510066 * aggregate_height) + (0.760666 * complete_lines) + (-0.35663 * holes) + (-0.184483 * bumpiness)
        return score


class Renderer:
    """Handles all Pygame drawing routines."""
    def __init__(self):
        """Initialize the Pygame window and assets."""
        pygame.init()
        self.screen_width = (BOARD_WIDTH * CELL_SIZE * 2) + 150 # Two boards + padding
        self.screen_height = BOARD_HEIGHT * CELL_SIZE + 80
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tetris: Human vs AI")
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)

    def draw_board(self, board: Board, offset_x: int, title: str) -> None:
        """
        Draw a single Tetris board.
        
        Args:
            board (Board): The board to draw.
            offset_x (int): X pixel offset for rendering.
            title (str): Title of the board.
        """
        # Draw background and border
        pygame.draw.rect(self.screen, COLORS['BLACK'], (offset_x, 60, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE))
        pygame.draw.rect(self.screen, COLORS['WHITE'], (offset_x, 60, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), 3)
        
        # Title and Score
        title_surf = self.font.render(title, True, COLORS['WHITE'])
        self.screen.blit(title_surf, (offset_x, 10))
        
        score_surf = self.small_font.render(f"Score: {board.score}", True, COLORS['WHITE'])
        self.screen.blit(score_surf, (offset_x, 35))

        # Draw grid blocks
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                color_name = board.grid[y][x]
                if color_name:
                    rect = (offset_x + x * CELL_SIZE, 60 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, COLORS[color_name], rect)
                    pygame.draw.rect(self.screen, COLORS['WHITE'], rect, 1) # Outline

    def draw_piece(self, piece: Tetromino, offset_x: int) -> None:
        """
        Draw an active Tetromino.
        
        Args:
            piece (Tetromino): The piece to draw.
            offset_x (int): X pixel offset for the board it belongs to.
        """
        for x, y in piece.get_absolute_coords():
            if y >= 0: # Only draw if visible
                rect = (offset_x + x * CELL_SIZE, 60 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, COLORS[piece.color], rect)
                pygame.draw.rect(self.screen, COLORS['WHITE'], rect, 1) # Outline

    def draw_game_over(self) -> None:
        """Render the game over message."""
        surf = self.font.render("GAME OVER - Press R to Restart", True, COLORS['WHITE'])
        rect = surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        # Background box
        bg_rect = rect.inflate(30, 20)
        pygame.draw.rect(self.screen, COLORS['BLACK'], bg_rect)
        pygame.draw.rect(self.screen, COLORS['WHITE'], bg_rect, 3)
        
        self.screen.blit(surf, rect)

    def update(self) -> None:
        """Flip the display buffer."""
        pygame.display.flip()


class GameManager:
    """Main loop controller uniting player input, AI logic, and rendering."""
    def __init__(self):
        """Initialize game states."""
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game boards and state."""
        self.human_board = Board()
        self.ai_board = Board()
        
        self.ai_logic = TetrisAI(self.ai_board)
        
        self.human_piece = self.spawn_piece()
        self.ai_piece = self.spawn_piece()
        
        self.fall_time = 0
        self.fall_speed = 500 # ms
        self.ai_fall_time = 0
        self.ai_target_x = 0
        self.ai_rotations_needed = 0
        self.ai_needs_plan = True

    def spawn_piece(self) -> Tetromino:
        """
        Spawn a random new Tetromino at the top.
        
        Returns:
            Tetromino: A newly instantiated piece.
        """
        shape_name = random.choice(list(SHAPES_DATA.keys()))
        return Tetromino(shape_name, BOARD_WIDTH // 2 - 1, 0)

    def handle_input(self) -> None:
        """Process keyboard inputs for the human player."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.human_board.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    continue

                if event.key == pygame.K_LEFT:
                    self.human_piece.x -= 1
                    if not self.human_board.is_valid_position(self.human_piece):
                        self.human_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    self.human_piece.x += 1
                    if not self.human_board.is_valid_position(self.human_piece):
                        self.human_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    self.human_piece.y += 1
                    if not self.human_board.is_valid_position(self.human_piece):
                        self.human_piece.y -= 1
                        self.lock_piece_human()
                elif event.key == pygame.K_UP:
                    self.human_piece.rotate()
                    if not self.human_board.is_valid_position(self.human_piece):
                        # Simple wall kick
                        self.human_piece.x -= 1
                        if not self.human_board.is_valid_position(self.human_piece):
                            self.human_piece.x += 2
                            if not self.human_board.is_valid_position(self.human_piece):
                                self.human_piece.x -= 1
                                self.human_piece.undo_rotate()
                elif event.key == pygame.K_SPACE:
                    while self.human_board.is_valid_position(self.human_piece):
                        self.human_piece.y += 1
                    self.human_piece.y -= 1
                    self.lock_piece_human()

    def lock_piece_human(self) -> None:
        """Lock human piece and spawn next."""
        self.human_board.place_tetromino(self.human_piece)
        self.human_board.clear_lines()
        self.human_piece = self.spawn_piece()
        if not self.human_board.is_valid_position(self.human_piece):
            self.human_board.game_over = True

    def lock_piece_ai(self) -> None:
        """Lock AI piece and spawn next."""
        self.ai_board.place_tetromino(self.ai_piece)
        self.ai_board.clear_lines()
        self.ai_piece = self.spawn_piece()
        self.ai_needs_plan = True
        if not self.ai_board.is_valid_position(self.ai_piece):
            self.ai_board.game_over = True

    def update_ai(self) -> None:
        """Process AI logic and actions."""
        if self.ai_board.game_over:
            return

        # 1. Plan if needed
        if self.ai_needs_plan:
            self.ai_target_x, self.ai_rotations_needed = self.ai_logic.get_best_move(self.ai_piece)
            self.ai_needs_plan = False

        # 2. Execute plan gradually
        if self.ai_rotations_needed > 0:
            self.ai_piece.rotate()
            self.ai_rotations_needed -= 1
            # Ensure valid rotation
            if not self.ai_board.is_valid_position(self.ai_piece):
                self.ai_piece.undo_rotate()
                self.ai_rotations_needed = 0
        elif self.ai_piece.x < self.ai_target_x:
            self.ai_piece.x += 1
            if not self.ai_board.is_valid_position(self.ai_piece):
                self.ai_piece.x -= 1
                self.ai_target_x = self.ai_piece.x # Give up on moving further
        elif self.ai_piece.x > self.ai_target_x:
            self.ai_piece.x -= 1
            if not self.ai_board.is_valid_position(self.ai_piece):
                self.ai_piece.x += 1
                self.ai_target_x = self.ai_piece.x
        else:
            # Drop fast when aligned
            self.ai_piece.y += 1
            if not self.ai_board.is_valid_position(self.ai_piece):
                self.ai_piece.y -= 1
                self.lock_piece_ai()

    def run(self) -> None:
        """Start the main game loop."""
        while True:
            dt = self.clock.tick(FPS)
            
            self.handle_input()
            
            # Gravity for human
            if not self.human_board.game_over:
                self.fall_time += dt
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    self.human_piece.y += 1
                    if not self.human_board.is_valid_position(self.human_piece):
                        self.human_piece.y -= 1
                        self.lock_piece_human()

            # Gravity and Logic for AI
            if not self.ai_board.game_over:
                self.ai_fall_time += dt
                if self.ai_fall_time >= self.fall_speed // 3: # AI moves faster
                    self.ai_fall_time = 0
                    self.update_ai()

            # Rendering
            self.renderer.screen.fill(COLORS['GRAY'])
            
            # Draw Human
            self.renderer.draw_board(self.human_board, 30, "Pemain Manusia")
            if not self.human_board.game_over:
                self.renderer.draw_piece(self.human_piece, 30)
                
            # Draw AI
            ai_offset = 30 + BOARD_WIDTH * CELL_SIZE + 60
            self.renderer.draw_board(self.ai_board, ai_offset, "Lawan AI")
            if not self.ai_board.game_over:
                self.renderer.draw_piece(self.ai_piece, ai_offset)

            if self.human_board.game_over or self.ai_board.game_over:
                self.renderer.draw_game_over()

            self.renderer.update()


if __name__ == "__main__":
    game = GameManager()
    game.run()
