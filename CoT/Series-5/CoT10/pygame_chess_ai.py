import sys
import random
import pygame

# Game configuration
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
MOVE_HINT = (106, 246, 105)
SELECTION = (255, 255, 0)
TEXT_COLOR = (20, 20, 20)
BG_PANEL = (30, 30, 30)

# Piece Unicode mapping
UNICODE_PIECES = {
    'wK': '\u2654', 'wQ': '\u2655', 'wR': '\u2656', 'wB': '\u2657', 'wN': '\u2658', 'wP': '\u2659',
    'bK': '\u265A', 'bQ': '\u265B', 'bR': '\u265C', 'bB': '\u265D', 'bN': '\u265E', 'bP': '\u265F'
}

# Piece values for AI capture priority
PIECE_VALUES = {
    'K': 10000,
    'Q': 900,
    'R': 500,
    'B': 330,
    'N': 320,
    'P': 100,
}

HUMAN_COLOR = 'w'  # White human
AI_COLOR = 'b'     # Black AI


def create_initial_board():
    # 8x8 board with strings like 'wP' or 'bK', or None
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    # Place pawns
    for c in range(COLS):
        board[6][c] = 'wP'
        board[1][c] = 'bP'

    # Place other pieces
    order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    for c, p in enumerate(order):
        board[7][c] = 'w' + p
        board[0][c] = 'b' + p

    return board


def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def is_empty(board, r, c):
    return in_bounds(r, c) and board[r][c] is None


def is_enemy(board, r, c, color):
    return in_bounds(r, c) and board[r][c] is not None and board[r][c][0] != color


def is_friend(board, r, c, color):
    return in_bounds(r, c) and board[r][c] is not None and board[r][c][0] == color


def generate_moves(board, color):
    moves = []  # each move: ((r, c), (nr, nc))
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece and piece[0] == color:
                moves.extend(generate_moves_for_piece(board, r, c))
    return moves


def generate_moves_for_piece(board, r, c):
    piece = board[r][c]
    if not piece:
        return []
    color, kind = piece[0], piece[1]

    if kind == 'P':
        return generate_pawn_moves(board, r, c, color)
    elif kind == 'N':
        return generate_knight_moves(board, r, c, color)
    elif kind == 'B':
        return generate_sliding_moves(board, r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)])
    elif kind == 'R':
        return generate_sliding_moves(board, r, c, color, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)])
    elif kind == 'Q':
        return generate_sliding_moves(board, r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])
    elif kind == 'K':
        return generate_king_moves(board, r, c, color)
    return []


def generate_pawn_moves(board, r, c, color):
    moves = []
    dir_step = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1

    # Forward 1
    nr = r + dir_step
    if in_bounds(nr, c) and board[nr][c] is None:
        moves.append(((r, c), (nr, c)))
        # Forward 2 from start
        nr2 = r + 2 * dir_step
        if r == start_row and board[nr2][c] is None:
            moves.append(((r, c), (nr2, c)))

    # Captures
    for dc in (-1, 1):
        nc = c + dc
        nr = r + dir_step
        if in_bounds(nr, nc) and is_enemy(board, nr, nc, color):
            moves.append(((r, c), (nr, nc)))

    return moves


def generate_knight_moves(board, r, c, color):
    moves = []
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        if not is_friend(board, nr, nc, color):
            moves.append(((r, c), (nr, nc)))
    return moves


def generate_sliding_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] is None:
                moves.append(((r, c), (nr, nc)))
            else:
                if is_enemy(board, nr, nc, color):
                    moves.append(((r, c), (nr, nc)))
                break
            nr += dr
            nc += dc
    return moves


