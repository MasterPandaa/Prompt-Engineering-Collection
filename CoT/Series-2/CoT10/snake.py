import pygame
import random
import sys

# =========================
# Konstanta & Konfigurasi
# =========================
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20
SNAKE_SPEED = 10  # FPS (pergerakan per detik)

# Warna
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREEN  = (0, 200, 0)
RED    = (200, 0, 0)
GRAY   = (40, 40, 40)
YELLOW = (255, 215, 0)

# Arah vektor (dx, dy) dalam kelipatan BLOCK_SIZE
DIR_UP    = (0, -BLOCK_SIZE)
DIR_DOWN  = (0, BLOCK_SIZE)
DIR_LEFT  = (-BLOCK_SIZE, 0)
DIR_RIGHT = (BLOCK_SIZE, 0)


def grid_align(value, block):
    """Menyelaraskan nilai ke grid terdekat (kelipatan block)."""
    return (value // block) * block


def spawn_food(snake, width, height, block):
    """Spawn makanan pada posisi acak yang tidak bertabrakan dengan tubuh ular."""
    while True:
        x = random.randrange(0, width, block)
        y = random.randrange(0, height, block)
        if (x, y) not in snake:
            return (x, y)


def draw_grid(surface, width, height, block, color):
    """Opsional: menggambar grid tipis agar terlihat rapih."""
    for x in range(0, width, block):
        pygame.draw.line(surface, color, (x, 0), (x, height), 1)
    for y in range(0, height, block):
        pygame.draw.line(surface, color, (0, y), (width, y), 1)


def draw_snake(surface, snake):
    """Gambar ular. Kepala diberi warna berbeda."""
    if not snake:
        return
    head = snake[0]
    # Kepala
    pygame.draw.rect(surface, YELLOW, (head[0], head[1], BLOCK_SIZE, BLOCK_SIZE))
    # Badan
    for segment in snake[1:]:
        pygame.draw.rect(surface, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_food(surface, food_pos):
    pygame.draw.rect(surface, RED, (food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))


def opposite_dir(dir_a, dir_b):
    """True jika dir_b adalah kebalikan (180°) dari dir_a."""
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 48)

    # Inisialisasi ular di tengah, panjang awal 3, bergerak ke kanan
    start_x = grid_align(WIDTH // 2, BLOCK_SIZE)
    start_y = grid_align(HEIGHT // 2, BLOCK_SIZE)
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = DIR_RIGHT
    pending_direction = direction  # untuk buffer input agar tidak 180° pada frame yang sama

    food_pos = spawn_food(snake, WIDTH, HEIGHT, BLOCK_SIZE)
    score = 0
    running = True
    game_over = False

    while running:
        # =========================
        # Event Handling
        # =========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        # Restart
                        return True  # sinyal ke main untuk restart
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                else:
                    if event.key == pygame.K_UP:
                        if not opposite_dir(direction, DIR_UP):
                            pending_direction = DIR_UP
                    elif event.key == pygame.K_DOWN:
                        if not opposite_dir(direction, DIR_DOWN):
                            pending_direction = DIR_DOWN
                    elif event.key == pygame.K_LEFT:
                        if not opposite_dir(direction, DIR_LEFT):
                            pending_direction = DIR_LEFT
                    elif event.key == pygame.K_RIGHT:
                        if not opposite_dir(direction, DIR_RIGHT):
                            pending_direction = DIR_RIGHT

        if not game_over:
            # Terapkan arah yang valid (hindari 180°)
            direction = pending_direction

            # =========================
            # Update Logika Ular
            # =========================
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            # Deteksi tabrakan dengan dinding
            hit_wall = (
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT
            )

            # Deteksi tabrakan dengan badan sendiri
            hit_self = new_head in snake[1:]

            if hit_wall or hit_self:
                game_over = True
            else:
                # Gerakkan ular: tambah kepala
                snake.insert(0, new_head)

                # Makan?
                if new_head == food_pos:
                    score += 1
                    food_pos = spawn_food(snake, WIDTH, HEIGHT, BLOCK_SIZE)
                    # Tidak pop ekor agar ular tumbuh
                else:
                    # Tidak makan: buang ekor
                    snake.pop()

        # =========================
        # Render
        # =========================
        screen.fill(BLACK)
        draw_grid(screen, WIDTH, HEIGHT, BLOCK_SIZE, GRAY)
        draw_snake(screen, snake)
        draw_food(screen, food_pos)

        # Tampilkan skor
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (10, 8))

        # Tampilkan Game Over
        if game_over:
            over_text = big_font.render("GAME OVER", True, WHITE)
            info_text = font.render("Press R/Enter/Space to Restart, Q/Esc to Quit", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 8))

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)

    return False  # tidak restart, keluar


def main():
    # Loop untuk memungkinkan restart tanpa menutup window secara paksa
    while True:
        restart = game_loop()
        if not restart:
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
