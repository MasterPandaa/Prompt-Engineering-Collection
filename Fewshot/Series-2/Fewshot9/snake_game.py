import pygame
import random
import sys

# -----------------------------
# Konfigurasi dasar
# -----------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 12  # kecepatan ular (semakin besar semakin cepat)

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
GRAY = (60, 60, 60)

# Arah
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def grid_aligned_random_pos():
    # Menghasilkan posisi makanan yang sejajar dengan grid 20x20
    x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
    y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)
    return [x, y]


def draw_block(surface, color, position):
    rect = pygame.Rect(position[0], position[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)


def draw_snake(surface, snake_body):
    for i, seg in enumerate(snake_body):
        # Kepala sedikit berbeda warna agar mudah terlihat
        color = GREEN if i > 0 else (0, 255, 100)
        draw_block(surface, color, seg)


def show_score(surface, score, font):
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 8))


def game_over_screen(surface, score, font_big, font_small):
    surface.fill(BLACK)
    msg = font_big.render("GAME OVER", True, RED)
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    surface.blit(msg, msg_rect)

    info = font_small.render("Press R to Restart or ESC to Quit", True, GRAY)
    info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    surface.blit(info, info_rect)

    score_text = font_small.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    surface.blit(score_text, score_rect)

    pygame.display.flip()


def is_opposite(dir_a, dir_b):
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game Snake")
    clock = pygame.time.Clock()

    font_score = pygame.font.SysFont("consolas", 24)
    font_big = pygame.font.SysFont("consolas", 48, bold=True)
    font_small = pygame.font.SysFont("consolas", 22)

    def reset_game():
        # Ular mulai di tengah
        start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
        start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
        snake_body = [
            [start_x, start_y],
            [start_x - BLOCK_SIZE, start_y],
            [start_x - 2 * BLOCK_SIZE, start_y],
        ]
        direction = RIGHT
        food_pos = grid_aligned_random_pos()
        score = 0
        return snake_body, direction, food_pos, score

    snake_body, direction, food_pos, score = reset_game()
    pending_direction = direction  # untuk mencegah reverse instant

    running = True
    game_over = False

    while running:
        # -----------------------------
        # Input
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not is_opposite(UP, direction):
                        pending_direction = UP
                elif event.key == pygame.K_DOWN:
                    if not is_opposite(DOWN, direction):
                        pending_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if not is_opposite(LEFT, direction):
                        pending_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if not is_opposite(RIGHT, direction):
                        pending_direction = RIGHT

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    snake_body, direction, food_pos, score = reset_game()
                    pending_direction = direction
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if game_over:
            game_over_screen(screen, score, font_big, font_small)
            clock.tick(10)
            continue

        # Terapkan perubahan arah yang valid
        if not is_opposite(pending_direction, direction):
            direction = pending_direction

        # -----------------------------
        # Update logika
        # -----------------------------
        head_x, head_y = snake_body[0]
        new_head = [
            head_x + direction[0] * BLOCK_SIZE,
            head_y + direction[1] * BLOCK_SIZE,
        ]

        # Cek tabrakan dinding
        if (
            new_head[0] < 0
            or new_head[0] >= SCREEN_WIDTH
            or new_head[1] < 0
            or new_head[1] >= SCREEN_HEIGHT
        ):
            game_over = True
        else:
            # Cek tabrakan tubuh sendiri (pakai posisi setelah bergerak)
            if new_head in snake_body:
                game_over = True
            else:
                # Pindahkan ular
                snake_body.insert(0, new_head)

                # Makan makanan
                if new_head[0] == food_pos[0] and new_head[1] == food_pos[1]:
                    score += 1
                    # Tempatkan makanan baru di posisi yang tidak bertabrakan dengan ular
                    while True:
                        food_pos = grid_aligned_random_pos()
                        if food_pos not in snake_body:
                            break
                else:
                    # Hapus ekor jika tidak makan
                    snake_body.pop()

        # -----------------------------
        # Render
        # -----------------------------
        screen.fill(BLACK)

        # Gambar makanan
        draw_block(screen, RED, food_pos)

        # Gambar ular
        draw_snake(screen, snake_body)

        # Tampilkan skor
        show_score(screen, score, font_score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
