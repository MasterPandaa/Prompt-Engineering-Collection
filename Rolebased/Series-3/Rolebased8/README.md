# Pacman (Simple OOP Clone with Pygame)

A clean, runnable Pacman clone built with Python and Pygame, using an OOP architecture:
- `Game`, `Maze`, `Player`, and `Ghost` classes
- Hardcoded 2D maze layout with dots and power-pellets
- Two ghost AIs: one chaser, one random
- Power mode makes ghosts vulnerable; eat them for combo score

## Requirements
- Python 3.9+ (works on Windows/macOS/Linux)
- Pygame 2.x

Install dependencies:
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Controls
- Arrow keys or WASD to move Pacman
- `R` to restart after Game Over

## Notes
- Chaser ghost tries to minimize Manhattan distance to the player.
- Random ghost picks a random valid direction at intersections.
- When a power-pellet is eaten, ghosts turn cyan and move slower; eating them increases score with a combo multiplier.
- Basic wrapping tunnels are supported horizontally.
