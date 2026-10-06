import sys
import random
import pygame

# =============================
# Chess with simple AI (pygame)
# - Board: 8x8 list of lists, strings like 'wP', 'bK', etc.
# - Rendering: Unicode chess symbols, no external assets.
# - Move generation: pseudo-legal (no check validation), includes:
#   - Pawn: single, double on first move, diagonal capture, auto-queen promotion
#   - Knight, Bishop, Rook, Queen, King (no castling, no en passant)
# - Turn handling: Human = White, AI = Black by default
# - AI: prefer capture with highest value, else random
# =============================

# Colors and sizes
WIDTH, HEIGHT = 640, 680  # extra space at bottom for status bar
BOARD_SIZE = 8
SQ_SIZE = 640 // BOARD_SIZE
MARGIN_TOP = 0
STATUS_BAR_H = HEIGHT - 640

LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
HIGHLIGHT_SQ = (246, 246, 105)
MOVE_DOT = (80, 80, 80)
CAPTURE_HI = (200, 60, 60)
TEXT_COLOR = (20, 20, 20)

# Unicode pieces
UNICODE_PIECES = {
    'wK': '\u2654', 'wQ': '\u2655', 'wR': '\u2656', 'wB': '\u2657', 'wN': '\u2658', 'wP': '\u2659',
    'bK': '\u265A', 'bQ': '\u265B', 'bR': '\u265C', 'bB': '\u265D', 'bN': '\u265E', 'bP': '\u265F',
}

PIECE_VALUES = {
    'K': 10000,
    'Q': 900,
    'R': 500,
    'B': 330,
    'N': 320,
    'P': 100,
}

# Starting position (rank 8 at index 0)
START_FEN = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
]


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def piece_color(piece):
    return piece[0] if piece else None


def piece_type(piece):
    return piece[1] if piece else None


