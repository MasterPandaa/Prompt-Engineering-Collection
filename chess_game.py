import pygame
import sys
from copy import deepcopy

# -------------------------------------------------------------
# Konstanta UI
# -------------------------------------------------------------
TILE_SIZE = 80
BOARD_SIZE = 8
MARGIN = 20
WIDTH = TILE_SIZE * BOARD_SIZE
HEIGHT = TILE_SIZE * BOARD_SIZE + MARGIN * 2
LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 0)
MOVE_DOT_COLOR = (30, 144, 255)
BG_COLOR = (32, 32, 32)
WHITE_PIECE_COLOR = (240, 240, 240)
BLACK_PIECE_COLOR = (16, 16, 16)
TEXT_COLOR = (220, 220, 220)

# -------------------------------------------------------------
# Representasi papan huruf
# - huruf kecil = hitam, huruf besar = putih, '.' = kosong
# -------------------------------------------------------------

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

# -------------------------------------------------------------
# Utilitas
# -------------------------------------------------------------

def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def is_empty(board, r, c):
    return board[r][c] == '.'

def color_of(piece):
    if piece == '.':
        return None
    return 'white' if piece.isupper() else 'black'


def is_enemy(piece_a, piece_b):
    ca = color_of(piece_a)
    cb = color_of(piece_b)
    return piece_b != '.' and ca and cb and ca != cb


def is_friend(piece_a, piece_b):
    ca = color_of(piece_a)
    cb = color_of(piece_b)
    return piece_b != '.' and ca and cb and ca == cb

# -------------------------------------------------------------
# Gerakan per bidak
# -------------------------------------------------------------

def get_pawn_moves(board, r, c, color):
    moves = []
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1

    # Maju 1
    nr = r + direction
    if in_bounds(nr, c) and is_empty(board, nr, c):
        moves.append((r, c, nr, c))
        # Maju 2 dari posisi awal
        nr2 = r + 2 * direction
        if r == start_row and is_empty(board, nr2, c):
            moves.append((r, c, nr2, c))

    # Makan serong kiri/kanan
    for dc in (-1, 1):
        nc = c + dc
        nr = r + direction
        if in_bounds(nr, nc) and is_enemy(board[r][c], board[nr][nc]):
            moves.append((r, c, nr, nc))

    return moves


def get_knight_moves(board, r, c, color):
    moves = []
    offsets = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 1)
    ]
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        target = board[nr][nc]
        if target == '.' or is_enemy(board[r][c], target):
            moves.append((r, c, nr, nc))
    return moves


