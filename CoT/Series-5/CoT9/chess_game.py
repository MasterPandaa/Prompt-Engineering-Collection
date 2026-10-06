import sys
import random
import pygame
from typing import List, Tuple, Optional

# -----------------------------
# Konfigurasi Visual & Game
# -----------------------------
TILE_SIZE = 80
BOARD_SIZE = 8
PADDING = 20
PANEL_WIDTH = 240  # panel kanan untuk info
WIDTH = TILE_SIZE * BOARD_SIZE + PANEL_WIDTH
HEIGHT = TILE_SIZE * BOARD_SIZE
FPS = 60

LIGHT_COLOR = (238, 238, 210)
DARK_COLOR = (118, 150, 86)
HIGHLIGHT_COLOR = (246, 246, 105)
SELECT_COLOR = (186, 202, 68)
MOVE_DOT_COLOR = (50, 50, 50)
TEXT_COLOR = (25, 25, 25)
BG_PANEL = (240, 240, 245)

# Nilai material sederhana untuk AI
PIECE_VALUES = {"K": 10000, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}

# Simbol Unicode untuk bidak
UNICODE_PIECES = {
    "wK": "\u2654", "wQ": "\u2655", "wR": "\u2656", "wB": "\u2657", "wN": "\u2658", "wP": "\u2659",
    "bK": "\u265A", "bQ": "\u265B", "bR": "\u265C", "bB": "\u265D", "bN": "\u265E", "bP": "\u265F",
}

# -----------------------------
# Representasi Board
# -----------------------------
# Board adalah list 2D 8x8. Setiap sel berisi None atau string dua karakter: 'wP', 'bK', dll.
Board = List[List[Optional[str]]]
Move = Tuple[Tuple[int, int], Tuple[int, int], Optional[str], Optional[str]]
# Move = ((r1,c1), (r2,c2), piece, captured)


def initial_board() -> Board:
    b: Board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # Hitam di atas (baris 0-1), Putih di bawah (baris 6-7)
    back_rank = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for c in range(BOARD_SIZE):
        b[1][c] = "bP"
        b[6][c] = "wP"
    for c, p in enumerate(back_rank):
        b[0][c] = "b" + p
        b[7][c] = "w" + p
    return b


# -----------------------------
# Utilitas Board
# -----------------------------

def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def get_color(piece: Optional[str]) -> Optional[str]:
    if not piece:
        return None
    return piece[0]  # 'w' atau 'b'


def get_type(piece: Optional[str]) -> Optional[str]:
    if not piece:
        return None
    return piece[1]  # 'K', 'Q', 'R', 'B', 'N', 'P'


# -----------------------------
# Generator Langkah Pseudo-Legal
# -----------------------------

