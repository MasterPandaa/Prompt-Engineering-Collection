import sys
import random
from typing import List, Tuple, Set

import pygame

# Game configuration
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20  # size of each grid cell in pixels
COLUMNS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE

# Colors
COLOR_BG = (18, 18, 18)
COLOR_GRID = (28, 28, 28)
COLOR_SNAKE = (80, 200, 120)
COLOR_SNAKE_HEAD = (100, 230, 150)
COLOR_FOOD = (235, 64, 52)
COLOR_TEXT = (230, 230, 230)
COLOR_GAME_OVER = (255, 100, 100)

# Game speed (frames per second)
FPS = 12

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    """Encapsulates snake state, movement, growth, and collision checks."""

    def __init__(self, start_pos: Tuple[int, int]):
        # Body is a list of (x, y) grid positions, head at index 0
        self.body: List[Tuple[int, int]] = [start_pos, (start_pos[0] - 1, start_pos[1])]
        self.direction: Tuple[int, int] = RIGHT
        self._pending_growth = 0
        self._next_direction = self.direction  # buffer to apply direction changes once per tick

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Set next direction if it isn't directly opposite of current direction."""
        if not self._is_opposite(new_dir, self.direction):
            self._next_direction = new_dir

    def move(self) -> None:
        """Advance the snake by one cell, applying growth when needed."""
        # apply buffered direction exactly once per tick
        self.direction = self._next_direction
        new_head = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()  # remove tail segment if not growing

    def grow(self, n: int = 1) -> None:
        self._pending_growth += max(1, n)

    def hits_wall(self) -> bool:
        x, y = self.head
        return x < 0 or x >= COLUMNS or y < 0 or y >= ROWS

    def hits_self(self) -> bool:
        return self.head in self.body[1:]

    def occupies(self) -> Set[Tuple[int, int]]:
        return set(self.body)

    @staticmethod
    def _is_opposite(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        return a[0] == -b[0] and a[1] == -b[1]


class Food:
    """Manages food position and efficient respawn excluding snake cells."""

    def __init__(self, snake_cells: Set[Tuple[int, int]]):
        self.pos: Tuple[int, int] = self._random_free_cell(snake_cells)

    def respawn(self, snake_cells: Set[Tuple[int, int]]):
        self.pos = self._random_free_cell(snake_cells)

    @staticmethod
    def _random_free_cell(occupied: Set[Tuple[int, int]]) -> Tuple[int, int]:
        # Efficient selection from available free cells without repeated retries
        all_cells = [(x, y) for x in range(COLUMNS) for y in range(ROWS)]
        # If snake covers most of the board, computing free_cells once is optimal
        free_cells = [c for c in all_cells if c not in occupied]
        if not free_cells:
            # Board full, fallback to (0,0) to avoid crash, game will be won
            return (0, 0)
        return random.choice(free_cells)


def draw_grid(surface: pygame.Surface) -> None:
    # Subtle grid to help player gauge positions
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1)


def draw_rect_cell(surface: pygame.Surface, color: Tuple[int, int, int], cell: Tuple[int, int]):
    x, y = cell
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, color, rect)


def render_text(surface: pygame.Surface, text: str, size: int, color: Tuple[int, int, int], center: Tuple[int, int]):
    font = pygame.font.SysFont("consolas,arial,dejavusans", size, bold=True)
    label = font.render(text, True, color)
    rect = label.get_rect(center=center)
    surface.blit(label, rect)


def game_loop():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    def start_new_game():
        start = (COLUMNS // 4, ROWS // 2)
        snake = Snake(start)
        food = Food(snake.occupies())
        score = 0
        return snake, food, score

    snake, food, score = start_new_game()
    running = True
    game_over = False

    while running:
        # Event handling
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
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        snake, food, score = start_new_game()
                        game_over = False

        if not game_over:
            # Update
            snake.move()

            # Check collisions
            if snake.hits_wall() or snake.hits_self():
                game_over = True

            # Food consumption
            if snake.head == food.pos:
                snake.grow(1)
                score += 1
                food.respawn(snake.occupies())

        # Draw
        screen.fill(COLOR_BG)
        draw_grid(screen)

        # Draw food
        draw_rect_cell(screen, COLOR_FOOD, food.pos)

        # Draw snake
        if snake.body:
            draw_rect_cell(screen, COLOR_SNAKE_HEAD, snake.head)
            for segment in snake.body[1:]:
                draw_rect_cell(screen, COLOR_SNAKE, segment)

        # HUD
        render_text(screen, f"Score: {score}", 20, COLOR_TEXT, (70, 18))

        if game_over:
            render_text(screen, "GAME OVER", 36, COLOR_GAME_OVER, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            render_text(screen, "Press Enter or R to Restart", 20, COLOR_TEXT, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 16))
            render_text(screen, "Esc to Quit", 18, (180, 180, 180), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 42))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
