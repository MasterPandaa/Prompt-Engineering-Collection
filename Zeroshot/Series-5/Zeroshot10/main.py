import sys
import random
import pygame
from typing import List, Tuple, Optional, Dict

# =========================
# Configuration
# =========================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

# Colors
LIGHT = (238, 238, 210)  # light squares
DARK = (118, 150, 86)    # dark squares
SELECT_COLOR = (246, 246, 105)
MOVE_HIGHLIGHT = (186, 202, 68)
CHECK_HIGHLIGHT = (255, 80, 80)
TEXT_COLOR = (30, 30, 30)

WHITE = 'w'
BLACK = 'b'

# Piece types
PAWN = 'P'
ROOK = 'R'
KNIGHT = 'N'
BISHOP = 'B'
QUEEN = 'Q'
KING = 'K'

Piece = Tuple[str, str]  # (color, type)
Move = Tuple[Tuple[int, int], Tuple[int, int], Optional[str]]  # ((r1,c1),(r2,c2), promotion)

# Unicode mapping for pieces
UNICODE_PIECES: Dict[Piece, str] = {
    (WHITE, KING):   '♔',
    (WHITE, QUEEN):  '♕',
    (WHITE, ROOK):   '♖',
    (WHITE, BISHOP): '♗',
    (WHITE, KNIGHT): '♘',
    (WHITE, PAWN):   '♙',
    (BLACK, KING):   '♚',
    (BLACK, QUEEN):  '♛',
    (BLACK, ROOK):   '♜',
    (BLACK, BISHOP): '♝',
    (BLACK, KNIGHT): '♞',
    (BLACK, PAWN):   '♟',
}

# Fallback letters if font lacks glyphs
LETTER_PIECES: Dict[Piece, str] = {
    (WHITE, KING):   'K',
    (WHITE, QUEEN):  'Q',
    (WHITE, ROOK):   'R',
    (WHITE, BISHOP): 'B',
    (WHITE, KNIGHT): 'N',
    (WHITE, PAWN):   'P',
    (BLACK, KING):   'k',
    (BLACK, QUEEN):  'q',
    (BLACK, ROOK):   'r',
    (BLACK, BISHOP): 'b',
    (BLACK, KNIGHT): 'n',
    (BLACK, PAWN):   'p',
}

MATERIAL_VALUES = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9, KING: 0}


