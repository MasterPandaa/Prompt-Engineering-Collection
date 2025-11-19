# Pong (Pygame)

A clean, OOP-based Pong implementation in Pygame with a fair-but-challenging AI opponent.

## Features
- Object-oriented `Paddle` and `Ball` classes in `main.py`.
- Player controls: `W` (up) and `S` (down).
- AI opponent with reaction delay, error margin, and capped speed (beatable).
- Accurate ball bounce physics with angle based on hit position.
- Gradual ball speed-up and score tracking.
- 800x600 window, smooth 60 FPS.

## Requirements
- Python 3.9+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run
On Windows (PowerShell), from the project directory:

```powershell
python main.py
```

Recommended (isolated) setup on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Controls
- W: Move left paddle up
- S: Move left paddle down
- SPACE: Serve after a point
- ESC: Quit

## Code Structure
- `main.py`
  - `Paddle`: movement, clamped to screen, drawing.
  - `Ball`: motion, wall bounce, paddle collision with angle control, speed ramping.
  - `AIPaddleController`: reaction interval, target with random error, center-return when ball is moving away.
  - Main loop: input, updates, collision, scoring, rendering (center dashed line + score HUD).
- `requirements.txt`: dependency pin for Pygame.

## Notes
- AI parameters (`AI_*` constants) and gameplay tuning (`BALL_*`, `PADDLE_*`) are centralized at the top of `main.py` for easy balancing.
- Code adheres to PEP 8 and is organized for readability.
