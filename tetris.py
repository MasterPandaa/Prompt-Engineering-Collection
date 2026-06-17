import pygame
import sys
import random
import copy
from typing import List, Tuple, Dict, Optional

# Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Tetromino shapes defined as 2D lists
SHAPES: Dict[str, List[List[int]]] = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

SHAPE_COLORS: Dict[str, Tuple[int, int, int]] = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'T': (128, 0, 128),
    'Z': (255, 0, 0)
}


class Tetromino:
    """
    Represents a Tetris piece with its shape data, color, and current position.
    Handles basic rotation.
    """
    def __init__(self, shape_name: str) -> None:
        self.name: str = shape_name
        self.shape: List[List[int]] = copy.deepcopy(SHAPES[shape_name])
        self.color: Tuple[int, int, int] = SHAPE_COLORS[shape_name]
        self.x: int = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        self.y: int = 0

    def rotate(self) -> None:
        """
        Rotates the tetromino 90 degrees clockwise.
        """
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def rotate_back(self) -> None:
        """
        Rotates the tetromino 90 degrees counter-clockwise to undo a rotation.
        """
        self.shape = [list(row) for row in zip(*self.shape)][::-1]


class Board:
    """
    Manages the 10x20 grid, collision detection, piece placement, and line clearing.
    """
    def __init__(self) -> None:
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score: int = 0
        self.game_over: bool = False

    def is_valid_position(self, tetromino: Tetromino, offset_x: int = 0, offset_y: int = 0) -> bool:
        """
        Checks if the tetromino's current position (with optional offsets) is valid.
        Optimized by only checking relevant filled cells.
        """
        for r, row in enumerate(tetromino.shape):
            for c, val in enumerate(row):
                if val:
                    new_x = tetromino.x + c + offset_x
                    new_y = tetromino.y + r + offset_y
                    
                    if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                        return False
                    
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return False
        return True

    def place_tetromino(self, tetromino: Tetromino) -> None:
        """
        Places the tetromino onto the grid and checks for cleared lines.
        """
        for r, row in enumerate(tetromino.shape):
            for c, val in enumerate(row):
                if val:
                    y_pos = tetromino.y + r
                    x_pos = tetromino.x + c
                    if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                        self.grid[y_pos][x_pos] = tetromino.color
        self.clear_lines()

    def clear_lines(self) -> None:
        """
        Clears full lines and updates the score.
        """
        lines_cleared = 0
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = BOARD_HEIGHT - len(new_grid)
        
        # Add empty rows at the top
        for _ in range(lines_cleared):
            new_grid.insert(0, [None for _ in range(BOARD_WIDTH)])
            
        self.grid = new_grid
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800

    def spawn(self, tetromino: Tetromino) -> bool:
        """
        Spawns a new tetromino. Sets game_over if spawn position is invalid.
        """
        if not self.is_valid_position(tetromino):
            self.game_over = True
            return False
        return True


class TetrisAI:
    """
    AI opponent logic based on heuristic scoring.
    """
    def __init__(self) -> None:
        pass

    def evaluate_board(self, grid: List[List[Optional[Tuple[int, int, int]]]]) -> float:
        """
        Evaluates the board state using heuristics:
        - Aggregate height
        - Complete lines
        - Holes
        - Bumpiness
        """
        aggregate_height = 0
        holes = 0
        bumpiness = 0
        complete_lines = 0

        heights = [0] * BOARD_WIDTH
        for c in range(BOARD_WIDTH):
            for r in range(BOARD_HEIGHT):
                if grid[r][c] is not None:
                    heights[c] = BOARD_HEIGHT - r
                    break
            
            aggregate_height += heights[c]
            
            # Check for holes
            hole_found = False
            for r in range(BOARD_HEIGHT - heights[c], BOARD_HEIGHT):
                if grid[r][c] is None:
                    holes += 1

        for c in range(BOARD_WIDTH - 1):
            bumpiness += abs(heights[c] - heights[c + 1])

        for r in range(BOARD_HEIGHT):
            if all(cell is not None for cell in grid[r]):
                complete_lines += 1

        # Heuristic weights
        score = (-0.510066 * aggregate_height) + (0.760666 * complete_lines) + (-0.35663 * holes) + (-0.184483 * bumpiness)
        return score

    def get_best_move(self, board: Board, current_piece: Tetromino) -> Tuple[int, int]:
        """
        Determines the best rotation and x-position for the given piece.
        Returns (best_rotation, best_x).
        """
        best_score = float('-inf')
        best_x = 0
        best_rotation = 0

        # Create a temporary piece to simulate moves
        temp_piece = Tetromino(current_piece.name)

        for rotation in range(4):
            for x in range(-2, BOARD_WIDTH + 2):
                temp_piece.x = x
                temp_piece.y = 0

                if board.is_valid_position(temp_piece):
                    # Hard drop simulation
                    while board.is_valid_position(temp_piece, offset_y=1):
                        temp_piece.y += 1

                    # Temporarily place piece
                    temp_grid = [row[:] for row in board.grid] # Shallow copy of rows for performance
                    
                    # Place the piece on temp_grid
                    for r, row in enumerate(temp_piece.shape):
                        for c, val in enumerate(row):
                            if val:
                                py = temp_piece.y + r
                                px = temp_piece.x + c
                                if 0 <= py < BOARD_HEIGHT and 0 <= px < BOARD_WIDTH:
                                    temp_grid[py][px] = temp_piece.color
                                    
                    score = self.evaluate_board(temp_grid)
                    if score > best_score:
                        best_score = score
                        best_x = x
                        best_rotation = rotation

            temp_piece.rotate()

        return best_rotation, best_x


