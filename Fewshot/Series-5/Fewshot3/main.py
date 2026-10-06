import sys
import math
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_r

# Chess with Pygame (text-rendered pieces)
# Uppercase = White, Lowercase = Black, '.' = empty
# Basic rules implemented:
# - Legal moves per piece (no friendly capture, path blocking for sliders)
# - Pawns: single/double forward (from start), diagonal capture, promotion to Queen
# - No castling, no en passant, no check/checkmate enforcement (basic only)
# AI: Greedy depth-1 (evaluate captures / best resulting material score)

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

WHITE = (240, 240, 240)
BLACK = (40, 40, 40)
LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (186, 202, 68)
SELECTED = (246, 246, 105)
MOVE_HINT = (246, 246, 105, 120)

PIECE_TEXT_COLOR_WHITE = (240, 240, 240)
PIECE_TEXT_COLOR_BLACK = (20, 20, 20)

PIECE_SYMBOLS = {
    'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': 'P',
    'k': 'k', 'q': 'q', 'r': 'r', 'b': 'b', 'n': 'n', 'p': 'p',
}

PIECE_VALUES = {
    'K': 0, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'P': 100,
    'k': 0, 'q': 900, 'r': 500, 'b': 330, 'n': 320, 'p': 100,
}

START_BOARD = [
    list("rnbqkbnr"),
    list("pppppppp"),
    list("........"),
    list("........"),
    list("........"),
    list("........"),
    list("PPPPPPPP"),
    list("RNBQKBNR"),
]

def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def is_white(piece):
    return piece != '.' and piece.isupper()


def is_black(piece):
    return piece != '.' and piece.islower()


def side_of(piece):
    if piece == '.':
        return None
    return 'white' if piece.isupper() else 'black'


class GameState:
    def __init__(self):
        self.board = [row[:] for row in START_BOARD]
        self.turn = 'white'  # white moves first (human)
        self.selected = None  # (row, col)
        self.valid_moves_from_selected = []  # list of (r, c)
        self.move_history = []  # tuples: (from_r, from_c, to_r, to_c, captured, promo)

    def reset(self):
        self.board = [row[:] for row in START_BOARD]
        self.turn = 'white'
        self.selected = None
        self.valid_moves_from_selected = []
        self.move_history = []

    def piece_at(self, r, c):
        return self.board[r][c]

    def set_piece(self, r, c, val):
        self.board[r][c] = val

    def generate_all_moves(self, side):
        moves = []  # (from_r, from_c, to_r, to_c, promotion_char or None)
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p == '.':
                    continue
                if (side == 'white' and p.isupper()) or (side == 'black' and p.islower()):
                    pmoves = get_piece_moves(self.board, r, c, side)
                    for (tr, tc) in pmoves:
                        promo = None
                        if p in ('P', 'p'):
                            if p == 'P' and tr == 0:
                                promo = 'Q'
                            elif p == 'p' and tr == ROWS - 1:
                                promo = 'q'
                        moves.append((r, c, tr, tc, promo))
        return moves

    def make_move(self, from_r, from_c, to_r, to_c, promotion=None):
        piece = self.piece_at(from_r, from_c)
        captured = self.piece_at(to_r, to_c)
        self.set_piece(to_r, to_c, piece)
        self.set_piece(from_r, from_c, '.')
        promo_applied = None
        if promotion:
            self.set_piece(to_r, to_c, promotion)
            promo_applied = promotion
        self.move_history.append((from_r, from_c, to_r, to_c, captured, promo_applied))
        self.turn = 'black' if self.turn == 'white' else 'white'

    def undo_move(self):
        if not self.move_history:
            return
        from_r, from_c, to_r, to_c, captured, promo = self.move_history.pop()
        moved_piece = self.piece_at(to_r, to_c)
        # If promotion happened, the moved piece at destination is a promoted piece; restore original pawn
        if promo is not None:
            if promo == 'Q':
                original = 'P'
            elif promo == 'q':
                original = 'p'
            else:
                original = moved_piece
            self.set_piece(from_r, from_c, original)
        else:
            self.set_piece(from_r, from_c, moved_piece)
        self.set_piece(to_r, to_c, captured)
        self.turn = 'black' if self.turn == 'white' else 'white'

    def evaluate_material(self):
        # positive means advantage for white
        score = 0
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p == '.':
                    continue
                val = PIECE_VALUES[p.upper()]
                score += val if p.isupper() else -val
        return score


def get_piece_moves(board, row, col, side):
    piece = board[row][col]
    moves = []
    if piece == '.':
        return moves
    color = 'white' if piece.isupper() else 'black'
    if color != side:
        return moves

    p = piece.upper()
    if p == 'N':
        moves = get_knight_moves(board, row, col, color)
    elif p == 'B':
        moves = get_bishop_moves(board, row, col, color)
    elif p == 'R':
        moves = get_rook_moves(board, row, col, color)
    elif p == 'Q':
        moves = get_queen_moves(board, row, col, color)
    elif p == 'K':
        moves = get_king_moves(board, row, col, color)
    elif p == 'P':
        moves = get_pawn_moves(board, row, col, color)
    return moves


def add_move_if_valid(board, r, c, color, moves):
    if not in_bounds(r, c):
        return False
    target = board[r][c]
    if target == '.':
        moves.append((r, c))
        return True  # empty square, sliders can continue
    else:
        # Can capture enemy, but cannot move past
        if color == 'white' and target.islower():
            moves.append((r, c))
        elif color == 'black' and target.isupper():
            moves.append((r, c))
        return False


