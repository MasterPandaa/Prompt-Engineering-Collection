import sys
import math
import pygame
from copy import deepcopy

# ---------------------------
# Config & Constants
# ---------------------------
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
SELECTED = (186, 202, 68)
MOVE_DOT = (50, 50, 50, 140)

# Unicode pieces
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

# Material values for evaluation
MATERIAL_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0  # King is invaluable; keep 0 for simple eval
}

# ---------------------------
# Board: representation & state
# ---------------------------
class Board:
    def __init__(self):
        # 8x8 with (color, type) or None
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.reset()

    def reset(self):
        # Place black
        self.grid[0] = [
            ('b', 'R'), ('b', 'N'), ('b', 'B'), ('b', 'Q'),
            ('b', 'K'), ('b', 'B'), ('b', 'N'), ('b', 'R')
        ]
        self.grid[1] = [('b', 'P')] * 8
        # Empty middle
        for r in range(2, 6):
            self.grid[r] = [None] * 8
        # Place white
        self.grid[6] = [('w', 'P')] * 8
        self.grid[7] = [
            ('w', 'R'), ('w', 'N'), ('w', 'B'), ('w', 'Q'),
            ('w', 'K'), ('w', 'B'), ('w', 'N'), ('w', 'R')
        ]

    def in_bounds(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def get(self, r, c):
        if not self.in_bounds(r, c):
            return None
        return self.grid[r][c]

    def set(self, r, c, piece):
        if self.in_bounds(r, c):
            self.grid[r][c] = piece

    def move_piece(self, src, dst, promotion=None):
        sr, sc = src
        dr, dc = dst
        piece = self.get(sr, sc)
        if not piece:
            return
        color, ptype = piece
        # Pawn promotion simple rule
        if ptype == 'P':
            if color == 'w' and dr == 0:
                ptype = promotion if promotion else 'Q'
            elif color == 'b' and dr == 7:
                ptype = promotion if promotion else 'Q'
        self.set(dr, dc, (color, ptype))
        self.set(sr, sc, None)

    def clone(self):
        b = Board.__new__(Board)
        b.grid = deepcopy(self.grid)
        return b

    def material_score(self, color):
        score = 0
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.grid[r][c]
                if piece:
                    pcolor, ptype = piece
                    val = MATERIAL_VALUES.get(ptype, 0)
                    score += val if pcolor == color else -val
        return score

# ---------------------------
# Rules: legal move generation per piece
# ---------------------------
class Rules:
    def __init__(self):
        pass

    def generate_legal_moves(self, board, turn_color):
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = board.get(r, c)
                if piece and piece[0] == turn_color:
                    ptype = piece[1]
                    if ptype == 'P':
                        moves.extend(self._pawn_moves(board, r, c, piece))
                    elif ptype == 'N':
                        moves.extend(self._knight_moves(board, r, c, piece))
                    elif ptype == 'B':
                        moves.extend(self._sliding_moves(board, r, c, piece, directions=[(-1,-1),(-1,1),(1,-1),(1,1)]))
                    elif ptype == 'R':
                        moves.extend(self._sliding_moves(board, r, c, piece, directions=[(-1,0),(1,0),(0,-1),(0,1)]))
                    elif ptype == 'Q':
                        moves.extend(self._sliding_moves(board, r, c, piece, directions=[(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]))
                    elif ptype == 'K':
                        moves.extend(self._king_moves(board, r, c, piece))
        # Note: This engine does not check for self-check legality for simplicity.
        return moves

    def _is_enemy(self, piece, color):
        return piece is not None and piece[0] != color

    def _is_empty(self, piece):
        return piece is None

    def _pawn_moves(self, board, r, c, piece):
        color, _ = piece
        dir_forward = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        moves = []

        # Forward 1
        nr, nc = r + dir_forward, c
        if board.in_bounds(nr, nc) and board.get(nr, nc) is None:
            moves.append(((r, c), (nr, nc)))
            # Forward 2 from start
            nr2 = nr + dir_forward
            if r == start_row and board.in_bounds(nr2, nc) and board.get(nr2, nc) is None:
                moves.append(((r, c), (nr2, nc)))

        # Captures
        for dc in (-1, 1):
            cr, cc = r + dir_forward, c + dc
            if board.in_bounds(cr, cc):
                target = board.get(cr, cc)
                if self._is_enemy(target, color):
                    moves.append(((r, c), (cr, cc)))

        # Promotions handled in move application by Board
        return moves

    def _knight_moves(self, board, r, c, piece):
        color, _ = piece
        moves = []
        deltas = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not board.in_bounds(nr, nc):
                continue
            target = board.get(nr, nc)
            if target is None or self._is_enemy(target, color):
                moves.append(((r, c), (nr, nc)))
        return moves

    def _sliding_moves(self, board, r, c, piece, directions):
        color, _ = piece
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while board.in_bounds(nr, nc):
                target = board.get(nr, nc)
                if target is None:
                    moves.append(((r, c), (nr, nc)))
                else:
                    if self._is_enemy(target, color):
                        moves.append(((r, c), (nr, nc)))
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, board, r, c, piece):
        color, _ = piece
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not board.in_bounds(nr, nc):
                    continue
                target = board.get(nr, nc)
                if target is None or self._is_enemy(target, color):
                    moves.append(((r, c), (nr, nc)))
        # No castling for simplicity
        return moves

# ---------------------------
# Simple AI: 1-ply material capture preference
# ---------------------------
class SimpleAI:
    def __init__(self, rules, color='b'):
        self.rules = rules
        self.color = color

    def choose_move(self, board):
        moves = self.rules.generate_legal_moves(board, self.color)
        if not moves:
            return None

        # Score each move by resulting material balance for AI color
        best_score = -math.inf
        best_moves = []

        for move in moves:
            src, dst = move
            sr, sc = src
            dr, dc = dst
            captured = board.get(dr, dc)
            # Quick capture priority: add captured value first
            capture_bonus = MATERIAL_VALUES.get(captured[1], 0) if captured else 0

            sim = board.clone()
            sim.move_piece(src, dst)

            # Basic evaluation: material for AI color after move
            eval_score = sim.material_score(self.color) + (0.1 * capture_bonus)

            if eval_score > best_score:
                best_score = eval_score
                best_moves = [move]
            elif eval_score == best_score:
                best_moves.append(move)

        # Prefer captures among equal best moves
        capture_best = []
        cap_best_val = 0
        for mv in best_moves:
            _, (dr, dc) = mv
            cap = board.get(dr, dc)
            if cap:
                val = MATERIAL_VALUES.get(cap[1], 0)
                if val > cap_best_val:
                    capture_best = [mv]
                    cap_best_val = val
                elif val == cap_best_val:
                    capture_best.append(mv)

        import random
        if capture_best:
            return random.choice(capture_best)
        return random.choice(best_moves)

# ---------------------------
# Game: input handling & rendering
# ---------------------------
class Game:
    def __init__(self, ai_color='b'):
        pygame.init()
        pygame.display.set_caption("Mini Chess Engine (Python + Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # Font: Try fonts with chess symbols support, fallback to default
        # Segoe UI Symbol commonly supports chess glyphs on Windows
        self.font = pygame.font.SysFont("Segoe UI Symbol", SQUARE_SIZE - 10, bold=True)
        if self.font is None:
            self.font = pygame.font.SysFont(None, SQUARE_SIZE - 10, bold=True)

        self.board = Board()
        self.rules = Rules()
        self.selected = None
        self.legal_moves_from_selected = []
        self.current_turn = 'w'
        self.ai = SimpleAI(self.rules, color=ai_color)
        self.ai_thinking = False

    def coord_from_mouse(self, pos):
        x, y = pos
        c = x // SQUARE_SIZE
        r = y // SQUARE_SIZE
        return r, c

    def is_ai_turn(self):
        return self.current_turn == self.ai.color

    def handle_click(self, pos):
        r, c = self.coord_from_mouse(pos)
        piece = self.board.get(r, c)

        # If nothing selected yet
        if self.selected is None:
            if piece and piece[0] == self.current_turn:
                self.selected = (r, c)
                self.legal_moves_from_selected = [
                    mv for mv in self.rules.generate_legal_moves(self.board, self.current_turn)
                    if mv[0] == self.selected
                ]
            return

        # If clicked the same color piece, reselect
        if piece and piece[0] == self.current_turn:
            self.selected = (r, c)
            self.legal_moves_from_selected = [
                mv for mv in self.rules.generate_legal_moves(self.board, self.current_turn)
                if mv[0] == self.selected
            ]
            return

        # Attempt move if clicked destination is in legal moves
        for mv in self.legal_moves_from_selected:
            src, dst = mv
            if dst == (r, c):
                self.board.move_piece(src, dst)
                self._post_move()
                return

        # Otherwise clear selection
        self.selected = None
        self.legal_moves_from_selected = []

    def _post_move(self):
        # Clear selection, switch turn
        self.selected = None
        self.legal_moves_from_selected = []
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

    def ai_move_if_needed(self):
        if not self.is_ai_turn():
            return
        mv = self.ai.choose_move(self.board)
        if mv is None:
            # No moves available (basic): switch to avoid freeze
            self._post_move()
            return
        self.board.move_piece(mv[0], mv[1])
        self._post_move()

    def draw(self):
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        pygame.display.flip()

    def _draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_highlights(self):
        # Selected square
        if self.selected:
            sr, sc = self.selected
            rect = pygame.Rect(sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, SELECTED, rect, 0)

            # Re-draw top highlight border to distinguish
            pygame.draw.rect(self.screen, (80, 120, 20), rect, 3)

        # Legal moves from selected
        for mv in self.legal_moves_from_selected:
            _, (dr, dc) = mv
            cx = dc * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = dr * SQUARE_SIZE + SQUARE_SIZE // 2
            radius = 7
            # Soft dot for move; larger ring if capturing
            target = self.board.get(dr, dc)
            if target is None:
                pygame.draw.circle(self.screen, (30, 30, 30), (cx, cy), radius)
            else:
                pygame.draw.circle(self.screen, (200, 30, 30), (cx, cy), radius + 8, 4)

    def _draw_pieces(self):
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board.get(r, c)
                if piece:
                    glyph = UNICODE_PIECES[piece]
                    text_color = (10, 10, 10) if piece[0] == 'b' else (250, 250, 250)
                    # Drop shadow for contrast
                    shadow = self.font.render(glyph, True, (0, 0, 0))
                    text = self.font.render(glyph, True, text_color)
                    x = c * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
                    y = r * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
                    self.screen.blit(shadow, (x + 2, y + 2))
                    self.screen.blit(text, (x, y))

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            if self.is_ai_turn():
                self.ai_move_if_needed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.is_ai_turn():
                        self.handle_click(event.pos)

            self.draw()

        pygame.quit()
        sys.exit()

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    # Human plays White, AI plays Black by default.
    # To switch, set ai_color='w' and adapt input handling if desired.
    game = Game(ai_color='b')
    game.run()
