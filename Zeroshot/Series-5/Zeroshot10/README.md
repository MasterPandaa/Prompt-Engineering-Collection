# Pygame Chess (Human vs Random AI)

A simple, fully self-contained chess game built with Python and Pygame.

- 8x8 board with alternating colors.
- No external images: pieces are rendered using Unicode characters (with automatic letter fallback).
- Implements legal moves for all standard pieces (Pawn, Knight, Bishop, Rook, Queen, King).
- Basic check detection and legal move filtering (you cannot leave your king in check).
- Simple AI for Black that prefers captures; otherwise, plays a random legal move.
- Click-to-move interaction for the human player (White).
- Basic endgame handling: checkmate and stalemate detection.

## Requirements

- Python 3.8+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

A game window will open.

## How to Play

- You play as White. Click a white piece to select it.
- Legal target squares will be highlighted. Click a target square to move.
- After your move, the AI (Black) will respond automatically.
- The current status (turn information, check, or game end) is shown in the top-left corner.

## Notes & Simplifications

- No external image files are used. The game attempts to use system fonts that include chess glyphs (e.g., "Segoe UI Symbol", "DejaVu Sans"). If unavailable, the game falls back to simple letter markers (K, Q, R, B, N, P).
- The following chess rules are intentionally omitted for simplicity:
  - Castling
  - En passant
  - Fifty-move rule and threefold repetition
  - Draw by insufficient material
- Pawn promotion automatically promotes to a Queen.

## Controls

- Left-click: Select/move a piece.
- Close the window to exit the game.

## Troubleshooting

- If Unicode chess symbols do not display correctly, the game will automatically use letters for the pieces.
- Ensure Pygame is installed and working with your Python environment.
