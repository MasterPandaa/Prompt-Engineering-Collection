import pygame
import random
import sys

# Konstanta
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
FPS = 10  # kecepatan permainan (semakin besar, semakin cepat)

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
GRAY = (60, 60, 60)

# Arah (dx, dy) dalam kelipatan BLOCK_SIZE
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

def grid_random_pos(excluded_positions):
    """Menghasilkan posisi acak pada grid yang tidak bertabrakan dengan 'excluded_positions' (set of (x, y))."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Kumpulkan semua sel kosong
    free_cells = []
    for c in range(cols):
        for r in range(rows):
            x = c * BLOCK_SIZE
            y = r * BLOCK_SIZE
            if (x, y) not in excluded_positions:
                free_cells.append((x, y))

    if not free_cells:
        return None  # tidak ada tempat kosong (menang penuh layar)
    return random.choice(free_cells)

def draw_block(surface, color, pos):
    """Gambar satu blok di posisi pos=(x, y)."""
    x, y = pos
    pygame.draw.rect(surface, color, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))

def draw_snake(surface, snake):
    """Gambar seluruh segmen ular (list of (x, y))."""
    # Kepala beda warna sedikit
    if snake:
        draw_block(surface, GREEN, snake[0])  # kepala
        for seg in snake[1:]:
            draw_block(surface, WHITE, seg)

def draw_grid(surface):
    """Garis grid opsional (visual)."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

def render_text(surface, text, font, color, topleft):
    img = font.render(text, True, color)
    surface.blit(img, topleft)

def game_loop(screen, clock, font):
    # Inisialisasi ular (panjang awal 3)
    start_x = SCREEN_WIDTH // 2 // BLOCK_SIZE * BLOCK_SIZE
    start_y = SCREEN_HEIGHT // 2 // BLOCK_SIZE * BLOCK_SIZE
    snake = [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]
    snake_set = set(snake)  # untuk lookup cepat

    current_dir = RIGHT
    next_dir = RIGHT

    score = 0

    # Makanan awal
    food_pos = grid_random_pos(set(snake))
    if food_pos is None:
        # Kondisi sangat jarang, tapi berjaga-jaga
        food_pos = (0, 0)

    running = True
    while running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # keluar game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    next_dir = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    next_dir = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    next_dir = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    next_dir = RIGHT

        # Cegah berbalik arah langsung (180 derajat)
        if next_dir != OPPOSITE.get(current_dir, None):
            current_dir = next_dir

        # Hitung posisi kepala baru
        head_x, head_y = snake[0]
        dx, dy = current_dir
        new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

        # Deteksi tabrakan dinding
        x, y = new_head
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
            if not game_over_screen(screen, clock, font, score):
                return False
            return True  # restart game

        # Deteksi tabrakan tubuh (kecuali jika memakan ekor yang bergerak)
        # Kita akan cek sebelum mem-pop tail hanya jika tidak makan
        will_eat = (new_head == food_pos)

        if will_eat:
            # Jika makan, kepala masuk ke sel makanan (boleh menabrak posisi ekor lama, karena ekor tak dipop)
            if new_head in snake_set:
                if not game_over_screen(screen, clock, font, score):
                    return False
                return True
            # Tambah kepala, tidak hapus ekor
            snake.insert(0, new_head)
            snake_set.add(new_head)
            score += 1
            # Spawn food baru
            food_pos = grid_random_pos(set(snake))
            if food_pos is None:
                # Menang: layar penuh oleh ular
                if not game_over_screen(screen, clock, font, score, win=True):
                    return False
                return True
        else:
            # Bergerak normal: tambahkan kepala, hapus ekor
            tail = snake[-1]
            # Hapus tail dari set sementara, lalu cek self-collision
            snake_set.remove(tail)
            if new_head in snake_set:
                # Tabrak tubuh
                if not game_over_screen(screen, clock, font, score):
                    return False
                return True
            snake.insert(0, new_head)
            snake.pop()
            snake_set.add(new_head)

        # Render
        screen.fill(BLACK)
        # Optional: grid
        # draw_grid(screen)

        # Gambar makanan
        draw_block(screen, RED, food_pos)

        # Gambar ular
        draw_snake(screen, snake)

        # Tampilkan skor
        render_text(screen, f"Score: {score}", font, WHITE, (10, 8))

        pygame.display.flip()

def game_over_screen(screen, clock, font, score, win=False):
    """Tampilkan layar Game Over, kembali True jika restart, False jika keluar."""
    title = "You Win!" if win else "Game Over"
    info1 = "Press R to Restart"
    info2 = "Press Q or ESC to Quit"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
                if event.key == pygame.K_r:
                    return True
        screen.fill(BLACK)
        render_text(screen, title, font, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 60))
        render_text(screen, f"Score: {score}", font, WHITE, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 30))
        render_text(screen, info1, font, WHITE, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 10))
        render_text(screen, info2, font, WHITE, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 40))
        pygame.display.flip()
        clock.tick(30)

def main():
    pygame.init()
    pygame.display.set_caption("Contoh Game Snake")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    # Loop utama yang memungkinkan restart
    while True:
        result = game_loop(screen, clock, font)
        if result is False:
            break  # keluar game

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
