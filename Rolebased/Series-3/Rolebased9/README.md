# Pacman Clone (Python + Pygame)

A clean, object-oriented Pacman clone featuring a hardcoded 2D maze, pellets, power-pellets, and simple ghost AIs (chaser and random). Built with Python and Pygame.

## Features
- Object-Oriented design: `Game`, `Maze`, `Player`, `Ghost` (with `ChaserGhost` and `RandomGhost`).
- Hardcoded 2D maze with pellets and power-pellets.
- Power mode: ghosts become vulnerable for a limited time.
- Simple AI:
  - ChaserGhost: targets the player using BFS-next-step.
  - RandomGhost: picks random valid direction at intersections.
- Scoring and lives; win condition when all pellets are eaten.

## Requirements
- Python 3.9+
- Pygame (installed via requirements.txt)

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python pacman.py
```

## Controls
- Arrow keys or WASD to move Pacman.
- ESC to quit.
- SPACE to restart after win/lose.

## Notes
- Window size: 28x31 tiles at 24px each, plus UI.
- Power duration: 6 seconds (configurable in code).
- Ghost respawn after being eaten: 3 seconds.

## Project Structure
- `pacman.py` — complete implementation (Game loop and all classes)
- `requirements.txt` — dependencies
- `README.md` — this file
