from __future__ import annotations
from typing import List, Tuple, Optional

from .board import Board, Coord, Move

PIECE_DIRS = {
    'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
    'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
    'Q': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)],
    'K': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
}

MATERIAL = {
    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
}


def enemy(color: str) -> str:
    return 'b' if color == 'w' else 'w'


def is_square_attacked(board: Board, sq: Coord, by_color: str) -> bool:
    # Generate pseudo-legal moves for by_color and see if any hit sq
    for mv in generate_pseudo_legal(board, by_color):
        if mv[1] == sq:
            return True
    return False


def in_check(board: Board, color: str) -> bool:
    ksq = board.find_king(color)
    if ksq is None:
        return False
    return is_square_attacked(board, ksq, enemy(color))


def generate_legal_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for mv in generate_pseudo_legal(board, color):
        nb = board.apply_move(mv)
        if not in_check(nb, color):
            moves.append(mv)
    return moves


def generate_pseudo_legal(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    forward = -1 if color == 'w' else 1
    start_rank = 6 if color == 'w' else 1
    promo_rank = 0 if color == 'w' else 7

    for piece, (r, c) in board.all_pieces():
        if board.color_of(piece) != color:
            continue
        up = piece.upper()
        if up == 'P':
            # Single push
            nr = r + forward
            if board.in_bounds(nr, c) and board.grid[nr][c] == '.':
                if nr == promo_rank:
                    for pr in ['Q', 'R', 'B', 'N']:
                        moves.append(((r, c), (nr, c), pr))
                else:
                    moves.append(((r, c), (nr, c), None))
                # Double push
                if r == start_rank:
                    nnr = r + 2 * forward
                    if board.grid[nnr][c] == '.':
                        moves.append(((r, c), (nnr, c), None))
            # Captures
            for dc in (-1, 1):
                nr = r + forward
                nc = c + dc
                if board.in_bounds(nr, nc):
                    tp = board.grid[nr][nc]
                    if tp != '.' and board.color_of(tp) == enemy(color):
                        if nr == promo_rank:
                            for pr in ['Q', 'R', 'B', 'N']:
                                moves.append(((r, c), (nr, nc), pr))
                        else:
                            moves.append(((r, c), (nr, nc), None))
            # Note: en passant not implemented
        elif up in ('N', 'K'):
            for dr, dc in PIECE_DIRS[up]:
                nr, nc = r + dr, c + dc
                if not board.in_bounds(nr, nc):
                    continue
                tp = board.grid[nr][nc]
                if tp == '.' or board.color_of(tp) == enemy(color):
                    moves.append(((r, c), (nr, nc), None))
        else:
            # Sliding pieces: B, R, Q
            for dr, dc in PIECE_DIRS[up]:
                nr, nc = r + dr, c + dc
                while board.in_bounds(nr, nc):
                    tp = board.grid[nr][nc]
                    if tp == '.':
                        moves.append(((r, c), (nr, nc), None))
                    else:
                        if board.color_of(tp) == enemy(color):
                            moves.append(((r, c), (nr, nc), None))
                        break
                    nr += dr
                    nc += dc
            # Note: castling not implemented
    return moves


def material_score(board: Board, color: str) -> int:
    score = 0
    for p, _ in board.all_pieces():
        val = MATERIAL[p.lower()]
        if board.color_of(p) == color:
            score += val
        else:
            score -= val
    return score
