"""
Chess Game with Minimax AI and Alpha-Beta Pruning.

This module implements a fully functional chess game using Pygame.
It adheres to the rules of chess, including castling, en passant,
and pawn promotion. The AI uses Minimax with Alpha-Beta Pruning
and a Transposition Table using Zobrist hashing.
"""

import pygame
import sys
import random
from typing import List, Tuple, Optional, Dict

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = BOARD_SIZE * SQUARE_SIZE
HEIGHT = BOARD_SIZE * SQUARE_SIZE
FPS = 30

# Colors
WHITE_COLOR = (240, 217, 181)
BLACK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)

# Piece Values
PAWN_VAL = 100
KNIGHT_VAL = 320
BISHOP_VAL = 330
ROOK_VAL = 500
QUEEN_VAL = 900
KING_VAL = 20000

WHITE = 1
BLACK = -1

class Move:
    """Represents a chess move."""
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], piece_moved: 'Piece', piece_captured: Optional['Piece'] = None, is_en_passant: bool = False, is_castle: bool = False, is_promotion: bool = False):
        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.is_en_passant = is_en_passant
        self.is_castle = is_castle
        self.is_promotion = is_promotion

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start == other.start and self.end == other.end
        return False

class Piece:
    """Base class for all chess pieces."""
    def __init__(self, color: int, row: int, col: int, value: int):
        self.color = color
        self.row = row
        self.col = col
        self.value = value
        self.has_moved = False

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        """Returns a list of valid moves for the piece (without checking for check)."""
        raise NotImplementedError

    def get_symbol(self) -> str:
        raise NotImplementedError

    def clone(self) -> 'Piece':
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, PAWN_VAL)

    def get_symbol(self) -> str:
        return 'P' if self.color == WHITE else 'p'

    def clone(self) -> 'Piece':
        p = Pawn(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        direction = -1 if self.color == WHITE else 1
        
        # Move forward 1
        r = self.row + direction
        if 0 <= r < BOARD_SIZE:
            if board.grid[r][self.col] is None:
                is_promo = (r == 0 or r == BOARD_SIZE - 1)
                moves.append(Move((self.row, self.col), (r, self.col), self, is_promotion=is_promo))
                
                # Move forward 2
                if not self.has_moved:
                    r2 = self.row + 2 * direction
                    if 0 <= r2 < BOARD_SIZE and board.grid[r2][self.col] is None:
                        moves.append(Move((self.row, self.col), (r2, self.col), self))
            
            # Captures
            for dc in [-1, 1]:
                c = self.col + dc
                if 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    is_promo = (r == 0 or r == BOARD_SIZE - 1)
                    if target is not None and target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, target, is_promotion=is_promo))
                    elif board.en_passant_target == (r, c):
                        ep_target = board.grid[self.row][c]
                        moves.append(Move((self.row, self.col), (r, c), self, ep_target, is_en_passant=True))
        return moves

