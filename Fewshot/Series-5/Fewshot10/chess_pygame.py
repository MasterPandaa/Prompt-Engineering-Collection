import sys
import pygame
from copy import deepcopy

# =====================
# Konfigurasi Tampilan
# =====================
TILE_SIZE = 80
BOARD_TILES = 8
MARGIN = 20
WIDTH = BOARD_TILES * TILE_SIZE + 2 * MARGIN
HEIGHT = BOARD_TILES * TILE_SIZE + 2 * MARGIN + 60  # ruang info

# Warna
COLOR_LIGHT = (240, 217, 181)
COLOR_DARK = (181, 136, 99)
COLOR_BG = (30, 30, 30)
COLOR_SEL = (255, 255, 0)
COLOR_MOVE = (50, 205, 50)
COLOR_TEXT = (230, 230, 230)
COLOR_PIECE_WHITE = (245, 245, 245)
COLOR_PIECE_BLACK = (30, 30, 30)

# Font size relatif terhadap tile
PIECE_FONT_RATIO = 0.6
INFO_FONT_SIZE = 20

# =====================
# Representasi Board
# huruf kecil = hitam, huruf besar = putih, '.' = kosong
# =====================

def initial_board():
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

# =====================
# Utilitas
# =====================

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def is_empty(piece):
    return piece == '.'


def is_white_piece(piece):
    return piece.isalpha() and piece.isupper()


def is_black_piece(piece):
    return piece.isalpha() and piece.islower()


def piece_color(piece):
    if is_white_piece(piece):
        return 'white'
    if is_black_piece(piece):
        return 'black'
    return None

# =====================
# Gerakan Bidak
# =====================

def get_pawn_moves(board, r, c, color):
    moves = []
    piece = board[r][c]
    dir_ = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1
    end_row_promo = 0 if color == 'white' else 7

    # Maju 1 langkah
    nr = r + dir_
    if in_bounds(nr, c) and is_empty(board[nr][c]):
        # promosi
        if nr == end_row_promo:
            moves.append(((r, c), (nr, c), 'promo'))
        else:
            moves.append(((r, c), (nr, c), None))
        # Maju 2 langkah dari posisi awal
        nr2 = r + 2 * dir_
        if r == start_row and is_empty(board[nr2][c]):
            moves.append(((r, c), (nr2, c), None))

    # Tangkap diagonal
    for dc in (-1, 1):
        nc = c + dc
        nr = r + dir_
        if in_bounds(nr, nc):
            target = board[nr][nc]
            if target != '.' and piece_color(target) and piece_color(target) != color:
                if nr == end_row_promo:
                    moves.append(((r, c), (nr, nc), 'promo'))
                else:
                    moves.append(((r, c), (nr, nc), None))

    # En passant tidak diimplementasikan
    return moves


def get_knight_moves(board, r, c, color):
    moves = []
    offsets = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        target = board[nr][nc]
        if is_empty(target) or (piece_color(target) and piece_color(target) != color):
            moves.append(((r, c), (nr, nc), None))
    return moves


def ray_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if is_empty(target):
                moves.append(((r, c), (nr, nc), None))
            else:
                if piece_color(target) != color:
                    moves.append(((r, c), (nr, nc), None))
                break
            nr += dr
            nc += dc
    return moves


def get_bishop_moves(board, r, c, color):
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return ray_moves(board, r, c, color, dirs)


def get_rook_moves(board, r, c, color):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return ray_moves(board, r, c, color, dirs)


def get_queen_moves(board, r, c, color):
    dirs = [
        (-1, -1), (-1, 1), (1, -1), (1, 1),
        (-1, 0), (1, 0), (0, -1), (0, 1)
    ]
    return ray_moves(board, r, c, color, dirs)


def get_king_moves(board, r, c, color):
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            target = board[nr][nc]
            if is_empty(target) or (piece_color(target) and piece_color(target) != color):
                moves.append(((r, c), (nr, nc), None))
    # Castling tidak diimplementasikan
    return moves


def get_piece_moves(board, r, c):
    piece = board[r][c]
    if piece == '.':
        return []
    color = 'white' if is_white_piece(piece) else 'black'
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
    all_moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.':
                continue
            if color == 'white' and not is_white_piece(piece):
                continue
            if color == 'black' and not is_black_piece(piece):
                continue
            for move in get_piece_moves(board, r, c):
                (sr, sc), (tr, tc), flag = move
                target = board[tr][tc]
                # Validasi dasar: tidak bisa menabrak teman sendiri
                if target != '.' and piece_color(target) == color:
                    continue
                all_moves.append(move)
    return all_moves

# =====================
# Aplikasi Langkah & Evaluasi
# =====================

def make_move(board, move):
    new_board = deepcopy(board)
    (sr, sc), (tr, tc), flag = move
    piece = new_board[sr][sc]
    new_board[sr][sc] = '.'

    # Promosi pion otomatis ke Queen
    if flag == 'promo':
        if piece_color(piece) == 'white':
            new_board[tr][tc] = 'Q'
        else:
            new_board[tr][tc] = 'q'
    else:
        new_board[tr][tc] = piece
    return new_board

# Skor material sederhana
PIECE_VALUES = {
    'p': 100,
    'n': 300,
    'b': 300,
    'r': 500,
    'q': 900,
    'k': 0,
}


