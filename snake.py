import pygame
import random
import sys

# Konstanta permainan
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20  # ukuran grid
GRID_COLS = WIDTH // CELL_SIZE
GRID_ROWS = HEIGHT // CELL_SIZE

# Kecepatan ular (frame per detik)
SNAKE_SPEED = 12

# Warna
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 30, 30)

# Arah gerak (dx, dy) dalam unit grid
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

def grid_to_pixel(cell):
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE

def random_empty_cell(occupied):
    """Pilih posisi makanan acak yang tidak ditempati ular."""
    all_cells = [(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)]
    candidates = [c for c in all_cells if c not in occupied]
    return random.choice(candidates) if candidates else None

def draw_rect_grid(surface):
    # Opsi: menggambar grid tipis agar lebih enak dilihat
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y), 1)

def draw_snake(surface, snake):
    # snake adalah list tuple (x, y) dalam koordinat grid
    for i, (sx, sy) in enumerate(snake):
        px, py = grid_to_pixel((sx, sy))
        color = GREEN if i > 0 else (0, 255, 0)  # kepala sedikit lebih terang
        pygame.draw.rect(surface, color, (px, py, CELL_SIZE, CELL_SIZE))

def draw_food(surface, food):
    fx, fy = food
    px, py = grid_to_pixel((fx, fy))
    # sedikit inset agar terlihat ada jarak
    inset = 3
    pygame.draw.rect(surface, RED, (px + inset, py + inset, CELL_SIZE - 2 * inset, CELL_SIZE - 2 * inset))

def render_text(surface, text, pos, font, color=WHITE):
    img = font.render(text, True, color)
    surface.blit(img, pos)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    def start_new_game():
        # Mulai dari tengah layar, panjang awal 3 segmen, bergerak ke kanan
        center = (GRID_COLS // 2, GRID_ROWS // 2)
        snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        direction = RIGHT
        score = 0
        food = random_empty_cell(set(snake))
        return snake, direction, score, food

    snake, direction, score, food = start_new_game()
    pending_direction = direction  # untuk mencegah reverse instan
    running = True
    game_over = False

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        if OPPOSITE.get(direction) != UP:
                            pending_direction = UP
                    elif event.key == pygame.K_DOWN:
                        if OPPOSITE.get(direction) != DOWN:
                            pending_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        if OPPOSITE.get(direction) != LEFT:
                            pending_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        if OPPOSITE.get(direction) != RIGHT:
                            pending_direction = RIGHT
                else:
                    # Saat game over: R untuk restart, Q atau ESC untuk keluar
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        snake, direction, score, food = start_new_game()
                        pending_direction = direction
                        game_over = False
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False

        if not game_over:
            # Update arah (hindari reverse)
            if pending_direction and OPPOSITE.get(direction) != pending_direction:
                direction = pending_direction

            # Gerakkan ular: hitung kepala baru
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Cek tabrak dinding
            if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
                game_over = True
            # Cek tabrak diri sendiri
            elif new_head in snake:
                game_over = True
            else:
                # Tambahkan kepala
                snake.insert(0, new_head)

                # Cek makan
                if food and new_head == food:
                    score += 1
                    # Spawn makanan baru
                    occupied = set(snake)
                    food = random_empty_cell(occupied)
                else:
                    # Gerakkan dengan menghapus ekor
                    snake.pop()

        # Gambar
        screen.fill(BLACK)
        draw_rect_grid(screen)
        draw_snake(screen, snake)
        if food:
            draw_food(screen, food)

        # Skor
        render_text(screen, f"Skor: {score}", (10, 8), font, WHITE)

        # Tampilkan Game Over jika perlu
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg1 = "GAME OVER"
            msg2 = "Tekan R untuk main lagi, Q untuk keluar"
            msg1_img = big_font.render(msg1, True, WHITE)
            msg2_img = font.render(msg2, True, WHITE)
            screen.blit(msg1_img, (WIDTH // 2 - msg1_img.get_width() // 2, HEIGHT // 2 - 48))
            screen.blit(msg2_img, (WIDTH // 2 - msg2_img.get_width() // 2, HEIGHT // 2 + 8))

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
