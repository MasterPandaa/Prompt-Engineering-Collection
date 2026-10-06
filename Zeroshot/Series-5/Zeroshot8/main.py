import sys
import math
import random
import pygame

# ============================
# Konfigurasi
# ============================
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 8
MARGIN_TOP = 60  # ruang untuk status bar
SQUARE_SIZE = min(WIDTH, HEIGHT - MARGIN_TOP) // BOARD_SIZE
BOARD_PIXELS = SQUARE_SIZE * BOARD_SIZE
OFFSET_X = (WIDTH - BOARD_PIXELS) // 2
OFFSET_Y = MARGIN_TOP

LIGHT_COLOR = (238, 238, 210)
DARK_COLOR = (118, 150, 86)
SELECT_COLOR = (246, 246, 105)
HIGHLIGHT_COLOR = (187, 203, 43)
CHECK_COLOR = (255, 100, 100)
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)
GHOST_MOVE_COLOR = (30, 30, 30, 120)

FPS = 60

# Unicode mapping untuk catur
UNICODE_PIECES = {
    ('w', 'K'): '\u2654',
    ('w', 'Q'): '\u2655',
    ('w', 'R'): '\u2656',
    ('w', 'B'): '\u2657',
    ('w', 'N'): '\u2658',
    ('w', 'P'): '\u2659',
    ('b', 'K'): '\u265A',
    ('b', 'Q'): '\u265B',
    ('b', 'R'): '\u265C',
    ('b', 'B'): '\u265D',
    ('b', 'N'): '\u265E',
    ('b', 'P'): '\u265F',
}

# ============================
# Utilitas Board
# ============================

def initial_board():
    # Representasi: None atau tuple (color, type)
    # Baris 0 adalah sisi hitam; baris 7 sisi putih
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Hitam
    back_rank = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    for c in range(BOARD_SIZE):
        board[0][c] = ('b', back_rank[c])
        board[1][c] = ('b', 'P')

    # Putih
    for c in range(BOARD_SIZE):
        board[6][c] = ('w', 'P')
        board[7][c] = ('w', back_rank[c])

    return board


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def clone_board(board):
    return [row[:] for row in board]


# ============================
# Gerak Bidak (Pseudolegal)
# ============================

def gen_pawn_moves(board, r, c, color):
    moves = []
    dir_ = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    # Maju 1
    nr = r + dir_
    if in_bounds(nr, c) and board[nr][c] is None:
        moves.append((nr, c))
        # Maju 2 dari posisi awal
        nr2 = r + 2 * dir_
        if r == start_row and board[nr2][c] is None:
            moves.append((nr2, c))
    # Makan diagonal
    for dc in (-1, 1):
        nc = c + dc
        nr = r + dir_
        if in_bounds(nr, nc) and board[nr][nc] is not None and board[nr][nc][0] != color:
            moves.append((nr, nc))
    # (Tidak implement en passant untuk kesederhanaan)
    return moves


def gen_knight_moves(board, r, c, color):
    moves = []
    steps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in steps:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        if board[nr][nc] is None or board[nr][nc][0] != color:
            moves.append((nr, nc))
    return moves


