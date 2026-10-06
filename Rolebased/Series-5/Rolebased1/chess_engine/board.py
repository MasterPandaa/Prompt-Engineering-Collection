from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

Coord = Tuple[int, int]
Move = Tuple[Coord, Coord]


UNICODE_PIECES: Dict[str, str] = {
    "wK": "\u2654", "wQ": "\u2655", "wR": "\u2656", "wB": "\u2657", "wN": "\u2658", "wP": "\u2659",
    "bK": "\u265A", "bQ": "\u265B", "bR": "\u265C", "bB": "\u265D", "bN": "\u265E", "bP": "\u265F",
}


START_FEN = (
    [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ]
)


@dataclass
class Board:
    grid: List[List[Optional[str]]]
    side_to_move: str = "w"  # 'w' or 'b'

    @classmethod
    def starting_position(cls) -> "Board":
        # Deep copy START_FEN grid
        grid = [row[:] for row in START_FEN]
        return cls(grid=grid, side_to_move="w")

    def at(self, r: int, c: int) -> Optional[str]:
        return self.grid[r][c]

    def set(self, r: int, c: int, piece: Optional[str]) -> None:
        self.grid[r][c] = piece

    def inside(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def color_of(self, piece: Optional[str]) -> Optional[str]:
        if piece is None:
            return None
        return piece[0]

    def apply_move(self, move: Move) -> Optional[str]:
        (r1, c1), (r2, c2) = move
        moving = self.at(r1, c1)
        captured = self.at(r2, c2)
        self.set(r2, c2, moving)
        self.set(r1, c1, None)
        # Promotion (auto-queen)
        if moving in ("wP", "bP"):
            if r2 == 0 and moving == "wP":
                self.set(r2, c2, "wQ")
            if r2 == 7 and moving == "bP":
                self.set(r2, c2, "bQ")
        # Switch side
        self.side_to_move = "b" if self.side_to_move == "w" else "w"
        return captured

    def copy(self) -> "Board":
        return Board(grid=[row[:] for row in self.grid], side_to_move=self.side_to_move)

    def find_king(self, color: str) -> Optional[Coord]:
        target = f"{color}K"
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == target:
                    return (r, c)
        return None

    def pieces(self, color: str) -> List[Tuple[Coord, str]]:
        out: List[Tuple[Coord, str]] = []
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p[0] == color:
                    out.append(((r, c), p))
        return out

    def to_unicode(self) -> List[List[str]]:
        return [[UNICODE_PIECES.get(cell, "") if cell else "" for cell in row] for row in self.grid]
