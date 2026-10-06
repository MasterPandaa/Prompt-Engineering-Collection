# Pygame Chess (Text-Rendered Pieces)

This is a simple chess game built with Pygame that renders pieces as text (letters). It includes:

- Board representation using characters: uppercase = white, lowercase = black, '.' = empty
- Legal move generation for all piece types (K, Q, R, B, N, P)
- Pawn rules: single/double moves, diagonal captures, promotion to Queen
- No castling, no en passant, and no check/checkmate detection (basic rules only)
- Greedy AI (depth 1): evaluates material and picks the move that minimizes white's material advantage (AI plays black)
- Click to select and move white pieces. Press `R` to reset the game.

## Requirements

- Python 3.9+
- Pygame (see `requirements.txt`)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From the project directory `Chess/Few-shot/Iterasi3/`:

```bash
python main.py
```

Controls:

- Left-click to select a white piece and then left-click a highlighted square to move.
- Press `R` to reset the game.

## Notes

- This version focuses on core move legality and a simple AI. It does not include advanced chess rules (castling, en passant) or check/checkmate validation.
- Pieces are drawn with `pygame.font` as text symbols based on the piece letter.
