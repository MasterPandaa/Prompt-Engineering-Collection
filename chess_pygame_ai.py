import pygame
import sys
import random
from typing import List, Optional, Tuple

# -------------------------------------
# Konfigurasi UI
# -------------------------------------
BOARD_SIZE = 8
SQUARE_PIXELS = 80
MARGIN = 40
PANEL_HEIGHT = 60
WIDTH = BOARD_SIZE * SQUARE_PIXELS
HEIGHT = BOARD_SIZE * SQUARE_PIXELS + PANEL_HEIGHT

COLOR_LIGHT = (238, 238, 210)
COLOR_DARK = (118, 150, 86)
COLOR_BG = (30, 30, 30)
COLOR_TEXT = (240, 240, 240)
COLOR_HIGHLIGHT = (246, 246, 105)
COLOR_MOVE = (180, 180, 60)
COLOR_LAST_MOVE = (184, 134, 11)

# Unicode Chess Characters
UNICODE_PIECES = {
    'wK': '\u2654', 'wQ': '\u2655', 'wR': '\u2656', 'wB': '\u2657', 'wN': '\u2658', 'wP': '\u2659',
    'bK': '\u265A', 'bQ': '\u265B', 'bR': '\u265C', 'bB': '\u265D', 'bN': '\u265E', 'bP': '\u265F',
}

PIECE_VALUES = {
    'K': 10000,
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'P': 1,
}

Move = Tuple[int, int, int, int, bool]  # (r1, c1, r2, c2, promotion)


def new_game_board() -> List[List[Optional[str]]]:
    # Representasi papan: 8x8 list of lists, berisi kode 'wP', 'bK', dll atau None
    board: List[List[Optional[str]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Bidak hitam (atas)
    board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
    board[1] = ['bP'] * 8

    # Bidak putih (bawah)
    board[6] = ['wP'] * 8
    board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    return board


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def piece_color(piece: Optional[str]) -> Optional[str]:
    if piece is None:
        return None
    return piece[0]


def piece_type(piece: Optional[str]) -> Optional[str]:
    if piece is None:
        return None
    return piece[1]


# -------------------------------------
# Move Generation (pseudo-legal)
# -------------------------------------

def generate_all_moves(board: List[List[Optional[str]]], color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p is None or piece_color(p) != color:
                continue
            t = piece_type(p)
            if t == 'P':
                moves.extend(gen_pawn_moves(board, r, c, color))
            elif t == 'N':
                moves.extend(gen_knight_moves(board, r, c, color))
            elif t == 'B':
                moves.extend(gen_sliding_moves(board, r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)]))
            elif t == 'R':
                moves.extend(gen_sliding_moves(board, r, c, color, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)]))
            elif t == 'Q':
                moves.extend(gen_sliding_moves(board, r, c, color, directions=[
                    (-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)
                ]))
            elif t == 'K':
                moves.extend(gen_king_moves(board, r, c, color))
    return moves


