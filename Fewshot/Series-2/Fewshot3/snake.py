import pygame
import random
import sys

# ---------- Konfigurasi ----------
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
GRID_COLS = SCREEN_WIDTH // BLOCK_SIZE
GRID_ROWS = SCREEN_HEIGHT // BLOCK_SIZE

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 200, 0)
DARK_GRAY = (40, 40, 40)

# Kecepatan (blok per detik)
SNAKE_SPEED = 10

# ---------- Utilitas ----------
def random_food_position(snake_body):
    """Kembalikan posisi food (grid-aligned) yang tidak menabrak tubuh ular."""
    while True:
        x = random.randint(0, GRID_COLS - 1) * BLOCK_SIZE
        y = random.randint(0, GRID_ROWS - 1) * BLOCK_SIZE
        if (x, y) not in snake_body:
            return x, y

def draw_grid(surface):
    # Garis grid opsional agar rapi
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_snake(surface, snake_body):
    for (x, y) in snake_body:
        pygame.draw.rect(surface, WHITE, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))

def draw_food(surface, pos):
    x, y = pos
    pygame.draw.rect(surface, RED, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))

def show_score(surface, score, font):
    text = font.render(f"Score: {score}", True, GREEN)
    surface.blit(text, (10, 8))

def game_over_screen(surface, score, font_big, font_small):
    surface.fill(BLACK)
    title = font_big.render("GAME OVER", True, RED)
    rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    surface.blit(title, rect)

    score_text = font_small.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
    surface.blit(score_text, score_rect)

    info = font_small.render("Press R to Restart or Q/Esc to Quit", True, WHITE)
    info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    surface.blit(info, info_rect)

    pygame.display.flip()

# ---------- Game Loop ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Contoh Game Snake")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 24)
    font_big = pygame.font.SysFont(None, 64)

    # State awal
    snake_body = [
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH // 2 - BLOCK_SIZE, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH // 2 - 2 * BLOCK_SIZE, SCREEN_HEIGHT // 2),
    ]
    direction = (BLOCK_SIZE, 0)  # Mulai bergerak ke kanan
    pending_direction = direction  # Menangkap input tapi mencegah berbalik arah
    food_pos = random_food_position(snake_body)
    score = 0
    game_over = False

    # Waktu update berbasis grid (agar konstan di FPS berbeda)
    move_delay = 1.0 / SNAKE_SPEED
    accumulator = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        accumulator += dt

        # ---------- Event ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        # Reset game
                        snake_body = [
                            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                            (SCREEN_WIDTH // 2 - BLOCK_SIZE, SCREEN_HEIGHT // 2),
                            (SCREEN_WIDTH // 2 - 2 * BLOCK_SIZE, SCREEN_HEIGHT // 2),
                        ]
                        direction = (BLOCK_SIZE, 0)
                        pending_direction = direction
                        food_pos = random_food_position(snake_body)
                        score = 0
                        game_over = False
                        accumulator = 0.0
                else:
                    # Kontrol arah, mencegah berbalik arah
                    if event.key == pygame.K_UP:
                        new_dir = (0, -BLOCK_SIZE)
                    elif event.key == pygame.K_DOWN:
                        new_dir = (0, BLOCK_SIZE)
                    elif event.key == pygame.K_LEFT:
                        new_dir = (-BLOCK_SIZE, 0)
                    elif event.key == pygame.K_RIGHT:
                        new_dir = (BLOCK_SIZE, 0)
                    else:
                        new_dir = None

                    if new_dir is not None:
                        # Cegah berbalik: (dx,dy) + (ndx,ndy) != (0,0)
                        if (new_dir[0] + direction[0], new_dir[1] + direction[1]) != (0, 0):
                            pending_direction = new_dir

        if game_over:
            game_over_screen(screen, score, font_big, font_small)
            continue

        # ---------- Update per langkah grid ----------
        while accumulator >= move_delay:
            accumulator -= move_delay

            # Terapkan pending_direction sekali per langkah
            direction = pending_direction

            head_x, head_y = snake_body[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Deteksi tabrakan dinding
            if not (0 <= new_head[0] < SCREEN_WIDTH and 0 <= new_head[1] < SCREEN_HEIGHT):
                game_over = True
                break

            # Deteksi tabrakan tubuh sendiri
            if new_head in snake_body:
                game_over = True
                break

            # Gerakkan ular
            snake_body.insert(0, new_head)

            # Cek makan makanan
            if new_head == food_pos:
                score += 1
                food_pos = random_food_position(snake_body)
                # Tidak pop tail: ular bertambah panjang
            else:
                snake_body.pop()  # gerak biasa: buang ekor

        # ---------- Render ----------
        screen.fill(BLACK)
        draw_grid(screen)
        draw_snake(screen, snake_body)
        draw_food(screen, food_pos)
        show_score(screen, score, font_small)
        pygame.display.flip()

if __name__ == "__main__":
    main()
