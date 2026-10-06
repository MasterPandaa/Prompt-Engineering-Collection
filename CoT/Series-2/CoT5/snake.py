import sys
import random
import pygame

# -----------------------------
# Konfigurasi dasar
# -----------------------------
WIDTH, HEIGHT = 600, 400       # Resolusi layar
BLOCK_SIZE = 20                # Ukuran grid per blok
SPEED = 10                     # FPS, semakin tinggi semakin cepat

# Warna
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREEN  = (0, 200, 0)
RED    = (220, 30, 30)
GRAY   = (40, 40, 40)
YELLOW = (240, 220, 70)

# -----------------------------
# Utilitas
# -----------------------------
def draw_grid(surface):
    """Gambar garis grid opsional untuk estetika/debug"""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)


def spawn_food(snake):
    """Munculkan makanan di sel acak yang tidak ditempati ular"""
    occupied = set(snake)
    while True:
        x = random.randrange(0, WIDTH, BLOCK_SIZE)
        y = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if (x, y) not in occupied:
            return (x, y)


def is_opposite(dir_a, dir_b):
    """True jika dir_b adalah kebalikan 180° dari dir_a"""
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


def draw_snake(surface, snake):
    for i, (x, y) in enumerate(snake):
        color = GREEN if i > 0 else YELLOW  # kepala kuning
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)  # outline


def draw_food(surface, food_pos):
    rect = pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, RED, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def render_text(surface, text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)


# -----------------------------
# Game utama
# -----------------------------

def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)
    big_font = pygame.font.SysFont("consolas", 36, bold=True)

    def reset_game():
        # Kepala di tengah grid
        grid_x = (WIDTH // (2 * BLOCK_SIZE)) * BLOCK_SIZE
        grid_y = (HEIGHT // (2 * BLOCK_SIZE)) * BLOCK_SIZE
        head = (grid_x, grid_y)
        # Tubuh awal: 3 segmen ke kiri dari kepala
        snake = [
            head,
            (head[0] - BLOCK_SIZE, head[1]),
            (head[0] - 2 * BLOCK_SIZE, head[1]),
        ]
        direction = (1, 0)  # bergerak ke kanan
        food = spawn_food(snake)
        score = 0
        return snake, direction, food, score

    snake, direction, food, score = reset_game()
    game_over = False

    # Buffer arah agar perubahan arah hanya dieksekusi sekali per frame
    pending_direction = direction

    while True:
        # -------------------------
        # Event Handling
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        snake, direction, food, score = reset_game()
                        game_over = False
                        pending_direction = direction
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        new_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        new_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        new_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        new_dir = (1, 0)
                    else:
                        new_dir = None

                    if new_dir is not None and not is_opposite(direction, new_dir):
                        # Simpan untuk diterapkan sekali per frame
                        pending_direction = new_dir

        # -------------------------
        # Update
        # -------------------------
        if not game_over:
            # Terapkan perubahan arah yang valid
            direction = pending_direction

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

            # Cek tabrakan dinding
            out_of_bounds = (
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT
            )

            # Sisipkan kepala baru
            snake.insert(0, new_head)

            # Cek tabrakan diri (kepala terhadap tubuh)
            hit_self = new_head in snake[1:]

            if out_of_bounds or hit_self:
                game_over = True
            else:
                # Makan?
                if new_head == food:
                    score += 1
                    food = spawn_food(snake)
                    # Tidak pop ekor -> panjang bertambah
                else:
                    # Bergerak biasa -> buang ekor
                    snake.pop()

        # -------------------------
        # Render
        # -------------------------
        screen.fill(BLACK)
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)

        render_text(screen, f"Score: {score}", font, WHITE, (80, 20))

        if game_over:
            render_text(screen, "GAME OVER", big_font, YELLOW, (WIDTH // 2, HEIGHT // 2 - 20))
            render_text(screen, "Press R/Enter/Space to Restart", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 20))
            render_text(screen, "Press Q/Esc to Quit", font, GRAY, (WIDTH // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(SPEED)


if __name__ == "__main__":
    main()
