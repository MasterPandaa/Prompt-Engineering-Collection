import sys
import random
import pygame

# ----------------------------
# Konstanta dan Konfigurasi
# ----------------------------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
SNAKE_SPEED = 12  # FPS

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
GREEN = (0, 200, 0)
RED   = (220, 50, 50)
GRAY  = (40, 40, 40)
YELLOW = (250, 200, 0)

# Arah sebagai vektor grid (dx, dy)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


def draw_grid(surface):
    """Gambar grid opsional untuk membantu visualisasi pergerakan ular."""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))


def random_food_position(snake_body):
    """Kembalikan posisi makanan acak pada grid yang tidak menimpa tubuh ular."""
    occupied = set(snake_body)
    while True:
        fx = random.randrange(0, WIDTH, BLOCK_SIZE)
        fy = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if (fx, fy) not in occupied:
            return fx, fy


def prevent_180_change(current_dir, new_dir):
    """Cegah perubahan arah 180 derajat (putar balik)."""
    cdx, cdy = current_dir
    ndx, ndy = new_dir
    return not (cdx == -ndx and cdy == -ndy)


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    def reset_game():
        # Tempatkan ular di tengah, memanjang 3 segmen ke kiri
        start_x = (WIDTH // 2 // BLOCK_SIZE) * BLOCK_SIZE
        start_y = (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
        snake = [
            (start_x, start_y),
            (start_x - BLOCK_SIZE, start_y),
            (start_x - 2 * BLOCK_SIZE, start_y),
        ]
        direction = DIR_RIGHT
        food = random_food_position(snake)
        score = 0
        return snake, direction, food, score

    snake, direction, food, score = reset_game()
    game_over = False

    while True:
        # ----------------------------
        # Event Handling
        # ----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if prevent_180_change(direction, DIR_UP):
                        direction = DIR_UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if prevent_180_change(direction, DIR_DOWN):
                        direction = DIR_DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if prevent_180_change(direction, DIR_LEFT):
                        direction = DIR_LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if prevent_180_change(direction, DIR_RIGHT):
                        direction = DIR_RIGHT

            if game_over and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    # restart
                    snake, direction, food, score = reset_game()
                    game_over = False
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        # ----------------------------
        # Update Game (ketika tidak game over)
        # ----------------------------
        if not game_over:
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

            # Cek tabrak dinding
            if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
                game_over = True
            else:
                # Cek tabrak tubuh (pakai set untuk cepat)
                body_set = set(snake)
                if new_head in body_set:
                    game_over = True
                else:
                    # Gerakkan ular: sisipkan kepala
                    snake.insert(0, new_head)

                    # Makan?
                    if new_head == food:
                        score += 1
                        food = random_food_position(snake)
                        # Tidak pop ekor => panjang bertambah
                    else:
                        # Tidak makan => pop ekor
                        snake.pop()

        # ----------------------------
        # Render
        # ----------------------------
        screen.fill(BLACK)
        draw_grid(screen)

        # Gambar makanan
        pygame.draw.rect(
            screen, RED, pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE)
        )

        # Gambar ular
        for i, (x, y) in enumerate(snake):
            color = GREEN if i == 0 else (0, 160, 0)
            pygame.draw.rect(screen, color, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
        # Opsional: detail mata pada kepala
        if snake:
            hx, hy = snake[0]
            eye_size = BLOCK_SIZE // 6
            pygame.draw.circle(screen, YELLOW, (hx + BLOCK_SIZE // 3, hy + BLOCK_SIZE // 3), eye_size)
            pygame.draw.circle(screen, YELLOW, (hx + 2 * BLOCK_SIZE // 3, hy + BLOCK_SIZE // 3), eye_size)

        # Skor
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (10, 8))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            go_text = big_font.render("GAME OVER", True, WHITE)
            go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(go_text, go_rect)

            tip_text = font.render("Press R/Enter/Space to Restart, Q/Esc to Quit", True, WHITE)
            tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(tip_text, tip_rect)

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)


if __name__ == "__main__":
    main()
