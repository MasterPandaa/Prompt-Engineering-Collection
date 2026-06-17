import pygame
import sys
import copy
import random
from typing import List, Tuple, Optional, Dict, Any

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_WIDTH = BOARD_SIZE * SQUARE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * SQUARE_SIZE

# Piece Values
PAWN_VAL = 100
KNIGHT_VAL = 320
BISHOP_VAL = 330
ROOK_VAL = 500
QUEEN_VAL = 900
KING_VAL = 20000

# Colors
COLOR_WHITE = "white"
COLOR_BLACK = "black"

# UI Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)

class Piece:
    """Base class for all chess pieces."""
    def __init__(self, color: str, name: str, value: int):
        self.color = color
        self.name = name
        self.value = value
        self.has_moved = False

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        """Returns a list of valid target squares (row, col) for this piece."""
        raise NotImplementedError("This method must be overridden by subclasses")

    def __str__(self) -> str:
        return f"{self.color[0].upper()}{self.name[0].upper()}"


class Pawn(Piece):
    """Pawn piece class."""
    def __init__(self, color: str):
        super().__init__(color, "Pawn", PAWN_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        direction = -1 if self.color == COLOR_WHITE else 1
        
        # Forward move
        if 0 <= row + direction < BOARD_SIZE:
            if board.grid[row + direction][col] is None:
                moves.append((row + direction, col))
                # Double forward move
                if not self.has_moved and 0 <= row + 2 * direction < BOARD_SIZE:
                    if board.grid[row + 2 * direction][col] is None:
                        moves.append((row + 2 * direction, col))
        
        # Captures
        for d_col in [-1, 1]:
            if 0 <= row + direction < BOARD_SIZE and 0 <= col + d_col < BOARD_SIZE:
                target_piece = board.grid[row + direction][col + d_col]
                if target_piece is not None and target_piece.color != self.color:
                    moves.append((row + direction, col + d_col))
                # En passant
                if board.en_passant_target == (row + direction, col + d_col):
                    moves.append((row + direction, col + d_col))
                    
        return moves


class Knight(Piece):
    """Knight piece class."""
    def __init__(self, color: str):
        super().__init__(color, "Knight", KNIGHT_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = board.grid[r][c]
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))
        return moves


class Bishop(Piece):
    """Bishop piece class."""
    def __init__(self, color: str):
        super().__init__(color, "Bishop", BISHOP_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = board.grid[r][c]
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class Rook(Piece):
    """Rook piece class."""
    def __init__(self, color: str):
        super().__init__(color, "Rook", ROOK_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = board.grid[r][c]
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class Queen(Piece):
    """Queen piece class."""
    def __init__(self, color: str):
        super().__init__(color, "Queen", QUEEN_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = board.grid[r][c]
                if target_piece is None:
                    moves.append((r, c))
                elif target_piece.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class King(Piece):
    """King piece class."""
    def __init__(self, color: str):
        super().__init__(color, "King", KING_VAL)

    def get_valid_moves(self, board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        moves = []
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target_piece = board.grid[r][c]
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))
                    
        # Castling
        if not self.has_moved and not board.is_in_check(self.color):
            # Kingside
            if board.grid[row][col + 1] is None and board.grid[row][col + 2] is None:
                rook = board.grid[row][BOARD_SIZE - 1]
                if isinstance(rook, Rook) and not rook.has_moved:
                    # Check if squares are under attack
                    if not board.is_square_under_attack(row, col + 1, self.color) and \
                       not board.is_square_under_attack(row, col + 2, self.color):
                        moves.append((row, col + 2))
            # Queenside
            if board.grid[row][col - 1] is None and board.grid[row][col - 2] is None and board.grid[row][col - 3] is None:
                rook = board.grid[row][0]
                if isinstance(rook, Rook) and not rook.has_moved:
                    if not board.is_square_under_attack(row, col - 1, self.color) and \
                       not board.is_square_under_attack(row, col - 2, self.color):
                        moves.append((row, col - 2))
                        
        return moves


class Move:
    """Represents a single move on the board."""
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], piece_moved: Piece, piece_captured: Optional[Piece] = None, is_castling: bool = False, is_en_passant: bool = False, promotion_choice: Optional[str] = None):
        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.promotion_choice = promotion_choice

