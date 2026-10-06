import pygame
import random
import sys

# Konstanta layar dan permainan
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 12  # Kecepatan permainan (sesuaikan sesuai preferensi)

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 30, 30)
GREEN = (40, 200, 40)
GRAY = (60, 60, 60)

# Arah gerak (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

def random_food_position(snake_body):
    """Menghasilkan posisi makanan yang rata dengan grid dan tidak menimpa tubuh ular."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    snake_cells = {(x // BLOCK_SIZE, y // BLOCK_SIZE) for (x, y) in snake_body}
    free_cells = [
        (cx, cy)
        for cx in range(cols)
        for cy in range(rows)
        if (cx, cy) not in snake_cells
    ]
    if not free_cells:
        # Tidak ada tempat kosong; pemain menang (ular memenuhi layar)
        return None

    fx, fy = random.choice(free_cells)
    return fx * BLOCK_SIZE, fy * BLOCK_SIZE

def draw_grid(surface):
    """Gambar grid opsional untuk memudahkan visualisasi."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

def draw_snake(surface, snake_body):
    for (x, y) in snake_body:
        pygame.draw.rect(surface, WHITE, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))

def draw_food(surface, food_pos):
    if food_pos is not None:
        fx, fy = food_pos
        pygame.draw.rect(surface, RED, pygame.Rect(fx, fy, BLOCK_SIZE, BLOCK_SIZE))

def draw_score(surface, font, score):
    text = font.render(f"Skor: {score}", True, GREEN)
    surface.blit(text, (10, 10))

def game_loop(screen, clock, font):
    # Inisialisasi ular: panjang awal 3, arah awal ke kanan
    start_x = (SCREEN_WIDTH // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    start_y = (SCREEN_HEIGHT // (2 * BLOCK_SIZE)) * BLOCK_SIZE
    snake_body = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    direction = RIGHT
    pending_direction = RIGHT

    food_pos = random_food_position(snake_body)
    score = 0

    running = True
    game_over = False

    while running:
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        pending_direction = UP
                    elif event.key == pygame.K_DOWN:
                        pending_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        pending_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        pending_direction = RIGHT
                else:
                    # Saat game over: R untuk restart, Esc untuk keluar
                    if event.key == pygame.K_r:
                        return "restart"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"

        if not game_over:
            # Cegah berbalik arah (reverse)
            if pending_direction != OPPOSITE.get(direction, None):
                direction = pending_direction

            # Hitung posisi kepala baru
            head_x, head_y = snake_body[0]
            dx, dy = direction
            new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

            # Deteksi tabrakan dinding
            x, y = new_head
            if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
                game_over = True
            else:
                # Deteksi tabrakan tubuh
                if new_head in snake_body:
                    game_over = True
                else:
                    # Gerakkan ular: tambah kepala
                    snake_body.insert(0, new_head)

                    # Cek apakah makan
                    if food_pos is not None and new_head == food_pos:
                        score += 1
                        food_pos = random_food_position(snake_body)
                    else:
                        # Hapus ekor jika tidak makan
                        snake_body.pop()

            # Jika tidak ada tempat makanan lagi (ular memenuhi layar) -> menang, tetapi anggap selesai
            if food_pos is None:
                game_over = True

        # Gambar
        screen.fill(BLACK)
        # Optional grid untuk referensi posisi
        # draw_grid(screen)
        draw_snake(screen, snake_body)
        draw_food(screen, food_pos)
        draw_score(screen, font, score)

        if game_over:
            over_text = font.render("Game Over - Tekan R untuk Restart atau Esc untuk Keluar", True, WHITE)
            rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(over_text, rect)

        pygame.display.flip()
        clock.tick(FPS)

def main():
    pygame.init()
    pygame.display.set_caption("Contoh Game Snake")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    while True:
        action = game_loop(screen, clock, font)
        if action == "quit":
            break
        # Jika "restart", loop akan mengulangi permainan baru

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
