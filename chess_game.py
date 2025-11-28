import pygame
import sys
from typing import List, Tuple, Optional

# ----------------------
# Configurations
# ----------------------
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 60

LIGHT_COLOR = (240, 217, 181)  # light squares
DARK_COLOR = (181, 136, 99)     # dark squares
HIGHLIGHT_COLOR = (106, 168, 79)
MOVE_DOT_COLOR = (30, 30, 30)
TEXT_COLOR_WHITE = (20, 20, 20)
TEXT_COLOR_BLACK = (240, 240, 240)
UI_BG = (25, 25, 25)
UI_TEXT = (230, 230, 230)

# Piece values for evaluation (positive = white advantage)
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000,
}

Board = List[List[str]]
Move = Tuple[int, int, int, int]  # (from_r, from_c, to_r, to_c)


def create_initial_board() -> Board:
    # Lowercase = black, Uppercase = white
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


def is_empty(board: Board, r: int, c: int) -> bool:
    return board[r][c] == '.'


def piece_color(ch: str) -> Optional[str]:
    if ch == '.':
        return None
    return 'white' if ch.isupper() else 'black'


def is_enemy(board: Board, r: int, c: int, color: str) -> bool:
    pc = piece_color(board[r][c])
    return pc is not None and pc != color


def add_sliding_moves(board: Board, r: int, c: int, color: str, dirs: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    moves = []
    for dr, dc in dirs:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            if is_empty(board, rr, cc):
                moves.append((rr, cc))
            else:
                if is_enemy(board, rr, cc, color):
                    moves.append((rr, cc))
                break
            rr += dr
            cc += dc
    return moves


def get_pawn_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # single step
    nr, nc = r + direction, c
    if in_bounds(nr, nc) and is_empty(board, nr, nc):
        moves.append((nr, nc))
        # double step from start
        nr2 = r + 2 * direction
        if r == start_row and is_empty(board, nr2, nc):
            moves.append((nr2, nc))

    # captures
    for dc in (-1, 1):
        nr, nc = r + direction, c + dc
        if in_bounds(nr, nc) and is_enemy(board, nr, nc, color):
            moves.append((nr, nc))

    # Note: No en passant in this basic version
    return moves


def get_knight_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        if is_empty(board, nr, nc) or is_enemy(board, nr, nc, color):
            moves.append((nr, nc))
    return moves


def get_bishop_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    return add_sliding_moves(board, r, c, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


def get_rook_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    return add_sliding_moves(board, r, c, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])


def get_queen_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    return add_sliding_moves(board, r, c, color,
                             [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])


def get_king_moves(board: Board, r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            if is_empty(board, nr, nc) or is_enemy(board, nr, nc, color):
                moves.append((nr, nc))
    # Note: No castling in this basic version
    return moves


def get_moves_for_piece(board: Board, r: int, c: int) -> List[Tuple[int, int]]:
    ch = board[r][c]
    if ch == '.':
        return []
    color = piece_color(ch)
    assert color is not None
    if ch in ('P', 'p'):
        return get_pawn_moves(board, r, c, color)
    if ch in ('N', 'n'):
        return get_knight_moves(board, r, c, color)
    if ch in ('B', 'b'):
        return get_bishop_moves(board, r, c, color)
    if ch in ('R', 'r'):
        return get_rook_moves(board, r, c, color)
    if ch in ('Q', 'q'):
        return get_queen_moves(board, r, c, color)
    if ch in ('K', 'k'):
        return get_king_moves(board, r, c, color)
    return []


def generate_legal_moves(board: Board, color: str) -> List[Move]:
    # Basic legality: cannot capture own piece. No check-rule enforcement.
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            if piece_color(board[r][c]) == color:
                for (tr, tc) in get_moves_for_piece(board, r, c):
                    # ensure not capturing own piece (already covered in generators)
                    moves.append((r, c, tr, tc))
    return moves


def apply_move(board: Board, move: Move) -> Board:
    fr, fc, tr, tc = move
    newb = [row.copy() for row in board]
    piece = newb[fr][fc]
    newb[fr][fc] = '.'
    newb[tr][tc] = piece
    # Promotion simple: auto-queen on last rank
    if piece == 'P' and tr == 0:
        newb[tr][tc] = 'Q'
    if piece == 'p' and tr == ROWS - 1:
        newb[tr][tc] = 'q'
    return newb


def evaluate(board: Board) -> int:
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            ch = board[r][c]
            if ch in PIECE_VALUES:
                score += PIECE_VALUES[ch]
    return score


def has_king(board: Board, color: str) -> bool:
    target = 'K' if color == 'white' else 'k'
    return any(target in row for row in board)


def detect_game_over(board: Board, to_move: str) -> Optional[str]:
    # End if a king is captured, or no moves available
    if not has_king(board, 'white'):
        return 'Black wins (white king captured).'
    if not has_king(board, 'black'):
        return 'White wins (black king captured).'
    if len(generate_legal_moves(board, to_move)) == 0:
        return f'Stalemate: {to_move} has no moves.'
    return None


def ai_move_greedy(board: Board) -> Optional[Move]:
    # Black AI: choose move that minimizes evaluation (since eval is white-positive)
    moves = generate_legal_moves(board, 'black')
    if not moves:
        return None
    best_move = None
    best_score = float('inf')
    for mv in moves:
        nb = apply_move(board, mv)
        sc = evaluate(nb)
        if sc < best_score:
            best_score = sc
            best_move = mv
    return best_move


def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font,
               selected: Optional[Tuple[int, int]], valid_targets: List[Tuple[int, int]]):
    screen.fill(UI_BG)
    # Draw squares
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Highlight selected and valid moves
    if selected is not None:
        sr, sc = selected
        sel_rect = pygame.Rect(sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((255, 255, 0, 70))
        screen.blit(s, sel_rect.topleft)

    for (mr, mc) in valid_targets:
        cx = mc * SQUARE_SIZE + SQUARE_SIZE // 2
        cy = mr * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, MOVE_DOT_COLOR, (cx, cy), 8)

    # Draw pieces as text
    for r in range(ROWS):
        for c in range(COLS):
            ch = board[r][c]
            if ch == '.':
                continue
            piece_surface = font.render(ch, True, TEXT_COLOR_WHITE if ch.isupper() else TEXT_COLOR_BLACK)
            rect = piece_surface.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                  r * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(piece_surface, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess (Pygame) - Text Pieces')
    clock = pygame.time.Clock()

    # Choose a large, readable font
    font = pygame.font.SysFont('consolas', SQUARE_SIZE - 10, bold=True)

    board = create_initial_board()
    selected: Optional[Tuple[int, int]] = None
    valid_targets: List[Tuple[int, int]] = []
    to_move = 'white'  # human is white, AI is black
    running = True
    game_over_text: Optional[str] = None

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over_text is None:
                mx, my = event.pos
                r, c = my // SQUARE_SIZE, mx // SQUARE_SIZE
                if not in_bounds(r, c):
                    continue
                if to_move == 'white':
                    if selected is None:
                        # select a white piece
                        if piece_color(board[r][c]) == 'white':
                            selected = (r, c)
                            valid_targets = get_moves_for_piece(board, r, c)
                        else:
                            selected = None
                            valid_targets = []
                    else:
                        sr, sc = selected
                        if (r, c) in valid_targets:
                            # make move if legal (and not capturing own piece)
                            if piece_color(board[r][c]) != 'white':
                                board = apply_move(board, (sr, sc, r, c))
                                to_move = 'black'
                                selected = None
                                valid_targets = []
                                # Check end after player move
                                game_over_text = detect_game_over(board, to_move)
                        else:
                            # reselect if clicked own piece
                            if piece_color(board[r][c]) == 'white':
                                selected = (r, c)
                                valid_targets = get_moves_for_piece(board, r, c)
                            else:
                                selected = None
                                valid_targets = []

        # AI move
        if running and game_over_text is None and to_move == 'black':
            mv = ai_move_greedy(board)
            if mv is None:
                game_over_text = 'Stalemate: black has no moves.'
            else:
                board = apply_move(board, mv)
                to_move = 'white'
                game_over_text = detect_game_over(board, to_move)

        # Draw
        draw_board(screen, board, font, selected, valid_targets)

        # Game over banner
        if game_over_text is not None:
            overlay = pygame.Surface((WIDTH, 60))
            overlay.fill(UI_BG)
            screen.blit(overlay, (0, HEIGHT // 2 - 30))
            banner_font = pygame.font.SysFont('consolas', 28, bold=True)
            msg = banner_font.render(game_over_text + '  (Press ESC to quit)', True, UI_TEXT)
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
