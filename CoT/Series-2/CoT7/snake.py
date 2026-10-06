import sys
import random
import pygame

# -----------------------------
# Konfigurasi dasar
# -----------------------------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
FPS = 12  # kecepatan ular (frame per detik)

# Warna
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 30, 30)
YELLOW = (240, 200, 0)

# Arah sebagai vektor grid (dx, dy)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

OPPOSITE = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}

# -----------------------------
# Utilitas
# -----------------------------
def snap_to_grid(val, size):
    return val - (val % size)

def random_food_position(snake_segments):
    """Kembalikan posisi makanan acak yang tidak bertumpuk dengan ular."""
    while True:
        x = random.randrange(0, WIDTH, BLOCK_SIZE)
        y = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if (x, y) not in snake_segments:
            return (x, y)

def draw_grid(surface):
    """Opsional: menggambar grid untuk visualisasi."""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))

def draw_snake(surface, snake_segments):
    for i, (x, y) in enumerate(snake_segments):
        color = GREEN if i == 0 else (0, 160, 0)
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surface, color, rect)
        # Highlight border
        pygame.draw.rect(surface, BLACK, rect, 1)

def draw_food(surface, food_pos):
    rect = pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, RED, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)

def render_text(surface, text, pos, size=24, color=WHITE, center=False):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(img, rect)

# -----------------------------
# Game utama
# -----------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Inisialisasi ular: mulai di tengah grid, panjang 3, arah ke kanan
    start_x = snap_to_grid(WIDTH // 2, BLOCK_SIZE)
    start_y = snap_to_grid(HEIGHT // 2, BLOCK_SIZE)
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    current_dir = DIR_RIGHT
    next_dir = DIR_RIGHT

    # Makanan pertama
    food = random_food_position(snake)

    score = 0
    game_over = False

    while True:
        # 1) Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        next_dir = DIR_UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        next_dir = DIR_DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        next_dir = DIR_LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        next_dir = DIR_RIGHT
                else:
                    # Saat game over, R untuk restart, Esc untuk quit
                    if event.key == pygame.K_r:
                        return main()
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()

        screen.fill(BLACK)
        draw_grid(screen)

        if not game_over:
            # 2) Update arah: cegah 180-derajat
            if next_dir != OPPOSITE.get(current_dir):
                current_dir = next_dir

            # 3) Hitung posisi kepala baru
            head_x, head_y = snake[0]
            dx, dy = current_dir
            new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

            # 4) Deteksi tabrakan dengan dinding
            out_x = new_head[0] < 0 or new_head[0] >= WIDTH
            out_y = new_head[1] < 0 or new_head[1] >= HEIGHT
            if out_x or out_y:
                game_over = True
            else:
                # 5) Deteksi tabrakan dengan tubuh sendiri
                if new_head in snake:
                    game_over = True
                else:
                    # 6) Gerakkan ular: tambah kepala
                    snake.insert(0, new_head)

                    # 7) Makan atau tidak
                    if new_head == food:
                        score += 1
                        food = random_food_position(snake)
                        # Tidak pop ekor => bertambah panjang
                    else:
                        # Hapus ekor agar panjang tetap
                        snake.pop()

        # 8) Gambar entitas
        draw_snake(screen, snake)
        draw_food(screen, food)
        render_text(screen, f"Score: {score}", (10, 8), size=24, color=YELLOW)

        if game_over:
            render_text(
                screen,
                "Game Over! Press R to Restart, Esc to Quit",
                (WIDTH // 2, HEIGHT // 2),
                size=28,
                color=WHITE,
                center=True,
            )

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
