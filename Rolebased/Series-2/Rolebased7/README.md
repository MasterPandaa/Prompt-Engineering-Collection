# Snake (Pygame)

Classic Snake implemented with clean, maintainable Python using Pygame.

## Features
- 600x400 window, grid-based movement (20px cells)
- `Snake` and `Food` classes to keep game loop clean
- Responsive arrow key controls with reverse-direction guard
- Accurate growth mechanics and efficient random food placement
- Solid collision detection (walls and self)
- Score display, game over screen, quick restart

## Requirements
- Python 3.8+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run
On Windows (PowerShell or CMD):

```bash
python snake.py
```

Controls:
- Arrow keys to move
- Space/Enter/R to restart on game over
- Esc to quit on game over

## Notes
- Movement is driven by a timer event for consistent speed independent of framerate.
- The reverse guard is applied to both the current and the pending direction to avoid mid-tick reversals.
