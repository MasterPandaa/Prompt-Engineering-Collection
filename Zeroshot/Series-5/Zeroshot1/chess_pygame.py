import sys
import random
import pygame
from typing import List, Optional, Tuple

# ---------------------------
# Config
# ---------------------------
WIDTH, HEIGHT = 720, 720
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Board colors
LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
HIGHLIGHT_MOVE = (118, 150, 86)
HIGHLIGHT_SELECT = (246, 246, 105)
HIGHLIGHT_CHECK = (255, 80, 80)
TEXT_COLOR = (30, 30, 30)
OVERLAY_BG = (0, 0, 0, 180)

# Unicode chess symbols
UNICODE_WHITE = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'
}
UNICODE_BLACK = {
    'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'
}

# ---------------------------
# Data Structures
# ---------------------------
class Piece:
    def __init__(self, kind: str, color: str):
        self.kind = kind  # 'P', 'R', 'N', 'B', 'Q', 'K'
        self.color = color  # 'w' or 'b'

    def __repr__(self):
        return f"{self.color}{self.kind}"

Board = List[List[Optional[Piece]]]
Move = Tuple[int, int, int, int, Optional[str]]  # (r1, c1, r2, c2, promotion)


# ---------------------------
# Initialization
# ---------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Chess (Unicode)")
clock = pygame.time.Clock()

# Try to pick a font likely to include Unicode chess glyphs
CANDIDATE_FONTS = [
    "DejaVu Sans", "Arial Unicode MS", "Segoe UI Symbol", "Noto Sans Symbols",
    "Segoe UI", "Arial", None
]

PIECE_FONT = None
for fname in CANDIDATE_FONTS:
    try:
        PIECE_FONT = pygame.font.SysFont(fname, int(SQUARE_SIZE * 0.8))
        test_surface = PIECE_FONT.render("♔", True, (0, 0, 0))
        # If width is 0 (unlikely), try next font
        if test_surface.get_width() <= 0:
            continue
        break
    except Exception:
        continue

if PIECE_FONT is None:
    PIECE_FONT = pygame.font.Font(None, int(SQUARE_SIZE * 0.8))

UI_FONT = pygame.font.SysFont("Segoe UI", 24) or pygame.font.Font(None, 24)
BIG_UI_FONT = pygame.font.SysFont("Segoe UI", 40) or pygame.font.Font(None, 40)


# ---------------------------
# Board Setup
# ---------------------------

def initial_board() -> Board:
    board: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    # Place pieces
    placement = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    # White back rank (row 7), pawns row 6
    for c, k in enumerate(placement):
        board[7][c] = Piece(k, 'w')
    for c in range(COLS):
        board[6][c] = Piece('P', 'w')
    # Black back rank (row 0), pawns row 1
    for c, k in enumerate(placement):
        board[0][c] = Piece(k, 'b')
    for c in range(COLS):
        board[1][c] = Piece('P', 'b')
    return board


# ---------------------------
# Helpers
# ---------------------------

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def find_king(board: Board, color: str) -> Tuple[int, int]:
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece and piece.kind == 'K' and piece.color == color:
                return (r, c)
    return (-1, -1)


def clone_board(board: Board) -> Board:
    newb: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p:
                newb[r][c] = Piece(p.kind, p.color)
    return newb


# ---------------------------
# Move Generation (Pseudo-legal)
# ---------------------------

def pawn_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    promotion_row = 0 if color == 'w' else 7

    # Forward 1
    r1, c1 = r + dir, c
    if in_bounds(r1, c1) and board[r1][c1] is None:
        if r1 == promotion_row:
            moves.append((r, c, r1, c1, 'Q'))
        else:
            moves.append((r, c, r1, c1, None))
        # Forward 2 from start
        r2 = r + 2 * dir
        if r == start_row and board[r2][c1] is None:
            moves.append((r, c, r2, c1, None))

    # Captures
    for dc in (-1, 1):
        rr, cc = r + dir, c + dc
        if in_bounds(rr, cc) and board[rr][cc] is not None and board[rr][cc].color != color:
            if rr == promotion_row:
                moves.append((r, c, rr, cc, 'Q'))
            else:
                moves.append((r, c, rr, cc, None))

    # No en passant for simplicity
    return moves


def sliding_moves(board: Board, r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    res: List[Move] = []
    for dr, dc in directions:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            if board[rr][cc] is None:
                res.append((r, c, rr, cc, None))
            else:
                if board[rr][cc].color != color:
                    res.append((r, c, rr, cc, None))
                break
            rr += dr
            cc += dc
    return res


def knight_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    res: List[Move] = []
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc) and (board[rr][cc] is None or board[rr][cc].color != color):
            res.append((r, c, rr, cc, None))
    return res