class Game:
    def __init__(self):
        self.board = [row[:] for row in START_FEN]
        self.turn = 'w'  # 'w' or 'b'
        self.selected = None  # (r, c) or None
        self.legal_moves_from_selected = []  # list of (r,c)
        self.running = True
        self.human_color = 'w'
        self.ai_color = 'b'
        self.font = None
        self.status_font = None

    # --------------- Rendering ---------------
    def init_fonts(self):
        # Try fonts that contain chess unicode on Windows
        candidates = ['Segoe UI Symbol', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans Symbols2', None]
        for name in candidates:
            try:
                self.font = pygame.font.SysFont(name, int(SQ_SIZE * 0.75))
                if self.font is not None:
                    break
            except Exception:
                continue
        self.status_font = pygame.font.SysFont('consolas', 20)

    def draw(self, screen):
        # Draw board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                rect = pygame.Rect(c * SQ_SIZE, MARGIN_TOP + r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(screen, color, rect)

        # Highlight selected square
        if self.selected:
            sr, sc = self.selected
            rect = pygame.Rect(sc * SQ_SIZE, MARGIN_TOP + sr * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 70))
            screen.blit(s, rect.topleft)

        # Highlight legal moves
        for (mr, mc) in self.legal_moves_from_selected:
            cx = mc * SQ_SIZE + SQ_SIZE // 2
            cy = mr * SQ_SIZE + SQ_SIZE // 2
            target_piece = self.board[mr][mc]
            if target_piece is None:
                pygame.draw.circle(screen, MOVE_DOT, (cx, cy), 8)
            else:
                # draw ring for capture
                pygame.draw.circle(screen, CAPTURE_HI, (cx, cy), SQ_SIZE // 2 - 6, 4)

        # Draw pieces
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece:
                    char = UNICODE_PIECES[piece]
                    text = self.font.render(char, True, TEXT_COLOR)
                    tr = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, MARGIN_TOP + r * SQ_SIZE + SQ_SIZE // 2))
                    screen.blit(text, tr)

        # Draw status bar
        pygame.draw.rect(screen, (230, 230, 230), (0, 640, WIDTH, STATUS_BAR_H))
        status = f"Turn: {'White' if self.turn=='w' else 'Black'}"
        if self.turn == self.ai_color:
            status += " | AI thinking..."
        text = self.status_font.render(status, True, (30, 30, 30))
        screen.blit(text, (10, 646))

    # --------------- Move Generation ---------------
    def generate_all_moves(self, color):
        moves = []  # list of ((r,c), (nr,nc))
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and piece_color(p) == color:
                    for (nr, nc) in self.generate_moves_for_piece(r, c):
                        moves.append(((r, c), (nr, nc)))
        return moves

    def generate_moves_for_piece(self, r, c):
        p = self.board[r][c]
        if not p:
            return []
        color = piece_color(p)
        t = piece_type(p)
        if t == 'P':
            return self._pawn_moves(r, c, color)
        elif t == 'N':
            return self._knight_moves(r, c, color)
        elif t == 'B':
            return self._slide_moves(r, c, color, directions=[(-1,-1), (-1,1), (1,-1), (1,1)])
        elif t == 'R':
            return self._slide_moves(r, c, color, directions=[(-1,0), (1,0), (0,-1), (0,1)])
        elif t == 'Q':
            return self._slide_moves(r, c, color, directions=[(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)])
        elif t == 'K':
            return self._king_moves(r, c, color)
        return []

    def _pawn_moves(self, r, c, color):
        moves = []
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        one_step = (r + dir, c)
        if in_bounds(*one_step) and self.board[one_step[0]][one_step[1]] is None:
            moves.append(one_step)
            # double move from start
            two_step = (r + 2*dir, c)
            if r == start_row and in_bounds(*two_step) and self.board[two_step[0]][two_step[1]] is None:
                moves.append(two_step)
        # diagonal captures
        for dc in (-1, 1):
            nr, nc = r + dir, c + dc
            if in_bounds(nr, nc):
                target = self.board[nr][nc]
                if target and piece_color(target) != color:
                    moves.append((nr, nc))
        return moves

    def _knight_moves(self, r, c, color):
        moves = []
        for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target is None or piece_color(target) != color:
                moves.append((nr, nc))
        return moves

    def _slide_moves(self, r, c, color, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                target = self.board[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                else:
                    if piece_color(target) != color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, r, c, color):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc):
                    continue
                target = self.board[nr][nc]
                if target is None or piece_color(target) != color:
                    moves.append((nr, nc))
        # No castling in this simple version
        return moves

    # --------------- Applying moves ---------------
    def make_move(self, from_sq, to_sq):
        fr, fc = from_sq
        tr, tc = to_sq
        piece = self.board[fr][fc]
        target = self.board[tr][tc]

        # Move piece
        self.board[fr][fc] = None
        # Pawn promotion (auto-queen)
        if piece_type(piece) == 'P':
            if (piece_color(piece) == 'w' and tr == 0) or (piece_color(piece) == 'b' and tr == 7):
                piece = piece_color(piece) + 'Q'
        self.board[tr][tc] = piece

        # Switch turn
        self.turn = 'b' if self.turn == 'w' else 'w'
        self.selected = None
        self.legal_moves_from_selected = []

    # --------------- AI ---------------
    def ai_move(self):
        # Very simple: choose capture with highest target value; if none, random move
        moves = self.generate_all_moves(self.ai_color)
        if not moves:
            return  # stalemate-like
        best_moves = []
        best_score = -10**9
        for (fr, to) in moves:
            tr, tc = to
            target = self.board[tr][tc]
            score = 0
            if target:
                score = PIECE_VALUES[piece_type(target)]
            if score > best_score:
                best_score = score
                best_moves = [(fr, to)]
            elif score == best_score:
                best_moves.append((fr, to))
        move = random.choice(best_moves) if best_moves else random.choice(moves)
        self.make_move(*move)

    # --------------- Input handling ---------------
    def handle_click(self, pos):
        x, y = pos
        if y >= 640:
            return
        c = x // SQ_SIZE
        r = (y - MARGIN_TOP) // SQ_SIZE
        if not in_bounds(r, c):
            return

        if self.turn != self.human_color:
            return

        if self.selected is None:
            piece = self.board[r][c]
            if piece and piece_color(piece) == self.human_color:
                self.selected = (r, c)
                self.legal_moves_from_selected = self.generate_moves_for_piece(r, c)
        else:
            # If clicked on a legal destination -> move
            if (r, c) in self.legal_moves_from_selected:
                self.make_move(self.selected, (r, c))
            else:
                # Re-select if clicking on another own piece; otherwise cancel
                piece = self.board[r][c]
                if piece and piece_color(piece) == self.human_color:
                    self.selected = (r, c)
                    self.legal_moves_from_selected = self.generate_moves_for_piece(r, c)
                else:
                    self.selected = None
                    self.legal_moves_from_selected = []


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess with Simple AI (Pygame)')
    clock = pygame.time.Clock()

    game = Game()
    game.init_fonts()

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)

        # AI turn
        if game.turn == game.ai_color:
            # Simple pacing so UI can update
            pygame.time.delay(120)
            game.ai_move()

        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
