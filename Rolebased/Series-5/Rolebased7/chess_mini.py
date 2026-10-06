import sys
import pygame
from typing import List, Tuple, Optional

# ------------------------------
# Config & Constants
# ------------------------------

WIDTH, HEIGHT = 640, 640
BOARD_SIZE = 8
SQ_SIZE = WIDTH // BOARD_SIZE
FPS = 60

WHITE = (238, 238, 210)
GREEN = (118, 150, 86)
HIGHLIGHT = (246, 246, 105)
MOVE_HINT = (187, 203, 43)
TEXT_COLOR = (20, 20, 20)

PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0  # King tidak dinilai untuk evaluasi material sederhana
}

UNICODE_PIECES = {
    ('w', 'K'): '♔',
    ('w', 'Q'): '♕',
    ('w', 'R'): '♖',
    ('w', 'B'): '♗',
    ('w', 'N'): '♘',
    ('w', 'P'): '♙',
    ('b', 'K'): '♚',
    ('b', 'Q'): '♛',
    ('b', 'R'): '♜',
    ('b', 'B'): '♝',
    ('b', 'N'): '♞',
    ('b', 'P'): '♟',
}

# ------------------------------
# Core Data Structures
# ------------------------------

Piece = Tuple[str, str]  # (color, type) e.g. ('w','P'), ('b','Q')
Move = Tuple[Tuple[int, int], Tuple[int, int], Optional[Piece]]  # ((r1,c1),(r2,c2),captured_piece)


class Board:
    """
    Representasi papan catur 8x8.
    Menyimpan state bidak dan menyediakan utilitas untuk memanipulasi state.
    """
    def __init__(self):
        # Matriks 8x8: None atau Piece
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self._setup_initial()

    def _setup_initial(self):
        # Setup bidak putih (row 7 & 6) dan hitam (row 0 & 1)
        # Hitam
        self.grid[0] = [
            ('b', 'R'), ('b', 'N'), ('b', 'B'), ('b', 'Q'),
            ('b', 'K'), ('b', 'B'), ('b', 'N'), ('b', 'R')
        ]
        self.grid[1] = [('b', 'P') for _ in range(BOARD_SIZE)]
        # Kosong tengah
        for r in range(2, 6):
            self.grid[r] = [None for _ in range(BOARD_SIZE)]
        # Putih
        self.grid[6] = [('w', 'P') for _ in range(BOARD_SIZE)]
        self.grid[7] = [
            ('w', 'R'), ('w', 'N'), ('w', 'B'), ('w', 'Q'),
            ('w', 'K'), ('w', 'B'), ('w', 'N'), ('w', 'R')
        ]

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get(self, rc: Tuple[int, int]) -> Optional[Piece]:
        r, c = rc
        return self.grid[r][c]

    def set(self, rc: Tuple[int, int], piece: Optional[Piece]):
        r, c = rc
        self.grid[r][c] = piece

    def move_piece(self, move: Move):
        (r1, c1), (r2, c2), _ = move
        piece = self.get((r1, c1))
        captured = self.get((r2, c2))
        self.set((r2, c2), piece)
        self.set((r1, c1), None)
        return captured

    def clone(self) -> "Board":
        b = Board.__new__(Board)
        b.grid = [row.copy() for row in self.grid]
        return b

    def material_eval(self, color: str) -> int:
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p:
                    sign = 1 if p[0] == color else -1
                    score += sign * PIECE_VALUES[p[1]]
        return score