def king_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    res: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and (board[rr][cc] is None or board[rr][cc].color != color):
                res.append((r, c, rr, cc, None))
    # Castling not implemented
    return res


def generate_pseudo_legal(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p or p.color != color:
                continue
            if p.kind == 'P':
                moves.extend(pawn_moves(board, r, c, color))
            elif p.kind == 'R':
                moves.extend(sliding_moves(board, r, c, color, [(1, 0), (-1, 0), (0, 1), (0, -1)]))
            elif p.kind == 'B':
                moves.extend(sliding_moves(board, r, c, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)]))
            elif p.kind == 'Q':
                moves.extend(sliding_moves(board, r, c, color,
                                           [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]))
            elif p.kind == 'N':
                moves.extend(knight_moves(board, r, c, color))
            elif p.kind == 'K':
                moves.extend(king_moves(board, r, c, color))
    return moves


# ---------------------------
# Check Detection and Legal Move Filtering
# ---------------------------

def apply_move(board: Board, move: Move) -> Board:
    r1, c1, r2, c2, promo = move
    newb = clone_board(board)
    piece = newb[r1][c1]
    newb[r1][c1] = None
    if promo and piece and piece.kind == 'P':
        newb[r2][c2] = Piece(promo, piece.color)
    else:
        newb[r2][c2] = piece
    return newb


def square_attacked_by(board: Board, r: int, c: int, attacker_color: str) -> bool:
    # Generate pseudo-legal moves for attacker and see if any reaches (r, c)
    # Slightly optimized by checking patterns
    # Pawns
    dir = -1 if attacker_color == 'w' else 1
    for dc in (-1, 1):
        rr, cc = r - dir, c - dc  # reverse because we want squares that attack (r,c)
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p.color == attacker_color and p.kind == 'P':
                return True

    # Knights
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p.color == attacker_color and p.kind == 'N':
                return True

    # Kings (adjacent squares)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                p = board[rr][cc]
                if p and p.color == attacker_color and p.kind == 'K':
                    return True

    # Sliding pieces: rooks/queens (orthogonal), bishops/queens (diagonal)
    # Orthogonal
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            p = board[rr][cc]
            if p:
                if p.color == attacker_color and (p.kind == 'R' or p.kind == 'Q'):
                    return True
                break
            rr += dr
            cc += dc
    # Diagonal
    for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            p = board[rr][cc]
            if p:
                if p.color == attacker_color and (p.kind == 'B' or p.kind == 'Q'):
                    return True
                break
            rr += dr
            cc += dc

    return False


def is_in_check(board: Board, color: str) -> bool:
    kr, kc = find_king(board, color)
    if kr == -1:
        return False
    opponent = 'b' if color == 'w' else 'w'
    return square_attacked_by(board, kr, kc, opponent)


def generate_legal_moves(board: Board, color: str) -> List[Move]:
    legal: List[Move] = []
    for move in generate_pseudo_legal(board, color):
        newb = apply_move(board, move)
        if not is_in_check(newb, color):
            legal.append(move)
    return legal


# ---------------------------
# AI (Random Move)
# ---------------------------

def ai_select_move(board: Board, color: str) -> Optional[Move]:
    moves = generate_legal_moves(board, color)
    if not moves:
        return None
    # Slightly prefer captures by shuffling then sorting
    random.shuffle(moves)
    def capture_score(m: Move) -> int:
        r1, c1, r2, c2, _ = m
        target = board[r2][c2]
        return 1 if target is not None else 0
    moves.sort(key=capture_score, reverse=True)
    return moves[0]


# ---------------------------
# Rendering
# ---------------------------

