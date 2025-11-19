# Pong with AI (Pygame)

A simple Pong game implemented with Pygame. Left paddle is controlled by the player (W/S), right paddle is controlled by a basic AI that follows the ball's Y position.

## Requirements

- Python 3.8+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python pong.py
```

## Controls

- W: move up
- S: move down
- ESC: quit

## Features

- 800x600 window
- Paddle and Ball classes
- Player paddle (left) with W/S controls
- AI paddle (right) that follows ball Y with a capped speed
- Ball-wall and ball-paddle collision with speed-up on paddle hit
- Score system and dashed center line
