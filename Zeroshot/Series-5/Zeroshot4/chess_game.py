import sys
import random
import pygame
from typing import List, Tuple, Optional

# ----------------------------------------------
# Configuration
# ----------------------------------------------
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
TILE_SIZE = WIDTH // COLS

LIGHT_COLOR = (240, 217, 181)  # light squares
DARK_COLOR = (181, 136, 99)     # dark squares
HIGHLIGHT_MOVE = (30, 144, 255, 130)  # semi-transparent blue
HIGHLIGHT_SELECT = (0, 255, 0, 120)   # semi-transparent green
CHECK_RED = (220, 20, 60, 120)

FPS = 60

# Unicode chess glyphs mapping
UNICODE_PIECES = {
    ("w", "K"): "\u2654",
    ("w", "Q"): "\u2655",
    ("w", "R"): "\u2656",
    ("w", "B"): "\u2657",
    ("w", "N"): "\u2658",
    ("w", "P"): "\u2659",
    ("b", "K"): "\u265A",
    ("b", "Q"): "\u265B",
    ("b", "R"): "\u265C",
    ("b", "B"): "\u265D",
    ("b", "N"): "\u265E",
    ("b", "P"): "\u265F",
}

PIECE_VALUES = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

# ----------------------------------------------
# Data Model
# ----------------------------------------------
class Piece:
    def __init__(self, color: str, kind: str):
        self.color = color  # 'w' or 'b'
        self.kind = kind    # 'K','Q','R','B','N','P'

    def __repr__(self):
        return f"{self.color}{self.kind}"

Board = List[List[Optional[Piece]]]
Move = Tuple[Tuple[int, int], Tuple[int, int]]  # ((r1,c1),(r2,c2))

# ----------------------------------------------
# Game Logic
# ----------------------------------------------
def initial_board() -> Board:
    board: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    # Place pieces
    # White at bottom (row 6-7), Black at top (row 0-1)
    order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for c, k in enumerate(order):
        board[0][c] = Piece("b", k)
        board[7][c] = Piece("w", k)
    for c in range(COLS):
        board[1][c] = Piece("b", "P")
        board[6][c] = Piece("w", "P")
    return board


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def find_king(board: Board, color: str) -> Optional[Tuple[int, int]]:
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p and p.color == color and p.kind == "K":
                return (r, c)
    return None


def is_square_attacked(board: Board, target: Tuple[int, int], by_color: str) -> bool:
    # Generate pseudo-legal moves for by_color and see if any hits target
    moves = generate_pseudo_legal_moves(board, by_color)
    for m in moves:
        if m[1] == target:
            return True
    return False


def is_in_check(board: Board, color: str) -> bool:
    king_pos = find_king(board, color)
    if not king_pos:
        return False
    opp = "b" if color == "w" else "w"
    return is_square_attacked(board, king_pos, opp)


def clone_board(board: Board) -> Board:
    return [[Piece(p.color, p.kind) if p else None for p in row] for row in board]


def make_move(board: Board, move: Move) -> Board:
    (r1, c1), (r2, c2) = move
    newb = clone_board(board)
    piece = newb[r1][c1]
    newb[r1][c1] = None
    newb[r2][c2] = piece
    # Pawn promotion (auto-queen)
    if piece and piece.kind == "P":
        if piece.color == "w" and r2 == 0:
            newb[r2][c2] = Piece("w", "Q")
        if piece.color == "b" and r2 == ROWS - 1:
            newb[r2][c2] = Piece("b", "Q")
    return newb


