import random
import sys
from typing import List, Tuple, Optional

import pygame

# ----------------------------
# Constants and configuration
# ----------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20

GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 30, 30)
GRAY = (35, 35, 35)

# Movement directions as (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game speed (cells per second approx)
SNAKE_SPEED = 10


# ----------------------------
# Helper functions
# ----------------------------

def grid_to_px(cell: Tuple[int, int]) -> Tuple[int, int]:
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE


# ----------------------------
# Game objects
# ----------------------------
class Snake:
    def __init__(self) -> None:
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        # Head at the end of initial positions for simpler insert-at-front logic
        self.body: List[Tuple[int, int]] = [
            (start_x - 2, start_y),
            (start_x - 1, start_y),
            (start_x, start_y),
        ]
        self.direction: Tuple[int, int] = RIGHT
        self.pending_growth: int = 0

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[-1]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        # Guard clause: prevent 180-degree turn
        cur_dx, cur_dy = self.direction
        new_dx, new_dy = new_dir
        if (cur_dx == -new_dx and cur_dy == -new_dy):
            return
        # If snake length is > 1, also ensure next cell isn't the second last cell
        if len(self.body) > 1:
            next_cell = (self.head[0] + new_dx, self.head[1] + new_dy)
            if next_cell == self.body[-2]:
                return
        self.direction = new_dir

    def move(self) -> None:
        dx, dy = self.direction
        new_head = (self.head[0] + dx, self.head[1] + dy)
        self.body.append(new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            # remove tail segment
            del self.body[0]

    def grow(self, amount: int = 1) -> None:
        self.pending_growth += amount

    def collided_with_wall(self) -> bool:
        hx, hy = self.head
        return not (0 <= hx < GRID_COLS and 0 <= hy < GRID_ROWS)

    def collided_with_self(self) -> bool:
        head = self.head
        return head in self.body[:-1]

    def draw(self, surface: pygame.Surface) -> None:
        # Draw body
        for idx, (x, y) in enumerate(self.body):
            px, py = grid_to_px((x, y))
            rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
            color = DARK_GREEN if idx < len(self.body) - 1 else GREEN
            pygame.draw.rect(surface, color, rect)


class Food:
    def __init__(self) -> None:
        self.pos: Optional[Tuple[int, int]] = None

    def spawn(self, snake_cells: List[Tuple[int, int]]) -> None:
        occupied = set(snake_cells)
        # Efficient placement: choose from free cells only
        free_cells = [
            (x, y)
            for x in range(GRID_COLS)
            for y in range(GRID_ROWS)
            if (x, y) not in occupied
        ]
        if not free_cells:
            self.pos = None
            return
        self.pos = random.choice(free_cells)

    def draw(self, surface: pygame.Surface) -> None:
        if self.pos is None:
            return
        px, py = grid_to_px(self.pos)
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)


# ----------------------------
# Rendering helpers
# ----------------------------

def draw_grid(surface: pygame.Surface) -> None:
    # Subtle grid for visual clarity
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)


# ----------------------------
# Main game loop
# ----------------------------

def run() -> None:
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    snake = Snake()
    food = Food()
    food.spawn(snake.body)

    score = 0
    move_event = pygame.USEREVENT + 1
    move_interval_ms = int(1000 / SNAKE_SPEED)
    pygame.time.set_timer(move_event, move_interval_ms)

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        snake.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction(RIGHT)
                else:
                    if event.key == pygame.K_r:
                        # Restart
                        snake = Snake()
                        food = Food()
                        food.spawn(snake.body)
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            elif event.type == move_event and not game_over:
                snake.move()
                # Collisions
                if snake.collided_with_wall() or snake.collided_with_self():
                    game_over = True
                else:
                    # Eat food
                    if food.pos is not None and snake.head == food.pos:
                        score += 1
                        snake.grow(1)
                        food.spawn(snake.body)

        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        # HUD
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (10, 8))

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg1 = font.render("Game Over", True, WHITE)
            msg2 = font.render("Press R to Restart or Esc to Quit", True, WHITE)
            screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
