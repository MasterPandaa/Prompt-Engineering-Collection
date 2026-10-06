import pygame
import sys
import copy
from typing import List, Tuple, Optional

# ==============================
# Konfigurasi
# ==============================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 60

# Warna
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
MOVE_HINT = (120, 180, 120)
SELECTION = (100, 149, 237)
TEXT_WHITE = (250, 250, 250)
TEXT_BLACK = (30, 30, 30)

# Nilai material untuk evaluasi AI
PIECE_VALUES = {
    'p': 100,
    'n': 320,
    'b': 330,
    'r': 500,
    'q': 900,
    'k': 20000,
}

# ==============================
# Utilitas Papan Catur
# ==============================
Board = List[List[str]]
Move = Tuple[int, int, int, int, Optional[str]]  # (r1, c1, r2, c2, promotion)


def create_initial_board() -> Board:
    # huruf kecil = hitam, huruf besar = putih, '.' = kosong
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


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def get_color(piece: str) -> Optional[str]:
    if piece == '.' or piece == '':
        return None
    return 'white' if piece.isupper() else 'black'


def is_enemy(piece: str, color: str) -> bool:
    pc = get_color(piece)
    return pc is not None and pc != color


def piece_letter(piece: str) -> str:
    return piece.lower()

# ==============================
# Generasi Gerakan
# ==============================

def get_pawn_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir_forward = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # maju satu
    nr, nc = row + dir_forward, col
    if in_bounds(nr, nc) and board[nr][nc] == '.':
        # promosi
        if (color == 'white' and nr == 0) or (color == 'black' and nr == 7):
            moves.append((row, col, nr, nc, 'Q'))
        else:
            moves.append((row, col, nr, nc, None))
        # dari posisi awal, bisa maju dua jika jalur kosong
        nr2 = row + 2 * dir_forward
        if row == start_row and in_bounds(nr2, nc) and board[nr2][nc] == '.':
            moves.append((row, col, nr2, nc, None))

    # tangkap diagonal
    for dc in (-1, 1):
        nr, nc = row + dir_forward, col + dc
        if in_bounds(nr, nc) and is_enemy(board[nr][nc], color):
            if (color == 'white' and nr == 0) or (color == 'black' and nr == 7):
                moves.append((row, col, nr, nc, 'Q'))
            else:
                moves.append((row, col, nr, nc, None))

    return moves


def get_knight_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for r_off, c_off in offsets:
        nr, nc = row + r_off, col + c_off
        if not in_bounds(nr, nc):
            continue
        target = board[nr][nc]
        if target == '.' or is_enemy(target, color):
            moves.append((row, col, nr, nc, None))
    return moves


def get_sliding_moves(board: Board, row: int, col: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target == '.':
                moves.append((row, col, nr, nc, None))
            else:
                if is_enemy(target, color):
                    moves.append((row, col, nr, nc, None))
                break
            nr += dr
            nc += dc
    return moves


def get_bishop_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return get_sliding_moves(board, row, col, color, directions)


def get_rook_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return get_sliding_moves(board, row, col, color, directions)


def get_queen_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    directions = [
        (-1, -1), (-1, 1), (1, -1), (1, 1),
        (-1, 0), (1, 0), (0, -1), (0, 1)
    ]
    return get_sliding_moves(board, row, col, color, directions)


def get_king_moves(board: Board, row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc):
                continue
            target = board[nr][nc]
            if target == '.' or is_enemy(target, color):
                moves.append((row, col, nr, nc, None))
    return moves


def get_moves_for_piece(board: Board, row: int, col: int) -> List[Move]:
    piece = board[row][col]
    if piece == '.':
        return []
    color = get_color(piece)
    letter = piece_letter(piece)
    if letter == 'p':
        return get_pawn_moves(board, row, col, color)
    if letter == 'n':
        return get_knight_moves(board, row, col, color)
    if letter == 'b':
        return get_bishop_moves(board, row, col, color)
    if letter == 'r':
        return get_rook_moves(board, row, col, color)
    if letter == 'q':
        return get_queen_moves(board, row, col, color)
    if letter == 'k':
        return get_king_moves(board, row, col, color)
    return []


def get_all_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            if get_color(piece) != color:
                continue
            for mv in get_moves_for_piece(board, r, c):
                r1, c1, r2, c2, promo = mv
                target = board[r2][c2]
                # Tidak boleh menabrak teman sendiri
                if target != '.' and get_color(target) == color:
                    continue
                moves.append(mv)
    return moves


# ==============================
# Aksi Papan (terapkan langkah, evaluasi)
# ==============================

def apply_move(board: Board, move: Move) -> Board:
    r1, c1, r2, c2, promo = move
    new_board = copy.deepcopy(board)
    piece = new_board[r1][c1]
    new_board[r1][c1] = '.'
    if promo is not None and piece_letter(piece) == 'p' and (r2 == 0 or r2 == 7):
        piece = promo if get_color(piece) == 'white' else promo.lower()
    new_board[r2][c2] = piece
    return new_board


def evaluate(board: Board) -> int:
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            val = PIECE_VALUES.get(piece_letter(piece), 0)
            score += val if piece.isupper() else -val
    return score


# ==============================
# AI Sederhana (Greedy / Minimax kedalaman 1)
# ==============================

def ai_choose_move(board: Board, color: str = 'black') -> Optional[Move]:
    moves = get_all_moves(board, color)
    if not moves:
        return None

    # Evaluasi kedalaman 1: pilih langkah yang memaksimalkan evaluasi untuk warna yang bermain
    # evaluate() positif menguntungkan putih. Jadi:
    # - Untuk putih: pilih move dengan skor tertinggi
    # - Untuk hitam: pilih move dengan skor terendah
    best_move = None
    best_score = None

    for mv in moves:
        new_board = apply_move(board, mv)
        sc = evaluate(new_board)
        if color == 'white':
            better = (best_score is None) or (sc > best_score)
        else:
            better = (best_score is None) or (sc < best_score)
        if better:
            best_score = sc
            best_move = mv

    return best_move


# ==============================
# Rendering Pygame
# ==============================

def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font, selected: Optional[Tuple[int, int]], legal_moves: List[Move]):
    # kotak
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

    # highlight legal moves
    for mv in legal_moves:
        _, _, r2, c2, _ = mv
        center = (c2 * SQUARE_SIZE + SQUARE_SIZE // 2, r2 * SQUARE_SIZE + SQUARE_SIZE // 2)
        pygame.draw.circle(screen, MOVE_HINT, center, 12)

    # highlight pilihan
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, SELECTION, rect, 4)

    # pieces menggunakan text (huruf)
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            is_white = piece.isupper()
            label = piece.upper()
            text_color = TEXT_BLACK if is_white else TEXT_WHITE
            # beri outline agar kontras
            render_and_blit_text(screen, label, font, c, r, text_color, outline=True)


