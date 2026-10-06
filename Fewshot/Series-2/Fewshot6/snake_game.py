import pygame
import random
import sys

# ---------------------------
# Konfigurasi utama
# ---------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 12  # Kecepatan permainan (semakin besar semakin cepat)

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 200, 0)
GRAY  = (40, 40, 40)

# Arah gerak (dx, dy) berbasis grid BLOCK_SIZE
UP    = (0, -BLOCK_SIZE)
DOWN  = (0,  BLOCK_SIZE)
LEFT  = (-BLOCK_SIZE, 0)
RIGHT = ( BLOCK_SIZE, 0)

# ---------------------------
# Utilitas
# ---------------------------
def random_food_position(snake_body):
    """Menghasilkan posisi makanan secara acak di grid, tidak bertumpuk dengan tubuh ular."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Kumpulkan semua sel kosong yang bukan tubuh ular
    snake_set = set((x, y) for (x, y) in snake_body)
    empty_cells = []
    for c in range(cols):
        for r in range(rows):
            x = c * BLOCK_SIZE
            y = r * BLOCK_SIZE
            if (x, y) not in snake_set:
                empty_cells.append((x, y))

    # Jika penuh (secara teori menang), kembalikan None
    if not empty_cells:
        return None

    return random.choice(empty_cells)

def is_opposite(dir_a, dir_b):
    """Cek apakah dua arah saling berlawanan."""
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]

# ---------------------------
# Game
# ---------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game Snake - Pygame')
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont(None, 24)
    font_large = pygame.font.SysFont(None, 48)

    def draw_score(score):
        text = font_small.render(f"Skor: {score}", True, WHITE)
        screen.blit(text, (10, 8))

    def draw_grid():
        # Opsional: grid tipis untuk membantu visual
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

    def draw_snake(snake_body):
        for (x, y) in snake_body:
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))

    def draw_food(food_pos):
        if food_pos is not None:
            pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

    def game_over_screen(score):
        screen.fill(BLACK)
        msg1 = font_large.render("Game Over", True, RED)
        msg2 = font_small.render("Tekan R untuk Restart, Q untuk Keluar", True, WHITE)
        msg3 = font_small.render(f"Skor akhir: {score}", True, WHITE)
        screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(msg3, (SCREEN_WIDTH // 2 - msg3.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        pygame.display.flip()

        # Tunggu input untuk restart/keluar
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit(0)
                    if event.key == pygame.K_r:
                        return  # Kembali ke main loop untuk restart
            clock.tick(30)

    # Inisialisasi ular (panjang awal 3 segmen) dan arah
    start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = RIGHT
    pending_direction = RIGHT  # Menyimpan input arah terbaru yang valid

    # Makanan
    food = random_food_position(snake)
    score = 0

    running = True
    while running:
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not is_opposite(direction, UP) and direction != UP:
                        pending_direction = UP
                elif event.key == pygame.K_DOWN:
                    if not is_opposite(direction, DOWN) and direction != DOWN:
                        pending_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if not is_opposite(direction, LEFT) and direction != LEFT:
                        pending_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if not is_opposite(direction, RIGHT) and direction != RIGHT:
                        pending_direction = RIGHT

        # Terapkan perubahan arah tepat sebelum gerak agar "tidak bisa berbalik"
        direction = pending_direction

        # Gerakkan ular: hitung posisi kepala baru
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        # Cek tabrakan dinding
        if (
            new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT
        ):
            game_over_screen(score)
            # Reset permainan
            start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
            start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
            snake = [
                (start_x, start_y),
                (start_x - BLOCK_SIZE, start_y),
                (start_x - 2 * BLOCK_SIZE, start_y),
            ]
            direction = RIGHT
            pending_direction = RIGHT
            food = random_food_position(snake)
            score = 0
            continue

        # Cek tabrakan dengan tubuh sendiri
        if new_head in snake:
            game_over_screen(score)
            # Reset permainan
            start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
            start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
            snake = [
                (start_x, start_y),
                (start_x - BLOCK_SIZE, start_y),
                (start_x - 2 * BLOCK_SIZE, start_y),
            ]
            direction = RIGHT
            pending_direction = RIGHT
            food = random_food_position(snake)
            score = 0
            continue

        # Tambahkan kepala baru
        snake.insert(0, new_head)

        # Cek makan makanan
        if food is not None and new_head == food:
            score += 1
            food = random_food_position(snake)
        else:
            # Gerak normal: hapus ekor
            snake.pop()

        # Render
        screen.fill(BLACK)
        # draw_grid()  # aktifkan jika ingin grid bantuan
        draw_food(food)
        draw_snake(snake)
        draw_score(score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
