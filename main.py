import sys
import random
from typing import List, Tuple, Set

import pygame

# --- Configuration ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE  # 30
GRID_ROWS = HEIGHT // CELL_SIZE  # 20
BACKGROUND_COLOR = (24, 26, 27)  # dark background
SNAKE_COLOR = (80, 200, 120)
SNAKE_HEAD_COLOR = (60, 180, 100)
FOOD_COLOR = (220, 80, 80)
GRID_COLOR = (40, 42, 45)
TEXT_COLOR = (220, 220, 220)

# Movement timer interval in milliseconds
STEP_INTERVAL_MS = 110

# Directions: (dx, dy) on grid
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def add_pos(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return a[0] + b[0], a[1] + b[1]


def opposite(d1: Tuple[int, int], d2: Tuple[int, int]) -> bool:
    return d1[0] == -d2[0] and d1[1] == -d2[1]


class Snake:
    def __init__(self, init_pos: Tuple[int, int]) -> None:
        # body is a list of grid positions, head at index 0
        self.body: List[Tuple[int, int]] = [
            init_pos,
            (init_pos[0] - 1, init_pos[1]),
            (init_pos[0] - 2, init_pos[1]),
        ]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Tuple[int, int] = RIGHT  # buffered from input
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        # Guard: prevent reversing into itself
        if opposite(new_dir, self.direction):
            return
        # Save as next_direction to apply on the next step for stable input handling
        self.next_direction = new_dir

    def step(self) -> None:
        # apply buffered direction (still ensuring no instant reverse)
        if not opposite(self.next_direction, self.direction):
            self.direction = self.next_direction

        new_head = add_pos(self.body[0], self.direction)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()  # remove tail if not growing

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def occupies(self) -> Set[Tuple[int, int]]:
        return set(self.body)

    def collided_with_walls(self) -> bool:
        hx, hy = self.head()
        return not (0 <= hx < GRID_COLS and 0 <= hy < GRID_ROWS)

    def collided_with_self(self) -> bool:
        return self.head() in self.body[1:]

    def draw(self, surface: pygame.Surface) -> None:
        # draw head with slightly different color
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            pygame.draw.rect(surface, color, rect)


class Food:
    def __init__(self) -> None:
        self.pos: Tuple[int, int] = (0, 0)

    def respawn(self, forbidden: Set[Tuple[int, int]]) -> None:
        # Efficient placement: choose from remaining free cells
        total_cells = GRID_COLS * GRID_ROWS
        if len(forbidden) >= total_cells:
            # no place to spawn (snake filled board)
            return
        while True:
            x = random.randrange(GRID_COLS)
            y = random.randrange(GRID_ROWS)
            if (x, y) not in forbidden:
                self.pos = (x, y)
                return

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.pos
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect)


def draw_grid(surface: pygame.Surface) -> None:
    # Light grid lines for visual alignment
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))


def reset_game() -> Tuple[Snake, Food, int]:
    snake = Snake(init_pos=(GRID_COLS // 2, GRID_ROWS // 2))
    food = Food()
    food.respawn(snake.occupies())
    score = 0
    return snake, food, score


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake (Pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, STEP_INTERVAL_MS)

    snake, food, score = reset_game()

    running = True
    while running:
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
            elif event.type == MOVE_EVENT:
                snake.step()

                # Collisions
                if snake.collided_with_walls() or snake.collided_with_self():
                    # reset game on collision
                    snake, food, score = reset_game()
                elif snake.head() == food.pos:
                    snake.grow(1)
                    score += 1
                    # respawn food avoiding snake
                    food.respawn(snake.occupies())

        # Drawing
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        food.draw(screen)
        snake.draw(screen)

        score_surf = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_surf, (10, 8))

        pygame.display.flip()
        # Keep a reasonable loop rate for input processing and rendering
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
