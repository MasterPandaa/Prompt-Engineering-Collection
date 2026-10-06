import sys
import random
import pygame
from typing import List, Tuple, Optional

# -----------------------------
# Configurations
# -----------------------------
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 60

# Colors
LIGHT = (240, 217, 181)   # light square
DARK = (181, 136, 99)     # dark square
HIGHLIGHT = (246, 246, 105)
MOVE_HINT = (120, 180, 120)
CHECK_RED = (220, 50, 50)
TEXT_COLOR = (20, 20, 20)
BG_COLOR = (30, 30, 30)

WHITE = 'w'
BLACK = 'b'

# Unicode chess symbols
UNICODE_PIECES = {
    (WHITE, 'K'): '♔',
    (WHITE, 'Q'): '♕',
    (WHITE, 'R'): '♖',
    (WHITE, 'B'): '♗',
    (WHITE, 'N'): '♘',
    (WHITE, 'P'): '♙',
    (BLACK, 'K'): '♚',
    (BLACK, 'Q'): '♛',
    (BLACK, 'R'): '♜',
    (BLACK, 'B'): '♝',
    (BLACK, 'N'): '♞',
    (BLACK, 'P'): '♟',
}

# Fallback font candidates likely to contain chess symbols
FONT_CANDIDATES = [
    'DejaVu Sans',
    'Segoe UI Symbol',
    'Arial Unicode MS',
    'Noto Sans Symbols2',
    'Noto Sans Symbols',
    'Arial',
]


class Piece:
    def __init__(self, color: str, kind: str):
        self.color = color  # 'w' or 'b'
        self.kind = kind    # 'K','Q','R','B','N','P'

    def __repr__(self):
        return f"{self.color}{self.kind}"


