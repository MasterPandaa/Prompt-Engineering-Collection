# Snake (Pygame)

Classic Snake implemented with clean, class-based Python using Pygame.

## Requirements
- Python 3.9+
- Pygame (see `requirements.txt`)

Install dependencies in a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

## Controls
- Arrow Keys or WASD: Move
- Enter or R: Restart after Game Over
- Esc: Quit

## Technical Notes
- Resolution: 600x400
- Grid cell size: 20px
- Guard clause prevents reversing direction into the snake’s body within one tick.
- `Snake` class encapsulates movement, growth, and collision helpers.
- `Food` class respawns efficiently on any free cell, avoiding the snake body.
- Solid collision detection with walls and self.
