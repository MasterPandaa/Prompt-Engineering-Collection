# Snake (Pygame)

A clean, efficient, and bug-free implementation of the classic Snake game using Pygame.

## Features
- Grid-based movement at fixed ticks for consistent speed.
- `Snake` and `Food` classes keep the main loop clean and maintainable.
- Responsive arrow key controls with guard to prevent instant reverse.
- Accurate growth logic and efficient random food placement avoiding the snake body.
- Solid collision detection (walls and self).
- Subtle grid, readable colors, score and game-over overlay.

## Requirements
- Python 3.9+
- Windows (optimized instructions below)

## Install
From the project directory `d:/laragon2/laragon/www/dataset/Snake/role-based/iterasi3/`:

1) Create and activate a virtual environment (PowerShell):
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Upgrade pip and install dependencies:
```
python -m pip install -U pip
pip install -r requirements.txt
```

## Run
```
python main.py
```

## Controls
- Arrow Up/Down/Left/Right: move the snake.
- Enter: restart after Game Over.
- Esc: quit.

## Notes
- The playfield is 600x400 with 20px grid cells (30x20 grid).
- Movement is processed on a fixed timer independent of frame rate (default 120ms per move).
- Food spawn is optimized: sampling for empty cells when the board is sparse, and a single filtered list when the board is crowded.
