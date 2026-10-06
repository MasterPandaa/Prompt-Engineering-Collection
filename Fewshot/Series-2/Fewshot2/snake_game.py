import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta layar dan permainan
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
SNAKE_SPEED = 12  # FPS, bisa disesuaikan untuk tingkat kesulitan

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (235, 64, 52)
GREEN = (0, 200, 0)
DARK_GRAY = (30, 30, 30)

# Setup layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake - Pygame")

# Font
score_font = pygame.font.SysFont("consolas", 22)
game_over_font = pygame.font.SysFont("consolas", 36)

clock = pygame.time.Clock()


def draw_rect(color, x, y, size):
    pygame.draw.rect(screen, color, pygame.Rect(x, y, size, size))


def random_food_position(snake_body):
    """Kembalikan posisi makanan (x, y) yang berada pada grid dan tidak menabrak tubuh ular."""
    grid_cols = SCREEN_WIDTH // BLOCK_SIZE
    grid_rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Daftar semua sel grid
    all_cells = [(c * BLOCK_SIZE, r * BLOCK_SIZE) for r in range(grid_rows) for c in range(grid_cols)]
    # Hapus sel yang ditempati ular
    snake_cells = set(tuple(seg) for seg in snake_body)
    free_cells = [cell for cell in all_cells if cell not in snake_cells]

    if not free_cells:
        # Ular memenuhi layar (menang), tapi untuk kasus ini kembalikan (0, 0)
        return (0, 0)

    return random.choice(free_cells)


def draw_score(score):
    text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 8))


def draw_game_over(score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    msg = game_over_font.render("GAME OVER", True, RED)
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(msg, msg_rect)

    score_msg = score_font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))
    screen.blit(score_msg, score_rect)

    info_msg = score_font.render("Press R to Restart, Esc/Q to Quit", True, WHITE)
    info_rect = info_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45))
    screen.blit(info_msg, info_rect)


def is_opposite(dir_a, dir_b):
    """Cek apakah dir_b berlawanan arah dengan dir_a."""
    ax, ay = dir_a
    bx, by = dir_b
    return ax == -bx and ay == -by


def main():
    # State awal permainan
    snake = [
        [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2],
        [SCREEN_WIDTH // 2 - BLOCK_SIZE, SCREEN_HEIGHT // 2],
        [SCREEN_WIDTH // 2 - 2 * BLOCK_SIZE, SCREEN_HEIGHT // 2],
    ]
    direction = (1, 0)  # Bergerak ke kanan pada awal
    pending_direction = direction  # Untuk mencegah reverse arah instan
    score = 0

    food_x, food_y = random_food_position(snake)

    game_over = False

    while True:
        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        # Restart game
                        return  # Kembali ke main() lagi di bawah (loop game utama)
                else:
                    if event.key == pygame.K_UP:
                        new_dir = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        new_dir = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        new_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        new_dir = (1, 0)
                    else:
                        new_dir = None

                    if new_dir is not None and not is_opposite(direction, new_dir):
                        pending_direction = new_dir

        if not game_over:
            # Update arah menggunakan pending_direction (mencegah reverse di frame yang sama)
            direction = pending_direction

            # Hitung posisi kepala baru
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = [head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE]

            # Deteksi tabrakan dinding
            if (
                new_head[0] < 0
                or new_head[0] >= SCREEN_WIDTH
                or new_head[1] < 0
                or new_head[1] >= SCREEN_HEIGHT
            ):
                game_over = True
            else:
                # Deteksi tabrakan tubuh sendiri
                if new_head in snake:
                    game_over = True
                else:
                    # Geser tubuh: tambah kepala
                    snake.insert(0, new_head)

                    # Cek makan
                    if new_head[0] == food_x and new_head[1] == food_y:
                        score += 1
                        food_x, food_y = random_food_position(snake)
                        # Tidak pop ekor (panjang bertambah)
                    else:
                        # Hapus ekor (bergerak normal)
                        snake.pop()

        # Render
        screen.fill(DARK_GRAY)

        # Gambar makanan
        draw_rect(RED, food_x, food_y, BLOCK_SIZE)

        # Gambar ular (kepala dengan warna berbeda)
        for i, (sx, sy) in enumerate(snake):
            color = GREEN if i == 0 else WHITE
            draw_rect(color, sx, sy, BLOCK_SIZE)

        # Tampilkan skor
        draw_score(score)

        if game_over:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)


if __name__ == "__main__":
    # Loop untuk memudahkan restart tanpa keluar program
    while True:
        main()
