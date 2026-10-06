import sys
import random
from collections import deque
from typing import Deque, Iterable, List, Optional, Set, Tuple

import pygame


# ---- Constants ----
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_W, GRID_H = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

BG_COLOR = (18, 18, 18)
SNAKE_HEAD_COLOR = (76, 175, 80)   # Green 500
SNAKE_BODY_COLOR = (56, 142, 60)   # Green 700
FOOD_COLOR = (244, 67, 54)         # Red 500
GRID_COLOR = (33, 33, 33)
TEXT_COLOR = (236, 239, 241)       # Blue Grey 50

FPS = 12  # Game speed; tweak for responsiveness/difficulty

# Direction vectors (dx, dy) in grid coordinates
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def add_pos(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return (a[0] + b[0], a[1] + b[1])


def is_opposite(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return a[0] == -b[0] and a[1] == -b[1]


class Snake:
    """Snake model with grid-based movement and growth mechanics.

    Attributes
    ----------
    body: Deque[Tuple[int, int]]
        Leftmost item is the head, rightmost is the tail.
    direction: Tuple[int, int]
        Current direction vector.
    grow_pending: int
        Number of segments to grow (increments after eating food).
    """

    def __init__(self, start: Tuple[int, int], length: int = 3, direction: Tuple[int, int] = RIGHT) -> None:
        self.body: Deque[Tuple[int, int]] = deque()
        # Initialize body horizontally to the left of start
        for i in range(length):
            self.body.appendleft((start[0] - i, start[1]))
        self.direction = direction
        self.grow_pending = 0

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    @property
    def positions_set(self) -> Set[Tuple[int, int]]:
        return set(self.body)

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Set a new direction if it is not opposite to current direction.
        Guard clause prevents reversing into itself, especially for length > 1.
        """
        if new_dir == self.direction:
            return
        if len(self.body) > 1 and is_opposite(new_dir, self.direction):
            return
        self.direction = new_dir

    def move(self) -> None:
        new_head = add_pos(self.head, self.direction)
        self.body.appendleft(new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def hits_wall(self) -> bool:
        x, y = self.head
        return not (0 <= x < GRID_W and 0 <= y < GRID_H)

    def hits_self(self) -> bool:
        # If head appears more than once in body, it collided with itself
        return self.head in list(self.body)[1:]

    def draw(self, surface: pygame.Surface) -> None:
        for idx, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = SNAKE_HEAD_COLOR if idx == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(surface, color, rect, border_radius=4)


class Food:
    """Food placed on an empty grid cell not occupied by the snake."""

    def __init__(self) -> None:
        self.position: Tuple[int, int] = (0, 0)

    def respawn(self, snake_positions: Set[Tuple[int, int]]) -> None:
        all_cells = {(x, y) for x in range(GRID_W) for y in range(GRID_H)}
        available = all_cells - snake_positions
        if not available:
            # Edge case: snake fills the board => player wins.
            self.position = (-1, -1)
            return
        self.position = random.choice(tuple(available))

    def draw(self, surface: pygame.Surface) -> None:
        if self.position == (-1, -1):
            return
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect, border_radius=6)


def draw_grid(surface: pygame.Surface) -> None:
    # Subtle grid to make movement clearer without visual clutter
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))


def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], font: pygame.font.Font, color: Tuple[int, int, int] = TEXT_COLOR) -> None:
    img = font.render(text, True, color)
    surface.blit(img, pos)


def reset_game() -> Tuple[Snake, Food, int, bool]:
    start_pos = (GRID_W // 2, GRID_H // 2)
    snake = Snake(start=start_pos, length=3, direction=RIGHT)
    food = Food()
    food.respawn(snake.positions_set)
    score = 0
    game_over = False
    return snake, food, score, game_over


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 28, bold=True)

    snake, food, score, game_over = reset_game()

    running = True
    while running:
        # --- Input handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        snake.set_direction(UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        snake.set_direction(DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        snake.set_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        snake.set_direction(RIGHT)
                else:
                    if event.key == pygame.K_r:
                        snake, food, score, game_over = reset_game()

        # --- Update ---
        if not game_over:
            snake.move()

            # Collisions
            if snake.hits_wall() or snake.hits_self():
                game_over = True

            # Eat food
            if snake.head == food.position:
                snake.grow(1)
                score += 1
                food.respawn(snake.positions_set)

        # --- Render ---
        screen.fill(BG_COLOR)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        draw_text(screen, f"Score: {score}", (10, 8), font_small)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            msg1 = "Game Over"
            msg2 = "Press R to Restart or ESC to Quit"
            t1 = font_big.render(msg1, True, TEXT_COLOR)
            t2 = font_small.render(msg2, True, TEXT_COLOR)
            screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 2 - 24))
            screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 8))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
