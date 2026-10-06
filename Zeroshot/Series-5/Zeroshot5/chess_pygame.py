import sys
import random
import pygame
from typing import List, Tuple, Optional, Dict

# ==========================
# Config
# ==========================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE = WIDTH // COLS
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (50, 50, 50)
SELECT_OUTLINE = (255, 215, 0)
TEXT_COLOR = (10, 10, 10)
BG = (30, 30, 30)

# AI settings
AI_DELAY_MS = 350

# Piece definitions
# White: uppercase; Black: lowercase in board representation for simplicity
# We'll also keep (type, color) dict for clarity in rendering.

Piece = Dict[str, str]  # { 'type': 'KQRBNP', 'color': 'w' or 'b' }
Board = List[List[Optional[Piece]]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]  # ((r1,c1), (r2,c2))

# ==========================
# Utilities
# ==========================

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def deep_copy_board(board: Board) -> Board:
    new_board: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p is None:
                new_board[r][c] = None
            else:
                new_board[r][c] = {'type': p['type'], 'color': p['color']}
    return new_board


# ==========================
# Chess Logic
# ==========================

def initial_board() -> Board:
    board: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def put(r, c, t, color):
        board[r][c] = {'type': t, 'color': color}

    # Place pawns
    for c in range(COLS):
        put(6, c, 'P', 'w')
        put(1, c, 'P', 'b')

    # Rooks
    put(7, 0, 'R', 'w'); put(7, 7, 'R', 'w')
    put(0, 0, 'R', 'b'); put(0, 7, 'R', 'b')

    # Knights
    put(7, 1, 'N', 'w'); put(7, 6, 'N', 'w')
    put(0, 1, 'N', 'b'); put(0, 6, 'N', 'b')

    # Bishops
    put(7, 2, 'B', 'w'); put(7, 5, 'B', 'w')
    put(0, 2, 'B', 'b'); put(0, 5, 'B', 'b')

    # Queens
    put(7, 3, 'Q', 'w')
    put(0, 3, 'Q', 'b')

    # Kings
    put(7, 4, 'K', 'w')
    put(0, 4, 'K', 'b')

    return board


def find_king(board: Board, color: str) -> Optional[Tuple[int, int]]:
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p and p['type'] == 'K' and p['color'] == color:
                return (r, c)
    return None


def squares_attacked_by(board: Board, color: str) -> List[Tuple[int, int]]:
    # Generate all squares attacked by color (pseudo-legal, no self-check concern)
    attacked = set()

    # Directions
    rook_dirs = [(-1,0), (1,0), (0,-1), (0,1)]
    bishop_dirs = [(-1,-1), (-1,1), (1,-1), (1,1)]

    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p or p['color'] != color:
                continue
            t = p['type']

            if t == 'P':
                dir_forward = -1 if color == 'w' else 1
                for dc in (-1, 1):
                    rr, cc = r + dir_forward, c + dc
                    if in_bounds(rr, cc):
                        attacked.add((rr, cc))

            elif t == 'N':
                for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
                    rr, cc = r + dr, c + dc
                    if in_bounds(rr, cc):
                        attacked.add((rr, cc))

            elif t == 'K':
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr == 0 and dc == 0:
                            continue
                        rr, cc = r + dr, c + dc
                        if in_bounds(rr, cc):
                            attacked.add((rr, cc))

            elif t == 'R':
                for dr, dc in rook_dirs:
                    rr, cc = r + dr, c + dc
                    while in_bounds(rr, cc):
                        attacked.add((rr, cc))
                        if board[rr][cc] is not None:
                            break
                        rr += dr; cc += dc

            elif t == 'B':
                for dr, dc in bishop_dirs:
                    rr, cc = r + dr, c + dc
                    while in_bounds(rr, cc):
                        attacked.add((rr, cc))
                        if board[rr][cc] is not None:
                            break
                        rr += dr; cc += dc

            elif t == 'Q':
                for dr, dc in rook_dirs + bishop_dirs:
                    rr, cc = r + dr, c + dc
                    while in_bounds(rr, cc):
                        attacked.add((rr, cc))
                        if board[rr][cc] is not None:
                            break
                        rr += dr; cc += dc

    return list(attacked)


def is_in_check(board: Board, color: str) -> bool:
    king_pos = find_king(board, color)
    if king_pos is None:
        return False
    enemy = 'b' if color == 'w' else 'w'
    attacked = squares_attacked_by(board, enemy)
    return king_pos in attacked


