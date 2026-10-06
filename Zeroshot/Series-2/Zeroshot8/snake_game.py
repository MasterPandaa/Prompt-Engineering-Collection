import sys
import random
import pygame

# Game constants
WIDTH, HEIGHT = 600, 400
TILE_SIZE = 20
GRID_COLS = WIDTH // TILE_SIZE
GRID_ROWS = HEIGHT // TILE_SIZE
FPS = 12  # Snake speed (tiles per second)

# Colors
BLACK = (0, 0, 0)
DARK_GREY = (30, 30, 30)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 30, 30)


class Snake:
    def __init__(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        # Start with 3 segments centered
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir = (1, 0)  # moving right
        self.grow_pending = 0

    def head(self):
        return self.body[0]

    def set_direction(self, new_dir):
        # Prevent reversing direction directly
        cur_dx, cur_dy = self.dir
        new_dx, new_dy = new_dir
        if (cur_dx == -new_dx and cur_dx != 0) or (cur_dy == -new_dy and cur_dy != 0):
            return
        # Ignore zero direction
        if new_dx == 0 and new_dy == 0:
            return
        self.dir = new_dir

    def move(self):
        hx, hy = self.head()
        dx, dy = self.dir
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def collided_with_self(self):
        return self.head() in self.body[1:]

    def collided_with_wall(self):
        x, y = self.head()
        return x < 0 or x >= GRID_COLS or y < 0 or y >= GRID_ROWS


class Food:
    def __init__(self, snake_body):
        self.pos = self._random_pos(snake_body)

    def _random_pos(self, snake_body):
        available = [(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS) if (x, y) not in snake_body]
        return random.choice(available) if available else None

    def respawn(self, snake_body):
        self.pos = self._random_pos(snake_body)


def draw_grid(surface):
    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(surface, DARK_GREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, DARK_GREY, (0, y), (WIDTH, y))


def draw_snake(surface, snake):
    for i, (x, y) in enumerate(snake.body):
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_food(surface, food):
    if food.pos is None:
        return
    x, y = food.pos
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(surface, RED, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def draw_score(surface, score, font):
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 10))


def draw_game_over(surface, score, font, font_small):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    msg = font.render("Game Over", True, WHITE)
    msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    surface.blit(msg, msg_rect)

    score_msg = font_small.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    surface.blit(score_msg, score_rect)

    info = font_small.render("Press R to Restart or ESC to Quit", True, WHITE)
    info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    surface.blit(info, info_rect)


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 32)
    font_big = pygame.font.SysFont(None, 64)

    def new_game():
        return Snake(), Food([]), 0, False

    snake, food, score, game_over = new_game()

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over:
                    if event.key == pygame.K_UP:
                        snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction((1, 0))
                else:
                    if event.key == pygame.K_r:
                        snake, food, score, game_over = new_game()

        if not game_over:
            # Continuous movement
            snake.move()

            # Check food collision
            if snake.head() == food.pos:
                snake.grow(1)
                score += 1
                food.respawn(snake.body)

            # Check collisions
            if snake.collided_with_wall() or snake.collided_with_self():
                game_over = True

        # Rendering
        screen.fill(BLACK)
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)
        draw_score(screen, score, font)
        if game_over:
            draw_game_over(screen, score, font_big, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
