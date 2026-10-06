import sys
import random
import pygame
from typing import List, Tuple, Optional

# ------------------------------
# Configuration
# ------------------------------
BOARD_SIZE = 8
SQ_SIZE = 80
MARGIN = 40  # margin for coordinates
WIDTH = MARGIN * 2 + SQ_SIZE * BOARD_SIZE
HEIGHT = MARGIN * 2 + SQ_SIZE * BOARD_SIZE
FPS = 60

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_FROM = (255, 255, 0)
HIGHLIGHT_TO = (50, 205, 50)
HIGHLIGHT_CHECK = (255, 99, 71)
MOVE_DOT = (30, 144, 255)
TEXT_COLOR = (20, 20, 20)

# Material values for evaluation
MATERIAL = {
    'P': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 0,
}

# Unicode chess symbols
UNICODE_WHITE = {
    'K': '\u2654',
    'Q': '\u2655',
    'R': '\u2656',
    'B': '\u2657',
    'N': '\u2658',
    'P': '\u2659',
}
UNICODE_BLACK = {
    'K': '\u265A',
    'Q': '\u265B',
    'R': '\u265C',
    'B': '\u265D',
    'N': '\u265E',
    'P': '\u265F',
}

# ------------------------------
# Data Structures
# ------------------------------
class Piece:
    def __init__(self, kind: str, color: str):
        self.kind = kind  # 'P','R','N','B','Q','K'
        self.color = color  # 'w' or 'b'

    def __repr__(self):
        return f"{self.color}{self.kind}"


