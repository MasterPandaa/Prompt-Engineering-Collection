import sys
import pygame
from typing import Optional, Tuple, List

from chess_engine.board import Board, UNICODE_PIECES
from chess_engine.rules import generate_moves
from chess_engine.ai import pick_move

WIDTH, HEIGHT = 640, 640
SQUARE = WIDTH // 8
LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (246, 246, 105)
MOVE_DOT = (80, 80, 80)
TEXT_COLOR = (20, 20, 20)


def square_at(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = pos
    return y // SQUARE, x // SQUARE


def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font, selected: Optional[Tuple[int, int]], legal_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]]):
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            rect = pygame.Rect(c * SQUARE, r * SQUARE, SQUARE, SQUARE)
            pygame.draw.rect(screen, color, rect)

    # Highlight selected square
    if selected is not None:
        sr, sc = selected
        rect = pygame.Rect(sc * SQUARE, sr * SQUARE, SQUARE, SQUARE)
        s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
        s.fill((*HIGHLIGHT, 90))
        screen.blit(s, rect.topleft)

    # Draw pieces
    for r in range(8):
        for c in range(8):
            p = board.at(r, c)
            if p:
                ch = UNICODE_PIECES[p]
                text = font.render(ch, True, TEXT_COLOR)
                tw, th = text.get_size()
                x = c * SQUARE + (SQUARE - tw) // 2
                y = r * SQUARE + (SQUARE - th) // 2 - 4
                screen.blit(text, (x, y))

    # Show legal moves for selected
    if selected is not None:
        dests = [dst for src, dst in legal_moves if src == selected]
        for (rr, cc) in dests:
            cx = cc * SQUARE + SQUARE // 2
            cy = rr * SQUARE + SQUARE // 2
            pygame.draw.circle(screen, MOVE_DOT, (cx, cy), 8)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Chess - You (White) vs AI (Black)")

    # Try a font that supports chess symbols; fall back to default
    try_fonts = ["Segoe UI Symbol", "DejaVu Sans", None]
    font_obj = None
    for fname in try_fonts:
        try:
            font_obj = pygame.font.SysFont(fname, 56)
            test = font_obj.render("\u2654", True, (0, 0, 0))
            if test.get_width() > 0:
                break
        except Exception:
            continue
    if font_obj is None:
        font_obj = pygame.font.SysFont(None, 56)

    clock = pygame.time.Clock()

    board = Board.starting_position()
    selected: Optional[Tuple[int, int]] = None

    legal_moves = generate_moves(board)

    running = True
    human_color = "w"
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                pos = pygame.mouse.get_pos()
                r, c = square_at(pos)
                if selected is None:
                    piece = board.at(r, c)
                    if piece and piece[0] == board.side_to_move == human_color:
                        selected = (r, c)
                else:
                    # Try to move
                    move_candidates = [m for m in legal_moves if m[0] == selected and m[1] == (r, c)]
                    if move_candidates:
                        board.apply_move(move_candidates[0])
                        selected = None
                        legal_moves = generate_moves(board)
                        # After human move, trigger AI if it's AI's turn
                        if board.side_to_move != human_color:
                            ai_m = pick_move(board)
                            if ai_m is not None:
                                board.apply_move(ai_m)
                                legal_moves = generate_moves(board)
                    else:
                        # Reselect if clicked own piece
                        piece = board.at(r, c)
                        if piece and piece[0] == human_color and piece[0] == board.side_to_move:
                            selected = (r, c)
                        else:
                            selected = None

        # Update possible moves and game over state
        if not game_over:
            ms = generate_moves(board)
            if not ms:
                game_over = True
                side = "White" if board.side_to_move == "w" else "Black"
                pygame.display.set_caption(f"Mini Chess - {side} has no moves. Game Over.")
            else:
                legal_moves = ms

        draw_board(screen, board, font_obj, selected, legal_moves)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