def evaluate(board):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.':
                continue
            val = PIECE_VALUES[piece.lower()]
            if is_white_piece(piece):
                score += val
            else:
                score -= val
    return score


def ai_pick_move(board, color):
    # Greedy kedalaman 1: pilih langkah yang memaksimalkan evaluasi
    moves = get_all_moves(board, color)
    if not moves:
        return None
    best_move = None
    if color == 'white':
        best_score = -10**9
    else:
        best_score = 10**9

    for mv in moves:
        nb = make_move(board, mv)
        sc = evaluate(nb)
        if color == 'white':
            if sc > best_score:
                best_score = sc
                best_move = mv
        else:
            if sc < best_score:
                best_score = sc
                best_move = mv
    return best_move

# =====================
# Pygame UI
# =====================

def board_to_screen(rc):
    r, c = rc
    x = MARGIN + c * TILE_SIZE
    y = MARGIN + r * TILE_SIZE
    return x, y


def screen_to_board(pos):
    x, y = pos
    x -= MARGIN
    y -= MARGIN
    if x < 0 or y < 0:
        return None
    c = x // TILE_SIZE
    r = y // TILE_SIZE
    if not in_bounds(r, c):
        return None
    return (r, c)


def draw_board(screen, font_piece, font_info, board, selected, legal_moves, turn, status_text):
    screen.fill(COLOR_BG)

    # Kotak papan
    for r in range(8):
        for c in range(8):
            x, y = board_to_screen((r, c))
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
            pygame.draw.rect(screen, color, rect)

    # Highlight selected
    if selected is not None:
        x, y = board_to_screen(selected)
        pygame.draw.rect(screen, COLOR_SEL, (x, y, TILE_SIZE, TILE_SIZE), 3)

    # Highlight legal moves
    for (_, _), (tr, tc), _ in legal_moves:
        cx, cy = board_to_screen((tr, tc))
        pygame.draw.circle(screen, COLOR_MOVE, (cx + TILE_SIZE // 2, cy + TILE_SIZE // 2), 10)

    # Render bidak (huruf)
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.':
                continue
            x, y = board_to_screen((r, c))
            text = piece.upper() if is_white_piece(piece) else piece.lower()
            color = COLOR_PIECE_WHITE if is_white_piece(piece) else COLOR_PIECE_BLACK
            surf = font_piece.render(text, True, color)
            rect = surf.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            screen.blit(surf, rect)

    # Info area
    info_y = MARGIN + 8 * TILE_SIZE + 10
    info_text = f"Giliran: {'Putih' if turn == 'white' else 'Hitam (AI)'}  |  {status_text}"
    surf = font_info.render(info_text, True, COLOR_TEXT)
    screen.blit(surf, (MARGIN, info_y))

    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption('Pygame Chess - Simple AI')

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    piece_font_size = int(TILE_SIZE * PIECE_FONT_RATIO)
    font_piece = pygame.font.SysFont('arial', piece_font_size, bold=True)
    font_info = pygame.font.SysFont('consolas', INFO_FONT_SIZE)

    board = initial_board()
    selected = None
    legal_moves = []
    turn = 'white'  # manusia putih, AI hitam
    running = True
    status_text = 'Klik sebuah bidak untuk bergerak.'

    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = initial_board()
                    selected = None
                    legal_moves = []
                    turn = 'white'
                    status_text = 'Reset papan.'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn != 'white':
                    break
                pos = pygame.mouse.get_pos()
                rc = screen_to_board(pos)
                if rc is None:
                    continue
                r, c = rc
                piece = board[r][c]
                if selected is None:
                    # Pilih bidak putih
                    if piece != '.' and is_white_piece(piece):
                        selected = (r, c)
                        legal_moves = [mv for mv in get_piece_moves(board, r, c)
                                       if piece_color(board[mv[1][0]][mv[1][1]]) != 'white']
                        status_text = 'Pilih petak tujuan.'
                    else:
                        status_text = 'Pilih bidak putih milik Anda.'
                else:
                    # Coba lakukan langkah
                    valid_targets = {(mv[1][0], mv[1][1]): mv for mv in legal_moves}
                    if (r, c) in valid_targets:
                        board = make_move(board, valid_targets[(r, c)])
                        selected = None
                        legal_moves = []
                        turn = 'black'
                        status_text = 'AI berpikir...'
                    else:
                        # klik ulang: ganti pilihan jika klik bidak sendiri
                        if piece != '.' and is_white_piece(piece):
                            selected = (r, c)
                            legal_moves = [mv for mv in get_piece_moves(board, r, c)
                                           if piece_color(board[mv[1][0]][mv[1][1]]) != 'white']
                            status_text = 'Pilih petak tujuan.'
                        else:
                            # batal seleksi
                            selected = None
                            legal_moves = []
                            status_text = 'Langkah dibatalkan.'

        # Giliran AI
        if running and turn == 'black':
            ai_move = ai_pick_move(board, 'black')
            if ai_move is None:
                status_text = 'AI tidak punya langkah. Game over.'
                turn = 'white'
            else:
                board = make_move(board, ai_move)
                turn = 'white'
                status_text = 'Giliran Anda.'

        draw_board(screen, font_piece, font_info, board, selected, legal_moves, turn, status_text)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
