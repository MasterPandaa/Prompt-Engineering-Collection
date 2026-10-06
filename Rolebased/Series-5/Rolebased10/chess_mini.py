import sys
import pygame
from typing import List, Tuple, Optional

# =========================
# Model: Papan dan Aturan
# =========================

# Representasi bidak:
# Kode dua huruf: 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK' untuk putih; awalan 'b' untuk hitam.
# Kosong = None
# Koordinat papan: (row, col) dengan row=0 di atas, col=0 di kiri.

PIECE_UNICODE = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',
}

PIECE_VALUE = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0,  # Untuk evaluasi material sederhana, raja tidak diberi nilai
}

WHITE, BLACK = 'w', 'b'

class Move:
    def __init__(self, src: Tuple[int, int], dst: Tuple[int, int], piece: str,
                 captured: Optional[str] = None, promotion: Optional[str] = None):
        self.src = src
        self.dst = dst
        self.piece = piece
        self.captured = captured
        self.promotion = promotion  # 'Q', 'R', 'B', 'N' jika promosi

    def __repr__(self):
        return f"Move({self.piece} {self.src}->{self.dst}, cap={self.captured}, promo={self.promotion})"


class Board:
    def __init__(self):
        # 8x8 dengan None atau 'wP' dst.
        self.grid: List[List[Optional[str]]] = [[None for _ in range(8)] for _ in range(8)]
        self.turn: str = WHITE
        self.setup_start_position()

    def setup_start_position(self):
        # Bidak hitam (baris atas)
        self.grid[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        self.grid[1] = ['bP'] * 8
        # Baris tengah
        for r in range(2, 6):
            self.grid[r] = [None] * 8
        # Bidak putih (baris bawah)
        self.grid[6] = ['wP'] * 8
        self.grid[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        self.turn = WHITE

    def copy(self) -> 'Board':
        b = Board.__new__(Board)
        b.grid = [[self.grid[r][c] for c in range(8)] for r in range(8)]
        b.turn = self.turn
        return b

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def piece_at(self, pos: Tuple[int, int]) -> Optional[str]:
        r, c = pos
        return self.grid[r][c]

    def set_piece(self, pos: Tuple[int, int], piece: Optional[str]):
        r, c = pos
        self.grid[r][c] = piece

    def apply_move(self, mv: Move) -> 'Board':
        newb = self.copy()
        sr, sc = mv.src
        dr, dc = mv.dst
        moving_piece = newb.piece_at((sr, sc))
        # Hapus dari sumber
        newb.set_piece((sr, sc), None)
        # Promosi otomatis ke Queen jika specified
        if mv.promotion:
            new_piece = newb.turn + mv.promotion
            newb.set_piece((dr, dc), new_piece)
        else:
            newb.set_piece((dr, dc), moving_piece)
        # Ganti giliran
        newb.turn = WHITE if self.turn == BLACK else BLACK
        return newb

    def all_pieces_of(self, color: str) -> List[Tuple[int, int]]:
        out = []
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p[0] == color:
                    out.append((r, c))
        return out

    def king_position(self, color: str) -> Optional[Tuple[int, int]]:
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p == color + 'K':
                    return (r, c)
        return None


class Rules:
    @staticmethod
    def generate_pseudo_legal_moves(board: Board, color: str) -> List[Move]:
        # Menghasilkan langkah tanpa menyaring kondisi "raja tidak boleh tersisa dalam cek".
        moves: List[Move] = []
        for (r, c) in board.all_pieces_of(color):
            piece = board.piece_at((r, c))
            if not piece:
                continue
            kind = piece[1]
            if kind == 'P':
                Rules._pawn_moves(board, (r, c), color, moves)
            elif kind == 'N':
                Rules._knight_moves(board, (r, c), color, moves)
            elif kind == 'B':
                Rules._slider_moves(board, (r, c), color, moves, directions=[(-1,-1), (-1,1), (1,-1), (1,1)])
            elif kind == 'R':
                Rules._slider_moves(board, (r, c), color, moves, directions=[(-1,0), (1,0), (0,-1), (0,1)])
            elif kind == 'Q':
                Rules._slider_moves(board, (r, c), color, moves, directions=[(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)])
            elif kind == 'K':
                Rules._king_moves(board, (r, c), color, moves)
        return moves

    @staticmethod
    def generate_legal_moves(board: Board, color: str) -> List[Move]:
        # Filter pseudo-legal moves: raja tidak boleh tersisa dalam cek
        legal = []
        for mv in Rules.generate_pseudo_legal_moves(board, color):
            nb = board.apply_move(mv)
            if not Rules.is_in_check(nb, color):
                legal.append(mv)
        return legal

    @staticmethod
    def is_in_check(board: Board, color: str) -> bool:
        king_pos = board.king_position(color)
        if king_pos is None:
            # Tidak ada raja (posisi invalid) -> anggap cek
            return True
        # Jika ada langkah pseudo-legal dari lawan yang menyerang tempat raja, maka cek
        opp = WHITE if color == BLACK else BLACK
        for mv in Rules.generate_pseudo_legal_moves(board, opp):
            if mv.dst == king_pos:
                return True
        return False

    @staticmethod
    def _pawn_moves(board: Board, pos: Tuple[int, int], color: str, out: List[Move]):
        r, c = pos
        dir = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        # Maju 1
        nr = r + dir
        if board.in_bounds(nr, c) and board.piece_at((nr, c)) is None:
            # Promosi?
            promo_row = 0 if color == WHITE else 7
            promotion = 'Q' if nr == promo_row else None
            out.append(Move((r, c), (nr, c), color+'P', None, promotion))
            # Maju 2 dari start
            if r == start_row:
                nr2 = r + 2*dir
                if board.in_bounds(nr2, c) and board.piece_at((nr2, c)) is None:
                    out.append(Move((r, c), (nr2, c), color+'P'))
        # Makan diagonal
        for dc in (-1, 1):
            nc = c + dc
            nr = r + dir
            if board.in_bounds(nr, nc):
                target = board.piece_at((nr, nc))
                if target and target[0] != color:
                    promo_row = 0 if color == WHITE else 7
                    promotion = 'Q' if nr == promo_row else None
                    out.append(Move((r, c), (nr, nc), color+'P', captured=target, promotion=promotion))

    @staticmethod
    def _knight_moves(board: Board, pos: Tuple[int, int], color: str, out: List[Move]):
        r, c = pos
        jumps = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if not board.in_bounds(nr, nc):
                continue
            target = board.piece_at((nr, nc))
            if target is None or target[0] != color:
                out.append(Move((r, c), (nr, nc), color+'N', captured=target))

    @staticmethod
    def _slider_moves(board: Board, pos: Tuple[int, int], color: str, out: List[Move], directions: List[Tuple[int,int]]):
        r, c = pos
        piece = board.piece_at(pos)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.in_bounds(nr, nc):
                target = board.piece_at((nr, nc))
                if target is None:
                    out.append(Move((r, c), (nr, nc), piece))
                else:
                    if target[0] != color:
                        out.append(Move((r, c), (nr, nc), piece, captured=target))
                    break
                nr += dr
                nc += dc

    @staticmethod
    def _king_moves(board: Board, pos: Tuple[int, int], color: str, out: List[Move]):
        r, c = pos
        piece = board.piece_at(pos)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not board.in_bounds(nr, nc):
                    continue
                target = board.piece_at((nr, nc))
                if target is None or target[0] != color:
                    out.append(Move((r, c), (nr, nc), piece, captured=target))


# =========================
# AI Sederhana
# =========================

def evaluate_material(board: Board) -> int:
    # Nilai positif menguntungkan Putih, negatif menguntungkan Hitam
    score = 0
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p:
                val = PIECE_VALUE[p[1]]
                score += val if p[0] == WHITE else -val
    return score


def is_square_attacked(board: Board, square: Tuple[int,int], by_color: str) -> bool:
    # Gunakan pseudo-legal moves pihak by_color, apakah ada yang mendarat di square
    for mv in Rules.generate_pseudo_legal_moves(board, by_color):
        if mv.dst == square:
            # Perlu pastikan legalitas? Tidak perlu akurat penuh untuk heuristik.
            return True
    return False


def ai_choose_move(board: Board, color: str) -> Optional[Move]:
    # AI sederhana:
    # 1) Cari capture menguntungkan (makan gratis): captured_value - penalty jika langsung tertangkap
    # 2) Jika tidak ada, pilih langkah yang memaksimalkan evaluasi material setelah langkah
    legal = Rules.generate_legal_moves(board, color)
    if not legal:
        return None

    opp = WHITE if color == BLACK else BLACK

    def move_score(mv: Move) -> float:
        # Nilai dasar = evaluasi material setelah langkah dari perspektif color
        nb = board.apply_move(mv)
        base_eval = evaluate_material(nb)
        score_for_color = base_eval if color == WHITE else -base_eval

        # Bonus capture
        cap_bonus = 0.0
        if mv.captured:
            cap_bonus += PIECE_VALUE[mv.captured[1]] * 2.0  # prioritaskan makan

        # Penalti jika bidak pindah ke petak yang diserang lawan (berisiko dimakan balik)
        moved_to = mv.dst
        # Setelah langkah, cek apakah square diserang lawan
        if is_square_attacked(nb, moved_to, opp):
            # penalti kira-kira nilai bidak yang dipindahkan
            moved_kind = mv.piece[1]
            cap_bonus -= PIECE_VALUE[moved_kind] * 1.5

        return score_for_color + cap_bonus

    # Pilih skor terbaik
    best = max(legal, key=move_score)
    # Namun, coba prioritaskan capture "gratis" terlebih dahulu bila ada beberapa
    capture_moves = [m for m in legal if m.captured]
    if capture_moves:
        # pilih capture dengan skor terbaik
        best_cap = max(capture_moves, key=move_score)
        return best_cap
    return best


# =========================
# Rendering dan UI (Pygame)
# =========================

TILE_SIZE = 80
MARGIN = 40
BOARD_SIZE = TILE_SIZE * 8
WINDOW_W = BOARD_SIZE + 2 * MARGIN
WINDOW_H = BOARD_SIZE + 2 * MARGIN + 60  # ruang status bawah

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
MOVE_HINT_COLOR = (120, 170, 60)
STATUS_BG = (30, 30, 30)
STATUS_FG = (230, 230, 230)


def to_screen(rc: Tuple[int,int]) -> Tuple[int,int]:
    r, c = rc
    x = MARGIN + c * TILE_SIZE
    y = MARGIN + r * TILE_SIZE
    return x, y


def from_screen(xy: Tuple[int,int]) -> Optional[Tuple[int,int]]:
    x, y = xy
    if x < MARGIN or y < MARGIN or x >= MARGIN + BOARD_SIZE or y >= MARGIN + BOARD_SIZE:
        return None
    col = (x - MARGIN) // TILE_SIZE
    row = (y - MARGIN) // TILE_SIZE
    return (row, col)


def draw_board(screen, board: Board, font, selected: Optional[Tuple[int,int]], legal_moves_for_selected: List[Move], status_text: str):
    # Latar papan
    for r in range(8):
        for c in range(8):
            color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(MARGIN + c*TILE_SIZE, MARGIN + r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Sorot petak terpilih
    if selected:
        x, y = to_screen(selected)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), border_radius=6)

    # Hint langkah dari petak terpilih
    if legal_moves_for_selected:
        for mv in legal_moves_for_selected:
            x, y = to_screen(mv.dst)
            center = (x + TILE_SIZE//2, y + TILE_SIZE//2)
            pygame.draw.circle(screen, MOVE_HINT_COLOR, center, 10)

    # Gambar bidak
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if not p:
                continue
            ux, uy = to_screen((r, c))
            piece_char = PIECE_UNICODE[p]
            # Outline sederhana untuk kontras
            shadow = font.render(piece_char, True, (0, 0, 0))
            screen.blit(shadow, (ux + 1, uy + 1))
            surf = font.render(piece_char, True, (245, 245, 245))
            screen.blit(surf, (ux, uy))

    # Panel status
    pygame.draw.rect(screen, STATUS_BG, pygame.Rect(0, BOARD_SIZE + 2*MARGIN, WINDOW_W, WINDOW_H - (BOARD_SIZE + 2*MARGIN)))
    status_font = pygame.font.SysFont(None, 26, bold=True)
    txt = status_font.render(status_text, True, STATUS_FG)
    screen.blit(txt, (MARGIN, BOARD_SIZE + 2*MARGIN + 15))


def format_game_status(board: Board) -> str:
    to_move = "Putih" if board.turn == WHITE else "Hitam"
    legal = Rules.generate_legal_moves(board, board.turn)
    if not legal:
        if Rules.is_in_check(board, board.turn):
            return f"Skakmat! {'Putih' if board.turn == WHITE else 'Hitam'} terskakmat."
        else:
            return "Stalemate! Tidak ada langkah legal."
    return f"Gilir: {to_move}"


def main():
    pygame.init()
    pygame.display.set_caption("Mini Chess Engine - Pygame Unicode")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    # Font sistem, ukuran menyesuaikan TILE_SIZE
    piece_font_size = int(TILE_SIZE * 0.8)
    font = pygame.font.SysFont(None, piece_font_size)

    board = Board()

    selected: Optional[Tuple[int,int]] = None
    legal_cache_for_selected: List[Move] = []

    running = True
    game_over = False
    human_color = WHITE
    ai_color = BLACK

    while running:
        clock.tick(60)
        status_text = format_game_status(board)
        if "Skakmat" in status_text or "Stalemate" in status_text:
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                # Input hanya saat giliran manusia
                if board.turn == human_color:
                    pos = from_screen(event.pos)
                    if pos is not None:
                        piece = board.piece_at(pos)
                        if selected is None:
                            # pilih jika ada bidak sendiri
                            if piece and piece[0] == human_color:
                                selected = pos
                                legal_cache_for_selected = [m for m in Rules.generate_legal_moves(board, human_color) if m.src == selected]
                        else:
                            # Coba gerakkan ke pos
                            moves = [m for m in legal_cache_for_selected if m.dst == pos]
                            if moves:
                                board = board.apply_move(moves[0])
                                selected = None
                                legal_cache_for_selected = []
                            else:
                                # ganti seleksi bila klik bidak sendiri
                                if piece and piece[0] == human_color:
                                    selected = pos
                                    legal_cache_for_selected = [m for m in Rules.generate_legal_moves(board, human_color) if m.src == selected]
                                else:
                                    # batal seleksi
                                    selected = None
                                    legal_cache_for_selected = []
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    board = Board()
                    selected = None
                    legal_cache_for_selected = []
                    game_over = False

        # Giliran AI
        if not game_over and board.turn == ai_color:
            pygame.time.delay(200)  # sedikit jeda biar terlihat
            mv = ai_choose_move(board, ai_color)
            if mv is not None:
                board = board.apply_move(mv)
            else:
                # Tidak ada langkah (checkmate/stalemate) akan terdeteksi di status
                pass

        screen.fill((15, 15, 20))
        draw_board(screen, board, font, selected, legal_cache_for_selected, status_text)
        # Instruksi
        ui_font = pygame.font.SysFont(None, 22)
        tips = [
            "Klik bidak untuk memilih, lalu klik petak tujuan.",
            "Putih = Anda, Hitam = AI.",
            "Promosi otomatis menjadi Ratu.",
            "Tekan 'R' untuk restart.",
        ]
        for i, line in enumerate(tips):
            label = ui_font.render(line, True, (210, 210, 210))
            screen.blit(label, (MARGIN, BOARD_SIZE + 2*MARGIN + 40 + i*20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
