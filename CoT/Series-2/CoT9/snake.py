import pygame
import random
import sys

# ----------------------------
# Konfigurasi dasar
# ----------------------------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
FPS = 12

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 20, 60)
DARK_GREEN = (0, 160, 0)
GRAY = (40, 40, 40)

# Arah (dx, dy)
UP = (0, -BLOCK_SIZE)
DOWN = (0, BLOCK_SIZE)
LEFT = (-BLOCK_SIZE, 0)
RIGHT = (BLOCK_SIZE, 0)

def init_snake():
    # Posisi awal di tengah, disejajarkan ke grid
    start_x = WIDTH // 2
    start_y = HEIGHT // 2
    start_x -= start_x % BLOCK_SIZE
    start_y -= start_y % BLOCK_SIZE

    # Ular awal menghadap kanan, panjang 3
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = RIGHT
    return snake, direction

def spawn_food(snake):
    snake_set = set(snake)
    # Hitung jumlah sel grid
    cells_x = WIDTH // BLOCK_SIZE
    cells_y = HEIGHT // BLOCK_SIZE

    # Kumpulkan semua sel kosong
    free_cells = [
        (x * BLOCK_SIZE, y * BLOCK_SIZE)
        for x in range(cells_x)
        for y in range(cells_y)
        if (x * BLOCK_SIZE, y * BLOCK_SIZE) not in snake_set
    ]
    if not free_cells:
        return None  # Tidak ada tempat (menang)
    return random.choice(free_cells)

def is_opposite(dir_a, dir_b):
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]

def draw_grid(surface):
    # Opsional: grid visual
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)

def draw_snake(surface, snake):
    # Kepala dan tubuh berbeda warna agar jelas
    if snake:
        head = snake[0]
        pygame.draw.rect(surface, GREEN, (head[0], head[1], BLOCK_SIZE, BLOCK_SIZE))
    for segment in snake[1:]:
        pygame.draw.rect(surface, DARK_GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

def draw_food(surface, food_pos):
    if food_pos is not None:
        pygame.draw.rect(surface, RED, (food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

def render_text(surface, text, font, color, pos, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(img, rect)

def game_loop(screen, clock, font, big_font):
    snake, direction = init_snake()
    next_direction = direction
    food = spawn_food(snake)
    score = 0

    running = True
    while running:
        clock.tick(FPS)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if not is_opposite(next_direction, UP):
                        next_direction = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if not is_opposite(next_direction, DOWN):
                        next_direction = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if not is_opposite(next_direction, LEFT):
                        next_direction = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if not is_opposite(next_direction, RIGHT):
                        next_direction = RIGHT

        # Terapkan perubahan arah sekali per frame
        if not is_opposite(direction, next_direction):
            direction = next_direction

        # Hitung posisi kepala baru
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        # Deteksi tabrakan batas
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            return "game_over", score

        # Deteksi tabrakan diri (kecuali ekor karena bisa berpindah)
        if new_head in snake[:-1]:
            return "game_over", score

        # Update ular
        snake.insert(0, new_head)

        # Makan?
        if food is not None and new_head == food:
            score += 1
            food = spawn_food(snake)
            # Jika tidak ada ruang tersisa, pemain menang
            if food is None:
                return "win", score
        else:
            # Tidak makan: pindahkan ekor
            snake.pop()

        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)
        render_text(screen, f"Score: {score}", font, WHITE, (10, 8))
        pygame.display.flip()

def show_end_screen(screen, big_font, font, status, score):
    screen.fill(BLACK)
    if status == "win":
        title = "You Win! 🎉"
    else:
        title = "Game Over!"

    render_text(screen, title, big_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 40), center=True)
    render_text(screen, f"Score: {score}", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 10), center=True)
    render_text(screen, "Press Enter to Play Again, Esc to Quit", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 40), center=True)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    while True:
        result = game_loop(screen, clock, font, big_font)
        if result == "quit":
            break
        elif isinstance(result, tuple):
            status, score = result
            post = show_end_screen(screen, big_font, font, status, score)
            if post == "quit":
                break
            # else restart (loop kembali)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
