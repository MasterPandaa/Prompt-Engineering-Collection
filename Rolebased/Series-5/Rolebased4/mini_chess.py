import sys
import random
import pygame
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

# =========================
# Konfigurasi Tampilan
# =========================
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS

COLOR_LIGHT = (240, 217, 181)   # terang
COLOR_DARK = (181, 136, 99)     # gelap
COLOR_HIGHLIGHT = (246, 246, 105)  # highlight kotak terpilih
COLOR_MOVE_HINT = (100, 180, 255)  # hint gerak

# =========================
# Representasi Bidak
# =========================
class Color(Enum):
    WHITE = 1
    BLACK = 2

class PieceType(Enum):
    KING   = "K"
    QUEEN  = "Q"
    ROOK   = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN   = "P"

UNICODE_PIECES = {
    (Color.WHITE, PieceType.KING):   "♔",
    (Color.WHITE, PieceType.QUEEN):  "♕",
    (Color.WHITE, PieceType.ROOK):   "♖",
    (Color.WHITE, PieceType.BISHOP): "♗",
    (Color.WHITE, PieceType.KNIGHT): "♘",
    (Color.WHITE, PieceType.PAWN):   "♙",
    (Color.BLACK, PieceType.KING):   "♚",
    (Color.BLACK, PieceType.QUEEN):  "♛",
    (Color.BLACK, PieceType.ROOK):   "♜",
    (Color.BLACK, PieceType.BISHOP): "♝",
    (Color.BLACK, PieceType.KNIGHT): "♞",
    (Color.BLACK, PieceType.PAWN):   "♟",
}

# Nilai evaluasi material sederhana
PIECE_VALUES = {
    PieceType.PAWN: 1,
    PieceType.KNIGHT: 3,
    PieceType.BISHOP: 3,
    PieceType.ROOK: 5,
    PieceType.QUEEN: 9,
    PieceType.KING: 0,  # biasanya 1000+, tapi untuk engine mini kita 0 agar fokus capture gratis
}

@dataclass
class Piece:
    color: Color
    kind: PieceType

@dataclass
class Move:
    src: Tuple[int, int]
    dst: Tuple[int, int]
    promotion: Optional[PieceType] = None

# =========================
# Board: representasi papan + state
# =========================
class Board:
    def __init__(self):
        # Matriks 8x8: (row, col) dengan 0 di atas (rank 8) dan 7 di bawah (rank 1)
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.turn: Color = Color.WHITE
        self._setup_initial()

    def _setup_initial(self):
        # Hitam (atas)
        self.grid[0] = [
            Piece(Color.BLACK, PieceType.ROOK),
            Piece(Color.BLACK, PieceType.KNIGHT),
            Piece(Color.BLACK, PieceType.BISHOP),
            Piece(Color.BLACK, PieceType.QUEEN),
            Piece(Color.BLACK, PieceType.KING),
            Piece(Color.BLACK, PieceType.BISHOP),
            Piece(Color.BLACK, PieceType.KNIGHT),
            Piece(Color.BLACK, PieceType.ROOK),
        ]
        self.grid[1] = [Piece(Color.BLACK, PieceType.PAWN) for _ in range(8)]
        # Kosong
        for r in range(2, 6):
            self.grid[r] = [None for _ in range(8)]
        # Putih (bawah)
        self.grid[6] = [Piece(Color.WHITE, PieceType.PAWN) for _ in range(8)]
        self.grid[7] = [
            Piece(Color.WHITE, PieceType.ROOK),
            Piece(Color.WHITE, PieceType.KNIGHT),
            Piece(Color.WHITE, PieceType.BISHOP),
            Piece(Color.WHITE, PieceType.QUEEN),
            Piece(Color.WHITE, PieceType.KING),
            Piece(Color.WHITE, PieceType.BISHOP),
            Piece(Color.WHITE, PieceType.KNIGHT),
            Piece(Color.WHITE, PieceType.ROOK),
        ]

    def inside(self, r: int, c: int) -> bool:
        return 0 <= r < ROWS and 0 <= c < COLS

    def piece_at(self, r: int, c: int) -> Optional[Piece]:
        if not self.inside(r, c):
            return None
        return self.grid[r][c]

    def move_piece(self, mv: Move):
        sr, sc = mv.src
        dr, dc = mv.dst
        piece = self.grid[sr][sc]
        self.grid[dr][dc] = piece
        self.grid[sr][sc] = None
        # Promotion sederhana otomatis jadi Queen
        if piece and piece.kind == PieceType.PAWN:
            if (piece.color == Color.WHITE and dr == 0) or (piece.color == Color.BLACK and dr == 7):
                self.grid[dr][dc] = Piece(piece.color, PieceType.QUEEN)
        # Ganti giliran
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE

    def copy(self) -> "Board":
        b = Board.__new__(Board)  # bypass __init__
        b.grid = [[(Piece(p.color, p.kind) if p else None) for p in row] for row in self.grid]
        b.turn = self.turn
        return b