class Board:
    def __init__(self):
        # 8x8 board, (row, col) with row 0 at top
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.to_move = WHITE
        self._setup()

    def _setup(self):
        # Place pieces in standard positions
        # Black back rank
        back = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for c, k in enumerate(back):
            self.grid[0][c] = Piece(BLACK, k)
            self.grid[1][c] = Piece(BLACK, 'P')
        # White back rank
        for c, k in enumerate(back):
            self.grid[7][c] = Piece(WHITE, k)
            self.grid[6][c] = Piece(WHITE, 'P')

    def copy(self) -> 'Board':
        b = Board.__new__(Board)
        b.grid = [[None if p is None else Piece(p.color, p.kind) for p in row] for row in self.grid]
        b.to_move = self.to_move
        return b

    def inside(self, r: int, c: int) -> bool:
        return 0 <= r < ROWS and 0 <= c < COLS

    def king_position(self, color: str) -> Optional[Tuple[int, int]]:
        for r in range(ROWS):
            for c in range(COLS):
                p = self.grid[r][c]
                if p and p.color == color and p.kind == 'K':
                    return (r, c)
        return None

    def is_in_check(self, color: str) -> bool:
        kpos = self.king_position(color)
        if not kpos:
            return False
        return self.is_square_attacked(kpos[0], kpos[1], WHITE if color == BLACK else BLACK)

    def is_square_attacked(self, r: int, c: int, by_color: str) -> bool:
        # Iterate all opponent moves (pseudo-legal) and see if they attack (r,c)
        # For efficiency, generate attacks by type
        # Knights
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            rr, cc = r + dr, c + dc
            if self.inside(rr, cc):
                p = self.grid[rr][cc]
                if p and p.color == by_color and p.kind == 'N':
                    return True
        # Pawns
        dir = -1 if by_color == WHITE else 1
        for dc in (-1, 1):
            rr, cc = r + dir, c + dc
            if self.inside(rr, cc):
                p = self.grid[rr][cc]
                if p and p.color == by_color and p.kind == 'P':
                    return True
        # Kings (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if self.inside(rr, cc):
                    p = self.grid[rr][cc]
                    if p and p.color == by_color and p.kind == 'K':
                        return True
        # Sliding pieces: rook/queen (straight), bishop/queen (diagonal)
        # Straight
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            rr, cc = r + dr, c + dc
            while self.inside(rr, cc):
                p = self.grid[rr][cc]
                if p:
                    if p.color == by_color and (p.kind == 'R' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # Diagonals
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            rr, cc = r + dr, c + dc
            while self.inside(rr, cc):
                p = self.grid[rr][cc]
                if p:
                    if p.color == by_color and (p.kind == 'B' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        return False

    def generate_pseudo_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                p = self.grid[r][c]
                if not p or p.color != color:
                    continue
                if p.kind == 'P':
                    moves.extend(self._pawn_moves(r, c, color))
                elif p.kind == 'N':
                    moves.extend(self._knight_moves(r, c, color))
                elif p.kind == 'B':
                    moves.extend(self._bishop_moves(r, c, color))
                elif p.kind == 'R':
                    moves.extend(self._rook_moves(r, c, color))
                elif p.kind == 'Q':
                    moves.extend(self._queen_moves(r, c, color))
                elif p.kind == 'K':
                    moves.extend(self._king_moves(r, c, color))
        return moves

    def generate_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        legal = []
        for src, dst in self.generate_pseudo_legal_moves(color):
            b2 = self.copy()
            b2._make_move_no_checks(src, dst)
            # Promotion auto to Queen when pawn reaches last rank
            sr, sc = src
            piece = self.grid[sr][sc]
            if piece and piece.kind == 'P':
                dr, dc = dst
                if (piece.color == WHITE and dr == 0) or (piece.color == BLACK and dr == 7):
                    # simulate promotion
                    b2.grid[dr][dc] = Piece(piece.color, 'Q')
            if not b2.is_in_check(color):
                legal.append((src, dst))
        return legal

    def _make_move_no_checks(self, src: Tuple[int, int], dst: Tuple[int, int]):
        sr, sc = src
        dr, dc = dst
        p = self.grid[sr][sc]
        self.grid[dr][dc] = p
        self.grid[sr][sc] = None
        # Promotion during actual move handled in game controller

    def _pawn_moves(self, r: int, c: int, color: str):
        moves = []
        dir = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        # One step forward
        nr = r + dir
        if self.inside(nr, c) and self.grid[nr][c] is None:
            moves.append(((r, c), (nr, c)))
            # Two steps from start if clear
            nr2 = r + 2 * dir
            if r == start_row and self.grid[nr2][c] is None:
                moves.append(((r, c), (nr2, c)))
        # Captures
        for dc in (-1, 1):
            nr, nc = r + dir, c + dc
            if self.inside(nr, nc):
                target = self.grid[nr][nc]
                if target and target.color != color:
                    moves.append(((r, c), (nr, nc)))
        return moves

    def _knight_moves(self, r: int, c: int, color: str):
        moves = []
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if self.inside(nr, nc):
                t = self.grid[nr][nc]
                if t is None or t.color != color:
                    moves.append(((r, c), (nr, nc)))
        return moves

    def _ray_moves(self, r: int, c: int, color: str, deltas: List[Tuple[int, int]]):
        moves = []
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            while self.inside(nr, nc):
                t = self.grid[nr][nc]
                if t is None:
                    moves.append(((r, c), (nr, nc)))
                else:
                    if t.color != color:
                        moves.append(((r, c), (nr, nc)))
                    break
                nr += dr
                nc += dc
        return moves

    def _bishop_moves(self, r: int, c: int, color: str):
        return self._ray_moves(r, c, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def _rook_moves(self, r: int, c: int, color: str):
        return self._ray_moves(r, c, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _queen_moves(self, r: int, c: int, color: str):
        return self._ray_moves(r, c, color, [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ])

    def _king_moves(self, r: int, c: int, color: str):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    t = self.grid[nr][nc]
                    if t is None or t.color != color:
                        # Avoid stepping into attacked square (pseudo check)
                        if not self.is_square_attacked(nr, nc, WHITE if color == BLACK else BLACK):
                            moves.append(((r, c), (nr, nc)))
        return moves


class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Python Pygame Chess')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.selected: Optional[Tuple[int, int]] = None
        self.legal_for_selected: List[Tuple[int, int]] = []
        self.running = True
        self.piece_font = self._init_piece_font()
        self.info_font = pygame.font.SysFont('arial', 20)

    def _init_piece_font(self):
        # Try candidate fonts for unicode chess symbols
        for name in FONT_CANDIDATES:
            try:
                font = pygame.font.SysFont(name, int(SQUARE_SIZE * 0.75))
                # test render one symbol
                test_surface = font.render(UNICODE_PIECES[(WHITE, 'K')], True, (0, 0, 0))
                if test_surface:  # best effort
                    return font
            except Exception:
                continue
        # fallback to default font (may not contain glyphs); we'll draw shapes if missing
        return pygame.font.SysFont(None, int(SQUARE_SIZE * 0.75))

    def reset(self):
        self.board = Board()
        self.selected = None
        self.legal_for_selected = []

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._ai_move_if_needed()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_click(self, pos: Tuple[int, int]):
        if self.board.to_move != WHITE:
            return  # wait AI
        x, y = pos
        c = x // SQUARE_SIZE
        r = y // SQUARE_SIZE
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return
        if self.selected is None:
            p = self.board.grid[r][c]
            if p and p.color == WHITE:
                self.selected = (r, c)
                self.legal_for_selected = [dst for src, dst in self.board.generate_legal_moves(WHITE) if src == (r, c)]
        else:
            # attempt move
            if (r, c) in self.legal_for_selected:
                self._make_move(self.selected, (r, c))
                self.selected = None
                self.legal_for_selected = []
            else:
                # reselect
                p = self.board.grid[r][c]
                if p and p.color == WHITE:
                    self.selected = (r, c)
                    self.legal_for_selected = [dst for src, dst in self.board.generate_legal_moves(WHITE) if src == (r, c)]
                else:
                    self.selected = None
                    self.legal_for_selected = []

    def _make_move(self, src: Tuple[int, int], dst: Tuple[int, int]):
        sr, sc = src
        dr, dc = dst
        piece = self.board.grid[sr][sc]
        self.board._make_move_no_checks(src, dst)
        # promotion auto to Queen
        if piece and piece.kind == 'P':
            if (piece.color == WHITE and dr == 0) or (piece.color == BLACK and dr == 7):
                self.board.grid[dr][dc] = Piece(piece.color, 'Q')
        # switch turn
        self.board.to_move = BLACK if self.board.to_move == WHITE else WHITE

    def _ai_move_if_needed(self):
        if self.board.to_move != BLACK:
            return
        # Simple AI: choose random legal move (prioritize captures)
        legal = self.board.generate_legal_moves(BLACK)
        if not legal:
            # No legal moves - checkmate or stalemate, just stop AI moving
            return
        # prioritize captures
        captures = []
        for src, dst in legal:
            dr, dc = dst
            if self.board.grid[dr][dc] is not None:
                captures.append((src, dst))
        move = random.choice(captures if captures else legal)
        self._make_move(*move)

    def _draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                pygame.draw.rect(self.screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        # highlight selection
        if self.selected:
            r, c = self.selected
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((*HIGHLIGHT, 100))
            self.screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
        # show legal move hints
        for (r, c) in self.legal_for_selected:
            cx = c * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = r * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, MOVE_HINT, (cx, cy), SQUARE_SIZE // 8)

        # check highlight on king
        if self.board.is_in_check(self.board.to_move):
            kp = self.board.king_position(self.board.to_move)
            if kp:
                r, c = kp
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((*CHECK_RED, 100))
                self.screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

    def _piece_glyph_available(self, piece: Piece) -> bool:
        glyph = UNICODE_PIECES.get((piece.color, piece.kind))
        if glyph is None:
            return False
        try:
            # Try rendering off-screen to check glyph support
            surf = self.piece_font.render(glyph, True, (0, 0, 0))
            return surf is not None and surf.get_width() > 0
        except Exception:
            return False

    def _draw_piece_shape(self, piece: Piece, rect: pygame.Rect):
        # Fallback simple geometric shapes per piece type
        cx = rect.x + rect.w // 2
        cy = rect.y + rect.h // 2
        size = rect.w // 2 - 6
        color = (30, 30, 30) if piece.color == WHITE else (240, 240, 240)
        outline = (0, 0, 0)
        if piece.kind == 'P':
            pygame.draw.circle(self.screen, color, (cx, cy - 6), size // 2)
            pygame.draw.rect(self.screen, color, (cx - size // 3, cy - 2, 2 * size // 3, size))
            pygame.draw.circle(self.screen, outline, (cx, cy - 6), size // 2, 2)
        elif piece.kind == 'R':
            pygame.draw.rect(self.screen, color, (rect.x + 8, rect.y + 14, rect.w - 16, rect.h - 22))
            pygame.draw.rect(self.screen, outline, (rect.x + 8, rect.y + 14, rect.w - 16, rect.h - 22), 2)
            # crenelations
            for i in range(3):
                pygame.draw.rect(self.screen, color, (rect.x + 10 + i * (rect.w - 20) // 3, rect.y + 6, (rect.w - 24)//3, 8))
        elif piece.kind == 'N':
            points = [
                (rect.x + 10, rect.y + rect.h - 10),
                (rect.x + rect.w - 10, rect.y + rect.h - 10),
                (rect.x + rect.w - 18, rect.y + 18),
                (rect.x + 20, rect.y + 24),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline, points, 2)
        elif piece.kind == 'B':
            pygame.draw.ellipse(self.screen, color, (rect.x + 10, rect.y + 8, rect.w - 20, rect.h - 16))
            pygame.draw.ellipse(self.screen, outline, (rect.x + 10, rect.y + 8, rect.w - 20, rect.h - 16), 2)
            pygame.draw.circle(self.screen, outline, (cx, rect.y + 14), 3)
        elif piece.kind == 'Q':
            points = [
                (cx, rect.y + 8),
                (rect.x + rect.w - 10, rect.y + rect.h - 12),
                (rect.x + 10, rect.y + rect.h - 12),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, outline, points, 2)
            pygame.draw.circle(self.screen, outline, (cx, rect.y + 8), 4)
        elif piece.kind == 'K':
            pygame.draw.rect(self.screen, color, (rect.x + 12, rect.y + 16, rect.w - 24, rect.h - 28))
            pygame.draw.rect(self.screen, outline, (rect.x + 12, rect.y + 16, rect.w - 24, rect.h - 28), 2)
            pygame.draw.line(self.screen, outline, (cx, rect.y + 8), (cx, rect.y + 26), 2)
            pygame.draw.line(self.screen, outline, (cx - 8, rect.y + 16), (cx + 8, rect.y + 16), 2)
        else:
            # Default fallback letter
            label = f"{piece.kind}"
            glyph_surf = self.piece_font.render(label, True, (0, 0, 0) if piece.color == WHITE else (255, 255, 255))
            rect2 = glyph_surf.get_rect(center=(cx, cy))
            self.screen.blit(glyph_surf, rect2)

    def _draw_pieces(self):
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board.grid[r][c]
                if not p:
                    continue
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                if self._piece_glyph_available(p):
                    glyph = UNICODE_PIECES[(p.color, p.kind)]
                    color = (0, 0, 0) if p.color == WHITE else (255, 255, 255)
                    surf = self.piece_font.render(glyph, True, color)
                    surf_rect = surf.get_rect(center=rect.center)
                    self.screen.blit(surf, surf_rect)
                else:
                    self._draw_piece_shape(p, rect)

    def _draw_info_bar(self):
        # Draw simple text info at top-left
        turn_text = 'Putih jalan' if self.board.to_move == WHITE else 'Hitam (AI) jalan'
        check_text = ' - SKAK!' if self.board.is_in_check(self.board.to_move) else ''
        text = self.info_font.render(f"{turn_text}{check_text}", True, TEXT_COLOR)
        pad = 6
        bg = pygame.Surface((text.get_width() + 2 * pad, text.get_height() + 2 * pad))
        bg.fill((230, 230, 230))
        self.screen.blit(bg, (5, 5))
        self.screen.blit(text, (5 + pad, 5 + pad))

    def _draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_board()
        self._draw_pieces()
        self._draw_info_bar()
        pygame.display.flip()


def main():
    game = ChessGame()
    game.run()


if __name__ == '__main__':
    main()
