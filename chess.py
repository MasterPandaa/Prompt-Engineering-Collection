import sys
import copy
import pygame
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# --- Constants & Configuration ---

# Window configurations
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
FPS = 60

# Colors
COLOR_WHITE = 'white'
COLOR_BLACK = 'black'
UI_COLOR_LIGHT = (238, 238, 210)  # Light square color
UI_COLOR_DARK = (118, 150, 86)    # Dark square color
UI_COLOR_HIGHLIGHT = (186, 202, 68) # Highlight color for selected piece
UI_COLOR_MOVES = (214, 214, 180)    # Highlight for possible moves

# Piece values for evaluation
PIECE_VALUES = {
    'Pawn': 10,
    'Knight': 30,
    'Bishop': 30,
    'Rook': 50,
    'Queen': 90,
    'King': 9000
}

# Unicode representations for rendering
PIECE_UNICODE = {
    COLOR_WHITE: {
        'King': '\u2654', 'Queen': '\u2655', 'Rook': '\u2656',
        'Bishop': '\u2657', 'Knight': '\u2658', 'Pawn': '\u2659'
    },
    COLOR_BLACK: {
        'King': '\u265A', 'Queen': '\u265B', 'Rook': '\u265C',
        'Bishop': '\u265D', 'Knight': '\u265E', 'Pawn': '\u265F'
    }
}


# --- Move Data Class ---

class Move:
    """Represents a chess move.

    Attributes:
        start_pos (Tuple[int, int]): Starting coordinates (row, col).
        end_pos (Tuple[int, int]): Ending coordinates (row, col).
        moved_piece (Piece): The piece that is moving.
        captured_piece (Optional[Piece]): The piece captured, if any.
        is_castling (bool): Whether the move is a castling move.
        is_en_passant (bool): Whether the move is en passant.
        is_promotion (bool): Whether the move results in pawn promotion.
    """

    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                 moved_piece: 'Piece', captured_piece: Optional['Piece'] = None,
                 is_castling: bool = False, is_en_passant: bool = False,
                 is_promotion: bool = False) -> None:
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.moved_piece = moved_piece
        self.captured_piece = captured_piece
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.is_promotion = is_promotion

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Move):
            return False
        return (self.start_pos == other.start_pos and
                self.end_pos == other.end_pos)


# --- Piece Classes ---

class Piece(ABC):
    """Abstract base class for all chess pieces.

    Attributes:
        color (str): Piece color ('white' or 'black').
        row (int): Row position (0-7).
        col (int): Column position (0-7).
        has_moved (bool): True if piece has moved (for castling/pawn first move).
    """

    def __init__(self, color: str, row: int, col: int) -> None:
        if color not in (COLOR_WHITE, COLOR_BLACK):
            raise ValueError(f"Invalid color: {color}")
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Coordinate out of bounds: ({row}, {col})")
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False

    @property
    def value(self) -> int:
        """Material value for AI evaluation."""
        return PIECE_VALUES[self.__class__.__name__]

    @property
    def symbol(self) -> str:
        """Returns the unicode symbol of the piece."""
        return PIECE_UNICODE[self.color][self.__class__.__name__]

    @abstractmethod
    def get_pseudo_legal_moves(self, board_state: List[List[Optional['Piece']]]) -> List[Move]:
        """Returns pseudo-legal moves without considering checks.

        Args:
            board_state: Current 8x8 matrix of the board.

        Returns:
            List of pseudo-legal Moves.
        """
        pass

    def clone(self) -> 'Piece':
        """Creates a copy of the piece."""
        new_piece = self.__class__(self.color, self.row, self.col)
        new_piece.has_moved = self.has_moved
        return new_piece


