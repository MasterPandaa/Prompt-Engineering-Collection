import sys
import copy
import pygame

# Config
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

# Colors
LIGHT = (234, 235, 200)
DARK = (119, 154, 88)
HIGHLIGHT = (246, 246, 105)
SELECT = (255, 213, 79)
MOVE_DOT = (66, 66, 66)
TEXT_WHITE = (245, 245, 245)
TEXT_BLACK = (20, 20, 20)
PANEL_BG = (30, 30, 30)

# Piece values for simple evaluation / greedy AI
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
}


def create_initial_board():
    # Using the user's format: lowercase = black, uppercase = white
    return [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ]


# Helpers

def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def is_empty(board, r, c):
    return board[r][c] == '.'


def get_color(piece):
    if piece == '.':
        return None
    return 'white' if piece.isupper() else 'black'


def is_enemy(p1, p2):
    if p1 == '.' or p2 == '.':
        return False
    return (p1.isupper() and p2.islower()) or (p1.islower() and p2.isupper())


def same_color(p1, p2):
    if p1 == '.' or p2 == '.':
        return False
    return (p1.isupper() and p2.isupper()) or (p1.islower() and p2.islower())


# Move generation per piece

def get_pawn_moves(board, r, c, color):
    moves = []
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1
    enemy_color = 'black' if color == 'white' else 'white'

    # forward one
    fr, fc = r + direction, c
    if in_bounds(fr, fc) and is_empty(board, fr, fc):
        moves.append((fr, fc))
        # forward two from start
        fr2 = r + 2*direction
        if r == start_row and is_empty(board, fr2, fc):
            moves.append((fr2, fc))

    # captures
    for dc in (-1, 1):
        tr, tc = r + direction, c + dc
        if in_bounds(tr, tc) and board[tr][tc] != '.' and get_color(board[tr][tc]) == enemy_color:
            moves.append((tr, tc))

    # no en passant in this basic version
    return moves


def get_knight_moves(board, r, c, color):
    moves = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in offsets:
        tr, tc = r + dr, c + dc
        if not in_bounds(tr, tc):
            continue
        target = board[tr][tc]
        if target == '.' or get_color(target) != color:
            moves.append((tr, tc))
    return moves


def slide_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        tr, tc = r + dr, c + dc
        while in_bounds(tr, tc):
            target = board[tr][tc]
            if target == '.':
                moves.append((tr, tc))
            else:
                if get_color(target) != color:
                    moves.append((tr, tc))
                break
            tr += dr
            tc += dc
    return moves


def get_bishop_moves(board, r, c, color):
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return slide_moves(board, r, c, color, dirs)


def get_rook_moves(board, r, c, color):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return slide_moves(board, r, c, color, dirs)


def get_queen_moves(board, r, c, color):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    return slide_moves(board, r, c, color, dirs)


