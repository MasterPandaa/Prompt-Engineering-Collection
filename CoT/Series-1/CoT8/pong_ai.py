import pygame
import random

# ----------------------------
# Konfigurasi dasar
# ----------------------------
WIDTH, HEIGHT = 800, 480
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
BALL_SIZE = 14

PADDLE_SPEED = 6
AI_SPEED = 5  # buat AI tidak terlalu sempurna
BALL_SPEED_X_INIT = 6
BALL_SPEED_Y_MAX = 6  # batas kecepatan vertikal bola

# ----------------------------
# Kelas Game Objects
# ----------------------------
class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # Clamp ke layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def auto_move(self, target_y):
        # target_y = posisi y pusat bola
        if self.rect.centery < target_y:
            self.rect.y += min(self.speed, target_y - self.rect.centery)
        elif self.rect.centery > target_y:
            self.rect.y -= min(self.speed, self.rect.centery - target_y)

        # Clamp ke layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self, size):
        self.rect = pygame.Rect(
            WIDTH // 2 - size // 2,
            HEIGHT // 2 - size // 2,
            size,
            size
        )
        self.vx = random.choice([-1, 1]) * BALL_SPEED_X_INIT
        self.vy = random.randint(-3, 3) or 3  # hindari nol

    def reset(self, direction):
        # direction: -1 (ke kiri), +1 (ke kanan)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vx = direction * BALL_SPEED_X_INIT
        self.vy = random.randint(-3, 3)
        if self.vy == 0:
            self.vy = random.choice([-2, 2])

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Pantulan atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy = -self.vy

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


# ----------------------------
# Fungsi utilitas
# ----------------------------
def handle_paddle_ball_collision(ball: Ball, paddle: Paddle, is_left_paddle: bool):
    if not ball.rect.colliderect(paddle.rect):
        return False

    # Tentukan arah baru horizontal
    ball.vx = -ball.vx

    # Hit factor untuk memvariasikan sudut pantulan berdasarkan titik tumbukan
    paddle_center = paddle.rect.centery
    ball_center = ball.rect.centery
    offset = ball_center - paddle_center  # positif jika kena di bawah pusat paddle
    norm = offset / (paddle.rect.height / 2)  # rentang kira-kira [-1, 1]
    ball.vy = int(norm * BALL_SPEED_Y_MAX)
    if ball.vy == 0:
        ball.vy = random.choice([-2, 2])

    # Geser bola keluar dari paddle untuk menghindari deteksi tumbukan ganda
    if is_left_paddle:
        ball.rect.left = paddle.rect.right
    else:
        ball.rect.right = paddle.rect.left

    return True


def draw_center_line(surface):
    # Garis tengah putus-putus
    segment = 10
    gap = 10
    x = WIDTH // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.line(surface, WHITE, (x, y), (x, min(y + segment, HEIGHT)), 2)
        y += segment + gap


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Objek
    player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)
    ai = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, AI_SPEED)
    ball = Ball(BALL_SIZE)

    player_score = 0
    ai_score = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # 1) Event handling (quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Input pemain (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_s]:
            dy += player.speed
        player.move(dy)

        # 3) Gerak AI mengikuti bola
        ai.auto_move(ball.rect.centery)

        # 4) Update bola
        ball.update()

        # 5) Tabrakan bola dengan paddle
        if ball.rect.left <= player.rect.right and ball.rect.colliderect(player.rect):
            handle_paddle_ball_collision(ball, player, is_left_paddle=True)
        elif ball.rect.right >= ai.rect.left and ball.rect.colliderect(ai.rect):
            handle_paddle_ball_collision(ball, ai, is_left_paddle=False)

        # 6) Skor jika bola keluar kiri/kanan
        if ball.rect.right < 0:
            ai_score += 1
            ball.reset(direction=1)
        elif ball.rect.left > WIDTH:
            player_score += 1
            ball.reset(direction=-1)

        # 7) Render
        screen.fill(BLACK)
        draw_center_line(screen)

        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = font.render(f"{player_score}   {ai_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, 40))
        screen.blit(score_text, score_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
