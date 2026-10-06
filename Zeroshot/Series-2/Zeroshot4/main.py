import pygame
import random
import sys

# --- Konstanta Permainan ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 30, 30)
DARK_GREY = (30, 30, 30)

# Arah (dx, dy) dalam satuan grid
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


def random_food_position(exclude_positions):
    """Menghasilkan posisi makanan acak pada grid yang tidak menabrak tubuh ular."""
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        pos = (x, y)
        if pos not in exclude_positions:
            return pos


def draw_rect_cell(surface, color, pos):
    x, y = pos
    pygame.draw.rect(
        surface,
        color,
        pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        border_radius=4,
    )


def draw_grid(surface):
    # Grid tipis opsional untuk mempercantik (bisa dimatikan jika ingin polos)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, DARK_GREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, DARK_GREY, (0, y), (WIDTH, y))


def render_text(surface, text, size, color, center=None, topleft=None):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center is not None:
        rect.center = center
    if topleft is not None:
        rect.topleft = topleft
    surface.blit(img, rect)


def game_loop():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Inisialisasi ular di tengah layar, panjang awal 3 segmen
    start_x = GRID_WIDTH // 2
    start_y = GRID_HEIGHT // 2
    snake = [
        (start_x, start_y),
        (start_x - 1, start_y),
        (start_x - 2, start_y),
    ]
    direction = RIGHT
    pending_direction = RIGHT  # menampung input player untuk diterapkan di frame berikutnya

    score = 0
    food = random_food_position(set(snake))

    running = True
    game_over = False

    while running:
        # --- Event ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        if direction != OPPOSITE[UP]:
                            pending_direction = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if direction != OPPOSITE[DOWN]:
                            pending_direction = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if direction != OPPOSITE[LEFT]:
                            pending_direction = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if direction != OPPOSITE[RIGHT]:
                            pending_direction = RIGHT
                else:
                    # Layar Game Over: R untuk restart, ESC/Q untuk keluar
                    if event.key in (pygame.K_r,):
                        return True  # sinyal untuk restart
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False

        if not game_over:
            # Terapkan arah input yang valid
            direction = pending_direction

            # Gerakkan ular: tambahkan kepala baru berdasarkan arah
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Cek tabrakan dengan dinding
            if (
                new_head[0] < 0
                or new_head[0] >= GRID_WIDTH
                or new_head[1] < 0
                or new_head[1] >= GRID_HEIGHT
            ):
                game_over = True
            else:
                # Cek tabrakan dengan tubuh sendiri
                if new_head in snake:
                    game_over = True
                else:
                    snake.insert(0, new_head)

                    # Cek makanan
                    if new_head == food:
                        score += 1
                        food = random_food_position(set(snake))
                        # Tidak pop tail -> ular bertambah panjang
                    else:
                        # Pindahkan dengan menghapus ekor
                        snake.pop()

        # --- Gambar ---
        screen.fill(BLACK)
        # draw_grid(screen)  # aktifkan jika ingin terlihat grid

        # Gambar makanan dan ular
        draw_rect_cell(screen, RED, food)
        for idx, seg in enumerate(snake):
            seg_color = GREEN if idx == 0 else (0, 160, 0)
            draw_rect_cell(screen, seg_color, seg)

        # Tampilkan skor
        render_text(screen, f"Score: {score}", 28, WHITE, topleft=(10, 8))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            render_text(screen, "GAME OVER", 48, WHITE, center=(WIDTH // 2, HEIGHT // 2 - 20))
            render_text(screen, f"Score: {score}", 36, WHITE, center=(WIDTH // 2, HEIGHT // 2 + 20))
            render_text(
                screen,
                "Press R to Restart | ESC to Quit",
                24,
                WHITE,
                center=(WIDTH // 2, HEIGHT // 2 + 60),
            )

        pygame.display.flip()

        # Kecepatan permainan (FPS)
        # Nilai 10-15 nyaman untuk Snake klasik
        clock.tick(12)

    return False  # keluar game


if __name__ == "__main__":
    # Dukungan restart sederhana: selama game_loop() return True, mulai ulang
    while True:
        want_restart = game_loop()
        if not want_restart:
            break
    pygame.quit()
    sys.exit()
