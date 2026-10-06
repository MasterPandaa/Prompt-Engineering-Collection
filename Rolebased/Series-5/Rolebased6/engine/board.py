from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Board representation: 8x8 list of strings
# Pieces: 'P','N','B','R','Q','K' for White, lowercase for Black
# Empty squares: '.'

Coord = Tuple[int, int]  # (row, col)
Move = Tuple[Coord, Coord, Optional[str]]  # from, to, promotion

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"


def fen_to_board(fen: str) -> Tuple[List[List[str]], str]:
    position, side = fen.split()
    rows = position.split('/')
    board: List[List[str]] = []
    for r in rows:
        row: List[str] = []
        for ch in r:
            if ch.isdigit():
                row.extend(['.'] * int(ch))
            else:
                row.append(ch)
        board.append(row)
    return board, side


def clone_grid(grid: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in grid]


@dataclass
class Board:
    grid: List[List[str]]
    side_to_move: str = 'w'  # 'w' or 'b'
    halfmove_clock: int = 0
    fullmove_number: int = 1

    @classmethod
    def starting(cls) -> "Board":
        grid, side = fen_to_board(START_FEN)
        return cls(grid=grid, side_to_move=side)

    def copy(self) -> "Board":
        return Board(grid=clone_grid(self.grid),
                     side_to_move=self.side_to_move,
                     halfmove_clock=self.halfmove_clock,
                     fullmove_number=self.fullmove_number)

    def piece_at(self, coord: Coord) -> str:
        r, c = coord
        return self.grid[r][c]

    def set_piece(self, coord: Coord, piece: str) -> None:
        r, c = coord
        self.grid[r][c] = piece

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def apply_move(self, move: Move) -> "Board":
        # Returns a new board with the move applied (no rule checking here)
        (r1, c1), (r2, c2), promo = move
        nb = self.copy()
        piece = nb.piece_at((r1, c1))
        nb.set_piece((r1, c1), '.')
        if promo:
            # Promotion piece should be uppercase for white and lowercase for black
            if piece.isupper():
                nb.set_piece((r2, c2), promo.upper())
            else:
                nb.set_piece((r2, c2), promo.lower())
        else:
            nb.set_piece((r2, c2), piece)
        nb.side_to_move = 'b' if self.side_to_move == 'w' else 'w'
        if nb.side_to_move == 'w':
            nb.fullmove_number += 1
        return nb

    def all_pieces(self) -> List[Tuple[str, Coord]]:
        out: List[Tuple[str, Coord]] = []
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p != '.':
                    out.append((p, (r, c)))
        return out

    def color_of(self, piece: str) -> Optional[str]:
        if piece == '.':
            return None
        return 'w' if piece.isupper() else 'b'

    def find_king(self, color: str) -> Optional[Coord]:
        target = 'K' if color == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == target:
                    return (r, c)
        return None
