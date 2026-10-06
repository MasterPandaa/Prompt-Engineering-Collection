# Chess (Pygame)

A simple standard chess game built with Python and Pygame.

Features:
- 8x8 board with alternating colors.
- Pieces rendered using Unicode chess glyphs (e.g., ♔, ♕) if available, or geometric-shape fallback if the font on your system does not support those glyphs.
- Legal move generation for all standard pieces (no castling or en passant in this version). Pawn promotion to Queen is supported.
- Turn-based play: White (human) vs. Black (AI).
- Basic check detection and legal-move filtering to prevent self-check.
- Simple AI for Black: picks a move using a very light material evaluation heuristic, falling back to random if equal.

Requirements:
- Python 3.9+
- Pygame 2.5+

Install dependencies:

```
pip install -r requirements.txt
```

Run the game:

```
python chess_game.py
```

Controls:
- Left click a white piece to select.
- Left click a highlighted square to move.

Notes:
- This implementation focuses on core rules and playability: it does not include castling or en passant.
- Pawn promotion is automatic to a queen.
- If your system font does not support chess Unicode glyphs, the game will automatically render simple geometric shapes for pieces.
