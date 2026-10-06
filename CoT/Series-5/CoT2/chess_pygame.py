import sys
import random
import pygame
from typing import List, Tuple, Optional, Dict

# ==========================
# Konfigurasi dasar
# ==========================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
MARGIN_BOTTOM = 80  # ruang untuk status bar
WINDOW_HEIGHT = HEIGHT + MARGIN_BOTTOM

# Warna
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HILITE = (246, 246, 105)
HILITE_MOVE = (187, 203, 43)
SEL = (255, 255, 0)
CHECK_RED = (214, 40, 40)
PANEL = (30, 30, 30)
TEXT = (230, 230, 230)

# Unicode bidak
UNICODE_PIECES = {
    'wk': '♔', 'wq': '♕', 'wr': '♖', 'wb': '♗', 'wn': '♘', 'wp': '♙',
    'bk': '♚', 'bq': '♛', 'br': '♜', 'bb': '♝', 'bn': '♞', 'bp': '♟',
}

# Nilai material sederhana untuk AI
PIECE_VALUES = {'k': 0, 'q': 9, 'r': 5, 'b': 3, 'n': 3, 'p': 1}

# ==========================
# Representasi papan
# ==========================
# Gunakan list 2D 8x8. Elemen None jika kosong, atau string 2 huruf: warna{'w','b'} + tipe{'k','q','r','b','n','p'}

Board = List[List[Optional[str]]]
Move = Dict[str, Tuple[int, int] | Optional[str]]  # {'from': (r,c), 'to': (r,c), 'promo': Optional['q','r','b','n']}


def create_start_board() -> Board:
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    # Bidak hitam
    board[0] = ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br']
    board[1] = ['bp'] * 8
    # Bidak putih
    board[6] = ['wp'] * 8
    board[7] = ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
    return board


# ==========================
# Utilitas
# ==========================

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def is_white(piece: Optional[str]) -> bool:
    return bool(piece) and piece[0] == 'w'


def is_black(piece: Optional[str]) -> bool:
    return bool(piece) and piece[0] == 'b'


def opponent(color: str) -> str:
    return 'b' if color == 'w' else 'w'


def clone_board(board: Board) -> Board:
    return [row[:] for row in board]


def find_king(board: Board, color: str) -> Tuple[int, int]:
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == f"{color}k":
                return r, c
    return -1, -1


# ==========================
# Generator langkah pseudo-legal
# ==========================

def gen_pawn_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir = -1 if color == 'w' else 1  # putih ke atas (-1), hitam ke bawah (+1)
    start_rank = 6 if color == 'w' else 1
    last_rank = 0 if color == 'w' else 7

    # Maju 1
    r1, c1 = r + dir, c
    if in_bounds(r1, c1) and board[r1][c1] is None:
        # Promosi
        if r1 == last_rank:
            moves.append({'from': (r, c), 'to': (r1, c1), 'promo': 'q'})
        else:
            moves.append({'from': (r, c), 'to': (r1, c1), 'promo': None})
        # Maju 2 dari posisi awal
        if r == start_rank:
            r2 = r + 2 * dir
            if in_bounds(r2, c) and board[r2][c] is None:
                moves.append({'from': (r, c), 'to': (r2, c), 'promo': None})

    # Tangkap kiri/kanan
    for dc in (-1, 1):
        rr, cc = r + dir, c + dc
        if in_bounds(rr, cc):
            target = board[rr][cc]
            if target and ((color == 'w' and is_black(target)) or (color == 'b' and is_white(target))):
                if rr == last_rank:
                    moves.append({'from': (r, c), 'to': (rr, cc), 'promo': 'q'})
                else:
                    moves.append({'from': (r, c), 'to': (rr, cc), 'promo': None})

    # Catatan: en passant tidak diimplementasi agar sederhana
    return moves


def gen_knight_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    deltas = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
    for dr, dc in deltas:
        rr, cc = r + dr, c + dc
        if not in_bounds(rr, cc):
            continue
        target = board[rr][cc]
        if target is None or (color == 'w' and is_black(target)) or (color == 'b' and is_white(target)):
            moves.append({'from': (r, c), 'to': (rr, cc), 'promo': None})
    return moves


