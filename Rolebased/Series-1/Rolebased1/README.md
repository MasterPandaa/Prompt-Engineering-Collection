# Pong (Pygame)

A clean, object-oriented Pong implementation using Pygame with a fair, beatable AI.

## Features
- OOP structure: `Paddle`, `Ball`, and `AIController` classes in `main.py`.
- Smooth physics: accurate wall and paddle bounces with spin based on hit offset.
- Fair AI: reaction delay and error margin so it can be beaten.
- Controls: Left paddle uses `W` and `S`.
- UI: Scoreboard, dashed midline, pause/reset controls.

## Requirements
- Python 3.8+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls
- W / S: Move left paddle up / down
- P: Pause / resume
- R: Reset match
- Esc: Quit

## Notes
- Default resolution is 800x600 at 60 FPS.
- First to 10 points wins. Serving alternates toward the conceding side.
