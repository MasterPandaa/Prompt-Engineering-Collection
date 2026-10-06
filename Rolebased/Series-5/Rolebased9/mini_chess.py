# mini_chess.py
# Playable mini chess engine using Python + Pygame
# - Board and Rules separated
# - Unicode piece rendering
# - Simple material-eval AI that prefers free captures
# - Click-to-select, click-to-move with highlighting

import sys
import math
import pygame
from pygame import Rect

# --------------- Config ---------------
WINDOW_SIZE = 640
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_SIZE // BOARD_SIZE
FPS = 60

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
MOVE_DOT_COLOR = (40, 40, 40)
CHECK_HIGHLIGHT = (255, 90, 90)

# Piece unicode map
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

PIECE_VALUES = {
    'K': 0,   # evaluate as 0 for material; game end handled separately
    'Q': 9,
    'R': 5,
    'B': 3,
    'N': 3,
    'P': 1
}

# --------------- Board ----------------
class Board:
    def __init__(self):
        # board[row][col] -> (color, piece) or None
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.to_move = 'w'
        self.history = []  # for undo
        self._setup_start()

    def _setup_start(self):
        # Black back rank
        self.board[0] = [
            ('b', 'R'), ('b', 'N'), ('b', 'B'), ('b', 'Q'),
            ('b', 'K'), ('b', 'B'), ('b', 'N'), ('b', 'R')
        ]
        # Black pawns
        self.board[1] = [('b', 'P') for _ in range(8)]
        # Empty
        for r in range(2, 6):
            self.board[r] = [None for _ in range(8)]
        # White pawns
        self.board[6] = [('w', 'P') for _ in range(8)]
        # White back rank
        self.board[7] = [
            ('w', 'R'), ('w', 'N'), ('w', 'B'), ('w', 'Q'),
            ('w', 'K'), ('w', 'B'), ('w', 'N'), ('w', 'R')
        ]

    def clone(self):
        nb = Board.__new__(Board)
        nb.board = [row[:] for row in self.board]
        nb.to_move = self.to_move
        nb.history = self.history[:]  # shallow copy sufficient
        return nb

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def at(self, r, c):
        return self.board[r][c]

    def set_at(self, r, c, piece):
        self.board[r][c] = piece

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == (color, 'K'):
                    return (r, c)
        return None

    def make_move(self, move):
        # move: (sr, sc, dr, dc, promotion)
        sr, sc, dr, dc, promo = move
        piece = self.at(sr, sc)
        captured = self.at(dr, dc)
        self.history.append((move, captured))
        # move piece
        self.set_at(dr, dc, piece)
        self.set_at(sr, sc, None)
        # handle promotion
        if promo:
            color, _ = piece
            self.set_at(dr, dc, (color, promo))
        # side to move
        self.to_move = 'b' if self.to_move == 'w' else 'w'

    def undo(self):
        if not self.history:
            return
        (sr, sc, dr, dc, promo), captured = self.history.pop()
        piece = self.at(dr, dc)
        # undo promotion
        if promo:
            color, _ = piece
            piece = (color, 'P')
        self.set_at(sr, sc, piece)
        self.set_at(dr, dc, captured)
        self.to_move = 'b' if self.to_move == 'w' else 'w'

    def material_score(self, color):
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    side, kind = p
                    val = PIECE_VALUES[kind]
                    score += val if side == color else -val
        return score

