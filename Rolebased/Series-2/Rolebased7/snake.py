import pygame
import random
from typing import List, Tuple, Deque, Set
from collections import deque

# --- Constants ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE  # 30
GRID_ROWS = HEIGHT // CELL_SIZE  # 20
MOVE_INTERVAL_MS = 120  # movement tick for consistent speed

# Colors
BG_COLOR = (24, 24, 24)
SNAKE_HEAD_COLOR = (80, 200, 120)
SNAKE_BODY_COLOR = (50, 160, 100)
FOOD_COLOR = (220, 90, 90)
GRID_COLOR = (40, 40, 40)
TEXT_COLOR = (230, 230, 230)

# Directions as (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class Food:
    """Handles food position and respawn logic on a discrete grid."""

    def __init__(self, snake_body: Set[Tuple[int, int]]):
        self.pos = self._random_free_cell(snake_body)

    def _random_free_cell(self, occupied: Set[Tuple[int, int]]) -> Tuple[int, int]:
        # Efficient placement: choose uniformly from free cells
        all_cells = [(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)]
        if occupied:
            # If the board is almost full, this remains efficient
            free_cells = [c for c in all_cells if c not in occupied]
        else:
            free_cells = all_cells
        if not free_cells:
            return (-1, -1)  # indicates no space (win condition)
        return random.choice(free_cells)

    def respawn(self, snake_body: Set[Tuple[int, int]]):
        self.pos = self._random_free_cell(snake_body)


class Snake:
    """Snake represented as deque of grid cells. Head at index 0."""

    def __init__(self):
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        self.segments: Deque[Tuple[int, int]] = deque(
            [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        )
        self.direction: Tuple[int, int] = RIGHT
        self._grow_on_next_move = False

    @property
    def head(self) -> Tuple[int, int]:
        return self.segments[0]

    def set_direction(self, new_dir: Tuple[int, int]):
        # Guard: prevent reversing directly into itself
        if new_dir == OPPOSITE[self.direction]:
            return
        self.direction = new_dir

    def occupies(self) -> Set[Tuple[int, int]]:
        return set(self.segments)

    def move(self):
        hx, hy = self.head
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.segments.appendleft(new_head)
        if self._grow_on_next_move:
            self._grow_on_next_move = False
        else:
            self.segments.pop()

    def grow(self):
        self._grow_on_next_move = True

    def collided_with_self(self) -> bool:
        return self.head in list(self.segments)[1:]

    def collided_with_wall(self) -> bool:
        x, y = self.head
        return not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        self.reset()

        # Use a timer event for movement to keep speed consistent
        self.MOVE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MOVE_EVENT, MOVE_INTERVAL_MS)

    def reset(self):
        self.snake = Snake()
        self.food = Food(self.snake.occupies())
        self.pending_dir = self.snake.direction  # buffer next direction for responsive control
        self.running = True
        self.game_over = False
        self.score = 0

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                return

            if event.key == pygame.K_UP:
                self._set_pending_dir(UP)
            elif event.key == pygame.K_DOWN:
                self._set_pending_dir(DOWN)
            elif event.key == pygame.K_LEFT:
                self._set_pending_dir(LEFT)
            elif event.key == pygame.K_RIGHT:
                self._set_pending_dir(RIGHT)

        elif event.type == pygame.QUIT:
            self.running = False

    def _set_pending_dir(self, new_dir: Tuple[int, int]):
        # Guard twice: against current and against pending to avoid mid-tick reverse chains
        curr = self.snake.direction
        if new_dir == OPPOSITE[curr]:
            return
        if new_dir == OPPOSITE.get(self.pending_dir, curr):
            return
        self.pending_dir = new_dir

    def update(self):
        if self.game_over:
            return
        # Apply pending direction at movement tick
        self.snake.set_direction(self.pending_dir)
        self.snake.move()

        # Check collisions
        if self.snake.collided_with_wall() or self.snake.collided_with_self():
            self.game_over = True
            return

        # Food consumption
        if self.snake.head == self.food.pos:
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.occupies())
            # Win condition: no spot to place new food
            if self.food.pos == (-1, -1):
                self.game_over = True

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.segments):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(self.screen, color, rect)

    def draw_food(self):
        if self.food.pos != (-1, -1):
            x, y = self.food.pos
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, FOOD_COLOR, rect)

    def draw_hud(self):
        text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(text, (8, 6))

        if self.game_over:
            title = self.font.render("Game Over", True, TEXT_COLOR)
            hint = self.font.render("Press R/Enter/Space to Restart, Esc to Quit", True, TEXT_COLOR)
            tw = title.get_width()
            hw = hint.get_width()
            self.screen.blit(title, ((WIDTH - tw) // 2, HEIGHT // 2 - 20))
            self.screen.blit(hint, ((WIDTH - hw) // 2, HEIGHT // 2 + 6))

    def render(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == self.MOVE_EVENT and not self.game_over:
                    self.update()
                else:
                    self.handle_input(event)

            self.render()
            self.clock.tick(60)  # smooth rendering

        pygame.quit()


if __name__ == "__main__":
    Game().run()
