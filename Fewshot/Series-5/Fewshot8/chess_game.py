import sys
import pygame
from typing import List, Tuple, Optional

# ============================
# Konfigurasi dan Konstanta
# ============================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
FPS = 60

# Warna
LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (80, 80, 80)
CAPTURE_RED = (200, 60, 60)
TEXT_WHITE = (250, 250, 250)
TEXT_BLACK = (10, 10, 10)

# Nilai material sederhana untuk evaluasi
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': 0,
}

# ============================
# Representasi papan
# ============================

def create_initial_board() -> List[List[str]]:
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


def is_white(piece: str) -> bool:
    return piece != '.' and piece.isupper()


def is_black(piece: str) -> bool:
    return piece != '.' and piece.islower()


def piece_color(piece: str) -> Optional[str]:
    if piece == '.':
        return None
    return 'white' if is_white(piece) else 'black'


Move = Tuple[Tuple[int, int], Tuple[int, int], Optional[str], Optional[str]]
# (from_pos, to_pos, captured_piece, promotion_piece)

# ============================
# Generator langkah per bidak
# ============================

def get_knight_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for r_off, c_off in offsets:
        r, c = row + r_off, col + c_off
        if not in_bounds(r, c):
            continue
        target = board[r][c]
        if target == '.' or (color == 'white' and is_black(target)) or (color == 'black' and is_white(target)):
            moves.append(((row, col), (r, c), target if target != '.' else None, None))
    return moves


def get_sliding_moves(board: List[List[str]], row: int, col: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
    moves: List[Move] = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            target = board[r][c]
            if target == '.':
                moves.append(((row, col), (r, c), None, None))
            else:
                # berhenti saat bertemu bidak
                if (color == 'white' and is_black(target)) or (color == 'black' and is_white(target)):
                    moves.append(((row, col), (r, c), target, None))
                break
            r += dr
            c += dc
    return moves


def get_bishop_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return get_sliding_moves(board, row, col, color, dirs)


def get_rook_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return get_sliding_moves(board, row, col, color, dirs)


def get_queen_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
    return get_sliding_moves(board, row, col, color, dirs)


def get_king_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if not in_bounds(r, c):
                continue
            target = board[r][c]
            if target == '.' or (color == 'white' and is_black(target)) or (color == 'black' and is_white(target)):
                moves.append(((row, col), (r, c), target if target != '.' else None, None))
    return moves


def get_pawn_moves(board: List[List[str]], row: int, col: int, color: str) -> List[Move]:
    moves: List[Move] = []
    dir_forward = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1
    promotion_row = 0 if color == 'white' else 7

    # maju 1
    r1, c1 = row + dir_forward, col
    if in_bounds(r1, c1) and board[r1][c1] == '.':
        promo = None
        if r1 == promotion_row:
            promo = 'Q' if color == 'white' else 'q'
        moves.append(((row, col), (r1, c1), None, promo))
        # maju 2 dari start
        r2 = row + 2 * dir_forward
        if row == start_row and in_bounds(r2, c1) and board[r2][c1] == '.':
            moves.append(((row, col), (r2, c1), None, None))

    # tangkap diagonal
    for dc in (-1, 1):
        r, c = row + dir_forward, col + dc
        if not in_bounds(r, c):
            continue
        target = board[r][c]
        if target != '.' and ((color == 'white' and is_black(target)) or (color == 'black' and is_white(target))):
            promo = None
            if r == promotion_row:
                promo = 'Q' if color == 'white' else 'q'
            moves.append(((row, col), (r, c), target, promo))

    # Catatan: Tidak ada en passant/castling untuk kesederhanaan
    return moves


def generate_piece_moves(board: List[List[str]], row: int, col: int) -> List[Move]:
    piece = board[row][col]
    if piece == '.':
        return []
    color = 'white' if is_white(piece) else 'black'
    p = piece.upper()
    if p == 'P':
        return get_pawn_moves(board, row, col, color)
    if p == 'N':
        return get_knight_moves(board, row, col, color)
    if p == 'B':
        return get_bishop_moves(board, row, col, color)
    if p == 'R':
        return get_rook_moves(board, row, col, color)
    if p == 'Q':
        return get_queen_moves(board, row, col, color)
    if p == 'K':
        return get_king_moves(board, row, col, color)
    return []


def generate_all_moves(board: List[List[str]], color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == '.':
                continue
            if color == 'white' and is_white(piece):
                moves.extend(generate_piece_moves(board, r, c))
            elif color == 'black' and is_black(piece):
                moves.extend(generate_piece_moves(board, r, c))
    return moves


# ============================
# Aksi papan dan evaluasi
# ============================

def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]


def make_move(board: List[List[str]], move: Move) -> List[List[str]]:
    new_board = clone_board(board)
    (r1, c1), (r2, c2), _capt, promo = move
    moving_piece = new_board[r1][c1]
    new_board[r1][c1] = '.'
    if promo is not None and moving_piece.upper() == 'P':
        # promosi mengganti bidak di petak tujuan
        new_board[r2][c2] = promo
    else:
        new_board[r2][c2] = moving_piece
    return new_board


def evaluate_board(board: List[List[str]]) -> int:
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p in PIECE_VALUES:
                score += PIECE_VALUES[p]
    return score  # skor dari sudut pandang putih


def ai_choose_move(board: List[List[str]], color: str) -> Optional[Move]:
    # Greedy depth 1: pilih langkah dengan evaluasi terbaik untuk warna tersebut
    moves = generate_all_moves(board, color)
    if not moves:
        return None

    best_move = None
    if color == 'white':
        best_score = -10**9
        for m in moves:
            b2 = make_move(board, m)
            score = evaluate_board(b2)
            if score > best_score:
                best_score = score
                best_move = m
    else:
        best_score = 10**9
        for m in moves:
            b2 = make_move(board, m)
            score = evaluate_board(b2)
            if score < best_score:
                best_score = score
                best_move = m
    return best_move


# ============================
# Pygame Rendering & Input
# ============================

def draw_board(screen: pygame.Surface):
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)


