# Tetris (Python + Pygame)

Tetris clone with clean OOP architecture, ghost piece, efficient line clearing, next queue, and hold support.

## Features
- Object-Oriented design: `Piece`, `Board`, `Game` in `main.py`
- Ghost piece (transparent preview of hard drop landing)
- Efficient line clear (no per-cell shifting; rebuilds grid for performance)
- 7-bag randomizer for fair piece distribution
- Hold piece (press `C`)
- Scoring, level, and lines tracked
- Smooth gravity and basic key repeat for left/right move
- Next queue preview and side panel UI

## Requirements
- Python 3.9+
- Pygame (see `requirements.txt`)

## Installation
```
pip install -r requirements.txt
```

## Run
```
python main.py
```

## Controls
- Left / Right: Move piece
- Down: Soft drop
- Up or X: Rotate clockwise
- Z: Rotate counter-clockwise
- Space: Hard drop
- C: Hold piece
- Esc: Quit

## Notes
- Level increases every 10 cleared lines; gravity speeds up accordingly.
- Line clear scoring: Single 100, Double 300, Triple 500, Tetris 800 (multiplied by level).
- Hard drop: +2 points per cell; Soft drop: +1 per cell.

Enjoy!
