# Mini Chess (Python + Pygame)

A small, playable chess engine with separated core logic (Board, Rules) and a basic AI that uses a material evaluation. Rendering uses Unicode chess characters via `pygame.font.SysFont`, so you don't need external image assets.

## Features

- Board representation and rules separated into `chess_engine/board.py` and `chess_engine/rules.py`.
- Basic AI in `chess_engine/ai.py` that prefers free captures and uses simple material evaluation (P=1, N=3, B=3, R=5, Q=9).
- Click to select, click to move.
- Highlights selected square and shows possible destinations.
- Auto-promotion to Queen.
- No castling or en passant (to keep the engine compact and readable).

## Requirements

- Python 3.9+
- pygame (see `requirements.txt`)

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the game:

```bash
python main.py
```

You play as White, the AI plays as Black.

## Notes

- Legal move generation is simplified and does not enforce check rules or special moves. This is intended to keep the code compact and educational.
- On Windows, the font fallback attempts to use `Segoe UI Symbol`. If pieces don't appear correctly, ensure a font with chess Unicode glyphs is available (e.g., DejaVu Sans) or adjust the font name in `main.py`.