def gen_pawn_moves(board: List[List[Optional[str]]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir_ = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    last_row = 0 if color == 'w' else 7

    # Maju 1
    nr, nc = r + dir_, c
    if in_bounds(nr, nc) and board[nr][nc] is None:
        promo = (nr == last_row)
        moves.append((r, c, nr, nc, promo))
        # Maju 2 dari posisi awal
        nr2 = r + 2 * dir_
        if r == start_row and board[nr2][nc] is None:
            moves.append((r, c, nr2, nc, False))

    # Makan diagonal kiri/kanan
    for dc in (-1, 1):
        nr, nc = r + dir_, c + dc
        if in_bounds(nr, nc) and board[nr][nc] is not None and piece_color(board[nr][nc]) != color:
            promo = (nr == last_row)
            moves.append((r, c, nr, nc, promo))

    return moves


def gen_knight_moves(board: List[List[Optional[str]]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        target = board[nr][nc]
        if target is None or piece_color(target) != color:
            moves.append((r, c, nr, nc, False))
    return moves


def gen_sliding_moves(board: List[List[Optional[str]]], r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target is None:
                moves.append((r, c, nr, nc, False))
            else:
                if piece_color(target) != color:
                    moves.append((r, c, nr, nc, False))
                break
            nr += dr
            nc += dc
    return moves


def gen_king_moves(board: List[List[Optional[str]]], r: int, c: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            target = board[nr][nc]
            if target is None or piece_color(target) != color:
                moves.append((r, c, nr, nc, False))
    return moves


# -------------------------------------
# Utilitas Eksekusi Langkah
# -------------------------------------

def apply_move(board: List[List[Optional[str]]], move: Move) -> Tuple[List[List[Optional[str]]], Optional[str]]:
    r1, c1, r2, c2, promo = move
    new_board = [row[:] for row in board]
    moving = new_board[r1][c1]
    captured = new_board[r2][c2]
    new_board[r2][c2] = moving
    new_board[r1][c1] = None

    # Promosi pion otomatis menjadi Queen
    if moving and piece_type(moving) == 'P' and promo:
        col = piece_color(moving)
        new_board[r2][c2] = f"{col}Q"

    return new_board, captured


def king_exists(board: List[List[Optional[str]]], color: str) -> bool:
    target = f"{color}K"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == target:
                return True
    return False


# -------------------------------------
# AI sederhana: pilih capture dengan nilai tertinggi, jika tidak ada pilih acak
# -------------------------------------

def choose_ai_move(board: List[List[Optional[str]]], color: str) -> Optional[Move]:
    moves = generate_all_moves(board, color)
    if not moves:
        return None

    best_score = -1
    best_moves: List[Move] = []

    for mv in moves:
        r1, c1, r2, c2, promo = mv
        target = board[r2][c2]
        score = 0
        if target is not None:
            t = piece_type(target)
            if t:
                score = PIECE_VALUES.get(t, 0)
        # Prefer promosi juga
        if promo:
            score += PIECE_VALUES['Q']

        if score > best_score:
            best_score = score
            best_moves = [mv]
        elif score == best_score:
            best_moves.append(mv)

    return random.choice(best_moves)


# -------------------------------------
# Rendering
# -------------------------------------

def draw_board(screen, font, board: List[List[Optional[str]]], selected: Optional[Tuple[int, int]], legal_moves: List[Move], last_move: Optional[Move], turn_color: str, status_text: str):
    screen.fill(COLOR_BG)

    # Panel atas
    panel_rect = pygame.Rect(0, 0, WIDTH, PANEL_HEIGHT)
    pygame.draw.rect(screen, COLOR_BG, panel_rect)

    text_surface = font.render(status_text, True, COLOR_TEXT)
    screen.blit(text_surface, (10, (PANEL_HEIGHT - text_surface.get_height()) // 2))

    # Papan
    offset_y = PANEL_HEIGHT
    legal_targets = {(m[2], m[3]) for m in legal_moves}

    # Highlight last move
    if last_move is not None:
        _, _, r2, c2, _ = last_move
    else:
        r2 = c2 = -1

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            is_light = (r + c) % 2 == 0
            color = COLOR_LIGHT if is_light else COLOR_DARK

            # Highlight selected
            if selected == (r, c):
                color = COLOR_HIGHLIGHT

            # Highlight last move destination
            if (r, c) == (r2, c2):
                color = COLOR_LAST_MOVE

            rect = pygame.Rect(c * SQUARE_PIXELS, offset_y + r * SQUARE_PIXELS, SQUARE_PIXELS, SQUARE_PIXELS)
            pygame.draw.rect(screen, color, rect)

            # Highlight legal targets
            if (r, c) in legal_targets:
                center = rect.center
                pygame.draw.circle(screen, COLOR_MOVE, center, 10)

            # Draw piece
            piece = board[r][c]
            if piece is not None:
                ch = UNICODE_PIECES.get(piece)
                if ch:
                    piece_font = piece_fonts['white'] if piece[0] == 'w' else piece_fonts['black']
                    surf = piece_font.render(ch, True, (20, 20, 20))
                    sw, sh = surf.get_size()
                    screen.blit(surf, (rect.x + (SQUARE_PIXELS - sw) // 2, rect.y + (SQUARE_PIXELS - sh) // 2))

    pygame.display.flip()


# -------------------------------------
# Main Loop
# -------------------------------------

def main():
    pygame.init()
    pygame.display.set_caption('Pygame Chess - Human vs Simple AI')

    global piece_fonts
    # Dua font: putih & hitam untuk style yang sedikit berbeda ketebalan
    piece_fonts = {
        'white': pygame.font.SysFont('segoe ui symbol', int(SQUARE_PIXELS * 0.8)),
        'black': pygame.font.SysFont('segoe ui symbol', int(SQUARE_PIXELS * 0.8)),
    }
    info_font = pygame.font.SysFont('consolas', 24)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    board = new_game_board()
    human_color = 'w'
    ai_color = 'b'
    turn = 'w'

    selected: Optional[Tuple[int, int]] = None
    legal_for_selected: List[Move] = []
    last_move: Optional[Move] = None

    game_over = False
    winner_text = ''

    ai_think_delay_ms = 200  # jeda kecil agar pergerakan AI terlihat
    ai_timer = 0

    while True:
        dt = clock.tick(60)
        status_text = ''

        # Cek kondisi game over (kings existence)
        white_king = king_exists(board, 'w')
        black_king = king_exists(board, 'b')
        if not white_king or not black_king:
            game_over = True
            winner_text = 'Hitam menang (♚ hilang)' if not white_king else 'Putih menang (♔ hilang)'

        if game_over:
            status_text = f"Game Over: {winner_text} | Tekan R untuk reset"
        else:
            status_text = f"Giliran: {'Putih' if turn == 'w' else 'Hitam'} | Klik untuk gerak, R reset"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset
                    board = new_game_board()
                    turn = 'w'
                    selected = None
                    legal_for_selected = []
                    last_move = None
                    game_over = False
                    winner_text = ''
                    ai_timer = 0
            if game_over:
                continue

            if turn == human_color and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < PANEL_HEIGHT:
                    # klik pada panel, abaikan
                    pass
                else:
                    row = (my - PANEL_HEIGHT) // SQUARE_PIXELS
                    col = mx // SQUARE_PIXELS
                    if not in_bounds(row, col):
                        continue

                    if selected is None:
                        # pilih jika bidak milik manusia
                        p = board[row][col]
                        if p is not None and piece_color(p) == human_color:
                            selected = (row, col)
                            # filter moves untuk bidak ini
                            all_moves = generate_all_moves(board, human_color)
                            legal_for_selected = [m for m in all_moves if (m[0], m[1]) == selected]
                        else:
                            selected = None
                            legal_for_selected = []
                    else:
                        # jika klik target yang legal -> jalankan
                        chosen: Optional[Move] = None
                        for m in legal_for_selected:
                            if (m[2], m[3]) == (row, col):
                                chosen = m
                                break
                        if chosen is not None:
                            board, _ = apply_move(board, chosen)
                            last_move = chosen
                            selected = None
                            legal_for_selected = []
                            turn = ai_color
                            ai_timer = 0
                        else:
                            # pilih ulang jika klik bidak sendiri
                            p = board[row][col]
                            if p is not None and piece_color(p) == human_color:
                                selected = (row, col)
                                all_moves = generate_all_moves(board, human_color)
                                legal_for_selected = [m for m in all_moves if (m[0], m[1]) == selected]
                            else:
                                selected = None
                                legal_for_selected = []

        # Giliran AI
        if not game_over and turn == ai_color:
            ai_timer += dt
            if ai_timer >= ai_think_delay_ms:
                mv = choose_ai_move(board, ai_color)
                if mv is None:
                    game_over = True
                    winner_text = 'Stalemate (AI tidak punya langkah)'
                else:
                    board, _ = apply_move(board, mv)
                    last_move = mv
                    turn = human_color
                ai_timer = 0

        draw_board(
            screen=screen,
            font=info_font,
            board=board,
            selected=selected,
            legal_moves=legal_for_selected,
            last_move=last_move,
            turn_color=turn,
            status_text=status_text,
        )


if __name__ == '__main__':
    main()