def get_knight_moves(board, row, col, color):
    moves = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, 1)]
    for r_off, c_off in offsets:
        r, c = row + r_off, col + c_off
        if not in_bounds(r, c):
            continue
        target = board[r][c]
        if target == '.' or (color == 'white' and target.islower()) or (color == 'black' and target.isupper()):
            moves.append((r, c))
    return moves


def get_bishop_moves(board, row, col, color):
    moves = []
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            if not add_move_if_valid(board, r, c, color, moves):
                break
            r += dr
            c += dc
    return moves


def get_rook_moves(board, row, col, color):
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            if not add_move_if_valid(board, r, c, color, moves):
                break
            r += dr
            c += dc
    return moves


def get_queen_moves(board, row, col, color):
    # queen = rook + bishop
    return (get_rook_moves(board, row, col, color) +
            get_bishop_moves(board, row, col, color))


def get_king_moves(board, row, col, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if not in_bounds(r, c):
                continue
            target = board[r][c]
            if target == '.' or (color == 'white' and target.islower()) or (color == 'black' and target.isupper()):
                moves.append((r, c))
    return moves


def get_pawn_moves(board, row, col, color):
    moves = []
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # single forward
    r1, c1 = row + direction, col
    if in_bounds(r1, c1) and board[r1][c1] == '.':
        moves.append((r1, c1))
        # double forward from starting rank
        r2 = row + 2 * direction
        if row == start_row and board[r2][c1] == '.':
            moves.append((r2, c1))

    # captures
    for dc in (-1, 1):
        rc, cc = row + direction, col + dc
        if not in_bounds(rc, cc):
            continue
        target = board[rc][cc]
        if target != '.':
            if color == 'white' and target.islower():
                moves.append((rc, cc))
            elif color == 'black' and target.isupper():
                moves.append((rc, cc))

    return moves


def ai_pick_move_greedy(state: GameState):
    # For black AI: choose the move that minimizes evaluation (white-positive score)
    best_move = None
    best_score = math.inf
    moves = state.generate_all_moves('black')
    # Simple ordering: consider captures first
    def move_gain(m):
        _, _, tr, tc, promo = m
        target = state.board[tr][tc]
        if target == '.':
            return 0
        return PIECE_VALUES[target.upper()]
    moves.sort(key=move_gain, reverse=True)

    for (fr, fc, tr, tc, promo) in moves:
        state.make_move(fr, fc, tr, tc, promo)
        score = state.evaluate_material()
        state.undo_move()
        if score < best_score:
            best_score = score
            best_move = (fr, fc, tr, tc, promo)
    return best_move


def draw_board(screen):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlights(screen, state: GameState):
    if state.selected:
        sr, sc = state.selected
        pygame.draw.rect(screen, SELECTED, (sc * SQ_SIZE, sr * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
        for (mr, mc) in state.valid_moves_from_selected:
            rect = pygame.Rect(mc * SQ_SIZE + SQ_SIZE // 4, mr * SQ_SIZE + SQ_SIZE // 4,
                               SQ_SIZE // 2, SQ_SIZE // 2)
            pygame.draw.ellipse(screen, HIGHLIGHT, rect, 3)


def draw_pieces(screen, font, state: GameState):
    for r in range(ROWS):
        for c in range(COLS):
            p = state.board[r][c]
            if p == '.':
                continue
            symbol = PIECE_SYMBOLS[p]
            color = PIECE_TEXT_COLOR_BLACK if p.isupper() else PIECE_TEXT_COLOR_WHITE
            text = font.render(symbol, True, color)
            text_rect = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
            screen.blit(text, text_rect)


def pos_to_square(pos):
    x, y = pos
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    return int(row), int(col)


def handle_click(state: GameState, pos):
    row, col = pos_to_square(pos)
    if not in_bounds(row, col):
        return

    if state.selected is None:
        p = state.board[row][col]
        if p != '.' and side_of(p) == state.turn:
            state.selected = (row, col)
            state.valid_moves_from_selected = get_piece_moves(state.board, row, col, state.turn)
            # filter out friendly-occupied targets (already handled in move gens, but safe)
    else:
        sr, sc = state.selected
        if (row, col) in state.valid_moves_from_selected:
            # Determine promotion
            piece = state.board[sr][sc]
            promo = None
            if piece == 'P' and row == 0:
                promo = 'Q'
            elif piece == 'p' and row == ROWS - 1:
                promo = 'q'
            state.make_move(sr, sc, row, col, promo)
            state.selected = None
            state.valid_moves_from_selected = []
        else:
            # reselect if clicked own piece
            p = state.board[row][col]
            if p != '.' and side_of(p) == state.turn:
                state.selected = (row, col)
                state.valid_moves_from_selected = get_piece_moves(state.board, row, col, state.turn)
            else:
                state.selected = None
                state.valid_moves_from_selected = []


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pygame Chess (Text)')
    clock = pygame.time.Clock()

    # Choose a legible mono font; fall back if not found
    try:
        font = pygame.font.SysFont('consolas', 44, bold=True)
    except Exception:
        font = pygame.font.SysFont(None, 44, bold=True)

    state = GameState()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_r:
                    state.reset()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if state.turn == 'white':
                    handle_click(state, event.pos)

        # AI move when it's black's turn
        if state.turn == 'black':
            ai_move = ai_pick_move_greedy(state)
            if ai_move is None:
                # no moves; just switch to white to avoid freeze
                state.turn = 'white'
            else:
                fr, fc, tr, tc, promo = ai_move
                state.make_move(fr, fc, tr, tc, promo)

        # Draw
        draw_board(screen)
        draw_highlights(screen, state)
        draw_pieces(screen, font, state)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
