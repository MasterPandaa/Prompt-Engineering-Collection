import sys
import random
import pygame
from typing import List, Optional, Tuple

# ---------- Konfigurasi ----------
TILE_SIZE = 80
BOARD_SIZE = 8
MARGIN = 40  # ruang untuk koordinat file/rank
WIDTH = MARGIN * 2 + TILE_SIZE * BOARD_SIZE
HEIGHT = MARGIN * 2 + TILE_SIZE * BOARD_SIZE
FPS = 60

# Warna
WHITE = (240, 240, 240)
BLACK = (10, 10, 10)
LIGHT_SQUARE = (235, 236, 208)
DARK_SQUARE = (119, 149, 86)
SELECT_COLOR = (246, 246, 105)
MOVE_DOT = (33, 33, 33)
CAPTURE_HIGHLIGHT = (200, 60, 60)
LAST_MOVE_COLOR = (246, 246, 105)
TEXT_COLOR = (30, 30, 30)

# Unicode chess pieces (font harus mendukung). Kita akan gunakan font default pygame yang umumnya cukup.
UNICODE_PIECES = {
    ('w', 'K'): '\u2654', ('w', 'Q'): '\u2655', ('w', 'R'): '\u2656', ('w', 'B'): '\u2657', ('w', 'N'): '\u2658', ('w', 'P'): '\u2659',
    ('b', 'K'): '\u265A', ('b', 'Q'): '\u265B', ('b', 'R'): '\u265C', ('b', 'B'): '\u265D', ('b', 'N'): '\u265E', ('b', 'P'): '\u265F',
}

PIECE_VALUES = {'K': 10000, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'P': 100}

Piece = Optional[Tuple[str, str]]  # ('w'/'b', 'K','Q','R','B','N','P') atau None
Board = List[List[Piece]]
Move = Tuple[int, int, int, int, Optional[str]]  # (r1, c1, r2, c2, promo)


def create_start_position() -> Board:
    board: Board = [[None for _ in range(8)] for __ in range(8)]
    # Bidak hitam (atas)
    board[0] = [
        ('b', 'R'), ('b', 'N'), ('b', 'B'), ('b', 'Q'), ('b', 'K'), ('b', 'B'), ('b', 'N'), ('b', 'R')
    ]
    board[1] = [('b', 'P') for _ in range(8)]
    # Bidak putih (bawah)
    board[6] = [('w', 'P') for _ in range(8)]
    board[7] = [
        ('w', 'R'), ('w', 'N'), ('w', 'B'), ('w', 'Q'), ('w', 'K'), ('w', 'B'), ('w', 'N'), ('w', 'R')
    ]
    return board


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def is_enemy(p: Piece, color: str) -> bool:
    return p is not None and p[0] != color


def is_empty(p: Piece) -> bool:
    return p is None


# --------- Generator Langkah Pseudo-Legal ---------

def generate_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p is None or p[0] != color:
                continue
            moves.extend(get_piece_moves(board, r, c))
    return moves


def get_piece_moves(board: Board, r: int, c: int) -> List[Move]:
    piece = board[r][c]
    if piece is None:
        return []
    color, kind = piece
    if kind == 'P':
        return pawn_moves(board, r, c, color)
    elif kind == 'N':
        return knight_moves(board, r, c, color)
    elif kind == 'B':
        return sliding_moves(board, r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)])
    elif kind == 'R':
        return sliding_moves(board, r, c, color, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)])
    elif kind == 'Q':
        return sliding_moves(board, r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])
    elif kind == 'K':
        return king_moves(board, r, c, color)
    return []


def pawn_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir_ = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    one = (r + dir_, c)
    two = (r + 2 * dir_, c)

    # Maju 1
    if in_bounds(*one) and is_empty(board[one[0]][one[1]]):
        promo = 'Q' if (one[0] == 0 or one[0] == 7) else None
        moves.append((r, c, one[0], one[1], promo))
        # Maju 2 dari baris awal
        if r == start_row and in_bounds(*two) and is_empty(board[two[0]][two[1]]):
            moves.append((r, c, two[0], two[1], None))

    # Tangkap diagonal
    for dc in (-1, 1):
        rr, cc = r + dir_, c + dc
        if in_bounds(rr, cc) and is_enemy(board[rr][cc], color):
            promo = 'Q' if (rr == 0 or rr == 7) else None
            moves.append((r, c, rr, cc, promo))

    return moves


