import sys
import random
import pygame

# ---------- Konfigurasi dasar ----------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
FPS = 12  # kecepatan game (semakin besar semakin cepat)

# Pastikan grid pas
assert WIDTH % BLOCK_SIZE == 0 and HEIGHT % BLOCK_SIZE == 0, "WIDTH/HEIGHT harus kelipatan BLOCK_SIZE"

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK_GREEN = (0, 150, 0)
GREY = (40, 40, 40)

# Arah gerak (vektor grid)
UP = (0, -BLOCK_SIZE)
DOWN = (0, BLOCK_SIZE)
LEFT = (-BLOCK_SIZE, 0)
RIGHT = (BLOCK_SIZE, 0)


def opposite_dir(d1, d2):
    """Cek apakah d2 adalah kebalikan 180° dari d1."""
    return d1[0] == -d2[0] and d1[1] == -d2[1]


def random_food_position(snake):
    """Spawn makanan pada posisi grid acak yang tidak bertabrakan dengan ular."""
    snake_set = set(snake)
    cols = WIDTH // BLOCK_SIZE
    rows = HEIGHT // BLOCK_SIZE

    # Jika grid hampir penuh, lakukan sampling dari semua sel kosong
    if len(snake) >= cols * rows - 1:
        # Cari sel kosong terakhir
        for r in range(rows):
            for c in range(cols):
                pos = (c * BLOCK_SIZE, r * BLOCK_SIZE)
                if pos not in snake_set:
                    return pos
        # fallback (harusnya tidak pernah tercapai)
        return (0, 0)

    while True:
        x = random.randrange(0, WIDTH, BLOCK_SIZE)
        y = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if (x, y) not in snake_set:
            return (x, y)


def draw_grid(surface):
    """Opsional: gambar grid halus untuk orientasi."""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GREY, (0, y), (WIDTH, y))


def draw_snake(surface, snake):
    # Kepala
    head = snake[0]
    pygame.draw.rect(surface, DARK_GREEN, (head[0], head[1], BLOCK_SIZE, BLOCK_SIZE))
    # Tubuh
    for segment in snake[1:]:
        pygame.draw.rect(surface, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_food(surface, food_pos):
    pygame.draw.rect(surface, RED, (food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_score(surface, font, score):
    text = font.render(f"Skor: {score}", True, WHITE)
    surface.blit(text, (10, 10))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 54)

    # Inisialisasi ular di tengah, arah ke kanan
    start_x = (WIDTH // 2) // BLOCK_SIZE * BLOCK_SIZE
    start_y = (HEIGHT // 2) // BLOCK_SIZE * BLOCK_SIZE
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = RIGHT
    pending_direction = RIGHT  # menyimpan input arah terbaru yang valid

    food = random_food_position(snake)
    score = 0

    game_over = False

    while True:
        # ---------- Event handling ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_r, pygame.K_SPACE):
                        # Restart
                        start_x = (WIDTH // 2) // BLOCK_SIZE * BLOCK_SIZE
                        start_y = (HEIGHT // 2) // BLOCK_SIZE * BLOCK_SIZE
                        snake = [
                            (start_x, start_y),
                            (start_x - BLOCK_SIZE, start_y),
                            (start_x - 2 * BLOCK_SIZE, start_y),
                        ]
                        direction = RIGHT
                        pending_direction = RIGHT
                        food = random_food_position(snake)
                        score = 0
                        game_over = False
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        if not opposite_dir(direction, UP):
                            pending_direction = UP
                    elif event.key == pygame.K_DOWN:
                        if not opposite_dir(direction, DOWN):
                            pending_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        if not opposite_dir(direction, LEFT):
                            pending_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        if not opposite_dir(direction, RIGHT):
                            pending_direction = RIGHT
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()

        # ---------- Update ----------
        if not game_over:
            # Terapkan perubahan arah yang valid
            if not opposite_dir(direction, pending_direction):
                direction = pending_direction

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Cek tabrakan dinding
            if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
                game_over = True
            else:
                # Cek tabrakan diri (gunakan set untuk cepat)
                if new_head in snake:
                    game_over = True
                else:
                    # Gerakkan ular
                    snake.insert(0, new_head)

                    # Makan?
                    if new_head == food:
                        score += 1
                        food = random_food_position(snake)
                        # Tidak pop -> tumbuh
                    else:
                        snake.pop()

        # ---------- Render ----------
        screen.fill(BLACK)
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)
        draw_score(screen, font, score)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            msg = big_font.render("Game Over", True, WHITE)
            sub = font.render("Tekan R atau SPACE untuk restart • ESC/Q untuk keluar", True, WHITE)
            score_msg = font.render(f"Skor akhir: {score}", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 70))
            screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