def draw_highlights(screen: pygame.Surface, selected: Optional[Tuple[int, int]], valid_moves: List[Move]):
    if selected is not None:
        r, c = selected
        rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect)
    # titik untuk petak tujuan
    for _from, to, captured, promo in valid_moves:
        r2, c2 = to
        center = (c2 * SQ_SIZE + SQ_SIZE // 2, r2 * SQ_SIZE + SQ_SIZE // 2)
        if captured:
            pygame.draw.circle(screen, CAPTURE_RED, center, SQ_SIZE // 6)
        else:
            pygame.draw.circle(screen, MOVE_DOT, center, SQ_SIZE // 10)


def draw_pieces(screen: pygame.Surface, board: List[List[str]], font: pygame.font.Font):
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == '.':
                continue
            text_color = TEXT_WHITE if is_white(p) else TEXT_BLACK
            surf = font.render(p.upper(), True, text_color)
            rect = surf.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
            screen.blit(surf, rect)


def pos_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    c = x // SQ_SIZE
    r = y // SQ_SIZE
    if in_bounds(r, c):
        return (r, c)
    return None


def is_own_piece(board: List[List[str]], r: int, c: int, color: str) -> bool:
    p = board[r][c]
    if p == '.':
        return False
    return (color == 'white' and is_white(p)) or (color == 'black' and is_black(p))


def filter_own_captures(moves: List[Move], color: str, board: List[List[str]]) -> List[Move]:
    # Langkah sudah dicegah menabrak kawan di generator, fungsi ini sebagai safeguard (opsional)
    filtered: List[Move] = []
    for m in moves:
        (_, _), (r2, c2), captured, _ = m
        target = board[r2][c2]
        if target != '.' and ((color == 'white' and is_white(target)) or (color == 'black' and is_black(target))):
            continue
        filtered.append(m)
    return filtered


def there_is_winner(board: List[List[str]]) -> Optional[str]:
    # Sederhana: jika salah satu raja hilang
    has_white_king = any('K' in row for row in board)
    has_black_king = any('k' in row for row in board)
    if has_white_king and has_black_king:
        return None
    elif has_white_king and not has_black_king:
        return 'white'
    elif has_black_king and not has_white_king:
        return 'black'
    return None


def main():
    pygame.init()
    pygame.display.set_caption('Simple Chess - Pygame (Text Pieces)')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font besar agar mudah dibaca
    # Gunakan font monospace yang umum tersedia
    font = pygame.font.SysFont('consolas', SQ_SIZE // 2 + 6, bold=True)

    board = create_initial_board()
    running = True

    human_color = 'white'
    ai_color = 'black'
    turn = 'white'

    selected: Optional[Tuple[int, int]] = None
    valid_moves: List[Move] = []

    game_over_text: Optional[str] = None

    while running:
        clock.tick(FPS)

        # Cek winner via raja hilang, atau tidak ada langkah untuk pemain yang jalan
        winner = there_is_winner(board)
        if winner is not None:
            game_over_text = f"Game Over: {winner.capitalize()} wins"
        else:
            # Jika tidak ada langkah yang tersedia untuk pemain saat ini, game over (stalemate dianggap kalah pemain yang jalan untuk kesederhanaan)
            current_moves = generate_all_moves(board, turn)
            if not current_moves:
                game_over_text = f"Game Over: {('Black' if turn == 'white' else 'White')} wins"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if game_over_text is not None:
                # Setelah game over, abaikan input
                continue

            if turn == human_color:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    grid = pos_from_mouse(pos)
                    if grid is None:
                        continue
                    r, c = grid
                    if selected is None:
                        # pilih bidak sendiri
                        if is_own_piece(board, r, c, human_color):
                            selected = (r, c)
                            valid_moves = generate_piece_moves(board, r, c)
                            valid_moves = filter_own_captures(valid_moves, human_color, board)
                        else:
                            selected = None
                            valid_moves = []
                    else:
                        # klik kedua: eksekusi jika cocok dengan tujuan
                        moved = False
                        for m in valid_moves:
                            (sr, sc), (tr, tc), _, _ = m
                            if (sr, sc) == selected and (tr, tc) == (r, c):
                                board = make_move(board, m)
                                turn = ai_color
                                moved = True
                                break
                        if not moved:
                            # pilih ulang jika klik bidak sendiri lain
                            if is_own_piece(board, r, c, human_color):
                                selected = (r, c)
                                valid_moves = generate_piece_moves(board, r, c)
                                valid_moves = filter_own_captures(valid_moves, human_color, board)
                            else:
                                selected = None
                                valid_moves = []

        # AI move
        if running and game_over_text is None and turn == ai_color:
            ai_move = ai_choose_move(board, ai_color)
            if ai_move is None:
                game_over_text = "Game Over: No moves for AI"
            else:
                board = make_move(board, ai_move)
                turn = human_color
            selected = None
            valid_moves = []

        # Render
        draw_board(screen)
        draw_highlights(screen, selected, valid_moves)
        draw_pieces(screen, board, font)

        if game_over_text is not None:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            end_font = pygame.font.SysFont('consolas', 36, bold=True)
            surf = end_font.render(game_over_text + "  (ESC untuk keluar)", True, (255, 255, 255))
            rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(surf, rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
