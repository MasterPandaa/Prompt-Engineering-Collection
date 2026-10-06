# Pong (Pygame)

A clean, readable, and efficient Pong implementation using Pygame with OOP design.

## Features
- 800x600 window @ 60 FPS.
- `Paddle` and `Ball` classes for structure and clarity.
- Player controls: `W` (up) and `S` (down).
- AI opponent with human-like imperfections (reaction delay and error margin).
- Accurate ball physics, wall and paddle collisions, and incremental speed-up.
- Simple scoring display and dashed center line.

## Requirements
- Python 3.9+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

- Press `ESC` or close the window to exit.

## Code Structure
- `main.py`: Contains all game logic.
  - `Paddle`: Handles movement, drawing, and bounds clamping.
  - `Ball`: Handles movement, collisions, speed clamping, and scoring detection.
  - `AIOpponent`: Tracks the ball with reaction intervals and aiming error.
  - `Game`: Orchestrates input, update loop, drawing, and scoring.

## Notes on AI Behavior
- The AI only updates its target periodically (reaction time) and aims with a small random error proportional to ball speed, so it is strong but beatable.
- When the ball moves away from the AI, it gradually re-centers.

## Controls
- `W`: Move player paddle up
- `S`: Move player paddle down
- `ESC`: Quit
