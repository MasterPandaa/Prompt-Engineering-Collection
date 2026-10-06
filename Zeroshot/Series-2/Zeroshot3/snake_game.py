import pygame
import sys
import random

# Game configuration
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
BLOCK_SIZE = 20  # Grid size for snake and food alignment
FPS = 12         # Snake speed (frames per second)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
GRAY = (30, 30, 30)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def random_food_position():
    cols = WINDOW_WIDTH // BLOCK_SIZE
    rows = WINDOW_HEIGHT // BLOCK_SIZE
    x = random.randint(0, cols - 1) * BLOCK_SIZE
    y = random.randint(0, rows - 1) * BLOCK_SIZE
    return x, y


def draw_grid(surface):
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WINDOW_WIDTH, y), 1)


def show_text(surface, text, size, color, center):
    font = pygame.font.SysFont("consolas", size)
    render = font.render(text, True, color)
    rect = render.get_rect(center=center)
    surface.blit(render, rect)


def show_score(surface, score):
    font = pygame.font.SysFont("consolas", 20)
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 8))


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Classic (Pygame)")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Initial snake in the center
    start_x = WINDOW_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    start_y = WINDOW_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    current_direction = RIGHT
    next_direction = RIGHT

    food_pos = random_food_position()
    while food_pos in snake:
        food_pos = random_food_position()

    score = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key == pygame.K_UP and current_direction != DOWN:
                        next_direction = UP
                    elif event.key == pygame.K_DOWN and current_direction != UP:
                        next_direction = DOWN
                    elif event.key == pygame.K_LEFT and current_direction != RIGHT:
                        next_direction = LEFT
                    elif event.key == pygame.K_RIGHT and current_direction != LEFT:
                        next_direction = RIGHT
                else:
                    # When game over, allow R to restart or Q to quit
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        # Restart
                        return main()
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False

        if not game_over:
            # Move snake
            current_direction = next_direction
            head_x, head_y = snake[0]
            dx, dy = current_direction
            new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

            # Check collisions with walls
            if (
                new_head[0] < 0
                or new_head[0] >= WINDOW_WIDTH
                or new_head[1] < 0
                or new_head[1] >= WINDOW_HEIGHT
            ):
                game_over = True
            # Check collisions with self
            elif new_head in snake:
                game_over = True
            else:
                snake.insert(0, new_head)
                # Check if food eaten
                if new_head == food_pos:
                    score += 1
                    # Place new food not on snake
                    food_pos = random_food_position()
                    while food_pos in snake:
                        food_pos = random_food_position()
                else:
                    snake.pop()  # remove tail

        # Drawing
        screen.fill(BLACK)
        draw_grid(screen)

        # Draw food
        fx, fy = food_pos
        pygame.draw.rect(screen, RED, (fx, fy, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, DARK_RED, (fx, fy, BLOCK_SIZE, BLOCK_SIZE), 2)

        # Draw snake
        for i, (x, y) in enumerate(snake):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)

        show_score(screen, score)

        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            show_text(screen, "GAME OVER", 40, WHITE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            show_text(screen, f"Score: {score}", 28, WHITE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
            show_text(screen, "Press R/Enter to Restart or Q/Esc to Quit", 18, WHITE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
