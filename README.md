# Tetris OOP with Pygame

This is a clean, robust Tetris clone implemented with Python and Pygame using an object-oriented architecture.

Features:
- Piece and Board classes to encapsulate game logic
- Ghost piece rendering to assist placement
- Efficient line clearing and scoring
- Leveling with gravity speed-up
- Hold piece and next queue

Controls:
- Left/Right: Move
- Up/Z: Rotate CW/CCW
- Down: Soft Drop
- Space: Hard Drop
- C: Hold
- Esc: Quit

Requirements:
- Python 3.9+
- Pygame (see requirements.txt)

Install and Run (Windows PowerShell):
1. python -m venv .venv
2. .venv\\Scripts\\Activate.ps1
3. pip install -r requirements.txt
4. python main.py

Notes:
- If your display scaling causes the window to be too small/large, adjust CELL_SIZE in main.py.
- The code uses a simple wall-kick system that should feel natural for most rotations.
