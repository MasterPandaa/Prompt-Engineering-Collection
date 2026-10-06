# Pong (Pygame)

A clean, OOP-based Pong implementation using Pygame.

## Features

- 800x600 window
- Left paddle controlled by `W` and `S`
- Right paddle powered by a fair-but-challenging AI (reaction delay + error)
- Accurate ball bounce physics and scoring
- Clear, readable, PEP 8–style code with `Paddle` and `Ball` classes

## Requirements

- Python 3.9+
- Pygame

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python pong.py
```

## Controls

- `W`: move up
- `S`: move down
- `Esc`: quit

## Notes on AI

The AI updates its target only at discrete intervals (reaction delay) and adds a
speed/distance-based error margin. This ensures it is beatable while remaining
challenging as the ball accelerates.
