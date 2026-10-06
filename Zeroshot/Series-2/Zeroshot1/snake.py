import sys
import random
import pygame

# Game configuration
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE
GRID_ROWS = HEIGHT // CELL_SIZE
FPS = 12  # Snake speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
RED = (220, 30, 30)
GREY = (40, 40, 40)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def grid_to_px(cell):
    """Convert grid position (col,row) to pixel rect (x,y,w,h)."""
    return (cell[0] * CELL_SIZE, cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def random_food_position(snake):
    """Return a random grid position not occupied by the snake."""
    empty_cells = [
        (x, y)
        for x in range(GRID_COLS)
        for y in range(GRID_ROWS)
        if (x, y) not in snake
    ]
    if not empty_cells:
        return None
    return random.choice(empty_cells)


def draw_grid(surface):
    """Optional: draw subtle grid lines for visual guidance."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GREY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GREY, (0, y), (WIDTH, y), 1)


def draw_snake(surface, snake):
    for i, segment in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(surface, color, grid_to_px(segment))


def draw_food(surface, food_pos):
    if food_pos is not None:
        pygame.draw.rect(surface, RED, grid_to_px(food_pos))


def draw_score(surface, font, score):
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (8, 8))


def next_direction(current_dir, queued_dir):
    """Apply queued_dir if it isn't a 180-degree reversal."""
    if queued_dir is None:
        return current_dir
    if (current_dir[0] + queued_dir[0] == 0) and (current_dir[1] + queued_dir[1] == 0):
        # It's a reversal; ignore
        return current_dir
    return queued_dir


def update_snake(snake, direction, grow=False):
    """Move the snake by adding a new head in direction. Optionally grow (no tail pop)."""
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    # Return new snake list
    new_snake = [new_head] + snake
    if not grow:
        new_snake.pop()
    return new_snake


def check_collisions(snake):
    """Check collisions with walls and self. Returns (hit_wall, hit_self)."""
    head_x, head_y = snake[0]

    hit_wall = not (0 <= head_x < GRID_COLS and 0 <= head_y < GRID_ROWS)
    hit_self = snake[0] in snake[1:]
    return hit_wall, hit_self


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 48)

    # Initialize snake centered
    start_col = GRID_COLS // 2
    start_row = GRID_ROWS // 2
    snake = [
        (start_col, start_row),
        (start_col - 1, start_row),
        (start_col - 2, start_row),
    ]
    direction = RIGHT
    queued_dir = None

    food = random_food_position(snake)
    score = 0

    game_over = False

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    queued_dir = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    queued_dir = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    queued_dir = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    queued_dir = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif event.key == pygame.K_RETURN and game_over:
                    # Restart game
                    start_col = GRID_COLS // 2
                    start_row = GRID_ROWS // 2
                    snake = [
                        (start_col, start_row),
                        (start_col - 1, start_row),
                        (start_col - 2, start_row),
                    ]
                    direction = RIGHT
                    queued_dir = None
                    food = random_food_position(snake)
                    score = 0
                    game_over = False

        if not game_over:
            # Apply input turning rules (no reversal)
            direction = next_direction(direction, queued_dir)
            queued_dir = None

            # Compute next head position
            head_x, head_y = snake[0]
            dx, dy = direction
            next_head = (head_x + dx, head_y + dy)

            # Check collisions against walls and self
            hit_wall = not (0 <= next_head[0] < GRID_COLS and 0 <= next_head[1] < GRID_ROWS)
            hit_self = next_head in snake

            if hit_wall or hit_self:
                game_over = True
            else:
                # Handle eating and growth without double-moving
                if food is not None and next_head == food:
                    score += 1
                    snake = [next_head] + snake  # grow: keep tail
                    food = random_food_position(snake)
                else:
                    snake = [next_head] + snake[:-1]

        # Drawing
        screen.fill(BLACK)
        # draw_grid(screen)  # uncomment to show grid lines
        draw_food(screen, food)
        draw_snake(screen, snake)
        draw_score(screen, font, score)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            game_over_text = big_font.render("GAME OVER", True, WHITE)
            hint_text = font.render("Press Enter to Restart or Esc to Quit", True, WHITE)
            rect1 = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            rect2 = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(game_over_text, rect1)
            screen.blit(hint_text, rect2)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
