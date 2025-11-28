import sys
import math
import random
import pygame
from typing import List, Tuple, Optional, Dict

# -----------------------------
# Constants and Types
# -----------------------------
WHITE = 'w'
BLACK = 'b'
EMPTY = None

PIECES = ['K', 'Q', 'R', 'B', 'N', 'P']
UNICODE_MAP = {
    (WHITE, 'K'): '\u2654',
    (WHITE, 'Q'): '\u2655',
    (WHITE, 'R'): '\u2656',
    (WHITE, 'B'): '\u2657',
    (WHITE, 'N'): '\u2658',
    (WHITE, 'P'): '\u2659',
    (BLACK, 'K'): '\u265A',
    (BLACK, 'Q'): '\u265B',
    (BLACK, 'R'): '\u265C',
    (BLACK, 'B'): '\u265D',
    (BLACK, 'N'): '\u265E',
    (BLACK, 'P'): '\u265F',
}

MATERIAL_VALUE = {
    'K': 0,
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'P': 1,
}

Coord = Tuple[int, int]  # (row, col)
Move = Tuple[Coord, Coord]  # ((r1,c1),(r2,c2))
Piece = Optional[Tuple[str, str]]  # (color, piece)

# -----------------------------
# Board
# -----------------------------
class Board:
    def __init__(self) -> None:
        # 8x8 board, row 0 is Black back rank, row 7 is White back rank
        self.squares: List[List[Piece]] = [[EMPTY for _ in range(8)] for _ in range(8)]
        self.turn: str = WHITE
        self.setup()

    def clone(self) -> 'Board':
        b = Board.__new__(Board)  # avoid re-setup
        b.squares = [[self.squares[r][c] for c in range(8)] for r in range(8)]
        b.turn = self.turn
        return b

    def setup(self) -> None:
        # Black pieces
        self.squares[0] = [
            (BLACK, 'R'), (BLACK, 'N'), (BLACK, 'B'), (BLACK, 'Q'),
            (BLACK, 'K'), (BLACK, 'B'), (BLACK, 'N'), (BLACK, 'R')
        ]
        self.squares[1] = [(BLACK, 'P')] * 8
        # Empty middle
        for r in range(2, 6):
            self.squares[r] = [EMPTY] * 8
        # White pieces
        self.squares[6] = [(WHITE, 'P')] * 8
        self.squares[7] = [
            (WHITE, 'R'), (WHITE, 'N'), (WHITE, 'B'), (WHITE, 'Q'),
            (WHITE, 'K'), (WHITE, 'B'), (WHITE, 'N'), (WHITE, 'R')
        ]

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def get(self, rc: Coord) -> Piece:
        r, c = rc
        return self.squares[r][c]

    def set(self, rc: Coord, piece: Piece) -> None:
        r, c = rc
        self.squares[r][c] = piece

    def move(self, mv: Move) -> None:
        (r1, c1), (r2, c2) = mv
        piece = self.get((r1, c1))
        self.set((r1, c1), EMPTY)
        # Simple promotion to queen if pawn reaches last rank
        if piece and piece[1] == 'P' and (r2 == 0 or r2 == 7):
            self.set((r2, c2), (piece[0], 'Q'))
        else:
            self.set((r2, c2), piece)
        self.turn = BLACK if self.turn == WHITE else WHITE

    def all_pieces(self, color: str) -> List[Tuple[Coord, Piece]]:
        out = []
        for r in range(8):
            for c in range(8):
                p = self.squares[r][c]
                if p is not None and p[0] == color:
                    out.append(((r, c), p))
        return out

