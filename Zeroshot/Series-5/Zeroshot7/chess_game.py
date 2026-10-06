import sys
import random
import copy
import pygame

# ---------- Config ----------
BOARD_SIZE = 8
TILE_SIZE = 84
MARGIN = 40
PANEL_HEIGHT = 80
WIDTH = MARGIN * 2 + TILE_SIZE * BOARD_SIZE
HEIGHT = MARGIN * 2 + TILE_SIZE * BOARD_SIZE + PANEL_HEIGHT
FPS = 60

# Colors
WHITE = (240, 240, 240)
BLACK = (40, 40, 40)
GREEN = (97, 153, 59)
BEIGE = (232, 235, 239)
BROWN = (125, 135, 150)
BLUE = (70, 130, 180)
YELLOW = (246, 219, 112)
RED = (200, 60, 60)
DARK_RED = (160, 40, 40)
LIGHT_HL = (180, 220, 130)
DARK_HL = (120, 170, 90)

# Piece values for simple evaluation (if needed)
PIECE_VALUES = {
    'K': 0,
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'P': 1,
}

# Unicode symbols for pieces
UNICODE_WHITE = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'
}
UNICODE_BLACK = {
    'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'
}


class Piece:
    def __init__(self, kind: str, color: str):
        # kind in {'K','Q','R','B','N','P'}
        # color in {'w','b'}
        self.kind = kind
        self.color = color
        self.has_moved = False

    def __repr__(self):
        return f"{self.color}{self.kind}"


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def start_position():
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # Place pieces
    back = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    for c, k in enumerate(back):
        board[0][c] = Piece(k, 'b')
        board[7][c] = Piece(k, 'w')
    for c in range(BOARD_SIZE):
        board[1][c] = Piece('P', 'b')
        board[6][c] = Piece('P', 'w')
    return board


def clone_board(board):
    return copy.deepcopy(board)


def find_king(board, color):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p and p.color == color and p.kind == 'K':
                return r, c
    return None


def is_square_attacked(board, r, c, by_color):
    # Check if square (r,c) is attacked by by_color
    directions = {
        'N': [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
    }

    # Knights
    for dr, dc in directions['N']:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p.color == by_color and p.kind == 'N':
                return True

    # Pawns
    if by_color == 'w':
        pawn_dirs = [(-1, -1), (-1, 1)]
    else:
        pawn_dirs = [(1, -1), (1, 1)]
    for dr, dc in pawn_dirs:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc):
            p = board[rr][cc]
            if p and p.color == by_color and p.kind == 'P':
                return True

    # Kings (adjacent)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                p = board[rr][cc]
                if p and p.color == by_color and p.kind == 'K':
                    return True

    # Sliding pieces: R, B, Q
    sliders = [
        ('R', [(-1, 0), (1, 0), (0, -1), (0, 1)]),
        ('B', [(-1, -1), (-1, 1), (1, -1), (1, 1)]),
        ('Q', [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)])
    ]
    for kind, dirs in sliders:
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                p = board[rr][cc]
                if p:
                    if p.color == by_color and (p.kind == kind or (kind in 'RB' and p.kind == 'Q')):
                        return True
                    break
                rr += dr
                cc += dc

    return False


def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return False
    r, c = king_pos
    enemy = 'b' if color == 'w' else 'w'
    return is_square_attacked(board, r, c, enemy)


def gen_moves_for_piece(board, r, c):
    p = board[r][c]
    if not p:
        return []
    moves = []
    color = p.color
    enemy = 'b' if color == 'w' else 'w'

    if p.kind == 'P':
        dir_ = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        # Forward 1
        rr, cc = r + dir_, c
        if in_bounds(rr, cc) and board[rr][cc] is None:
            moves.append(((r, c), (rr, cc)))
            # Forward 2 from start
            rr2 = r + 2 * dir_
            if r == start_row and board[rr2][cc] is None:
                moves.append(((r, c), (rr2, cc)))
        # Captures
        for dc in (-1, 1):
            rr, cc = r + dir_, c + dc
            if in_bounds(rr, cc) and board[rr][cc] is not None and board[rr][cc].color == enemy:
                moves.append(((r, c), (rr, cc)))
        # Promotion handled at make_move time

    elif p.kind == 'N':
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                target = board[rr][cc]
                if target is None or target.color == enemy:
                    moves.append(((r, c), (rr, cc)))

    elif p.kind in ('B', 'R', 'Q'):
        dirs = []
        if p.kind in ('B', 'Q'):
            dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if p.kind in ('R', 'Q'):
            dirs += [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                target = board[rr][cc]
                if target is None:
                    moves.append(((r, c), (rr, cc)))
                else:
                    if target.color == enemy:
                        moves.append(((r, c), (rr, cc)))
                    break
                rr += dr
                cc += dc

    elif p.kind == 'K':
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc):
                    target = board[rr][cc]
                    if target is None or target.color == enemy:
                        moves.append(((r, c), (rr, cc)))
        # No castling in this implementation

    return moves