def get_king_moves(board, r, c, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            tr, tc = r + dr, c + dc
            if not in_bounds(tr, tc):
                continue
            target = board[tr][tc]
            if target == '.' or get_color(target) != color:
                moves.append((tr, tc))
    # no castling in this basic version
    return moves


def get_moves_for_piece(board, r, c):
    piece = board[r][c]
    if piece == '.':
        return []
    color = get_color(piece)
    p = piece.lower()
    if p == 'p':
        return get_pawn_moves(board, r, c, color)
    if p == 'n':
        return get_knight_moves(board, r, c, color)
    if p == 'b':
        return get_bishop_moves(board, r, c, color)
    if p == 'r':
        return get_rook_moves(board, r, c, color)
    if p == 'q':
        return get_queen_moves(board, r, c, color)
    if p == 'k':
        return get_king_moves(board, r, c, color)
    return []


def get_all_moves(board, color):
    all_moves = []  # list of (from_r, from_c, to_r, to_c)
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.' or get_color(piece) != color:
                continue
            for (tr, tc) in get_moves_for_piece(board, r, c):
                # basic validation: do not capture own piece already guaranteed
                if same_color(piece, board[tr][tc]):
                    continue
                all_moves.append((r, c, tr, tc))
    return all_moves


def apply_move(board, move):
    r, c, tr, tc = move
    piece = board[r][c]
    captured = board[tr][tc]
    board[tr][tc] = piece
    board[r][c] = '.'

    # promotion: auto-queen
    if piece == 'P' and tr == 0:
        board[tr][tc] = 'Q'
    if piece == 'p' and tr == ROWS - 1:
        board[tr][tc] = 'q'
    return captured


def board_copy(board):
    return [row[:] for row in board]


def evaluate_board_material(board):
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == '.':
                continue
            v = PIECE_VALUES[p]
            score += v if p.isupper() else -v
    return score  # positive means advantage for white


# Greedy AI (depth 1): choose move maximizing own material after move

def choose_ai_move(board, color):
    best_score = None
    best_move = None

    moves = get_all_moves(board, color)
    if not moves:
        return None

    for m in moves:
        b2 = board_copy(board)
        apply_move(b2, m)
        score = evaluate_board_material(b2)
        # Black wants lower score, white wants higher
        signed_score = score if color == 'white' else -score
        if best_score is None or signed_score > best_score:
            best_score = signed_score
            best_move = m
    return best_move


# Drawing

def draw_board(screen):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_selection_and_moves(screen, selected, legal_moves):
    if selected is not None:
        r, c = selected
        pygame.draw.rect(screen, SELECT, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
    for (tr, tc) in legal_moves:
        cx = tc * SQ_SIZE + SQ_SIZE // 2
        cy = tr * SQ_SIZE + SQ_SIZE // 2
        pygame.draw.circle(screen, MOVE_DOT, (cx, cy), 8)


def draw_pieces(screen, board, font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            text_color = TEXT_WHITE if piece.isupper() else TEXT_BLACK
            # Display the character itself (e.g., 'P', 'p', etc.)
            label = font.render(piece, True, text_color)
            rect = label.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
            screen.blit(label, rect)


def main():
    pygame.init()
    pygame.display.set_caption("Chess (Pygame) - Human vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 44, bold=True)

    board = create_initial_board()
    turn = 'white'  # Human plays white

    selected = None  # (r, c) or None
    legal_moves = []  # list of (tr, tc) for selected piece

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'white':
                    mx, my = event.pos
                    c = mx // SQ_SIZE
                    r = my // SQ_SIZE
                    if not in_bounds(r, c):
                        continue
                    if selected is None:
                        # select a white piece
                        if board[r][c] != '.' and get_color(board[r][c]) == 'white':
                            selected = (r, c)
                            # compute legal moves
                            legal_moves = []
                            for (tr, tc) in get_moves_for_piece(board, r, c):
                                if not same_color(board[r][c], board[tr][tc]):
                                    legal_moves.append((tr, tc))
                    else:
                        # attempt to move to clicked square if legal
                        sr, sc = selected
                        if (r, c) in legal_moves:
                            apply_move(board, (sr, sc, r, c))
                            selected = None
                            legal_moves = []
                            turn = 'black'
                        else:
                            # reselect if clicked own piece
                            if board[r][c] != '.' and get_color(board[r][c]) == 'white':
                                selected = (r, c)
                                legal_moves = []
                                for (tr, tc) in get_moves_for_piece(board, r, c):
                                    if not same_color(board[r][c], board[tr][tc]):
                                        legal_moves.append((tr, tc))
                            else:
                                selected = None
                                legal_moves = []

        # AI move when it's black's turn
        if running and turn == 'black':
            ai_move = choose_ai_move(board, 'black')
            if ai_move is None:
                # no legal moves (very rare here since we don't consider check) -> switch back
                turn = 'white'
            else:
                apply_move(board, ai_move)
                turn = 'white'

        # Draw
        draw_board(screen)
        draw_selection_and_moves(screen, selected, legal_moves)
        draw_pieces(screen, board, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
