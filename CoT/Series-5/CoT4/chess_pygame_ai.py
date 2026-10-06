import sys
import random
import pygame
from typing import List, Tuple, Optional

# ---- Configs ----
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ = WIDTH // COLS
FPS = 60

# Colors
LIGHT = (238, 238, 210)  # light squares
DARK = (118, 150, 86)     # dark squares
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (50, 50, 50)
SELECT_OUTLINE = (255, 215, 0)
TEXT_COLOR = (20, 20, 20)
BG_PANEL = (245, 245, 245)

# Unicode mapping for pieces
UNICODE_PIECES = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
    'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
}

# Material values for a simple evaluation (used by AI to prefer captures)
VALUES = {
    'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'P': 1,
    'k': 0, 'q': 9, 'r': 5, 'b': 3, 'n': 3, 'p': 1,
}

Board = List[List[str]]
Move = Tuple[int, int, int, int]  # (r1, c1, r2, c2)


def new_board() -> Board:
    """Return initial chess board as 8x8 list of strings. Uppercase=White, lowercase=Black."""
    # Note: row 0 at top, row increases downward. We'll have White at bottom (rows 6-7) moving up (r-1)
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def is_white(piece: str) -> bool:
    return piece.isupper()


def is_black(piece: str) -> bool:
    return piece.islower()


def side_of(piece: str) -> Optional[str]:
    if not piece or piece == '.':
        return None
    return 'w' if is_white(piece) else 'b'


def generate_moves(board: Board, side: str) -> List[Move]:
    """Generate pseudo-legal moves for the given side (no check verification)."""
    moves: List[Move] = []

    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            if side == 'w' and not is_white(piece):
                continue
            if side == 'b' and not is_black(piece):
                continue

            p = piece.lower()
            if p == 'p':
                moves.extend(gen_pawn(board, r, c, side))
            elif p == 'n':
                moves.extend(gen_knight(board, r, c, side))
            elif p == 'b':
                moves.extend(gen_bishop(board, r, c, side))
            elif p == 'r':
                moves.extend(gen_rook(board, r, c, side))
            elif p == 'q':
                moves.extend(gen_queen(board, r, c, side))
            elif p == 'k':
                moves.extend(gen_king(board, r, c, side))

    return moves


def gen_pawn(board: Board, r: int, c: int, side: str) -> List[Move]:
    moves: List[Move] = []
    dir = -1 if side == 'w' else 1
    start_row = 6 if side == 'w' else 1

    # Single push
    r1 = r + dir
    if in_bounds(r1, c) and board[r1][c] == '.':
        moves.append((r, c, r1, c))
        # Double push from start
        r2 = r + 2 * dir
        if r == start_row and in_bounds(r2, c) and board[r2][c] == '.' and board[r1][c] == '.':
            moves.append((r, c, r2, c))

    # Captures
    for dc in (-1, 1):
        cc = c + dc
        rr = r + dir
        if in_bounds(rr, cc):
            target = board[rr][cc]
            if target != '.' and side_of(target) and side_of(target) != side:
                moves.append((r, c, rr, cc))

    # Note: No en passant for simplicity
    return moves


def gen_knight(board: Board, r: int, c: int, side: str) -> List[Move]:
    moves: List[Move] = []
    jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in jumps:
        rr, cc = r + dr, c + dc
        if not in_bounds(rr, cc):
            continue
        target = board[rr][cc]
        if target == '.' or side_of(target) != side:
            moves.append((r, c, rr, cc))
    return moves


