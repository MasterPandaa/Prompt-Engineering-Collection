import sys
import random
import pygame

# Inisialisasi Pygame
pygame.init()

# Konstanta layar
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WINDOW_TITLE = "Pong dengan AI (Pygame)"

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Setup window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()
FPS = 60

# Parameter permainan
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
PLAYER_SPEED = 6
AI_MAX_SPEED = 5
BALL_SIZE = 12
BALL_START_SPEED_X = 5
BALL_START_SPEED_Y = 4
BALL_SPEEDUP_FACTOR = 1.05  # percepatan tiap kena paddle
SCORE_TO_WIN = 10

# Font untuk skor
try:
    score_font = pygame.font.SysFont("consolas", 36)
except Exception:
    score_font = pygame.font.Font(None, 36)


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, speed: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def move(self, y_change: float):
        self.rect.y += y_change
        # Batasi agar tidak keluar layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Ball:
    def __init__(self, x: int, y: int, size: int, vel_x: float, vel_y: float):
        self.rect = pygame.Rect(x, y, size, size)
        self.vx = vel_x
        self.vy = vel_y
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def reset(self, direction: int = 1):
        # direction: 1 ke kanan, -1 ke kiri
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        base_vx = BALL_START_SPEED_X * direction
        base_vy = random.choice([-BALL_START_SPEED_Y, BALL_START_SPEED_Y])
        self.vx, self.vy = base_vx, base_vy

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        # Pantulan atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy *= -1


def ai_follow_ball(ai_paddle: Paddle, ball: Ball):
    # AI akan berusaha memposisikan pusat paddle sejajar dengan pusat Y bola
    target_y = ball.rect.centery
    center_y = ai_paddle.rect.centery

    if abs(target_y - center_y) < AI_MAX_SPEED:
        dy = target_y - center_y
    else:
        dy = AI_MAX_SPEED if target_y > center_y else -AI_MAX_SPEED

    ai_paddle.move(dy)


def handle_paddle_collision(ball: Ball, paddle: Paddle, is_left: bool):
    # Deteksi dan respon tabrakan bola dengan paddle
    if ball.rect.colliderect(paddle.rect):
        # Tentukan sisi mana yang bertabrakan dan reposisi agar tidak saling menembus
        if is_left:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left
        # Balik arah X dan sedikit percepat
        ball.vx *= -BALL_SPEEDUP_FACTOR
        # Beri efek arah vertikal berdasarkan titik tumbukan relatif
        offset = (ball.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        ball.vy += offset * 2.0  # tweak sensitivitas
        # Clamp vy agar tidak terlalu lambat/terlalu cepat
        ball.vy = max(min(ball.vy, 10), -10)


def draw_center_line(surface):
    # Garis putus-putus di tengah
    segment_height = 15
    gap = 10
    x = SCREEN_WIDTH // 2 - 1
    for y in range(0, SCREEN_HEIGHT, segment_height + gap):
        pygame.draw.rect(surface, GREY, pygame.Rect(x, y, 2, segment_height))


def main():
    # Objek permainan
    player = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PLAYER_SPEED)
    ai = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, AI_MAX_SPEED)
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE,
                random.choice([-BALL_START_SPEED_X, BALL_START_SPEED_X]),
                random.choice([-BALL_START_SPEED_Y, BALL_START_SPEED_Y]))

    score_left = 0
    score_right = 0

    running = True
    while running:
        dt = clock.tick(FPS)  # batas FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Input pemain (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_s]:
            dy += player.speed
        player.move(dy)

        # AI mengikuti bola
        ai_follow_ball(ai, ball)

        # Update bola
        ball.update()

        # Cek tabrakan bola dengan paddle
        handle_paddle_collision(ball, player, is_left=True)
        handle_paddle_collision(ball, ai, is_left=False)

        # Cek jika bola keluar kiri/kanan (skor)
        if ball.rect.left <= 0:
            score_right += 1
            ball.reset(direction=-1)  # servis ke kiri
        elif ball.rect.right >= SCREEN_WIDTH:
            score_left += 1
            ball.reset(direction=1)  # servis ke kanan

        # Gambar
        screen.fill(BLACK)
        draw_center_line(screen)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        score_text = score_font.render(f"{score_left} : {score_right}", True, WHITE)
        text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(score_text, text_rect)

        # Tampilkan pesan menang jika mencapai skor
        if score_left >= SCORE_TO_WIN or score_right >= SCORE_TO_WIN:
            winner = "Pemain" if score_left > score_right else "AI"
            win_text = score_font.render(f"{winner} Menang! Tekan ESC untuk keluar.", True, WHITE)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_text, win_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
