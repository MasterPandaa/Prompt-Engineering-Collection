import sys
import random
from collections import deque
from typing import Deque, Set, Tuple, Optional

import pygame

# --- Constants ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20  # Grid cell size; 600x400 -> 30x20 cells
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (40, 200, 40)
DARK_GREEN = (20, 120, 20)
RED = (220, 50, 50)
GRAY = (30, 30, 30)

# Directions as (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Movement speed in steps per second
SNAKE_SPEED = 10


class Snake:
    """Snake represented as a deque of grid positions (x, y). Head at the right end."""

    def __init__(self) -> None:
        start_x, start_y = COLS // 2, ROWS // 2
        self.body: Deque[Tuple[int, int]] = deque([(start_x - 1, start_y), (start_x, start_y)])
        self.direction: Tuple[int, int] = RIGHT
        self.grow_pending: int = 0
        self.occupied: Set[Tuple[int, int]] = set(self.body)

    def head(self) -> Tuple[int, int]:
        return self.body[-1]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Update direction with guard clause preventing direct reversal."""
        if not self.body:
            self.direction = new_dir
            return
        dx, dy = self.direction
        ndx, ndy = new_dir
        # Prevent reversing directly into the previous segment
        if (dx + ndx, dy + ndy) == (0, 0):
            return
        self.direction = new_dir

    def step(self) -> None:
        """Advance the snake by one cell. Handles growth."""
        hx, hy = self.head()
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.append(new_head)
        self.occupied.add(new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            tail = self.body.popleft()
            # Update occupied set only if tail is not the new head
            if tail not in self.body:
                self.occupied.discard(tail)

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def hits_wall(self) -> bool:
        x, y = self.head()
        return x < 0 or x >= COLS or y < 0 or y >= ROWS

    def hits_self(self) -> bool:
        head = self.head()
        # Count of head in body > 1 implies collision with itself
        return head in set(list(self.body)[:-1])

    def draw(self, surface: pygame.Surface) -> None:
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = DARK_GREEN if i < len(self.body) - 1 else GREEN
            pygame.draw.rect(surface, color, rect)
            # Optional border for readability
            pygame.draw.rect(surface, BLACK, rect, 1)


class Food:
    """Food placed on an empty grid cell not occupied by the snake."""

    def __init__(self, snake: Snake) -> None:
        self.position: Tuple[int, int] = (0, 0)
        self.relocate(snake)

    def relocate(self, snake: Snake) -> None:
        """Place food at a random free cell. Efficient by sampling from remaining cells."""
        total_cells = COLS * ROWS
        occupied = snake.occupied
        free_count = total_cells - len(occupied)
        if free_count <= 0:
            # No space left; position is irrelevant
            self.position = snake.head()
            return

        # To avoid building a large list every frame, we can attempt random sampling
        # with a cap on retries, and fall back to enumerating free cells only if needed.
        max_random_tries = 50
        for _ in range(max_random_tries):
            x = random.randrange(COLS)
            y = random.randrange(ROWS)
            if (x, y) not in occupied:
                self.position = (x, y)
                return

        # Fallback: deterministic search for a free cell
        for y in range(ROWS):
            for x in range(COLS):
                if (x, y) not in occupied:
                    self.position = (x, y)
                    return

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))


def render_text(surface: pygame.Surface, text: str, size: int, color, y: int) -> None:
    font = pygame.font.SysFont("consolas", size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    def reset_game() -> Tuple[Snake, Food, int, bool]:
        snake = Snake()
        food = Food(snake)
        score = 0
        game_over = False
        return snake, food, score, game_over

    snake, food, score, game_over = reset_game()

    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, int(1000 / SNAKE_SPEED))

    running = True
    pending_dir: Optional[Tuple[int, int]] = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    snake, food, score, game_over = reset_game()
                    pending_dir = None
                    continue
                # Direction handling: set a pending direction applied on the next tick
                if event.key in (pygame.K_UP, pygame.K_w):
                    pending_dir = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    pending_dir = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    pending_dir = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    pending_dir = RIGHT
            elif event.type == move_event and not game_over:
                if pending_dir is not None:
                    snake.set_direction(pending_dir)
                    pending_dir = None
                snake.step()

                # Check collisions
                if snake.hits_wall() or snake.hits_self():
                    game_over = True
                elif snake.head() == food.position:
                    snake.grow()
                    score += 1
                    food.relocate(snake)

        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        # HUD
        hud_font = pygame.font.SysFont("consolas", 20)
        score_surf = hud_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (8, 6))

        if game_over:
            render_text(screen, "GAME OVER", 32, WHITE, HEIGHT // 2 - 20)
            render_text(screen, "Press R to Restart or ESC to Quit", 20, WHITE, HEIGHT // 2 + 20)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