def generate_pseudo_legal_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []

    def add_move(r1, c1, r2, c2):
        moves.append(((r1, c1), (r2, c2)))

    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p or p['color'] != color:
                continue
            t = p['type']

            if t == 'P':
                dir_forward = -1 if color == 'w' else 1
                start_row = 6 if color == 'w' else 1
                # one forward
                r1 = r + dir_forward
                if in_bounds(r1, c) and board[r1][c] is None:
                    add_move(r, c, r1, c)
                    # two forward from start
                    r2 = r + 2*dir_forward
                    if r == start_row and in_bounds(r2, c) and board[r2][c] is None:
                        add_move(r, c, r2, c)
                # captures
                for dc in (-1, 1):
                    cc = c + dc
                    rr = r + dir_forward
                    if in_bounds(rr, cc) and board[rr][cc] is not None and board[rr][cc]['color'] != color:
                        add_move(r, c, rr, cc)
                # No en passant in this simplified version

            elif t == 'N':
                for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
                    rr, cc = r + dr, c + dc
                    if not in_bounds(rr, cc):
                        continue
                    if board[rr][cc] is None or board[rr][cc]['color'] != color:
                        add_move(r, c, rr, cc)

            elif t in ('B', 'R', 'Q'):
                directions = []
                if t in ('B', 'Q'):
                    directions += [(-1,-1), (-1,1), (1,-1), (1,1)]
                if t in ('R', 'Q'):
                    directions += [(-1,0), (1,0), (0,-1), (0,1)]
                for dr, dc in directions:
                    rr, cc = r + dr, c + dc
                    while in_bounds(rr, cc):
                        if board[rr][cc] is None:
                            add_move(r, c, rr, cc)
                        else:
                            if board[rr][cc]['color'] != color:
                                add_move(r, c, rr, cc)
                            break
                        rr += dr; cc += dc

            elif t == 'K':
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr == 0 and dc == 0:
                            continue
                        rr, cc = r + dr, c + dc
                        if not in_bounds(rr, cc):
                            continue
                        if board[rr][cc] is None or board[rr][cc]['color'] != color:
                            add_move(r, c, rr, cc)
                # No castling in this simplified version

    return moves


def make_move(board: Board, move: Move) -> Board:
    (r1, c1), (r2, c2) = move
    new_board = deep_copy_board(board)
    piece = new_board[r1][c1]
    new_board[r1][c1] = None
    # Promotion: auto-queen if pawn reaches last rank
    if piece and piece['type'] == 'P':
        final_row = 0 if piece['color'] == 'w' else 7
        if r2 == final_row:
            new_board[r2][c2] = {'type': 'Q', 'color': piece['color']}
            return new_board
    new_board[r2][c2] = piece
    return new_board


def generate_legal_moves(board: Board, color: str) -> List[Move]:
    legal: List[Move] = []
    for m in generate_pseudo_legal_moves(board, color):
        nb = make_move(board, m)
        if not is_in_check(nb, color):
            legal.append(m)
    return legal


# ==========================
# AI
# ==========================

def ai_choose_move(board: Board) -> Optional[Move]:
    # Simple: choose random legal move for black; prefer captures if any
    color = 'b'
    moves = generate_legal_moves(board, color)
    if not moves:
        return None
    capture_moves = []
    for m in moves:
        (r1, c1), (r2, c2) = m
        if board[r2][c2] is not None:
            capture_moves.append(m)
    pool = capture_moves if capture_moves else moves
    return random.choice(pool)


# ==========================
# Rendering
# ==========================

UNICODE_PIECES = {
    ('K', 'w'): '♔', ('Q', 'w'): '♕', ('R', 'w'): '♖', ('B', 'w'): '♗', ('N', 'w'): '♘', ('P', 'w'): '♙',
    ('K', 'b'): '♚', ('Q', 'b'): '♛', ('R', 'b'): '♜', ('B', 'b'): '♝', ('N', 'b'): '♞', ('P', 'b'): '♟',
}


def pick_unicode_font(size: int) -> pygame.font.Font:
    # Try several fonts likely to contain chess glyphs
    candidates = [
        'segoeuisymbol', 'segoe ui symbol', 'segoeuiemoji', 'dejavusans', 'dejavu sans', 'arialunicodems',
        'notoemoji', 'symbola', 'cambria', 'timesnewroman', 'arial'
    ]
    available = set(pygame.font.get_fonts())
    for name in candidates:
        key = name.replace(' ', '')
        if key in available:
            try:
                return pygame.font.SysFont(name, size)
            except Exception:
                continue
    # Fallback default
    return pygame.font.SysFont(None, size)


def draw_board(screen: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQUARE, r * SQUARE, SQUARE, SQUARE))


def draw_selection(screen: pygame.Surface, selected: Optional[Tuple[int, int]]):
    if selected is None:
        return
    r, c = selected
    x, y = c * SQUARE, r * SQUARE
    pygame.draw.rect(screen, SELECT_OUTLINE, (x, y, SQUARE, SQUARE), width=4)