def render_and_blit_text(screen: pygame.Surface, text: str, font: pygame.font.Font, col: int, row: int, color, outline: bool = True):
    x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    y = row * SQUARE_SIZE + SQUARE_SIZE // 2
    if outline:
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            surf_o = font.render(text, True, (0, 0, 0))
            rect_o = surf_o.get_rect(center=(x + ox, y + oy))
            screen.blit(surf_o, rect_o)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)


# ==============================
# Input & Game Loop
# ==============================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catur Pygame (Huruf)")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 44, bold=True)

    board = create_initial_board()
    selected: Optional[Tuple[int, int]] = None
    legal_moves: List[Move] = []
    turn = 'white'  # giliran mulai

    running = True
    ai_think_delay = 250  # ms
    ai_pending = False
    ai_timer_start = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = create_initial_board()
                    selected = None
                    legal_moves = []
                    turn = 'white'
                    ai_pending = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'white':  # pemain = putih
                    mx, my = pygame.mouse.get_pos()
                    c = mx // SQUARE_SIZE
                    r = my // SQUARE_SIZE
                    if selected is None:
                        # pilih bidak putih
                        piece = board[r][c]
                        if piece != '.' and get_color(piece) == 'white':
                            selected = (r, c)
                            # filter gerak valid dari petak ini
                            legal_moves = []
                            for mv in get_moves_for_piece(board, r, c):
                                r1, c1, r2, c2, promo = mv
                                target = board[r2][c2]
                                if target != '.' and get_color(target) == 'white':
                                    continue
                                legal_moves.append(mv)
                        else:
                            selected = None
                            legal_moves = []
                    else:
                        # coba pindahkan ke petak klik
                        dest_r, dest_c = r, c
                        chosen = None
                        for mv in legal_moves:
                            if mv[2] == dest_r and mv[3] == dest_c:
                                chosen = mv
                                break
                        if chosen is not None:
                            board = apply_move(board, chosen)
                            selected = None
                            legal_moves = []
                            turn = 'black'
                            ai_pending = True
                            ai_timer_start = pygame.time.get_ticks()
                        else:
                            # klik lain: jika pilih bidak putih lain
                            piece = board[r][c]
                            if piece != '.' and get_color(piece) == 'white':
                                selected = (r, c)
                                legal_moves = []
                                for mv in get_moves_for_piece(board, r, c):
                                    r1, c1, r2, c2, promo = mv
                                    target = board[r2][c2]
                                    if target != '.' and get_color(target) == 'white':
                                        continue
                                    legal_moves.append(mv)
                            else:
                                selected = None
                                legal_moves = []

        # Giliran AI (hitam)
        if turn == 'black' and ai_pending:
            now = pygame.time.get_ticks()
            if now - ai_timer_start >= ai_think_delay:
                mv = ai_choose_move(board, 'black')
                if mv is not None:
                    board = apply_move(board, mv)
                # selesai giliran
                turn = 'white'
                ai_pending = False
                selected = None
                legal_moves = []

        # Render
        screen.fill((0, 0, 0))
        draw_board(screen, board, font, selected, legal_moves)

        # status text
        info_font = pygame.font.SysFont("arial", 20, bold=False)
        status = f"Giliran: {'Putih' if turn == 'white' else 'Hitam (AI)'} | Tekan R untuk reset"
        info_surf = info_font.render(status, True, (255, 255, 255))
        screen.blit(info_surf, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