class Knight(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, KNIGHT_VAL)

    def get_symbol(self) -> str:
        return 'N' if self.color == WHITE else 'n'

    def clone(self) -> 'Piece':
        p = Knight(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.grid[r][c]
                if target is None or target.color != self.color:
                    moves.append(Move((self.row, self.col), (r, c), self, target))
        return moves

class Bishop(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, BISHOP_VAL)

    def get_symbol(self) -> str:
        return 'B' if self.color == WHITE else 'b'

    def clone(self) -> 'Piece':
        p = Bishop(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Rook(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, ROOK_VAL)

    def get_symbol(self) -> str:
        return 'R' if self.color == WHITE else 'r'

    def clone(self) -> 'Piece':
        p = Rook(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Queen(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, QUEEN_VAL)

    def get_symbol(self) -> str:
        return 'Q' if self.color == WHITE else 'q'

    def clone(self) -> 'Piece':
        p = Queen(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class King(Piece):
    def __init__(self, color: int, row: int, col: int):
        super().__init__(color, row, col, KING_VAL)

    def get_symbol(self) -> str:
        return 'K' if self.color == WHITE else 'k'

    def clone(self) -> 'Piece':
        p = King(self.color, self.row, self.col)
        p.has_moved = self.has_moved
        return p

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.grid[r][c]
                if target is None or target.color != self.color:
                    moves.append(Move((self.row, self.col), (r, c), self, target))
        
        # Castling
        if not self.has_moved and not board.is_in_check(self.color):
            # Kingside
            if board.grid[self.row][5] is None and board.grid[self.row][6] is None:
                rook = board.grid[self.row][7]
                if isinstance(rook, Rook) and not rook.has_moved:
                    if not board.square_under_attack(self.row, 5, -self.color) and not board.square_under_attack(self.row, 6, -self.color):
                        moves.append(Move((self.row, self.col), (self.row, 6), self, is_castle=True))
            # Queenside
            if board.grid[self.row][1] is None and board.grid[self.row][2] is None and board.grid[self.row][3] is None:
                rook = board.grid[self.row][0]
                if isinstance(rook, Rook) and not rook.has_moved:
                    if not board.square_under_attack(self.row, 2, -self.color) and not board.square_under_attack(self.row, 3, -self.color):
                        moves.append(Move((self.row, self.col), (self.row, 2), self, is_castle=True))
        return moves

class Board:
    """Manages the chess board state."""
    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = WHITE
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.half_moves = 0
        self.move_log: List[Move] = []
        self.board_states: Dict[int, int] = {} # For 3-fold repetition
        self.zobrist_table = self._init_zobrist()
        self.zobrist_hash = 0
        self.setup_board()

    def _init_zobrist(self) -> Dict[str, int]:
        """Initializes Zobrist hashing table for Transposition Tables."""
        table = {}
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                for p in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
                    table[f"{r},{c},{p}"] = random.getrandbits(64)
        table['turn'] = random.getrandbits(64)
        return table

    def compute_hash(self) -> int:
        h = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece:
                    h ^= self.zobrist_table[f"{r},{c},{piece.get_symbol()}"]
        if self.turn == BLACK:
            h ^= self.zobrist_table['turn']
        return h

    def setup_board(self):
        """Sets up the initial board configuration."""
        for c in range(BOARD_SIZE):
            self.grid[1][c] = Pawn(BLACK, 1, c)
            self.grid[6][c] = Pawn(WHITE, 6, c)
        
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c in range(BOARD_SIZE):
            self.grid[0][c] = placement[c](BLACK, 0, c)
            self.grid[7][c] = placement[c](WHITE, 7, c)
            
        self.zobrist_hash = self.compute_hash()

    def make_move(self, move: Move):
        """Executes a move on the board."""
        sr, sc = move.start
        er, ec = move.end
        piece = self.grid[sr][sc]
        
        if piece is None:
            return

        self.grid[sr][sc] = None
        self.grid[er][ec] = piece
        piece.row = er
        piece.col = ec
        
        if move.is_en_passant:
            self.grid[sr][ec] = None
            
        if move.is_promotion:
            self.grid[er][ec] = Queen(piece.color, er, ec)
            
        if move.is_castle:
            if ec == 6: # Kingside
                rook = self.grid[sr][7]
                self.grid[sr][7] = None
                self.grid[sr][5] = rook
                rook.row, rook.col = sr, 5
                rook.has_moved = True
            elif ec == 2: # Queenside
                rook = self.grid[sr][0]
                self.grid[sr][0] = None
                self.grid[sr][3] = rook
                rook.row, rook.col = sr, 3
                rook.has_moved = True

        piece.has_moved = True
        
        # En passant target update
        if isinstance(piece, Pawn) and abs(sr - er) == 2:
            self.en_passant_target = ((sr + er) // 2, sc)
        else:
            self.en_passant_target = None

        if isinstance(piece, Pawn) or move.piece_captured is not None:
            self.half_moves = 0
        else:
            self.half_moves += 1

        self.turn = -self.turn
        self.move_log.append(move)
        self.zobrist_hash = self.compute_hash()

    def square_under_attack(self, r: int, c: int, attacker_color: int) -> bool:
        """Checks if a square is attacked by a specific color."""
        # Simple implementation: check if any attacker has a valid move to (r, c)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                p = self.grid[row][col]
                if p is not None and p.color == attacker_color:
                    if isinstance(p, King): # Prevent infinite recursion
                        if abs(p.row - r) <= 1 and abs(p.col - c) <= 1:
                            return True
                    else:
                        moves = p.get_valid_moves(self)
                        for m in moves:
                            if m.end == (r, c):
                                return True
        return False

    def is_in_check(self, color: int) -> bool:
        """Checks if the given color's king is in check."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if isinstance(p, King) and p.color == color:
                    return self.square_under_attack(r, c, -color)
        return False

    def get_all_valid_moves(self, color: int) -> List[Move]:
        """Gets all valid moves for a color, considering checks."""
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None and p.color == color:
                    pseudo_moves = p.get_valid_moves(self)
                    for pm in pseudo_moves:
                        if self.is_move_safe(pm):
                            moves.append(pm)
        return moves

    def is_move_safe(self, move: Move) -> bool:
        """Simulates a move to check if it leaves the king in check."""
        # Temporarily apply move
        sr, sc = move.start
        er, ec = move.end
        piece = self.grid[sr][sc]
        captured = self.grid[er][ec]
        
        # Handle en passant capture sim
        ep_captured = None
        if move.is_en_passant:
            ep_captured = self.grid[sr][ec]
            self.grid[sr][ec] = None
            
        self.grid[sr][sc] = None
        self.grid[er][ec] = piece
        piece.row, piece.col = er, ec
        
        is_safe = not self.is_in_check(piece.color)
        
        # Undo move
        self.grid[sr][sc] = piece
        self.grid[er][ec] = captured
        piece.row, piece.col = sr, sc
        if move.is_en_passant:
            self.grid[sr][ec] = ep_captured
            
        return is_safe

    def evaluate(self) -> int:
        """Evaluates the board state. Positive favors WHITE, negative favors BLACK."""
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None:
                    # Basic piece value
                    score += p.value * p.color
                    # Positional bonus (center control)
                    if isinstance(p, (Knight, Bishop, Pawn)):
                        dist_center = abs(3.5 - r) + abs(3.5 - c)
                        score += (10 - dist_center) * p.color * 2
        return score

    def is_game_over(self) -> Tuple[bool, str]:
        """Checks if the game is over and returns status."""
        valid_moves = self.get_all_valid_moves(self.turn)
        if len(valid_moves) == 0:
            if self.is_in_check(self.turn):
                winner = "White" if self.turn == BLACK else "Black"
                return True, f"Checkmate! {winner} wins."
            else:
                return True, "Stalemate! Draw."
        
        if self.half_moves >= 100:
            return True, "Draw by 50-move rule."
            
        return False, ""

    def clone(self) -> 'Board':
        """Creates a deep copy of the board for AI simulation."""
        new_board = Board()
        new_board.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.grid[r][c] is not None:
                    new_board.grid[r][c] = self.grid[r][c].clone()
        new_board.turn = self.turn
        new_board.en_passant_target = self.en_passant_target
        new_board.half_moves = self.half_moves
        return new_board

class ChessAI:
    """AI using Minimax with Alpha-Beta Pruning."""
    def __init__(self, depth: int):
        self.depth = depth
        self.transposition_table = {}

    def get_best_move(self, board: Board) -> Optional[Move]:
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        valid_moves = board.get_all_valid_moves(board.turn)
        if not valid_moves:
            return None
            
        # Move ordering: Captures first to improve pruning
        valid_moves.sort(key=lambda m: m.piece_captured is not None, reverse=True)

        if board.turn == WHITE:
            max_eval = float('-inf')
            for move in valid_moves:
                sim_board = board.clone()
                sim_board.make_move(move)
                eval = self.minimax(sim_board, self.depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        else:
            min_eval = float('inf')
            for move in valid_moves:
                sim_board = board.clone()
                sim_board.make_move(move)
                eval = self.minimax(sim_board, self.depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                    
        return best_move

    def minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        # Check Transposition Table
        board_hash = board.compute_hash()
        if board_hash in self.transposition_table:
            stored_depth, score = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return score

        is_over, _ = board.is_game_over()
        if depth == 0 or is_over:
            score = board.evaluate()
            self.transposition_table[board_hash] = (depth, score)
            return score

        valid_moves = board.get_all_valid_moves(board.turn)
        # Move ordering
        valid_moves.sort(key=lambda m: m.piece_captured is not None, reverse=True)

        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                sim_board = board.clone()
                sim_board.make_move(move)
                eval = self.minimax(sim_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table[board_hash] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                sim_board = board.clone()
                sim_board.make_move(move)
                eval = self.minimax(sim_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table[board_hash] = (depth, min_eval)
            return min_eval

class GameRenderer:
    """Handles Pygame rendering."""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        # Fallback dictionary for rendering pieces if images are missing
        self.piece_texts = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }

    def draw_board(self, board: Board, selected_square: Optional[Tuple[int, int]], valid_moves: List[Move]):
        """Draws the board, pieces, and highlights."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = WHITE_COLOR if (r + c) % 2 == 0 else BLACK_COLOR
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
                # Highlight selected
                if selected_square == (r, c):
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect)

                # Draw pieces
                piece = board.grid[r][c]
                if piece:
                    text = self.font.render(self.piece_texts[piece.get_symbol()], True, (0, 0, 0) if piece.color == BLACK else (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)

        # Highlight valid moves
        for move in valid_moves:
            r, c = move.end
            center = (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.circle(self.screen, (100, 100, 100), center, 10)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI - Minimax Alpha-Beta")
    clock = pygame.time.Clock()
    
    board = Board()
    renderer = GameRenderer(screen)
    ai = ChessAI(depth=3)
    
    selected_square = None
    valid_moves = []
    
    running = True
    game_over = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if not game_over and board.turn == WHITE and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if selected_square:
                        # Try to make move
                        move_made = False
                        for move in valid_moves:
                            if move.end == (row, col):
                                board.make_move(move)
                                move_made = True
                                selected_square = None
                                valid_moves = []
                                break
                        if not move_made:
                            piece = board.grid[row][col]
                            if piece and piece.color == board.turn:
                                selected_square = (row, col)
                                valid_moves = [m for m in board.get_all_valid_moves(board.turn) if m.start == (row, col)]
                            else:
                                selected_square = None
                                valid_moves = []
                    else:
                        piece = board.grid[row][col]
                        if piece and piece.color == board.turn:
                            selected_square = (row, col)
                            valid_moves = [m for m in board.get_all_valid_moves(board.turn) if m.start == (row, col)]

        # AI Turn
        if not game_over and board.turn == BLACK:
            pygame.event.pump() # Keep UI responsive
            best_move = ai.get_best_move(board)
            if best_move:
                board.make_move(best_move)
                
        # Check game over
        is_over, msg = board.is_game_over()
        if is_over:
            game_over = True
            print(msg)

        renderer.draw_board(board, selected_square, valid_moves)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
