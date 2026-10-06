# Pacman Clone (Python + Pygame)

A clean, object-oriented Pacman clone implemented with Python and Pygame.

## Features

- OOP architecture: `Game`, `Player`, `Ghost`, `Maze` classes.
- Hardcoded 2D maze layout with walls, pellets, and power-pellets.
- Two ghost AIs:
  - `Blinky` (chaser): simple BFS-based chasing towards the player.
  - `Clyde` (random): random walker that avoids immediate reversals.
- Power-pellet mechanic: ghosts become vulnerable for a duration; the player can "eat" them.
- Scoring, lives, win and game over states.
- Wrap-around tunnels.

## File Structure

- `pacman.py` — main game entry and all classes.
- `requirements.txt` — pinned dependency versions.

## Requirements

- Python 3.9+
- Windows/macOS/Linux with a working display.

## Installation

```bash
python -m pip install -r requirements.txt
```

If you have multiple Python versions, you may need to use `python3` instead of `python`.

## Run

```bash
python pacman.py
```

## Controls

- Arrow keys or WASD to move.
- Press Enter to restart after Win/Game Over.

## Notes

- The implementation focuses on clean OOP and straightforward mechanics. Ghost AI is intentionally simple to keep the code approachable.
- Tile size and maze dimensions are configurable at the top of `pacman.py`.

## Credits

Built by Cascade (Expert Arcade Game Developer).
