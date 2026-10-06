# Pacman Clone (Python + Pygame)

This is a clean, OOP-structured Pacman clone built with Python and Pygame.

## Features
- Object-Oriented design: `Game`, `Maze`, `Player`, `Ghost`
- Hardcoded 2D maze layout
- Two ghost AIs:
  - Chaser: greedy Manhattan pursuit
  - Random: picks random valid directions at intersections
- Power-pellet: sets ghosts to `vulnerable` state for a short duration
- Score and lives HUD

## Controls
- Arrow keys to move

## Install & Run
1. Create and activate a virtual environment (recommended)
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python pacman.py
   ```

If running on Windows and `python` maps to Python 2 or is not found, try:
```bash
py pacman.py
```

## Notes
- Legend in the layout:
  - `#` wall
  - `.` pellet
  - `o` power pellet
  - `P` player start
  - `C` chaser ghost start
  - `R` random ghost start
  - `H` ghost house (eaten ghosts return here before respawning)

Enjoy!
