import pygame
import random
from typing import List, Tuple, Deque, Set
from collections import deque

# -----------------------------
# Constants and Configurations
# -----------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20  # grid cell size; 600x400 -> 30x20 cells
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 20, 60)
GRAY = (50, 50, 50)

# Movement vectors (dx, dy) in grid cells
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game speeds
MOVE_TICKS_MS = 120  # snake moves every N ms (controls game speed)


# -----------------------------
# Helper functions
# -----------------------------

def grid_to_px(cell: Tuple[int, int]) -> Tuple[int, int]:
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE


# -----------------------------
# Food Class
# -----------------------------
class Food:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.position: Tuple[int, int] = (0, 0)

    def respawn(self, occupied: Set[Tuple[int, int]]):
        # Efficient random respawn avoiding snake body
        total_cells = GRID_COLS * GRID_ROWS
        # If snake occupies most of the board, compute remaining cells once
        if len(occupied) > total_cells // 2:
            available = [
                (x, y)
                for y in range(GRID_ROWS)
                for x in range(GRID_COLS)
                if (x, y) not in occupied
            ]
            if not available:
                self.position = (-1, -1)
                return
            self.position = self.rng.choice(available)
            return

        # Otherwise, sample until finding a free cell
        while True:
            pos = (self.rng.randrange(GRID_COLS), self.rng.randrange(GRID_ROWS))
            if pos not in occupied:
                self.position = pos
                return

    def draw(self, surface: pygame.Surface):
        px = grid_to_px(self.position)
        rect = pygame.Rect(px[0], px[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)


# -----------------------------
# Snake Class
# -----------------------------
class Snake:
    def __init__(self):
        # Start roughly center
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        self.body: Deque[Tuple[int, int]] = deque(
            [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        )
        self.body_set: Set[Tuple[int, int]] = set(self.body)
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Tuple[int, int] = RIGHT
        self.grow_pending: int = 0
        self.alive: bool = True

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def set_direction(self, new_dir: Tuple[int, int]):
        # Guard clause to prevent reversing direction directly
        cur_dx, cur_dy = self.direction
        new_dx, new_dy = new_dir
        if (cur_dx == -new_dx and cur_dx != 0) or (cur_dy == -new_dy and cur_dy != 0):
            return
        # Queue the direction to apply at next movement tick
        self.next_direction = new_dir

    def step(self) -> bool:
        # Apply any queued direction change
        self.direction = self.next_direction

        dx, dy = self.direction
        hx, hy = self.head()
        new_head = (hx + dx, hy + dy)

        # Check wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            self.alive = False
            return False

        # If not growing, tail will be removed after moving; so moving into the current tail is allowed.
        tail = self.body[-1]
        will_remove_tail = self.grow_pending == 0

        # Check self-collision (except the tail if it will move)
        if new_head in self.body_set and (not will_remove_tail or new_head != tail):
            self.alive = False
            return False

        # Move: add new head
        self.body.appendleft(new_head)
        self.body_set.add(new_head)

        # Handle growth or pop tail
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            removed = self.body.pop()
            self.body_set.remove(removed)

        return True

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def draw(self, surface: pygame.Surface):
        # Draw head a bit brighter
        for i, (x, y) in enumerate(self.body):
            px = x * CELL_SIZE
            py = y * CELL_SIZE
            rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
            color = GREEN if i > 0 else DARK_GREEN
            pygame.draw.rect(surface, color, rect)
            # Optional: subtle grid-like inner border for visibility
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(surface, BLACK, inner, width=1)


# -----------------------------
# Game Functions
# -----------------------------

def draw_grid(surface: pygame.Surface):
    # Subtle grid for visual aid
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y))


def draw_score(surface: pygame.Surface, font: pygame.font.Font, score: int):
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 8))


def game_over_screen(surface: pygame.Surface, font: pygame.font.Font, score: int):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    title = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    hint = font.render("Press Enter to Restart or Esc to Quit", True, WHITE)

    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    surface.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))


# -----------------------------
# Main loop
# -----------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 20)
    rng = random.Random()

    def new_game():
        snake = Snake()
        food = Food(rng)
        food.respawn(snake.body_set)
        score = 0
        return snake, food, score

    snake, food, score = new_game()

    # Timing for deterministic movement independent of frame rate
    accumulator_ms = 0

    running = True
    while running:
        dt = clock.tick(60)  # limit FPS, get elapsed ms
        accumulator_ms += dt

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    snake.set_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.set_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction(RIGHT)
                elif not snake.alive and event.key == pygame.K_RETURN:
                    snake, food, score = new_game()
                    accumulator_ms = 0

        # Update movement at fixed intervals
        while accumulator_ms >= MOVE_TICKS_MS and snake.alive:
            accumulator_ms -= MOVE_TICKS_MS
            progressed = snake.step()
            if not progressed:
                break

            # Check food collision
            if snake.head() == food.position:
                snake.grow(1)
                score += 1
                food.respawn(snake.body_set)

        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)
        draw_score(screen, font, score)

        if not snake.alive:
            game_over_screen(screen, font, score)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