def gen_sliding_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] is None:
                moves.append((nr, nc))
            else:
                if board[nr][nc][0] != color:
                    moves.append((nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def gen_bishop_moves(board, r, c, color):
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return gen_sliding_moves(board, r, c, color, dirs)


def gen_rook_moves(board, r, c, color):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return gen_sliding_moves(board, r, c, color, dirs)


def gen_queen_moves(board, r, c, color):
    dirs = [
        (-1, -1), (-1, 1), (1, -1), (1, 1),
        (-1, 0), (1, 0), (0, -1), (0, 1)
    ]
    return gen_sliding_moves(board, r, c, color, dirs)


def gen_king_moves(board, r, c, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            if board[nr][nc] is None or board[nr][nc][0] != color:
                moves.append((nr, nc))
    # (Tidak implement castling untuk kesederhanaan)
    return moves


def gen_pseudolegal_moves_for_piece(board, r, c):
    piece = board[r][c]
    if piece is None:
        return []
    color, kind = piece
    if kind == 'P':
        return gen_pawn_moves(board, r, c, color)
    if kind == 'N':
        return gen_knight_moves(board, r, c, color)
    if kind == 'B':
        return gen_bishop_moves(board, r, c, color)
    if kind == 'R':
        return gen_rook_moves(board, r, c, color)
    if kind == 'Q':
        return gen_queen_moves(board, r, c, color)
    if kind == 'K':
        return gen_king_moves(board, r, c, color)
    return []


# ============================
# Validasi Check & Legal Moves
# ============================

def find_king(board, color):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            v = board[r][c]
            if v is not None and v[0] == color and v[1] == 'K':
                return (r, c)
    return None


def squares_attacked_by(board, attacker_color):
    # Kembalikan set posisi (r, c) yang diserang oleh attacker_color
    attacked = set()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            v = board[r][c]
            if v is None or v[0] != attacker_color:
                continue
            color, kind = v
            moves = []
            if kind == 'P':
                dir_ = -1 if color == 'w' else 1
                for dc in (-1, 1):
                    nr, nc = r + dir_, c + dc
                    if in_bounds(nr, nc):
                        attacked.add((nr, nc))
                continue
            elif kind == 'N':
                moves = gen_knight_moves(board, r, c, color)
            elif kind == 'B':
                moves = gen_bishop_moves(board, r, c, color)
            elif kind == 'R':
                moves = gen_rook_moves(board, r, c, color)
            elif kind == 'Q':
                moves = gen_queen_moves(board, r, c, color)
            elif kind == 'K':
                # Raja menyerang sekitar 1 petak
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if in_bounds(nr, nc):
                            attacked.add((nr, nc))
                continue
            for m in moves:
                attacked.add(m)
    return attacked


def in_check(board, color):
    kr, kc = find_king(board, color)
    if kr is None:
        return False
    attacker = 'b' if color == 'w' else 'w'
    attacked = squares_attacked_by(board, attacker)
    return (kr, kc) in attacked


def apply_move(board, from_sq, to_sq):
    r1, c1 = from_sq
    r2, c2 = to_sq
    piece = board[r1][c1]
    new_board = clone_board(board)
    new_board[r1][c1] = None
    # Promosi pion otomatis menjadi Queen
    if piece[1] == 'P' and (r2 == 0 or r2 == BOARD_SIZE - 1):
        new_board[r2][c2] = (piece[0], 'Q')
    else:
        new_board[r2][c2] = piece
    return new_board


def generate_legal_moves(board, color):
    legal = []  # list of (from_r, from_c, to_r, to_c)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            v = board[r][c]
            if v is None or v[0] != color:
                continue
            for (nr, nc) in gen_pseudolegal_moves_for_piece(board, r, c):
                nb = apply_move(board, (r, c), (nr, nc))
                if not in_check(nb, color):
                    legal.append((r, c, nr, nc))
    return legal


# ============================
# Rendering
# ============================

def try_get_font(size):
    # Coba beberapa font yang umumnya punya glyph catur
    candidates = [
        'Segoe UI Symbol',  # Windows
        'DejaVu Sans',      # Linux/Many
        'Arial Unicode MS', # Kadang ada
        None                # Default font
    ]
    for name in candidates:
        try:
            if name is None:
                return pygame.font.Font(None, size)
            f = pygame.font.SysFont(name, size)
            # Pastikan objek font valid
            if f is not None:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)


def draw_board(surface, selected_square, legal_targets, board, check_state):
    # Latar
    surface.fill(BG_COLOR)

    # Garis status area atas
    pygame.draw.rect(surface, (45, 45, 45), pygame.Rect(0, 0, WIDTH, MARGIN_TOP))

    # Papan 8x8
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(OFFSET_X + c * SQUARE_SIZE, OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)

    # Highlight selected
    if selected_square is not None:
        r, c = selected_square
        rect = pygame.Rect(OFFSET_X + c * SQUARE_SIZE, OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(surface, SELECT_COLOR, rect, 4)

    # Highlight legal targets
    for (tr, tc) in legal_targets:
        cx = OFFSET_X + tc * SQUARE_SIZE + SQUARE_SIZE // 2
        cy = OFFSET_Y + tr * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 8
        pygame.draw.circle(surface, HIGHLIGHT_COLOR, (cx, cy), radius)

    # Highlight check king
    if check_state is not None:
        king_pos, color = check_state
        r, c = king_pos
        rect = pygame.Rect(OFFSET_X + c * SQUARE_SIZE, OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((*CHECK_COLOR, 90))
        surface.blit(s, rect.topleft)


def draw_pieces(surface, board, piece_font):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            v = board[r][c]
            if v is None:
                continue
            glyph = UNICODE_PIECES.get(v)
            rect = pygame.Rect(OFFSET_X + c * SQUARE_SIZE, OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if glyph is not None:
                text = piece_font.render(glyph, True, (20, 20, 20))
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
            else:
                # Fallback: bentuk sederhana (lingkaran putih/hitam)
                cx, cy = rect.center
                col = (240, 240, 240) if v[0] == 'w' else (30, 30, 30)
                pygame.draw.circle(surface, col, (cx, cy), SQUARE_SIZE // 3)


def draw_status(surface, turn_color, is_check, result_text, ui_font):
    status_text = f"Giliran: {'Putih' if turn_color == 'w' else 'Hitam'}"
    if is_check:
        status_text += "  |  Skak!"
    if result_text:
        status_text = result_text
    text_surf = ui_font.render(status_text, True, TEXT_COLOR)
    surface.blit(text_surf, (OFFSET_X, 18))


# ============================
# AI Sederhana
# ============================

def ai_choose_move(board, color):
    # Pilih langkah legal acak; preferensi sederhana: ambil langkah yang menangkap jika ada
    legal = generate_legal_moves(board, color)
    if not legal:
        return None
    capture_moves = []
    for r1, c1, r2, c2 in legal:
        if board[r2][c2] is not None:
            capture_moves.append((r1, c1, r2, c2))
    if capture_moves:
        return random.choice(capture_moves)
    return random.choice(legal)


# ============================
# Game Loop & Input
# ============================

def board_from_pixel(px, py):
    if not (OFFSET_X <= px < OFFSET_X + BOARD_PIXELS and OFFSET_Y <= py < OFFSET_Y + BOARD_PIXELS):
        return None
    c = (px - OFFSET_X) // SQUARE_SIZE
    r = (py - OFFSET_Y) // SQUARE_SIZE
    return (r, c)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catur Pygame - Tanpa Gambar Eksternal")
    clock = pygame.time.Clock()

    piece_font = try_get_font(int(SQUARE_SIZE * 0.8))
    ui_font = try_get_font(28)

    board = initial_board()
    turn = 'w'  # pemain putih
    selected = None
    legal_targets = []
    running = True
    result_text = ''

    while running:
        clock.tick(FPS)

        # Status skak
        is_check = in_check(board, turn)
        check_state = None
        if is_check:
            king_pos = find_king(board, turn)
            if king_pos:
                check_state = (king_pos, turn)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    board = initial_board()
                    turn = 'w'
                    selected = None
                    legal_targets = []
                    result_text = ''
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and result_text == '':
                pos = pygame.mouse.get_pos()
                sq = board_from_pixel(*pos)
                if sq is None:
                    selected = None
                    legal_targets = []
                else:
                    r, c = sq
                    v = board[r][c]
                    if selected is None:
                        # Pilih bidak milik pemain putih saja (player white)
                        if v is not None and v[0] == turn:
                            selected = (r, c)
                            # kalkulasi legal moves untuk selected
                            temp_moves = gen_pseudolegal_moves_for_piece(board, r, c)
                            # saring legal (tidak membuat raja sendiri ter-schak)
                            legal_targets = []
                            for (nr, nc) in temp_moves:
                                nb = apply_move(board, (r, c), (nr, nc))
                                if not in_check(nb, turn):
                                    legal_targets.append((nr, nc))
                        else:
                            selected = None
                            legal_targets = []
                    else:
                        # Coba melakukan langkah ke sq jika legal
                        if (r, c) in legal_targets:
                            board = apply_move(board, selected, (r, c))
                            selected = None
                            legal_targets = []
                            # Cek akhir giliran: apakah lawan punya langkah?
                            turn = 'b' if turn == 'w' else 'w'
                            # Setelah pemain putih jalan, biarkan AI hitam bergerak otomatis
                            if turn == 'b':
                                pygame.display.flip()  # render dulu agar terasa responsif
                                pygame.event.pump()
                                # AI bergerak
                                ai_move = ai_choose_move(board, 'b')
                                if ai_move is None:
                                    # Tidak ada langkah legal untuk hitam
                                    if in_check(board, 'b'):
                                        result_text = 'Skakmat! Putih menang.'
                                    else:
                                        result_text = 'Stalemate! Seri.'
                                else:
                                    r1, c1, r2, c2 = ai_move
                                    board = apply_move(board, (r1, c1), (r2, c2))
                                    turn = 'w'
                                    # Setelah AI bergerak, cek apakah putih punya langkah
                                    white_legal = generate_legal_moves(board, 'w')
                                    if not white_legal:
                                        if in_check(board, 'w'):
                                            result_text = 'Skakmat! Hitam menang.'
                                        else:
                                            result_text = 'Stalemate! Seri.'
                        else:
                            # Re-seleksi jika klik bidak sendiri lagi
                            if v is not None and v[0] == turn:
                                selected = (r, c)
                                temp_moves = gen_pseudolegal_moves_for_piece(board, r, c)
                                legal_targets = []
                                for (nr, nc) in temp_moves:
                                    nb = apply_move(board, (r, c), (nr, nc))
                                    if not in_check(nb, turn):
                                        legal_targets.append((nr, nc))
                            else:
                                selected = None
                                legal_targets = []

        # Cek kondisi akhir jika bukan saat giliran AI
        if result_text == '':
            legal_now = generate_legal_moves(board, turn)
            if not legal_now:
                if in_check(board, turn):
                    if turn == 'w':
                        result_text = 'Skakmat! Hitam menang.'
                    else:
                        result_text = 'Skakmat! Putih menang.'
                else:
                    result_text = 'Stalemate! Seri.'

        draw_board(screen, selected, legal_targets, board, check_state)
        draw_pieces(screen, board, piece_font)
        draw_status(screen, turn, is_check and result_text == '', result_text, ui_font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
