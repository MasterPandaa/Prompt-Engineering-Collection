import pygame
import random
import sys

# --------------------------------------
# Inisialisasi Pygame dan layar
# --------------------------------------
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLOCK_SIZE = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game Snake - Pygame')

# Warna
WHITE = (255, 255, 255)
RED = (220, 30, 30)
GREEN = (30, 200, 30)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

# Font
font = pygame.font.SysFont('consolas', 24)

clock = pygame.time.Clock()
FPS = 10  # kecepatan dasar permainan; bisa Anda ubah

# Arah (dx, dy) berbasis grid
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

def draw_rect(color, grid_pos):
    """Menggambar satu blok di posisi grid (x, y) menggunakan BLOCK_SIZE."""
    x, y = grid_pos
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, color, rect)


def random_food_position(snake_body):
    """Menghasilkan posisi makanan acak di grid yang tidak bertabrakan dengan tubuh ular."""
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE
    all_cells = [(x, y) for x in range(cols) for y in range(rows)]
    snake_set = set(snake_body)
    available = [cell for cell in all_cells if cell not in snake_set]
    if not available:
        return None  # tidak ada ruang tersisa
    return random.choice(available)


def render_score(score):
    """Tampilkan skor di kiri atas."""
    text_surface = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text_surface, (10, 8))


def game_over_screen(score):
    """Layar Game Over dengan opsi untuk main lagi atau keluar."""
    screen.fill(BLACK)
    over_text = font.render("Game Over!", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    hint_text = font.render("Press R to Restart, Q or ESC to Quit", True, WHITE)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    pygame.display.flip()

    # Tunggu input untuk restart/quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    return  # kembali ke game loop untuk restart
        clock.tick(30)


def main():
    # Setup grid
    cols = SCREEN_WIDTH // BLOCK_SIZE
    rows = SCREEN_HEIGHT // BLOCK_SIZE

    # Inisialisasi ular: panjang awal 3, bergerak ke kanan di tengah layar
    start_x = cols // 2
    start_y = rows // 2
    snake = [(start_x - 1, start_y), (start_x, start_y), (start_x + 1, start_y)]
    direction = RIGHT
    pending_direction = RIGHT  # menyimpan input agar tidak langsung berbalik

    # Makanan
    food = random_food_position(snake)
    score = 0

    running = True
    while running:
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # keluar program
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # keluar program
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    # Tentukan arah baru dari input
                    if event.key == pygame.K_UP:
                        new_dir = UP
                    elif event.key == pygame.K_DOWN:
                        new_dir = DOWN
                    elif event.key == pygame.K_LEFT:
                        new_dir = LEFT
                    else:
                        new_dir = RIGHT

                    # Cegah berbalik arah 180 derajat
                    if new_dir != OPPOSITE[direction]:
                        pending_direction = new_dir

        # Update arah secara aman (tidak langsung berbalik)
        direction = pending_direction

        # Hitung posisi kepala baru
        head_x, head_y = snake[-1]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Deteksi tabrakan dinding
        if not (0 <= new_head[0] < cols and 0 <= new_head[1] < rows):
            game_over_screen(score)
            return True  # restart

        # Deteksi tabrakan tubuh sendiri
        if new_head in snake:
            game_over_screen(score)
            return True  # restart

        # Gerakkan ular
        snake.append(new_head)

        # Cek makan makanan
        if food is not None and new_head == food:
            score += 1
            food = random_food_position(snake)
            # Tidak pop tail -> ular bertambah panjang
        else:
            # Pindah biasa: pop tail
            snake.pop(0)

        # Gambar
        screen.fill(BLACK)

        # (Opsional) grid tipis
        for gx in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, GRAY, (gx, 0), (gx, SCREEN_HEIGHT), 1)
        for gy in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, GRAY, (0, gy), (SCREEN_WIDTH, gy), 1)

        # Gambar ular (setiap segmen)
        for segment in snake:
            draw_rect(WHITE, segment)

        # Gambar makanan
        if food is not None:
            draw_rect(RED, food)
        else:
            # Jika tidak ada ruang untuk makanan, artinya menang penuh
            win_text = font.render("You Win! Press R to Restart, Q/ESC to Quit", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            # Tunggu input
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            pygame.quit()
                            sys.exit(0)
                        if event.key == pygame.K_r:
                            return True  # restart
                clock.tick(30)

        # Skor
        render_score(score)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    # Loop utama agar bisa restart setelah game over
    while True:
        should_restart = main()  # jalankan satu sesi permainan
        if not should_restart:
            break

    pygame.quit()
