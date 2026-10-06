# Pong (Pygame)

A clean, object-oriented implementation of the classic Pong game using Pygame.

## Requirements

- Python 3.9+
- Pygame (see `requirements.txt`)

## Installation

1. Create and activate a virtual environment (recommended):
   
   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run

```powershell
python main.py
```

## Controls

- Player (left paddle): `W` = up, `S` = down
- Quit: `Esc`

## Features

- OOP design with `Paddle` and `Ball` classes
- Beatable AI with reaction delay and error margin
- Accurate collisions and bounce angles
- Progressive ball speed and score tracking
- 800x600 window with clean minimal UI
