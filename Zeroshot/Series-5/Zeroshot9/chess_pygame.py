import sys
import math
import random
import pygame
from typing import List, Tuple, Optional, Dict

# ---------------------------
# Chess game with Pygame UI
# - No external images. Uses Unicode chess symbols; falls back to shapes if not available.
# - Implements basic chess rules, turn system, check detection, simple AI for Black.
# - No castling, no en passant, simple auto-promotion to Queen.
# ---------------------------

WHITE = 'w'
BLACK = 'b'

# Board is 8x8, coordinates as (row, col) with row 0 at top (Black side), row 7 at bottom (White side)

# Unicode symbols mapping
UNICODE_PIECES = {
    WHITE: {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'
    },
    BLACK: {
        'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'
    }
}

# Material values for simple evaluation (used by AI capture preference)
MATERIAL_VALUES = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'P': 1}

# Colors
LIGHT_SQUARE = (235, 236, 208)
DARK_SQUARE = (119, 149, 86)
HIGHLIGHT_SQUARE = (246, 246, 105)
MOVE_DOT = (40, 40, 40)
SELECTED_OUTLINE = (255, 215, 0)
CHECK_HIGHLIGHT = (255, 120, 120)
TEXT_COLOR = (20, 20, 20)
PANEL_BG = (245, 245, 250)

# UI sizes
TILE_SIZE = 80
BOARD_SIZE = TILE_SIZE * 8
PANEL_WIDTH = 240
WINDOW_SIZE = (BOARD_SIZE + PANEL_WIDTH, BOARD_SIZE)
FPS = 60

class Piece:
    def __init__(self, color: str, kind: str):
        self.color = color  # 'w' or 'b'
        self.kind = kind    # 'K','Q','R','B','N','P'

    def __repr__(self):
        return f"{self.color}{self.kind}"

