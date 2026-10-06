import sys
import random
import pygame
from typing import List, Optional, Tuple

# =============================
# Config & Constants
# =============================
BOARD_SIZE = 8
TILE_SIZE = 80
MARGIN = 20
PANEL_HEIGHT = 60
WIDTH = TILE_SIZE * BOARD_SIZE + MARGIN * 2
HEIGHT = TILE_SIZE * BOARD_SIZE + MARGIN * 2 + PANEL_HEIGHT
FPS = 60

# Colors
LIGHT_SQ = (238, 238, 210)
DARK_SQ = (118, 150, 86)
SELECT_COLOR = (246, 246, 105)
MOVE_HINT = (186, 202, 68)
CAPTURE_HINT = (205, 92, 92)
LAST_MOVE = (246, 246, 105)
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)

# Players
WHITE = 'w'
BLACK = 'b'
HUMAN_COLOR = WHITE  # Human plays White by default
AI_COLOR = BLACK

# Piece values for AI heuristic
PIECE_VALUE = {
    'K': 0,  # we won't use king value for capture heuristic
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'P': 1,
}

# Unicode symbols for rendering pieces
UNICODE_PIECES = {
    (WHITE, 'K'): '\u2654',
    (WHITE, 'Q'): '\u2655',
    (WHITE, 'R'): '\u2656',
    (WHITE, 'B'): '\u2657',
    (WHITE, 'N'): '\u2658',
    (WHITE, 'P'): '\u2659',
    (BLACK, 'K'): '\u265A',
    (BLACK, 'Q'): '\u265B',
    (BLACK, 'R'): '\u265C',
    (BLACK, 'B'): '\u265D',
    (BLACK, 'N'): '\u265E',
    (BLACK, 'P'): '\u265F',
}

Piece = Optional[Tuple[str, str]]  # (color, type) e.g., ('w','P') or None
Board = List[List[Piece]]
Move = Tuple[int, int, int, int]  # (from_r, from_c, to_r, to_c)


def create_initial_board() -> Board:
    # Returns the initial chess setup as 8x8 list of tuples or None
    empty = [None] * BOARD_SIZE
    board: Board = [empty.copy() for _ in range(BOARD_SIZE)]

    # Place pieces - ranks from White perspective: row 7 is white back rank if top-left is (0,0)
    # We'll define row 0 as Black back rank at top, row 7 as White back rank at bottom.
    # Black pieces (top)
    board[0] = [
        (BLACK, 'R'), (BLACK, 'N'), (BLACK, 'B'), (BLACK, 'Q'),
        (BLACK, 'K'), (BLACK, 'B'), (BLACK, 'N'), (BLACK, 'R')
    ]
    board[1] = [(BLACK, 'P')] * BOARD_SIZE

    # Empty middle
    for r in range(2, 6):
        board[r] = [None] * BOARD_SIZE

    # White pieces (bottom)
    board[6] = [(WHITE, 'P')] * BOARD_SIZE
    board[7] = [
        (WHITE, 'R'), (WHITE, 'N'), (WHITE, 'B'), (WHITE, 'Q'),
        (WHITE, 'K'), (WHITE, 'B'), (WHITE, 'N'), (WHITE, 'R')
    ]
    return board


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def piece_color(p: Piece) -> Optional[str]:
    return p[0] if p else None


def is_enemy(p: Piece, color: str) -> bool:
    return p is not None and p[0] != color


def generate_pawn_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    direction = -1 if color == WHITE else 1  # White moves up (toward row 0), Black moves down
    start_row = 6 if color == WHITE else 1

    # one step forward
    nr, nc = r + direction, c
    if in_bounds(nr, nc) and board[nr][nc] is None:
        moves.append((nr, nc))
        # two steps from starting row if clear
        nr2 = r + 2 * direction
        if r == start_row and in_bounds(nr2, nc) and board[nr2][nc] is None:
            moves.append((nr2, nc))

    # captures
    for dc in (-1, 1):
        nr, nc = r + direction, c + dc
        if in_bounds(nr, nc) and is_enemy(board[nr][nc], color):
            moves.append((nr, nc))

    # En passant not implemented
    return moves


def generate_knight_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in deltas:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and piece_color(board[nr][nc]) != color:
            moves.append((nr, nc))
    return moves


