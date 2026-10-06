import pygame
import random
import sys

# ---------- Konfigurasi Dasar ----------
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
GRID_W = WIDTH // BLOCK_SIZE
GRID_H = HEIGHT // BLOCK_SIZE

# Warna
COLOR_BG = (30, 30, 30)
COLOR_SNAKE = (0, 200, 120)
COLOR_SNAKE_HEAD = (0, 255, 160)
COLOR_FOOD = (220, 80, 80)
COLOR_GRID = (45, 45, 45)
COLOR_TEXT = (240, 240, 240)

# Kecepatan ular (step per detik)
SNAKE_SPEED = 12

# Arah
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def draw_grid(surface):
    # Garis grid opsional agar orientasi lebih mudah
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (WIDTH, y))


def draw_rect_cell(surface, color, cell):
    x, y = cell
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)


def draw_snake(surface, snake):
    # Kepala
    if snake:
        draw_rect_cell(surface, COLOR_SNAKE_HEAD, snake[0])
    # Tubuh
    for seg in snake[1:]:
        draw_rect_cell(surface, COLOR_SNAKE, seg)


def random_food_position(snake_set):
    # Spawn makanan di sel kosong acak
    empty_cells = [
        (x, y)
        for x in range(GRID_W)
        for y in range(GRID_H)
        if (x, y) not in snake_set
    ]
    if not empty_cells:
        return None  # artinya snake menutupi grid (menang penuh)
    return random.choice(empty_cells)


def is_opposite(dir_a, dir_b):
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]


def render_text_center(surface, text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)


def game_loop(screen, clock, main_font, small_font):
    # Inisialisasi ular di tengah
    cx, cy = GRID_W // 2, GRID_H // 2
    snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
    direction = RIGHT
    pending_growth = 0
    score = 0

    snake_set = set(snake)
    food = random_food_position(snake_set)

    running = True
    while running:
        # 1) Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if not is_opposite(direction, UP):
                        direction = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if not is_opposite(direction, DOWN):
                        direction = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if not is_opposite(direction, LEFT):
                        direction = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if not is_opposite(direction, RIGHT):
                        direction = RIGHT

        # 2) Update (gerakkan ular)
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Cek tabrakan dinding
        if (
            new_head[0] < 0
            or new_head[0] >= GRID_W
            or new_head[1] < 0
            or new_head[1] >= GRID_H
        ):
            return score  # game over

        # Cek tabrakan badan
        if new_head in snake_set:
            return score  # game over

        # Masukkan kepala baru
        snake.insert(0, new_head)
        snake_set.add(new_head)

        # Cek makan
        if food is not None and new_head == food:
            score += 1
            pending_growth += 1
            # Spawn makanan baru
            food = random_food_position(snake_set)
        else:
            # Jika tidak makan, hapus ekor kecuali sedang tumbuh
            if pending_growth > 0:
                pending_growth -= 1
            else:
                tail = snake.pop()
                snake_set.remove(tail)

        # 3) Render
        screen.fill(COLOR_BG)
        draw_grid(screen)
        # Gambar makanan
        if food is not None:
            draw_rect_cell(screen, COLOR_FOOD, food)
        # Gambar ular
        draw_snake(screen, snake)

        # Tampilkan skor
        score_text = main_font.render(f"Score: {score}", True, COLOR_TEXT)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)


def game_over_screen(screen, main_font, small_font, score):
    screen.fill(COLOR_BG)
    render_text_center(screen, "Game Over", main_font, COLOR_TEXT, HEIGHT // 2 - 20)
    render_text_center(
        screen, f"Score: {score}", small_font, COLOR_TEXT, HEIGHT // 2 + 10
    )
    render_text_center(
        screen, "Press R to Restart or Q to Quit", small_font, COLOR_TEXT, HEIGHT // 2 + 40
    )
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    waiting = False


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Pygame")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("consolas", 28)
    small_font = pygame.font.SysFont("consolas", 20)

    while True:
        score = game_loop(screen, clock, main_font, small_font)
        game_over_screen(screen, main_font, small_font, score)


if __name__ == "__main__":
    main()
