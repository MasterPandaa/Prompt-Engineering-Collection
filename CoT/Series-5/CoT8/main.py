import sys
import random
import pygame

# ---------------------------
# Konfigurasi
# ---------------------------
WIDTH, HEIGHT = 640, 700  # ruang tambahan di bawah untuk status
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
MARGIN_BOTTOM = HEIGHT - WIDTH

# Warna
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (50, 50, 50)
CAPTURE_HIGHLIGHT = (200, 60, 60)
TEXT_COLOR = (20, 20, 20)
BG_STATUS = (230, 230, 230)

# Nilai bidak untuk AI
PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 1000,
}

# Mapping Unicode bidak
UNICODE_PIECES = {
    'wK': '\u2654', 'wQ': '\u2655', 'wR': '\u2656', 'wB': '\u2657', 'wN': '\u2658', 'wP': '\u2659',
    'bK': '\u265A', 'bQ': '\u265B', 'bR': '\u265C', 'bB': '\u265D', 'bN': '\u265E', 'bP': '\u265F',
}


def create_initial_board():
    # Representasi papan sebagai list 2D 8x8: None atau kode 2 huruf cth 'wP'
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    # Bidak hitam (atas)
    board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
    board[1] = ['bP'] * 8

    # Bidak putih (bawah)
    board[6] = ['wP'] * 8
    board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    return board


def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def get_piece_color(piece):
    if not piece:
        return None
    return piece[0]  # 'w' atau 'b'


def piece_type(piece):
    return piece[1] if piece else None  # 'P','N','B','R','Q','K'


# ---------------------------
# Generator Langkah (Pseudo-legal)
# ---------------------------

def generate_moves_for_piece(board, r, c):
    piece = board[r][c]
    if not piece:
        return []
    color = get_piece_color(piece)
    ptype = piece_type(piece)

    if ptype == 'P':
        return pawn_moves(board, r, c, color)
    elif ptype == 'N':
        return knight_moves(board, r, c, color)
    elif ptype == 'B':
        return bishop_moves(board, r, c, color)
    elif ptype == 'R':
        return rook_moves(board, r, c, color)
    elif ptype == 'Q':
        return queen_moves(board, r, c, color)
    elif ptype == 'K':
        return king_moves(board, r, c, color)
    return []


def generate_all_moves(board, color):
    moves = []  # list of ((sr, sc), (dr, dc))
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece and get_piece_color(piece) == color:
                for dr, dc in generate_moves_for_piece(board, r, c):
                    moves.append(((r, c), (dr, dc)))
    return moves


def pawn_moves(board, r, c, color):
    moves = []
    dir = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1

    # Maju satu
    fr, fc = r + dir, c
    if in_bounds(fr, fc) and board[fr][fc] is None:
        moves.append((fr, fc))
        # Maju dua jika dari baris awal dan jalur kosong
        fr2 = r + 2 * dir
        if r == start_row and in_bounds(fr2, fc) and board[fr2][fc] is None:
            moves.append((fr2, fc))

    # Tangkap diagonal
    for dc in (-1, 1):
        tr, tc = r + dir, c + dc
        if in_bounds(tr, tc) and board[tr][tc] is not None and get_piece_color(board[tr][tc]) != color:
            moves.append((tr, tc))

    return moves


def knight_moves(board, r, c, color):
    moves = []
    deltas = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 1),
    ]
    for dr, dc in deltas:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc):
            target = board[nr][nc]
            if target is None or get_piece_color(target) != color:
                moves.append((nr, nc))
    return moves


