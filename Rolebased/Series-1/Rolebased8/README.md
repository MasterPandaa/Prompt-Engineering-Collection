# Pong (Pygame)

A clean, efficient, and easy-to-read Pong implementation using Pygame.

## Features
- 800x600 window.
- OOP design with `Paddle` and `Ball` classes.
- Player controls: Left paddle uses `W` (up) and `S` (down).
- AI opponent: Fair and beatable with reaction delay, capped speed, and small error margin.
- Accurate ball bounces and scoring system.
- Frame-rate–independent movement using `dt`.

## Requirements
- Python 3.9+
- Pygame (see `requirements.txt`)

## Setup
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python pong.py
```

## Controls
- W: Move up
- S: Move down
- Esc: Quit
- Space: Serve/Reset after a point

## Notes on AI
The AI paddle includes:
- Reaction delay before changing target.
- Small random aim offset that changes over time.
- Speed cap and smoothing to avoid perfect tracking.
- Only engages when the ball moves towards the AI; otherwise, it recenters slowly.