def apply_move(board, move):
    # Returns a new board with move applied and info about promotion
    (sr, sc), (dr, dc) = move
    nb = clone_board(board)
    piece = nb[sr][sc]
    nb[sr][sc] = None
    # Promotion auto to Queen if pawn reaches last rank
    if piece.kind == 'P' and (dr == 0 or dr == BOARD_SIZE - 1):
        # dr==0 means white promoted? Actually white moves up, so last rank is 0; black last rank is 7
        pass
    captured = nb[dr][dc]
    nb[dr][dc] = piece
    piece.has_moved = True

    # Handle promotion
    if piece.kind == 'P':
        if piece.color == 'w' and dr == 0:
            nb[dr][dc] = Piece('Q', 'w')
        elif piece.color == 'b' and dr == BOARD_SIZE - 1:
            nb[dr][dc] = Piece('Q', 'b')

    return nb


def legal_moves(board, color):
    # Generate moves that do not leave king in check
    pseudo = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p and p.color == color:
                for mv in gen_moves_for_piece(board, r, c):
                    pseudo.append(mv)

    legal = []
    for mv in pseudo:
        nb = apply_move(board, mv)
        if not is_in_check(nb, color):
            legal.append(mv)
    return legal


def simple_ai_choose_move(board, color):
    # Random legal move. If no moves return None
    moves = legal_moves(board, color)
    if not moves:
        return None
    # optional: prefer captures
    def capture_value(mv):
        (sr, sc), (dr, dc) = mv
        target = board[dr][dc]
        return PIECE_VALUES.get(target.kind, 0) if target else 0
    # 50% chance prefer best capture
    if random.random() < 0.5:
        best = sorted(moves, key=capture_value, reverse=True)
        if best and capture_value(best[0]) > 0:
            return best[0]
    return random.choice(moves)


# ---------- Rendering ----------

def init_fonts():
    # Try a few fonts that usually contain chess unicode
    pygame.font.init()
    candidates = [
        pygame.font.get_default_font(),
        'arial', 'segoeui', 'dejavusans', 'dejavu sans', 'noto sans symbols'
    ]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, int(TILE_SIZE * 0.7))
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, int(TILE_SIZE * 0.7))


def piece_to_text(piece):
    if not piece:
        return None
    if piece.color == 'w':
        return UNICODE_WHITE.get(piece.kind, piece.kind)
    return UNICODE_BLACK.get(piece.kind, piece.kind)


def draw_board(screen, board, ui_state, fonts):
    screen.fill(BLACK)

    # Board background
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x = MARGIN + c * TILE_SIZE
            y = MARGIN + r * TILE_SIZE
            is_light = (r + c) % 2 == 0
            color = BEIGE if is_light else GREEN
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    # Highlight legal moves for selected piece
    if ui_state['selected'] is not None:
        (sr, sc) = ui_state['selected']
        moves = ui_state['legal_moves']
        for (_, _), (dr, dc) in moves:
            x = MARGIN + dc * TILE_SIZE
            y = MARGIN + dr * TILE_SIZE
            # draw small circle or overlay
            center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
            radius = TILE_SIZE // 6
            pygame.draw.circle(screen, BLUE, center, radius)
        # highlight selected square
        x = MARGIN + sc * TILE_SIZE
        y = MARGIN + sr * TILE_SIZE
        pygame.draw.rect(screen, YELLOW, (x, y, TILE_SIZE, TILE_SIZE), 4, border_radius=6)

    # Highlight king in check
    for color in ('w', 'b'):
        if is_in_check(board, color):
            kr, kc = find_king(board, color)
            x = MARGIN + kc * TILE_SIZE
            y = MARGIN + kr * TILE_SIZE
            pygame.draw.rect(screen, RED, (x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8), 4, border_radius=6)

    # Draw pieces
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p:
                txt = piece_to_text(p)
                if txt:
                    surf = fonts.render(txt, True, BLACK if p.color == 'w' else WHITE)
                else:
                    surf = fonts.render(p.kind, True, BLACK if p.color == 'w' else WHITE)
                rect = surf.get_rect()
                x = MARGIN + c * TILE_SIZE + TILE_SIZE // 2 - rect.width // 2
                y = MARGIN + r * TILE_SIZE + TILE_SIZE // 2 - rect.height // 2
                screen.blit(surf, (x, y))

    # Panel
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - PANEL_HEIGHT, WIDTH, PANEL_HEIGHT))

    info_font = pygame.font.SysFont(None, 28)
    turn_text = 'White to move' if ui_state['turn'] == 'w' else 'Black (AI) to move'

    # Game state text
    white_moves = legal_moves(board, 'w')
    black_moves = legal_moves(board, 'b')
    status = ''
    if ui_state['turn'] == 'w' and not white_moves:
        status = 'Checkmate!' if is_in_check(board, 'w') else 'Stalemate.'
    elif ui_state['turn'] == 'b' and not black_moves:
        status = 'Checkmate!' if is_in_check(board, 'b') else 'Stalemate.'

    info1 = info_font.render(turn_text, True, WHITE)
    info2 = info_font.render('R: Restart  |  ESC: Quit', True, WHITE)
    info3 = info_font.render(status, True, YELLOW if 'mate' in status.lower() else WHITE)
    screen.blit(info1, (MARGIN, HEIGHT - PANEL_HEIGHT + 14))
    screen.blit(info2, (MARGIN, HEIGHT - PANEL_HEIGHT + 44))
    if status:
        sw = info3.get_rect().width
        screen.blit(info3, (WIDTH - MARGIN - sw, HEIGHT - PANEL_HEIGHT + 28))


