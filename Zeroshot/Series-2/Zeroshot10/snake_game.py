import sys
import random
import pygame

# -----------------------------
# Konstanta Game
# -----------------------------
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20  # ukuran sel grid agar gerakan ular halus dan sejajar
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
DARK_GREEN = (25, 120, 52)
RED = (200, 30, 30)
GREY = (50, 50, 50)

# Arah
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Kecepatan game (tick per detik)
SNAKE_SPEED = 12


def draw_grid(surface):
    # Garis grid halus (opsional untuk estetika)
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GREY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GREY, (0, y), (WIDTH, y), 1)


class Snake:
    def __init__(self):
        # Mulai dari tengah grid
        cx = GRID_WIDTH // 2
        cy = GRID_HEIGHT // 2
        self.positions = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # kepala di index 0
        self.direction = RIGHT
        self.grow_pending = 0

    @property
    def head(self):
        return self.positions[0]

    def set_direction(self, new_dir):
        # Cegah pembalikan arah langsung
        if (new_dir[0] * -1, new_dir[1] * -1) == self.direction:
            return
        # Abaikan jika arah sama untuk menghindari input tidak perlu
        if new_dir == self.direction:
            return
        self.direction = new_dir

    def move(self):
        x, y = self.head
        dx, dy = self.direction
        new_head = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
        # Kita akan cek tabrak dinding secara eksplisit di luar (tanpa wrap). Jadi jangan mod %.
        new_head = (x + dx, y + dy)

        # Tabrak dinding?
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            raise RuntimeError("hit_wall")

        # Tabrak badan sendiri?
        if new_head in self.positions:
            raise RuntimeError("hit_self")

        # Update posisi
        self.positions.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def draw(self, surface):
        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = DARK_GREEN if i == 0 else GREEN
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)


class Food:
    def __init__(self, snake_positions):
        self.position = self.random_position(snake_positions)

    def random_position(self, snake_positions):
        # Pilih sel acak yang tidak ditempati ular
        empty_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                       if (x, y) not in snake_positions]
        if not empty_cells:
            return None
        return random.choice(empty_cells)

    def respawn(self, snake_positions):
        self.position = self.random_position(snake_positions)

    def draw(self, surface):
        if self.position is None:
            return
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_text(surface, text, font, color, pos):
    rendered = font.render(text, True, color)
    surface.blit(rendered, pos)


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("consolas", 18)
    font_big = pygame.font.SysFont("consolas", 28, bold=True)

    def run_game():
        snake = Snake()
        food = Food(snake.positions)
        score = 0
        running = True
        while running:
            # Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
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
            try:
                snake.move()
            except RuntimeError as e:
                if str(e) in ("hit_wall", "hit_self"):
                    return score  # game over, kembalikan skor untuk ditampilkan
                else:
                    raise

            # Makan?
            if food.position is not None and snake.head == food.position:
                snake.grow(1)
                score += 1
                food.respawn(snake.positions)

            # Render
            screen.fill(WHITE)
            # draw_grid(screen)  # aktifkan jika ingin grid terlihat
            snake.draw(screen)
            food.draw(screen)

            draw_text(screen, f"Score: {score}", font_small, BLACK, (10, 8))

            pygame.display.flip()
            clock.tick(SNAKE_SPEED)

    # Loop utama dengan layar Game Over dan Restart
    while True:
        last_score = run_game()
        # Layar Game Over
        screen.fill(WHITE)
        msg1 = "Game Over"
        msg2 = f"Score: {last_score}"
        msg3 = "Press ENTER to play again or ESC to quit"

        # Posisikan teks di tengah
        text1 = font_big.render(msg1, True, BLACK)
        text2 = font_big.render(msg2, True, BLACK)
        text3 = font_small.render(msg3, True, BLACK)

        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 70))
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
            clock.tick(30)


if __name__ == "__main__":
    main()
