import sys
import random
import pygame

# ---- Konstanta Permainan ----
WIDTH, HEIGHT = 600, 400          # Ukuran layar
CELL_SIZE = 20                    # Ukuran grid (px)
GRID_W = WIDTH // CELL_SIZE
GRID_H = HEIGHT // CELL_SIZE

# Warna
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
RED = (220, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)

# Kecepatan game (frame per detik)
FPS = 12

# Arah (dx, dy) dalam satuan sel/grid
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def spawn_food(snake_body):
    """Menghasilkan posisi makanan acak yang tidak bertabrakan dengan tubuh ular."""
    all_cells = [(x, y) for x in range(GRID_W) for y in range(GRID_H)]
    valid_cells = [c for c in all_cells if c not in snake_body]
    return random.choice(valid_cells) if valid_cells else None


def draw_cell(surface, color, grid_pos):
    """Menggambar satu sel grid sebagai kotak di layar."""
    x, y = grid_pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)


def draw_snake(surface, snake_body):
    """Menggambar ular. Kepala diberi warna hijau yang lebih terang."""
    if not snake_body:
        return
    # Kepala
    draw_cell(surface, GREEN, snake_body[0])
    # Tubuh
    for seg in snake_body[1:]:
        draw_cell(surface, DARK_GREEN, seg)


def draw_food(surface, food_pos):
    """Menggambar makanan."""
    if food_pos is None:
        return
    draw_cell(surface, RED, food_pos)


def draw_grid(surface):
    """Opsional: garis grid halus untuk estetika."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, DARK_GRAY, (0, y), (WIDTH, y), 1)


def opposite_dir(a, b):
    """Cek apakah arah a berlawanan dengan b."""
    return a[0] == -b[0] and a[1] == -b[1]


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20, bold=True)
    big_font = pygame.font.SysFont("consolas", 36, bold=True)

    def reset_game():
        # Mulai dari tengah
        start_x, start_y = GRID_W // 2, GRID_H // 2
        # Ular awal: 3 segmen, bergerak ke kanan
        snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        direction = RIGHT
        next_direction = RIGHT
        food = spawn_food(snake)
        score = 0
        game_over = False
        return snake, direction, next_direction, food, score, game_over

    snake, direction, next_direction, food, score, game_over = reset_game()

    running = True
    while running:
        # ---- Event Handling ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Kontrol arah
                if event.key == pygame.K_UP:
                    if not opposite_dir(UP, direction):
                        next_direction = UP
                elif event.key == pygame.K_DOWN:
                    if not opposite_dir(DOWN, direction):
                        next_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if not opposite_dir(LEFT, direction):
                        next_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if not opposite_dir(RIGHT, direction):
                        next_direction = RIGHT

                # Restart saat Game Over
                if game_over and event.key == pygame.K_r:
                    snake, direction, next_direction, food, score, game_over = reset_game()

        # ---- Update State ----
        if not game_over:
            # Terapkan arah baru jika valid (mencegah balik arah langsung)
            if not opposite_dir(next_direction, direction):
                direction = next_direction

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Cek tabrak dinding
            x, y = new_head
            if x < 0 or x >= GRID_W or y < 0 or y >= GRID_H:
                game_over = True
            # Cek tabrak badan sendiri
            elif new_head in snake:
                game_over = True
            else:
                # Gerakkan ular
                snake.insert(0, new_head)
                if food is not None and new_head == food:
                    score += 1
                    food = spawn_food(snake)
                else:
                    snake.pop()  # geser tanpa tumbuh

        # ---- Render ----
        screen.fill((12, 12, 12))
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)

        # Skor
        score_surf = font.render(f"Score: {score}", True, YELLOW)
        screen.blit(score_surf, (10, 8))

        # Game Over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            go_text = big_font.render("GAME OVER", True, WHITE)
            info_text = font.render("Press R to Restart or Esc to Quit", True, WHITE)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 5))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