class Renderer:
    """
    Handles the rendering of the Pygame GUI.
    """
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        self.screen = screen
        self.font = font

    def draw_board(self, board: Board, offset_x: int, title: str) -> None:
        """
        Draws a single Tetris board.
        """
        # Draw Title
        title_surface = self.font.render(title, True, WHITE)
        self.screen.blit(title_surface, (offset_x, 10))

        # Draw Grid background
        pygame.draw.rect(self.screen, BLACK, (offset_x, 50, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE))

        # Draw Cells
        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                cell_color = board.grid[r][c]
                rect = (offset_x + c * CELL_SIZE, 50 + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell_color:
                    pygame.draw.rect(self.screen, cell_color, rect)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect, 1)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Draw Score
        score_surface = self.font.render(f"Score: {board.score}", True, WHITE)
        self.screen.blit(score_surface, (offset_x, 60 + BOARD_HEIGHT * CELL_SIZE))

        if board.game_over:
            over_surface = self.font.render("GAME OVER", True, RED)
            self.screen.blit(over_surface, (offset_x + 30, 50 + BOARD_HEIGHT * CELL_SIZE // 2))

    def draw_piece(self, piece: Tetromino, offset_x: int) -> None:
        """
        Draws the active Tetromino.
        """
        for r, row in enumerate(piece.shape):
            for c, val in enumerate(row):
                if val:
                    rect = (offset_x + (piece.x + c) * CELL_SIZE, 50 + (piece.y + r) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, piece.color, rect)
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect, 1)


def get_random_piece() -> Tetromino:
    """Returns a new random Tetromino."""
    return Tetromino(random.choice(list(SHAPES.keys())))


def main() -> None:
    """Main game loop and event handling."""
    pygame.init()
    screen_width = (BOARD_WIDTH * CELL_SIZE * 2) + 150
    screen_height = BOARD_HEIGHT * CELL_SIZE + 150
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris: Player vs AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    renderer = Renderer(screen, font)
    ai = TetrisAI()

    player_board = Board()
    ai_board = Board()

    player_piece = get_random_piece()
    ai_piece = get_random_piece()
    
    player_board.spawn(player_piece)
    ai_board.spawn(ai_piece)

    fall_time = 0.0
    fall_speed = 500  # ms per fall

    ai_move_timer = 0.0
    ai_move_delay = 200 # ms per AI action
    ai_target_rotation, ai_target_x = ai.get_best_move(ai_board, ai_piece)

    running = True
    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        ai_move_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not player_board.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if player_board.is_valid_position(player_piece, offset_x=-1):
                        player_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if player_board.is_valid_position(player_piece, offset_x=1):
                        player_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if player_board.is_valid_position(player_piece, offset_y=1):
                        player_piece.y += 1
                elif event.key == pygame.K_UP:
                    player_piece.rotate()
                    # Simple wall kick
                    if not player_board.is_valid_position(player_piece):
                        if player_board.is_valid_position(player_piece, offset_x=-1):
                            player_piece.x -= 1
                        elif player_board.is_valid_position(player_piece, offset_x=1):
                            player_piece.x += 1
                        else:
                            player_piece.rotate_back()
                elif event.key == pygame.K_SPACE:
                    while player_board.is_valid_position(player_piece, offset_y=1):
                        player_piece.y += 1
                    player_board.place_tetromino(player_piece)
                    player_piece = get_random_piece()
                    player_board.spawn(player_piece)

        # AI Logic
        if not ai_board.game_over and ai_move_timer >= ai_move_delay:
            ai_move_timer = 0
            
            # Apply rotation
            if ai_target_rotation > 0:
                ai_piece.rotate()
                ai_target_rotation -= 1
            # Apply movement
            elif ai_piece.x > ai_target_x:
                if ai_board.is_valid_position(ai_piece, offset_x=-1):
                    ai_piece.x -= 1
            elif ai_piece.x < ai_target_x:
                if ai_board.is_valid_position(ai_piece, offset_x=1):
                    ai_piece.x += 1
            # Fast drop once positioned
            elif ai_piece.x == ai_target_x and ai_target_rotation == 0:
                if ai_board.is_valid_position(ai_piece, offset_y=1):
                    ai_piece.y += 1
                else:
                    ai_board.place_tetromino(ai_piece)
                    ai_piece = get_random_piece()
                    if ai_board.spawn(ai_piece):
                        ai_target_rotation, ai_target_x = ai.get_best_move(ai_board, ai_piece)

        # Natural falling
        if fall_time >= fall_speed:
            fall_time = 0
            
            if not player_board.game_over:
                if player_board.is_valid_position(player_piece, offset_y=1):
                    player_piece.y += 1
                else:
                    player_board.place_tetromino(player_piece)
                    player_piece = get_random_piece()
                    player_board.spawn(player_piece)
                    
            if not ai_board.game_over:
                if ai_board.is_valid_position(ai_piece, offset_y=1):
                    ai_piece.y += 1
                else:
                    ai_board.place_tetromino(ai_piece)
                    ai_piece = get_random_piece()
                    if ai_board.spawn(ai_piece):
                        ai_target_rotation, ai_target_x = ai.get_best_move(ai_board, ai_piece)

        # Rendering
        screen.fill((30, 30, 30))
        
        renderer.draw_board(player_board, 50, "Player")
        if not player_board.game_over:
            renderer.draw_piece(player_piece, 50)
            
        renderer.draw_board(ai_board, BOARD_WIDTH * CELL_SIZE + 100, "AI Opponent")
        if not ai_board.game_over:
            renderer.draw_piece(ai_piece, BOARD_WIDTH * CELL_SIZE + 100)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
