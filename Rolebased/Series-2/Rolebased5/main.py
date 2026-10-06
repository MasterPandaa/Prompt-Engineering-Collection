import sys
import random
from dataclasses import dataclass
from typing import List, Tuple, Set

import pygame

# -----------------------------
# Configuration & Constants
# -----------------------------
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE  # 30
GRID_ROWS = HEIGHT // CELL_SIZE  # 20
FPS = 12  # Game speed; tweak for difficulty

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
GRAY = (40, 40, 40)

# Direction vectors (dx, dy) in grid coordinates
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


@dataclass
class Food:
    position: Tuple[int, int]

    def respawn(self, snake_positions: Set[Tuple[int, int]]) -> None:
        """Place food in a random free cell avoiding the snake's body."""
        free_cells = [(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)
                      if (x, y) not in snake_positions]
        if not free_cells:
            # No free cell: player wins; keep current position (game will end elsewhere)
            return
        self.position = random.choice(free_cells)

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)


class Snake:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        # Initial snake of length 3 moving to the right
        self.segments: List[Tuple[int, int]] = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self.direction: Tuple[int, int] = RIGHT
        self._pending_growth: int = 0

    @property
    def head(self) -> Tuple[int, int]:
        return self.segments[0]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Update direction unless it would reverse the snake instantly."""
        cur_dx, cur_dy = self.direction
        ndx, ndy = new_dir
        # Guard: prevent reversing direction
        if (cur_dx + ndx == 0) and (cur_dy + ndy == 0):
            return
        # Ignore if same direction to avoid redundant updates
        if new_dir == self.direction:
            return
        self.direction = new_dir

    def grow(self, amount: int = 1) -> None:
        self._pending_growth += amount

    def move(self) -> None:
        dx, dy = self.direction
        hx, hy = self.head
        new_head = (hx + dx, hy + dy)
        # Insert new head
        self.segments.insert(0, new_head)
        # Remove tail unless we are growing
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.segments.pop()

    def hits_wall(self) -> bool:
        x, y = self.head
        return not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS)

    def hits_self(self) -> bool:
        return self.head in self.segments[1:]

    def occupies(self) -> Set[Tuple[int, int]]:
        return set(self.segments)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw head darker for clarity
        for i, (x, y) in enumerate(self.segments):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = DARK_GREEN if i == 0 else GREEN
            pygame.draw.rect(surface, color, rect)


def draw_grid(surface: pygame.Surface) -> None:
    # Subtle grid background for visual clarity
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))


def render_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: pygame.font.Font) -> None:
    img = font.render(text, True, WHITE)
    surface.blit(img, pos)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 28, bold=True)

    snake = Snake()
    food = Food(position=(0, 0))
    food.respawn(snake.occupies())

    score = 0
    game_over = False

    def reset_game() -> None:
        nonlocal snake, food, score, game_over
        snake.reset()
        food.respawn(snake.occupies())
        score = 0
        game_over = False

    running = True
    while running:
        # -----------------------------
        # Event Handling
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
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
                    # Restart on Enter when game over
                    if event.key == pygame.K_RETURN:
                        reset_game()

        # -----------------------------
        # Update
        # -----------------------------
        if not game_over:
            snake.move()

            # Collisions
            if snake.hits_wall() or snake.hits_self():
                game_over = True
            elif snake.head == food.position:
                score += 1
                snake.grow(1)
                food.respawn(snake.occupies())

        # -----------------------------
        # Render
        # -----------------------------
        screen.fill(BLACK)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        render_text(screen, f"Score: {score}", (8, 6), font_small)

        if game_over:
            msg1 = "Game Over"
            msg2 = "Press Enter to Restart or Esc to Quit"
            text1 = font_big.render(msg1, True, WHITE)
            text2 = font_small.render(msg2, True, WHITE)
            rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 18))
            screen.blit(text1, rect1)
            screen.blit(text2, rect2)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