class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pygame Chess - Human (White) vs Random AI (Black)')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Try loading a font that supports chess unicode; fallback to default
        self.font = self._load_font()

        self.board: List[List[Optional[Piece]]] = self._create_start_position()
        self.turn: str = WHITE
        self.selected: Optional[Tuple[int, int]] = None
        self.legal_moves_from_selected: List[Move] = []
        self.game_over: bool = False
        self.status_message: str = ''
        self.ai_delay_ms = 400
        self._ai_move_due_at: Optional[int] = None

    def _load_font(self) -> pygame.font.Font:
        # Common fonts that include chess unicode on Windows/macOS/Linux
        preferred = ['Segoe UI Symbol', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans Symbols2', 'Noto Sans Symbols']
        for name in preferred:
            try:
                font = pygame.font.SysFont(name, SQ_SIZE - 10)
                # Test render a white king glyph; if width is reasonable, accept
                surf = font.render(UNICODE_PIECES[(WHITE, KING)], True, (0, 0, 0))
                if surf.get_width() > SQ_SIZE // 3:
                    return font
            except Exception:
                continue
        # Fallback to default font
        return pygame.font.SysFont(None, SQ_SIZE - 10)

    def _create_start_position(self) -> List[List[Optional[Piece]]]:
        board: List[List[Optional[Piece]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        # Place pawns
        for c in range(COLS):
            board[6][c] = (WHITE, PAWN)
            board[1][c] = (BLACK, PAWN)
        # Place back rank
        back = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for c, pt in enumerate(back):
            board[7][c] = (WHITE, pt)
            board[0][c] = (BLACK, pt)
        return board

    # =========================
    # Utility & Board Helpers
    # =========================
    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < ROWS and 0 <= c < COLS

    def clone_board(self) -> List[List[Optional[Piece]]]:
        return [row.copy() for row in self.board]

    def find_king(self, color: str, board: Optional[List[List[Optional[Piece]]]] = None) -> Tuple[int, int]:
        b = board if board is not None else self.board
        for r in range(ROWS):
            for c in range(COLS):
                p = b[r][c]
                if p is not None and p[0] == color and p[1] == KING:
                    return (r, c)
        return (-1, -1)

    # =========================
    # Move Generation (Pseudo-legal)
    # =========================
    def generate_pseudo_legal_moves(self, color: str, board: Optional[List[List[Optional[Piece]]]] = None) -> List[Move]:
        b = board if board is not None else self.board
        moves: List[Move] = []
        for r in range(ROWS):
            for c in range(COLS):
                p = b[r][c]
                if p is None or p[0] != color:
                    continue
                pt = p[1]
                if pt == PAWN:
                    moves.extend(self._pawn_moves(r, c, color, b))
                elif pt == KNIGHT:
                    moves.extend(self._knight_moves(r, c, color, b))
                elif pt == BISHOP:
                    moves.extend(self._sliding_moves(r, c, color, b, [(-1, -1), (-1, 1), (1, -1), (1, 1)]))
                elif pt == ROOK:
                    moves.extend(self._sliding_moves(r, c, color, b, [(-1, 0), (1, 0), (0, -1), (0, 1)]))
                elif pt == QUEEN:
                    moves.extend(self._sliding_moves(r, c, color, b, [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]))
                elif pt == KING:
                    moves.extend(self._king_moves(r, c, color, b))
        return moves

    def _pawn_moves(self, r: int, c: int, color: str, b: List[List[Optional[Piece]]]) -> List[Move]:
        moves: List[Move] = []
        dir = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        next_r = r + dir
        # Forward move
        if self.in_bounds(next_r, c) and b[next_r][c] is None:
            # Promotion
            if next_r == 0 or next_r == 7:
                moves.append(((r, c), (next_r, c), QUEEN))
            else:
                moves.append(((r, c), (next_r, c), None))
            # Double move from start
            if r == start_row:
                jump_r = r + 2 * dir
                if self.in_bounds(jump_r, c) and b[jump_r][c] is None:
                    moves.append(((r, c), (jump_r, c), None))
        # Captures
        for dc in (-1, 1):
            nc = c + dc
            if self.in_bounds(next_r, nc) and b[next_r][nc] is not None and b[next_r][nc][0] != color:
                if next_r == 0 or next_r == 7:
                    moves.append(((r, c), (next_r, nc), QUEEN))
                else:
                    moves.append(((r, c), (next_r, nc), None))
        # Note: En passant omitted for simplicity
        return moves

    def _knight_moves(self, r: int, c: int, color: str, b: List[List[Optional[Piece]]]) -> List[Move]:
        moves: List[Move] = []
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            if b[nr][nc] is None or b[nr][nc][0] != color:
                moves.append(((r, c), (nr, nc), None))
        return moves

    def _sliding_moves(self, r: int, c: int, color: str, b: List[List[Optional[Piece]]], directions: List[Tuple[int, int]]) -> List[Move]:
        moves: List[Move] = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                if b[nr][nc] is None:
                    moves.append(((r, c), (nr, nc), None))
                else:
                    if b[nr][nc][0] != color:
                        moves.append(((r, c), (nr, nc), None))
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, r: int, c: int, color: str, b: List[List[Optional[Piece]]]) -> List[Move]:
        moves: List[Move] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                if b[nr][nc] is None or b[nr][nc][0] != color:
                    moves.append(((r, c), (nr, nc), None))
        # Note: Castling omitted for simplicity
        return moves

    # =========================
    # Check / Legal Move Filtering
    # =========================
    def is_square_attacked(self, r: int, c: int, by_color: str, board: Optional[List[List[Optional[Piece]]]] = None) -> bool:
        b = board if board is not None else self.board
        opp = by_color
        me = WHITE if opp == BLACK else BLACK

        # 1) Pawn attacks
        pawn_dir = -1 if opp == WHITE else 1
        for dc in (-1, 1):
            pr, pc = r - pawn_dir, c + dc  # reverse from attackers' perspective
            if self.in_bounds(pr, pc):
                p = b[pr][pc]
                if p is not None and p[0] == opp and p[1] == PAWN:
                    return True

        # 2) Knight attacks
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                p = b[nr][nc]
                if p is not None and p[0] == opp and p[1] == KNIGHT:
                    return True

        # 3) King attacks (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc):
                    p = b[nr][nc]
                    if p is not None and p[0] == opp and p[1] == KING:
                        return True

        # 4) Sliding pieces: bishops/rooks/queens
        # Bishop/Queen diagonals
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                p = b[nr][nc]
                if p is not None:
                    if p[0] == opp and (p[1] == BISHOP or p[1] == QUEEN):
                        return True
                    break
                nr += dr
                nc += dc
        # Rook/Queen orthogonals
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                p = b[nr][nc]
                if p is not None:
                    if p[0] == opp and (p[1] == ROOK or p[1] == QUEEN):
                        return True
                    break
                nr += dr
                nc += dc

        return False

    def in_check(self, color: str, board: Optional[List[List[Optional[Piece]]]] = None) -> bool:
        b = board if board is not None else self.board
        kr, kc = self.find_king(color, b)
        if kr == -1:
            return False
        opp = WHITE if color == BLACK else BLACK
        return self.is_square_attacked(kr, kc, opp, b)

    def make_move_on_board(self, b: List[List[Optional[Piece]]], move: Move) -> List[List[Optional[Piece]]]:
        newb = [row.copy() for row in b]
        (r1, c1), (r2, c2), promo = move
        piece = newb[r1][c1]
        newb[r1][c1] = None
        if piece is None:
            return newb
        color, pt = piece
        # Promotion handling for pawns
        if promo is not None:
            newb[r2][c2] = (color, promo)
        else:
            newb[r2][c2] = (color, pt)
        return newb

    def generate_legal_moves(self, color: str) -> List[Move]:
        legal: List[Move] = []
        for move in self.generate_pseudo_legal_moves(color):
            newb = self.make_move_on_board(self.board, move)
            if not self.in_check(color, newb):
                legal.append(move)
        return legal

    # =========================
    # AI (Random Mover with capture preference)
    # =========================
    def ai_choose_move(self) -> Optional[Move]:
        moves = self.generate_legal_moves(BLACK)
        if not moves:
            return None
        # Prefer captures by estimated material gain; otherwise random
        scored: List[Tuple[int, Move]] = []
        for mv in moves:
            (r1, c1), (r2, c2), promo = mv
            target = self.board[r2][c2]
            gain = 0
            if target is not None:
                gain = MATERIAL_VALUES[target[1]]
            # Tiny random to diversify
            scored.append((gain, mv))
        # Choose best gain; if tie, random among them
        best_gain = max(s for s, _ in scored)
        best_moves = [mv for s, mv in scored if s == best_gain]
        return random.choice(best_moves)

    # =========================
    # Input Handling
    # =========================
    def handle_click(self, pos: Tuple[int, int]):
        if self.game_over or self.turn != WHITE:
            return
        x, y = pos
        c, r = x // SQ_SIZE, y // SQ_SIZE
        if not self.in_bounds(r, c):
            return
        clicked_piece = self.board[r][c]
        if self.selected is None:
            # Select a white piece
            if clicked_piece is not None and clicked_piece[0] == WHITE:
                self.selected = (r, c)
                self.legal_moves_from_selected = [m for m in self.generate_legal_moves(WHITE) if m[0] == (r, c)]
        else:
            # Attempt to move if clicked square is a legal target
            for mv in self.legal_moves_from_selected:
                (_, _), (tr, tc), _ = mv
                if tr == r and tc == c:
                    # Make the move
                    self.board = self.make_move_on_board(self.board, mv)
                    self.selected = None
                    self.legal_moves_from_selected = []
                    # Switch turn
                    self.turn = BLACK
                    # Check end state after player's move
                    self._update_status_after_move()
                    if not self.game_over:
                        # Schedule AI move after delay
                        self._ai_move_due_at = pygame.time.get_ticks() + self.ai_delay_ms
                    return
            # If not a legal move, either reselect or clear selection
            if clicked_piece is not None and clicked_piece[0] == WHITE:
                self.selected = (r, c)
                self.legal_moves_from_selected = [m for m in self.generate_legal_moves(WHITE) if m[0] == (r, c)]
            else:
                self.selected = None
                self.legal_moves_from_selected = []

    def _update_status_after_move(self):
        # Check opponent's state
        opp = WHITE if self.turn == BLACK else BLACK
        legal = self.generate_legal_moves(self.turn)
        if not legal:
            if self.in_check(self.turn):
                self.game_over = True
                self.status_message = 'Checkmate! {} wins.'.format('White' if opp == WHITE else 'Black')
            else:
                self.game_over = True
                self.status_message = 'Stalemate! Draw.'
        else:
            # Update check info
            if self.in_check(self.turn):
                self.status_message = '{} to move: Check!'.format('White' if self.turn == WHITE else 'Black')
            else:
                self.status_message = '{} to move.'.format('White' if self.turn == WHITE else 'Black')

    # =========================
    # Rendering
    # =========================
    def draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                pygame.draw.rect(self.screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        # Highlight selected square
        if self.selected is not None:
            r, c = self.selected
            pygame.draw.rect(self.screen, SELECT_COLOR, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        # Highlight legal moves from selected
        for mv in self.legal_moves_from_selected:
            (_, _), (tr, tc), _ = mv
            surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            surf.fill((*MOVE_HIGHLIGHT, 120))
            self.screen.blit(surf, (tc * SQ_SIZE, tr * SQ_SIZE))

        # Highlight king in check
        if self.in_check(self.turn):
            kr, kc = self.find_king(self.turn)
            surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            surf.fill((*CHECK_HIGHLIGHT, 120))
            self.screen.blit(surf, (kc * SQ_SIZE, kr * SQ_SIZE))

    def draw_pieces(self):
        use_unicode = True
        # quick heuristic: render a white king and check if width is non-trivial
        test = self.font.render(UNICODE_PIECES[(WHITE, KING)], True, (10, 10, 10))
        if test.get_width() <= SQ_SIZE // 3:
            use_unicode = False

        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p is None:
                    continue
                color, pt = p
                if use_unicode:
                    char = UNICODE_PIECES[p]
                else:
                    char = LETTER_PIECES[p]
                # Choose piece color for text: black pieces darker
                piece_color = (15, 15, 15) if color == BLACK else (240, 240, 240)
                text = self.font.render(char, True, piece_color)
                rect = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                # Add slight outline for contrast
                outline = self.font.render(char, True, (0, 0, 0))
                outline_rect = outline.get_rect(center=rect.center)
                self.screen.blit(outline, outline_rect.move(1, 1))
                self.screen.blit(text, rect)

    def draw_status(self):
        # Render a small status bar at top-left using a smaller font
        small_font = pygame.font.SysFont(self.font.get_name() if hasattr(self.font, 'get_name') else None, 20)
        msg = self.status_message if self.status_message else ('White to move.' if self.turn == WHITE else 'Black to move.')
        text = small_font.render(msg, True, TEXT_COLOR)
        self.screen.blit(text, (8, 8))

    # =========================
    # Main Loop
    # =========================
    def run(self):
        self._update_status_after_move()  # initialize status
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            # AI Move (Black)
            if not self.game_over and self.turn == BLACK:
                now = pygame.time.get_ticks()
                if self._ai_move_due_at is None:
                    self._ai_move_due_at = now + self.ai_delay_ms
                if now >= self._ai_move_due_at:
                    mv = self.ai_choose_move()
                    if mv is None:
                        # No legal moves: checkmate or stalemate
                        self._update_status_after_move()
                    else:
                        self.board = self.make_move_on_board(self.board, mv)
                        self.turn = WHITE
                        self._ai_move_due_at = None
                        self._update_status_after_move()

            # Draw
            self.draw_board()
            self.draw_pieces()
            self.draw_status()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = ChessGame()
    game.run()