def slide_moves(board: Board, r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] is None:
                moves.append((nr, nc))
            else:
                if is_enemy(board[nr][nc], color):
                    moves.append((nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def generate_king_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and piece_color(board[nr][nc]) != color:
                moves.append((nr, nc))
    # Castling not implemented
    return moves


def generate_moves_for_piece(board: Board, r: int, c: int) -> List[Tuple[int, int]]:
    piece = board[r][c]
    if piece is None:
        return []
    color, ptype = piece
    if ptype == 'P':
        return generate_pawn_moves(board, r, c, color)
    if ptype == 'N':
        return generate_knight_moves(board, r, c, color)
    if ptype == 'B':
        return slide_moves(board, r, c, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
    if ptype == 'R':
        return slide_moves(board, r, c, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])
    if ptype == 'Q':
        return slide_moves(board, r, c, color, [
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ])
    if ptype == 'K':
        return generate_king_moves(board, r, c, color)
    return []


def generate_all_moves(board: Board, color: str) -> List[Move]:
    all_moves: List[Move] = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p and p[0] == color:
                for (nr, nc) in generate_moves_for_piece(board, r, c):
                    all_moves.append((r, c, nr, nc))
    return all_moves


def make_move(board: Board, move: Move) -> Tuple[Piece, Optional[Tuple[int, int, Piece]]]:
    """
    Executes move on board in-place. Also handles pawn promotion to Queen automatically.
    Returns (captured_piece, promotion_info)
      - captured_piece: the piece that was on destination (if any)
      - promotion_info: (r, c, original_piece) if a promotion occurred; used for rendering/logging only
    """
    fr, fc, tr, tc = move
    moving = board[fr][fc]
    captured = board[tr][tc]
    board[tr][tc] = moving
    board[fr][fc] = None

    promo: Optional[Tuple[int, int, Piece]] = None
    if moving and moving[1] == 'P':
        if (moving[0] == WHITE and tr == 0) or (moving[0] == BLACK and tr == BOARD_SIZE - 1):
            # promote to Queen
            board[tr][tc] = (moving[0], 'Q')
            promo = (tr, tc, moving)
    return captured, promo


def evaluate_capture(piece: Piece) -> int:
    if piece is None:
        return 0
    return PIECE_VALUE.get(piece[1], 0)


def ai_choose_move(board: Board, color: str) -> Optional[Move]:
    moves = generate_all_moves(board, color)
    if not moves:
        return None
    # Choose the capture with highest value, else random
    best_val = -1
    best_moves: List[Move] = []
    for mv in moves:
        _, _, tr, tc = mv
        target = board[tr][tc]
        val = evaluate_capture(target)
        if val > best_val:
            best_val = val
            best_moves = [mv]
        elif val == best_val:
            best_moves.append(mv)
    return random.choice(best_moves)


# =============================
# Rendering
# =============================

def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font,
               selected: Optional[Tuple[int, int]], legal: List[Tuple[int, int]],
               last_move: Optional[Move], turn: str, status_text: str) -> None:
    screen.fill(BG_COLOR)
    # Draw board background
    board_rect = pygame.Rect(MARGIN, MARGIN, TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE)
    pygame.draw.rect(screen, (50, 50, 50), board_rect, border_radius=8)

    # Highlight last move
    if last_move:
        fr, fc, tr, tc = last_move
        for (rr, cc) in [(fr, fc), (tr, tc)]:
            x = MARGIN + cc * TILE_SIZE
            y = MARGIN + rr * TILE_SIZE
            pygame.draw.rect(screen, LAST_MOVE, (x, y, TILE_SIZE, TILE_SIZE))

    # Draw squares
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x = MARGIN + c * TILE_SIZE
            y = MARGIN + r * TILE_SIZE
            color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    # Highlight selected square
    if selected:
        sr, sc = selected
        x = MARGIN + sc * TILE_SIZE
        y = MARGIN + sr * TILE_SIZE
        pygame.draw.rect(screen, SELECT_COLOR, (x, y, TILE_SIZE, TILE_SIZE))

    # Highlight legal moves
    for (mr, mc) in legal:
        x = MARGIN + mc * TILE_SIZE
        y = MARGIN + mr * TILE_SIZE
        if board[mr][mc] is None:
            pygame.draw.rect(screen, MOVE_HINT, (x, y, TILE_SIZE, TILE_SIZE))
        else:
            pygame.draw.rect(screen, CAPTURE_HINT, (x, y, TILE_SIZE, TILE_SIZE))

    # Draw pieces
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p:
                sym = UNICODE_PIECES.get(p, '?')
                piece_surf = font.render(sym, True, (10, 10, 10))
                # Center in square
                rect = piece_surf.get_rect()
                rect.center = (
                    MARGIN + c * TILE_SIZE + TILE_SIZE // 2,
                    MARGIN + r * TILE_SIZE + TILE_SIZE // 2,
                )
                screen.blit(piece_surf, rect)

    # Bottom panel for status
    panel_rect = pygame.Rect(MARGIN, MARGIN + TILE_SIZE * BOARD_SIZE + 8, TILE_SIZE * BOARD_SIZE, PANEL_HEIGHT)
    pygame.draw.rect(screen, (45, 45, 45), panel_rect, border_radius=6)

    turn_text = f"Turn: {'White' if turn == WHITE else 'Black'}"
    turn_surf = font.render(turn_text, True, TEXT_COLOR)
    screen.blit(turn_surf, (panel_rect.x + 10, panel_rect.y + 10))

    status_surf = font.render(status_text, True, TEXT_COLOR)
    screen.blit(status_surf, (panel_rect.x + 200, panel_rect.y + 10))

    pygame.display.flip()


# =============================
# Input helpers
# =============================

def screen_to_board(mx: int, my: int) -> Optional[Tuple[int, int]]:
    if not (MARGIN <= mx < MARGIN + TILE_SIZE * BOARD_SIZE and MARGIN <= my < MARGIN + TILE_SIZE * BOARD_SIZE):
        return None
    c = (mx - MARGIN) // TILE_SIZE
    r = (my - MARGIN) // TILE_SIZE
    return int(r), int(c)


# =============================
# Main Game
# =============================

def run_game() -> None:
    pygame.init()
    pygame.display.set_caption('Pygame Chess - Human vs Simple AI')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Fonts: pick a large size to render Unicode nice and crisp
    piece_font = pygame.font.SysFont(None, int(TILE_SIZE * 0.8))

    board = create_initial_board()
    turn = WHITE  # White starts

    selected: Optional[Tuple[int, int]] = None
    legal_moves: List[Tuple[int, int]] = []
    last_move: Optional[Move] = None
    status_text: str = ""  # short info messages

    running = True
    while running:
        clock.tick(FPS)

        # If it's AI's turn, let AI move automatically
        if turn == AI_COLOR:
            pygame.event.pump()  # keep window responsive
            pygame.time.delay(200)  # small delay to look natural
            mv = ai_choose_move(board, AI_COLOR)
            if mv is None:
                status_text = 'AI has no legal moves. Game over.'
                running = False
            else:
                captured, _ = make_move(board, mv)
                last_move = mv
                selected = None
                legal_moves = []
                turn = HUMAN_COLOR
                if captured:
                    status_text = f"AI captured {captured[0].upper()}{captured[1]}"
                else:
                    status_text = "AI moved"

        # Handle events (mouse for human, quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and turn == HUMAN_COLOR:
                pos = pygame.mouse.get_pos()
                sq = screen_to_board(*pos)
                if sq is None:
                    # clicked outside board; clear selection
                    selected = None
                    legal_moves = []
                else:
                    r, c = sq
                    if selected is None:
                        # select if own piece
                        p = board[r][c]
                        if p and p[0] == HUMAN_COLOR:
                            selected = (r, c)
                            legal_moves = generate_moves_for_piece(board, r, c)
                        else:
                            selected = None
                            legal_moves = []
                    else:
                        sr, sc = selected
                        # if clicking same color piece, change selection
                        if board[r][c] and board[r][c][0] == HUMAN_COLOR:
                            selected = (r, c)
                            legal_moves = generate_moves_for_piece(board, r, c)
                        else:
                            # attempt move if within legal moves
                            if (r, c) in legal_moves:
                                mv: Move = (sr, sc, r, c)
                                captured, _ = make_move(board, mv)
                                last_move = mv
                                selected = None
                                legal_moves = []
                                turn = AI_COLOR
                                if captured:
                                    status_text = f"You captured {captured[0].upper()}{captured[1]}"
                                else:
                                    status_text = "You moved"
                            else:
                                # invalid target; clear selection
                                selected = None
                                legal_moves = []

        draw_board(screen, board, piece_font, selected, legal_moves, last_move, turn, status_text)

    # End screen simple pause
    end_font = pygame.font.SysFont(None, 36)
    end_msg = end_font.render('Game Over - Close window', True, (255, 255, 255))
    rect = end_msg.get_rect(center=(WIDTH // 2, HEIGHT - PANEL_HEIGHT // 2))
    screen.blit(end_msg, rect)
    pygame.display.flip()

    # Wait until quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    try:
        run_game()
    except ImportError as e:
        print('Missing dependency. Please install pygame:')
        print('  pip install pygame')
        raise