def gen_slider_moves(board: Board, r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            target = board[rr][cc]
            if target is None:
                moves.append({'from': (r, c), 'to': (rr, cc), 'promo': None})
            else:
                if (color == 'w' and is_black(target)) or (color == 'b' and is_white(target)):
                    moves.append({'from': (r, c), 'to': (rr, cc), 'promo': None})
                break
            rr += dr
            cc += dc
    return moves


def gen_king_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not in_bounds(rr, cc):
                continue
            target = board[rr][cc]
            if target is None or (color == 'w' and is_black(target)) or (color == 'b' and is_white(target)):
                moves.append({'from': (r, c), 'to': (rr, cc), 'promo': None})
    # Catatan: rokas tidak diimplementasi agar sederhana
    return moves


def gen_pseudo_legal_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if not piece:
                continue
            if color == 'w' and not is_white(piece):
                continue
            if color == 'b' and not is_black(piece):
                continue
            ptype = piece[1]
            if ptype == 'p':
                moves.extend(gen_pawn_moves(board, r, c, color))
            elif ptype == 'n':
                moves.extend(gen_knight_moves(board, r, c, color))
            elif ptype == 'b':
                moves.extend(gen_slider_moves(board, r, c, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)]))
            elif ptype == 'r':
                moves.extend(gen_slider_moves(board, r, c, color, [(1, 0), (-1, 0), (0, 1), (0, -1)]))
            elif ptype == 'q':
                moves.extend(gen_slider_moves(board, r, c, color, [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]))
            elif ptype == 'k':
                moves.extend(gen_king_moves(board, r, c, color))
    return moves


# ==========================
# Validasi: cek skak dan langkah legal
# ==========================

def make_move(board: Board, move: Move) -> Board:
    b = clone_board(board)
    (fr, fc) = move['from']  # type: ignore[index]
    (tr, tc) = move['to']    # type: ignore[index]
    piece = b[fr][fc]
    b[fr][fc] = None
    if move.get('promo') and piece and piece[1] == 'p':
        b[tr][tc] = piece[0] + move['promo']  # type: ignore[operator]
    else:
        b[tr][tc] = piece
    return b


def square_attacked_by(board: Board, r: int, c: int, attacker_color: str) -> bool:
    # Periksa apakah kotak (r,c) diserang oleh warna attacker_color
    # 1. Serangan pion
    dir = -1 if attacker_color == 'w' else 1
    for dc in (-1, 1):
        rr, cc = r + dir, c + dc
        if in_bounds(rr, cc) and board[rr][cc] == f"{attacker_color}p":
            return True

    # 2. Kuda
    for dr, dc in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc) and board[rr][cc] == f"{attacker_color}n":
            return True

    # 3. Bishop/Queen diagonal
    for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            piece = board[rr][cc]
            if piece:
                if piece[0] == attacker_color and piece[1] in ('b', 'q'):
                    return True
                break
            rr += dr
            cc += dc

    # 4. Rook/Queen orthogonal
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            piece = board[rr][cc]
            if piece:
                if piece[0] == attacker_color and piece[1] in ('r', 'q'):
                    return True
                break
            rr += dr
            cc += dc

    # 5. King satu langkah
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and board[rr][cc] == f"{attacker_color}k":
                return True

    return False


def is_in_check(board: Board, color: str) -> bool:
    kr, kc = find_king(board, color)
    if kr == -1:
        return True  # raja hilang -> dianggap skak (posisi ilegal)
    return square_attacked_by(board, kr, kc, opponent(color))


def gen_legal_moves(board: Board, color: str) -> List[Move]:
    legal: List[Move] = []
    for mv in gen_pseudo_legal_moves(board, color):
        nb = make_move(board, mv)
        if not is_in_check(nb, color):
            legal.append(mv)
    return legal


# ==========================
# AI sederhana
# ==========================

def choose_ai_move(board: Board, color: str) -> Optional[Move]:
    legal = gen_legal_moves(board, color)
    if not legal:
        return None

    best_moves: List[Tuple[int, Move]] = []
    best_score = -10**9

    for mv in legal:
        (fr, fc) = mv['from']  # type: ignore[index]
        (tr, tc) = mv['to']    # type: ignore[index]
        captured = board[tr][tc]
        score = 0
        if captured:
            score = PIECE_VALUES[captured[1]]
        # Prefer promosi
        if mv.get('promo'):
            score += PIECE_VALUES['q']
        if score > best_score:
            best_score = score
            best_moves = [(score, mv)]
        elif score == best_score:
            best_moves.append((score, mv))

    # Jika semua skor sama (mis. tidak ada tangkapan), pilih acak dari legal
    if best_score == 0:
        return random.choice(legal)
    return random.choice(best_moves)[1]


# ==========================
# Rendering Pygame
# ==========================