def draw_moves(screen: pygame.Surface, moves: List[Move], from_pos: Optional[Tuple[int, int]]):
    if from_pos is None:
        return
    fr, fc = from_pos
    for (r1, c1), (r2, c2) in moves:
        if (r1, c1) != (fr, fc):
            continue
        cx = c2 * SQUARE + SQUARE // 2
        cy = r2 * SQUARE + SQUARE // 2
        # draw a dot on destination squares
        pygame.draw.circle(screen, MOVE_DOT, (cx, cy), max(6, SQUARE // 10))


def draw_pieces(screen: pygame.Surface, board: Board, font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p:
                continue
            glyph = UNICODE_PIECES.get((p['type'], p['color']))
            if glyph:
                text = font.render(glyph, True, TEXT_COLOR)
                rect = text.get_rect(center=(c * SQUARE + SQUARE // 2, r * SQUARE + SQUARE // 2))
                screen.blit(text, rect)
            else:
                # Fallback: draw simple shapes for pieces in case glyph missing
                center = (c * SQUARE + SQUARE // 2, r * SQUARE + SQUARE // 2)
                color = (240, 240, 240) if p['color'] == 'w' else (20, 20, 20)
                pygame.draw.circle(screen, color, center, SQUARE // 3)


def draw_status_bar(screen: pygame.Surface, info: str, font_small: pygame.font.Font):
    bar_h = 28
    rect = pygame.Rect(0, HEIGHT - bar_h, WIDTH, bar_h)
    pygame.draw.rect(screen, BG, rect)
    text = font_small.render(info, True, (230, 230, 230))
    screen.blit(text, (10, HEIGHT - bar_h + 5))


# ==========================
# Interaction
# ==========================

def pos_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    if y >= HEIGHT:
        return None
    c = x // SQUARE
    r = y // SQUARE
    if in_bounds(r, c):
        return (r, c)
    return None


# ==========================
# Main Game
# ==========================

def main():
    pygame.init()
    pygame.display.set_caption('Pygame Chess - Unicode, No Images')
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 0))
    clock = pygame.time.Clock()

    # Fonts
    piece_font = pick_unicode_font(int(SQUARE * 0.8))
    info_font = pygame.font.SysFont('consolas', 18)

    board = initial_board()
    turn = 'w'  # White moves first (human)
    selected: Optional[Tuple[int, int]] = None
    legal_moves_cache: List[Move] = []
    info = 'White to move. Click a piece, then a destination.'

    ai_pending = False
    ai_timer_start = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'w' and not ai_pending:
                    pos = pos_from_mouse(event.pos)
                    if pos is None:
                        continue
                    r, c = pos
                    if selected is None:
                        # select a white piece
                        p = board[r][c]
                        if p and p['color'] == 'w':
                            selected = (r, c)
                            legal_moves_cache = generate_legal_moves(board, 'w')
                        else:
                            selected = None
                            legal_moves_cache = []
                    else:
                        # attempt move
                        cand = (selected, (r, c))
                        legal_moves = [m for m in legal_moves_cache if m[0] == selected]
                        if cand in legal_moves:
                            board = make_move(board, cand)
                            turn = 'b'
                            selected = None
                            legal_moves_cache = []
                            info = 'Black thinking...'
                            ai_pending = True
                            ai_timer_start = pygame.time.get_ticks()
                        else:
                            # reselect if clicked own piece, else keep selection
                            p = board[r][c]
                            if p and p['color'] == 'w':
                                selected = (r, c)
                                legal_moves_cache = generate_legal_moves(board, 'w')
                            else:
                                # invalid target, keep selection
                                pass

        # AI move after delay
        if turn == 'b' and ai_pending:
            now = pygame.time.get_ticks()
            if now - ai_timer_start >= AI_DELAY_MS:
                m = ai_choose_move(board)
                if m is None:
                    info = 'Black has no legal moves.'
                    ai_pending = False
                    # Do not change turn; effectively stalemate or checkmate detection not implemented
                else:
                    board = make_move(board, m)
                    turn = 'w'
                    ai_pending = False
                    # Post-move check status
                    if is_in_check(board, 'w'):
                        info = 'Check on White! Your move.'
                    else:
                        info = 'White to move.'

        # Post human move, check status when it's human's turn
        if turn == 'w' and not ai_pending:
            if is_in_check(board, 'w'):
                info = 'Check on White! Your move.'

        # Draw
        screen.fill(BG)
        draw_board(screen)
        draw_selection(screen, selected)
        if selected is not None:
            draw_moves(screen, legal_moves_cache, selected)
        draw_pieces(screen, board, piece_font)
        draw_status_bar(screen, info, info_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