def draw_board(board: Board, selected: Optional[Tuple[int, int]], legal_moves_for_selected: List[Tuple[int, int]], turn: str, game_over_text: Optional[str]):
    # Draw squares
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
            pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Highlight legal moves for selected
    for (rr, cc) in legal_moves_for_selected:
        rect = pygame.Rect(cc * SQUARE_SIZE, rr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((*HIGHLIGHT_MOVE, 100))
        screen.blit(s, rect.topleft)

    # Highlight selected square
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_SELECT, rect, 4)

    # Highlight check on current player's king
    if is_in_check(board, turn):
        kr, kc = find_king(board, turn)
        rect = pygame.Rect(kc * SQUARE_SIZE, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_CHECK, rect, 6)

    # Draw pieces
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p:
                continue
            center = (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2)
            draw_piece(p, center)

    # Game status overlay if game over
    if game_over_text:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        screen.blit(overlay, (0, 0))
        text_surf = BIG_UI_FONT.render(game_over_text, True, (255, 255, 255))
        screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def draw_piece(piece: Piece, center: Tuple[int, int]):
    glyph_map = UNICODE_WHITE if piece.color == 'w' else UNICODE_BLACK
    glyph = glyph_map.get(piece.kind, '?')
    try:
        surf = PIECE_FONT.render(glyph, True, (0, 0, 0))
        # Simple shadow
        shadow = PIECE_FONT.render(glyph, True, (255, 255, 255))
        rect = surf.get_rect(center=center)
        srect = shadow.get_rect(center=(center[0] + 2, center[1] + 2))
        screen.blit(shadow, srect)
        screen.blit(surf, rect)
    except Exception:
        # Fallback: draw simple shapes/letters
        color = (20, 20, 20) if piece.color == 'b' else (240, 240, 240)
        radius = int(SQUARE_SIZE * 0.35)
        pygame.draw.circle(screen, color, center, radius)
        label = UI_FONT.render(piece.kind, True, (0, 0, 0) if piece.color == 'w' else (255, 255, 255))
        screen.blit(label, label.get_rect(center=center))


# ---------------------------
# Game State and Loop
# ---------------------------

def has_any_legal_moves(board: Board, color: str) -> bool:
    return len(generate_legal_moves(board, color)) > 0


def game_status_text(board: Board, turn: str) -> Optional[str]:
    opponent = 'b' if turn == 'w' else 'w'
    # If it's the current turn's move and no legal moves
    legal = generate_legal_moves(board, turn)
    if not legal:
        if is_in_check(board, turn):
            # The side to move is checkmated; opponent wins
            return "Checkmate! " + ("White" if opponent == 'w' else "Black") + " wins"
        else:
            return "Stalemate"
    return None


def run_game():
    board = initial_board()
    turn = 'w'  # white moves first
    selected: Optional[Tuple[int, int]] = None
    legal_moves_cache: List[Move] = []
    legal_squares_for_selected: List[Tuple[int, int]] = []
    game_over_text: Optional[str] = None

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over_text is None:
                mx, my = event.pos
                r, c = my // SQUARE_SIZE, mx // SQUARE_SIZE
                if turn == 'w':
                    if selected is None:
                        # Select a white piece
                        p = board[r][c]
                        if p and p.color == 'w':
                            selected = (r, c)
                            legal_moves_cache = generate_legal_moves(board, 'w')
                            legal_squares_for_selected = [(m[2], m[3]) for m in legal_moves_cache if m[0] == r and m[1] == c]
                    else:
                        sr, sc = selected
                        # If clicking the same color piece, reselect
                        p = board[r][c]
                        if p and p.color == 'w' and (r, c) != (sr, sc):
                            selected = (r, c)
                            legal_moves_cache = generate_legal_moves(board, 'w')
                            legal_squares_for_selected = [(m[2], m[3]) for m in legal_moves_cache if m[0] == r and m[1] == c]
                        else:
                            # Attempt to move
                            chosen: Optional[Move] = None
                            for m in legal_moves_cache:
                                if m[0] == sr and m[1] == sc and m[2] == r and m[3] == c:
                                    chosen = m
                                    break
                            if chosen:
                                board = apply_move(board, chosen)
                                turn = 'b'
                                selected = None
                                legal_moves_cache = []
                                legal_squares_for_selected = []
                                # After white move, check if game ended
                                game_over_text = game_status_text(board, turn)
                            else:
                                # Deselect if clicked elsewhere
                                selected = None
                                legal_moves_cache = []
                                legal_squares_for_selected = []

        # AI move if black to move and not game over
        if game_over_text is None and turn == 'b':
            # Simple delay could be added; for now, instant move
            move = ai_select_move(board, 'b')
            if move is None:
                # No legal moves -> checkmate or stalemate from black's perspective
                game_over_text = game_status_text(board, turn)
            else:
                board = apply_move(board, move)
                turn = 'w'
                game_over_text = game_status_text(board, turn)

        # Draw
        draw_board(board, selected, legal_squares_for_selected, turn, game_over_text)
        pygame.display.flip()


if __name__ == "__main__":
    try:
        run_game()
    except SystemExit:
        pass
