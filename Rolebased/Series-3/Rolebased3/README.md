# Pacman OOP Clone (Python + Pygame)

A compact, clean Pacman clone built with Python and Pygame using OOP. It includes a hardcoded 2D maze, grid-based movement, pellets and power-pellets, and two ghost AIs (chaser and random). Power-pellets make ghosts vulnerable for a limited time.

## Features
- Object-Oriented design: `Game`, `Maze`, `Player`, `Ghost` base, `ChaserGhost`, `RandomGhost`.
- Hardcoded maze layout rendered from a 2D character map.
- Pellets (`.`) and Power-pellets (`o`).
- Ghost AI:
  - Chaser: Greedy Manhattan chase when normal, runs away when vulnerable.
  - Random: Picks random direction at junctions (avoids immediate reversal).
- Simple UI with score and lives.

## Requirements
- Python 3.9+
- Pygame (see `requirements.txt`)

## Install
```
pip install -r requirements.txt
```

## Run
```
python main.py
```

## Controls
- Arrow keys or WASD to move.
- Esc to quit.
- When Game Over / Win: Press Enter or Space to restart.

## Notes
- Movement is grid-aware and wraps horizontally through the tunnel.
- Power duration and speeds are tunable via constants at the top of `main.py`.
- The code keeps things simple while maintaining readability and separation of concerns.
