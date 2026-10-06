import sys
import random
import pygame
from typing import List, Tuple, Optional, Dict

# ------------------------------
# Configuration
# ------------------------------
TILE_SIZE = 80
BOARD_SIZE = 8
BOARD_PIXELS = TILE_SIZE * BOARD_SIZE
INFO_BAR_HEIGHT = 80
WINDOW_WIDTH = BOARD_PIXELS
WINDOW_HEIGHT = BOARD_PIXELS + INFO_BAR_HEIGHT
FPS = 60

# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
LIGHT = (236, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
MOVE_HINT = (140, 162, 70)
CHECK_RED = (200, 60, 60)
TEXT_COLOR = (20, 20, 20)
TEXT_COLOR_INV = (240, 240, 240)

# Unicode chess symbols
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

# Types
Color = str  # 'w' or 'b'
PieceType = str  # 'K','Q','R','B','N','P'
Square = Tuple[int, int]  # (row, col)
Move = Tuple[Square, Square, Optional[PieceType]]  # from, to, promotion


class Piece:
    def __init__(self, color: Color, kind: PieceType):
        self.color = color
        self.kind = kind

    def __repr__(self):
        return f"{self.color}{self.kind}"


class Board:
    def __init__(self):
        # 8x8 board. (0,0) top-left, (7,7) bottom-right
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.turn: Color = 'w'
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.game_over: Optional[str] = None  # 'checkmate', 'stalemate'
        self.winner: Optional[Color] = None
        self.place_start_position()

    def clone(self) -> 'Board':
        b = Board.__new__(Board)
        b.grid = [[(None if p is None else Piece(p.color, p.kind)) for p in row] for row in self.grid]
        b.turn = self.turn
        b.halfmove_clock = self.halfmove_clock
        b.fullmove_number = self.fullmove_number
        b.game_over = self.game_over
        b.winner = self.winner
        return b

    def place_start_position(self):
        # Place pieces for standard chess starting position
        order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        # Black side (top)
        for c, kind in enumerate(order):
            self.grid[0][c] = Piece('b', kind)
            self.grid[1][c] = Piece('b', 'P')
        # White side (bottom)
        for c, kind in enumerate(order):
            self.grid[7][c] = Piece('w', kind)
            self.grid[6][c] = Piece('w', 'P')

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def king_position(self, color: Color) -> Optional[Square]:
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color and p.kind == 'K':
                    return (r, c)
        return None

    def is_square_attacked_by(self, sq: Square, attacker_color: Color) -> bool:
        # Generate all pseudo moves for attacker_color and see if any attack sq
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == attacker_color:
                    for _from, _to, _promo in self.generate_pseudo_moves_from((r, c), p):
                        if _to == sq:
                            return True
        return False

    def in_check(self, color: Color) -> bool:
        kpos = self.king_position(color)
        if not kpos:
            return False
        opp = 'b' if color == 'w' else 'w'
        return self.is_square_attacked_by(kpos, opp)

    def empty(self, r: int, c: int) -> bool:
        return self.grid[r][c] is None

    def occupied_by(self, r: int, c: int, color: Color) -> bool:
        p = self.grid[r][c]
        return p is not None and p.color == color

    def generate_pseudo_moves_from(self, sq: Square, p: Piece) -> List[Move]:
        r, c = sq
        moves: List[Move] = []
        if p.kind == 'P':
            dir = -1 if p.color == 'w' else 1
            start_row = 6 if p.color == 'w' else 1
            # Forward one
            nr = r + dir
            if self.in_bounds(nr, c) and self.empty(nr, c):
                # Promotion check
                if nr == 0 or nr == 7:
                    moves.append(((r, c), (nr, c), 'Q'))
                else:
                    moves.append(((r, c), (nr, c), None))
                # Forward two from start
                nr2 = r + 2 * dir
                if r == start_row and self.empty(nr2, c):
                    moves.append(((r, c), (nr2, c), None))
            # Captures
            for dc in (-1, 1):
                nr = r + dir
                nc = c + dc
                if self.in_bounds(nr, nc) and not self.empty(nr, nc):
                    if not self.occupied_by(nr, nc, p.color):
                        if nr == 0 or nr == 7:
                            moves.append(((r, c), (nr, nc), 'Q'))
                        else:
                            moves.append(((r, c), (nr, nc), None))
            # Note: en passant not implemented
        elif p.kind == 'N':
            for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                if self.occupied_by(nr, nc, p.color):
                    continue
                moves.append(((r, c), (nr, nc), None))
        elif p.kind in ('B', 'R', 'Q'):
            directions = []
            if p.kind in ('B', 'Q'):
                directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if p.kind in ('R', 'Q'):
                directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc):
                    if self.occupied_by(nr, nc, p.color):
                        break
                    moves.append(((r, c), (nr, nc), None))
                    if not self.empty(nr, nc):
                        break
                    nr += dr
                    nc += dc
        elif p.kind == 'K':
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if not self.in_bounds(nr, nc):
                        continue
                    if self.occupied_by(nr, nc, p.color):
                        continue
                    moves.append(((r, c), (nr, nc), None))
            # Note: castling not implemented
        return moves

    def generate_legal_moves(self, color: Color) -> List[Move]:
        legal: List[Move] = []
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color:
                    for mv in self.generate_pseudo_moves_from((r, c), p):
                        if self.is_legal_move(mv, color):
                            legal.append(mv)
        return legal

    def is_legal_move(self, mv: Move, color: Color) -> bool:
        (r1, c1), (r2, c2), promo = mv
        piece = self.grid[r1][c1]
        captured = self.grid[r2][c2]
        # Apply
        self.grid[r2][c2] = piece if promo is None else Piece(piece.color, promo)
        self.grid[r1][c1] = None
        king_in_check = self.in_check(color)
        # Undo
        self.grid[r1][c1] = piece
        self.grid[r2][c2] = captured
        return not king_in_check

    def make_move(self, mv: Move):
        (r1, c1), (r2, c2), promo = mv
        piece = self.grid[r1][c1]
        captured = self.grid[r2][c2]
        # Move
        if promo is None:
            self.grid[r2][c2] = piece
        else:
            self.grid[r2][c2] = Piece(piece.color, promo)
        self.grid[r1][c1] = None

        # Update turn
        self.turn = 'b' if self.turn == 'w' else 'w'
        if self.turn == 'w':
            self.fullmove_number += 1

        # Check end states
        self.update_game_state()

    def update_game_state(self):
        # Determine if current side to move has legal moves
        if self.game_over:
            return
        color = self.turn
        legal = self.generate_legal_moves(color)
        if len(legal) == 0:
            if self.in_check(color):
                self.game_over = 'checkmate'
                self.winner = 'b' if color == 'w' else 'w'
            else:
                self.game_over = 'stalemate'
                self.winner = None


