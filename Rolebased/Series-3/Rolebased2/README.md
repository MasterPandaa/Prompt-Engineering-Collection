# Pacman OOP Clone (Pygame)

A minimal but complete Pacman clone built with Python and Pygame, showcasing OOP structure and simple ghost AI behaviors.

## Features
- OOP classes: `Game`, `Player`, `Ghost` (with `ChaserGhost`, `RandomGhost`), and `Maze`.
- Hardcoded 2D maze layout parsed into walls, pellets, and power-pellets.
- Two ghost AIs:
  - Chaser (BFS to player's tile).
  - Random (random at intersections; greedy return-to-lair when eaten).
- Power-pellet mechanics: ghosts turn frightened (cyan), can be eaten, respawn at lair.
- HUD: score and lives, game over and level complete overlays.

## Requirements
- Python 3.9+
- Pygame (see `requirements.txt`)

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the game:
   ```bash
   python main.py
   ```

## Controls
- Arrow Keys or WASD to move
- ESC to quit
- R to restart

## Notes
- The maze includes wrap-around tunnels horizontally.
- Layout symbols: `#` wall, `.` pellet, `o` power-pellet, `P` player start, `G` ghost spawn, space = empty.