def slide_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target == '.':
                moves.append((r, c, nr, nc))
            else:
                if is_enemy(board[r][c], target):
                    moves.append((r, c, nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def get_rook_moves(board, r, c, color):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    return slide_moves(board, r, c, color, dirs)


def get_bishop_moves(board, r, c, color):
    dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    return slide_moves(board, r, c, color, dirs)


def get_queen_moves(board, r, c, color):
    return get_rook_moves(board, r, c, color) + get_bishop_moves(board, r, c, color)


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
            if target == '.' or is_enemy(board[r][c], target):
                moves.append((r, c, nr, nc))
    return moves


PIECE_MOVE_FUNCS = {
    'p': get_pawn_moves,
    'r': get_rook_moves,
    'n': get_knight_moves,
    'b': get_bishop_moves,
    'q': get_queen_moves,
    'k': get_king_moves,
}

# -------------------------------------------------------------
# Generate semua langkah valid (tanpa cek skak)
# -------------------------------------------------------------

def generate_moves(board, turn_color):
    all_moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece == '.':
                continue
            if color_of(piece) != turn_color:
                continue
            lower = piece.lower()
            move_func = PIECE_MOVE_FUNCS.get(lower)
            if not move_func:
                continue
            for move in move_func(board, r, c, turn_color):
                _, _, tr, tc = move
                # tidak boleh menabrak teman sendiri
                if is_friend(piece, board[tr][tc]):
                    continue
                all_moves.append(move)
    return all_moves

# -------------------------------------------------------------
# Make move + promosi otomatis ke menteri
# -------------------------------------------------------------

def make_move(board, move):
    r, c, tr, tc = move
    piece = board[r][c]
    new_board = deepcopy(board)
    new_board[r][c] = '.'
    # Promosi pion
    if piece == 'P' and tr == 0:
        new_board[tr][tc] = 'Q'
    elif piece == 'p' and tr == BOARD_SIZE - 1:
        new_board[tr][tc] = 'q'
    else:
        new_board[tr][tc] = piece
    return new_board

# -------------------------------------------------------------
# Evaluasi material sederhana (positif = keuntungan putih)
# -------------------------------------------------------------
PIECE_VALUES = {
    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
}

def evaluate(board):
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece == '.':
                continue
            val = PIECE_VALUES[piece.lower()]
            score += val if piece.isupper() else -val
    return score

# -------------------------------------------------------------
# AI: Greedy (minimax kedalaman 1)
# - Pilih langkah hitam yang meminimalkan evaluasi
# -------------------------------------------------------------

def ai_choose_move(board):
    moves = generate_moves(board, 'black')
    if not moves:
        return None
    best_move = None
    best_score = float('inf')
    for mv in moves:
        nb = make_move(board, mv)
        sc = evaluate(nb)
        if sc < best_score:
            best_score = sc
            best_move = mv
    return best_move

# -------------------------------------------------------------
# Rendering
# -------------------------------------------------------------

def draw_board(surface, board, font, selected, legal_moves):
    surface.fill(BG_COLOR)

    # Petak
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE + MARGIN, TILE_SIZE, TILE_SIZE)
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            pygame.draw.rect(surface, color, rect)

    # Highlight selected
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * TILE_SIZE, sr * TILE_SIZE + MARGIN, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect, 4)

    # Highlight legal moves
    for mv in legal_moves:
        _, _, tr, tc = mv
        cx = tc * TILE_SIZE + TILE_SIZE // 2
        cy = tr * TILE_SIZE + MARGIN + TILE_SIZE // 2
        pygame.draw.circle(surface, MOVE_DOT_COLOR, (cx, cy), 8)

    # Pieces (huruf)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece == '.':
                continue
            text_color = WHITE_PIECE_COLOR if piece.isupper() else BLACK_PIECE_COLOR
            label = font.render(piece.upper(), True, text_color)
            rect = label.get_rect(center=(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + MARGIN + TILE_SIZE // 2))
            surface.blit(label, rect)

    # Header
    info_font = pygame.font.SysFont(None, 24)
    info_surf = info_font.render("Pygame Chess - Putih (Anda) vs Hitam (AI)", True, TEXT_COLOR)
    surface.blit(info_surf, (10, 2))


# -------------------------------------------------------------
# Deteksi akhir sederhana
# - Game selesai jika salah satu raja hilang atau tidak ada langkah untuk giliran
# -------------------------------------------------------------

def has_king(board, color):
    target = 'K' if color == 'white' else 'k'
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == target:
                return True
    return False


def any_moves(board, color):
    return len(generate_moves(board, color)) > 0


# -------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Chess (Letters)")
    clock = pygame.time.Clock()

    # Font besar untuk bidak
    font = pygame.font.SysFont(None, 56, bold=True)

    board = initial_board()
    turn = 'white'  # white = player, black = AI
    selected = None
    legal_moves_from_selected = []
    running = True
    game_over = False
    winner_text = None

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # restart
                    board = initial_board()
                    turn = 'white'
                    selected = None
                    legal_moves_from_selected = []
                    game_over = False
                    winner_text = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                mx, my = event.pos
                # hit test ke papan
                if MARGIN <= my <= MARGIN + TILE_SIZE * BOARD_SIZE:
                    r = (my - MARGIN) // TILE_SIZE
                    c = mx // TILE_SIZE
                    if in_bounds(r, c):
                        if turn == 'white':
                            if selected is None:
                                # pilih bidak putih
                                if board[r][c] != '.' and color_of(board[r][c]) == 'white':
                                    selected = (r, c)
                                    # filter moves dari petak ini
                                    all_moves = generate_moves(board, 'white')
                                    legal_moves_from_selected = [m for m in all_moves if m[0] == r and m[1] == c]
                                else:
                                    selected = None
                                    legal_moves_from_selected = []
                            else:
                                # coba lakukan langkah jika valid
                                moved = False
                                for mv in legal_moves_from_selected:
                                    if mv[2] == r and mv[3] == c:
                                        board = make_move(board, mv)
                                        moved = True
                                        break
                                selected = None
                                legal_moves_from_selected = []
                                if moved:
                                    # cek akhir setelah langkah putih
                                    if not has_king(board, 'black'):
                                        game_over = True
                                        winner_text = "Putih menang (raja hitam hilang)"
                                    elif not any_moves(board, 'black'):
                                        game_over = True
                                        winner_text = "Putih menang (hitam tidak punya langkah)"
                                    else:
                                        turn = 'black'
                        # jika bukan giliran putih, klik diabaikan

        # Giliran AI
        if not game_over and turn == 'black':
            mv = ai_choose_move(board)
            if mv is None:
                game_over = True
                winner_text = "Putih menang (hitam tidak punya langkah)"
            else:
                board = make_move(board, mv)
                # cek akhir setelah langkah hitam
                if not has_king(board, 'white'):
                    game_over = True
                    winner_text = "Hitam menang (raja putih hilang)"
                elif not any_moves(board, 'white'):
                    game_over = True
                    winner_text = "Hitam menang (putih tidak punya langkah)"
                else:
                    turn = 'white'

        # Render
        draw_board(screen, board, font, selected, legal_moves_from_selected if selected else [])

        # Teks status
        status_font = pygame.font.SysFont(None, 28)
        if game_over:
            msg = winner_text or "Game Over"
        else:
            msg = f"Giliran: {'Putih' if turn == 'white' else 'Hitam (AI)'} - Tekan R untuk restart"
        status_surf = status_font.render(msg, True, TEXT_COLOR)
        screen.blit(status_surf, (10, HEIGHT - MARGIN + 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