def draw_board(surface: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(surface, color, rect)


def draw_highlights(surface: pygame.Surface, selected: Optional[Tuple[int, int]], moves: List[Move], in_check_square: Optional[Tuple[int, int]], last_move: Optional[Move]):
    # Highlight langkah yang mungkin
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * SQ_SIZE, sr * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s.fill((*HILITE, 120))
        surface.blit(s, rect.topleft)

    for mv in moves:
        tr, tc = mv['to']  # type: ignore[index]
        rect = pygame.Rect(tc * SQ_SIZE, tr * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s.fill((*HILITE_MOVE, 120))
        surface.blit(s, rect.topleft)

    if last_move is not None:
        for (rr, cc) in [last_move['from'], last_move['to']]:  # type: ignore[index]
            rect = pygame.Rect(cc * SQ_SIZE, rr * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(surface, (255, 255, 255), rect, 3)

    if in_check_square is not None:
        rr, cc = in_check_square
        rect = pygame.Rect(cc * SQ_SIZE, rr * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s.fill((*CHECK_RED, 120))
        surface.blit(s, rect.topleft)


def draw_pieces(surface: pygame.Surface, board: Board, font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if not piece:
                continue
            ch = UNICODE_PIECES.get(piece)
            if not ch:
                continue
            text = font.render(ch, True, (0, 0, 0) if piece[0] == 'w' else (0, 0, 0))
            # Untuk kontras, letakkan outline/Shadow sederhana
            tx = c * SQ_SIZE + SQ_SIZE // 2
            ty = r * SQ_SIZE + SQ_SIZE // 2
            text_rect = text.get_rect(center=(tx, ty))
            surface.blit(text, text_rect)


def draw_status(surface: pygame.Surface, msg: str, small_font: pygame.font.Font):
    rect = pygame.Rect(0, HEIGHT, WIDTH, MARGIN_BOTTOM)
    pygame.draw.rect(surface, PANEL, rect)
    label = small_font.render(msg, True, TEXT)
    surface.blit(label, (10, HEIGHT + (MARGIN_BOTTOM - label.get_height()) // 2))


# ==========================
# Game loop dan input
# ==========================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Catur Pygame - Manusia (Putih) vs AI (Hitam)')
    clock = pygame.time.Clock()

    # Cari font yang support unicode chess. None -> default system font.
    font_size = int(SQ_SIZE * 0.8)
    piece_font = pygame.font.SysFont(None, font_size)
    small_font = pygame.font.SysFont(None, 28)

    board: Board = create_start_board()
    turn = 'w'  # putih jalan dulu

    selected: Optional[Tuple[int, int]] = None
    legal_for_selected: List[Move] = []
    last_move: Optional[Move] = None
    game_over = False
    game_over_message = ''

    def status_text() -> str:
        if game_over:
            return game_over_message + "  |  Tekan R untuk restart, ESC untuk keluar"
        return ("Giliran: Putih" if turn == 'w' else "Giliran: Hitam (AI)")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    # restart
                    board = create_start_board()
                    turn = 'w'
                    selected = None
                    legal_for_selected = []
                    last_move = None
                    game_over = False
                    game_over_message = ''
            if not game_over and turn == 'w' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if my < HEIGHT:
                    c = mx // SQ_SIZE
                    r = my // SQ_SIZE
                    if selected is None:
                        piece = board[r][c]
                        if piece and is_white(piece):
                            # pilih bidak dan tampilkan langkah legalnya
                            selected = (r, c)
                            all_legal = gen_legal_moves(board, 'w')
                            legal_for_selected = [m for m in all_legal if m['from'] == (r, c)]
                    else:
                        # coba gerak
                        candidate = None
                        for m in legal_for_selected:
                            if m['to'] == (r, c):
                                candidate = m
                                break
                        if candidate:
                            board = make_move(board, candidate)
                            last_move = candidate
                            selected = None
                            legal_for_selected = []
                            # Cek akhir permainan setelah langkah putih
                            if not gen_legal_moves(board, 'b'):
                                if is_in_check(board, 'b'):
                                    game_over = True
                                    game_over_message = 'Skakmat! Putih menang.'
                                else:
                                    game_over = True
                                    game_over_message = 'Stalemate! Seri.'
                            else:
                                turn = 'b'
                        else:
                            # klik di tempat lain -> ganti seleksi jika bidak putih
                            piece = board[r][c]
                            if piece and is_white(piece):
                                selected = (r, c)
                                all_legal = gen_legal_moves(board, 'w')
                                legal_for_selected = [m for m in all_legal if m['from'] == (r, c)]
                            else:
                                selected = None
                                legal_for_selected = []

        # AI bergerak jika giliran hitam dan game belum selesai
        if not game_over and turn == 'b':
            pygame.time.delay(200)  # sedikit jeda agar terasa alami
            ai_move = choose_ai_move(board, 'b')
            if ai_move is None:
                # tidak ada langkah
                if is_in_check(board, 'b'):
                    game_over = True
                    game_over_message = 'Skakmat! Putih menang.'
                else:
                    game_over = True
                    game_over_message = 'Stalemate! Seri.'
            else:
                board = make_move(board, ai_move)
                last_move = ai_move
                # Cek akhir permainan untuk putih
                if not gen_legal_moves(board, 'w'):
                    if is_in_check(board, 'w'):
                        game_over = True
                        game_over_message = 'Skakmat! Hitam menang.'
                    else:
                        game_over = True
                        game_over_message = 'Stalemate! Seri.'
                else:
                    turn = 'w'

        # Gambar
        screen.fill((0, 0, 0))
        draw_board(screen)

        # Highlight raja yang sedang diserang
        in_check_square = None
        if is_in_check(board, turn):
            in_check_square = find_king(board, turn)

        draw_highlights(screen, selected, legal_for_selected, in_check_square, last_move)
        draw_pieces(screen, board, piece_font)
        draw_status(screen, status_text(), small_font)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
