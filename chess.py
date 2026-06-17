import sys
import pygame
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

# Konstanta warna
WHITE_COLOR: Tuple[int, int, int] = (240, 217, 181)
BLACK_COLOR: Tuple[int, int, int] = (181, 136, 99)
HIGHLIGHT_COLOR: Tuple[int, int, int] = (170, 162, 58)

BOARD_SIZE: int = 8
SQUARE_SIZE: int = 80
WINDOW_SIZE: int = BOARD_SIZE * SQUARE_SIZE

# Konstanta nilai bidak
PIECE_VALUES: Dict[str, int] = {
    'pawn': 10, 'knight': 30, 'bishop': 30,
    'rook': 50, 'queen': 90, 'king': 900
}

# Representasi teks untuk bidak
PIECE_TEXT: Dict[str, Dict[str, str]] = {
    'white': {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
    'black': {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
}

class Move:
    """Representasi pergerakan bidak catur."""
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 piece_moved: 'Piece', piece_captured: Optional['Piece'] = None, 
                 is_en_passant: bool = False, is_castling: bool = False, 
                 promotion_choice: str = ''):
        self.start_row, self.start_col = start_pos
        self.end_row, self.end_col = end_pos
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.is_en_passant = is_en_passant
        self.is_castling = is_castling
        self.promotion_choice = promotion_choice

class GameStateRecord:
    """Menyimpan status sebelum langkah dibuat agar bisa di-undo dengan aman."""
    def __init__(self, en_passant_sq: Optional[Tuple[int, int]], 
                 castling_rights: Dict[str, bool]):
        self.en_passant_sq = en_passant_sq
        self.castling_rights = castling_rights.copy()

class Piece(ABC):
    """Kelas dasar abstrak untuk semua bidak catur."""
    def __init__(self, color: str, row: int, col: int) -> None:
        if color not in ('white', 'black'):
            raise ValueError(f"Warna tidak valid: {color}")
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Koordinat di luar papan: ({row}, {col})")
        self.color = color
        self.row = row
        self.col = col

    @property
    def value(self) -> int:
        """Nilai material bidak untuk evaluasi AI."""
        return PIECE_VALUES[self.__class__.__name__.lower()]

    @abstractmethod
    def get_moves(self, board: 'Board') -> List[Move]:
        """Kembalikan daftar langkah pseudo-legal."""
        pass

class Pawn(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1
        
        # Maju 1 langkah
        next_row = self.row + direction
        if 0 <= next_row < BOARD_SIZE:
            if board.grid[next_row][self.col] is None:
                if next_row == 0 or next_row == 7:
                    for choice in ['queen', 'rook', 'bishop', 'knight']:
                        moves.append(Move((self.row, self.col), (next_row, self.col), self, promotion_choice=choice))
                else:
                    moves.append(Move((self.row, self.col), (next_row, self.col), self))
                
                # Maju 2 langkah
                if self.row == start_row and board.grid[next_row + direction][self.col] is None:
                    moves.append(Move((self.row, self.col), (next_row + direction, self.col), self))
                    
        # Makan menyilang
        for dc in [-1, 1]:
            if 0 <= self.col + dc < BOARD_SIZE and 0 <= next_row < BOARD_SIZE:
                target = board.grid[next_row][self.col + dc]
                if target is not None and target.color != self.color:
                    if next_row == 0 or next_row == 7:
                        for choice in ['queen', 'rook', 'bishop', 'knight']:
                            moves.append(Move((self.row, self.col), (next_row, self.col + dc), self, piece_captured=target, promotion_choice=choice))
                    else:
                        moves.append(Move((self.row, self.col), (next_row, self.col + dc), self, piece_captured=target))
                elif board.en_passant_sq == (next_row, self.col + dc):
                    en_passant_target = board.grid[self.row][self.col + dc]
                    moves.append(Move((self.row, self.col), (next_row, self.col + dc), self, piece_captured=en_passant_target, is_en_passant=True))
        return moves

class Knight(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.grid[r][c]
                if target is None or target.color != self.color:
                    moves.append(Move((self.row, self.col), (r, c), self, piece_captured=target))
        return moves

class Bishop(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, piece_captured=target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Rook(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, piece_captured=target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Queen(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = self.row + dr * i, self.col + dc * i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = board.grid[r][c]
                    if target is None:
                        moves.append(Move((self.row, self.col), (r, c), self))
                    elif target.color != self.color:
                        moves.append(Move((self.row, self.col), (r, c), self, piece_captured=target))
                        break
                    else:
                        break
                else:
                    break
        return moves

class King(Piece):
    def get_moves(self, board: 'Board') -> List[Move]:
        moves: List[Move] = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = board.grid[r][c]
                if target is None or target.color != self.color:
                    moves.append(Move((self.row, self.col), (r, c), self, piece_captured=target))
        
        # Castling
        if (self.color == 'white' and board.current_castling_rights['wKs']) or \
           (self.color == 'black' and board.current_castling_rights['bKs']):
            if board.grid[self.row][5] is None and board.grid[self.row][6] is None:
                if not board.is_under_attack(self.row, 4, self.color) and \
                   not board.is_under_attack(self.row, 5, self.color) and \
                   not board.is_under_attack(self.row, 6, self.color):
                    moves.append(Move((self.row, self.col), (self.row, 6), self, is_castling=True))
        
        if (self.color == 'white' and board.current_castling_rights['wQs']) or \
           (self.color == 'black' and board.current_castling_rights['bQs']):
            if board.grid[self.row][1] is None and board.grid[self.row][2] is None and board.grid[self.row][3] is None:
                if not board.is_under_attack(self.row, 4, self.color) and \
                   not board.is_under_attack(self.row, 3, self.color) and \
                   not board.is_under_attack(self.row, 2, self.color):
                    moves.append(Move((self.row, self.col), (self.row, 2), self, is_castling=True))
        return moves

class Board:
    """Mengelola status papan catur dan logikanya."""
    def __init__(self) -> None:
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.white_to_move: bool = True
        self.move_log: List[Move] = []
        self.state_log: List[GameStateRecord] = []
        self.en_passant_sq: Optional[Tuple[int, int]] = None
        self.white_king_pos: Tuple[int, int] = (7, 4)
        self.black_king_pos: Tuple[int, int] = (0, 4)
        self.current_castling_rights: Dict[str, bool] = {'wKs': True, 'wQs': True, 'bKs': True, 'bQs': True}
        self.setup_board()

    def setup_board(self) -> None:
        for c in range(BOARD_SIZE):
            self.grid[1][c] = Pawn('black', 1, c)
            self.grid[6][c] = Pawn('white', 6, c)
        
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, piece_class in enumerate(placement):
            self.grid[0][c] = piece_class('black', 0, c)
            self.grid[7][c] = piece_class('white', 7, c)

    def is_under_attack(self, row: int, col: int, color: str) -> bool:
        opponent_color = 'black' if color == 'white' else 'white'
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece is not None and piece.color == opponent_color:
                    if isinstance(piece, King):
                        if max(abs(piece.row - row), abs(piece.col - col)) <= 1:
                            return True
                    else:
                        for move in piece.get_moves(self):
                            if move.end_row == row and move.end_col == col:
                                return True
        return False

    def in_check(self) -> bool:
        if self.white_to_move:
            return self.is_under_attack(self.white_king_pos[0], self.white_king_pos[1], 'white')
        return self.is_under_attack(self.black_king_pos[0], self.black_king_pos[1], 'black')

    def update_castling_rights(self, move: Move) -> None:
        piece = move.piece_moved
        if isinstance(piece, King):
            if piece.color == 'white':
                self.current_castling_rights['wKs'] = False
                self.current_castling_rights['wQs'] = False
            else:
                self.current_castling_rights['bKs'] = False
                self.current_castling_rights['bQs'] = False
        elif isinstance(piece, Rook):
            if piece.row == 7:
                if piece.col == 0: self.current_castling_rights['wQs'] = False
                elif piece.col == 7: self.current_castling_rights['wKs'] = False
            elif piece.row == 0:
                if piece.col == 0: self.current_castling_rights['bQs'] = False
                elif piece.col == 7: self.current_castling_rights['bKs'] = False
        
        if move.piece_captured and isinstance(move.piece_captured, Rook):
            if move.piece_captured.row == 7:
                if move.piece_captured.col == 0: self.current_castling_rights['wQs'] = False
                elif move.piece_captured.col == 7: self.current_castling_rights['wKs'] = False
            elif move.piece_captured.row == 0:
                if move.piece_captured.col == 0: self.current_castling_rights['bQs'] = False
                elif move.piece_captured.col == 7: self.current_castling_rights['bKs'] = False

    def make_move(self, move: Move) -> None:
        self.state_log.append(GameStateRecord(self.en_passant_sq, self.current_castling_rights))
        
        self.grid[move.start_row][move.start_col] = None
        self.grid[move.end_row][move.end_col] = move.piece_moved
        move.piece_moved.row = move.end_row
        move.piece_moved.col = move.end_col

        if isinstance(move.piece_moved, King):
            if move.piece_moved.color == 'white':
                self.white_king_pos = (move.end_row, move.end_col)
            else:
                self.black_king_pos = (move.end_row, move.end_col)

        if move.promotion_choice != '':
            color = move.piece_moved.color
            if move.promotion_choice == 'queen': self.grid[move.end_row][move.end_col] = Queen(color, move.end_row, move.end_col)
            elif move.promotion_choice == 'rook': self.grid[move.end_row][move.end_col] = Rook(color, move.end_row, move.end_col)
            elif move.promotion_choice == 'bishop': self.grid[move.end_row][move.end_col] = Bishop(color, move.end_row, move.end_col)
            elif move.promotion_choice == 'knight': self.grid[move.end_row][move.end_col] = Knight(color, move.end_row, move.end_col)

        if move.is_en_passant:
            self.grid[move.start_row][move.end_col] = None

        if move.is_castling:
            if move.end_col - move.start_col == 2:
                rook = self.grid[move.end_row][7]
                if rook:
                    self.grid[move.end_row][5] = rook
                    rook.col = 5
                    self.grid[move.end_row][7] = None
            else:
                rook = self.grid[move.end_row][0]
                if rook:
                    self.grid[move.end_row][3] = rook
                    rook.col = 3
                    self.grid[move.end_row][0] = None

        self.update_castling_rights(move)

        if isinstance(move.piece_moved, Pawn) and abs(move.start_row - move.end_row) == 2:
            self.en_passant_sq = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_sq = None

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self) -> None:
        if not self.move_log: return
        move = self.move_log.pop()
        prev_state = self.state_log.pop()
        
        self.grid[move.start_row][move.start_col] = move.piece_moved
        move.piece_moved.row = move.start_row
        move.piece_moved.col = move.start_col
        self.grid[move.end_row][move.end_col] = move.piece_captured

        if isinstance(move.piece_moved, King):
            if move.piece_moved.color == 'white':
                self.white_king_pos = (move.start_row, move.start_col)
            else:
                self.black_king_pos = (move.start_row, move.start_col)

        if move.is_en_passant:
            self.grid[move.end_row][move.end_col] = None
            self.grid[move.start_row][move.end_col] = move.piece_captured

        if move.is_castling:
            if move.end_col - move.start_col == 2:
                rook = self.grid[move.end_row][5]
                if rook:
                    self.grid[move.end_row][7] = rook
                    rook.col = 7
                    self.grid[move.end_row][5] = None
            else:
                rook = self.grid[move.end_row][3]
                if rook:
                    self.grid[move.end_row][0] = rook
                    rook.col = 0
                    self.grid[move.end_row][3] = None

        self.en_passant_sq = prev_state.en_passant_sq
        self.current_castling_rights = prev_state.castling_rights
        self.white_to_move = not self.white_to_move

    def get_valid_moves(self) -> List[Move]:
        moves = []
        color = 'white' if self.white_to_move else 'black'
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece is not None and piece.color == color:
                    for move in piece.get_moves(self):
                        self.make_move(move)
                        self.white_to_move = not self.white_to_move
                        if not self.in_check():
                            moves.append(move)
                        self.white_to_move = not self.white_to_move
                        self.undo_move()
        return moves

    def evaluate(self) -> float:
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece:
                    if piece.color == 'white': score += piece.value
                    else: score -= piece.value
        return float(score)

    def is_game_over(self, valid_moves: List[Move]) -> bool:
        return len(valid_moves) == 0

    def get_ordered_moves(self, valid_moves: List[Move]) -> List[Move]:
        def move_score(move: Move) -> int:
            score = 0
            if move.piece_captured:
                score += 10 * move.piece_captured.value - move.piece_moved.value
            if move.promotion_choice:
                score += PIECE_VALUES.get(move.promotion_choice, 0)
            return score
        return sorted(valid_moves, key=move_score, reverse=True)


def minimax(board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    """Algoritma Minimax dengan Alpha-Beta Pruning untuk AI catur."""
    valid_moves = board.get_valid_moves()
    
    if depth == 0 or board.is_game_over(valid_moves):
        if board.is_game_over(valid_moves):
            if board.in_check(): return -9999.0 if maximizing else 9999.0
            return 0.0 # Stalemate
        return board.evaluate()

    ordered_moves = board.get_ordered_moves(valid_moves)

    if maximizing:
        max_eval = float('-inf')
        for move in ordered_moves:
            board.make_move(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.undo_move()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for move in ordered_moves:
            board.make_move(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha: break
        return min_eval

def find_best_move(board: Board) -> Optional[Move]:
    """Cari move terbaik untuk AI menggunakan Minimax."""
    valid_moves = board.get_valid_moves()
    if not valid_moves: return None
        
    ordered_moves = board.get_ordered_moves(valid_moves)
    best_move = None
    alpha = float('-inf')
    beta = float('inf')
    
    min_eval = float('inf')
    for move in ordered_moves:
        board.make_move(move)
        eval_score = minimax(board, 3, alpha, beta, True)
        board.undo_move()
        if eval_score < min_eval:
            min_eval = eval_score
            best_move = move
    
    return best_move

class GameRenderer:
    """Kelas untuk merender permainan catur menggunakan Pygame."""
    def __init__(self, board: Board):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess AI - SAST Compliant")
        pygame.font.init()
        
        # Coba gunakan font sistem yang mendukung unicode catur
        font_name = pygame.font.match_font('segoeuisymbol')
        if not font_name:
            font_name = pygame.font.match_font('arial')
        self.font = pygame.font.Font(font_name, int(SQUARE_SIZE * 0.7)) if font_name else pygame.font.SysFont(None, int(SQUARE_SIZE * 0.7))
        
        self.board = board
        self.selected_sq: Optional[Tuple[int, int]] = None
        self.player_clicks: List[Tuple[int, int]] = []
        self.valid_moves = self.board.get_valid_moves()

    def draw_board(self) -> None:
        colors = [WHITE_COLOR, BLACK_COLOR]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = colors[((r + c) % 2)]
                pygame.draw.rect(self.screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
        if self.selected_sq:
            r, c = self.selected_sq
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(HIGHLIGHT_COLOR)
            self.screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            
            for move in self.valid_moves:
                if move.start_row == r and move.start_col == c:
                    pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, 
                                     (move.end_col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                      move.end_row * SQUARE_SIZE + SQUARE_SIZE // 2), 10)

    def draw_pieces(self) -> None:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board.grid[r][c]
                if piece:
                    symbol = PIECE_TEXT[piece.color][piece.__class__.__name__.lower()]
                    text_color = (0, 0, 0) if piece.color == 'black' else (255, 255, 255)
                    text_surface = self.font.render(symbol, True, text_color)
                    text_rect = text_surface.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text_surface, text_rect)

    def draw(self) -> None:
        self.draw_board()
        self.draw_pieces()
        pygame.display.flip()

def main() -> None:
    board = Board()
    renderer = GameRenderer(board)
    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and board.white_to_move:
                location = pygame.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE

                if renderer.selected_sq == (row, col):
                    renderer.selected_sq = None
                    renderer.player_clicks = []
                else:
                    renderer.selected_sq = (row, col)
                    renderer.player_clicks.append((row, col))
                
                if len(renderer.player_clicks) == 2:
                    start = renderer.player_clicks[0]
                    end = renderer.player_clicks[1]
                    
                    move_attempt = None
                    for move in renderer.valid_moves:
                        if move.start_row == start[0] and move.start_col == start[1] and \
                           move.end_row == end[0] and move.end_col == end[1]:
                            move_attempt = move
                            break

                    if move_attempt:
                        # Auto promotion to queen for simplicity in UI
                        if move_attempt.promotion_choice == '' and isinstance(move_attempt.piece_moved, Pawn):
                            if move_attempt.end_row == 0 or move_attempt.end_row == 7:
                                move_attempt.promotion_choice = 'queen'
                        
                        board.make_move(move_attempt)
                        renderer.selected_sq = None
                        renderer.player_clicks = []
                        renderer.valid_moves = board.get_valid_moves()
                        if board.is_game_over(renderer.valid_moves):
                            game_over = True
                    else:
                        renderer.player_clicks = [renderer.selected_sq]

        if not board.white_to_move and not game_over:
            renderer.draw()
            best_move = find_best_move(board)
            if best_move:
                board.make_move(best_move)
                renderer.valid_moves = board.get_valid_moves()
                if board.is_game_over(renderer.valid_moves):
                    game_over = True

        renderer.draw()
        clock.tick(15)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