# =========================
# Rules: generate langkah pseudo-legal (tanpa cek skak untuk kesederhanaan)
# =========================
class Rules:
    @staticmethod
    def generate_moves(board: Board, color: Color) -> List[Move]:
        moves: List[Move] = []
        for r in range(ROWS):
            for c in range(COLS):
                p = board.piece_at(r, c)
                if not p or p.color != color:
                    continue
                if p.kind == PieceType.PAWN:
                    moves.extend(Rules._pawn_moves(board, r, c, p))
                elif p.kind == PieceType.KNIGHT:
                    moves.extend(Rules._knight_moves(board, r, c, p))
                elif p.kind == PieceType.BISHOP:
                    moves.extend(Rules._slide_moves(board, r, c, p, directions=[(-1,-1),(-1,1),(1,-1),(1,1)]))
                elif p.kind == PieceType.ROOK:
                    moves.extend(Rules._slide_moves(board, r, c, p, directions=[(-1,0),(1,0),(0,-1),(0,1)]))
                elif p.kind == PieceType.QUEEN:
                    moves.extend(Rules._slide_moves(board, r, c, p, directions=[(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]))
                elif p.kind == PieceType.KING:
                    moves.extend(Rules._king_moves(board, r, c, p))
        return moves

    @staticmethod
    def _pawn_moves(board: Board, r: int, c: int, p: Piece) -> List[Move]:
        moves: List[Move] = []
        dir_ = -1 if p.color == Color.WHITE else 1
        start_row = 6 if p.color == Color.WHITE else 1
        # maju 1
        nr = r + dir_
        if board.inside(nr, c) and board.piece_at(nr, c) is None:
            moves.append(Move((r, c), (nr, c)))
            # maju 2 dari posisi awal
            nr2 = r + 2*dir_
            if r == start_row and board.inside(nr2, c) and board.piece_at(nr2, c) is None:
                moves.append(Move((r, c), (nr2, c)))
        # makan diagonal
        for dc in (-1, 1):
            nc = c + dc
            if board.inside(nr, nc):
                target = board.piece_at(nr, nc)
                if target and target.color != p.color:
                    moves.append(Move((r, c), (nr, nc)))
        # (Tidak implement en passant demi kesederhanaan)
        return moves

    @staticmethod
    def _knight_moves(board: Board, r: int, c: int, p: Piece) -> List[Move]:
        moves: List[Move] = []
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = r+dr, c+dc
            if not board.inside(nr, nc): 
                continue
            target = board.piece_at(nr, nc)
            if target is None or target.color != p.color:
                moves.append(Move((r, c), (nr, nc)))
        return moves

    @staticmethod
    def _slide_moves(board: Board, r: int, c: int, p: Piece, directions: List[Tuple[int,int]]) -> List[Move]:
        moves: List[Move] = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.inside(nr, nc):
                target = board.piece_at(nr, nc)
                if target is None:
                    moves.append(Move((r, c), (nr, nc)))
                else:
                    if target.color != p.color:
                        moves.append(Move((r, c), (nr, nc)))
                    break
                nr += dr
                nc += dc
        return moves

    @staticmethod
    def _king_moves(board: Board, r: int, c: int, p: Piece) -> List[Move]:
        moves: List[Move] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r+dr, c+dc
                if not board.inside(nr, nc):
                    continue
                target = board.piece_at(nr, nc)
                if target is None or target.color != p.color:
                    moves.append(Move((r, c), (nr, nc)))
        # (Tidak implement castling demi kesederhanaan)
        return moves

# =========================
# Evaluator dan AI Sederhana
# =========================
class Evaluator:
    @staticmethod
    def material_score(board: Board, color: Color) -> int:
        score = 0
        for r in range(ROWS):
            for c in range(COLS):
                p = board.piece_at(r, c)
                if p:
                    val = PIECE_VALUES[p.kind]
                    score += val if p.color == color else -val
        return score

    @staticmethod
    def captured_value(board: Board, mv: Move) -> int:
        dr, dc = mv.dst
        target = board.piece_at(dr, dc)
        if target:
            return PIECE_VALUES[target.kind]
        return 0

class SimpleAI:
    def __init__(self, color: Color):
        self.color = color

    def choose_move(self, board: Board) -> Optional[Move]:
        moves = Rules.generate_moves(board, self.color)
        if not moves:
            return None

        # 1) Cari capture terbaik
        best_capture = None
        best_value = -999
        for mv in moves:
            val = Evaluator.captured_value(board, mv)
            if val > best_value and val > 0:
                best_value = val
                best_capture = mv
        if best_capture:
            return best_capture

        # 2) Kalau tidak ada capture, pilih langkah yang meningkatkan material (1-ply lookahead)
        best_move = None
        best_score = -9999
        for mv in moves:
            sim = board.copy()
            sim.move_piece(mv)
            sc = Evaluator.material_score(sim, self.color)
            if sc > best_score:
                best_score = sc
                best_move = mv

        # 3) Fallback random bila skornya sama saja
        return best_move or random.choice(moves)

# =========================
# UI / Rendering (Pygame)
# =========================
class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        # Coba beberapa font yang umumnya punya glyph catur
        candidates = [
            "Segoe UI Symbol",
            "DejaVu Sans",
            "Arial Unicode MS",
            "Noto Sans Symbols2",
            "Noto Sans Symbols",
        ]
        font = None
        for name in candidates:
            try:
                font = pygame.font.SysFont(name, int(SQ_SIZE * 0.8))
                # quick check by rendering a glyph
                if font is not None:
                    test = font.render("♔", True, (0, 0, 0))
                    if test is not None:
                        break
            except:
                font = None
        if font is None:
            # fallback default
            font = pygame.font.SysFont(None, int(SQ_SIZE * 0.8))
        self.font = font

    def draw_board(self, selected: Optional[Tuple[int,int]] = None, moves: List[Move] = []):
        # Gambar kotak
        for r in range(ROWS):
            for c in range(COLS):
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                rect = pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, color, rect)
        # Highlight kotak terpilih
        if selected:
            sr, sc = selected
            rect = pygame.Rect(sc*SQ_SIZE, sr*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect, border_radius=6)

        # Hint langkah dari petak terpilih
        if selected and moves:
            sr, sc = selected
            for mv in moves:
                if mv.src == (sr, sc):
                    dr, dc = mv.dst
                    cx = dc*SQ_SIZE + SQ_SIZE//2
                    cy = dr*SQ_SIZE + SQ_SIZE//2
                    pygame.draw.circle(self.screen, COLOR_MOVE_HINT, (cx, cy), 8)

    def draw_pieces(self, board: Board):
        for r in range(ROWS):
            for c in range(COLS):
                p = board.piece_at(r, c)
                if p:
                    sym = UNICODE_PIECES[(p.color, p.kind)]
                    text = self.font.render(sym, True, (20, 20, 20))
                    tr = text.get_rect(center=(c*SQ_SIZE + SQ_SIZE//2, r*SQ_SIZE + SQ_SIZE//2 + 2))
                    self.screen.blit(text, tr)

# =========================
# Game: mengikat semuanya
# =========================
class Game:
    def __init__(self, human_color: Color = Color.WHITE):
        pygame.init()
        pygame.display.set_caption("Mini Chess Engine - Pygame Unicode")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.renderer = Renderer(self.screen)
        self.human_color = human_color
        self.ai = SimpleAI(Color.BLACK if human_color == Color.WHITE else Color.WHITE)
        self.selected_sq: Optional[Tuple[int,int]] = None
        self.legal_moves_cache: List[Move] = Rules.generate_moves(self.board, self.board.turn)
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._maybe_ai_move()
            self._render()

        pygame.quit()
        sys.exit(0)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(pygame.mouse.get_pos())

    def _board_coords_from_mouse(self, pos: Tuple[int,int]) -> Tuple[int,int]:
        x, y = pos
        c = x // SQ_SIZE
        r = y // SQ_SIZE
        return (r, c)

    def _handle_click(self, pos: Tuple[int,int]):
        if self.board.turn != self.human_color:
            return  # bukan giliran manusia

        r, c = self._board_coords_from_mouse(pos)
        if not self.board.inside(r, c):
            return

        p = self.board.piece_at(r, c)

        # Jika belum ada seleksi dan klik di bidak sendiri -> seleksi
        if self.selected_sq is None:
            if p and p.color == self.human_color:
                self.selected_sq = (r, c)
            return

        # Jika ada seleksi:
        sr, sc = self.selected_sq
        # Klik bidak sendiri lain -> ganti seleksi
        if p and p.color == self.human_color and (r, c) != (sr, sc):
            self.selected_sq = (r, c)
            return

        # Coba lakukan langkah jika legal
        move = Move((sr, sc), (r, c))
        if self._is_legal(move):
            self.board.move_piece(move)
            self.selected_sq = None
            self._refresh_legal_moves()
        else:
            # Jika klik kotak kosong bukan langkah legal -> batalkan seleksi
            if not p:
                self.selected_sq = None

    def _is_legal(self, mv: Move) -> bool:
        # Validasi berdasarkan pseudo-legal dari Rules (tanpa cek skak)
        return any(m.src == mv.src and m.dst == mv.dst for m in self.legal_moves_cache)

    def _refresh_legal_moves(self):
        self.legal_moves_cache = Rules.generate_moves(self.board, self.board.turn)

    def _maybe_ai_move(self):
        # Jika gilirannya AI, biarkan AI jalan
        if self.board.turn == self.ai.color and self.running:
            pygame.time.delay(150)  # kecil jeda agar terasa "berpikir"
            mv = self.ai.choose_move(self.board)
            if mv is not None:
                self.board.move_piece(mv)
            # jika tidak ada langkah, game over (stalemate/cekmat - kita cukup hentikan loop)
            else:
                self.running = False
            self._refresh_legal_moves()

    def _render(self):
        # Kumpulkan moves dari selected untuk hint
        moves_from_selected = []
        if self.selected_sq:
            sr, sc = self.selected_sq
            moves_from_selected = [m for m in self.legal_moves_cache if m.src == (sr, sc)]
        self.renderer.draw_board(self.selected_sq, moves_from_selected)
        self.renderer.draw_pieces(self.board)
        pygame.display.flip()

# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    # Human main sebagai Putih vs AI Hitam
    game = Game(human_color=Color.WHITE)
    game.run()
