import pygame
import random
import sys

# Konfigurasi utama
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 12  # Kecepatan permainan

# Warna
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

# Arah gerak (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def random_food_position(snake_body):
    """Menghasilkan posisi makanan acak pada grid, tidak menabrak tubuh ular."""
    grid_w = SCREEN_WIDTH // BLOCK_SIZE
    grid_h = SCREEN_HEIGHT // BLOCK_SIZE

    empty_cells = {(x, y) for x in range(grid_w) for y in range(grid_h)} - set(snake_body)
    if not empty_cells:
        # Tidak ada tempat tersisa; pemain menang secara teknis
        return None

    x, y = random.choice(tuple(empty_cells))
    return (x, y)

def draw_grid(surface):
    """Gambar grid halus supaya lebih rapi."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

def draw_snake(surface, snake_body):
    """Gambar ular. snake_body berisi list tuple (grid_x, grid_y)."""
    for i, (gx, gy) in enumerate(snake_body):
        rect = pygame.Rect(gx * BLOCK_SIZE, gy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        color = DARK_GREEN if i == 0 else GREEN  # Kepala lebih gelap
        pygame.draw.rect(surface, color, rect)

def draw_food(surface, food_pos):
    """Gambar makanan."""
    if food_pos is None:
        return
    fx, fy = food_pos
    rect = pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, RED, rect)

def render_text(surface, text, font, color, topleft):
    img = font.render(text, True, color)
    surface.blit(img, topleft)

def is_opposite(dir_a, dir_b):
    """Cek apakah dir_b adalah kebalikan dari dir_a."""
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]

def game_loop(screen, clock, font):
    # Inisialisasi ular di tengah layar (dalam koordinat grid)
    start_x = (SCREEN_WIDTH // BLOCK_SIZE) // 2
    start_y = (SCREEN_HEIGHT // BLOCK_SIZE) // 2
    snake_body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    current_direction = RIGHT
    next_direction = RIGHT

    food_pos = random_food_position(snake_body)
    score = 0

    running = True
    while running:
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"  # Keluar ke menu utama
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not is_opposite(current_direction, UP):
                        next_direction = UP
                elif event.key == pygame.K_DOWN:
                    if not is_opposite(current_direction, DOWN):
                        next_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if not is_opposite(current_direction, LEFT):
                        next_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if not is_opposite(current_direction, RIGHT):
                        next_direction = RIGHT

        # Update
        current_direction = next_direction
        head_x, head_y = snake_body[0]
        dx, dy = current_direction
        new_head = (head_x + dx, head_y + dy)

        # Deteksi tabrakan dinding
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH // BLOCK_SIZE or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT // BLOCK_SIZE):
            return "game_over", score

        # Deteksi tabrakan dengan tubuh sendiri
        if new_head in snake_body:
            return "game_over", score

        # Gerakkan ular
        snake_body.insert(0, new_head)

        # Makan makanan
        if food_pos is not None and new_head == food_pos:
            score += 1
            food_pos = random_food_position(snake_body)
            # Jika food_pos None, berarti tidak ada tempat kosong: menang
        else:
            snake_body.pop()  # Hapus ekor jika tidak makan

        # Render
        screen.fill(BLACK)
        draw_grid(screen)
        draw_food(screen, food_pos)
        draw_snake(screen, snake_body)
        render_text(screen, f"Skor: {score}", font, WHITE, (10, 8))

        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(screen, font_big, font, score):
    """Tampilan Game Over dengan opsi restart atau keluar."""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return "quit"

        screen.fill(BLACK)
        render_text(screen, "GAME OVER", font_big, WHITE, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 70))
        render_text(screen, f"Skor: {score}", font, WHITE, (SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT // 2))
        render_text(screen, "Tekan R untuk main lagi", font, WHITE, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 40))
        render_text(screen, "Tekan Q untuk keluar", font, WHITE, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 70))

        pygame.display.flip()

def main():
    pygame.init()
    pygame.display.set_caption("Contoh Game Snake")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Font
    font = pygame.font.SysFont("consolas", 22)
    font_big = pygame.font.SysFont("consolas", 48)

    while True:
        result = game_loop(screen, clock, font)
        if result == "quit":
            break
        elif isinstance(result, tuple) and result[0] == "game_over":
            _, score = result
            action = game_over_screen(screen, font_big, font, score)
            if action == "quit":
                break
            # Jika restart, lanjut ke iterasi berikutnya (ulang game_loop)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
