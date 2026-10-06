import sys
import random
import pygame

# -------------------------
# Konfigurasi dasar
# -------------------------
WIDTH, HEIGHT = 600, 400
BLOCK = 20
FPS = 12  # kecepatan permainan (semakin besar semakin cepat)

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 200, 0)
GRAY  = (40, 40, 40)

# -------------------------
# Utilitas
# -------------------------

def draw_grid(surface):
    # Garis-garis grid opsional (untuk estetika)
    for x in range(0, WIDTH, BLOCK):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, BLOCK):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)


def draw_text(surface, text, size, color, pos, center=False, font_name=None):
    font = pygame.font.SysFont(font_name, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(surf, rect)


def random_food_position(snake_body):
    # Menghasilkan posisi makanan yang berada di grid dan tidak bertabrakan dengan ular
    while True:
        x = random.randrange(0, WIDTH, BLOCK)
        y = random.randrange(0, HEIGHT, BLOCK)
        if (x, y) not in snake_body:
            return (x, y)


def is_opposite(dir_a, dir_b):
    # Mengecek apakah dir_b adalah kebalikan dir_a (untuk mencegah berbalik arah)
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


# -------------------------
# Game utama
# -------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()

    # Inisialisasi permainan
    def reset_game():
        # Mulai dari tengah grid
        start_x = WIDTH // 2 // BLOCK * BLOCK
        start_y = HEIGHT // 2 // BLOCK * BLOCK
        snake = [(start_x, start_y)]
        direction = (BLOCK, 0)  # bergerak ke kanan di awal
        next_direction = direction
        food = random_food_position(snake)
        score = 0
        return snake, direction, next_direction, food, score

    snake, direction, next_direction, food, score = reset_game()
    game_over = False

    running = True
    while running:
        clock.tick(FPS)

        # -------------------------
        # Input
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        candidate = (0, -BLOCK)
                        if not is_opposite(direction, candidate):
                            next_direction = candidate
                    elif event.key == pygame.K_DOWN:
                        candidate = (0, BLOCK)
                        if not is_opposite(direction, candidate):
                            next_direction = candidate
                    elif event.key == pygame.K_LEFT:
                        candidate = (-BLOCK, 0)
                        if not is_opposite(direction, candidate):
                            next_direction = candidate
                    elif event.key == pygame.K_RIGHT:
                        candidate = (BLOCK, 0)
                        if not is_opposite(direction, candidate):
                            next_direction = candidate
                else:
                    # State game over
                    if event.key == pygame.K_r:
                        snake, direction, next_direction, food, score = reset_game()
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        # -------------------------
        # Update
        # -------------------------
        if not game_over:
            # Terapkan arah yang valid setelah input (mencegah reverse instan)
            if not is_opposite(direction, next_direction):
                direction = next_direction

            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            # Cek tabrakan dengan dinding
            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT):
                game_over = True
            # Cek tabrakan dengan tubuh sendiri
            elif new_head in snake:
                game_over = True
            else:
                # Gerakkan ular
                snake.insert(0, new_head)

                # Cek makan
                if new_head == food:
                    score += 1
                    food = random_food_position(snake)
                    # Tidak pop tail (ular tumbuh)
                else:
                    snake.pop()  # gerak biasa: remove ekor

        # -------------------------
        # Render
        # -------------------------
        screen.fill(BLACK)
        # draw_grid(screen)  # aktifkan jika ingin melihat grid

        # Gambar makanan
        pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], BLOCK, BLOCK))

        # Gambar ular
        for i, (x, y) in enumerate(snake):
            color = WHITE if i == 0 else (200, 200, 200)
            pygame.draw.rect(screen, color, pygame.Rect(x, y, BLOCK, BLOCK))

        # Skor
        draw_text(screen, f"Skor: {score}", 22, GREEN, (10, 8))

        # Game Over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", 48, WHITE, (WIDTH // 2, HEIGHT // 2 - 30), center=True)
            draw_text(screen, f"Skor Akhir: {score}", 28, WHITE, (WIDTH // 2, HEIGHT // 2 + 10), center=True)
            draw_text(screen, "Tekan R untuk Restart | Esc untuk Keluar", 22, WHITE, (WIDTH // 2, HEIGHT // 2 + 45), center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
