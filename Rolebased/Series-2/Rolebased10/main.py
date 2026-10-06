import sys
import random
from collections import deque
from typing import Deque, List, Set, Tuple

import pygame

# --- Configuration ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20  # Grid size (must evenly divide both width and height)
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

BG_COLOR = (18, 18, 18)
SNAKE_COLOR = (80, 220, 100)
SNAKE_HEAD_COLOR = (120, 255, 140)
FOOD_COLOR = (240, 80, 80)
GRID_COLOR = (30, 30, 30)
TEXT_COLOR = (230, 230, 230)

INITIAL_SPEED = 10  # frames per second
SPEED_INCREMENT_ON_EAT = 0.5

# Directions as (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def grid_to_px(cell: Tuple[int, int]) -> Tuple[int, int]:
    """Convert grid coordinates to top-left pixel coordinates."""
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE


class Snake:
    """Snake represented as a deque of grid positions (x, y)."""

    def __init__(self) -> None:
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self._body: Deque[Tuple[int, int]] = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        self._body_set: Set[Tuple[int, int]] = set(self._body)
        self._direction: Tuple[int, int] = RIGHT
        self._pending_direction: Tuple[int, int] = RIGHT
        self._grow_segments: int = 0

    @property
    def head(self) -> Tuple[int, int]:
        return self._body[0]

    @property
    def body(self) -> List[Tuple[int, int]]:
        return list(self._body)

    @property
    def body_set(self) -> Set[Tuple[int, int]]:
        return set(self._body_set)

    @property
    def direction(self) -> Tuple[int, int]:
        return self._direction

    def try_set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Queue a new direction if it's not directly opposite the current direction."""
        if new_dir == OPPOSITE[self._direction]:
            return  # Guard: prevent reversing into itself
        self._pending_direction = new_dir

    def move(self) -> bool:
        """Advance the snake by one cell and return True if it collided with itself.

        Performs O(1) self-collision detection by checking the new head against the
        current body set before removing the tail. The tail cell is allowed to be
        re-entered in the same tick if we are not growing, since it will move away.
        """
        # Apply pending direction once per tick to keep movement deterministic
        self._direction = self._pending_direction

        hx, hy = self.head
        dx, dy = self._direction
        new_head = (hx + dx, hy + dy)

        # Determine tail (may be removed if not growing)
        tail = None if self._grow_segments > 0 else self._body[-1]

        # Collision if new head hits body, excluding the tail which will vacate
        collided_self = new_head in self._body_set and new_head != tail

        self._body.appendleft(new_head)
        self._body_set.add(new_head)

        if self._grow_segments > 0:
            self._grow_segments -= 1
        else:
            assert tail is not None
            self._body.pop()
            self._body_set.remove(tail)

        return collided_self

    def grow(self, n: int = 1) -> None:
        self._grow_segments += n

    def hits_wall(self) -> bool:
        x, y = self.head
        return x < 0 or x >= GRID_COLS or y < 0 or y >= GRID_ROWS

    def hits_self(self) -> bool:
        # Fallback check; main loop uses move()'s returned collision flag
        # More efficient than counting: set size shrinks if there is a duplicate
        return len(self._body_set) != len(self._body)


class Food:
    def __init__(self, snake: Snake) -> None:
        self.position: Tuple[int, int] = self._random_free_cell(snake)

    def _random_free_cell(self, snake: Snake) -> Tuple[int, int]:
        """Efficiently choose a random free cell not occupied by the snake."""
        occupied = snake.body_set
        total_cells = GRID_COLS * GRID_ROWS
        # Fast path: if snake is small, retry a few times
        if len(occupied) < total_cells // 3:
            while True:
                candidate = (random.randrange(GRID_COLS), random.randrange(GRID_ROWS))
                if candidate not in occupied:
                    return candidate
        # Otherwise compute free list once
        free_cells = [(x, y) for y in range(GRID_ROWS) for x in range(GRID_COLS) if (x, y) not in occupied]
        return random.choice(free_cells) if free_cells else (-1, -1)

    def relocate(self, snake: Snake) -> None:
        self.position = self._random_free_cell(snake)


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)


def draw_snake(surface: pygame.Surface, snake: Snake) -> None:
    for i, (x, y) in enumerate(snake.body):
        px, py = grid_to_px((x, y))
        color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, color, rect, border_radius=4)


def draw_food(surface: pygame.Surface, food: Food) -> None:
    fx, fy = grid_to_px(food.position)
    padding = CELL_SIZE // 6
    rect = pygame.Rect(fx + padding, fy + padding, CELL_SIZE - 2 * padding, CELL_SIZE - 2 * padding)
    pygame.draw.rect(surface, FOOD_COLOR, rect, border_radius=6)


def render_text(surface: pygame.Surface, text: str, size: int, y: int) -> None:
    font = pygame.font.SysFont("consolas,monospace", size)
    s = font.render(text, True, TEXT_COLOR)
    rect = s.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(s, rect)


def main() -> None:
    if SCREEN_WIDTH % CELL_SIZE != 0 or SCREEN_HEIGHT % CELL_SIZE != 0:
        raise ValueError("SCREEN dimensions must be multiples of CELL_SIZE")

    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food(snake)

    score = 0
    speed = INITIAL_SPEED
    running = True
    game_over = False

    while running:
        # --- Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        snake.try_set_direction(UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        snake.try_set_direction(DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        snake.try_set_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        snake.try_set_direction(RIGHT)
                else:
                    # On game over, allow restart with Space/Enter
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        snake = Snake()
                        food = Food(snake)
                        score = 0
                        speed = INITIAL_SPEED
                        game_over = False

        if not game_over:
            # --- Update ---
            collided_self = snake.move()

            # Collision with walls or self
            if snake.hits_wall() or collided_self:
                game_over = True

            # Eat food
            if snake.head == food.position:
                snake.grow(1)
                score += 1
                speed = min(30, speed + SPEED_INCREMENT_ON_EAT)
                food.relocate(snake)

        # --- Draw ---
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_snake(screen, snake)
        draw_food(screen, food)

        render_text(screen, f"Score: {score}", 20, 16)
        if game_over:
            render_text(screen, "Game Over - Press Space to Restart", 22, SCREEN_HEIGHT // 2)

        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
