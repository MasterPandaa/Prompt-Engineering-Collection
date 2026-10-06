# Snake (Pygame)

A clean, efficient, and maintainable implementation of the classic Snake game using Pygame.

## Features
- 600x400 window with subtle grid
- Class-based design: `Snake` and `Food`
- Responsive arrow/WASD controls with guard against reversing
- Accurate growth logic and efficient random food placement
- Robust collision detection (walls and self)
- Simple score display and restart option

## Requirements
- Python 3.8+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python snake_game.py
```

## Controls
- Arrow keys or WASD to move
- R to restart after game over
- ESC to quit

## Code Structure
- `snake_game.py` contains:
  - `Snake` class: movement, growth, collision checks, and rendering
  - `Food` class: respawn on free grid cells and rendering
  - Main loop: input handling, update, render phases

## Notes
- Grid size is derived from constants: `WIDTH=600`, `HEIGHT=400`, `CELL_SIZE=20`.
- Game speed can be adjusted via `FPS`.