class Board:
    """Class representing the chess board."""
    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = COLOR_WHITE
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.half_move_clock = 0
        self.move_history: List[Move] = []
        self._setup_board()

    def _setup_board(self) -> None:
        """Initializes the board with pieces in their starting positions."""
        for col in range(BOARD_SIZE):
            self.grid[1][col] = Pawn(COLOR_BLACK)
            self.grid[6][col] = Pawn(COLOR_WHITE)

        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(placement):
            self.grid[0][col] = piece_class(COLOR_BLACK)
            self.grid[7][col] = piece_class(COLOR_WHITE)

    def is_square_under_attack(self, row: int, col: int, defending_color: str) -> bool:
        """Checks if a given square is attacked by any enemy piece."""
        enemy_color = COLOR_BLACK if defending_color == COLOR_WHITE else COLOR_WHITE
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece is not None and piece.color == enemy_color:
                    if isinstance(piece, King):
                        # Avoid infinite recursion when checking king moves
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return True
                    else:
                        moves = piece.get_valid_moves(self, r, c)
                        if (row, col) in moves:
                            return True
        return False

    def is_in_check(self, color: str) -> bool:
        """Checks if the king of the given color is in check."""
        king_pos = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
            
        return self.is_square_under_attack(king_pos[0], king_pos[1], color)

    def get_all_legal_moves(self, color: str) -> List[Move]:
        """Generates all legal moves for a given color."""
        legal_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece is not None and piece.color == color:
                    pseudo_legal_moves = piece.get_valid_moves(self, r, c)
                    for end_r, end_c in pseudo_legal_moves:
                        # Determine move details
                        piece_captured = self.grid[end_r][end_c]
                        is_en_passant = isinstance(piece, Pawn) and self.en_passant_target == (end_r, end_c)
                        is_castling = isinstance(piece, King) and abs(end_c - c) == 2
                        
                        promotion_choices = [None]
                        if isinstance(piece, Pawn) and (end_r == 0 or end_r == BOARD_SIZE - 1):
                            promotion_choices = ["Queen", "Rook", "Bishop", "Knight"]

                        for promo in promotion_choices:
                            move = Move((r, c), (end_r, end_c), piece, piece_captured, is_castling, is_en_passant, promo)
                            if self.is_legal_move(move):
                                legal_moves.append(move)
        return legal_moves

    def is_legal_move(self, move: Move) -> bool:
        """Simulates a move to check if it leaves the king in check."""
        # Simple simulation by making and unmaking the move
        self.make_move(move, is_simulation=True)
        in_check = self.is_in_check(move.piece_moved.color)
        self.undo_move(move)
        return not in_check

    def make_move(self, move: Move, is_simulation: bool = False) -> None:
        """Executes a move on the board."""
        start_r, start_c = move.start
        end_r, end_c = move.end
        piece = move.piece_moved

        self.grid[start_r][start_c] = None
        
        if move.is_en_passant:
            self.grid[start_r][end_c] = None
            
        self.grid[end_r][end_c] = piece

        if move.is_castling:
            if end_c > start_c: # Kingside
                rook = self.grid[start_r][BOARD_SIZE - 1]
                self.grid[start_r][end_c - 1] = rook
                self.grid[start_r][BOARD_SIZE - 1] = None
                if rook:
                    rook.has_moved = True
            else: # Queenside
                rook = self.grid[start_r][0]
                self.grid[start_r][end_c + 1] = rook
                self.grid[start_r][0] = None
                if rook:
                    rook.has_moved = True

        if move.promotion_choice:
            color = piece.color
            if move.promotion_choice == "Queen":
                self.grid[end_r][end_c] = Queen(color)
            elif move.promotion_choice == "Rook":
                self.grid[end_r][end_c] = Rook(color)
            elif move.promotion_choice == "Bishop":
                self.grid[end_r][end_c] = Bishop(color)
            elif move.promotion_choice == "Knight":
                self.grid[end_r][end_c] = Knight(color)

        if not is_simulation:
            piece.has_moved = True
            if isinstance(piece, Pawn) or move.piece_captured is not None:
                self.half_move_clock = 0
            else:
                self.half_move_clock += 1

            if isinstance(piece, Pawn) and abs(end_r - start_r) == 2:
                self.en_passant_target = (start_r + (end_r - start_r) // 2, start_c)
            else:
                self.en_passant_target = None
                
            self.turn = COLOR_BLACK if self.turn == COLOR_WHITE else COLOR_WHITE
            self.move_history.append(move)

    def undo_move(self, move: Move) -> None:
        """Reverts the board state (used primarily during simulation/AI)."""
        # A full undo logic is complex, for simplicity we rely on deepcopy in AI or simple reversal
        # This implementation is a minimal reversal for the is_legal_move check
        start_r, start_c = move.start
        end_r, end_c = move.end
        
        self.grid[start_r][start_c] = move.piece_moved
        self.grid[end_r][end_c] = move.piece_captured
        
        if move.is_en_passant:
            self.grid[start_r][end_c] = Pawn(COLOR_WHITE if move.piece_moved.color == COLOR_BLACK else COLOR_BLACK)
            self.grid[end_r][end_c] = None

        if move.is_castling:
            if end_c > start_c: # Kingside
                rook = self.grid[start_r][end_c - 1]
                self.grid[start_r][BOARD_SIZE - 1] = rook
                self.grid[start_r][end_c - 1] = None
            else: # Queenside
                rook = self.grid[start_r][end_c + 1]
                self.grid[start_r][0] = rook
                self.grid[start_r][end_c + 1] = None
                
        # We don't restore has_moved here precisely for simulation as it's assumed true if it already moved, 
        # but for true undo history we'd need more state saved.


class ChessAI:
    """Class handling the Minimax algorithm with Alpha-Beta Pruning for the AI opponent."""
    
    def __init__(self, color: str, depth: int = 3):
        self.color = color
        self.depth = depth

    def evaluate_board(self, board: Board) -> int:
        """Evaluates the board state. Positive score favors White, negative favors Black."""
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board.grid[r][c]
                if piece is not None:
                    val = piece.value
                    if piece.color == COLOR_WHITE:
                        score += val
                    else:
                        score -= val
        return score

    def order_moves(self, moves: List[Move]) -> List[Move]:
        """Orders moves to optimize Alpha-Beta pruning (captures first)."""
        def move_score(move: Move):
            score = 0
            if move.piece_captured:
                score += 10 * move.piece_captured.value - move.piece_moved.value
            if move.promotion_choice:
                score += 900
            return score
            
        return sorted(moves, key=move_score, reverse=True)

    def minimax(self, board: Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """Minimax algorithm with Alpha-Beta pruning."""
        if depth == 0:
            return self.evaluate_board(board)

        current_color = COLOR_WHITE if is_maximizing else COLOR_BLACK
        legal_moves = board.get_all_legal_moves(current_color)
        
        if not legal_moves:
            if board.is_in_check(current_color):
                return -99999 if is_maximizing else 99999
            return 0 # Stalemate
            
        legal_moves = self.order_moves(legal_moves)

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board_copy = copy.deepcopy(board)
                board_copy.make_move(move)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board_copy = copy.deepcopy(board)
                board_copy.make_move(move)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board: Board) -> Optional[Move]:
        """Finds the best move using Minimax."""
        best_move = None
        is_maximizing = self.color == COLOR_WHITE
        best_eval = float('-inf') if is_maximizing else float('inf')
        
        legal_moves = board.get_all_legal_moves(self.color)
        legal_moves = self.order_moves(legal_moves)
        
        alpha = float('-inf')
        beta = float('inf')
        
        for move in legal_moves:
            board_copy = copy.deepcopy(board)
            board_copy.make_move(move)
            eval = self.minimax(board_copy, self.depth - 1, alpha, beta, not is_maximizing)
            
            if is_maximizing:
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
            else:
                if eval < best_eval:
                    best_eval = eval
                    best_move = move
                beta = min(beta, eval)
                
        # Fallback if no best move found but legal moves exist
        if best_move is None and legal_moves:
            best_move = legal_moves[0]
            
        return best_move


class GameRenderer:
    """Handles Pygame rendering."""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        
    def draw_board(self):
        """Draws the checkerboard pattern."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
    def draw_highlights(self, valid_moves: List[Tuple[int, int]]):
        """Highlights valid moves."""
        for r, c in valid_moves:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(HIGHLIGHT_COLOR)
            self.screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            
    def draw_pieces(self, board: Board):
        """Draws the pieces textually (simple representation)."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board.grid[r][c]
                if piece:
                    text_color = (255, 255, 255) if piece.color == COLOR_WHITE else (0, 0, 0)
                    symbol = "P" if isinstance(piece, Pawn) else \
                             "N" if isinstance(piece, Knight) else \
                             "B" if isinstance(piece, Bishop) else \
                             "R" if isinstance(piece, Rook) else \
                             "Q" if isinstance(piece, Queen) else "K"
                    text = self.font.render(symbol, True, text_color)
                    text_rect = text.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, text_rect)

