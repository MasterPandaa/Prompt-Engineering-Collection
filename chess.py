import pygame
import sys
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Konstanta warna
WHITE_COLOR = (240, 217, 181)
BLACK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (170, 210, 120)
TEXT_COLOR = (0, 0, 0)

# Konstanta permainan
BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE
FPS = 30
MAX_DEPTH = 3

PIECE_VALUES = {
    'pawn': 10, 'knight': 30, 'bishop': 30,
    'rook': 50, 'queen': 90, 'king': 10000
}

# Simbol Unicode Bidak Catur
UNICODE_PIECES = {
    'white': {
        'king': '\u2654', 'queen': '\u2655', 'rook': '\u2656',
        'bishop': '\u2657', 'knight': '\u2658', 'pawn': '\u2659'
    },
    'black': {
        'king': '\u265A', 'queen': '\u265B', 'rook': '\u265C',
        'bishop': '\u265D', 'knight': '\u265E', 'pawn': '\u265F'
    }
}


class Piece(ABC):
    """Kelas dasar abstrak untuk semua bidak catur."""
    def __init__(self, color: str, row: int, col: int) -> None:
        """Inisialisasi bidak dengan validasi koordinat."""
        if color not in ('white', 'black'):
            raise ValueError(f"Warna tidak valid: {color}")
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Koordinat di luar papan: ({row}, {col})")
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False

    @property
    def value(self) -> int:
        """Nilai material bidak untuk evaluasi AI."""
        return PIECE_VALUES[self.__class__.__name__.lower()]

    @abstractmethod
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        """Kembalikan daftar koordinat tujuan yang legal."""
        pass

    def get_symbol(self) -> str:
        """Mendapatkan simbol Unicode bidak."""
        return UNICODE_PIECES[self.color][self.__class__.__name__.lower()]


class Pawn(Piece):
    """Kelas untuk bidak Pawn/Pion."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Move forward 1
        r = self.row + direction
        if 0 <= r < BOARD_SIZE and board.get_piece(r, self.col) is None:
            moves.append((r, self.col))
            # Move forward 2
            if self.row == start_row:
                r2 = self.row + 2 * direction
                if board.get_piece(r2, self.col) is None:
                    moves.append((r2, self.col))

        # Captures
        for dc in [-1, 1]:
            c = self.col + dc
            if 0 <= c < BOARD_SIZE and 0 <= r < BOARD_SIZE:
                target = board.get_piece(r, c)
                if target is not None and target.color != self.color:
                    moves.append((r, c))
                # En Passant
                if (r, c) == board.en_passant_target:
                    moves.append((r, c))
        return moves

class Knight(Piece):
    """Kelas untuk bidak Knight/Kuda."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves

