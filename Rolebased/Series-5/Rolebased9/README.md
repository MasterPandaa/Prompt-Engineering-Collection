# Mini Chess (Python + Pygame)

Playable mini chess engine with:
- Clean separation of `Board` state and `Rules` for move generation.
- Unicode chess piece rendering with `pygame.font.SysFont` (no image assets).
- Simple AI using material evaluation that prefers profitable captures.
- Click-to-select, click-to-move with highlighting; check/checkmate/stalemate cues.

## Requirements
- Python 3.9+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python mini_chess.py
```

By default you play White vs AI Black. To play Black:

```bash
python mini_chess.py black
```

## Notes
- Simplified rules: en passant and castling are omitted to keep the engine compact.
- Pawn promotes automatically to Queen.
- Font fallback: tries `Segoe UI Symbol` (Windows), `Arial Unicode MS`, `DejaVu Sans`, then default system font.