class Board:
    def __init__(self):
        # board[r][c] -> Piece or None
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.to_move: str = WHITE
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.place_starting_position()

    def clone(self) -> 'Board':
        b = Board.__new__(Board)
        b.board = [[None if p is None else Piece(p.color, p.kind) for p in row] for row in self.board]
        b.to_move = self.to_move
        b.halfmove_clock = self.halfmove_clock
        b.fullmove_number = self.fullmove_number
        return b

    def place_starting_position(self):
        # Place pawns
        for c in range(8):
            self.board[6][c] = Piece(WHITE, 'P')
            self.board[1][c] = Piece(BLACK, 'P')
        # Place other pieces
        order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for c, k in enumerate(order):
            self.board[7][c] = Piece(WHITE, k)
            self.board[0][c] = Piece(BLACK, k)

    def inside(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def king_position(self, color: str) -> Tuple[int, int]:
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p.color == color and p.kind == 'K':
                    return (r, c)
        # Should not happen in normal game
        return (-1, -1)

    def is_square_attacked_by(self, r: int, c: int, attacker_color: str) -> bool:
        # Check if square (r,c) is attacked by any piece of attacker_color
        # We'll generate attack rays and piece-specific patterns
        # Knights
        knight_moves = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr, dc in knight_moves:
            rr, cc = r + dr, c + dc
            if self.inside(rr, cc):
                p = self.board[rr][cc]
                if p and p.color == attacker_color and p.kind == 'N':
                    return True
        # Pawns
        dir = -1 if attacker_color == WHITE else 1  # pawns attack forward relative to their color
        for dc in (-1, 1):
            rr, cc = r + dir, c + dc
            if self.inside(rr, cc):
                p = self.board[rr][cc]
                if p and p.color == attacker_color and p.kind == 'P':
                    return True
        # Kings (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if self.inside(rr, cc):
                    p = self.board[rr][cc]
                    if p and p.color == attacker_color and p.kind == 'K':
                        return True
        # Sliding pieces: bishops/queens on diagonals; rooks/queens on ranks/files
        # Diagonals for B/Q
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            rr, cc = r + dr, c + dc
            while self.inside(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p.color == attacker_color and (p.kind == 'B' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # Straights for R/Q
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            rr, cc = r + dr, c + dc
            while self.inside(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p.color == attacker_color and (p.kind == 'R' or p.kind == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        return False

    def is_in_check(self, color: str) -> bool:
        kr, kc = self.king_position(color)
        if kr == -1:
            return False
        opp = WHITE if color == BLACK else BLACK
        return self.is_square_attacked_by(kr, kc, opp)

    def generate_pseudo_legal_moves_from(self, r: int, c: int) -> List[Tuple[Tuple[int,int], Tuple[int,int]]]:
        p = self.board[r][c]
        if not p:
            return []
        color = p.color
        moves = []
        if p.kind == 'P':
            dir = -1 if color == WHITE else 1
            start_row = 6 if color == WHITE else 1
            # Forward one
            rr = r + dir
            if self.inside(rr, c) and self.board[rr][c] is None:
                moves.append(((r,c),(rr,c)))
                # Forward two from start
                rr2 = r + 2*dir
                if r == start_row and self.board[rr2][c] is None:
                    moves.append(((r,c),(rr2,c)))
            # Captures
            for dc in (-1, 1):
                cc = c + dc
                rr = r + dir
                if self.inside(rr, cc):
                    target = self.board[rr][cc]
                    if target and target.color != color:
                        moves.append(((r,c),(rr,cc)))
            # No en passant
        elif p.kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                rr, cc = r + dr, c + dc
                if not self.inside(rr, cc):
                    continue
                target = self.board[rr][cc]
                if target is None or target.color != color:
                    moves.append(((r,c),(rr,cc)))
        elif p.kind in ('B', 'R', 'Q'):
            directions = []
            if p.kind in ('B','Q'):
                directions += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'):
                directions += [(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in directions:
                rr, cc = r + dr, c + dc
                while self.inside(rr, cc):
                    target = self.board[rr][cc]
                    if target is None:
                        moves.append(((r,c),(rr,cc)))
                    else:
                        if target.color != color:
                            moves.append(((r,c),(rr,cc)))
                        break
                    rr += dr
                    cc += dc
        elif p.kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0:
                        continue
                    rr, cc = r + dr, c + dc
                    if not self.inside(rr, cc):
                        continue
                    target = self.board[rr][cc]
                    if target is None or target.color != color:
                        moves.append(((r,c),(rr,cc)))
            # No castling implemented
        return moves

    def generate_legal_moves(self, color: str) -> List[Tuple[Tuple[int,int], Tuple[int,int]]]:
        # Generate pseudo-legal then filter out those that leave king in check
        res = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p.color == color:
                    for move in self.generate_pseudo_legal_moves_from(r, c):
                        if self.is_legal_move(move, color):
                            res.append(move)
        return res

    def is_legal_move(self, move: Tuple[Tuple[int,int], Tuple[int,int]], color: str) -> bool:
        (r1,c1),(r2,c2) = move
        p = self.board[r1][c1]
        if not p or p.color != color:
            return False
        # Make move on cloned board and test check
        b2 = self.clone()
        b2._make_move_no_checks(move)
        return not b2.is_in_check(color)

    def _make_move_no_checks(self, move: Tuple[Tuple[int,int], Tuple[int,int]]):
        (r1,c1),(r2,c2) = move
        p = self.board[r1][c1]
        self.board[r1][c1] = None
        # Promotion auto to Queen if pawn reaches end
        if p.kind == 'P' and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = Piece(p.color, 'Q')
        else:
            self.board[r2][c2] = p

    def make_move(self, move: Tuple[Tuple[int,int], Tuple[int,int]]):
        (r1,c1),(r2,c2) = move
        moving = self.board[r1][c1]
        captured = self.board[r2][c2]
        self._make_move_no_checks(move)
        # Update clocks
        if moving.kind == 'P' or captured is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        if self.to_move == BLACK:
            self.fullmove_number += 1
        # Switch turn
        self.to_move = WHITE if self.to_move == BLACK else BLACK

# ---------------------------
# Simple AI: choose random legal move; prefer capturing highest material if available
# ---------------------------

def choose_ai_move(board: Board) -> Optional[Tuple[Tuple[int,int], Tuple[int,int]]]:
    moves = board.generate_legal_moves(BLACK)
    if not moves:
        return None
    # Prefer captures
    best_capture_value = -1
    best_captures = []
    for (r1,c1),(r2,c2) in moves:
        target = board.board[r2][c2]
        if target and target.color == WHITE:
            val = MATERIAL_VALUES.get(target.kind, 0)
            if val > best_capture_value:
                best_capture_value = val
                best_captures = [((r1,c1),(r2,c2))]
            elif val == best_capture_value:
                best_captures.append(((r1,c1),(r2,c2)))
    if best_captures:
        return random.choice(best_captures)
    return random.choice(moves)

# ---------------------------
# Pygame UI
# ---------------------------

class ChessUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Chess - Pygame (No external images)')
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.selected: Optional[Tuple[int,int]] = None
        self.legal_targets: List[Tuple[int,int]] = []
        self.font = self._load_best_font()
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.game_over_text: Optional[str] = None

    def _load_best_font(self) -> pygame.font.Font:
        # Try fonts that likely include chess glyphs
        candidates = [
            'Segoe UI Symbol',   # Windows
            'Noto Sans Symbols', # Linux/others
            'DejaVu Sans',       # Common fallback
            'Arial Unicode MS',  # Older Windows/Mac installs
        ]
        for name in candidates:
            try:
                f = pygame.font.SysFont(name, int(TILE_SIZE * 0.8))
                # quick glyph check
                if f.render('♔', True, (0,0,0)).get_width() > 0:
                    return f
            except Exception:
                continue
        # Fallback generic font
        return pygame.font.SysFont(None, int(TILE_SIZE * 0.8))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over_text:
                    self.handle_mouse_click(event.pos)

            self.draw()

            if not self.game_over_text and self.board.to_move == BLACK:
                # AI turn
                pygame.time.delay(200)
                move = choose_ai_move(self.board)
                if move is None:
                    # Checkmate or stalemate
                    if self.board.is_in_check(BLACK):
                        self.game_over_text = 'Checkmate! White wins.'
                    else:
                        self.game_over_text = 'Stalemate!'
                else:
                    self.board.make_move(move)
                    # After AI move, check if White is mated or stalemated
                    white_moves = self.board.generate_legal_moves(WHITE)
                    if not white_moves:
                        if self.board.is_in_check(WHITE):
                            self.game_over_text = 'Checkmate! Black wins.'
                        else:
                            self.game_over_text = 'Stalemate!'

        pygame.quit()
        sys.exit()

    def handle_mouse_click(self, pos: Tuple[int,int]):
        x, y = pos
        if x >= BOARD_SIZE:
            return
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if not self.board.inside(r,c):
            return
        if self.selected:
            # Try move to (r,c)
            (sr, sc) = self.selected
            move = ((sr, sc), (r, c))
            if any((r,c) == t for t in self.legal_targets):
                # Execute
                self.board.make_move(move)
                self.selected = None
                self.legal_targets = []
                # Check for end after White move
                black_moves = self.board.generate_legal_moves(BLACK)
                if not black_moves:
                    if self.board.is_in_check(BLACK):
                        self.game_over_text = 'Checkmate! White wins.'
                    else:
                        self.game_over_text = 'Stalemate!'
                return
            else:
                # Reselect if clicking own piece
                p = self.board.board[r][c]
                if p and p.color == self.board.to_move == WHITE and self.board.to_move == WHITE:
                    self.select_square(r, c)
                else:
                    # Deselect
                    self.selected = None
                    self.legal_targets = []
        else:
            # Select a piece if it's White to move and piece is white
            if self.board.to_move != WHITE:
                return
            p = self.board.board[r][c]
            if p and p.color == WHITE:
                self.select_square(r, c)

    def select_square(self, r: int, c: int):
        self.selected = (r, c)
        self.legal_targets = []
        for (src, dst) in self.board.generate_legal_moves(WHITE):
            if src == (r, c):
                self.legal_targets.append(dst)

    def draw(self):
        self.screen.fill(PANEL_BG)
        # Draw board squares
        king_in_check = None
        if self.board.is_in_check(self.board.to_move):
            king_in_check = self.board.king_position(self.board.to_move)
        for r in range(8):
            for c in range(8):
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                is_light = (r + c) % 2 == 0
                color = LIGHT_SQUARE if is_light else DARK_SQUARE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                if king_in_check == (r, c):
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((*CHECK_HIGHLIGHT, 80))
                    self.screen.blit(s, (x, y))
        # Highlight selected
        if self.selected:
            (sr, sc) = self.selected
            sx, sy = sc * TILE_SIZE, sr * TILE_SIZE
            pygame.draw.rect(self.screen, SELECTED_OUTLINE, (sx, sy, TILE_SIZE, TILE_SIZE), 4)
            # Draw legal target dots or outlines
            for (tr, tc) in self.legal_targets:
                tx, ty = tc * TILE_SIZE, tr * TILE_SIZE
                target_piece = self.board.board[tr][tc]
                if target_piece is None:
                    pygame.draw.circle(self.screen, MOVE_DOT, (tx + TILE_SIZE//2, ty + TILE_SIZE//2), 8)
                else:
                    pygame.draw.rect(self.screen, (230, 90, 90), (tx+6, ty+6, TILE_SIZE-12, TILE_SIZE-12), 3)
        # Draw pieces
        for r in range(8):
            for c in range(8):
                p = self.board.board[r][c]
                if p:
                    self.draw_piece(p, r, c)
        # Right panel info
        self.draw_panel()
        pygame.display.flip()

    def draw_panel(self):
        # Panel background already filled; draw text info
        x0 = BOARD_SIZE + 10
        y = 10
        title = self.small_font.render('Pygame Chess', True, TEXT_COLOR)
        self.screen.blit(title, (x0, y))
        y += 28
        turn_text = f"Turn: {'White' if self.board.to_move == WHITE else 'Black'}"
        turn_surf = self.small_font.render(turn_text, True, TEXT_COLOR)
        self.screen.blit(turn_surf, (x0, y))
        y += 24
        if self.board.is_in_check(self.board.to_move) and not self.game_over_text:
            chk = self.small_font.render('Check!', True, (200, 40, 40))
            self.screen.blit(chk, (x0, y))
            y += 24
        y += 10
        tips = [
            'How to play:',
            '- You are White.',
            '- Click a piece, then a target square.',
            '- AI (Black) moves automatically.',
            '',
            'Rules:',
            '- No castling, no en passant.',
            '- Promotion -> Queen automatically.',
        ]
        for t in tips:
            surf = self.small_font.render(t, True, TEXT_COLOR)
            self.screen.blit(surf, (x0, y))
            y += 20
        if self.game_over_text:
            y += 10
            big = pygame.font.SysFont('Arial', 22, bold=True)
            msg = big.render(self.game_over_text, True, (20, 20, 20))
            self.screen.blit(msg, (x0, y))

    def draw_piece(self, piece: Piece, r: int, c: int):
        x = c * TILE_SIZE
        y = r * TILE_SIZE
        sym = UNICODE_PIECES.get(piece.color, {}).get(piece.kind)
        # Try unicode render
        try:
            text = self.font.render(sym if sym else '', True, (0,0,0) if piece.color == BLACK else (255,255,255))
            # Shadow for contrast
            shadow = self.font.render(sym if sym else '', True, (0,0,0))
            tx = x + TILE_SIZE//2 - text.get_width()//2
            ty = y + TILE_SIZE//2 - text.get_height()//2
            # draw slight shadow offset
            self.screen.blit(shadow, (tx+1, ty+1))
            self.screen.blit(text, (tx, ty))
        except Exception:
            # Fallback: draw simple geometry
            radius = TILE_SIZE//2 - 8
            color = (30,30,30) if piece.color == BLACK else (240,240,240)
            pygame.draw.circle(self.screen, color, (x + TILE_SIZE//2, y + TILE_SIZE//2), radius)
            # mark kind with small letter
            lbl = self.small_font.render(piece.kind, True, (0,0,0) if piece.color == WHITE else (255,255,255))
            self.screen.blit(lbl, (x + TILE_SIZE//2 - lbl.get_width()//2, y + TILE_SIZE//2 - lbl.get_height()//2))


def main():
    ui = ChessUI()
    ui.run()

if __name__ == '__main__':
    main()
