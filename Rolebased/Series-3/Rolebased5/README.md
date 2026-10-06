# Pacman (Pygame)

A clean, object-oriented Pacman clone built with Python and Pygame.

## Requirements
- Python 3.9+
- Pygame

## Setup (Windows)
1. Create a virtual environment (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Run the game:
   ```powershell
   python pacman.py
   ```

## Controls
- Arrow keys or WASD to move
- Esc to quit

## Features
- OOP architecture: `Game`, `Maze`, `Player`, `Ghost` (with `ChaserGhost` and `WanderGhost`)
- Hardcoded 2D maze layout
- Dot and power-pellet logic with score
- Ghost AI:
  - Chaser: pursues the player using BFS pathfinding to target tile
  - Wander: random movement at intersections
- Power pellets turn ghosts vulnerable for a limited time; they can be eaten and will respawn

## Notes
- Window size and speeds are tuned for a 28x31-style maze.
- Code is organized and commented for clarity and extension.