def slide_moves(board: Board, r: int, c: int, side: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            target = board[rr][cc]
            if target == '.':
                moves.append((r, c, rr, cc))
            else:
                if side_of(target) != side:
                    moves.append((r, c, rr, cc))
                break
            rr += dr
            cc += dc
    return moves


def gen_bishop(board: Board, r: int, c: int, side: str) -> List[Move]:
    dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    return slide_moves(board, r, c, side, dirs)


def gen_rook(board: Board, r: int, c: int, side: str) -> List[Move]:
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    return slide_moves(board, r, c, side, dirs)


def gen_queen(board: Board, r: int, c: int, side: str) -> List[Move]:
    dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    return slide_moves(board, r, c, side, dirs)


def gen_king(board: Board, r: int, c: int, side: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not in_bounds(rr, cc):
                continue
            target = board[rr][cc]
            if target == '.' or side_of(target) != side:
                moves.append((r, c, rr, cc))
    # No castling for simplicity
    return moves


def apply_move(board: Board, move: Move) -> Board:
    r1, c1, r2, c2 = move
    piece = board[r1][c1]
    new_b = [row.copy() for row in board]
    new_b[r1][c1] = '.'
    new_b[r2][c2] = piece

    # Pawn promotion (auto-queen)
    if piece == 'P' and r2 == 0:
        new_b[r2][c2] = 'Q'
    if piece == 'p' and r2 == ROWS - 1:
        new_b[r2][c2] = 'q'
    return new_b


def has_moves(board: Board, side: str) -> bool:
    return len(generate_moves(board, side)) > 0


# ---- AI ----

def ai_choose_move(board: Board, side: str) -> Optional[Move]:
    """Very simple AI: choose capture with highest value; otherwise random move."""
    moves = generate_moves(board, side)
    if not moves:
        return None

    best_moves: List[Move] = []
    best_score = -999
    for m in moves:
        r1, c1, r2, c2 = m
        target = board[r2][c2]
        score = 0
        if target != '.':
            # prefer capturing more valuable piece
            score = VALUES[target]
        if score > best_score:
            best_score = score
            best_moves = [m]
        elif score == best_score:
            best_moves.append(m)

    # if none is a capture (best_score==0), still pick randomly among them
    return random.choice(best_moves) if best_moves else random.choice(moves)


# ---- Rendering ----

def draw_board(screen: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQ, r * SQ, SQ, SQ))


def draw_highlights(screen: pygame.Surface, selected: Optional[Tuple[int, int]], legal_moves: List[Move]):
    # Selected square outline
    if selected is not None:
        r, c = selected
        pygame.draw.rect(screen, HIGHLIGHT, (c * SQ, r * SQ, SQ, SQ))

    # Moves
    for (r1, c1, r2, c2) in legal_moves:
        cx = c2 * SQ + SQ // 2
        cy = r2 * SQ + SQ // 2
        # draw small dot for moves
        pygame.draw.circle(screen, MOVE_DOT, (cx, cy), 8)


def draw_pieces(screen: pygame.Surface, board: Board, font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            glyph = UNICODE_PIECES[piece]
            surf = font.render(glyph, True, TEXT_COLOR)
            rect = surf.get_rect(center=(c * SQ + SQ // 2, r * SQ + SQ // 2))
            screen.blit(surf, rect)


def render_info_panel(screen: pygame.Surface, turn: str, font_small: pygame.font.Font, status_text: str = ""):
    # Draw a top info bar with text
    panel_rect = pygame.Rect(0, 0, WIDTH, 32)
    pygame.draw.rect(screen, BG_PANEL, panel_rect)

    turn_text = "Turn: White" if turn == 'w' else "Turn: Black"
    label = font_small.render(turn_text + (f"  {status_text}" if status_text else ""), True, (30, 30, 30))
    screen.blit(label, (8, 6))


# ---- Input Helpers ----

def mouse_to_square(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    if y < 32:  # info panel height
        return None
    y_adj = y - 32
    r = y_adj // SQ
    c = x // SQ
    if in_bounds(r, c):
        return (r, c)
    return None


# ---- Main Game ----

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 32))  # include top panel
    pygame.display.set_caption("Chess with Simple AI (Pygame)")

    # Fonts: large for pieces, small for info
    try:
        piece_font = pygame.font.SysFont("Segoe UI Symbol", SQ - 8)
    except Exception:
        piece_font = pygame.font.SysFont(None, SQ - 8)
    info_font = pygame.font.SysFont(None, 22)

    clock = pygame.time.Clock()

    board = new_board()
    turn = 'w'  # human white vs AI black

    selected: Optional[Tuple[int, int]] = None
    legal_for_selected: List[Move] = []

    running = True
    status_text = ""

    while running:
        clock.tick(FPS)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'w':  # human's turn
                    sq = mouse_to_square(pygame.mouse.get_pos())
                    if sq is None:
                        continue
                    r, c = sq
                    if selected is None:
                        piece = board[r][c]
                        if piece != '.' and is_white(piece):
                            selected = (r, c)
                            # compute legal moves for this piece only
                            all_moves = generate_moves(board, 'w')
                            legal_for_selected = [m for m in all_moves if m[0] == r and m[1] == c]
                        else:
                            selected = None
                            legal_for_selected = []
                    else:
                        # if click is a legal destination, make the move
                        made = False
                        for m in legal_for_selected:
                            if (m[2], m[3]) == (r, c):
                                board = apply_move(board, m)
                                turn = 'b'
                                selected = None
                                legal_for_selected = []
                                made = True
                                status_text = ""
                                break
                        if not made:
                            # maybe reselect your own piece
                            piece = board[r][c]
                            if piece != '.' and is_white(piece):
                                selected = (r, c)
                                all_moves = generate_moves(board, 'w')
                                legal_for_selected = [m for m in all_moves if m[0] == r and m[1] == c]
                            else:
                                selected = None
                                legal_for_selected = []

        # After human move, AI moves automatically
        if running and turn == 'b':
            pygame.time.delay(200)  # small delay for UX
            move = ai_choose_move(board, 'b')
            if move is None:
                status_text = "Black has no moves. Game over."
                turn = 'w'
            else:
                board = apply_move(board, move)
                turn = 'w'

        # Check end conditions (very basic): if a side has no legal moves
        if running:
            if not has_moves(board, 'w'):
                status_text = "White has no moves. Game over."
            if not has_moves(board, 'b'):
                if status_text:
                    status_text += " | Black has no moves."
                else:
                    status_text = "Black has no moves. Game over."

        # Render
        screen.fill((0, 0, 0))
        render_info_panel(screen, turn, info_font, status_text)

        # Chessboard area starts at y=32
        board_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_board(board_surface)
        if selected is not None:
            draw_highlights(board_surface, selected, legal_for_selected)
        draw_pieces(board_surface, board, piece_font)
        screen.blit(board_surface, (0, 32))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
