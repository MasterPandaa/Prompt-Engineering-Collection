import sys
import math
import pygame
from typing import List, Tuple, Optional

# ==========================
# Konfigurasi Tampilan
# ==========================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

# Warna
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
SELECTED = (186, 202, 68)
TEXT_BLACK = (30, 30, 30)
TEXT_WHITE = (230, 230, 230)
BG = (25, 25, 25)

# Nilai material untuk evaluasi sederhana
PIECE_VALUES = {
    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0,
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0,
}

# ==========================
# Representasi Papan
# Huruf kecil = hitam, huruf besar = putih, '.' = kosong
# Baris 0 di atas layar, baris 7 di bawah layar
# ==========================

def initial_board() -> List[List[str]]:
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

# ==========================
# Utilitas dasar
# ==========================

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def piece_color(p: str) -> Optional[str]:
    if p == '.':
        return None
    return 'white' if p.isupper() else 'black'


def is_enemy(p: str, color: str) -> bool:
    if p == '.':
        return False
    return piece_color(p) != color


def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]

# ==========================
# Gerakan bidak
# ==========================

Move = Tuple[int, int, int, int]  # (r1, c1, r2, c2)


def get_pawn_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir_ = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # Maju 1
    nr, nc = r + dir_, c
    if in_bounds(nr, nc) and board[nr][nc] == '.':
        moves.append((r, c, nr, nc))
        # Maju 2 dari posisi awal
        nr2 = r + 2 * dir_
        if r == start_row and board[nr2][nc] == '.':
            moves.append((r, c, nr2, nc))

    # Tangkap diagonal
    for dc in (-1, 1):
        nr, nc = r + dir_, c + dc
        if in_bounds(nr, nc) and is_enemy(board[nr][nc], color):
            moves.append((r, c, nr, nc))

    return moves


def get_knight_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        target = board[nr][nc]
        if target == '.' or is_enemy(target, color):
            moves.append((r, c, nr, nc))
    return moves