class Pawn(Piece):
    """Pawn piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        direction = -1 if self.color == COLOR_WHITE else 1
        start_row = 6 if self.color == COLOR_WHITE else 1

        # Move forward 1 step
        if 0 <= self.row + direction < BOARD_SIZE:
            if board_state[self.row + direction][self.col] is None:
                is_promo = (self.row + direction == 0) or (self.row + direction == 7)
                moves.append(Move((self.row, self.col), (self.row + direction, self.col), self, is_promotion=is_promo))

                # Move forward 2 steps from starting position
                if self.row == start_row and board_state[self.row + 2 * direction][self.col] is None:
                    moves.append(Move((self.row, self.col), (self.row + 2 * direction, self.col), self))

        # Captures
        for col_offset in [-1, 1]:
            new_col = self.col + col_offset
            if 0 <= self.row + direction < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target_piece = board_state[self.row + direction][new_col]
                if target_piece is not None and target_piece.color != self.color:
                    is_promo = (self.row + direction == 0) or (self.row + direction == 7)
                    moves.append(Move((self.row, self.col), (self.row + direction, new_col), self, target_piece, is_promotion=is_promo))

        return moves


class Knight(Piece):
    """Knight piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        jump_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for r_offset, c_offset in jump_offsets:
            new_row, new_col = self.row + r_offset, self.col + c_offset
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target_piece = board_state[new_row][new_col]
                if target_piece is None or target_piece.color != self.color:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self, target_piece))
        return moves


class Bishop(Piece):
    """Bishop piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d_row, d_col in directions:
            for step in range(1, BOARD_SIZE):
                new_row = self.row + d_row * step
                new_col = self.col + d_col * step
                if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                    break
                target_piece = board_state[new_row][new_col]
                if target_piece is None:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self))
                elif target_piece.color != self.color:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self, target_piece))
                    break
                else:
                    break
        return moves


class Rook(Piece):
    """Rook piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in directions:
            for step in range(1, BOARD_SIZE):
                new_row = self.row + d_row * step
                new_col = self.col + d_col * step
                if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                    break
                target_piece = board_state[new_row][new_col]
                if target_piece is None:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self))
                elif target_piece.color != self.color:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self, target_piece))
                    break
                else:
                    break
        return moves


