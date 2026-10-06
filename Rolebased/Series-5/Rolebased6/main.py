import sys
import pygame
from typing import List, Tuple, Optional

from engine.board import Board, Move
from engine.rules import generate_legal_moves
from engine.ai import SimpleAI

# UI constants
TILE_SIZE = 80
BOARD_SIZE = TILE_SIZE * 8
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
TARGET = (106, 135, 89)
TEXT_COLOR = (20, 20, 20)

# Unicode symbols mapping
PIECE_UNI = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
    'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
}

FONT_CANDIDATES = [
    "Segoe UI Symbol",  # Windows
    "DejaVu Sans",      # Linux
    "Arial Unicode MS",
    "Noto Sans Symbols",
]


def pick_font(size: int) -> pygame.font.Font:
    for name in FONT_CANDIDATES:
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.SysFont(None, size)


def draw_board(screen: pygame.Surface, board: Board, selected: Optional[Tuple[int, int]], legal_from_selected: List[Move], font: pygame.font.Font):
    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, rect)

    # Highlights
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * TILE_SIZE, sr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 6)
        # draw targets
        for mv in legal_from_selected:
            (_, _), (tr, tc), _ = mv
            rect = pygame.Rect(tc * TILE_SIZE, tr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, TARGET, rect, 4)

    # Pieces
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p == '.':
                continue
            ch = PIECE_UNI[p]
            text = font.render(ch, True, TEXT_COLOR)
            tw, th = text.get_size()
            x = c * TILE_SIZE + (TILE_SIZE - tw) // 2
            y = r * TILE_SIZE + (TILE_SIZE - th) // 2
            screen.blit(text, (x, y))


def square_from_mouse(pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    x, y = pos
    c = x // TILE_SIZE
    r = y // TILE_SIZE
    if 0 <= r < 8 and 0 <= c < 8:
        return (r, c)
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption("Mini Chess - Human (White) vs AI (Black)")
    clock = pygame.time.Clock()

    font = pick_font(int(TILE_SIZE * 0.8))

    board = Board.starting()
    human_color = 'w'
    ai = SimpleAI('b')

    selected: Optional[Tuple[int, int]] = None
    legal_moves_cache: List[Move] = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if board.side_to_move == human_color:
                    sq = square_from_mouse(event.pos)
                    if sq is None:
                        continue
                    r, c = sq
                    p = board.grid[r][c]
                    if selected is None:
                        # select if it's your piece
                        if p != '.' and (p.isupper() if human_color == 'w' else p.islower()):
                            selected = sq
                            # cache legal moves from this square
                            all_legal = generate_legal_moves(board, human_color)
                            legal_moves_cache = [mv for mv in all_legal if mv[0] == selected]
                        else:
                            selected = None
                            legal_moves_cache = []
                    else:
                        # attempt move
                        mv = None
                        for cand in legal_moves_cache:
                            if cand[1] == sq:
                                mv = cand
                                break
                        if mv is None:
                            # reselect
                            if p != '.' and (p.isupper() if human_color == 'w' else p.islower()):
                                selected = sq
                                all_legal = generate_legal_moves(board, human_color)
                                legal_moves_cache = [m for m in all_legal if m[0] == selected]
                            else:
                                selected = None
                                legal_moves_cache = []
                        else:
                            # handle promotion UI minimally: auto promote to Queen
                            (fr, fc), (tr, tc), promo = mv
                            piece = board.grid[fr][fc]
                            if (piece == 'P' and tr == 0) or (piece == 'p' and tr == 7):
                                mv = ((fr, fc), (tr, tc), 'Q')
                            board = board.apply_move(mv)
                            selected = None
                            legal_moves_cache = []
        # AI move if it's AI's turn
        if running and board.side_to_move != human_color:
            pygame.event.pump()
            mv = ai.choose_move(board)
            if mv is not None:
                # ensure promotion auto to queen for AI
                (fr, fc), (tr, tc), promo = mv
                piece = board.grid[fr][fc]
                if (piece == 'P' and tr == 0) or (piece == 'p' and tr == 7):
                    mv = ((fr, fc), (tr, tc), 'Q')
                board = board.apply_move(mv)
            # simple delay for UX
            pygame.time.delay(150)

        screen.fill((0, 0, 0))
        draw_board(screen, board, selected, legal_moves_cache, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        pygame.quit()
        raise
