# Pacman Clone (Python + Pygame)

## Requirements
- Python 3.9+
- See `requirements.txt` for Python packages

Install dependencies:

```
pip install -r requirements.txt
```

## Run

```
python pacman_game.py
```

- Move Pacman with arrow keys.
- Eat dots for 10 points and power pellets for 50 points.
- When powered, ghosts turn blue and can be eaten (200 points each) for a short time.
- You have 3 lives.
- Win by eating all pellets.

## Code Structure
- `pacman_game.py`
  - `Game`: Main loop, state, rendering, collisions, power mode.
  - `Maze`: Hardcoded 2D layout, walls, pellets, power pellets, doors, rendering.
  - `Player`: Input handling, movement, pellet consumption interaction.
  - `Ghost` base + `ChaserGhost` and `RandomGhost`: Simple AI behaviors and states (`NORMAL`, `VULNERABLE`, `EATEN`).

## Notes
- Layout is a 28x31 grid similar to classic Pacman; `H` marks ghost-house doors.
- Tunnels wrap horizontally on row 14.
- Power mode duration and speeds are tunable in the config section of `pacman_game.py`.