class Queen(Piece):
    """Queen piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in directions:
            for step in range(1, BOARD_SIZE):
                new_row = self.row + d_row * step
                new_col = self.col + d_col * step
                if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                    break
                target_piece = board_state[new_row][new_col]
                if target_piece is None:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self))
                elif target_piece.color != self.color:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self, target_piece))
                    break
                else:
                    break
        return moves


class King(Piece):
    """King piece."""

    def get_pseudo_legal_moves(self, board_state: List[List[Optional[Piece]]]) -> List[Move]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in directions:
            new_row = self.row + d_row
            new_col = self.col + d_col
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target_piece = board_state[new_row][new_col]
                if target_piece is None or target_piece.color != self.color:
                    moves.append(Move((self.row, self.col), (new_row, new_col), self, target_piece))

        # Castling is handled in Board class to avoid complex dependencies here
        return moves


# --- Board Class ---

class Board:
    """Manages the chess board state and move logic."""

    def __init__(self) -> None:
        self.state: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = COLOR_WHITE
        self.move_log: List[Move] = []
        self.en_passant_target: Optional[Tuple[int, int]] = None  # Coordinate where en passant is possible
        self._setup_pieces()

    def _setup_pieces(self) -> None:
        """Initializes pieces on the board."""
        # Pawns
        for col in range(BOARD_SIZE):
            self.state[1][col] = Pawn(COLOR_BLACK, 1, col)
            self.state[6][col] = Pawn(COLOR_WHITE, 6, col)

        # Other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_cls in enumerate(piece_order):
            self.state[0][col] = piece_cls(COLOR_BLACK, 0, col)
            self.state[7][col] = piece_cls(COLOR_WHITE, 7, col)

    def is_in_check(self, color: str) -> bool:
        """Determines if the given color is currently in check."""
        king_pos = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if piece is not None and isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # Should not happen in normal play

        opponent_color = COLOR_BLACK if color == COLOR_WHITE else COLOR_WHITE
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_pseudo_legal_moves(self.state)
                    for move in moves:
                        if move.end_pos == king_pos:
                            return True
        return False

    def get_legal_moves(self, color: str) -> List[Move]:
        """Returns all legal moves for the given color."""
        legal_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if piece is not None and piece.color == color:
                    pseudo_moves = piece.get_pseudo_legal_moves(self.state)

                    # En Passant logic for pawns
                    if isinstance(piece, Pawn) and self.en_passant_target is not None:
                        ep_row, ep_col = self.en_passant_target
                        if abs(piece.col - ep_col) == 1 and piece.row + (-1 if color == COLOR_WHITE else 1) == ep_row:
                            target_piece = self.state[ep_row - (-1 if color == COLOR_WHITE else 1)][ep_col]
                            pseudo_moves.append(Move((piece.row, piece.col), (ep_row, ep_col), piece, target_piece, is_en_passant=True))

                    # Castling Logic for King
                    if isinstance(piece, King) and not piece.has_moved and not self.is_in_check(color):
                        # Kingside
                        rook = self.state[row][7]
                        if isinstance(rook, Rook) and not rook.has_moved:
                            if self.state[row][5] is None and self.state[row][6] is None:
                                if not self._is_square_attacked(row, 5, color) and not self._is_square_attacked(row, 6, color):
                                    pseudo_moves.append(Move((row, 4), (row, 6), piece, is_castling=True))
                        # Queenside
                        rook = self.state[row][0]
                        if isinstance(rook, Rook) and not rook.has_moved:
                            if self.state[row][1] is None and self.state[row][2] is None and self.state[row][3] is None:
                                if not self._is_square_attacked(row, 3, color) and not self._is_square_attacked(row, 2, color):
                                    pseudo_moves.append(Move((row, 4), (row, 2), piece, is_castling=True))

                    # Filter out moves that leave king in check
                    for move in pseudo_moves:
                        self.make_move(move, validate=False)
                        if not self.is_in_check(color):
                            legal_moves.append(move)
                        self.undo_move()

        return legal_moves

    def _is_square_attacked(self, row: int, col: int, ally_color: str) -> bool:
        """Checks if a specific square is under attack by the opponent."""
        opponent_color = COLOR_BLACK if ally_color == COLOR_WHITE else COLOR_WHITE
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.state[r][c]
                if piece is not None and piece.color == opponent_color:
                    # Minor optimization: check if knight/king can even reach before computing all
                    if isinstance(piece, (Knight, King)) and max(abs(piece.row - row), abs(piece.col - col)) > 2:
                        continue
                    moves = piece.get_pseudo_legal_moves(self.state)
                    for m in moves:
                        if m.end_pos == (row, col):
                            return True
        return False

    def make_move(self, move: Move, validate: bool = True) -> None:
        """Executes a move on the board."""
        start_row, start_col = move.start_pos
        end_row, end_col = move.end_pos
        piece = move.moved_piece

        # Update board array
        self.state[start_row][start_col] = None
        self.state[end_row][end_col] = piece
        piece.row = end_row
        piece.col = end_col

        # Handle En Passant Capture
        if move.is_en_passant:
            cap_row = start_row
            cap_col = end_col
            self.state[cap_row][cap_col] = None

        # Set En Passant Target for next turn
        if isinstance(piece, Pawn) and abs(start_row - end_row) == 2:
            self.en_passant_target = ((start_row + end_row) // 2, start_col)
        else:
            self.en_passant_target = None

        # Handle Castling
        if move.is_castling:
            if end_col == 6:  # Kingside
                rook = self.state[start_row][7]
                if rook:
                    self.state[start_row][7] = None
                    self.state[start_row][5] = rook
                    rook.row, rook.col = start_row, 5
            elif end_col == 2:  # Queenside
                rook = self.state[start_row][0]
                if rook:
                    self.state[start_row][0] = None
                    self.state[start_row][3] = rook
                    rook.row, rook.col = start_row, 3

        # Handle Promotion (Auto Queen for simplicity)
        if move.is_promotion:
            self.state[end_row][end_col] = Queen(piece.color, end_row, end_col)

        # Track state
        self.move_log.append(move)
        if validate:
            piece.has_moved = True
            self.turn = COLOR_BLACK if self.turn == COLOR_WHITE else COLOR_WHITE

    def undo_move(self) -> None:
        """Undoes the last move made."""
        if not self.move_log:
            return

        move = self.move_log.pop()
        start_row, start_col = move.start_pos
        end_row, end_col = move.end_pos
        piece = move.moved_piece

        # Restore piece position
        self.state[start_row][start_col] = piece
        piece.row = start_row
        piece.col = start_col

        # If it was promotion, we need to revert the queen back to pawn
        if move.is_promotion:
            self.state[start_row][start_col] = Pawn(piece.color, start_row, start_col)
            # Revert has_moved if it was from starting position (though rare to undo mid-game)
            self.state[start_row][start_col].has_moved = True

        # Restore captured piece
        if move.is_en_passant:
            self.state[end_row][end_col] = None
            cap_row = start_row
            cap_col = end_col
            self.state[cap_row][cap_col] = move.captured_piece
        else:
            self.state[end_row][end_col] = move.captured_piece

        # Revert Castling
        if move.is_castling:
            if end_col == 6:  # Kingside
                rook = self.state[start_row][5]
                if rook:
                    self.state[start_row][5] = None
                    self.state[start_row][7] = rook
                    rook.row, rook.col = start_row, 7
                    rook.has_moved = False
            elif end_col == 2:  # Queenside
                rook = self.state[start_row][3]
                if rook:
                    self.state[start_row][3] = None
                    self.state[start_row][0] = rook
                    rook.row, rook.col = start_row, 0
                    rook.has_moved = False
            piece.has_moved = False # Revert king moved flag

        # Note: In a full rigorous engine, we would store state histories (en passant targets, castling rights)
        # For simplicity, we assume undo is mainly used for AI exploration which perfectly unwinds.
        
        # Turn reversion
        self.turn = COLOR_BLACK if self.turn == COLOR_WHITE else COLOR_WHITE

    def evaluate(self) -> float:
        """Evaluates the current board state. Positive means White is winning."""
        score = 0.0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state[row][col]
                if piece is not None:
                    val = piece.value
                    if piece.color == COLOR_WHITE:
                        score += val
                    else:
                        score -= val
        return score

    def is_game_over(self) -> bool:
        """Checks if the game has ended."""
        if not self.get_legal_moves(self.turn):
            return True
        return False

    def get_ordered_moves(self, color: str) -> List[Move]:
        """Returns legal moves ordered to improve Alpha-Beta pruning efficiency."""
        moves = self.get_legal_moves(color)
        
        def move_score(move: Move) -> int:
            score = 0
            if move.captured_piece is not None:
                score += 10 * move.captured_piece.value - move.moved_piece.value
            if move.is_promotion:
                score += PIECE_VALUES['Queen']
            return score

        moves.sort(key=move_score, reverse=True)
        return moves


# --- AI Implementation ---

class ChessAI:
    """Provides AI capabilities using Minimax and Alpha-Beta Pruning."""

    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def get_best_move(self, board: Board) -> Optional[Move]:
        """Finds the best move for the current player."""
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        is_maximizing = (board.turn == COLOR_WHITE)
        
        moves = board.get_ordered_moves(board.turn)
        if not moves:
            return None

        if is_maximizing:
            max_eval = float('-inf')
            for move in moves:
                board.make_move(move)
                eval_score = self._minimax(board, self.depth - 1, alpha, beta, False)
                board.undo_move()
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
        else:
            min_eval = float('inf')
            for move in moves:
                board.make_move(move)
                eval_score = self._minimax(board, self.depth - 1, alpha, beta, True)
                board.undo_move()
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
        return best_move

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax algorithm with Alpha-Beta Pruning."""
        if depth == 0 or board.is_game_over():
            return board.evaluate()

        if maximizing:
            max_eval = float('-inf')
            for move in board.get_ordered_moves(COLOR_WHITE):
                board.make_move(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_ordered_moves(COLOR_BLACK):
                board.make_move(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval


# --- GUI GameManager ---

class GameManager:
    """Handles Pygame execution and user interaction."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Secure Chess AI")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.ai = ChessAI(depth=3)
        self.font = pygame.font.SysFont("segoeuiemoji", int(SQUARE_SIZE * 0.75)) # Font supporting Unicode chess
        if not self.font:
            self.font = pygame.font.Font(None, int(SQUARE_SIZE * 0.75)) # Fallback
            
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.valid_moves: List[Move] = []
        self.running = True

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self._handle_events()
            
            # AI Turn
            if self.board.turn == COLOR_BLACK and not self.board.is_game_over():
                self._draw() # Render before AI blocks thread
                pygame.display.flip()
                ai_move = self.ai.get_best_move(self.board)
                if ai_move:
                    self.board.make_move(ai_move)
                else:
                    print("Game Over! No valid moves for AI.")
            
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        """Process user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and self.board.turn == COLOR_WHITE:
                self._handle_mouse_click(pygame.mouse.get_pos())

    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """Processes logic for clicking a square."""
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE

        # If a piece is already selected, check if click is a valid move
        if self.selected_pos:
            move_executed = False
            for move in self.valid_moves:
                if move.end_pos == (row, col):
                    self.board.make_move(move)
                    self.selected_pos = None
                    self.valid_moves = []
                    move_executed = True
                    break
            if move_executed:
                return
            
            # If click was not a valid move, either deselect or select new piece
            self.selected_pos = None
            self.valid_moves = []

        # Select a piece
        piece = self.board.state[row][col]
        if piece is not None and piece.color == self.board.turn:
            self.selected_pos = (row, col)
            self.valid_moves = [m for m in self.board.get_legal_moves(self.board.turn) if m.start_pos == (row, col)]


    def _draw(self) -> None:
        """Renders the game state to the screen."""
        # Draw board squares
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = UI_COLOR_LIGHT if (row + col) % 2 == 0 else UI_COLOR_DARK
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

        # Draw highlight for selected piece
        if self.selected_pos:
            r, c = self.selected_pos
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, UI_COLOR_HIGHLIGHT, rect)

        # Draw highlights for valid moves
        for move in self.valid_moves:
            r, c = move.end_pos
            center = (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.circle(self.screen, UI_COLOR_MOVES, center, SQUARE_SIZE // 6)

        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.state[row][col]
                if piece is not None:
                    # Render Unicode text
                    text_surface = self.font.render(piece.symbol, True, (0, 0, 0) if piece.color == COLOR_BLACK else (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    
                    # For white pieces on light squares or black pieces on dark, outline helps.
                    # Pygame doesn't have native outline, so we can draw it multiple times with slight offset if needed.
                    # For simplicity, we just blit it.
                    self.screen.blit(text_surface, text_rect)
                    
        # Check for game over
        if self.board.is_game_over():
            if self.board.is_in_check(self.board.turn):
                winner = "Black" if self.board.turn == COLOR_WHITE else "White"
                msg = f"Checkmate! {winner} wins."
            else:
                msg = "Stalemate! Draw."
                
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            font_go = pygame.font.SysFont("arial", 48, bold=True)
            text_go = font_go.render(msg, True, (255, 255, 255))
            text_rect = text_go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(text_go, text_rect)


if __name__ == "__main__":
    game = GameManager()
    game.run()