# -----------------------------
# Rules (Move Generation)
# -----------------------------
class Rules:
    @staticmethod
    def legal_moves(board: Board, rc: Coord) -> List[Coord]:
        piece = board.get(rc)
        if not piece:
            return []
        color, kind = piece
        r, c = rc
        moves: List[Coord] = []

        if kind == 'P':
            dir_ = -1 if color == WHITE else 1
            start_row = 6 if color == WHITE else 1
            # forward 1
            nr, nc = r + dir_, c
            if board.in_bounds(nr, nc) and board.get((nr, nc)) is EMPTY:
                moves.append((nr, nc))
                # forward 2 from start
                nr2 = r + 2 * dir_
                if r == start_row and board.get((nr2, nc)) is EMPTY:
                    moves.append((nr2, nc))
            # captures
            for dc in (-1, 1):
                nr, nc = r + dir_, c + dc
                if board.in_bounds(nr, nc):
                    target = board.get((nr, nc))
                    if target is not None and target[0] != color:
                        moves.append((nr, nc))
            return moves

        if kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r + dr, c + dc
                if board.in_bounds(nr, nc):
                    target = board.get((nr, nc))
                    if target is None or target[0] != color:
                        moves.append((nr, nc))
            return moves

        if kind in ('B', 'R', 'Q'):
            directions = []
            if kind in ('B', 'Q'):
                directions += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if kind in ('R', 'Q'):
                directions += [(-1,0),(1,0),(0,-1),(0,1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while board.in_bounds(nr, nc):
                    target = board.get((nr, nc))
                    if target is None:
                        moves.append((nr, nc))
                    else:
                        if target[0] != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc
            return moves

        if kind == 'K':
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if board.in_bounds(nr, nc):
                        target = board.get((nr, nc))
                        if target is None or target[0] != color:
                            moves.append((nr, nc))
            return moves

        return moves

    @staticmethod
    def all_legal_moves(board: Board, color: str) -> List[Move]:
        res: List[Move] = []
        for (rc, _piece) in board.all_pieces(color):
            for dst in Rules.legal_moves(board, rc):
                res.append((rc, dst))
        return res

    @staticmethod
    def attack_map(board: Board, color: str) -> List[Coord]:
        # squares attacked by color (ignoring king safety)
        attacked: List[Coord] = []
        for (rc, piece) in board.all_pieces(color):
            kind = piece[1]
            r, c = rc
            if kind == 'P':
                dir_ = -1 if color == WHITE else 1
                for dc in (-1, 1):
                    nr, nc = r + dir_, c + dc
                    if board.in_bounds(nr, nc):
                        attacked.append((nr, nc))
            elif kind == 'N':
                for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                    nr, nc = r + dr, c + dc
                    if board.in_bounds(nr, nc):
                        attacked.append((nr, nc))
            elif kind in ('B', 'R', 'Q'):
                directions = []
                if kind in ('B', 'Q'):
                    directions += [(-1,-1),(-1,1),(1,-1),(1,1)]
                if kind in ('R', 'Q'):
                    directions += [(-1,0),(1,0),(0,-1),(0,1)]
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    while board.in_bounds(nr, nc):
                        attacked.append((nr, nc))
                        if board.get((nr, nc)) is not None:
                            break
                        nr += dr
                        nc += dc
            elif kind == 'K':
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if board.in_bounds(nr, nc):
                            attacked.append((nr, nc))
        return attacked

# -----------------------------
# Simple AI
# -----------------------------
class SimpleAI:
    def __init__(self, color: str):
        self.color = color

    def evaluate_material(self, board: Board) -> int:
        score = 0
        for r in range(8):
            for c in range(8):
                p = board.squares[r][c]
                if p is None:
                    continue
                val = MATERIAL_VALUE[p[1]]
                score += val if p[0] == self.color else -val
        return score

    def pick_move(self, board: Board) -> Optional[Move]:
        moves = Rules.all_legal_moves(board, self.color)
        if not moves:
            return None

        opponent = WHITE if self.color == BLACK else BLACK
        opp_attacks = set(Rules.attack_map(board, opponent))

        def capture_gain(mv: Move) -> int:
            (r1, c1), (r2, c2) = mv
            target = board.get((r2, c2))
            return MATERIAL_VALUE[target[1]] if target else 0

        # Prefer safe captures (destination square not attacked by opponent after move)
        safe_captures: List[Tuple[int, Move]] = []
        trades: List[Tuple[int, Move]] = []
        quiets: List[Move] = []
        for mv in moves:
            gain = capture_gain(mv)
            if gain > 0:
                (_, _), (r2, c2) = mv
                # naive safety: destination not currently attacked
                if (r2, c2) not in opp_attacks:
                    safe_captures.append((gain, mv))
                else:
                    trades.append((gain, mv))
            else:
                quiets.append(mv)

        if safe_captures:
            safe_captures.sort(key=lambda x: (-x[0]))
            return safe_captures[0][1]
        if trades:
            trades.sort(key=lambda x: (-x[0]))
            return trades[0][1]
        # Else any legal move
        return random.choice(quiets if quiets else moves)

# -----------------------------
# Rendering & UI
# -----------------------------
class Renderer:
    def __init__(self, square_size: int = 80):
        pygame.init()
        self.square = square_size
        self.margin = 20
        self.board_px = self.square * 8
        self.width = self.board_px + self.margin * 2
        self.height = self.board_px + self.margin * 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Mini Chess (Human vs AI)')
        self.clock = pygame.time.Clock()
        self.bg_light = (240, 217, 181)
        self.bg_dark = (181, 136, 99)
        self.sel_color = (246, 246, 105)
        self.move_hint = (106, 168, 79)
        self.text_color = (20, 20, 20)
        self.font = self._load_font()

    def _load_font(self) -> pygame.font.Font:
        # Try a few common fonts that include chess Unicode glyphs
        candidates = [
            'Segoe UI Symbol', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans Symbols2', 'Symbola'
        ]
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, int(self.square * 0.8))
                # Quick test render to ensure glyphs exist
                test = f.render('\u265A', True, (0, 0, 0))
                if test is not None:
                    return f
            except Exception:
                pass
        # fallback default
        return pygame.font.SysFont(None, int(self.square * 0.8))

    def draw(self, board: Board, selected: Optional[Coord], moves: List[Coord]) -> None:
        self.screen.fill((30, 30, 30))
        ox = self.margin
        oy = self.margin
        # Draw squares
        for r in range(8):
            for c in range(8):
                rect = pygame.Rect(ox + c * self.square, oy + r * self.square, self.square, self.square)
                base = self.bg_light if (r + c) % 2 == 0 else self.bg_dark
                pygame.draw.rect(self.screen, base, rect)

        # Highlight selected
        if selected:
            sr, sc = selected
            rect = pygame.Rect(ox + sc * self.square, oy + sr * self.square, self.square, self.square)
            pygame.draw.rect(self.screen, self.sel_color, rect, 5)

        # Show possible moves
        for (mr, mc) in moves:
            center = (ox + mc * self.square + self.square // 2, oy + mr * self.square + self.square // 2)
            pygame.draw.circle(self.screen, self.move_hint, center, max(6, self.square // 10))

        # Draw pieces
        for r in range(8):
            for c in range(8):
                p = board.squares[r][c]
                if p is None:
                    continue
                glyph = UNICODE_MAP.get(p)
                if glyph:
                    surf = self.font.render(glyph, True, self.text_color)
                    rect = surf.get_rect()
                    rect.center = (ox + c * self.square + self.square // 2, oy + r * self.square + self.square // 2)
                    self.screen.blit(surf, rect)

        pygame.display.flip()

    def coord_from_mouse(self, pos: Tuple[int, int]) -> Optional[Coord]:
        x, y = pos
        x -= self.margin
        y -= self.margin
        if not (0 <= x < self.board_px and 0 <= y < self.board_px):
            return None
        c = x // self.square
        r = y // self.square
        return (int(r), int(c))

# -----------------------------
# Game Loop
# -----------------------------
class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.rules = Rules()
        self.renderer = Renderer(square_size=80)
        self.selected: Optional[Coord] = None
        self.available_moves: List[Coord] = []
        self.human_color = WHITE
        self.ai = SimpleAI(BLACK)
        self.running = True

    def is_human_turn(self) -> bool:
        return self.board.turn == self.human_color

    def try_select(self, rc: Coord) -> None:
        piece = self.board.get(rc)
        if piece is None:
            self.selected = None
            self.available_moves = []
            return
        if piece[0] != self.human_color:
            # selecting opponent piece does nothing unless it's a valid move destination
            if self.selected and rc in self.available_moves:
                self.board.move((self.selected, rc))
                self.selected = None
                self.available_moves = []
            return
        self.selected = rc
        self.available_moves = self.rules.legal_moves(self.board, rc)

    def try_move(self, dst: Coord) -> None:
        if self.selected is None:
            return
        if dst in self.available_moves:
            self.board.move((self.selected, dst))
            self.selected = None
            self.available_moves = []

    def ai_turn(self) -> None:
        mv = self.ai.pick_move(self.board)
        if mv is None:
            return
        self.board.move(mv)

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rc = self.renderer.coord_from_mouse(event.pos)
                    if rc is None:
                        self.selected = None
                        self.available_moves = []
                    else:
                        if self.is_human_turn():
                            if self.selected is None:
                                self.try_select(rc)
                            else:
                                if rc == self.selected:
                                    self.selected = None
                                    self.available_moves = []
                                elif rc in self.available_moves:
                                    self.try_move(rc)
                                else:
                                    # selecting another own piece updates selection
                                    piece = self.board.get(rc)
                                    if piece is not None and piece[0] == self.human_color:
                                        self.try_select(rc)
            # AI move if it's AI's turn
            if not self.is_human_turn():
                self.ai_turn()

            self.renderer.draw(self.board, self.selected, self.available_moves)
            self.renderer.clock.tick(60)
        pygame.quit()


if __name__ == '__main__':
    try:
        Game().run()
    except Exception as e:
        pygame.quit()
        raise