# --------------- Rules ----------------
class Rules:
    @staticmethod
    def generate_legal_moves(board: Board, color: str):
        # Pseudo-legal then filter out those leaving own king in check
        moves = Rules.generate_pseudo_legal(board, color)
        legal = []
        for mv in moves:
            board.make_move(mv)
            if not Rules.is_in_check(board, color):
                legal.append(mv)
            board.undo()
        return legal

    @staticmethod
    def generate_pseudo_legal(board: Board, color: str):
        moves = []
        for r in range(8):
            for c in range(8):
                p = board.at(r, c)
                if p and p[0] == color:
                    kind = p[1]
                    if kind == 'P':
                        moves.extend(Rules._pawn_moves(board, r, c, color))
                    elif kind == 'N':
                        moves.extend(Rules._knight_moves(board, r, c, color))
                    elif kind == 'B':
                        moves.extend(Rules._bishop_moves(board, r, c, color))
                    elif kind == 'R':
                        moves.extend(Rules._rook_moves(board, r, c, color))
                    elif kind == 'Q':
                        moves.extend(Rules._queen_moves(board, r, c, color))
                    elif kind == 'K':
                        moves.extend(Rules._king_moves(board, r, c, color))
        return moves

    @staticmethod
    def is_in_check(board: Board, color: str):
        # Is color's king attacked by the opponent?
        king_pos = board.find_king(color)
        if not king_pos:
            return True  # no king means effectively check (game over)
        kr, kc = king_pos
        opp = 'b' if color == 'w' else 'w'
        # generate all opponent pseudo moves and see if any hits king
        for r in range(8):
            for c in range(8):
                p = board.at(r, c)
                if p and p[0] == opp:
                    kind = p[1]
                    if kind == 'P':
                        dirs = [(-1, -1), (-1, 1)] if opp == 'w' else [(1, -1), (1, 1)]
                        for dr, dc in dirs:
                            rr, cc = r + dr, c + dc
                            if board.in_bounds(rr, cc) and (rr, cc) == (kr, kc):
                                return True
                    elif kind == 'N':
                        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                                       (1, -2), (1, 2), (2, -1), (2, 1)]:
                            rr, cc = r + dr, c + dc
                            if board.in_bounds(rr, cc) and (rr, cc) == (kr, kc):
                                return True
                    elif kind in ('B', 'R', 'Q'):
                        for dr, dc in Rules._sliding_dirs(kind):
                            rr, cc = r + dr, c + dc
                            while board.in_bounds(rr, cc):
                                p2 = board.at(rr, cc)
                                if (rr, cc) == (kr, kc):
                                    return True
                                if p2:
                                    break
                                rr += dr
                                cc += dc
                    elif kind == 'K':
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                rr, cc = r + dr, c + dc
                                if board.in_bounds(rr, cc) and (rr, cc) == (kr, kc):
                                    return True
        return False

    @staticmethod
    def _pawn_moves(board: Board, r, c, color):
        moves = []
        dir_forward = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        promote_row = 0 if color == 'w' else 7

        # forward 1
        fr, fc = r + dir_forward, c
        if board.in_bounds(fr, fc) and board.at(fr, fc) is None:
            promo = 'Q' if fr == promote_row else None
            moves.append((r, c, fr, fc, promo))
            # forward 2
            fr2 = r + 2 * dir_forward
            if r == start_row and board.in_bounds(fr2, fc) and board.at(fr2, fc) is None:
                moves.append((r, c, fr2, fc, None))

        # captures
        for dc in [-1, 1]:
            rr, cc = r + dir_forward, c + dc
            if board.in_bounds(rr, cc):
                target = board.at(rr, cc)
                if target and target[0] != color:
                    promo = 'Q' if rr == promote_row else None
                    moves.append((r, c, rr, cc, promo))

        # en passant omitted (by design to keep it simple)
        return moves

    @staticmethod
    def _knight_moves(board: Board, r, c, color):
        moves = []
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]:
            rr, cc = r + dr, c + dc
            if board.in_bounds(rr, cc):
                target = board.at(rr, cc)
                if target is None or target[0] != color:
                    moves.append((r, c, rr, cc, None))
        return moves

    @staticmethod
    def _sliding_dirs(kind):
        if kind == 'B':
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if kind == 'R':
            return [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Queen
        return [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]

    @staticmethod
    def _slide(board: Board, r, c, color, dirs):
        moves = []
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while board.in_bounds(rr, cc):
                target = board.at(rr, cc)
                if target is None:
                    moves.append((r, c, rr, cc, None))
                else:
                    if target[0] != color:
                        moves.append((r, c, rr, cc, None))
                    break
                rr += dr
                cc += dc
        return moves

    @staticmethod
    def _bishop_moves(board: Board, r, c, color):
        return Rules._slide(board, r, c, color, Rules._sliding_dirs('B'))

    @staticmethod
    def _rook_moves(board: Board, r, c, color):
        return Rules._slide(board, r, c, color, Rules._sliding_dirs('R'))

    @staticmethod
    def _queen_moves(board: Board, r, c, color):
        return Rules._slide(board, r, c, color, Rules._sliding_dirs('Q'))

    @staticmethod
    def _king_moves(board: Board, r, c, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if board.in_bounds(rr, cc):
                    target = board.at(rr, cc)
                    if target is None or target[0] != color:
                        moves.append((r, c, rr, cc, None))
        # Castling omitted for simplicity
        return moves

# --------------- Simple AI ----------------
class SimpleAI:
    def __init__(self, color: str):
        self.color = color

    def choose_move(self, board: Board):
        legal = Rules.generate_legal_moves(board, self.color)
        if not legal:
            return None

        # 1) Prefer winning captures (MVV-LVA-ish by material gain)
        best_cap = None
        best_gain = -math.inf
        for mv in legal:
            sr, sc, dr, dc, promo = mv
            captured = board.at(dr, dc)
            if captured:
                gain = PIECE_VALUES[captured[1]]
                # simulate lose back piece naive: subtract moving piece value (LVA)
                mover = board.at(sr, sc)
                if mover:
                    gain -= PIECE_VALUES[mover[1]] * 0.1  # small penalty
                if promo == 'Q':
                    gain += PIECE_VALUES['Q'] - PIECE_VALUES['P']
                if gain > best_gain:
                    best_gain = gain
                    best_cap = mv
        if best_cap and best_gain > 0:
            return best_cap

        # 2) Else, 1-ply static eval: maximize our material score after move
        best_score = -math.inf
        best_move = None
        for mv in legal:
            board.make_move(mv)
            score = board.material_score(self.color)
            board.undo()
            if score > best_score:
                best_score = score
                best_move = mv

        return best_move or legal[0]

# --------------- Rendering / Game ---------------
class Game:
    def __init__(self, human_color='w'):
        pygame.init()
        pygame.display.set_caption("Mini Chess - Python + Pygame")
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.clock = pygame.time.Clock()
        self.board = Board()

        self.human_color = human_color
        self.ai_color = 'b' if human_color == 'w' else 'w'
        self.ai = SimpleAI(self.ai_color)

        self.selected = None
        self.legal_moves_from_selected = []
        self.running = True

        # Font fallback
        self.font = self._load_chess_font(int(SQUARE_SIZE * 0.8))

    def _load_chess_font(self, size):
        candidates = [
            'segoe ui symbol',    # Windows
            'arial unicode ms',
            'dejavusans',
            None                  # default
        ]
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, size)
                # quick render test
                surf = f.render('♔', True, (0, 0, 0))
                if surf:  # success
                    return f
            except Exception:
                continue
        return pygame.font.SysFont(None, size)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            # AI move if it's AI's turn and game not over
            if self.board.to_move == self.ai_color and not self._game_over():
                pygame.time.delay(150)  # small think time for UX
                mv = self.ai.choose_move(self.board)
                if mv:
                    self.board.make_move(mv)
                    self._clear_selection()

            self._draw()

        pygame.quit()
        sys.exit(0)

    def _clear_selection(self):
        self.selected = None
        self.legal_moves_from_selected = []

    def _square_at_pixel(self, x, y):
        return y // SQUARE_SIZE, x // SQUARE_SIZE

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._game_over():
                    return
                if self.board.to_move != self.human_color:
                    return
                mx, my = pygame.mouse.get_pos()
                r, c = self._square_at_pixel(mx, my)
                self._handle_click(r, c)

    def _handle_click(self, r, c):
        # First click: select own piece
        if self.selected is None:
            p = self.board.at(r, c)
            if p and p[0] == self.human_color:
                self.selected = (r, c)
                self.legal_moves_from_selected = [
                    mv for mv in Rules.generate_legal_moves(self.board, self.human_color)
                    if mv[0] == r and mv[1] == c
                ]
        else:
            # Second click: attempt move if legal
            sr, sc = self.selected
            chosen = None
            for mv in self.legal_moves_from_selected:
                _, _, dr, dc, _ = mv
                if (dr, dc) == (r, c):
                    chosen = mv
                    break
            if chosen:
                self.board.make_move(chosen)
            self._clear_selection()

    def _game_over(self):
        # If side to move has no legal moves: checkmate or stalemate
        color = self.board.to_move
        legal = Rules.generate_legal_moves(self.board, color)
        if legal:
            return False
        if Rules.is_in_check(self.board, color):
            pygame.display.set_caption(f"Mini Chess - Checkmate! {'White' if color=='b' else 'Black'} wins")
        else:
            pygame.display.set_caption("Mini Chess - Stalemate!")
        return True

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                is_light = (r + c) % 2 == 0
                color = LIGHT_COLOR if is_light else DARK_COLOR
                rect = Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

        # highlight selection
        if self.selected:
            sr, sc = self.selected
            rect = Rect(sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect)

        # highlight check on current player's king (visual cue)
        for side in ('w', 'b'):
            if Rules.is_in_check(self.board, side):
                kp = self.board.find_king(side)
                if kp:
                    kr, kc = kp
                    rect = Rect(kc * SQUARE_SIZE, kr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    pygame.draw.rect(self.screen, CHECK_HIGHLIGHT, rect, width=4)

        # draw move targets
        for mv in self.legal_moves_from_selected:
            _, _, dr, dc, _ = mv
            cx = dc * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = dr * SQUARE_SIZE + SQUARE_SIZE // 2
            radius = max(6, SQUARE_SIZE // 10)
            pygame.draw.circle(self.screen, MOVE_DOT_COLOR, (cx, cy), radius)

    def _draw_pieces(self):
        for r in range(8):
            for c in range(8):
                p = self.board.at(r, c)
                if not p:
                    continue
                symbol = UNICODE_PIECES.get(p, '?')
                # choose color contrasting with square
                is_light = (r + c) % 2 == 0
                text_color = (30, 30, 30) if is_light else (240, 240, 240)
                surf = self.font.render(symbol, True, text_color)
                rect = surf.get_rect(center=(
                    c * SQUARE_SIZE + SQUARE_SIZE // 2,
                    r * SQUARE_SIZE + SQUARE_SIZE // 2
                ))
                self.screen.blit(surf, rect)

    def _draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_board()
        self._draw_pieces()
        pygame.display.flip()

# --------------- Entry Point ---------------
if __name__ == "__main__":
    # Default: Human plays White vs AI Black.
    # To switch, pass "black" as CLI arg: python mini_chess.py black
    human_color = 'w'
    if len(sys.argv) > 1 and sys.argv[1].lower().startswith('b'):
        human_color = 'b'
    Game(human_color=human_color).run()
