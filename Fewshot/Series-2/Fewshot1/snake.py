import pygame
import random
import sys

# ----------------------------
# Konfigurasi dasar
# ----------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 12  # Kecepatan game (frame per detik)

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
GRAY = (40, 40, 40)

# Arah (dx, dy) dalam unit grid (BLOCK_SIZE)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


def grid_random_pos(exclude_positions):
    """Ambil posisi acak di grid yang tidak bertabrakan dengan posisi pada exclude_positions (set of tuples)."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Jika grid penuh (skenario sangat jarang), kembalikan None
    if len(exclude_positions) >= cols * rows:
        return None

    while True:
        x = random.randrange(cols) * BLOCK_SIZE
        y = random.randrange(rows) * BLOCK_SIZE
        if (x, y) not in exclude_positions:
            return (x, y)


def draw_rect(screen, color, pos):
    """Gambar kotak ukuran BLOCK_SIZE pada posisi pos=(x,y)."""
    pygame.draw.rect(screen, color, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_snake(screen, snake):
    """Gambar seluruh segmen ular. Kepala dibedakan dengan warna lebih gelap."""
    for i, segment in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        draw_rect(screen, color, segment)


def draw_grid(screen):
    """Opsional: grid halus agar orientasi lebih mudah."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)


def draw_score(screen, font, score):
    text = font.render(f"Skor: {score}", True, WHITE)
    screen.blit(text, (10, 8))


def game_over_screen(screen, big_font, small_font, score):
    screen.fill(BLACK)
    msg = big_font.render("Game Over!", True, RED)
    sub = small_font.render("Tekan R untuk main lagi, atau Q untuk keluar.", True, WHITE)
    score_txt = small_font.render(f"Skor Anda: {score}", True, WHITE)

    screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
    screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
    pygame.display.flip()

    # Tunggu input R (restart) atau Q (quit)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    return


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game Snake")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 28)

    # Inisialisasi ular (panjang awal 3) di tengah layar, bergerak ke kanan
    start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = DIR_RIGHT
    pending_direction = direction  # menyimpan input arah terbaru yang valid

    # Makanan pertama, pastikan tidak muncul di tubuh ular
    snake_set = set(snake)
    food = grid_random_pos(snake_set)

    score = 0
    running = True

    while running:
        # 1) Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if direction != DIR_DOWN:  # tidak bisa berbalik arah
                        pending_direction = DIR_UP
                elif event.key == pygame.K_DOWN:
                    if direction != DIR_UP:
                        pending_direction = DIR_DOWN
                elif event.key == pygame.K_LEFT:
                    if direction != DIR_RIGHT:
                        pending_direction = DIR_LEFT
                elif event.key == pygame.K_RIGHT:
                    if direction != DIR_LEFT:
                        pending_direction = DIR_RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

        # Terapkan arah baru (mencegah reverse instan)
        direction = pending_direction

        # 2) Update posisi ular
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

        # 2a) Deteksi tabrakan dengan dinding
        if (
            new_head[0] < 0
            or new_head[0] >= SCREEN_WIDTH
            or new_head[1] < 0
            or new_head[1] >= SCREEN_HEIGHT
        ):
            game_over_screen(screen, big_font, small_font, score)
            return  # keluar dari run_game agar main loop (restart) bisa memanggil lagi

        # 2b) Deteksi tabrakan dengan tubuh sendiri (kecuali ekor jika bergerak tanpa makan)
        if new_head in snake[:-1]:
            game_over_screen(screen, big_font, small_font, score)
            return

        # Tambahkan kepala
        snake.insert(0, new_head)

        # 2c) Cek makan
        if new_head == food:
            score += 1
            # spawn makanan baru di posisi kosong
            snake_set = set(snake)
            food = grid_random_pos(snake_set)
            if food is None:
                # Menang: grid penuh, akhiri permainan
                game_over_screen(screen, big_font, small_font, score)
                return
            # Tidak menghapus ekor (ular bertambah panjang)
        else:
            # Gerakkan ular: hapus ekor
            snake.pop()

        # 3) Render
        screen.fill(BLACK)
        # draw_grid(screen)  # aktifkan jika ingin menampilkan grid tipis
        draw_snake(screen, snake)
        draw_rect(screen, RED, food)
        draw_score(screen, font, score)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        run_game()
        # Jika run_game return (Game Over dan pilih R), loop akan memulai game baru


if __name__ == "__main__":
    main()