class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Python Chess - Pygame (No images)")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        # Fonts: try fonts with chess glyphs; fallback to default
        piece_font_size = int(TILE_SIZE * 0.8)
        candidates = ["Segoe UI Symbol", "DejaVu Sans", "Arial Unicode MS", None]
        chosen = None
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, piece_font_size)
                # Simple sanity render to ensure creation; if fails, continue
                _ = f.render('♔', True, (255, 255, 255))
                chosen = f
                break
            except Exception:
                continue
        if chosen is None:
            chosen = pygame.font.SysFont(None, piece_font_size)
        self.font_pieces = chosen
        self.font_info = pygame.font.SysFont("Segoe UI", 28) or pygame.font.SysFont(None, 28)
        self.board = Board()
        self.selected: Optional[Square] = None
        self.legal_moves_from_selected: List[Square] = []
        self.running = True
        self.ai_enabled_for_black = True
        self.ai_delay_ms = 250
        self.pending_ai_time: Optional[int] = None

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit(0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.board.game_over:
                    # Click to reset game
                    self.reset_game()
                    continue
                # Only accept input if it's White's turn (human as white)
                if self.board.turn == 'w':
                    self.handle_click(event.pos)

    def handle_click(self, pos: Tuple[int, int]):
        x, y = pos
        if y >= BOARD_PIXELS:
            return
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if not self.board.in_bounds(r, c):
            return
        piece = self.board.grid[r][c]
        # Selection logic
        if self.selected is None:
            if piece and piece.color == self.board.turn:
                self.selected = (r, c)
                self.legal_moves_from_selected = [to for (_f, to, _p) in self.board.generate_legal_moves(self.board.turn) if _f == self.selected]
        else:
            # If clicking same color piece, change selection
            if piece and piece.color == self.board.turn:
                self.selected = (r, c)
                self.legal_moves_from_selected = [to for (_f, to, _p) in self.board.generate_legal_moves(self.board.turn) if _f == self.selected]
                return
            # Attempt move
            move_candidates = [mv for mv in self.board.generate_legal_moves(self.board.turn) if mv[0] == self.selected and mv[1] == (r, c)]
            if move_candidates:
                mv = move_candidates[0]
                self.board.make_move(mv)
                self.selected = None
                self.legal_moves_from_selected = []
                # Trigger AI turn if enabled
                if self.ai_enabled_for_black and not self.board.game_over and self.board.turn == 'b':
                    self.pending_ai_time = pygame.time.get_ticks() + self.ai_delay_ms
            else:
                # Clear selection if clicked invalid target
                self.selected = None
                self.legal_moves_from_selected = []

    def ai_move(self):
        # Simple random move AI for black
        legal = self.board.generate_legal_moves('b')
        if not legal:
            self.board.update_game_state()
            return
        mv = random.choice(legal)
        self.board.make_move(mv)

    def update(self):
        if self.ai_enabled_for_black and not self.board.game_over and self.board.turn == 'b':
            if self.pending_ai_time is None:
                self.pending_ai_time = pygame.time.get_ticks() + self.ai_delay_ms
            elif pygame.time.get_ticks() >= self.pending_ai_time:
                self.ai_move()
                self.pending_ai_time = None

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = LIGHT if (r + c) % 2 == 0 else DARK
                pygame.draw.rect(self.screen, color, rect)

        # Highlight legal moves from selection
        if self.selected is not None:
            sr, sc = self.selected
            sel_rect = pygame.Rect(sc * TILE_SIZE, sr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((*HIGHLIGHT, 90))
            self.screen.blit(s, sel_rect.topleft)
            for (tr, tc) in self.legal_moves_from_selected:
                hint_rect = pygame.Rect(tc * TILE_SIZE, tr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                h = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                h.fill((*MOVE_HINT, 90))
                self.screen.blit(h, hint_rect.topleft)

        # If in check, shade king square
        for color in ['w', 'b']:
            if self.board.in_check(color):
                kpos = self.board.king_position(color)
                if kpos:
                    kr, kc = kpos
                    rect = pygame.Rect(kc * TILE_SIZE, kr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((*CHECK_RED, 90))
                    self.screen.blit(s, rect.topleft)

    def draw_pieces(self):
        for r in range(8):
            for c in range(8):
                p = self.board.grid[r][c]
                if not p:
                    continue
                symbol = UNICODE_PIECES.get((p.color, p.kind), '?')
                text_color = TEXT_COLOR if p.color == 'w' else TEXT_COLOR_INV
                # Slight shadow for contrast
                piece_surf_shadow = self.font_pieces.render(symbol, True, (0, 0, 0))
                piece_surf = self.font_pieces.render(symbol, True, text_color)
                rect = piece_surf.get_rect(center=(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
                rect_shadow = piece_surf_shadow.get_rect(center=(rect.centerx + 2, rect.centery + 2))
                self.screen.blit(piece_surf_shadow, rect_shadow)
                self.screen.blit(piece_surf, rect)

    def draw_info_bar(self):
        rect = pygame.Rect(0, BOARD_PIXELS, WINDOW_WIDTH, INFO_BAR_HEIGHT)
        pygame.draw.rect(self.screen, (50, 50, 60), rect)

        turn_text = "White to move" if self.board.turn == 'w' else "Black to move"
        if self.board.game_over == 'checkmate':
            if self.winner_text():
                turn_text = f"Checkmate! {self.winner_text()} wins. Click anywhere to reset."
        elif self.board.game_over == 'stalemate':
            turn_text = "Stalemate. Click anywhere to reset."
        else:
            if self.board.in_check(self.board.turn):
                turn_text += " - Check!"

        info_surf = self.font_info.render(turn_text, True, WHITE)
        self.screen.blit(info_surf, (12, BOARD_PIXELS + 24))

        hint_text = "Left click: select/move. White is human; Black is AI."
        hint_surf = self.font_info.render(hint_text, True, WHITE)
        self.screen.blit(hint_surf, (12, BOARD_PIXELS + 48))

    def winner_text(self) -> Optional[str]:
        if self.board.winner == 'w':
            return "White"
        if self.board.winner == 'b':
            return "Black"
        return None

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_board()
        self.draw_pieces()
        self.draw_info_bar()
        pygame.display.flip()

    def reset_game(self):
        self.board = Board()
        self.selected = None
        self.legal_moves_from_selected = []
        self.pending_ai_time = None


if __name__ == "__main__":
    try:
        game = ChessGame()
        game.run()
    except Exception as e:
        print("An error occurred:", e)
        pygame.quit()
        sys.exit(1)
