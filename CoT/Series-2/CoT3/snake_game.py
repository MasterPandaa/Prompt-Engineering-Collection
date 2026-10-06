import pygame
import random
import sys

# ========== Konfigurasi Dasar ==========
WIDTH, HEIGHT = 600, 400        # Pastikan kelipatan BLOCK_SIZE
BLOCK_SIZE = 20                 # Ukuran satu grid
SPEED = 10                      # FPS awal (kecepatan permainan)

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 0, 0)
GRAY = (40, 40, 40)
YELLOW = (240, 220, 0)

# ========== Utility ==========
def draw_grid(surface):
    # Garis grid opsional untuk membantu visual
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))

def random_food_position(snake_body):
    # Pilih posisi acak yang tidak menabrak tubuh ular
    # Cara sederhana: loop sampai dapat cell kosong
    while True:
        x = random.randrange(0, WIDTH, BLOCK_SIZE)
        y = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if (x, y) not in snake_body:
            return (x, y)

def render_text(surface, text, size, color, center):
    font = pygame.font.SysFont(None, size, bold=True)
    r = font.render(text, True, color)
    rect = r.get_rect(center=center)
    surface.blit(r, rect)

# ========== Game Loop ==========
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()

    # Inisialisasi ular
    start_x = WIDTH // 2
    start_y = HEIGHT // 2
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = (BLOCK_SIZE, 0)  # ke kanan sebagai arah awal
    pending_direction = direction

    # Inisialisasi makanan dan skor
    food = random_food_position(snake)
    score = 0
    speed = SPEED

    running = True
    game_over = False

    while running:
        # ========== Event Handling ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        # Cegah 180 derajat
                        if direction != (0, BLOCK_SIZE):
                            pending_direction = (0, -BLOCK_SIZE)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if direction != (0, -BLOCK_SIZE):
                            pending_direction = (0, BLOCK_SIZE)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if direction != (BLOCK_SIZE, 0):
                            pending_direction = (-BLOCK_SIZE, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if direction != (-BLOCK_SIZE, 0):
                            pending_direction = (BLOCK_SIZE, 0)
                else:
                    # Layar game over
                    if event.key in (pygame.K_r, pygame.K_SPACE):
                        # Restart game
                        start_x = WIDTH // 2
                        start_y = HEIGHT // 2
                        snake = [
                            (start_x, start_y),
                            (start_x - BLOCK_SIZE, start_y),
                            (start_x - 2 * BLOCK_SIZE, start_y),
                        ]
                        direction = (BLOCK_SIZE, 0)
                        pending_direction = direction
                        food = random_food_position(snake)
                        score = 0
                        speed = SPEED
                        game_over = False
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False

        if not game_over:
            # Terapkan perubahan arah yang valid
            direction = pending_direction

            # ========== Update Posisi Ular ==========
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Cek tabrakan dinding
            x, y = new_head
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                game_over = True
            else:
                # Cek tabrakan diri sendiri (pakai snake tanpa ekor jika nanti tidak makan)
                if new_head in snake:
                    game_over = True
                else:
                    # Masukkan kepala baru
                    snake.insert(0, new_head)

                    # Cek makan
                    if new_head == food:
                        score += 1
                        # Optional: tingkatkan kecepatan setiap beberapa poin
                        if score % 5 == 0:
                            speed = min(25, speed + 1)
                        # Spawn makanan baru
                        food = random_food_position(snake)
                        # Tidak pop ekor (panjang bertambah)
                    else:
                        # Tidak makan -> gerak normal pop ekor
                        snake.pop()

        # ========== Render ==========
        screen.fill(BLACK)
        # draw_grid(screen)  # aktifkan jika ingin melihat grid

        # Gambar makanan
        pygame.draw.rect(
            screen,
            RED,
            pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE),
            border_radius=4,
        )

        # Gambar ular
        # Kepala sedikit lebih terang
        if snake:
            hx, hy = snake[0]
            pygame.draw.rect(
                screen,
                YELLOW,
                pygame.Rect(hx, hy, BLOCK_SIZE, BLOCK_SIZE),
                border_radius=4,
            )
        for seg in snake[1:]:
            pygame.draw.rect(
                screen,
                GREEN,
                pygame.Rect(seg[0], seg[1], BLOCK_SIZE, BLOCK_SIZE),
                border_radius=4,
            )

        # Skor
        render_text(screen, f"Score: {score}", 28, WHITE, (70, 20))

        # Game Over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            render_text(screen, "GAME OVER", 56, WHITE, (WIDTH // 2, HEIGHT // 2 - 30))
            render_text(screen, "Press R/Space to Restart", 28, WHITE, (WIDTH // 2, HEIGHT // 2 + 10))
            render_text(screen, "Press Q/Esc to Quit", 22, WHITE, (WIDTH // 2, HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
