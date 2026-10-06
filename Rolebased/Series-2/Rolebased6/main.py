import sys
import random
import pygame
from typing import List, Tuple, Set

# Configuration
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE
GRID_ROWS = HEIGHT // CELL_SIZE

# Colors
BG_COLOR = (18, 18, 18)
GRID_COLOR = (30, 30, 30)
SNAKE_HEAD_COLOR = (80, 200, 120)
SNAKE_BODY_COLOR = (60, 160, 100)
FOOD_COLOR = (220, 80, 80)
TEXT_COLOR = (230, 230, 230)

# Directions as (dx, dy) in grid coordinates
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class Snake:
    def __init__(self, start: Tuple[int, int]):
        # positions store grid coordinates (col, row)
        self.positions: List[Tuple[int, int]] = [start]
        self.direction: Tuple[int, int] = RIGHT
        self.pending_direction: Tuple[int, int] = RIGHT
        self.grow_pending: int = 0

    def head(self) -> Tuple[int, int]:
        return self.positions[0]

    def set_direction(self, new_dir: Tuple[int, int]):
        # Guard: prevent reversing into itself if length > 1
        if len(self.positions) > 1 and new_dir == OPPOSITE[self.direction]:
            return
        self.pending_direction = new_dir

    def step(self):
        # Apply pending direction once per tick to keep input responsive but consistent
        self.direction = self.pending_direction
        hx, hy = self.head()
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.positions.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def hits_self(self) -> bool:
        return self.head() in self.positions[1:]

    def occupies(self) -> Set[Tuple[int, int]]:
        return set(self.positions)

    def draw(self, surface: pygame.Surface):
        # Draw head
        for i, (cx, cy) in enumerate(self.positions):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect, border_radius=4)


class Food:
    def __init__(self, snake: Snake):
        self.position: Tuple[int, int] = self._random_empty_cell(snake)

    def _random_empty_cell(self, snake: Snake) -> Tuple[int, int]:
        occupied = snake.occupies()
        # Efficient random placement by sampling from the set of free cells
        all_cells = {(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)}
        free_cells = list(all_cells - occupied)
        if not free_cells:
            return (-1, -1)  # fallback (should indicate win state)
        return random.choice(free_cells)

    def respawn(self, snake: Snake):
        self.position = self._random_empty_cell(snake)

    def draw(self, surface: pygame.Surface):
        if self.position == (-1, -1):
            return
        cx, cy = self.position
        rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect, border_radius=4)


def draw_grid(surface: pygame.Surface):
    # Subtle grid for visual polish
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))


def within_bounds(cell: Tuple[int, int]) -> bool:
    x, y = cell
    return 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS


def render_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: pygame.font.Font, color=TEXT_COLOR):
    img = font.render(text, True, color)
    surface.blit(img, pos)


def reset_game() -> Tuple[Snake, Food, int, bool]:
    start = (GRID_COLS // 2, GRID_ROWS // 2)
    snake = Snake(start)
    food = Food(snake)
    score = 0
    game_over = False
    return snake, food, score, game_over


def main():
    pygame.init()
    pygame.display.set_caption("Snake (Pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    big_font = pygame.font.SysFont("consolas", 36)

    snake, food, score, game_over = reset_game()

    # Movement speed (steps per second)
    speed = 10

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
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
                        snake, food, score, game_over = reset_game()

        if not game_over:
            # Update
            snake.step()

            # Collisions
            if not within_bounds(snake.head()) or snake.hits_self():
                game_over = True
            else:
                if snake.head() == food.position:
                    score += 1
                    snake.grow(1)
                    food.respawn(snake)

        # Draw
        screen.fill(BG_COLOR)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        render_text(screen, f"Score: {score}", (10, 8), font)
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg1 = "Game Over"
            msg2 = "Press R to Restart | Esc to Quit"
            text1 = big_font.render(msg1, True, TEXT_COLOR)
            text2 = font.render(msg2, True, TEXT_COLOR)
            screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT // 2 - 40))
            screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT // 2 + 5))

        pygame.display.flip()
        clock.tick(speed)


if __name__ == "__main__":
    main()
