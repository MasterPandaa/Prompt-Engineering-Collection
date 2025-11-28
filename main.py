import pygame
import sys
from typing import List, Tuple, Optional

# ============================
# Konfigurasi dan Konstanta
# ============================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
TILE_SIZE = WIDTH // COLS
FPS = 60

# Warna
LIGHT = (240, 217, 181)   # light square
DARK = (181, 136, 99)      # dark square
HIGHLIGHT = (246, 246, 105)
MOVE_HIGHLIGHT = (120, 170, 120)
SELECT_COLOR = (100, 140, 200)
TEXT_WHITE = (245, 245, 245)
TEXT_BLACK = (25, 25, 25)
UI_BG = (30, 30, 35)
UI_TEXT = (235, 235, 240)

# Nilai material untuk evaluasi AI sederhana
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000,
}

# ============================
# Representasi Papan
# huruf kecil = hitam, huruf besar = putih, '.' = kosong
# ============================

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

# ============================
# Utilitas
# ============================

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def get_color(piece: str) -> Optional[str]:
    if piece == '.' or piece == '':
        return None
    return 'white' if piece.isupper() else 'black'


def is_enemy(piece: str, color: str) -> bool:
    pcol = get_color(piece)
    return pcol is not None and pcol != color


def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]


# ============================
# Gerakan Bidak
# ============================

def get_pawn_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # langkah maju 1
    fr, fc = r + direction, c
    if in_bounds(fr, fc) and board[fr][fc] == '.':
        moves.append((fr, fc))
        # langkah awal 2
        if r == start_row:
            fr2 = r + 2 * direction
            if in_bounds(fr2, fc) and board[fr2][fc] == '.':
                moves.append((fr2, fc))

    # tangkap diagonal
    for dc in (-1, 1):
        tr, tc = r + direction, c + dc
        if in_bounds(tr, tc) and is_enemy(board[tr][tc], color):
            moves.append((tr, tc))

    # Catatan: en passant tidak diimplementasikan untuk kesederhanaan
    return moves


def get_knight_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in offsets:
        tr, tc = r + dr, c + dc
        if not in_bounds(tr, tc):
            continue
        target = board[tr][tc]
        if target == '.' or is_enemy(target, color):
            moves.append((tr, tc))
    return moves


