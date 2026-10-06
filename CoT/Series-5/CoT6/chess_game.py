import sys
import random
import pygame
from typing import List, Tuple, Optional

# -----------------------------
# Config
# -----------------------------
TILE_SIZE = 80
BOARD_SIZE = 8
WIDTH = TILE_SIZE * BOARD_SIZE
HEIGHT = TILE_SIZE * BOARD_SIZE
FPS = 60

# Colors
LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
HIGHLIGHT_SQ = (246, 246, 105)
MOVE_SQ = (186, 202, 68)
SELECT_SQ = (255, 255, 140)
TEXT_COLOR = (20, 20, 20)

# Piece values for AI capture priority
PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 100,
}

# Unicode mapping
UNICODE_PIECES = {
    'wK': '\u2654',
    'wQ': '\u2655',
    'wR': '\u2656',
    'wB': '\u2657',
    'wN': '\u2658',
    'wP': '\u2659',
    'bK': '\u265A',
    'bQ': '\u265B',
    'bR': '\u265C',
    'bB': '\u265D',
    'bN': '\u265E',
    'bP': '\u265F',
}

Move = Tuple[int, int, int, int, Optional[str]]  # (from_r, from_c, to_r, to_c, promo)


class Board:
    def __init__(self):
        # 8x8 board, row 0 at top. White at bottom (rows 6,7) moving up (-1)
        self.board: List[List[str]] = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.turn: str = 'w'  # 'w' or 'b'

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get_color(self, piece: str) -> Optional[str]:
        if piece == '--':
            return None
        return piece[0]

    def piece_type(self, piece: str) -> Optional[str]:
        if piece == '--':
            return None
        return piece[1]

    def copy(self) -> 'Board':
        b = Board()
        b.board = [row[:] for row in self.board]
        b.turn = self.turn
        return b

    def make_move(self, move: Move) -> None:
        fr, fc, tr, tc, promo = move
        moving = self.board[fr][fc]
        self.board[fr][fc] = '--'
        # Promotion
        if promo is not None:
            self.board[tr][tc] = self.get_color(moving) + promo
        else:
            self.board[tr][tc] = moving
        self.turn = 'b' if self.turn == 'w' else 'w'

    def generate_all_moves(self, color: str) -> List[Move]:
        moves: List[Move] = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if self.get_color(piece) == color:
                    moves.extend(self.generate_piece_moves(r, c))
        return moves

    def generate_piece_moves(self, r: int, c: int) -> List[Move]:
        piece = self.board[r][c]
        color = self.get_color(piece)
        if color is None:
            return []
        p = self.piece_type(piece)
        if p == 'P':
            return self._pawn_moves(r, c, color)
        elif p == 'N':
            return self._knight_moves(r, c, color)
        elif p == 'B':
            return self._sliding_moves(r, c, color, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif p == 'R':
            return self._sliding_moves(r, c, color, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif p == 'Q':
            return self._sliding_moves(r, c, color, directions=[
                (-1, -1), (-1, 1), (1, -1), (1, 1),
                (-1, 0), (1, 0), (0, -1), (0, 1)
            ])
        elif p == 'K':
            return self._king_moves(r, c, color)
        return []

    def _pawn_moves(self, r: int, c: int, color: str) -> List[Move]:
        moves: List[Move] = []
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        promo_row = 0 if color == 'w' else 7

        # Forward one
        fr = r + dir
        if self.in_bounds(fr, c) and self.board[fr][c] == '--':
            # promotion check
            if fr == promo_row:
                moves.append((r, c, fr, c, 'Q'))
            else:
                moves.append((r, c, fr, c, None))
            # Forward two from start
            if r == start_row:
                fr2 = r + 2 * dir
                if self.in_bounds(fr2, c) and self.board[fr2][c] == '--':
                    moves.append((r, c, fr2, c, None))
        # Captures
        for dc in (-1, 1):
            fc = c + dc
            fr = r + dir
            if self.in_bounds(fr, fc):
                target = self.board[fr][fc]
                if target != '--' and self.get_color(target) != color:
                    if fr == promo_row:
                        moves.append((r, c, fr, fc, 'Q'))
                    else:
                        moves.append((r, c, fr, fc, None))
        # Note: en passant not implemented
        return moves

    def _knight_moves(self, r: int, c: int, color: str) -> List[Move]:
        moves: List[Move] = []
        deltas = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target == '--' or self.get_color(target) != color:
                moves.append((r, c, nr, nc, None))
        return moves

    def _sliding_moves(self, r: int, c: int, color: str, directions: List[Tuple[int, int]]) -> List[Move]:
        moves: List[Move] = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                target = self.board[nr][nc]
                if target == '--':
                    moves.append((r, c, nr, nc, None))
                else:
                    if self.get_color(target) != color:
                        moves.append((r, c, nr, nc, None))
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, r: int, c: int, color: str) -> List[Move]:
        moves: List[Move] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                target = self.board[nr][nc]
                if target == '--' or self.get_color(target) != color:
                    moves.append((r, c, nr, nc, None))
        # Note: castling not implemented
        return moves


class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pygame Chess - Human vs Simple AI')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # Choose a font that likely supports Unicode chess symbols
        # Fallback to default if not available
        try:
            self.font = pygame.font.SysFont('Segoe UI Symbol', 56)
        except Exception:
            self.font = pygame.font.SysFont(None, 56)
        self.small_font = pygame.font.SysFont(None, 24)

        self.board = Board()
        self.selected: Optional[Tuple[int, int]] = None
        self.legal_moves_for_selected: List[Move] = []
        self.running = True
        self.human_color = 'w'  # human plays white

    def pos_to_square(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        return r, c

    def square_to_pos(self, r: int, c: int) -> Tuple[int, int]:
        return c * TILE_SIZE, r * TILE_SIZE

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                pygame.draw.rect(self.screen, color, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Highlight selection
        if self.selected is not None:
            sr, sc = self.selected
            pygame.draw.rect(self.screen, SELECT_SQ, (sc * TILE_SIZE, sr * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Highlight moves for selected
        for move in self.legal_moves_for_selected:
            _, _, tr, tc, _ = move
            rect = pygame.Rect(tc * TILE_SIZE, tr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            # Use semi-transparent overlay via a surface
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((MOVE_SQ[0], MOVE_SQ[1], MOVE_SQ[2], 120))
            self.screen.blit(overlay, rect.topleft)

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board.board[r][c]
                if piece == '--':
                    continue
                text = UNICODE_PIECES.get(piece, piece[1])
                # Render with dark text; add light outline on dark squares for readability
                label = self.font.render(text, True, TEXT_COLOR)
                rect = label.get_rect(center=(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2))
                self.screen.blit(label, rect)

    def draw_status(self, info: str = ""):
        # Draw simple status text at top-left
        msg = f"Turn: {'White' if self.board.turn == 'w' else 'Black'}"
        if info:
            msg += f" | {info}"
        label = self.small_font.render(msg, True, (10, 10, 10))
        self.screen.blit(label, (8, 8))

    def handle_click(self, pos: Tuple[int, int]):
        r, c = self.pos_to_square(pos)
        if not self.board.in_bounds(r, c):
            return
        current_turn = self.board.turn

        # If it's human's turn, allow selecting/moving
        if current_turn == self.human_color:
            if self.selected is None:
                piece = self.board.board[r][c]
                if self.board.get_color(piece) == current_turn:
                    self.selected = (r, c)
                    self.legal_moves_for_selected = [m for m in self.board.generate_piece_moves(r, c)]
                else:
                    # clicked empty or opponent piece; ignore
                    pass
            else:
                # Try to move if in legal moves for selected
                possible = None
                for m in self.legal_moves_for_selected:
                    fr, fc, tr, tc, promo = m
                    if tr == r and tc == c:
                        possible = m
                        break
                if possible is not None:
                    self.board.make_move(possible)
                    self.selected = None
                    self.legal_moves_for_selected = []
                    # After human moves, AI will play automatically in next update cycle
                else:
                    # If clicking own piece, re-select
                    piece = self.board.board[r][c]
                    if self.board.get_color(piece) == current_turn:
                        self.selected = (r, c)
                        self.legal_moves_for_selected = [m for m in self.board.generate_piece_moves(r, c)]
                    else:
                        # Clicked elsewhere; clear selection
                        self.selected = None
                        self.legal_moves_for_selected = []
        else:
            # Not human's turn, ignore clicks
            pass

    def ai_choose_move(self) -> Optional[Move]:
        # Simple AI for black: choose highest-value capture, else random move
        color = self.board.turn
        moves = self.board.generate_all_moves(color)
        if not moves:
            return None
        best_moves: List[Move] = []
        best_score = -999
        for m in moves:
            fr, fc, tr, tc, promo = m
            target = self.board.board[tr][tc]
            if target != '--' and self.board.get_color(target) != color:
                score = PIECE_VALUES.get(self.board.piece_type(target) or 'P', 0)
                if score > best_score:
                    best_score = score
                    best_moves = [m]
                elif score == best_score:
                    best_moves.append(m)
        if best_moves:
            return random.choice(best_moves)
        # No captures, pick random move
        return random.choice(moves)

    def check_game_end(self) -> Optional[str]:
        # Very simple: if side to move has no moves => game over (not distinguishing checkmate/stalemate)
        moves = self.board.generate_all_moves(self.board.turn)
        if not moves:
            return f"No moves for {'White' if self.board.turn == 'w' else 'Black'}. Game Over."
        return None

    def run(self):
        info_text = ""
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            # AI move if it's AI's turn
            if self.board.turn != self.human_color:
                ai_move = self.ai_choose_move()
                if ai_move is None:
                    info_text = self.check_game_end() or ""
                    self.running = False
                else:
                    self.board.make_move(ai_move)

            # Check end of game (very naive) only when turn switches to someone with no moves
            end = self.check_game_end()
            if end is not None:
                info_text = end
                # Don't break immediately so message can render one frame
                # But stop after showing
                self.running = False

            # Render
            self.draw_board()
            self.draw_pieces()
            self.draw_status(info_text)
            pygame.display.flip()

        # Show final frame for a short moment
        self.draw_board()
        self.draw_pieces()
        self.draw_status("Game Ended. Close window.")
        pygame.display.flip()
        # Wait until window closed
        ending = True
        while ending:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ending = False
            self.clock.tick(30)
        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    game = ChessGame()
    game.run()
