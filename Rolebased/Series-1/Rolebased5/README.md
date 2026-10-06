# Pong (Pygame)

A clean, object-oriented Pong implementation using Pygame with a fair, beatable AI.

## Requirements

- Python 3.9+
- pygame (see `requirements.txt`)

## Install

```bash
python -m venv .venv
.venv\Scripts\pip install -U pip
.venv\Scripts\pip install -r requirements.txt
```

## Run

```bash
.venv\Scripts\python pong.py
```

## Controls

- W: Move up (left paddle)
- S: Move down (left paddle)
- ESC: Quit

## Features

- OOP classes: `Paddle`, `Ball`
- Accurate bounce physics with variable angle based on hit position
- Progressive ball speed with an upper cap
- AI opponent with reaction delay, lookahead and aim error so it can be beaten
- Score tracking and win banner (first to 10)
- 800x600 screen, 60 FPS
