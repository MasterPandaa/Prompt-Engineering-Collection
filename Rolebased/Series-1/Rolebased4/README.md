# Pong (Pygame)

A clean, object-oriented Pong game built with Pygame.

## Features

- 800x600 window, classic Pong look.
- OOP structure with `Paddle`, `Ball`, and `Game` classes.
- Player controls: `W` (up), `S` (down).
- Fair AI: tracks the ball with reaction delay and error margin so it can be beaten.
- Accurate wall and paddle collisions with spin based on hit position.
- Scoring system with on-screen display.

## Requirements

- Python 3.9+
- See `requirements.txt` for Python dependencies.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python pong.py
```

## Controls

- W: Move up
- S: Move down
- ESC: Quit
