# Mini Chess (Pygame + Simple AI)

A minimal, playable chess engine written in Python using Pygame. It renders pieces using Unicode characters (no image assets) and includes a very simple AI opponent based on material evaluation that prefers taking free pieces.

## Features

- Separate engine core: `Board` (state) and `Rules` (move generation)
- Unicode chess piece rendering via `pygame.font.SysFont`
- Click to select, click to move; selected square and move hints highlighted
- Simple AI (Black): material evaluation + greedy captures
- Basic rules: legal piece moves, double pawn push, automatic promotion to Queen. No castling, en passant, or check/checkmate validation.

## Requirements

- Python 3.9+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python mini_chess.py
```

- You play as White. Click a White piece to see available moves (green hints), then click a destination square.
- Black is controlled by the AI and moves automatically.

## Notes

- The engine does not enforce check/checkmate or stalemate. It is intended as a compact, educational demo.
- Promotion is automatic to a Queen upon reaching the last rank.