def generate_king_moves(board, r, c, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            if not is_friend(board, nr, nc, color):
                moves.append(((r, c), (nr, nc)))
    return moves


def make_move(board, move):
    # Returns a new board after applying move. Handles basic promotion to Queen.
    (r, c), (nr, nc) = move
    piece = board[r][c]
    new_board = [row[:] for row in board]
    new_board[nr][nc] = piece
    new_board[r][c] = None

    # Pawn promotion (auto-queen)
    if piece and piece[1] == 'P':
        if (piece[0] == 'w' and nr == 0) or (piece[0] == 'b' and nr == ROWS - 1):
            new_board[nr][nc] = piece[0] + 'Q'
    return new_board


def get_captured_value(board, move):
    (_, _), (nr, nc) = move
    target = board[nr][nc]
    if target is None:
        return 0
    return PIECE_VALUES[target[1]]


def choose_ai_move(board, color):
    moves = generate_moves(board, color)
    if not moves:
        return None

    # Prefer highest capture value
    best_value = -1
    best_moves = []
    for mv in moves:
        value = get_captured_value(board, mv)
        if value > best_value:
            best_value = value
            best_moves = [mv]
        elif value == best_value:
            best_moves.append(mv)

    return random.choice(best_moves)


def draw_board(surface):
    surface.fill(BG_PANEL)
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(surface, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlights(surface, selected, moves_for_selected):
    if selected:
        sr, sc = selected
        # selection outline
        pygame.draw.rect(surface, SELECTION, (sc * SQ_SIZE, sr * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
        # move hints
        for (_, _), (mr, mc) in moves_for_selected:
            center = (mc * SQ_SIZE + SQ_SIZE // 2, mr * SQ_SIZE + SQ_SIZE // 2)
            pygame.draw.circle(surface, MOVE_HINT, center, SQ_SIZE // 8)


def draw_pieces(surface, board, font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece:
                text = UNICODE_PIECES[piece]
                img = font.render(text, True, TEXT_COLOR)
                rect = img.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                surface.blit(img, rect)


def pos_from_mouse(mx, my):
    c = mx // SQ_SIZE
    r = my // SQ_SIZE
    if in_bounds(r, c):
        return (r, c)
    return None


def filter_moves_from(board, r, c):
    all_moves = generate_moves_for_piece(board, r, c)
    return all_moves


def no_moves_left(board, color):
    return len(generate_moves(board, color)) == 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pygame Chess vs AI (Simple)')

    # Use a large font supporting Unicode chess glyphs
    # Try several common fonts across platforms, fallback to default
    candidate_fonts = [
        'Segoe UI Symbol',      # Windows
        'Arial Unicode MS',     # Windows/Office
        'Noto Sans Symbols2',   # Google Noto
        'DejaVu Sans',          # Linux/macOS
        None                    # default fallback
    ]
    chosen = None
    for fname in candidate_fonts:
        try:
            font = pygame.font.SysFont(fname, SQ_SIZE - 12)
            test_img = font.render(UNICODE_PIECES['wK'], True, (0, 0, 0))
            if test_img.get_width() > 0:
                chosen = fname
                break
        except Exception:
            continue
    if chosen is None:
        font = pygame.font.SysFont(None, SQ_SIZE - 12)

    clock = pygame.time.Clock()

    board = create_initial_board()
    current_turn = 'w'
    selected = None
    moves_for_selected = []
    running = True
    game_over = False
    winner_text = ''

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                if current_turn == HUMAN_COLOR:
                    pos = pos_from_mouse(*event.pos)
                    if not pos:
                        continue
                    r, c = pos
                    if selected is None:
                        # Select a piece if it belongs to the human
                        if board[r][c] and board[r][c][0] == HUMAN_COLOR:
                            selected = (r, c)
                            moves_for_selected = filter_moves_from(board, r, c)
                        else:
                            selected = None
                            moves_for_selected = []
                    else:
                        # Try to move if clicked destination matches available moves
                        possible = {(dst_r, dst_c): mv for (src, (dst_r, dst_c)) in moves_for_selected}
                        if (r, c) in possible:
                            mv = possible[(r, c)]
                            board = make_move(board, mv)
                            current_turn = AI_COLOR
                            selected = None
                            moves_for_selected = []
                        else:
                            # Re-select if clicking another own piece
                            if board[r][c] and board[r][c][0] == HUMAN_COLOR:
                                selected = (r, c)
                                moves_for_selected = filter_moves_from(board, r, c)
                            else:
                                # Deselect if invalid
                                selected = None
                                moves_for_selected = []

        # AI move when it's AI's turn
        if not game_over and current_turn == AI_COLOR:
            pygame.time.delay(150)  # small delay for UX
            mv = choose_ai_move(board, AI_COLOR)
            if mv is None:
                game_over = True
                winner_text = 'White wins! (Black has no moves)'
            else:
                board = make_move(board, mv)
                current_turn = HUMAN_COLOR
                if no_moves_left(board, HUMAN_COLOR):
                    game_over = True
                    winner_text = 'Black wins! (White has no moves)'

        # Render
        draw_board(screen)
        draw_highlights(screen, selected, moves_for_selected)
        draw_pieces(screen, board, font)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            end_font = pygame.font.SysFont('Arial', 36)
            msg = end_font.render(winner_text + '  (Press ESC to quit)', True, (255, 255, 255))
            rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(msg, rect)

        pygame.display.flip()

        # ESC to quit any time
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