def ray_moves(board: List[List[str]], r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    moves = []
    for dr, dc in directions:
        tr, tc = r + dr, c + dc
        while in_bounds(tr, tc):
            target = board[tr][tc]
            if target == '.':
                moves.append((tr, tc))
            else:
                if is_enemy(target, color):
                    moves.append((tr, tc))
                break
            tr += dr
            tc += dc
    return moves


def get_bishop_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return ray_moves(board, r, c, color, dirs)


def get_rook_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return ray_moves(board, r, c, color, dirs)


def get_queen_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
    return ray_moves(board, r, c, color, dirs)


def get_king_moves(board: List[List[str]], r: int, c: int, color: str) -> List[Tuple[int, int]]:
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            tr, tc = r + dr, c + dc
            if not in_bounds(tr, tc):
                continue
            target = board[tr][tc]
            if target == '.' or is_enemy(target, color):
                moves.append((tr, tc))
    # Catatan: Tidak ada castling untuk kesederhanaan
    return moves


def get_moves_for_piece(board: List[List[str]], r: int, c: int) -> List[Tuple[int, int]]:
    piece = board[r][c]
    if piece == '.':
        return []
    color = get_color(piece)
    p = piece.upper()
    if p == 'P':
        return get_pawn_moves(board, r, c, color)
    if p == 'N':
        return get_knight_moves(board, r, c, color)
    if p == 'B':
        return get_bishop_moves(board, r, c, color)
    if p == 'R':
        return get_rook_moves(board, r, c, color)
    if p == 'Q':
        return get_queen_moves(board, r, c, color)
    if p == 'K':
        return get_king_moves(board, r, c, color)
    return []


def all_moves_for_color(board: List[List[str]], color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            if get_color(piece) != color:
                continue
            for (tr, tc) in get_moves_for_piece(board, r, c):
                # validasi tidak menabrak teman sendiri sudah dipastikan oleh generator
                moves.append(((r, c), (tr, tc)))
    return moves


# ============================
# Evaluasi dan AI Greedy
# ============================

def evaluate_material(board: List[List[str]]) -> int:
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            val = PIECE_VALUES.get(piece, 0)
            if piece.isupper():  # white
                score += val
            else:
                score -= val
    return score


def make_move(board: List[List[str]], src: Tuple[int, int], dst: Tuple[int, int]) -> List[List[str]]:
    nr, nc = dst
    sr, sc = src
    new_board = clone_board(board)
    piece = new_board[sr][sc]
    new_board[sr][sc] = '.'

    # Promosi sederhana: otomatis promosi ke Queen
    if piece.upper() == 'P':
        if piece.isupper() and nr == 0:
            new_board[nr][nc] = 'Q'
            return new_board
        if piece.islower() and nr == ROWS - 1:
            new_board[nr][nc] = 'q'
            return new_board

    new_board[nr][nc] = piece
    return new_board


def greedy_ai_move(board: List[List[str]], color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    moves = all_moves_for_color(board, color)
    if not moves:
        return None

    best_move = None
    best_score = None

    for src, dst in moves:
        nb = make_move(board, src, dst)
        score = evaluate_material(nb)
        # Jika AI hitam, ia ingin meminimalkan skor; jika putih memaksimalkan
        if color == 'black':
            score = -score
        if best_score is None or score > best_score:
            best_score = score
            best_move = (src, dst)

    return best_move


# ============================
# Rendering
# ============================

def draw_board(screen: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)


def draw_highlights(screen: pygame.Surface, selected: Optional[Tuple[int, int]], moves: List[Tuple[int, int]]):
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * TILE_SIZE, sr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((*SELECT_COLOR, 80))
        screen.blit(s, rect.topleft)

    for (r, c) in moves:
        rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((*MOVE_HIGHLIGHT, 80))
        screen.blit(s, rect.topleft)


def draw_pieces(screen: pygame.Surface, board: List[List[str]], font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            text_color = TEXT_WHITE if piece.isupper() else TEXT_BLACK
            label = piece.upper()  # gunakan huruf untuk kesederhanaan
            surf = font.render(label, True, text_color)
            rect = surf.get_rect(center=(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(surf, rect)


def draw_ui_bar(screen: pygame.Surface, turn: str, info_text: str, ui_font: pygame.font.Font):
    # Bar bawah sederhana
    bar_height = 36
    rect = pygame.Rect(0, HEIGHT - bar_height, WIDTH, bar_height)
    pygame.draw.rect(screen, UI_BG, rect)

    text = f"Giliran: {'Putih' if turn == 'white' else 'Hitam'}  |  {info_text}"
    surf = ui_font.render(text, True, UI_TEXT)
    screen.blit(surf, (10, HEIGHT - bar_height + 8))


# ============================
# Game Loop
# ============================

def square_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    if y >= HEIGHT:
        return None
    c = x // TILE_SIZE
    r = y // TILE_SIZE
    if in_bounds(r, c):
        return (r, c)
    return None


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catur - Pygame (Human vs AI)")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, int(TILE_SIZE * 0.6), bold=True)
    ui_font = pygame.font.SysFont(None, 24)

    board = initial_board()
    turn = 'white'  # pemain manusia
    selected: Optional[Tuple[int, int]] = None
    legal_moves_for_selected: List[Tuple[int, int]] = []
    info_text = "Klik bidak putih untuk bergerak."

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 'white':
                    sq = square_from_mouse(event.pos)
                    if sq is None:
                        continue
                    r, c = sq
                    # Jika belum memilih, pilih bidak putih
                    if selected is None:
                        if board[r][c] != '.' and get_color(board[r][c]) == 'white':
                            selected = (r, c)
                            # filter moves agar tidak mendarat di teman sendiri (sudah aman dari generator)
                            legal_moves_for_selected = get_moves_for_piece(board, r, c)
                        else:
                            info_text = "Pilih bidak putih Anda."
                    else:
                        # Coba lakukan langkah
                        if (r, c) in legal_moves_for_selected:
                            board = make_move(board, selected, (r, c))
                            selected = None
                            legal_moves_for_selected = []
                            turn = 'black'
                            info_text = "AI berpikir..."
                        else:
                            # klik ulang: jika klik teman sendiri, ganti seleksi
                            if board[r][c] != '.' and get_color(board[r][c]) == 'white':
                                selected = (r, c)
                                legal_moves_for_selected = get_moves_for_piece(board, r, c)
                            else:
                                # batal seleksi
                                selected = None
                                legal_moves_for_selected = []

        # Giliran AI
        if turn == 'black':
            ai_move = greedy_ai_move(board, 'black')
            if ai_move is None:
                info_text = "AI tidak punya langkah. Permainan berakhir."
            else:
                board = make_move(board, ai_move[0], ai_move[1])
                info_text = "Giliran Anda."
            turn = 'white'

        # Render
        draw_board(screen)
        draw_highlights(screen, selected, legal_moves_for_selected)
        draw_pieces(screen, board, font)
        draw_ui_bar(screen, turn, info_text, ui_font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()