def generate_moves(board: Board, side: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece and get_color(piece) == side:
                p_type = get_type(piece)
                if p_type == "P":
                    moves.extend(gen_pawn(board, r, c, side))
                elif p_type == "N":
                    moves.extend(gen_knight(board, r, c, side))
                elif p_type == "B":
                    moves.extend(gen_slider(board, r, c, side, [(-1, -1), (-1, 1), (1, -1), (1, 1)]))
                elif p_type == "R":
                    moves.extend(gen_slider(board, r, c, side, [(-1, 0), (1, 0), (0, -1), (0, 1)]))
                elif p_type == "Q":
                    moves.extend(gen_slider(board, r, c, side, [
                        (-1, -1), (-1, 1), (1, -1), (1, 1),
                        (-1, 0), (1, 0), (0, -1), (0, 1)
                    ]))
                elif p_type == "K":
                    moves.extend(gen_king(board, r, c, side))
    return moves


def gen_pawn(board: Board, r: int, c: int, side: str) -> List[Move]:
    res: List[Move] = []
    dir = -1 if side == "w" else 1
    start_row = 6 if side == "w" else 1
    promo_row = 0 if side == "w" else 7

    # maju 1
    r1, c1 = r + dir, c
    if in_bounds(r1, c1) and board[r1][c1] is None:
        res.append(((r, c), (r1, c1), board[r][c], None))
        # maju 2 dari posisi awal
        if r == start_row:
            r2 = r + 2 * dir
            if in_bounds(r2, c1) and board[r2][c1] is None:
                res.append(((r, c), (r2, c1), board[r][c], None))

    # tangkap diagonal
    for dc in (-1, 1):
        rr, cc = r + dir, c + dc
        if in_bounds(rr, cc) and board[rr][cc] is not None and get_color(board[rr][cc]) != side:
            res.append(((r, c), (rr, cc), board[r][c], board[rr][cc]))

    # promosi (kita terapkan saat melakukan langkah)
    return res


def gen_knight(board: Board, r: int, c: int, side: str) -> List[Move]:
    res: List[Move] = []
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        rr, cc = r + dr, c + dc
        if not in_bounds(rr, cc):
            continue
        target = board[rr][cc]
        if target is None or get_color(target) != side:
            res.append(((r, c), (rr, cc), board[r][c], target))
    return res


def gen_slider(board: Board, r: int, c: int, side: str, deltas: List[Tuple[int, int]]) -> List[Move]:
    res: List[Move] = []
    for dr, dc in deltas:
        rr, cc = r + dr, c + dc
        while in_bounds(rr, cc):
            target = board[rr][cc]
            if target is None:
                res.append(((r, c), (rr, cc), board[r][c], None))
            else:
                if get_color(target) != side:
                    res.append(((r, c), (rr, cc), board[r][c], target))
                break
            rr += dr
            cc += dc
    return res


def gen_king(board: Board, r: int, c: int, side: str) -> List[Move]:
    res: List[Move] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not in_bounds(rr, cc):
                continue
            target = board[rr][cc]
            if target is None or get_color(target) != side:
                res.append(((r, c), (rr, cc), board[r][c], target))
    return res


# -----------------------------
# Eksekusi Langkah & Promosi
# -----------------------------

def make_move(board: Board, move: Move) -> Board:
    (r1, c1), (r2, c2), piece, captured = move
    new_b = [row[:] for row in board]
    new_b[r1][c1] = None
    # Promosi pion otomatis ke Queen jika mencapai baris akhir
    if get_type(piece) == "P" and (r2 == 0 or r2 == BOARD_SIZE - 1):
        new_b[r2][c2] = get_color(piece) + "Q"
    else:
        new_b[r2][c2] = piece
    return new_b


# -----------------------------
# AI Sederhana
# -----------------------------

def ai_choose_move(board: Board, side: str) -> Optional[Move]:
    moves = generate_moves(board, side)
    if not moves:
        return None
    # pilih capture terbaik berdasarkan nilai material target
    best_capture = None
    best_score = -10**9
    for mv in moves:
        captured = mv[3]
        if captured:
            val = PIECE_VALUES[get_type(captured)]
            if val > best_score:
                best_score = val
                best_capture = mv
    if best_capture:
        return best_capture
    # tidak ada capture, pilih acak
    return random.choice(moves)


# -----------------------------
# Rendering
# -----------------------------

def draw_board(screen, fonts, board: Board, selected: Optional[Tuple[int, int]], legal_moves_from_sel: List[Tuple[int, int]]):
    # papan
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            is_light = (r + c) % 2 == 0
            color = LIGHT_COLOR if is_light else DARK_COLOR
            pygame.draw.rect(screen, color, rect)

            # highlight seleksi
            if selected == (r, c):
                pygame.draw.rect(screen, SELECT_COLOR, rect)

            # highlight tujuan legal dari seleksi
            if (r, c) in legal_moves_from_sel:
                # titik kecil
                center = (rect.x + TILE_SIZE // 2, rect.y + TILE_SIZE // 2)
                pygame.draw.circle(screen, MOVE_DOT_COLOR, center, 8)

            # gambar piece
            piece = board[r][c]
            if piece:
                draw_piece(screen, fonts, piece, rect)

    # panel kanan
    pygame.draw.rect(screen, BG_PANEL, pygame.Rect(BOARD_SIZE * TILE_SIZE, 0, PANEL_WIDTH, HEIGHT))


def draw_piece(screen, fonts, piece: str, rect: pygame.Rect):
    color = get_color(piece)
    code = UNICODE_PIECES[piece]
    # coba beberapa font; Windows biasanya punya Segoe UI Symbol
    for fname in ["Segoe UI Symbol", "DejaVu Sans", None]:
        try:
            font = fonts.get(fname)
            if font is None:
                font = pygame.font.SysFont(fname, int(TILE_SIZE * 0.8))
                fonts[fname] = font
            surf = font.render(code, True, (0, 0, 0)) if color == 'b' else font.render(code, True, (255, 255, 255))
            # Outline tipis agar putih kontras: render dua kali (bayangan)
            shadow = font.render(code, True, (0, 0, 0))
            shadow_pos = (rect.x + (TILE_SIZE - surf.get_width()) // 2 + 1,
                          rect.y + (TILE_SIZE - surf.get_height()) // 2 + 1)
            screen.blit(shadow, shadow_pos)
            pos = (rect.x + (TILE_SIZE - surf.get_width()) // 2,
                   rect.y + (TILE_SIZE - surf.get_height()) // 2)
            screen.blit(surf, pos)
            return
        except Exception:
            continue
    # fallback huruf jika font gagal
    basic_font = pygame.font.SysFont(None, int(TILE_SIZE * 0.6))
    label = basic_font.render(piece, True, (0, 0, 0))
    screen.blit(label, (rect.x + 10, rect.y + 10))


# -----------------------------
# Input Handling
# -----------------------------

def square_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    if x >= BOARD_SIZE * TILE_SIZE or y >= BOARD_SIZE * TILE_SIZE:
        return None
    return (y // TILE_SIZE, x // TILE_SIZE)


# -----------------------------
# Game Loop
# -----------------------------

def main():
    pygame.init()
    pygame.display.set_caption("Catur Pygame - Manusia vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    fonts_cache = {}

    board = initial_board()
    turn = 'w'  # putih = pemain manusia
    selected: Optional[Tuple[int, int]] = None
    legal_targets_from_sel: List[Tuple[int, int]] = []

    running = True
    game_over_text: Optional[str] = None

    info_font = pygame.font.SysFont("Arial", 22)
    title_font = pygame.font.SysFont("Arial", 26, bold=True)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over_text is None:
                if turn == 'w':
                    sq = square_from_mouse(event.pos)
                    if sq:
                        r, c = sq
                        piece = board[r][c]
                        # klik pertama: pilih bidak milik sendiri
                        if selected is None:
                            if piece and get_color(piece) == 'w':
                                selected = (r, c)
                                # hitung semua langkah dari kotak ini
                                legal_targets_from_sel = [dst for (src, dst, p, cap) in generate_moves(board, 'w') if src == selected]
                            else:
                                selected = None
                                legal_targets_from_sel = []
                        else:
                            # klik kedua: jika tujuan ada di legal list, lakukan langkah
                            if (r, c) in legal_targets_from_sel:
                                # temukan move object yang cocok
                                move_obj = None
                                for mv in generate_moves(board, 'w'):
                                    if mv[0] == selected and mv[1] == (r, c):
                                        move_obj = mv
                                        break
                                if move_obj:
                                    board = make_move(board, move_obj)
                                    turn = 'b'
                                    selected = None
                                    legal_targets_from_sel = []
                            else:
                                # ganti seleksi jika klik bidak sendiri, atau batal jika tidak
                                if piece and get_color(piece) == 'w':
                                    selected = (r, c)
                                    legal_targets_from_sel = [dst for (src, dst, p, cap) in generate_moves(board, 'w') if src == selected]
                                else:
                                    selected = None
                                    legal_targets_from_sel = []

        # Jika giliran AI dan game belum selesai
        if game_over_text is None and turn == 'b':
            ai_move = ai_choose_move(board, 'b')
            if ai_move is None:
                game_over_text = "Permainan selesai: Tidak ada langkah untuk Hitam."
            else:
                board = make_move(board, ai_move)
                turn = 'w'

        # Cek jika salah satu sisi tidak punya langkah (sederhana)
        if game_over_text is None:
            if turn == 'w' and not generate_moves(board, 'w'):
                game_over_text = "Permainan selesai: Tidak ada langkah untuk Putih."
            elif turn == 'b' and not generate_moves(board, 'b'):
                game_over_text = "Permainan selesai: Tidak ada langkah untuk Hitam."

        # Render
        screen.fill((0, 0, 0))
        draw_board(screen, fonts_cache, board, selected, legal_targets_from_sel)

        # Panel teks
        panel_x = BOARD_SIZE * TILE_SIZE
        title = title_font.render("Catur Pygame", True, TEXT_COLOR)
        screen.blit(title, (panel_x + 20, 20))
        turn_text = "Giliran: Putih" if turn == 'w' else "Giliran: Hitam"
        t_surf = info_font.render(turn_text, True, TEXT_COLOR)
        screen.blit(t_surf, (panel_x + 20, 60))

        controls = [
            "Kontrol:",
            "- Klik bidak Anda untuk memilih",
            "- Klik petak tujuan untuk bergerak",
            "- ESC untuk keluar",
        ]
        y = 110
        for line in controls:
            surf = info_font.render(line, True, TEXT_COLOR)
            screen.blit(surf, (panel_x + 20, y))
            y += 28

        if game_over_text:
            go_surf = info_font.render(game_over_text, True, (180, 30, 30))
            screen.blit(go_surf, (panel_x + 20, HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
