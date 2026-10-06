# Python Chess (Pygame, No Image Assets)

A simple chess game built with Python and Pygame that:

- Draws an 8x8 board with alternating colors.
- Renders pieces using Unicode chess characters (no external images).
- Implements basic movement rules for Pawn, Rook, Knight, Bishop, Queen, King.
- Enforces turn order (White -> Black).
- Detects check (skak) and prevents illegal moves that leave your king in check.
- AI opponent (Black) plays a random legal move.
- Mouse interaction: click a piece, then click a destination square.

Note:
- Castling, en passant are not implemented.
- Promotion is auto-promoted to Queen.

## Requirements

- Python 3.8+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python chess_game.py
```

## Controls

- Left-click to select a White piece.
- Left-click a highlighted square to move.
- Press `R` to restart.
- Press `ESC` or close window to quit.

## Fonts

The game uses Unicode pieces: ♔ ♕ ♖ ♗ ♘ ♙ and ♚ ♛ ♜ ♝ ♞ ♟.
Most systems support them in default fonts. If not available, the game will fallback to letter notation.