# ---------- Game Loop ----------

def pos_from_mouse(mx, my):
    if mx < MARGIN or my < MARGIN:
        return None
    if mx >= MARGIN + TILE_SIZE * BOARD_SIZE or my >= MARGIN + TILE_SIZE * BOARD_SIZE:
        return None
    c = (mx - MARGIN) // TILE_SIZE
    r = (my - MARGIN) // TILE_SIZE
    return int(r), int(c)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess (Pygame, Unicode)')
    clock = pygame.time.Clock()

    fonts = init_fonts()

    board = start_position()
    ui_state = {
        'turn': 'w',
        'selected': None,  # (r,c) or None
        'legal_moves': [],  # legal moves for selected piece
        'game_over': False,
    }

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    board = start_position()
                    ui_state['turn'] = 'w'
                    ui_state['selected'] = None
                    ui_state['legal_moves'] = []
                    ui_state['game_over'] = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ui_state['turn'] == 'w' and not ui_state['game_over']:
                    pos = pos_from_mouse(*event.pos)
                    if pos:
                        r, c = pos
                        sel = ui_state['selected']
                        if sel is None:
                            # select piece if white
                            p = board[r][c]
                            if p and p.color == 'w':
                                # compute legal moves for that piece only
                                moves = [mv for mv in legal_moves(board, 'w') if mv[0] == (r, c)]
                                ui_state['selected'] = (r, c)
                                ui_state['legal_moves'] = moves
                        else:
                            # try move
                            legal_for_sel = ui_state['legal_moves']
                            chosen = None
                            for mv in legal_for_sel:
                                (_, _), (dr, dc) = mv
                                if (dr, dc) == (r, c):
                                    chosen = mv
                                    break
                            if chosen:
                                board = apply_move(board, chosen)
                                ui_state['selected'] = None
                                ui_state['legal_moves'] = []
                                # swap turn
                                ui_state['turn'] = 'b'
                            else:
                                # reselect or cancel
                                p = board[r][c]
                                if p and p.color == 'w':
                                    moves = [mv for mv in legal_moves(board, 'w') if mv[0] == (r, c)]
                                    ui_state['selected'] = (r, c)
                                    ui_state['legal_moves'] = moves
                                else:
                                    ui_state['selected'] = None
                                    ui_state['legal_moves'] = []

        # After player move, AI plays
        if ui_state['turn'] == 'b' and not ui_state['game_over']:
            pygame.time.delay(200)  # small delay for UX
            mv = simple_ai_choose_move(board, 'b')
            if mv is None:
                # no legal moves: game over
                ui_state['game_over'] = True
                ui_state['turn'] = 'w'  # so status text looks accurate for stalemate/mate
            else:
                board = apply_move(board, mv)
                ui_state['turn'] = 'w'

        # Game over detection
        if not ui_state['game_over']:
            current_moves = legal_moves(board, ui_state['turn'])
            if not current_moves:
                ui_state['game_over'] = True

        draw_board(screen, board, ui_state, fonts)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
