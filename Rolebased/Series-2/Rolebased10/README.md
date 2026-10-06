# Snake (Pygame)

A clean, efficient, and maintainable implementation of the classic Snake game using Pygame.

## Features
- Class-based architecture: `Snake` and `Food` keep the main loop clean.
- Responsive controls with guard against instant reverse.
- Accurate growth mechanics and efficient random food placement.
- Solid collision detection (walls and self) with O(1) self-collision checks during movement.
- Simple, modern visuals and grid.

## Requirements
- Python 3.8+
- Windows, macOS, or Linux with a working display environment

## Installation (Windows)
1. Create and activate a virtual environment (recommended):
   - PowerShell
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`

2. Install dependencies:
   - `pip install -r requirements.txt`

## Running the Game
- `python main.py`

## Controls
- Arrow keys or WASD to move.
- Esc to quit.
- Space/Enter to restart after Game Over.

## Code Structure
- `main.py`
  - `Snake` class: manages body deque/set, movement, growth, and collision helpers.
  - `Food` class: efficient random placement on free grid cells.
  - Main loop: event handling, update, draw, and FPS control via `pygame.time.Clock`.

## Configuration
- Screen size: 600x400.
- Grid cell size: 20 (must divide screen dimensions exactly).
- Initial speed: 10 FPS, increases slightly on each food eaten.

## Notes
- If the game window does not appear, ensure your environment has a working display and that Pygame installed correctly.
- To tweak speed limits or colors, edit the constants near the top of `main.py`.
