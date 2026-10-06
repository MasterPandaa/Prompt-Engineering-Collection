from __future__ import annotations
from typing import List, Tuple, Optional

from .board import Board, Move


def generate_moves(board: Board) -> List[Move]:
    color = board.side_to_move
    moves: List[Move] = []
    for (r, c), piece in board.pieces(color):
        ptype = piece[1]
        if ptype == "P":
            moves.extend(_pawn_moves(board, r, c, color))
        elif ptype == "N":
            moves.extend(_knight_moves(board, r, c, color))
        elif ptype == "B":
            moves.extend(_slider_moves(board, r, c, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)]))
        elif ptype == "R":
            moves.extend(_slider_moves(board, r, c, color, [(-1, 0), (1, 0), (0, -1), (0, 1)]))
        elif ptype == "Q":
            moves.extend(_slider_moves(board, r, c, color, [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]))
        elif ptype == "K":
            moves.extend(_king_moves(board, r, c, color))
    return moves


def _pawn_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir = -1 if color == "w" else 1
    start_row = 6 if color == "w" else 1

    # One step forward
    r1, c1 = r + dir, c
    if board.inside(r1, c1) and board.at(r1, c1) is None:
        moves.append(((r, c), (r1, c1)))
        # Two steps from start
        r2 = r + 2 * dir
        if r == start_row and board.at(r2, c) is None:
            moves.append(((r, c), (r2, c)))

    # Captures
    for dc in (-1, 1):
        rr, cc = r + dir, c + dc
        if board.inside(rr, cc):
            target = board.at(rr, cc)
            if target is not None and board.color_of(target) != color:
                moves.append(((r, c), (rr, cc)))
    return moves


def _knight_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        rr, cc = r + dr, c + dc
        if not board.inside(rr, cc):
            continue
        target = board.at(rr, cc)
        if target is None or board.color_of(target) != color:
            moves.append(((r, c), (rr, cc)))
    return moves


def _slider_moves(board: Board, r: int, c: int, color: str, deltas: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in deltas:
        rr, cc = r + dr, c + dc
        while board.inside(rr, cc):
            target = board.at(rr, cc)
            if target is None:
                moves.append(((r, c), (rr, cc)))
            else:
                if board.color_of(target) != color:
                    moves.append(((r, c), (rr, cc)))
                break
            rr += dr
            cc += dc
    return moves


def _king_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if board.inside(rr, cc):
                target = board.at(rr, cc)
                if target is None or board.color_of(target) != color:
                    moves.append(((r, c), (rr, cc)))
    return moves
