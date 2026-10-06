from __future__ import annotations
import random
from typing import List, Tuple

from .board import Board, Move
from .rules import generate_moves

PIECE_VALUE = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "P": 1,
}


def evaluate_material(board: Board, color: str) -> int:
    total = 0
    for r in range(8):
        for c in range(8):
            p = board.at(r, c)
            if not p:
                continue
            sign = 1 if p[0] == color else -1
            total += sign * PIECE_VALUE[p[1]]
    return total


def pick_move(board: Board) -> Move | None:
    moves = generate_moves(board)
    if not moves:
        return None

    # Prefer immediate captures with max gain
    best_cap = None
    best_gain = -999
    for m in moves:
        (r1, c1), (r2, c2) = m
        target = board.at(r2, c2)
        if target:
            gain = PIECE_VALUE[target[1]]
            if gain > best_gain:
                best_gain = gain
                best_cap = m
    if best_cap:
        return best_cap

    # Otherwise, simple one-ply evaluation and pick the best
    color = board.side_to_move
    scored: List[Tuple[int, Move]] = []
    for m in moves:
        b2 = board.copy()
        b2.apply_move(m)
        score = evaluate_material(b2, color)
        scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    top_moves = [m for s, m in scored if s == top_score]
    return random.choice(top_moves)
