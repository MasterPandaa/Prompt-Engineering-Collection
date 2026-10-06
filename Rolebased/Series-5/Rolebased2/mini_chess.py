import sys
import math
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# =========================
# Config & Constants
# =========================

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
TILE_SIZE = WIDTH // COLS

# Colors
LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
HIGHLIGHT_SQ = (246, 246, 105)
MOVE_DOT = (50, 50, 50)
MOVE_DOT_ALPHA = 170
SELECT_OUTLINE = (255, 215, 0)
SELECT_OUTLINE_WIDTH = 4

# Unicode symbols for chess pieces
UNICODE_PIECES = {
    ('w', 'K'): '♔',
    ('w', 'Q'): '♕',
    ('w', 'R'): '♖',
    ('w', 'B'): '♗',
    ('w', 'N'): '♘',
    ('w', 'P'): '♙',
    ('b', 'K'): '♚',
    ('b', 'Q'): '♛',
    ('b', 'R'): '♜',
    ('b', 'B'): '♝',
    ('b', 'N'): '♞',
    ('b', 'P'): '♟',
}

# Piece values for evaluation
PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0  # We don't evaluate king value in simple material (we avoid infinity)
}

# =========================
# Data Structures
# =========================

@dataclass
class Piece:
    color: str  # 'w' or 'b'
    kind: str   # 'K','Q','R','B','N','P'

    def symbol(self) -> str:
        return UNICODE_PIECES[(self.color, self.kind)]


@dataclass
class Move:
    start: Tuple[int, int]
    end: Tuple[int, int]
    promotion: Optional[str] = None  # 'Q','R','B','N' (we will use 'Q')


# =========================
# Board Representation
# =========================

class Board:
    def __init__(self):
        # board[r][c] with r=0 at top (Black side), r=7 at bottom (White side)
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.to_move: str = 'w'  # 'w' or 'b'
        self._setup_initial()

    def _setup_initial(self):
        # Black pieces
        self.board[0] = [
            Piece('b', 'R'), Piece('b', 'N'), Piece('b', 'B'), Piece('b', 'Q'),
            Piece('b', 'K'), Piece('b', 'B'), Piece('b', 'N'), Piece('b', 'R')
        ]
        self.board[1] = [Piece('b', 'P') for _ in range(COLS)]
        # Empty middle
        for r in range(2, 6):
            self.board[r] = [None for _ in range(COLS)]
        # White pieces
        self.board[6] = [Piece('w', 'P') for _ in range(COLS)]
        self.board[7] = [
            Piece('w', 'R'), Piece('w', 'N'), Piece('w', 'B'), Piece('w', 'Q'),
            Piece('w', 'K'), Piece('w', 'B'), Piece('w', 'N'), Piece('w', 'R')
        ]
        self.to_move = 'w'

    def clone(self) -> 'Board':
        new_b = Board.__new__(Board)
        new_b.board = [[None if p is None else Piece(p.color, p.kind) for p in row] for row in self.board]
        new_b.to_move = self.to_move
        return new_b

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < ROWS and 0 <= c < COLS

    def get(self, r: int, c: int) -> Optional[Piece]:
        if not self.in_bounds(r, c):
            return None
        return self.board[r][c]

    def set(self, r: int, c: int, piece: Optional[Piece]):
        self.board[r][c] = piece

    def move_piece(self, mv: Move):
        sr, sc = mv.start
        er, ec = mv.end
        piece = self.get(sr, sc)
        self.set(sr, sc, None)
        if mv.promotion and piece and piece.kind == 'P':
            self.set(er, ec, Piece(piece.color, mv.promotion))
        else:
            self.set(er, ec, piece)
        # Toggle side to move
        self.to_move = 'b' if self.to_move == 'w' else 'w'

    def all_pieces(self):
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p:
                    yield r, c, p

    def material(self) -> int:
        # Positive if white is better, negative if black better
        score = 0
        for _, _, p in self.all_pieces():
            val = PIECE_VALUES[p.kind]
            score += val if p.color == 'w' else -val
        return score


# =========================
# Rules Engine
# =========================