def generate_pseudo_legal_moves(board: Board, color: str) -> List[Move]:
    moves: List[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if not p or p.color != color:
                continue
            if p.kind == "P":
                pawn_moves(board, r, c, p, moves)
            elif p.kind == "N":
                knight_moves(board, r, c, p, moves)
            elif p.kind == "B":
                bishop_moves(board, r, c, p, moves)
            elif p.kind == "R":
                rook_moves(board, r, c, p, moves)
            elif p.kind == "Q":
                queen_moves(board, r, c, p, moves)
            elif p.kind == "K":
                king_moves(board, r, c, p, moves)
    return moves


def generate_legal_moves(board: Board, color: str) -> List[Move]:
    legal: List[Move] = []
    for m in generate_pseudo_legal_moves(board, color):
        nb = make_move(board, m)
        if not is_in_check(nb, color):
            legal.append(m)
    return legal

# -- Per-piece generators

def pawn_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    dir = -1 if p.color == "w" else 1
    start_row = 6 if p.color == "w" else 1
    # One step forward
    nr = r + dir
    if in_bounds(nr, c) and board[nr][c] is None:
        moves.append(((r, c), (nr, c)))
        # Two steps from start
        nr2 = r + 2 * dir
        if r == start_row and board[nr2][c] is None:
            moves.append(((r, c), (nr2, c)))
    # Captures
    for dc in (-1, 1):
        nc = c + dc
        nr = r + dir
        if in_bounds(nr, nc) and board[nr][nc] is not None and board[nr][nc].color != p.color:
            moves.append(((r, c), (nr, nc)))


def knight_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in jumps:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        q = board[nr][nc]
        if q is None or q.color != p.color:
            moves.append(((r, c), (nr, nc)))


def slide_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move], deltas: List[Tuple[int, int]]):
    for dr, dc in deltas:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            q = board[nr][nc]
            if q is None:
                moves.append(((r, c), (nr, nc)))
            else:
                if q.color != p.color:
                    moves.append(((r, c), (nr, nc)))
                break
            nr += dr
            nc += dc


def bishop_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    slide_moves(board, r, c, p, moves, [(1, 1), (1, -1), (-1, 1), (-1, -1)])


def rook_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    slide_moves(board, r, c, p, moves, [(1, 0), (-1, 0), (0, 1), (0, -1)])


def queen_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    slide_moves(board, r, c, p, moves, [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)])


def king_moves(board: Board, r: int, c: int, p: Piece, moves: List[Move]):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            q = board[nr][nc]
            if q is None or q.color != p.color:
                moves.append(((r, c), (nr, nc)))

# ----------------------------------------------
# AI (very simple material evaluation one-ply)
# ----------------------------------------------

def evaluate_material(board: Board) -> int:
    # Positive if White is ahead, negative if Black ahead
    score = 0
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p:
                v = PIECE_VALUES[p.kind]
                score += v if p.color == "w" else -v
    return score


def ai_choose_move(board: Board, color: str) -> Optional[Move]:
    legal = generate_legal_moves(board, color)
    if not legal:
        return None
    # One-ply material evaluation
    best_score = None
    best_moves: List[Move] = []
    sign = 1 if color == "w" else -1
    for m in legal:
        nb = make_move(board, m)
        sc = evaluate_material(nb) * sign
        if best_score is None or sc > best_score:
            best_score = sc
            best_moves = [m]
        elif sc == best_score:
            best_moves.append(m)
    return random.choice(best_moves) if best_moves else random.choice(legal)

