import pygame
import sys
import random

# -----------------------------
# Konfigurasi dasar
# -----------------------------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
SNAKE_SPEED = 12  # FPS

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 30, 30)
DARK_GRAY = (40, 40, 40)
YELLOW = (240, 220, 50)

# Arah grid (dx, dy)
DIRS = {
    "UP": (0, -BLOCK_SIZE),
    "DOWN": (0, BLOCK_SIZE),
    "LEFT": (-BLOCK_SIZE, 0),
    "RIGHT": (BLOCK_SIZE, 0),
}

def draw_grid(surface):
    # Garis grid opsional untuk visual
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (0, y), (WIDTH, y))


def render_text(surface, text, font, color, topleft):
    img = font.render(text, True, color)
    surface.blit(img, topleft)


def random_food_position(snake_set):
    # Bangun semua sel grid
    cols = WIDTH // BLOCK_SIZE
    rows = HEIGHT // BLOCK_SIZE
    all_cells = [(c * BLOCK_SIZE, r * BLOCK_SIZE) for r in range(rows) for c in range(cols)]
    # Filter yang bukan ular
    empties = [pos for pos in all_cells if pos not in snake_set]
    if not empties:
        return None  # Tidak ada tempat (menang penuh)
    return random.choice(empties)


def reset_game():
    # Inisialisasi ular di tengah, panjang 3, mengarah ke kanan
    start_x = (WIDTH // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    start_y = (HEIGHT // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    snake = [
        (start_x - 2 * BLOCK_SIZE, start_y),
        (start_x - 1 * BLOCK_SIZE, start_y),
        (start_x, start_y),
    ]
    direction = DIRS["RIGHT"]
    snake_set = set(snake)
    food = random_food_position(snake_set)
    score = 0
    return snake, direction, food, score


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    big_font = pygame.font.SysFont("consolas", 32, bold=True)

    snake, direction, food, score = reset_game()
    pending_direction = direction  # buffer agar 1 perubahan arah per frame

    running = True
    game_over = False

    while running:
        # -----------------------------
        # Event handling
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake, direction, food, score = reset_game()
                        pending_direction = direction
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        new_dir = DIRS["UP"]
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        new_dir = DIRS["DOWN"]
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        new_dir = DIRS["LEFT"]
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        new_dir = DIRS["RIGHT"]
                    else:
                        new_dir = None

                    # Cegah berbalik 180 derajat
                    if new_dir is not None:
                        cur_dx, cur_dy = direction
                        new_dx, new_dy = new_dir
                        # Tidak boleh berlawanan persis
                        if (cur_dx + new_dx, cur_dy + new_dy) != (0, 0):
                            pending_direction = new_dir

        if not game_over:
            # Terapkan pending direction hanya sekali per tick
            direction = pending_direction

            # -----------------------------
            # Update posisi ular
            # -----------------------------
            head_x, head_y = snake[-1]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Deteksi tabrak dinding
            x, y = new_head
            if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
                game_over = True
            else:
                # Tabrak diri: cek terhadap tubuh lama (kecuali ekor akan bergerak jika tidak makan)
                will_eat = (food is not None and new_head == food)

                # Jika tidak makan, ekor akan keluar, jadi buat set tubuh tanpa ekor untuk cek cepat
                body_set = set(snake[1:]) if not will_eat else set(snake)
                if new_head in body_set:
                    game_over = True
                else:
                    # Gerakkan ular
                    snake.append(new_head)
                    if will_eat:
                        score += 1
                        # Spawn makanan baru
                        snake_set = set(snake)
                        food = random_food_position(snake_set)
                    else:
                        # Pertahankan panjang
                        snake.pop(0)

                    # Optional: jika food None artinya semua sel penuh (kemenangan sempurna)
                    if food is None:
                        game_over = True

        # -----------------------------
        # Render
        # -----------------------------
        screen.fill(BLACK)
        draw_grid(screen)

        # Gambar ular
        for i, (sx, sy) in enumerate(snake):
            color = GREEN if i < len(snake) - 1 else YELLOW  # kepala warna berbeda
            pygame.draw.rect(screen, color, (sx, sy, BLOCK_SIZE, BLOCK_SIZE))

        # Gambar makanan
        if food is not None:
            fx, fy = food
            pygame.draw.rect(screen, RED, (fx, fy, BLOCK_SIZE, BLOCK_SIZE))

        # Skor
        render_text(screen, f"Score: {score}", font, WHITE, (10, 8))

        # Game Over overlay
        if game_over:
            msg1 = "Game Over!"
            msg2 = "Press R to Restart or ESC to Quit"
            t1 = big_font.render(msg1, True, WHITE)
            t2 = font.render(msg2, True, WHITE)
            rect1 = t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            rect2 = t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(t1, rect1)
            screen.blit(t2, rect2)

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