def knight_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    res: List[Move] = []
    jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in jumps:
        rr, cc = r + dr, c + dc
        if not in_bounds(rr, cc):
            continue
        target = board[rr][cc]
        if is_empty(target) or is_enemy(target, color):
            res.append((r, c, rr, cc, None))
    return res


def sliding_moves(board: Board, r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    res: List[Move] = []
    for dr, dc in directions:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            target = board[rr][cc]
            if is_empty(target):
                res.append((r, c, rr, cc, None))
            else:
                if is_enemy(target, color):
                    res.append((r, c, rr, cc, None))
                break
            rr += dr
            cc += dc
    return res


def king_moves(board: Board, r: int, c: int, color: str) -> List[Move]:
    res: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not in_bounds(rr, cc):
                continue
            target = board[rr][cc]
            if is_empty(target) or is_enemy(target, color):
                res.append((r, c, rr, cc, None))
    return res


# --------- Manipulasi Papan ---------

def make_move(board: Board, move: Move) -> Optional[Piece]:
    r1, c1, r2, c2, promo = move
    moved = board[r1][c1]
    captured = board[r2][c2]
    board[r2][c2] = moved
    board[r1][c1] = None
    # Promosi pion (otomatis jadi Queen)
    if moved and moved[1] == 'P' and promo is not None:
        board[r2][c2] = (moved[0], promo)
    return captured


# --------- Rendering ---------

def draw_board(screen: pygame.Surface, font: pygame.font.Font, board: Board, selected: Optional[Tuple[int, int]], legal: List[Tuple[int, int]], last_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]]):
    screen.fill(WHITE)

    # Gambar papan
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x = MARGIN + c * TILE_SIZE
            y = MARGIN + r * TILE_SIZE
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    # Highlight last move
    if last_move is not None:
        (r1, c1), (r2, c2) = last_move
        for rr, cc in [(r1, c1), (r2, c2)]:
            x = MARGIN + cc * TILE_SIZE
            y = MARGIN + rr * TILE_SIZE
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((*LAST_MOVE_COLOR, 90))
            screen.blit(s, (x, y))

    # Highlight selected
    if selected is not None:
        sr, sc = selected
        x = MARGIN + sc * TILE_SIZE
        y = MARGIN + sr * TILE_SIZE
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((*SELECT_COLOR, 120))
        screen.blit(s, (x, y))

    # Legal move hints
    for rr, cc in legal:
        x = MARGIN + cc * TILE_SIZE
        y = MARGIN + rr * TILE_SIZE
        center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
        if board[rr][cc] is None:
            pygame.draw.circle(screen, MOVE_DOT, center, 8)
        else:
            pygame.draw.rect(screen, (*CAPTURE_HIGHLIGHT, 140), (x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8), 3)

    # Gambar bidak
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece is None:
                continue
            ch = UNICODE_PIECES[piece]
            text = font.render(ch, True, BLACK if piece[0] == 'b' else (30, 30, 30))
            text_rect = text.get_rect(center=(MARGIN + c * TILE_SIZE + TILE_SIZE // 2, MARGIN + r * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)

    # Gambar koordinat file/rank
    coord_font = pygame.font.SysFont(None, 18)
    files = 'abcdefgh'
    ranks = '87654321'
    # files
    for i in range(8):
        ftxt = coord_font.render(files[i], True, TEXT_COLOR)
        x = MARGIN + i * TILE_SIZE + TILE_SIZE // 2
        screen.blit(ftxt, ftxt.get_rect(center=(x, HEIGHT - MARGIN // 2)))
        screen.blit(ftxt, ftxt.get_rect(center=(x, MARGIN // 2)))
    # ranks
    for i in range(8):
        rtxt = coord_font.render(ranks[i], True, TEXT_COLOR)
        y = MARGIN + i * TILE_SIZE + TILE_SIZE // 2
        screen.blit(rtxt, rtxt.get_rect(center=(MARGIN // 2, y)))
        screen.blit(rtxt, rtxt.get_rect(center=(WIDTH - MARGIN // 2, y)))


# --------- AI Sederhana ---------

def choose_ai_move(board: Board, color: str) -> Optional[Move]:
    moves = generate_moves(board, color)
    if not moves:
        return None

    # Pilih capture terbaik berdasarkan nilai target; jika tie, random di antara terbaik
    best_value = -1
    best_moves: List[Move] = []
    for mv in moves:
        r1, c1, r2, c2, promo = mv
        target = board[r2][c2]
        if target is not None:
            v = PIECE_VALUES[target[1]]
            if v > best_value:
                best_value = v
                best_moves = [mv]
            elif v == best_value:
                best_moves.append(mv)
    if best_moves:
        return random.choice(best_moves)

    # Jika tidak ada capture, acak dari semua langkah
    return random.choice(moves)


# --------- Input & Utilitas ---------

def square_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    mx, my = pos
    if mx < MARGIN or my < MARGIN or mx >= WIDTH - MARGIN or my >= HEIGHT - MARGIN:
        return None
    c = (mx - MARGIN) // TILE_SIZE
    r = (my - MARGIN) // TILE_SIZE
    if in_bounds(r, c):
        return int(r), int(c)
    return None


# --------- Main Loop ---------

def main():
    pygame.init()
    pygame.display.set_caption('Catur - Pygame (Manusia vs AI)')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font besar untuk bidak. Ukuran disesuaikan agar muat dalam kotak.
    piece_font = pygame.font.SysFont(None, int(TILE_SIZE * 0.8))

    board = create_start_position()
    turn = 'w'  # pemain manusia = putih; AI = hitam

    selected: Optional[Tuple[int, int]] = None
    legal_targets: List[Tuple[int, int]] = []
    last_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # reset
                    board = create_start_position()
                    turn = 'w'
                    selected = None
                    legal_targets = []
                    last_move = None
                    game_over = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                if turn == 'w':
                    sq = square_from_mouse(event.pos)
                    if sq is None:
                        selected = None
                        legal_targets = []
                    else:
                        r, c = sq
                        piece = board[r][c]
                        # Jika belum memilih dan klik bidak sendiri -> select
                        if selected is None:
                            if piece is not None and piece[0] == 'w':
                                selected = (r, c)
                                # hitung legal targets dari piece ini
                                legal_moves = get_piece_moves(board, r, c)
                                legal_targets = [(mv[2], mv[3]) for mv in legal_moves]
                            else:
                                selected = None
                                legal_targets = []
                        else:
                            # Sudah ada yang dipilih -> cek apakah klik target legal
                            sr, sc = selected
                            moves_from_selected = get_piece_moves(board, sr, sc)
                            chosen: Optional[Move] = None
                            for mv in moves_from_selected:
                                if mv[2] == r and mv[3] == c:
                                    chosen = mv
                                    break
                            if chosen is not None:
                                make_move(board, chosen)
                                last_move = ((sr, sc), (r, c))
                                selected = None
                                legal_targets = []
                                # ganti giliran ke AI
                                turn = 'b'
                            else:
                                # kalau klik bidak sendiri yang lain, ganti pilihan
                                if piece is not None and piece[0] == 'w':
                                    selected = (r, c)
                                    legal_moves = get_piece_moves(board, r, c)
                                    legal_targets = [(mv[2], mv[3]) for mv in legal_moves]
                                else:
                                    # klik tempat lain yang tidak legal
                                    selected = None
                                    legal_targets = []

        # Giliran AI (hitam)
        if not game_over and turn == 'b':
            ai_move = choose_ai_move(board, 'b')
            if ai_move is None:
                game_over = True
            else:
                r1, c1, r2, c2, _ = ai_move
                make_move(board, ai_move)
                last_move = ((r1, c1), (r2, c2))
                turn = 'w'

        # Cek akhir permainan sederhana: jika salah satu pihak tidak punya langkah
        if not game_over:
            if turn == 'w' and not generate_moves(board, 'w'):
                game_over = True
            elif turn == 'b' and not generate_moves(board, 'b'):
                game_over = True

        # Render
        draw_board(screen, piece_font, board, selected, legal_targets, last_move)

        if game_over:
            end_font = pygame.font.SysFont(None, 36)
            msg = 'Permainan Selesai'  # Kita tidak bedakan checkmate/stalemate pada versi sederhana ini
            text = end_font.render(msg + ' - Tekan R untuk restart', True, (200, 40, 40))
            screen.blit(text, text.get_rect(center=(WIDTH // 2, MARGIN // 2)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