def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess AI")
    
    board = Board()
    renderer = GameRenderer(screen)
    ai = ChessAI(COLOR_BLACK, depth=3)
    
    selected_square = None
    valid_moves: List[Move] = []
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == COLOR_WHITE:
                col = event.pos[0] // SQUARE_SIZE
                row = event.pos[1] // SQUARE_SIZE
                
                # Valid coordinate check
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if selected_square:
                        # Attempt to move
                        move_made = False
                        for move in valid_moves:
                            if move.end == (row, col):
                                board.make_move(move)
                                selected_square = None
                                valid_moves = []
                                move_made = True
                                break
                        if not move_made:
                            piece = board.grid[row][col]
                            if piece and piece.color == COLOR_WHITE:
                                selected_square = (row, col)
                                valid_moves = [m for m in board.get_all_legal_moves(COLOR_WHITE) if m.start == (row, col)]
                            else:
                                selected_square = None
                                valid_moves = []
                    else:
                        piece = board.grid[row][col]
                        if piece and piece.color == COLOR_WHITE:
                            selected_square = (row, col)
                            valid_moves = [m for m in board.get_all_legal_moves(COLOR_WHITE) if m.start == (row, col)]

        # AI Turn
        if board.turn == COLOR_BLACK and running:
            pygame.display.flip() # Update screen before AI thinks
            best_move = ai.get_best_move(board)
            if best_move:
                board.make_move(best_move)
            else:
                print("Game Over")
                running = False

        # Rendering
        renderer.draw_board()
        if selected_square:
            renderer.draw_highlights([m.end for m in valid_moves])
        renderer.draw_pieces(board)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
