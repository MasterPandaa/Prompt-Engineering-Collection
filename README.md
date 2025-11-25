# Pacman (Pygame)

A minimal yet complete Pacman clone implemented with Pygame.

## Features
- Grid-based maze with walls, pellets, and power pellets.
- Pacman player with arrow-key controls.
- Four ghosts with simple AI: avoid immediate reversal and choose direction at intersections; chase the player, wander when frightened.
- Power mode: eat power pellets to frighten ghosts temporarily.
- Basic HUD with score and lives.
- Win and Game Over states.

## Requirements
- Python 3.9+
- pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Controls:
- Arrow keys to move Pacman
- R to restart on Game Over / Win
- Esc to quit

## Notes
- The maze is defined in `main.py` via `MAZE_LAYOUT`.
- All assets are drawn procedurally; no external image files required.
