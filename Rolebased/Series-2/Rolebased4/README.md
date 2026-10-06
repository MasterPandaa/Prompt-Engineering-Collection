# Pygame Snake

A clean, efficient, and maintainable implementation of the classic Snake game using Pygame.

## Specs
- Window: 600 x 400
- Grid cell size: 20px (30x20 grid)
- Organized classes: `Snake`, `Food`
- Responsive controls with guard against reverse direction
- Solid collision detection (walls and self)
- Efficient food placement avoiding the snake body

## Controls
- Arrow Keys or WASD to move
- R to restart after Game Over
- ESC to quit

## Run Locally
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Code Overview
- `main.py`: Contains the game loop and the `Snake` and `Food` classes.
  - `Snake` uses a `deque` for efficient head/tail operations and maintains an `occupied` set for fast membership checks.
  - Movement timing is driven by a `pygame.time.set_timer` event to ensure consistent step rate.
  - Direction changes use a guard clause to prevent 180° reversals in a single step.
  - Food placement tries random free cells with a capped retry, then falls back to a deterministic scan to guarantee placement.

## Notes
- Requires Python 3.9+.
- Tested with `pygame==2.6.1`.