def sliding_moves(board: List[List[str]], r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target == '.':
                moves.append((r, c, nr, nc))
            else:
                if is_enemy(target, color):
                    moves.append((r, c, nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def get_bishop_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return sliding_moves(board, r, c, color, dirs)


def get_rook_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return sliding_moves(board, r, c, color, dirs)


def get_queen_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    dirs = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # rook-like
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # bishop-like
    ]
    return sliding_moves(board, r, c, color, dirs)


def get_king_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            target = board[nr][nc]
            if target == '.' or is_enemy(target, color):
                moves.append((r, c, nr, nc))
    return moves


def get_piece_moves(board: List[List[str]], r: int, c: int) -> List[Move]:
    piece = board[r][c]
    if piece == '.':
        return []
    color = piece_color(piece)
    assert color in ('white', 'black')

    if piece in ('P', 'p'):
        return get_pawn_moves(board, r, c, color)
    if piece in ('N', 'n'):
        return get_knight_moves(board, r, c, color)
    if piece in ('B', 'b'):
        return get_bishop_moves(board, r, c, color)
    if piece in ('R', 'r'):
        return get_rook_moves(board, r, c, color)
    if piece in ('Q', 'q'):
        return get_queen_moves(board, r, c, color)
    if piece in ('K', 'k'):
        return get_king_moves(board, r, c, color)
    return []


def get_legal_moves(board: List[List[str]], turn: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == '.' or piece_color(p) != turn:
                continue
            for mv in get_piece_moves(board, r, c):
                r1, c1, r2, c2 = mv
                dest = board[r2][c2]
                # Validasi dasar: tidak menabrak teman sendiri sudah ditangani di generator gerak
                # Di sini bisa tambahkan validasi tingkat lanjut (misal raja tidak dalam skak), tapi tidak diwajibkan
                moves.append(mv)
    return moves


# ==========================
# Mekanisme Pindah & Evaluasi
# ==========================

def make_move(board: List[List[str]], move: Move) -> Tuple[List[List[str]], Optional[str], Optional[str]]:
    r1, c1, r2, c2 = move
    newb = clone_board(board)
    moved = newb[r1][c1]
    captured = newb[r2][c2] if newb[r2][c2] != '.' else None
    newb[r2][c2] = moved
    newb[r1][c1] = '.'

    # Promosi pion sederhana -> Queen
    if moved == 'P' and r2 == 0:
        newb[r2][c2] = 'Q'
    elif moved == 'p' and r2 == ROWS - 1:
        newb[r2][c2] = 'q'

    return newb, moved, captured


def evaluate_board(board: List[List[str]]) -> int:
    # Nilai positif menguntungkan putih, negatif menguntungkan hitam
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == '.':
                continue
            val = PIECE_VALUES[p]
            score += val if p.isupper() else -val
    return score


def ai_choose_greedy(board: List[List[str]], turn: str) -> Optional[Move]:
    # Greedy: pilih langkah yang memaksimalkan evaluasi dari perspektif pemain yang melangkah
    best_move: Optional[Move] = None
    best_score = -math.inf if turn == 'white' else math.inf

    for mv in get_legal_moves(board, turn):
        newb, _, _ = make_move(board, mv)
        sc = evaluate_board(newb)
        if turn == 'white':
            if sc > best_score:
                best_score = sc
                best_move = mv
        else:
            if sc < best_score:
                best_score = sc
                best_move = mv
    return best_move

# ==========================
# Rendering
# ==========================

def draw_board(surface: pygame.Surface):
    surface.fill(BG)
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(surface, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlights(surface: pygame.Surface, selected: Optional[Tuple[int, int]], moves: List[Move]):
    if selected is not None:
        sr, sc = selected
        pygame.draw.rect(surface, SELECTED, pygame.Rect(sc * SQ_SIZE, sr * SQ_SIZE, SQ_SIZE, SQ_SIZE), 0)
    for (_, _, r2, c2) in moves:
        pygame.draw.rect(surface, HIGHLIGHT, pygame.Rect(c2 * SQ_SIZE, r2 * SQ_SIZE, SQ_SIZE, SQ_SIZE), 0)


def draw_pieces(surface: pygame.Surface, board: List[List[str]], font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == '.':
                continue
            txt_color = TEXT_WHITE if p.isupper() else TEXT_BLACK
            text_surf = font.render(p, True, txt_color)
            rect = text_surf.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
            surface.blit(text_surf, rect)


# ==========================
# Main Game Loop
# ==========================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Catur Pygame (Huruf)')
    clock = pygame.time.Clock()

    # Gunakan font monospace agar rapi
    try:
        font = pygame.font.SysFont('consolas', SQ_SIZE - 20, bold=True)
    except Exception:
        font = pygame.font.SysFont(None, SQ_SIZE - 20, bold=True)

    board = initial_board()
    turn = 'white'  # putih (manusia) mulai

    selected: Optional[Tuple[int, int]] = None
    candidate_moves: List[Move] = []

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    board = initial_board()
                    turn = 'white'
                    selected = None
                    candidate_moves = []
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if turn == 'white' and event.button == 1:
                    mx, my = event.pos
                    c = mx // SQ_SIZE
                    r = my // SQ_SIZE

                    if selected is None:
                        # pilih bidak
                        if piece_color(board[r][c]) == 'white':
                            selected = (r, c)
                            # Filter hanya gerakan dari petak ini
                            candidate_moves = [mv for mv in get_piece_moves(board, r, c)
                                               if piece_color(board[r][c]) == 'white']
                        else:
                            selected = None
                            candidate_moves = []
                    else:
                        # coba gerakkan ke petak tujuan jika valid
                        legal = [mv for mv in candidate_moves if mv[2] == r and mv[3] == c]
                        if legal:
                            mv = legal[0]
                            board, _, _ = make_move(board, mv)
                            turn = 'black'
                        # reset seleksi apapun hasilnya
                        selected = None
                        candidate_moves = []

        # AI gerak (hitam) - sederhana greedy
        if running and turn == 'black':
            ai_move = ai_choose_greedy(board, 'black')
            if ai_move is None:
                # Tidak ada gerakan: selesai (stale/mate sederhana)
                turn = 'white'
            else:
                board, _, _ = make_move(board, ai_move)
                turn = 'white'

        # Render
        draw_board(screen)
        draw_highlights(screen, selected, candidate_moves)
        draw_pieces(screen, board, font)

        # Info bar sederhana (opsional): giliran
        info_font = pygame.font.SysFont('consolas', 18)
        info_text = f"Giliran: {'Putih' if turn == 'white' else 'Hitam (AI)'} | R untuk reset | ESC untuk keluar"
        info_surf = info_font.render(info_text, True, (240, 240, 240))
        screen.blit(info_surf, (10, HEIGHT - 24))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
