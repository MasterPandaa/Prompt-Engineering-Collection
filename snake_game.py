import sys
import random
import pygame

# ===============================
# Game Configuration
# ===============================
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20  # Each cell is GRID_SIZE x GRID_SIZE
FPS = 12  # Snake speed (frames per second)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
RED = (220, 50, 50)
GRAY = (40, 40, 40)

# Directions as (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def grid_aligned_randpos(occupied):
    """
    Return a random (x, y) aligned to GRID_SIZE and not overlapping with occupied set.
    occupied: set of (x, y) tuples representing pixels positions already taken (snake body)
    """
    cells_x = WIDTH // GRID_SIZE
    cells_y = HEIGHT // GRID_SIZE
    free_cells = [(cx * GRID_SIZE, cy * GRID_SIZE)
                  for cx in range(cells_x)
                  for cy in range(cells_y)
                  if (cx * GRID_SIZE, cy * GRID_SIZE) not in occupied]
    if not free_cells:
        # No free cells (should only happen if snake fills the board)
        return None
    return random.choice(free_cells)


class Snake:
    def __init__(self):
        # Start from center, with length 3 heading to the right
        start_x = WIDTH // 2 // GRID_SIZE * GRID_SIZE
        start_y = HEIGHT // 2 // GRID_SIZE * GRID_SIZE
        self.body = [
            (start_x, start_y),
            (start_x - GRID_SIZE, start_y),
            (start_x - 2 * GRID_SIZE, start_y)
        ]
        self.direction = RIGHT
        self.pending_dir = RIGHT  # store last input dir to apply on next move
        self.grow_segments = 0

    def set_direction(self, new_dir):
        # Prevent reversing directly
        opposite = (self.direction[0] * -1, self.direction[1] * -1)
        if new_dir != opposite and new_dir != self.direction:
            self.pending_dir = new_dir

    def move(self):
        # Apply any pending direction change at the start of move
        self.direction = self.pending_dir
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)
        self.body.insert(0, new_head)
        if self.grow_segments > 0:
            self.grow_segments -= 1
        else:
            self.body.pop()  # remove tail

    def grow(self, segments=1):
        self.grow_segments += segments

    def hits_wall(self):
        x, y = self.body[0]
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT

    def hits_self(self):
        head = self.body[0]
        return head in self.body[1:]

    def head_position(self):
        return self.body[0]

    def body_set(self):
        return set(self.body)


class Food:
    def __init__(self, snake_body_set):
        self.position = grid_aligned_randpos(snake_body_set)

    def respawn(self, snake_body_set):
        self.position = grid_aligned_randpos(snake_body_set)


def draw_grid(surface):
    # Optional subtle grid lines for visual aid
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)


def draw_snake(surface, snake: Snake):
    for i, (x, y) in enumerate(snake.body):
        color = DARK_GREEN if i == 0 else GREEN
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)  # outline


def draw_food(surface, food: Food):
    if food.position is None:
        return
    x, y = food.position
    rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, RED, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def render_text(surface, text, size, color, center):
    font = pygame.font.SysFont("arial", size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_score(surface, score):
    font = pygame.font.SysFont("arial", 20)
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 8))


def game_over_screen(surface, score):
    surface.fill(BLACK)
    render_text(surface, "GAME OVER", 48, RED, (WIDTH // 2, HEIGHT // 2 - 30))
    render_text(surface, f"Final Score: {score}", 30, WHITE, (WIDTH // 2, HEIGHT // 2 + 10))
    render_text(surface, "Press R to Restart or ESC to Quit", 20, WHITE, (WIDTH // 2, HEIGHT // 2 + 45))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    waiting = False


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    while True:
        # Initialize a new game
        snake = Snake()
        food = Food(snake.body_set())
        score = 0

        running = True
        while running:
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction(RIGHT)

            # Update game state
            snake.move()

            # Check collisions
            if snake.hits_wall() or snake.hits_self():
                running = False
                break

            # Check food consumption
            if food.position is not None and snake.head_position() == food.position:
                snake.grow(1)
                score += 1
                food.respawn(snake.body_set())

            # Draw
            screen.fill(BLACK)
            draw_grid(screen)
            draw_snake(screen, snake)
            draw_food(screen, food)
            draw_score(screen, score)

            pygame.display.flip()
            clock.tick(FPS)

        # Game Over
        game_over_screen(screen, score)


if __name__ == "__main__":
    main()