class Board:
    def __init__(self):
        # board[r][c] with r=0 at top (Black side), c=0 at left
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.to_move: str = 'w'  # 'w' or 'b'
        self.place_starting_position()

    def clone(self) -> 'Board':
        b = Board.__new__(Board)
        b.board = [[None if p is None else Piece(p.kind, p.color) for p in row] for row in self.board]
        b.to_move = self.to_move
        return b

    def place_starting_position(self):
        # Place pawns
        for c in range(BOARD_SIZE):
            self.board[1][c] = Piece('P', 'b')
            self.board[6][c] = Piece('P', 'w')
        # Place back ranks
        back = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for c, k in enumerate(back):
            self.board[0][c] = Piece(k, 'b')
            self.board[7][c] = Piece(k, 'w')

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def king_pos(self, color: str) -> Tuple[int, int]:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board[r][c]
                if p and p.kind == 'K' and p.color == color:
                    return r, c
        # Should never happen in normal play
        return -1, -1

    # --------------------------
    # Move Generation
    # --------------------------
    def generate_pseudo_legal_moves(self, color: str) -> List[Tuple[Tuple[int,int], Tuple[int,int], Optional[str]]]:
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board[r][c]
                if not p or p.color != color:
                    continue
                if p.kind == 'P':
                    moves.extend(self._pawn_moves(r, c, color))
                elif p.kind == 'N':
                    moves.extend(self._knight_moves(r, c, color))
                elif p.kind == 'B':
                    moves.extend(self._slider_moves(r, c, color, [(-1,-1),(-1,1),(1,-1),(1,1)]))
                elif p.kind == 'R':
                    moves.extend(self._slider_moves(r, c, color, [(-1,0),(1,0),(0,-1),(0,1)]))
                elif p.kind == 'Q':
                    moves.extend(self._slider_moves(r, c, color, [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]))
                elif p.kind == 'K':
                    moves.extend(self._king_moves(r, c, color))
        return moves

    def generate_legal_moves(self, color: str) -> List[Tuple[Tuple[int,int], Tuple[int,int], Optional[str]]]:
        moves = []
        for move in self.generate_pseudo_legal_moves(color):
            b2 = self.clone()
            b2._apply_move(move)
            if not b2.is_in_check(color):
                moves.append(move)
        return moves

    def is_in_check(self, color: str) -> bool:
        kr, kc = self.king_pos(color)
        # attacked by opponent
        opp = 'b' if color == 'w' else 'w'
        return self.square_attacked_by(kr, kc, opp)

    def square_attacked_by(self, r: int, c: int, color: str) -> bool:
        # Knights
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr, cc = r+dr, c+dc
            if self.in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p and p.color == color and p.kind == 'N':
                    return True
        # Sliding bishops/queens
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            rr, cc = r+dr, c+dc
            while self.in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p.color == color and (p.kind == 'B' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # Sliding rooks/queens
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            rr, cc = r+dr, c+dc
            while self.in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p.color == color and (p.kind == 'R' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # Kings
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r+dr, c+dc
                if self.in_bounds(rr, cc):
                    p = self.board[rr][cc]
                    if p and p.color == color and p.kind == 'K':
                        return True
        # Pawns
        dir = -1 if color == 'w' else 1  # if white attacks upward (from bottom), their pawns attack -1 rows relative to their own movement; here color is attacker
        for dc in (-1, 1):
            rr, cc = r + dir, c + dc
            if self.in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p and p.color == color and p.kind == 'P':
                    return True
        return False

    # Piece moves
    def _pawn_moves(self, r: int, c: int, color: str):
        moves = []
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        promo_row = 0 if color == 'w' else 7
        # one forward
        r1, c1 = r + dir, c
        if self.in_bounds(r1, c1) and self.board[r1][c1] is None:
            promo = 'Q' if r1 == promo_row else None
            moves.append(((r, c), (r1, c1), promo))
            # two forward from start
            r2 = r + 2*dir
            if r == start_row and self.board[r2][c1] is None:
                moves.append(((r, c), (r2, c1), None))
        # captures
        for dc in (-1, 1):
            rr, cc = r + dir, c + dc
            if self.in_bounds(rr, cc):
                target = self.board[rr][cc]
                if target and target.color != color:
                    promo = 'Q' if rr == promo_row else None
                    moves.append(((r, c), (rr, cc), promo))
        # No en passant for simplicity
        return moves

    def _knight_moves(self, r: int, c: int, color: str):
        moves = []
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr, cc = r+dr, c+dc
            if not self.in_bounds(rr, cc):
                continue
            target = self.board[rr][cc]
            if target is None or target.color != color:
                moves.append(((r, c), (rr, cc), None))
        return moves

    def _slider_moves(self, r: int, c: int, color: str, directions: List[Tuple[int,int]]):
        moves = []
        for dr, dc in directions:
            rr, cc = r+dr, c+dc
            while self.in_bounds(rr, cc):
                target = self.board[rr][cc]
                if target is None:
                    moves.append(((r, c), (rr, cc), None))
                else:
                    if target.color != color:
                        moves.append(((r, c), (rr, cc), None))
                    break
                rr += dr
                cc += dc
        return moves

    def _king_moves(self, r: int, c: int, color: str):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r+dr, c+dc
                if not self.in_bounds(rr, cc):
                    continue
                target = self.board[rr][cc]
                if target is None or target.color != color:
                    moves.append(((r, c), (rr, cc), None))
        # Castling omitted for simplicity
        return moves

    # --------------------------
    # Apply / Undo
    # --------------------------
    def _apply_move(self, move):
        (r1, c1), (r2, c2), promo = move
        piece = self.board[r1][c1]
        self.board[r1][c1] = None
        if promo and piece and piece.kind == 'P':
            self.board[r2][c2] = Piece(promo, piece.color)
        else:
            self.board[r2][c2] = piece
        self.to_move = 'b' if self.to_move == 'w' else 'w'

    def make_move(self, move):
        self._apply_move(move)

    # --------------------------
    # Evaluation for AI
    # --------------------------
    def evaluate(self) -> int:
        # Positive is good for White
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board[r][c]
                if p:
                    val = MATERIAL[p.kind]
                    score += val if p.color == 'w' else -val
        return score


# ------------------------------
# Rendering and UI
# ------------------------------
class ChessUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pygame Chess - Player (White) vs Random AI (Black)')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_coords = pygame.font.SysFont('consolas', 16)
        self.font_status = pygame.font.SysFont('consolas', 20)
        self.chess_font = self._find_chess_font(size=int(SQ_SIZE*0.8))

        self.board = Board()
        self.selected: Optional[Tuple[int,int]] = None
        self.legal_moves_from_selected: List[Tuple[Tuple[int,int], Tuple[int,int], Optional[str]]] = []
        self.game_over_text: Optional[str] = None

        # To avoid AI moving too fast; small delay
        self.after_player_move_cooldown = 0

    def _find_chess_font(self, size: int) -> Optional[pygame.font.Font]:
        # Try common fonts that include chess symbols
        candidates = [
            'dejavusans', 'dejavu sans', 'segoe ui symbol', 'arial unicode ms', 'noto sans symbols2', 'symbola',
            'liberation sans', 'lucida sans unicode'
        ]
        for name in candidates:
            try:
                fpath = pygame.font.match_font(name)
                if fpath:
                    font = pygame.font.Font(fpath, size)
                    # Try render a chess char to ensure glyph exists
                    test_surface = font.render(UNICODE_WHITE['K'], True, (0,0,0))
                    if test_surface.get_width() > 0:
                        return font
            except Exception:
                continue
        # Fall back to default; may or may not include glyphs
        try:
            font = pygame.font.SysFont(None, size)
            test_surface = font.render(UNICODE_WHITE['K'], True, (0,0,0))
            if test_surface.get_width() > 0:
                return font
        except Exception:
            pass
        return None

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_over_text is None and self.board.to_move == 'w':
                        self.handle_click(event.pos)

            # After player's move, make AI move with small cooldown
            if self.game_over_text is None and self.board.to_move == 'b':
                if self.after_player_move_cooldown > 0:
                    self.after_player_move_cooldown -= 1
                else:
                    self.make_ai_move()

            self.draw()
        pygame.quit()
        sys.exit(0)

    def handle_click(self, pos):
        r, c = self.pixel_to_square(pos)
        if r is None:
            return
        piece = self.board.board[r][c]
        if self.selected:
            # Try to move to clicked square if legal
            for move in self.legal_moves_from_selected:
                (_, _), (tr, tc), promo = move
                if tr == r and tc == c:
                    self.board.make_move(move)
                    self.selected = None
                    self.legal_moves_from_selected = []
                    self.after_player_move_cooldown = int(FPS * 0.2)
                    self.check_end_conditions()
                    return
            # If clicked on same color piece, reselect
            if piece and piece.color == 'w':
                self.select_square(r, c)
            else:
                # deselect
                self.selected = None
                self.legal_moves_from_selected = []
        else:
            # No selection yet: select if white piece
            if piece and piece.color == 'w' and self.board.to_move == 'w':
                self.select_square(r, c)

    def select_square(self, r, c):
        self.selected = (r, c)
        all_legal = self.board.generate_legal_moves('w')
        self.legal_moves_from_selected = [m for m in all_legal if m[0] == (r, c)]

    def make_ai_move(self):
        legal = self.board.generate_legal_moves('b')
        if not legal:
            self.check_end_conditions()
            return
        # Simple 1-ply material evaluation, choose best for Black (minimizes white eval)
        best_score = None
        best_moves = []
        for m in legal:
            b2 = self.board.clone()
            b2._apply_move(m)
            score = b2.evaluate()  # white perspective; black wants to minimize
            if best_score is None or score < best_score - 1:
                best_score = score
                best_moves = [m]
            elif best_score is not None and abs(score - best_score) <= 1:
                best_moves.append(m)
        move = random.choice(best_moves) if best_moves else random.choice(legal)
        self.board.make_move(move)
        self.check_end_conditions()

    def check_end_conditions(self):
        # Check for checkmate or stalemate
        color = self.board.to_move
        legal = self.board.generate_legal_moves(color)
        if not legal:
            if self.board.is_in_check(color):
                self.game_over_text = 'Skakmat! ' + ('Putih menang' if color == 'b' else 'Hitam menang')
            else:
                self.game_over_text = 'Stalemate! Seri'
        else:
            # Info if side to move is in check
            if self.board.is_in_check(color):
                # just info; render highlight
                pass

    # --------------------------
    # Drawing
    # --------------------------
    def draw(self):
        self.screen.fill((230, 230, 230))
        # Draw board squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                rect = self.square_rect(r, c)
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
                pygame.draw.rect(self.screen, color, rect)
        # Highlights
        if self.selected:
            sr, sc = self.selected
            pygame.draw.rect(self.screen, HIGHLIGHT_FROM, self.square_rect(sr, sc), 4)
            for (_, _), (tr, tc), _ in self.legal_moves_from_selected:
                pygame.draw.circle(self.screen, MOVE_DOT, self.square_center(tr, tc), 10)
        # Highlight checked king
        for color in ('w', 'b'):
            if self.board.is_in_check(color):
                kr, kc = self.board.king_pos(color)
                pygame.draw.rect(self.screen, HIGHLIGHT_CHECK, self.square_rect(kr, kc), 4)

        # Draw pieces
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board.board[r][c]
                if p:
                    self.draw_piece(r, c, p)

        # Draw coordinates
        self.draw_coordinates()

        # Status line
        status = ''
        if self.game_over_text:
            status = self.game_over_text
        else:
            status = ('Giliran: Putih' if self.board.to_move == 'w' else 'Giliran: Hitam (AI)')
            if self.board.is_in_check(self.board.to_move):
                status += ' — SKAK!'
        self.draw_status(status)

        pygame.display.flip()

    def draw_piece(self, r: int, c: int, piece: Piece):
        rect = self.square_rect(r, c)
        center = rect.center
        if self.chess_font is not None:
            symbol = UNICODE_WHITE[piece.kind] if piece.color == 'w' else UNICODE_BLACK[piece.kind]
            # draw with slight shadow for contrast
            surf_shadow = self.chess_font.render(symbol, True, (0,0,0))
            surf = self.chess_font.render(symbol, True, (255,255,255) if piece.color=='w' else (0,0,0))
            offset = int(SQ_SIZE*0.04)
            self._blit_center(surf_shadow, (center[0]+offset, center[1]+offset))
            self._blit_center(surf, center)
        else:
            # Fallback: simple geometric shapes
            if piece.kind == 'P':
                radius = int(SQ_SIZE*0.25)
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                pygame.draw.circle(self.screen, color, center, radius)
            elif piece.kind == 'R':
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                w, h = int(SQ_SIZE*0.6), int(SQ_SIZE*0.6)
                rect2 = pygame.Rect(0,0,w,h)
                rect2.center = center
                pygame.draw.rect(self.screen, color, rect2)
            elif piece.kind == 'N':
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                # Triangle
                x, y = center
                size = int(SQ_SIZE*0.3)
                pts = [(x, y-size), (x-size, y+size), (x+size, y+size)]
                pygame.draw.polygon(self.screen, color, pts)
            elif piece.kind == 'B':
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                pygame.draw.ellipse(self.screen, color, pygame.Rect(center[0]-SQ_SIZE*0.25, center[1]-SQ_SIZE*0.3, SQ_SIZE*0.5, SQ_SIZE*0.6))
            elif piece.kind == 'Q':
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                pygame.draw.circle(self.screen, color, (center[0], center[1]-int(SQ_SIZE*0.15)), int(SQ_SIZE*0.2))
                pygame.draw.rect(self.screen, color, pygame.Rect(center[0]-SQ_SIZE*0.2, center[1]-SQ_SIZE*0.05, SQ_SIZE*0.4, SQ_SIZE*0.3))
            elif piece.kind == 'K':
                color = (255,255,255) if piece.color=='w' else (0,0,0)
                pygame.draw.rect(self.screen, color, pygame.Rect(center[0]-SQ_SIZE*0.2, center[1]-SQ_SIZE*0.2, SQ_SIZE*0.4, SQ_SIZE*0.4))
                pygame.draw.line(self.screen, color, (center[0], center[1]-int(SQ_SIZE*0.3)), (center[0], center[1]-int(SQ_SIZE*0.45)), 6)
                pygame.draw.line(self.screen, color, (center[0]-int(SQ_SIZE*0.1), center[1]-int(SQ_SIZE*0.375)), (center[0]+int(SQ_SIZE*0.1), center[1]-int(SQ_SIZE*0.375)), 6)

    def draw_coordinates(self):
        # Files a-h at bottom and top, ranks 1-8 at sides
        for c in range(BOARD_SIZE):
            file_char = chr(ord('a') + c)
            # bottom
            surf = self.font_coords.render(file_char, True, TEXT_COLOR)
            x = MARGIN + c*SQ_SIZE + SQ_SIZE//2
            y = HEIGHT - MARGIN + 12
            self._blit_center(surf, (x, y))
            # top
            surf2 = self.font_coords.render(file_char, True, TEXT_COLOR)
            x2 = MARGIN + c*SQ_SIZE + SQ_SIZE//2
            y2 = MARGIN - 16
            self._blit_center(surf2, (x2, y2))
        for r in range(BOARD_SIZE):
            rank_char = str(BOARD_SIZE - r)
            # left
            surf = self.font_coords.render(rank_char, True, TEXT_COLOR)
            x = MARGIN - 16
            y = MARGIN + r*SQ_SIZE + SQ_SIZE//2
            self._blit_center(surf, (x, y))
            # right
            surf2 = self.font_coords.render(rank_char, True, TEXT_COLOR)
            x2 = WIDTH - MARGIN + 16
            y2 = MARGIN + r*SQ_SIZE + SQ_SIZE//2
            self._blit_center(surf2, (x2, y2))

    def draw_status(self, text: str):
        surf = self.font_status.render(text, True, (10,10,10))
        self.screen.blit(surf, (MARGIN, 8))

    # --------------------------
    # Helpers
    # --------------------------
    def square_rect(self, r: int, c: int) -> pygame.Rect:
        x = MARGIN + c * SQ_SIZE
        y = MARGIN + r * SQ_SIZE
        return pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)

    def square_center(self, r: int, c: int) -> Tuple[int, int]:
        rect = self.square_rect(r, c)
        return rect.center

    def pixel_to_square(self, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[int]]:
        x, y = pos
        x -= MARGIN
        y -= MARGIN
        if x < 0 or y < 0:
            return None, None
        c = x // SQ_SIZE
        r = y // SQ_SIZE
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return int(r), int(c)
        return None, None

    def _blit_center(self, surf: pygame.Surface, center: Tuple[int,int]):
        rect = surf.get_rect(center=center)
        self.screen.blit(surf, rect)


def main():
    ui = ChessUI()
    ui.run()


if __name__ == '__main__':
    main()