def sliding_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target is None:
                moves.append((nr, nc))
            else:
                if get_piece_color(target) != color:
                    moves.append((nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def bishop_moves(board, r, c, color):
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return sliding_moves(board, r, c, color, dirs)


def rook_moves(board, r, c, color):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return sliding_moves(board, r, c, color, dirs)


def queen_moves(board, r, c, color):
    dirs = [
        (-1, -1), (-1, 1), (1, -1), (1, 1),
        (-1, 0), (1, 0), (0, -1), (0, 1)
    ]
    return sliding_moves(board, r, c, color, dirs)


def king_moves(board, r, c, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None or get_piece_color(target) != color:
                    moves.append((nr, nc))
    return moves


# ---------------------------
# Mekanisme Game
# ---------------------------

def make_move(board, src, dst):
    sr, sc = src
    dr, dc = dst
    piece = board[sr][sc]
    captured = board[dr][dc]

    board[dr][dc] = piece
    board[sr][sc] = None

    # Promosi pion otomatis menjadi Queen ketika mencapai ujung
    ptype = piece_type(piece)
    color = get_piece_color(piece)
    if ptype == 'P':
        if (color == 'w' and dr == 0) or (color == 'b' and dr == 7):
            board[dr][dc] = color + 'Q'
    return captured


def find_kings(board):
    w_king = b_king = False
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 'wK':
                w_king = True
            elif board[r][c] == 'bK':
                b_king = True
    return w_king, b_king


def ai_choose_move(board):
    # AI untuk hitam ('b')
    moves = generate_all_moves(board, 'b')
    if not moves:
        return None

    # Pilih langkah yang memakan bidak bernilai tertinggi. Jika tidak ada tangkapan, pilih acak.
    best_score = -1
    best_moves = []

    for (sr, sc), (dr, dc) in moves:
        target = board[dr][dc]
        score = PIECE_VALUES.get(piece_type(target), 0) if target else 0
        if score > best_score:
            best_score = score
            best_moves = [((sr, sc), (dr, dc))]
        elif score == best_score:
            best_moves.append(((sr, sc), (dr, dc)))

    return random.choice(best_moves) if best_moves else None


# ---------------------------
# Rendering
# ---------------------------

def draw_board(screen):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_status_bar(screen, font_small, text):
    pygame.draw.rect(screen, BG_STATUS, (0, WIDTH, WIDTH, MARGIN_BOTTOM))
    surface = font_small.render(text, True, TEXT_COLOR)
    screen.blit(surface, (10, WIDTH + (MARGIN_BOTTOM - surface.get_height()) // 2))


def draw_pieces(screen, board, font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece:
                char = UNICODE_PIECES[piece]
                img = font.render(char, True, (0, 0, 0))
                # center
                rect = img.get_rect(center=(c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(img, rect)


def highlight_selection_and_moves(screen, selected, legal_moves, board):
    if selected is None:
        return
    sr, sc = selected
    # Highlight kotak terpilih
    pygame.draw.rect(screen, HIGHLIGHT, (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

    # Tampilkan moves: titik untuk langkah biasa, kotak merah untuk capture
    for (dr, dc) in legal_moves:
        target = board[dr][dc]
        cx = dc * SQUARE_SIZE + SQUARE_SIZE // 2
        cy = dr * SQUARE_SIZE + SQUARE_SIZE // 2
        if target is None:
            pygame.draw.circle(screen, MOVE_DOT, (cx, cy), 8)
        else:
            pygame.draw.rect(screen, CAPTURE_HIGHLIGHT, (dc * SQUARE_SIZE + 4, dr * SQUARE_SIZE + 4, SQUARE_SIZE - 8, SQUARE_SIZE - 8), 4)


# ---------------------------
# Input & Main Loop
# ---------------------------

def main():
    pygame.init()
    pygame.display.set_caption('Catur Pygame - Manusia vs AI')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Font: gunakan font bawaan untuk render Unicode bidak
    # Ukuran font disesuaikan agar pas di kotak
    piece_font = pygame.font.SysFont(None, int(SQUARE_SIZE * 0.9))
    status_font = pygame.font.SysFont(None, 28)

    board = create_initial_board()
    running = True
    clock = pygame.time.Clock()

    selected = None
    legal_moves_cache = []
    turn = 'w'  # putih (manusia) mulai
    status_text = 'Giliran Putih (Kamu)'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < WIDTH and turn == 'w':  # klik dalam papan dan hanya saat giliran manusia
                    c = mx // SQUARE_SIZE
                    r = my // SQUARE_SIZE
                    if selected is None:
                        # Pilih bidak sendiri
                        piece = board[r][c]
                        if piece and get_piece_color(piece) == 'w':
                            selected = (r, c)
                            legal_moves_cache = generate_moves_for_piece(board, r, c)
                        else:
                            selected = None
                            legal_moves_cache = []
                    else:
                        # Coba lakukan langkah jika valid
                        if (r, c) in legal_moves_cache:
                            captured = make_move(board, selected, (r, c))
                            selected = None
                            legal_moves_cache = []

                            # Cek raja masih ada?
                            w_king, b_king = find_kings(board)
                            if not b_king:
                                status_text = 'Kamu menang! Raja hitam tertangkap.'
                            elif not w_king:
                                status_text = 'Kamu kalah! Raja putih tertangkap.'
                            else:
                                # Ganti giliran ke AI
                                turn = 'b'
                                status_text = 'Giliran Hitam (AI)'
                        else:
                            # Ganti seleksi jika klik bidak sendiri
                            piece = board[r][c]
                            if piece and get_piece_color(piece) == 'w':
                                selected = (r, c)
                                legal_moves_cache = generate_moves_for_piece(board, r, c)
                            else:
                                selected = None
                                legal_moves_cache = []

        # Gerakan AI ketika gilirannya
        if turn == 'b':
            pygame.time.delay(200)  # sedikit jeda agar terasa natural
            move = ai_choose_move(board)
            if move is None:
                status_text = 'Seri: AI tidak punya langkah.'
                turn = 'w'
            else:
                make_move(board, move[0], move[1])
                w_king, b_king = find_kings(board)
                if not w_king:
                    status_text = 'Kamu kalah! Raja putih tertangkap.'
                elif not b_king:
                    status_text = 'Kamu menang! Raja hitam tertangkap.'
                else:
                    turn = 'w'
                    status_text = 'Giliran Putih (Kamu)'

        # Render
        draw_board(screen)
        highlight_selection_and_moves(screen, selected, legal_moves_cache, board)
        draw_pieces(screen, board, piece_font)
        draw_status_bar(screen, status_font, status_text)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