class Rules:
    """
    Generator gerakan bidak.
    Pseudolegal moves: tidak mengecek kondisi skak/cek.
    Termasuk: Pion (jalan, makan, start-double), Kuda, Gajah, Benteng, Ratu, Raja.
    Tidak termasuk: en passant, castling. Promosi otomatis ke Queen.
    """
    KNIGHT_DIRS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
    KING_DIRS = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),          (0, 1),
                 (1, -1),  (1, 0), (1, 1)]

    ROOK_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    BISHOP_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    QUEEN_DIRS = ROOK_DIRS + BISHOP_DIRS

    def __init__(self):
        pass

    def is_enemy(self, a: Optional[Piece], b: Optional[Piece]) -> bool:
        if not a or not b:
            return False
        return a[0] != b[0]

    def generate_moves_for_piece(self, board: Board, rc: Tuple[int, int]) -> List[Move]:
        r, c = rc
        piece = board.get((r, c))
        if not piece:
            return []
        color, ptype = piece
        moves: List[Move] = []

        if ptype == 'P':
            dir_forward = -1 if color == 'w' else 1
            start_rank = 6 if color == 'w' else 1
            # maju 1
            r1 = r + dir_forward
            if board.in_bounds(r1, c) and board.get((r1, c)) is None:
                moves.append(((r, c), (r1, c), None))
                # start double
                r2 = r + 2 * dir_forward
                if r == start_rank and board.in_bounds(r2, c) and board.get((r2, c)) is None:
                    moves.append(((r, c), (r2, c), None))
            # makan
            for dc in (-1, 1):
                cc = c + dc
                rr = r + dir_forward
                if board.in_bounds(rr, cc):
                    target = board.get((rr, cc))
                    if self.is_enemy(piece, target):
                        moves.append(((r, c), (rr, cc), target))
            # promosi akan ditangani saat eksekusi move (di Game/AI) secara otomatis
            return moves

        if ptype == 'N':
            for dr, dc in self.KNIGHT_DIRS:
                rr, cc = r + dr, c + dc
                if not board.in_bounds(rr, cc):
                    continue
                tgt = board.get((rr, cc))
                if tgt is None or self.is_enemy(piece, tgt):
                    moves.append(((r, c), (rr, cc), tgt))
            return moves

        if ptype == 'K':
            for dr, dc in self.KING_DIRS:
                rr, cc = r + dr, c + dc
                if not board.in_bounds(rr, cc):
                    continue
                tgt = board.get((rr, cc))
                if tgt is None or self.is_enemy(piece, tgt):
                    moves.append(((r, c), (rr, cc), tgt))
            # castling: diabaikan untuk kesederhanaan
            return moves

        # Sliding pieces
        dirs = []
        if ptype == 'R':
            dirs = self.ROOK_DIRS
        elif ptype == 'B':
            dirs = self.BISHOP_DIRS
        elif ptype == 'Q':
            dirs = self.QUEEN_DIRS

        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while board.in_bounds(rr, cc):
                tgt = board.get((rr, cc))
                if tgt is None:
                    moves.append(((r, c), (rr, cc), None))
                else:
                    if self.is_enemy(piece, tgt):
                        moves.append(((r, c), (rr, cc), tgt))
                    break
                rr += dr
                cc += dc

        return moves

    def all_moves(self, board: Board, color: str) -> List[Move]:
        res: List[Move] = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = board.get((r, c))
                if p and p[0] == color:
                    res.extend(self.generate_moves_for_piece(board, (r, c)))
        return res

    def apply_promotion_if_any(self, board: Board, move: Move):
        # Promosi otomatis ke Queen bila pion mencapai rank terakhir
        (r1, c1), (r2, c2), _ = move
        p = board.get((r2, c2))
        if not p:
            return
        color, ptype = p
        if ptype != 'P':
            return
        if (color == 'w' and r2 == 0) or (color == 'b' and r2 == BOARD_SIZE - 1):
            board.set((r2, c2), (color, 'Q'))


# ------------------------------
# Simple AI (Greedy Capture)
# ------------------------------

class GreedyAI:
    """
    AI sederhana:
    - Cari tangkapan "aman" terbaik (tujuan tidak bisa dibalas langsung).
    - Jika tidak ada, pilih tangkapan terbaik menurut delta material.
    - Jika tetap tidak ada, pilih langkah acak/pertahankan sederhana (first legal).
    """
    def __init__(self, rules: Rules):
        self.rules = rules

    def choose_move(self, board: Board, color: str) -> Optional[Move]:
        moves = self.rules.all_moves(board, color)
        if not moves:
            return None

        # 1) Cari capture yang aman dan terbaik
        safe_captures = []
        for mv in moves:
            (r1, c1), (r2, c2), captured = mv
            if captured is None:
                continue
            gain = PIECE_VALUES[captured[1]]
            if self._is_destination_safe_after_move(board, mv, color):
                safe_captures.append((gain, mv))
        if safe_captures:
            safe_captures.sort(key=lambda x: x[0], reverse=True)
            return safe_captures[0][1]

        # 2) Kalau tidak ada safe capture, pilih capture dengan delta terbaik (gain - value moved if recaptured)
        scored_caps = []
        for mv in moves:
            (r1, c1), (r2, c2), captured = mv
            if captured is None:
                continue
            gain = PIECE_VALUES[captured[1]]
            # naive: kurangi dengan kemungkinan kehilangan piece yang bergerak (nilai piece sendiri)
            moving_piece = board.get((r1, c1))
            move_cost = PIECE_VALUES[moving_piece[1]] if moving_piece else 0
            scored_caps.append((gain - move_cost / 2.0, mv))
        if scored_caps:
            scored_caps.sort(key=lambda x: x[0], reverse=True)
            return scored_caps[0][1]

        # 3) Tidak ada capture, pilih langkah pertama yang sah
        return moves[0]

    def _is_destination_safe_after_move(self, board: Board, move: Move, color: str) -> bool:
        # Cek apakah setelah menjalankan move, kotak tujuan diserang lawan
        enemy = 'b' if color == 'w' else 'w'
        (r1, c1), (r2, c2), _ = move
        sim = board.clone()
        sim.move_piece(move)

        # setelah pindah, promosi bisa mengubah piece yang berada di (r2,c2)
        Rules().apply_promotion_if_any(sim, move)

        enemy_moves = Rules().all_moves(sim, enemy)
        for em in enemy_moves:
            _, (er2, ec2), _ = em
            if (er2, ec2) == (r2, c2):
                return False
        return True


