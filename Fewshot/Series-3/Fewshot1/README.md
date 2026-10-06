# Pacman Pygame (Grid-based)

A simple Pacman clone built with Pygame using a 2D grid for the maze.

## Features
- Renders a maze from a 2D grid (1=wall, 0=empty, 2=pellet, 3=power pellet)
- Pacman movement with arrow keys
- Pellet and power pellet consumption, scoring
- Two ghosts with simple random movement on valid paths
- Collision logic: Pacman vs Ghosts, frightened mode on power-up
- HUD for score, lives, win/lose states, and restart (press `R`)

## Requirements
- Python 3.8+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls
- Arrow keys: Move Pacman
- R: Restart when game over or win
- ESC or window close: Quit
