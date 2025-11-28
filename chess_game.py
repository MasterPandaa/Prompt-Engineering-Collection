import sys
import copy
import pygame

# Pygame Chess with text-rendered pieces
# Board representation: '.' empty, lowercase = black, uppercase = white
# Pieces: P, R, N, B, Q, K

WIDTH, HEIGHT = 640, 700  # extra space for UI text
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
MARGIN_TOP = HEIGHT - WIDTH

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
SELECT_COLOR = (246, 246, 105)
MOVE_COLOR = (106, 246, 105)
TAKE_COLOR = (240, 85, 85)
TEXT_COLOR = (20, 20, 20)
WHITE_PIECE_COLOR = (20, 20, 20)
BLACK_PIECE_COLOR = (20, 20, 20)

PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000,
}

FPS = 60


def init_board():
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


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def piece_color(ch):
    if ch == '.':
        return None
    return 'white' if ch.isupper() else 'black'


def is_empty(board, r, c):
    return board[r][c] == '.'


def is_enemy(board, r, c, color):
    pc = piece_color(board[r][c])
    return pc is not None and pc != color


def is_friend(board, r, c, color):
    pc = piece_color(board[r][c])
    return pc is not None and pc == color


def add_move_if_valid(board, moves, r, c, color):
    # Valid if empty or enemy; but never friend
    if not in_bounds(r, c):
        return False
    if is_friend(board, r, c, color):
        return False
    # Capture if enemy, quiet if empty
    moves.append((r, c))
    # For sliders: stop if enemy encountered
    return not is_empty(board, r, c)


def ray_moves(board, row, col, color, directions):
    result = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            if is_friend(board, r, c, color):
                break
            result.append((r, c))
            if not is_empty(board, r, c):
                break
            r += dr
            c += dc
    return result


def get_pawn_moves(board, row, col, color):
    moves = []
    dir_forward = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # forward 1
    r1, c1 = row + dir_forward, col
    if in_bounds(r1, c1) and is_empty(board, r1, c1):
        moves.append((r1, c1))
        # forward 2 from start
        r2 = row + 2 * dir_forward
        if row == start_row and in_bounds(r2, c1) and is_empty(board, r2, c1):
            moves.append((r2, c1))

    # captures
    for dc in (-1, 1):
        r, c = row + dir_forward, col + dc
        if in_bounds(r, c) and is_enemy(board, r, c, color):
            moves.append((r, c))

    # Note: no en passant for simplicity
    return moves


def get_knight_moves(board, row, col, color):
    moves = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in offsets:
        r, c = row + dr, col + dc
        if in_bounds(r, c) and not is_friend(board, r, c, color):
            moves.append((r, c))
    return moves


def get_bishop_moves(board, row, col, color):
    return ray_moves(board, row, col, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


def get_rook_moves(board, row, col, color):
    return ray_moves(board, row, col, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])


def get_queen_moves(board, row, col, color):
    return ray_moves(board, row, col, color,
                     [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])