# ----------------------------------------------
# Rendering
# ----------------------------------------------
class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = None
        self.use_unicode = False
        self._init_fonts()
        # For alpha overlays
        self.overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

    def _init_fonts(self):
        pygame.font.init()
        # Try fonts that likely support chess glyphs
        candidates = [
            "DejaVu Sans", "Arial Unicode MS", "Segoe UI Symbol", "Noto Sans Symbols", "Symbola", "Cambria", "Arial"
        ]
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, TILE_SIZE - 10)
                # Test render a white king
                test = f.render(UNICODE_PIECES[("w", "K")], True, (0, 0, 0))
                if test.get_width() > 0:
                    self.font = f
                    self.use_unicode = True
                    break
            except Exception:
                continue
        if self.font is None:
            # Fallback generic font for shapes mode
            self.font = pygame.font.SysFont(None, TILE_SIZE - 10)
            self.use_unicode = False

    def draw_board(self, board: Board, selected: Optional[Tuple[int,int]], legal_moves_for_selected: List[Tuple[int,int]], in_check_square: Optional[Tuple[int,int]]):
        # Draw squares
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
                pygame.draw.rect(self.screen, color, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Highlight selected
        if selected:
            sr, sc = selected
            self.overlay.fill((0,0,0,0))
            pygame.draw.rect(self.overlay, HIGHLIGHT_SELECT, (0, 0, TILE_SIZE, TILE_SIZE))
            self.screen.blit(self.overlay, (sc * TILE_SIZE, sr * TILE_SIZE))
        # Highlight legal moves
        for (mr, mc) in legal_moves_for_selected:
            center = (mc * TILE_SIZE + TILE_SIZE // 2, mr * TILE_SIZE + TILE_SIZE // 2)
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, HIGHLIGHT_MOVE, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//6)
            self.screen.blit(surf, (mc * TILE_SIZE, mr * TILE_SIZE))
        # Highlight check
        if in_check_square:
            cr, cc = in_check_square
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surf, CHECK_RED, (0, 0, TILE_SIZE, TILE_SIZE))
            self.screen.blit(surf, (cc * TILE_SIZE, cr * TILE_SIZE))
        # Draw pieces
        for r in range(ROWS):
            for c in range(COLS):
                p = board[r][c]
                if p:
                    self.draw_piece(p, r, c)

    def draw_piece(self, piece: Piece, r: int, c: int):
        x = c * TILE_SIZE + TILE_SIZE // 2
        y = r * TILE_SIZE + TILE_SIZE // 2
        if self.use_unicode:
            glyph = UNICODE_PIECES[(piece.color, piece.kind)]
            color = (0, 0, 0) if piece.color == "b" else (255, 255, 255)
            # Outline effect: draw text twice with offset
            text_outline = self.font.render(glyph, True, (0, 0, 0))
            text_main = self.font.render(glyph, True, color)
            rect_o = text_outline.get_rect(center=(x+1, y+1))
            rect = text_main.get_rect(center=(x, y))
            self.screen.blit(text_outline, rect_o)
            self.screen.blit(text_main, rect)
        else:
            # Geometric fallback: simple shapes by piece type
            base_color = (20, 20, 20) if piece.color == "b" else (235, 235, 235)
            edge = (0, 0, 0)
            if piece.kind == "P":
                pygame.draw.circle(self.screen, base_color, (x, y), TILE_SIZE//4)
                pygame.draw.circle(self.screen, edge, (x, y), TILE_SIZE//4, 2)
            elif piece.kind == "R":
                rect = pygame.Rect(0, 0, TILE_SIZE//2, TILE_SIZE//2)
                rect.center = (x, y)
                pygame.draw.rect(self.screen, base_color, rect)
                pygame.draw.rect(self.screen, edge, rect, 2)
            elif piece.kind == "N":
                points = [(x - TILE_SIZE//4, y + TILE_SIZE//4), (x, y - TILE_SIZE//4), (x + TILE_SIZE//4, y + TILE_SIZE//4)]
                pygame.draw.polygon(self.screen, base_color, points)
                pygame.draw.polygon(self.screen, edge, points, 2)
            elif piece.kind == "B":
                pygame.draw.ellipse(self.screen, base_color, (x - TILE_SIZE//4, y - TILE_SIZE//3, TILE_SIZE//2, TILE_SIZE//1.5))
                pygame.draw.ellipse(self.screen, edge, (x - TILE_SIZE//4, y - TILE_SIZE//3, TILE_SIZE//2, TILE_SIZE//1.5), 2)
            elif piece.kind == "Q":
                pygame.draw.circle(self.screen, base_color, (x, y - TILE_SIZE//6), TILE_SIZE//6)
                pygame.draw.rect(self.screen, base_color, (x - TILE_SIZE//4, y - TILE_SIZE//8, TILE_SIZE//2, TILE_SIZE//3))
                pygame.draw.rect(self.screen, edge, (x - TILE_SIZE//4, y - TILE_SIZE//8, TILE_SIZE//2, TILE_SIZE//3), 2)
            elif piece.kind == "K":
                pygame.draw.rect(self.screen, base_color, (x - TILE_SIZE//5, y - TILE_SIZE//5, TILE_SIZE//2.5, TILE_SIZE//2.5))
                pygame.draw.rect(self.screen, edge, (x - TILE_SIZE//5, y - TILE_SIZE//5, TILE_SIZE//2.5, TILE_SIZE//2.5), 2)
                pygame.draw.line(self.screen, edge, (x, y - TILE_SIZE//3), (x, y - TILE_SIZE//7), 2)
                pygame.draw.line(self.screen, edge, (x - TILE_SIZE//10, y - TILE_SIZE//5), (x + TILE_SIZE//10, y - TILE_SIZE//5), 2)

# ----------------------------------------------
# Game Controller
# ----------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess - Pygame")
        self.clock = pygame.time.Clock()
        self.board = initial_board()
        self.turn = 'w'  # white to move
        self.selected: Optional[Tuple[int,int]] = None
        self.legal_for_selected: List[Tuple[int,int]] = []
        self.renderer = Renderer(self.screen)
        self.game_over = False
        self.result_text = ""

    def square_at_pixel(self, pos: Tuple[int,int]) -> Optional[Tuple[int,int]]:
        x, y = pos
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if in_bounds(r, c):
            return (r, c)
        return None

    def update_legals_for_selected(self):
        self.legal_for_selected = []
        if not self.selected:
            return
        r, c = self.selected
        p = self.board[r][c]
        if not p or p.color != self.turn:
            return
        # compute legal moves and keep only destinations
        all_legals = generate_legal_moves(self.board, self.turn)
        self.legal_for_selected = [dst for (src, dst) in all_legals if src == (r, c)]

    def click(self, pos: Tuple[int,int]):
        if self.game_over:
            return
        sq = self.square_at_pixel(pos)
        if not sq:
            return
        r, c = sq
        if self.selected:
            # try move
            if (r, c) in self.legal_for_selected:
                self.apply_move((self.selected, (r, c)))
                return
            # otherwise, change selection if clicking same-color piece
            p = self.board[r][c]
            if p and p.color == self.turn:
                self.selected = (r, c)
                self.update_legals_for_selected()
            else:
                self.selected = None
                self.legal_for_selected = []
        else:
            p = self.board[r][c]
            if p and p.color == self.turn:
                self.selected = (r, c)
                self.update_legals_for_selected()

    def apply_move(self, move: Move):
        self.board = make_move(self.board, move)
        self.selected = None
        self.legal_for_selected = []
        self.turn = 'b' if self.turn == 'w' else 'w'
        self.check_game_end()

    def check_game_end(self):
        # Checkmate/Stalemate detection based on legal moves
        legal = generate_legal_moves(self.board, self.turn)
        if not legal:
            if is_in_check(self.board, self.turn):
                self.game_over = True
                self.result_text = "Checkmate! " + ("White" if self.turn == 'b' else "Black") + " wins."
            else:
                self.game_over = True
                self.result_text = "Stalemate! Draw."

    def ai_move_if_needed(self):
        if self.game_over:
            return
        if self.turn == 'b':
            pygame.time.delay(200)  # small delay for UX
            mv = ai_choose_move(self.board, 'b')
            if mv is None:
                self.check_game_end()
                return
            self.board = make_move(self.board, mv)
            self.turn = 'w'
            self.check_game_end()

    def draw(self):
        in_check_sq = None
        if is_in_check(self.board, self.turn):
            kp = find_king(self.board, self.turn)
            in_check_sq = kp
        self.renderer.draw_board(self.board, self.selected, self.legal_for_selected, in_check_sq)
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont(None, 48)
        text = font.render(self.result_text, True, (255, 255, 255))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, rect)
        sub = pygame.font.SysFont(None, 28).render("Press R to Restart or ESC to Quit", True, (230, 230, 230))
        rect2 = sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        self.screen.blit(sub, rect2)

    def restart(self):
        self.board = initial_board()
        self.turn = 'w'
        self.selected = None
        self.legal_for_selected = []
        self.game_over = False
        self.result_text = ""

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.restart()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click(event.pos)
            # AI move
            self.ai_move_if_needed()
            # Draw frame
            self.draw()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
