import sys
import random
import pygame

# Game constants
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 12

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 30, 30)
GREEN = (30, 200, 60)
DARK_GREEN = (20, 120, 40)
GRAY = (40, 40, 40)

# Directions (dx, dy) in grid units
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def draw_text(surface, text, size, color, x, y, center=False):
    font = pygame.font.SysFont("consolas", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


class Snake:
    def __init__(self):
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        # Start moving to the right with length 3
        self.direction = RIGHT
        self.segments = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.grow_pending = 0

    def head(self):
        return self.segments[0]

    def set_direction(self, new_dir):
        # Prevent reversing direction
        if (self.direction[0] + new_dir[0] == 0) and (self.direction[1] + new_dir[1] == 0):
            return  # ignore reverse
        self.direction = new_dir

    def move(self):
        hx, hy = self.head()
        nx, ny = hx + self.direction[0], hy + self.direction[1]
        self.segments.insert(0, (nx, ny))
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def hit_wall(self):
        x, y = self.head()
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def hit_self(self):
        return self.head() in self.segments[1:]


def random_food_position(exclude_cells):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude_cells:
            return pos


def draw_cell(surface, pos, color):
    x, y = pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)


def draw_grid(surface):
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))


def game_over_screen(screen, clock, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    draw_text(screen, "GAME OVER", 48, WHITE, WIDTH // 2, HEIGHT // 2 - 40, center=True)
    draw_text(screen, f"Score: {score}", 32, WHITE, WIDTH // 2, HEIGHT // 2 + 5, center=True)
    draw_text(screen, "Press Enter to restart or Esc to quit", 20, WHITE, WIDTH // 2, HEIGHT // 2 + 40, center=True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(30)


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    while True:
        # Initialize game state
        snake = Snake()
        food = random_food_position(set(snake.segments))
        score = 0
        running = True

        while running:
            # Input handling
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

            # Update
            snake.move()

            # Check collisions
            if snake.hit_wall() or snake.hit_self():
                running = False
                break

            if snake.head() == food:
                snake.grow(1)
                score += 1
                food = random_food_position(set(snake.segments))

            # Draw
            screen.fill(BLACK)
            # Optional: grid lines for visual clarity
            # draw_grid(screen)

            # Draw food and snake
            draw_cell(screen, food, RED)
            for i, seg in enumerate(snake.segments):
                color = DARK_GREEN if i == 0 else GREEN
                draw_cell(screen, seg, color)

            # Draw score
            draw_text(screen, f"Score: {score}", 20, WHITE, 8, 6, center=False)

            pygame.display.flip()
            clock.tick(FPS)

        # Game over screen (restart or quit)
        game_over_screen(screen, clock, score)


if __name__ == "__main__":
    main()