# ------------------------------
# Rendering
# ------------------------------

def get_font():
    # Cari font yang memiliki glyph chess unicode
    # Beberapa font umum: "Segoe UI Symbol", "DejaVu Sans", "Noto Sans Symbols"
    candidates = [
        "Segoe UI Symbol",
        "DejaVu Sans",
        "Noto Sans Symbols",
        "Arial Unicode MS",
        "Symbola",
        "FreeSerif",
        None  # fallback default
    ]
    for name in candidates:
        try:
            font = pygame.font.SysFont(name, int(SQ_SIZE * 0.8), bold=False)
            if font:
                return font
        except Exception:
            continue
    return pygame.font.SysFont(None, int(SQ_SIZE * 0.8))


def draw_board(surface: pygame.Surface):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = WHITE if (r + c) % 2 == 0 else GREEN
            pygame.draw.rect(surface, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_highlight(surface: pygame.Surface, selected: Optional[Tuple[int, int]], moves: List[Move]):
    if selected:
        r, c = selected
        s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s.fill((*HIGHLIGHT, 80))
        surface.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

    # Hint gerakan dari petak terpilih
    for (_, _), (r2, c2), captured in moves:
        center = (c2 * SQ_SIZE + SQ_SIZE // 2, r2 * SQ_SIZE + SQ_SIZE // 2)
        radius = max(6, SQ_SIZE // 8)
        color = MOVE_HINT if captured is None else (180, 50, 50)
        pygame.draw.circle(surface, color, center, radius)


def draw_pieces(surface: pygame.Surface, board: Board, font: pygame.font.Font):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board.get((r, c))
            if piece:
                glyph = UNICODE_PIECES.get(piece)
                if glyph:
                    text = font.render(glyph, True, TEXT_COLOR)
                    text_rect = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                    surface.blit(text, text_rect)


# ------------------------------
# Game Controller
# ------------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mini Chess Engine (Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = get_font()

        self.board = Board()
        self.rules = Rules()
        self.ai = GreedyAI(self.rules)

        self.turn = 'w'  # putih mulai
        self.selected: Optional[Tuple[int, int]] = None
        self.cached_moves_from_selected: List[Move] = []
        self.running = True

        # Opsi: AI main hitam
        self.ai_color = 'b'

    def run(self):
        while self.running:
            self._handle_events()

            # Jika giliran AI
            if self.turn == self.ai_color:
                pygame.time.delay(150)  # sedikit jeda biar terasa
                mv = self.ai.choose_move(self.board, self.ai_color)
                if mv:
                    self._execute_move(mv)
                else:
                    # Tidak ada gerak: game over sederhana
                    self.running = False

            self._render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)

    def _render(self):
        draw_board(self.screen)
        draw_highlight(self.screen, self.selected, self.cached_moves_from_selected)
        draw_pieces(self.screen, self.board, self.font)
        pygame.display.flip()

    def _square_from_mouse(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        x, y = pos
        c = x // SQ_SIZE
        r = y // SQ_SIZE
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return (r, c)
        return None

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.turn == self.ai_color:
                    # Disable input saat AI berpikir/jalan
                    return
                rc = self._square_from_mouse(event.pos)
                if rc:
                    self._on_click(rc)

    def _on_click(self, rc: Tuple[int, int]):
        p = self.board.get(rc)
        if self.selected is None:
            # pilih bidak milik pemain turn
            if p and p[0] == self.turn:
                self.selected = rc
                self.cached_moves_from_selected = self._filter_own_moves(rc)
        else:
            # jika klik square tujuan valid -> jalan
            mv = self._find_move_from_selected_to(rc)
            if mv:
                self._execute_move(mv)
                self.selected = None
                self.cached_moves_from_selected = []
            else:
                # jika klik bidak sendiri lain -> ganti pilihan
                if p and p[0] == self.turn:
                    self.selected = rc
                    self.cached_moves_from_selected = self._filter_own_moves(rc)
                else:
                    # batalkan pilihan
                    self.selected = None
                    self.cached_moves_from_selected = []

    def _filter_own_moves(self, rc: Tuple[int, int]) -> List[Move]:
        allm = self.rules.generate_moves_for_piece(self.board, rc)
        # Bisa tambahkan filter untuk menghindari gerakan yang membuat raja skak (di-skip demi kesederhanaan)
        return allm

    def _find_move_from_selected_to(self, dst: Tuple[int, int]) -> Optional[Move]:
        for mv in self.cached_moves_from_selected:
            (_, _), (r2, c2), _ = mv
            if (r2, c2) == dst:
                return mv
        return None

    def _execute_move(self, move: Move):
        # Jalankan move
        self.board.move_piece(move)
        # Promosi jika perlu
        self.rules.apply_promotion_if_any(self.board, move)
        # Ganti giliran
        self.turn = 'b' if self.turn == 'w' else 'w'


# ------------------------------
# Entrypoint
# ------------------------------

if __name__ == "__main__":
    try:
        Game().run()
    except SystemExit:
        pass