def get_king_moves(board, row, col, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if in_bounds(r, c) and not is_friend(board, r, c, color):
                moves.append((r, c))
    # No castling for simplicity
    return moves


def generate_moves_for_piece(board, row, col):
    ch = board[row][col]
    if ch == '.':
        return []
    color = piece_color(ch)
    kind = ch.lower()
    if kind == 'p':
        return get_pawn_moves(board, row, col, color)
    if kind == 'n':
        return get_knight_moves(board, row, col, color)
    if kind == 'b':
        return get_bishop_moves(board, row, col, color)
    if kind == 'r':
        return get_rook_moves(board, row, col, color)
    if kind == 'q':
        return get_queen_moves(board, row, col, color)
    if kind == 'k':
        return get_king_moves(board, row, col, color)
    return []


def get_all_moves(board, color):
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == '.':
                continue
            if piece_color(board[r][c]) != color:
                continue
            targets = generate_moves_for_piece(board, r, c)
            for tr, tc in targets:
                moves.append(((r, c), (tr, tc)))
    return moves


def make_move(board, move):
    (r1, c1), (r2, c2) = move
    new_board = copy.deepcopy(board)
    piece = new_board[r1][c1]
    new_board[r1][c1] = '.'
    new_board[r2][c2] = piece
    # simple promotion to queen
    if piece == 'P' and r2 == 0:
        new_board[r2][c2] = 'Q'
    if piece == 'p' and r2 == 7:
        new_board[r2][c2] = 'q'
    return new_board


def evaluate_board(board):
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            ch = board[r][c]
            if ch != '.':
                score += PIECE_VALUES[ch]
    return score


def ai_choose_move(board, color='black'):
    # Depth-1 minimax (greedy): pick move that yields best eval for 'color'
    moves = get_all_moves(board, color)
    if not moves:
        return None
    best_move = None
    if color == 'white':
        best_score = -float('inf')
    else:
        best_score = float('inf')
    for mv in moves:
        b2 = make_move(board, mv)
        eval_score = evaluate_board(b2)
        if color == 'white':
            if eval_score > best_score:
                best_score = eval_score
                best_move = mv
        else:
            if eval_score < best_score:
                best_score = eval_score
                best_move = mv
    return best_move


def draw_board(screen, font, board, selected_sq, legal_targets, status_text):
    screen.fill((230, 230, 230))
    # draw squares
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            is_light = (r + c) % 2 == 0
            color = LIGHT_COLOR if is_light else DARK_COLOR
            rect = pygame.Rect(c * SQUARE_SIZE, MARGIN_TOP + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

    # highlight selected
    if selected_sq is not None:
        sr, sc = selected_sq
        sel_rect = pygame.Rect(sc * SQUARE_SIZE, MARGIN_TOP + sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, SELECT_COLOR, sel_rect, 5)

    # highlight legal targets
    for (tr, tc) in legal_targets:
        target_rect = pygame.Rect(tc * SQUARE_SIZE, MARGIN_TOP + tr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        if board[tr][tc] == '.':
            pygame.draw.rect(screen, MOVE_COLOR, target_rect, 5)
        else:
            pygame.draw.rect(screen, TAKE_COLOR, target_rect, 5)

    # draw pieces as letters
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            ch = board[r][c]
            if ch == '.':
                continue
            # Render uppercase letter for both; use color hinting if desired
            display_char = ch.upper()
            text_surface = font.render(display_char, True, WHITE_PIECE_COLOR if ch.isupper() else BLACK_PIECE_COLOR)
            text_rect = text_surface.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                      MARGIN_TOP + r * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(text_surface, text_rect)

    # top area for status
    header_rect = pygame.Rect(0, 0, WIDTH, MARGIN_TOP)
    pygame.draw.rect(screen, (245, 245, 245), header_rect)

    small_font = pygame.font.SysFont(None, 24)
    text = small_font.render(status_text, True, TEXT_COLOR)
    screen.blit(text, (10, (MARGIN_TOP - text.get_height()) // 2))

    pygame.display.flip()


def pos_to_square(pos):
    x, y = pos
    if y < MARGIN_TOP:
        return None
    col = x // SQUARE_SIZE
    row = (y - MARGIN_TOP) // SQUARE_SIZE
    if in_bounds(row, col):
        return (row, col)
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pygame Chess (Text Pieces)')
    clock = pygame.time.Clock()

    # Choose a big, legible font
    try:
        piece_font = pygame.font.SysFont('arial', SQUARE_SIZE - 10, bold=True)
    except Exception:
        piece_font = pygame.font.SysFont(None, SQUARE_SIZE - 10, bold=True)

    board = init_board()
    turn = 'white'  # human as white
    running = True

    selected_sq = None
    legal_targets = []
    status_text = 'Giliran: Putih (Anda). Klik bidak untuk bergerak.'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'white':
                    sq = pos_to_square(event.pos)
                    if sq is None:
                        selected_sq = None
                        legal_targets = []
                    else:
                        r, c = sq
                        if selected_sq is None:
                            # select piece if white
                            if board[r][c] != '.' and piece_color(board[r][c]) == 'white':
                                selected_sq = (r, c)
                                legal_targets = generate_moves_for_piece(board, r, c)
                            else:
                                selected_sq = None
                                legal_targets = []
                        else:
                            # attempt move
                            if sq in legal_targets:
                                move = (selected_sq, sq)
                                board = make_move(board, move)
                                turn = 'black'
                                status_text = 'Giliran: Hitam (AI).'
                            # reset selection regardless
                            selected_sq = None
                            legal_targets = []

        # AI move when it's black's turn
        if running and turn == 'black':
            pygame.time.delay(200)  # small delay for UX
            ai_mv = ai_choose_move(board, 'black')
            if ai_mv is None:
                status_text = 'Hitam tidak punya langkah. Game selesai.'
                turn = 'white'
            else:
                board = make_move(board, ai_mv)
                turn = 'white'
                status_text = 'Giliran: Putih (Anda).'

        draw_board(screen, piece_font, board, selected_sq, legal_targets, status_text)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
