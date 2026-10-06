import pygame
import random
import sys

# Game configuration
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_COLS = WIDTH // CELL_SIZE
GRID_ROWS = HEIGHT // CELL_SIZE
SNAKE_SPEED = 12  # frames per second

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
RED = (220, 50, 50)
GRAY = (40, 40, 40)

# Directions as (dx, dy) in grid steps
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def grid_to_pixels(cell):
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE


def random_empty_cell(occupied):
    """Return a random grid cell that is not in occupied set."""
    while True:
        cell = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
        if cell not in occupied:
            return cell


def init_snake():
    """Initialize snake centered horizontally and vertically on grid."""
    cx = GRID_COLS // 2
    cy = GRID_ROWS // 2
    # Start moving to the right, with 3 initial segments
    snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
    direction = RIGHT
    return snake, direction


def draw_grid(surface):
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)


def draw_snake(surface, snake):
    for i, (sx, sy) in enumerate(snake):
        rect = pygame.Rect(sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_food(surface, food):
    fx, fy = food
    rect = pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, RED, rect)


def draw_score(surface, font, score):
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 8))


def is_opposite(dir_a, dir_b):
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


def handle_input(pending_direction, current_direction):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            elif event.key == pygame.K_UP:
                if not is_opposite(UP, current_direction):
                    pending_direction = UP
            elif event.key == pygame.K_DOWN:
                if not is_opposite(DOWN, current_direction):
                    pending_direction = DOWN
            elif event.key == pygame.K_LEFT:
                if not is_opposite(LEFT, current_direction):
                    pending_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                if not is_opposite(RIGHT, current_direction):
                    pending_direction = RIGHT
    return pending_direction


def step_snake(snake, direction, grow=False):
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)
    # Insert new head
    snake.insert(0, new_head)
    # Remove tail unless growing
    if not grow:
        snake.pop()
    return new_head


def check_collision(head, snake):
    hx, hy = head
    # Wall collision
    if hx < 0 or hx >= GRID_COLS or hy < 0 or hy >= GRID_ROWS:
        return True
    # Self collision (ignore head at index 0)
    if head in snake[1:]:
        return True
    return False


def game_over_screen(screen, font_large, font_small, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    msg = font_large.render("GAME OVER", True, WHITE)
    msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(msg, msg_rect)

    score_msg = font_small.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    screen.blit(score_msg, score_rect)

    hint = font_small.render("Press R to Restart or ESC to Quit", True, WHITE)
    hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(hint, hint_rect)

    pygame.display.flip()

    # Wait for user decision
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    return  # restart


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 24)
    font_large = pygame.font.SysFont(None, 48)

    while True:
        # Initialize a new game round
        snake, direction = init_snake()
        pending_direction = direction
        score = 0
        occupied = set(snake)
        food = random_empty_cell(occupied)

        running = True
        while running:
            clock.tick(SNAKE_SPEED)

            # Input
            pending_direction = handle_input(pending_direction, direction)
            # Apply direction change if not reversing into the immediate next cell
            if not is_opposite(pending_direction, direction):
                direction = pending_direction

            # Update
            grow = False
            next_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if next_head == food:
                grow = True
                score += 1
                occupied = set(snake)  # occupied before growth
                # Spawn new food excluding next head position (since it will be occupied)
                occupied.add(next_head)
                food = random_empty_cell(occupied)

            new_head = step_snake(snake, direction, grow=grow)

            # Collision
            if check_collision(new_head, snake):
                # Draw final state before game over screen
                screen.fill(BLACK)
                draw_snake(screen, snake)
                draw_food(screen, food)
                draw_score(screen, font_small, score)
                pygame.display.flip()
                game_over_screen(screen, font_large, font_small, score)
                running = False
                break

            # Render
            screen.fill(BLACK)
            # Optional: draw grid for aesthetics
            # draw_grid(screen)
            draw_snake(screen, snake)
            draw_food(screen, food)
            draw_score(screen, font_small, score)

            pygame.display.flip()


if __name__ == "__main__":
    main()
