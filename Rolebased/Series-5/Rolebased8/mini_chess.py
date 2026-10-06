import sys
import pygame
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ----------------------------
# Data Structures & Constants
# ----------------------------

BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 20
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE

LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
HIGHLIGHT_SQ = (246, 246, 105)
MOVE_HINT_SQ = (110, 160, 110)
SELECT_SQ = (120, 180, 240)

PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0,  # King is invaluable; set 0 for material evaluation
}

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


@dataclass
class Piece:
    color: str  # 'w' or 'b'
    kind: str   # 'P','N','B','R','Q','K'


Coord = Tuple[int, int]  # (row, col)
Move = Tuple[Coord, Coord]  # ((r1, c1), (r2, c2))


# ----------------------------
# Rules: move generation (no castling/en passant)
# ----------------------------

class Rules:
    @staticmethod
    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    @staticmethod
    def line_moves(board: 'Board', start: Coord, deltas: List[Tuple[int, int]]) -> List[Coord]:
        r, c = start
        src_piece = board.get(r, c)
        assert src_piece is not None
        res: List[Coord] = []
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            while Rules.in_bounds(nr, nc):
                tgt = board.get(nr, nc)
                if tgt is None:
                    res.append((nr, nc))
                else:
                    if tgt.color != src_piece.color:
                        res.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return res

    @staticmethod
    def knight_moves(board: 'Board', start: Coord) -> List[Coord]:
        r, c = start
        src = board.get(r, c)
        res: List[Coord] = []
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            nr, nc = r + dr, c + dc
            if not Rules.in_bounds(nr, nc):
                continue
            tgt = board.get(nr, nc)
            if tgt is None or tgt.color != src.color:
                res.append((nr, nc))
        return res

    @staticmethod
    def king_moves(board: 'Board', start: Coord) -> List[Coord]:
        r, c = start
        src = board.get(r, c)
        res: List[Coord] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not Rules.in_bounds(nr, nc):
                    continue
                tgt = board.get(nr, nc)
                if tgt is None or tgt.color != src.color:
                    res.append((nr, nc))
        return res

    @staticmethod
    def pawn_moves(board: 'Board', start: Coord) -> List[Coord]:
        r, c = start
        src = board.get(r, c)
        assert src is not None and src.kind == 'P'
        res: List[Coord] = []
        dir = -1 if src.color == 'w' else 1  # white moves up (towards row 0)
        start_row = 6 if src.color == 'w' else 1

        # Forward one
        nr, nc = r + dir, c
        if Rules.in_bounds(nr, nc) and board.get(nr, nc) is None:
            res.append((nr, nc))
            # Forward two from start
            nr2 = r + 2 * dir
            if r == start_row and Rules.in_bounds(nr2, c) and board.get(nr2, c) is None:
                res.append((nr2, c))

        # Captures
        for dc in (-1, 1):
            nr, nc = r + dir, c + dc
            if not Rules.in_bounds(nr, nc):
                continue
            tgt = board.get(nr, nc)
            if tgt is not None and tgt.color != src.color:
                res.append((nr, nc))

        return res

    @staticmethod
    def moves_for_piece(board: 'Board', pos: Coord) -> List[Coord]:
        piece = board.get(*pos)
        if piece is None:
            return []
        if piece.kind == 'P':
            return Rules.pawn_moves(board, pos)
        if piece.kind == 'N':
            return Rules.knight_moves(board, pos)
        if piece.kind == 'B':
            return Rules.line_moves(board, pos, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        if piece.kind == 'R':
            return Rules.line_moves(board, pos, [(-1, 0), (1, 0), (0, -1), (0, 1)])
        if piece.kind == 'Q':
            return Rules.line_moves(board, pos, [
                (-1, -1), (-1, 1), (1, -1), (1, 1),
                (-1, 0), (1, 0), (0, -1), (0, 1),
            ])
        if piece.kind == 'K':
            return Rules.king_moves(board, pos)
        return []


# ----------------------------
# Board: state & helpers
# ----------------------------

class Board:
    def __init__(self):
        self.grid: List[List[Optional[Piece]] ] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_initial()

    def clone(self) -> 'Board':
        b = Board.__new__(Board)
        b.grid = [[None if p is None else Piece(p.color, p.kind) for p in row] for row in self.grid]
        return b

    def setup_initial(self):
        # Place pieces for black (top)
        back_rank = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for c, k in enumerate(back_rank):
            self.grid[0][c] = Piece('b', k)
            self.grid[7][c] = Piece('w', k)
        for c in range(BOARD_SIZE):
            self.grid[1][c] = Piece('b', 'P')
            self.grid[6][c] = Piece('w', 'P')

    def get(self, r: int, c: int) -> Optional[Piece]:
        return self.grid[r][c]

    def set(self, r: int, c: int, piece: Optional[Piece]):
        self.grid[r][c] = piece

    def move(self, src: Coord, dst: Coord) -> Optional[Piece]:
        sr, sc = src
        dr, dc = dst
        moving = self.get(sr, sc)
        captured = self.get(dr, dc)
        self.set(dr, dc, moving)
        self.set(sr, sc, None)
        # Promotion (simple: auto-queen)
        if moving and moving.kind == 'P':
            if moving.color == 'w' and dr == 0:
                moving.kind = 'Q'
            elif moving.color == 'b' and dr == 7:
                moving.kind = 'Q'
        return captured

    def generate_moves(self, color: str) -> List[Move]:
        moves: List[Move] = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.get(r, c)
                if p is None or p.color != color:
                    continue
                for (nr, nc) in Rules.moves_for_piece(self, (r, c)):
                    moves.append(((r, c), (nr, nc)))
        return moves

    def material_eval(self) -> int:
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.get(r, c)
                if p:
                    val = PIECE_VALUES[p.kind]
                    score += val if p.color == 'w' else -val
        return score


# ----------------------------
# Simple AI: prefer free captures, otherwise random-ish best material
# ----------------------------

import random

class SimpleAI:
    def __init__(self, color: str):
        self.color = color  # 'w' or 'b'

    def choose_move(self, board: Board) -> Optional[Move]:
        moves = board.generate_moves(self.color)
        if not moves:
            return None

        # Score moves: prioritize captures by captured value, slight penalty for using more valuable mover
        best_score = -9999 if self.color == 'w' else 9999
        best_moves: List[Move] = []

        for mv in moves:
            src, dst = mv
            sr, sc = src
            dr, dc = dst
            mover = board.get(sr, sc)
            tgt = board.get(dr, dc)
            capture_val = PIECE_VALUES[tgt.kind] if tgt else 0
            mover_val = PIECE_VALUES[mover.kind] if mover else 0
            # Immediate heuristic score (capture greediness)
            immediate = capture_val - 0.01 * mover_val

            # Shallow lookahead: apply move and evaluate material
            sim = board.clone()
            sim.move(src, dst)
            eval_after = sim.material_eval()
            score = immediate + (eval_after if self.color == 'w' else -eval_after) * 0.05

            if self.color == 'w':
                if score > best_score + 1e-9:
                    best_score = score
                    best_moves = [mv]
                elif abs(score - best_score) < 1e-9:
                    best_moves.append(mv)
            else:
                if score < best_score - 1e-9:
                    best_score = score
                    best_moves = [mv]
                elif abs(score - best_score) < 1e-9:
                    best_moves.append(mv)

        return random.choice(best_moves)


# ----------------------------
# Pygame UI
# ----------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Mini Chess - Unicode & Simple AI')
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, int(SQUARE_SIZE * 0.75))

        self.board = Board()
        self.turn = 'w'  # Human as white
        self.ai = SimpleAI('b')

        self.selected: Optional[Coord] = None
        self.legal_from_selected: List[Coord] = []

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

        # Highlight selected square
        if self.selected is not None:
            r, c = self.selected
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, SELECT_SQ, rect, 0)

        # Draw move hints from selected
        for (mr, mc) in self.legal_from_selected:
            hint_rect = pygame.Rect(mc * SQUARE_SIZE, mr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            surface.fill((*MOVE_HINT_SQ, 90))
            self.screen.blit(surface, (mc * SQUARE_SIZE, mr * SQUARE_SIZE))

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board.get(r, c)
                if not p:
                    continue
                ch = UNICODE_PIECES[(p.color, p.kind)]
                text = self.font.render(ch, True, (20, 20, 20))
                text_rect = text.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2))
                self.screen.blit(text, text_rect)

    def square_at(self, pos: Tuple[int, int]) -> Optional[Coord]:
        x, y = pos
        c = x // SQUARE_SIZE
        r = y // SQUARE_SIZE
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return (r, c)
        return None

    def update_selection(self, sq: Optional[Coord]):
        if sq is None:
            self.selected = None
            self.legal_from_selected = []
            return
        r, c = sq
        piece = self.board.get(r, c)
        if piece and piece.color == self.turn:
            self.selected = sq
            self.legal_from_selected = Rules.moves_for_piece(self.board, sq)
        else:
            # Clicked empty or enemy while not selected or invalid -> maybe try move
            if self.selected is not None and sq in self.legal_from_selected:
                self.make_move(self.selected, sq)
                self.selected = None
                self.legal_from_selected = []
            else:
                self.selected = None
                self.legal_from_selected = []

    def make_move(self, src: Coord, dst: Coord):
        # No check rules; just basic legal moves by piece rules
        self.board.move(src, dst)
        self.turn = 'b' if self.turn == 'w' else 'w'

    def maybe_ai_move(self):
        if self.turn != self.ai.color:
            return
        mv = self.ai.choose_move(self.board)
        if mv is None:
            return
        self.board.move(*mv)
        self.turn = 'b' if self.turn == 'w' else 'w'

    def draw_turn_label(self):
        label = f"Turn: {'White' if self.turn == 'w' else 'Black'}"
        small_font = pygame.font.SysFont(None, 24)
        text = small_font.render(label, True, (10, 10, 10))
        self.screen.blit(text, (6, 6))

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.turn == 'w':  # Human turn
                        sq = self.square_at(event.pos)
                        self.update_selection(sq)

            # AI move when it's AI's turn
            if self.turn == self.ai.color:
                self.maybe_ai_move()

            self.draw_board()
            self.draw_pieces()
            self.draw_turn_label()
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    Game().run()