class Bishop(Piece):
    """Kelas untuk bidak Bishop/Gajah."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif target.color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Rook(Piece):
    """Kelas untuk bidak Rook/Benteng."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif target.color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Queen(Piece):
    """Kelas untuk bidak Queen/Menteri."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif target.color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves

class King(Piece):
    """Kelas untuk bidak King/Raja."""
    def get_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        
        # Castling
        if not self.has_moved and not board.is_in_check(self.color):
            # Kingside
            rook_ks = board.get_piece(self.row, 7)
            if isinstance(rook_ks, Rook) and not rook_ks.has_moved:
                if board.get_piece(self.row, 5) is None and board.get_piece(self.row, 6) is None:
                    if not board.is_square_attacked(self.row, 5, self.color) and not board.is_square_attacked(self.row, 6, self.color):
                        moves.append((self.row, 6))
            
            # Queenside
            rook_qs = board.get_piece(self.row, 0)
            if isinstance(rook_qs, Rook) and not rook_qs.has_moved:
                if board.get_piece(self.row, 1) is None and board.get_piece(self.row, 2) is None and board.get_piece(self.row, 3) is None:
                    if not board.is_square_attacked(self.row, 2, self.color) and not board.is_square_attacked(self.row, 3, self.color):
                        moves.append((self.row, 2))
        return moves


class Move:
    """Mewakili satu langkah pergerakan bidak catur."""
    def __init__(self, piece: Piece, end_row: int, end_col: int,
                 captured_piece: Optional[Piece] = None,
                 is_en_passant: bool = False,
                 is_castling: bool = False,
                 is_promotion: bool = False):
        """Inisialisasi record move untuk riwayat."""
        self.piece = piece
        self.start_row = piece.row
        self.start_col = piece.col
        self.end_row = end_row
        self.end_col = end_col
        self.captured_piece = captured_piece
        self.is_en_passant = is_en_passant
        self.is_castling = is_castling
        self.is_promotion = is_promotion
        self.piece_has_moved_before = piece.has_moved


class Board:
    """Manajemen state papan catur."""
    def __init__(self) -> None:
        """Inisialisasi state board."""
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.move_history: List[Move] = []
        self._setup_board()

    def _setup_board(self) -> None:
        """Menyusun posisi awal bidak."""
        for c in range(BOARD_SIZE):
            self.grid[1][c] = Pawn('black', 1, c)
            self.grid[6][c] = Pawn('white', 6, c)
        
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, piece_class in enumerate(placement):
            self.grid[0][c] = piece_class('black', 0, c)
            self.grid[7][c] = piece_class('white', 7, c)

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Mengambil bidak di koordinat tertentu."""
        return self.grid[row][col]

    def make_move(self, move: Move) -> None:
        """Menjalankan sebuah move dan memperbarui state papan."""
        self.grid[move.start_row][move.start_col] = None
        self.grid[move.end_row][move.end_col] = move.piece
        move.piece.row = move.end_row
        move.piece.col = move.end_col
        move.piece.has_moved = True

        if move.is_en_passant:
            self.grid[move.start_row][move.end_col] = None

        if move.is_castling:
            if move.end_col == 6: # Kingside
                rook = self.grid[move.start_row][7]
                if rook:
                    self.grid[move.start_row][7] = None
                    self.grid[move.start_row][5] = rook
                    rook.col = 5
                    rook.has_moved = True
            elif move.end_col == 2: # Queenside
                rook = self.grid[move.start_row][0]
                if rook:
                    self.grid[move.start_row][0] = None
                    self.grid[move.start_row][3] = rook
                    rook.col = 3
                    rook.has_moved = True

        if move.is_promotion:
            self.grid[move.end_row][move.end_col] = Queen(move.piece.color, move.end_row, move.end_col)

        if isinstance(move.piece, Pawn) and abs(move.start_row - move.end_row) == 2:
            self.en_passant_target = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_target = None

        self.move_history.append(move)

    def undo_move(self) -> None:
        """Membatalkan langkah terakhir pada papan."""
        if not self.move_history:
            return
        
        move = self.move_history.pop()
        
        self.grid[move.end_row][move.end_col] = move.captured_piece
        if move.captured_piece:
            move.captured_piece.row = move.end_row
            move.captured_piece.col = move.end_col

        self.grid[move.start_row][move.start_col] = move.piece
        move.piece.row = move.start_row
        move.piece.col = move.start_col
        move.piece.has_moved = move.piece_has_moved_before

        if move.is_promotion:
            self.grid[move.start_row][move.start_col] = move.piece
            
        if move.is_en_passant:
            self.grid[move.end_row][move.end_col] = None
            self.grid[move.start_row][move.end_col] = move.captured_piece
            if move.captured_piece:
                move.captured_piece.row = move.start_row
                move.captured_piece.col = move.end_col

        if move.is_castling:
            if move.end_col == 6: # Kingside
                rook = self.grid[move.start_row][5]
                if rook:
                    self.grid[move.start_row][5] = None
                    self.grid[move.start_row][7] = rook
                    rook.col = 7
                    rook.has_moved = False
            elif move.end_col == 2: # Queenside
                rook = self.grid[move.start_row][3]
                if rook:
                    self.grid[move.start_row][3] = None
                    self.grid[move.start_row][0] = rook
                    rook.col = 0
                    rook.has_moved = False

        if self.move_history:
            prev_move = self.move_history[-1]
            if isinstance(prev_move.piece, Pawn) and abs(prev_move.start_row - prev_move.end_row) == 2:
                self.en_passant_target = ((prev_move.start_row + prev_move.end_row) // 2, prev_move.end_col)
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None

    def generate_legal_moves(self, color: str) -> List[Move]:
        """Mendapatkan seluruh langkah valid untuk satu pemain."""
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    potential_ends = piece.get_moves(self)
                    for er, ec in potential_ends:
                        captured = self.grid[er][ec]
                        is_ep = False
                        if isinstance(piece, Pawn) and ec != c and captured is None:
                            is_ep = True
                            captured = self.grid[r][ec]
                        
                        is_castling = isinstance(piece, King) and abs(ec - c) == 2
                        is_promo = isinstance(piece, Pawn) and (er == 0 or er == 7)

                        move = Move(piece, er, ec, captured, is_ep, is_castling, is_promo)
                        
                        self.make_move(move)
                        if not self.is_in_check(color):
                            moves.append(move)
                        self.undo_move()
        return moves

    def is_square_attacked(self, row: int, col: int, defending_color: str) -> bool:
        """Memeriksa apakah satu kotak diserang pihak lawan."""
        attacker_color = 'black' if defending_color == 'white' else 'white'
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece and piece.color == attacker_color:
                    if isinstance(piece, King):
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return True
                    else:
                        ends = piece.get_moves(self)
                        if (row, col) in ends:
                            return True
        return False

    def is_in_check(self, color: str) -> bool:
        """Memeriksa apakah raja warna tertentu ter-check."""
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
        return self.is_square_attacked(king_pos[0], king_pos[1], color)

    def is_game_over(self, turn_color: str) -> bool:
        """Memeriksa apakah permainan telah berakhir."""
        return len(self.generate_legal_moves(turn_color)) == 0

    def evaluate(self) -> float:
        """Fungsi evaluasi material. Nilai positif baik untuk Putih."""
        score = 0.0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece:
                    val = piece.value
                    if piece.color == 'white':
                        score += val
                    else:
                        score -= val
        return score

    def get_ordered_moves(self, color: str) -> List[Move]:
        """Move ordering: memprioritaskan capture untuk pruning lebih baik."""
        moves = self.generate_legal_moves(color)
        
        def move_score(move: Move) -> int:
            score = 0
            if move.captured_piece:
                score += 10 * move.captured_piece.value - move.piece.value
            if move.is_promotion:
                score += 900
            return score
            
        moves.sort(key=move_score, reverse=True)
        return moves


class ChessAI:
    """Manajemen AI Catur."""
    @staticmethod
    def minimax(board: Board, depth: int, alpha: float, beta: float,
                maximizing: bool, turn_color: str) -> float:
        """Algoritma Minimax dengan Alpha-Beta Pruning untuk AI catur."""
        if depth == 0 or board.is_game_over(turn_color):
            return board.evaluate()

        if maximizing:
            max_eval = float('-inf')
            for move in board.get_ordered_moves('white'):
                board.make_move(move)
                eval_score = ChessAI.minimax(board, depth - 1, alpha, beta, False, 'black')
                board.undo_move()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_ordered_moves('black'):
                board.make_move(move)
                eval_score = ChessAI.minimax(board, depth - 1, alpha, beta, True, 'white')
                board.undo_move()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    @staticmethod
    def find_best_move(board: Board, color: str) -> Optional[Move]:
        """Mencari langkah terbaik dengan limit depth."""
        best_move = None
        maximizing = (color == 'white')
        
        best_val = float('-inf') if maximizing else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        ordered_moves = board.get_ordered_moves(color)
        if not ordered_moves:
            return None
            
        for move in ordered_moves:
            board.make_move(move)
            next_color = 'black' if color == 'white' else 'white'
            eval_score = ChessAI.minimax(board, MAX_DEPTH - 1, alpha, beta, not maximizing, next_color)
            board.undo_move()
            
            if maximizing:
                if eval_score > best_val:
                    best_val = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
            else:
                if eval_score < best_val:
                    best_val = eval_score
                    best_move = move
                beta = min(beta, eval_score)
        
        return best_move if best_move else ordered_moves[0]


class GameRenderer:
    """Manajemen render UI dan IO dengan Pygame."""
    def __init__(self) -> None:
        """Inisialisasi Pygame display."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Secure Chess AI')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoeuisymbol', int(SQUARE_SIZE * 0.8))
        if not pygame.font.match_font('segoeuisymbol'):
            self.font = pygame.font.SysFont('arial', int(SQUARE_SIZE * 0.8))

    def draw_board(self, board: Board, selected_sq: Optional[Tuple[int, int]], valid_moves: List[Tuple[int, int]]) -> None:
        """Merender papan, bidak, dan indikator."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = WHITE_COLOR if (r + c) % 2 == 0 else BLACK_COLOR
                pygame.draw.rect(self.screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                if selected_sq == (r, c):
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                if (r, c) in valid_moves:
                    pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2), 10)

                piece = board.get_piece(r, c)
                if piece:
                    text_surface = self.font.render(piece.get_symbol(), True, TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()

def main() -> None:
    """Entry point permainan."""
    renderer = GameRenderer()
    board = Board()
    
    turn = 'white'
    selected_sq = None
    valid_moves: List[Tuple[int, int]] = []
    legal_moves = board.generate_legal_moves(turn)
    
    running = True
    while running:
        human_turn = (turn == 'white')
        
        if not human_turn and running:
            best_move = ChessAI.find_best_move(board, 'black')
            if best_move:
                board.make_move(best_move)
                turn = 'white'
                legal_moves = board.generate_legal_moves(turn)
            else:
                running = False
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and human_turn:
                pos = pygame.mouse.get_pos()
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                
                if selected_sq:
                    move_made = False
                    for move in legal_moves:
                        if move.start_row == selected_sq[0] and move.start_col == selected_sq[1] and move.end_row == row and move.end_col == col:
                            board.make_move(move)
                            move_made = True
                            turn = 'black'
                            legal_moves = board.generate_legal_moves(turn)
                            break
                    if not move_made:
                        selected_sq = None
                        valid_moves = []
                    else:
                        selected_sq = None
                        valid_moves = []
                
                if not selected_sq:
                    piece = board.get_piece(row, col)
                    if piece and piece.color == turn:
                        selected_sq = (row, col)
                        valid_moves = [(m.end_row, m.end_col) for m in legal_moves if m.start_row == row and m.start_col == col]

        if len(legal_moves) == 0:
            if board.is_in_check(turn):
                print(f"Checkmate! {'Black' if turn == 'white' else 'White'} wins.")
            else:
                print("Stalemate! Draw.")
            running = False

        renderer.draw_board(board, selected_sq, valid_moves)
        renderer.clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
