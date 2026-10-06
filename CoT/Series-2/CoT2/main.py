import pygame
import random
import sys

# -----------------------------
# Konfigurasi dasar
# -----------------------------
WIDTH, HEIGHT = 640, 480
BLOCK = 20
SNAKE_SPEED = 12  # FPS

# Warna
BLACK = (18, 18, 18)
WHITE = (240, 240, 240)
GREEN = (40, 200, 120)
DARK_GREEN = (30, 160, 95)
RED = (235, 80, 80)
GRID = (30, 30, 30)

# -----------------------------
# Utilitas
# -----------------------------
def draw_grid(surface):
    # Garis grid opsional agar terlihat rapi
    for x in range(0, WIDTH, BLOCK):
        pygame.draw.line(surface, GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, BLOCK):
        pygame.draw.line(surface, GRID, (0, y), (WIDTH, y), 1)

def spawn_food(snake):
    # Spawn makanan yang tidak menimpa ular
    while True:
        fx = random.randrange(0, WIDTH // BLOCK) * BLOCK
        fy = random.randrange(0, HEIGHT // BLOCK) * BLOCK
        if (fx, fy) not in snake:
            return (fx, fy)

def render_text(surface, text, size, color, center):
    font = pygame.font.SysFont("consolas", size, bold=True)
    s = font.render(text, True, color)
    rect = s.get_rect(center=center)
    surface.blit(s, rect)

# -----------------------------
# Game utama
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake (Pygame)")
    clock = pygame.time.Clock()

    # Inisialisasi ular
    start_x = (WIDTH // (2 * BLOCK)) * BLOCK
    start_y = (HEIGHT // (2 * BLOCK)) * BLOCK
    snake = [
        (start_x, start_y),
        (start_x - BLOCK, start_y),
        (start_x - 2 * BLOCK, start_y),
    ]
    dir_x, dir_y = (1, 0)  # bergerak ke kanan
    pending_dir = (1, 0)   # arah yang diminta dari input

    # Makanan dan skor
    food = spawn_food(snake)
    score = 0

    running = True
    game_over = False

    while running:
        # 1) Event/input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if game_over:
                    # Setelah game over, tombol apa pun untuk reset
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        # Reset permainan
                        snake = [
                            (start_x, start_y),
                            (start_x - BLOCK, start_y),
                            (start_x - 2 * BLOCK, start_y),
                        ]
                        dir_x, dir_y = (1, 0)
                        pending_dir = (1, 0)
                        food = spawn_food(snake)
                        score = 0
                        game_over = False
                else:
                    # Input arah selama bermain
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pending_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pending_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        pending_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        pending_dir = (1, 0)

        if not game_over:
            # 2) Terapkan perubahan arah jika bukan kebalikan
            ndx, ndy = pending_dir
            if (ndx, ndy) != (-dir_x, -dir_y):  # cegah putar balik 180°
                dir_x, dir_y = ndx, ndy

            # 3) Hitung kepala baru
            head_x, head_y = snake[0]
            new_head = (head_x + dir_x * BLOCK, head_y + dir_y * BLOCK)

            # 4) Deteksi tabrak dinding
            x, y = new_head
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                game_over = True
            else:
                # 5) Masukkan kepala baru
                snake.insert(0, new_head)

                # 6) Deteksi diri sendiri
                if new_head in snake[1:]:
                    game_over = True

                # 7) Makan atau bergerak biasa
                if not game_over:
                    if new_head == food:
                        score += 1
                        food = spawn_food(snake)
                        # Tidak pop ekor -> ular bertambah panjang
                    else:
                        snake.pop()  # gerak biasa, panjang tetap

        # 8) Render
        screen.fill(BLACK)
        draw_grid(screen)

        # Gambar makanan
        pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK, BLOCK))

        # Gambar ular (kepala lebih terang)
        for i, (sx, sy) in enumerate(snake):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (sx, sy, BLOCK, BLOCK))

        # Skor
        render_text(screen, f"Score: {score}", 20, WHITE, (70, 20))

        if game_over:
            render_text(screen, "GAME OVER", 48, WHITE, (WIDTH // 2, HEIGHT // 2 - 20))
            render_text(
                screen,
                "Press any key to restart • ESC to quit",
                22,
                WHITE,
                (WIDTH // 2, HEIGHT // 2 + 20),
            )

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
