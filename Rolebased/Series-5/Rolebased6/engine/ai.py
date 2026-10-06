from __future__ import annotations
import random
from typing import Optional, Tuple

from .board import Board, Move
from .rules import generate_legal_moves, material_score


class SimpleAI:
    def __init__(self, color: str):
        self.color = color

    def choose_move(self, board: Board) -> Optional[Move]:
        legal = generate_legal_moves(board, self.color)
        if not legal:
            return None
        # Prefer captures with best material gain
        best_moves = []
        best_gain = -999
        for mv in legal:
            (r1, c1), (r2, c2), promo = mv
            before = material_score(board, self.color)
            nb = board.apply_move(mv)
            after = material_score(nb, self.color)
            gain = after - before
            if gain > best_gain:
                best_gain = gain
                best_moves = [mv]
            elif gain == best_gain:
                best_moves.append(mv)
        return random.choice(best_moves)