class Rules:
    @staticmethod
    def generate_moves(board: Board, color: str) -> List[Move]:
        moves: List[Move] = []
        for r, c, p in board.all_pieces():
            if p.color != color:
                continue
            moves.extend(Rules._piece_moves(board, r, c, p))
        return moves

    @staticmethod
    def _piece_moves(board: Board, r: int, c: int, p: Piece) -> List[Move]:
        if p.kind == 'P':
            return Rules._pawn_moves(board, r, c, p.color)
        elif p.kind == 'N':
            return Rules._knight_moves(board, r, c, p.color)
        elif p.kind == 'B':
            return Rules._slider_moves(board, r, c, p.color, directions=[(-1,-1),(-1,1),(1,-1),(1,1)])
        elif p.kind == 'R':
            return Rules._slider_moves(board, r, c, p.color, directions=[(-1,0),(1,0),(0,-1),(0,1)])
        elif p.kind == 'Q':
            return Rules._slider_moves(board, r, c, p.color, directions=[(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])
        elif p.kind == 'K':
            return Rules._king_moves(board, r, c, p.color)
        return []

    @staticmethod
    def _pawn_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
        moves = []
        dir_ = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        # Forward 1
        nr = r + dir_
        if board.in_bounds(nr, c) and board.get(nr, c) is None:
            moves.append(Rules._maybe_promote(Move((r, c), (nr, c)), color, nr))
            # Forward 2 from start
            nr2 = r + 2 * dir_
            if r == start_row and board.get(nr2, c) is None:
                moves.append(Move((r, c), (nr2, c)))
        # Captures
        for dc in (-1, 1):
            nc = c + dc
            nr = r + dir_
            if board.in_bounds(nr, nc):
                target = board.get(nr, nc)
                if target and target.color != color:
                    moves.append(Rules._maybe_promote(Move((r, c), (nr, nc)), color, nr))
        # No en passant implemented for simplicity
        return moves

    @staticmethod
    def _maybe_promote(mv: Move, color: str, dest_row: int) -> Move:
        if (color == 'w' and dest_row == 0) or (color == 'b' and dest_row == 7):
            mv.promotion = 'Q'
        return mv

    @staticmethod
    def _knight_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
        moves = []
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = r + dr, c + dc
            if not board.in_bounds(nr, nc):
                continue
            target = board.get(nr, nc)
            if target is None or target.color != color:
                moves.append(Move((r, c), (nr, nc)))
        return moves

    @staticmethod
    def _slider_moves(board: Board, r: int, c: int, color: str, directions: List[Tuple[int,int]]) -> List[Move]:
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.in_bounds(nr, nc):
                target = board.get(nr, nc)
                if target is None:
                    moves.append(Move((r, c), (nr, nc)))
                else:
                    if target.color != color:
                        moves.append(Move((r, c), (nr, nc)))
                    break
                nr += dr
                nc += dc
        return moves

    @staticmethod
    def _king_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not board.in_bounds(nr, nc):
                    continue
                target = board.get(nr, nc)
                if target is None or target.color == None or target.color != color:
                    moves.append(Move((r, c), (nr, nc)))
        # Castling omitted for simplicity
        return moves

    @staticmethod
    def is_square_attacked(board: Board, r: int, c: int, by_color: str) -> bool:
        # Generate pseudo-legal attacks by 'by_color' and see if any hit (r,c)
        for rr, cc, p in board.all_pieces():
            if p.color != by_color:
                continue
            if p.kind == 'P':
                dir_ = -1 if by_color == 'w' else 1
                for dc in (-1, 1):
                    nr, nc = rr + dir_, cc + dc
                    if nr == r and nc == c:
                        if board.in_bounds(nr, nc):
                            # Pawn attacks regardless of occupancy
                            return True
            elif p.kind == 'N':
                for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                    if rr + dr == r and cc + dc == c:
                        if board.in_bounds(r, c):
                            return True
            elif p.kind in ('B', 'R', 'Q'):
                directions = []
                if p.kind in ('B', 'Q'):
                    directions += [(-1,-1),(-1,1),(1,-1),(1,1)]
                if p.kind in ('R', 'Q'):
                    directions += [(-1,0),(1,0),(0,-1),(0,1)]
                for dr, dc in directions:
                    nr, nc = rr + dr, cc + dc
                    while board.in_bounds(nr, nc):
                        if nr == r and nc == c:
                            return True
                        if board.get(nr, nc) is not None:
                            break
                        nr += dr
                        nc += dc
            elif p.kind == 'K':
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        if rr + dr == r and cc + dc == c:
                            return True
        return False


# =========================
# Simple AI
# =========================

class SimpleAI:
    def __init__(self, color: str):
        self.color = color

    def choose_move(self, board: Board) -> Optional[Move]:
        moves = Rules.generate_moves(board, self.color)
        if not moves:
            return None

        # 1) Try free captures: capture where landing square after capture is not attacked by opponent
        best_free_capture = None
        best_capture_value = -math.inf
        for mv in moves:
            sr, sc = mv.start
            er, ec = mv.end
            target = board.get(er, ec)
            if target and target.color != self.color:
                # simulate move
                sim = board.clone()
                sim.move_piece(mv)
                # After move, our piece is now at (er,ec) in sim, and it's opponent to move
                # Check if our captured piece is safe (i.e., not attacked by opponent)
                if not Rules.is_square_attacked(sim, er, ec, by_color=('w' if self.color == 'b' else 'b')):
                    val = PIECE_VALUES[target.kind]
                    if val > best_capture_value:
                        best_capture_value = val
                        best_free_capture = mv
        if best_free_capture:
            return best_free_capture

        # 2) Otherwise, pick move that maximizes material evaluation after one ply
        best_eval = -math.inf if self.color == 'w' else math.inf
        best_move = None
        for mv in moves:
            sim = board.clone()
            sim.move_piece(mv)
            eval_score = sim.material()
            if self.color == 'w':
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = mv
            else:
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = mv

        # 3) Fallback
        return best_move or (moves[0] if moves else None)


# =========================
# Rendering & UI
# =========================

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = self._load_font()
        # Pre-render move dot
        self.move_dot = pygame.Surface((TILE_SIZE // 6, TILE_SIZE // 6), pygame.SRCALPHA)
        self.move_dot.fill((0, 0, 0, 0))
        pygame.draw.circle(self.move_dot, MOVE_DOT + (MOVE_DOT_ALPHA,), (self.move_dot.get_width()//2, self.move_dot.get_height()//2), self.move_dot.get_width()//2)

    def _load_font(self) -> pygame.font.Font:
        # Try fonts that typically contain chess unicode
        candidates = ['Segoe UI Symbol', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans Symbols2', 'Noto Sans Symbols']
        size = int(TILE_SIZE * 0.8)
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, size)
                # Test render a chess king
                test = f.render('♔', True, (0, 0, 0))
                if test.get_width() > 0:
                    return f
            except Exception:
                continue
        # Fallback default
        return pygame.font.SysFont(None, size)

    def draw_board(self, selected: Optional[Tuple[int,int]], moves: List[Move]):
        # Draw squares
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

        # Highlight selected
        if selected:
            sr, sc = selected
            rect = pygame.Rect(sc * TILE_SIZE, sr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, HIGHLIGHT_SQ, rect)

            # Outline
            pygame.draw.rect(self.screen, SELECT_OUTLINE, rect, SELECT_OUTLINE_WIDTH)

        # Draw move hints
        for mv in moves:
            er, ec = mv.end
            cx = ec * TILE_SIZE + TILE_SIZE // 2
            cy = er * TILE_SIZE + TILE_SIZE // 2
            dot_rect = self.move_dot.get_rect(center=(cx, cy))
            self.screen.blit(self.move_dot, dot_rect)

    def draw_pieces(self, board: Board):
        for r in range(ROWS):
            for c in range(COLS):
                p = board.get(r, c)
                if not p:
                    continue
                text = p.symbol()
                color = (20, 20, 20) if p.color == 'b' else (245, 245, 245)
                glyph = self.font.render(text, True, color)
                gx, gy = glyph.get_size()
                x = c * TILE_SIZE + (TILE_SIZE - gx) // 2
                y = r * TILE_SIZE + (TILE_SIZE - gy) // 2
                # Draw slight shadow for visibility on light squares
                self.screen.blit(self.font.render(text, True, (0, 0, 0)), (x+1, y+1))
                self.screen.blit(glyph, (x, y))


# =========================
# Game Controller
# =========================

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mini Chess Engine - Python/Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.renderer = Renderer(self.screen)

        # Human plays white, AI plays black
        self.human_color = 'w'
        self.ai = SimpleAI('b')

        self.selected: Optional[Tuple[int,int]] = None
        self.legal_moves_from_selected: List[Move] = []
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self._handle_events()

            # AI move if it's AI's turn
            if self.board.to_move == self.ai.color:
                pygame.time.delay(150)
                ai_move = self.ai.choose_move(self.board)
                if ai_move:
                    self.board.move_piece(ai_move)
                else:
                    # No legal moves -> halt or switch
                    pass
                self.selected = None
                self.legal_moves_from_selected = []

            self._draw()

        pygame.quit()
        sys.exit(0)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_click(self, pos: Tuple[int,int]):
        if self.board.to_move != self.human_color:
            return
        c = pos[0] // TILE_SIZE
        r = pos[1] // TILE_SIZE

        if self.selected is None:
            # Select a piece
            p = self.board.get(r, c)
            if p and p.color == self.human_color:
                self.selected = (r, c)
                self.legal_moves_from_selected = [mv for mv in Rules.generate_moves(self.board, self.human_color) if mv.start == (r, c)]
        else:
            # Attempt to move to clicked square if legal
            mv = None
            for m in self.legal_moves_from_selected:
                if m.end == (r, c):
                    mv = m
                    break

            if mv:
                self.board.move_piece(mv)
                self.selected = None
                self.legal_moves_from_selected = []
            else:
                # Re-select or clear selection
                p = self.board.get(r, c)
                if p and p.color == self.human_color:
                    self.selected = (r, c)
                    self.legal_moves_from_selected = [m for m in Rules.generate_moves(self.board, self.human_color) if m.start == (r, c)]
                else:
                    self.selected = None
                    self.legal_moves_from_selected = []

    def _draw(self):
        self.screen.fill((0, 0, 0))
        self.renderer.draw_board(self.selected, self.legal_moves_from_selected)
        self.renderer.draw_pieces(self.board)
        pygame.display.flip()


# =========================
# Main Entry
# =========================

if __name__ == "__main__":
    Game().run()
