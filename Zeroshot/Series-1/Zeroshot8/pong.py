import pygame
import random

# Konfigurasi dasar
WIDTH, HEIGHT = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ukuran paddle dan bola
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

# Kecepatan
PLAYER_SPEED = 6
AI_SPEED = 5.2  # Sedikit lebih lambat dari pemain agar adil
BALL_SPEED_X = 5
BALL_SPEED_Y = 4

# Margin skor dari atas
SCORE_MARGIN_TOP = 30


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.vel_y = 0

    def move(self, direction, bounds_height):
        # direction: -1 (up), 1 (down), 0 (none)
        self.vel_y = direction * self.speed
        self.rect.y += self.vel_y
        # Batasi dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > bounds_height:
            self.rect.bottom = bounds_height

    def ai_follow(self, target_y, bounds_height):
        # Gerakkan paddle AI ke arah posisi Y bola dengan batas kecepatan
        center_y = self.rect.centery
        if abs(target_y - center_y) > AI_SPEED:
            direction = 1 if target_y > center_y else -1
        else:
            direction = 0
        self.move(direction, bounds_height)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)


class Ball:
    def __init__(self, x, y, size, speed_x, speed_y):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.base_speed_x = speed_x
        self.base_speed_y = speed_y
        self.vel_x = 0
        self.vel_y = 0
        self.reset(center_to_right=random.choice([True, False]))

    def reset(self, center_to_right=True):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        # Arah horizontal ke kanan jika True, ke kiri jika False
        self.vel_x = self.base_speed_x if center_to_right else -self.base_speed_x
        # Variasikan arah vertikal awal
        self.vel_y = random.choice([-self.base_speed_y, self.base_speed_y])

    def update(self):
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Pantul atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)

    def paddle_bounce(self, paddle_rect):
        # Pantulkan arah X dan ubah sudut berdasarkan titik benturan dengan paddle
        if self.vel_x == 0:  # proteksi, harusnya jarang terjadi
            self.vel_x = self.base_speed_x

        # Hit position relatif terhadap pusat paddle: -0.5..0.5
        offset = (self.rect.centery - paddle_rect.centery) / (paddle_rect.height / 2)
        offset = max(-1.0, min(1.0, offset))

        # Kecepatan setelah pantul: sedikit meningkat
        speed = (abs(self.vel_x) + 0.4)
        speed = min(speed, 12)  # batasi maksimal

        # Sudutkan laju: komponen Y dipengaruhi offset
        self.vel_x = -speed if self.vel_x > 0 else speed
        self.vel_y = offset * speed

        # Pastikan bola tidak menempel pada paddle (geser keluar)
        if self.vel_x < 0:
            self.rect.right = paddle_rect.left
        else:
            self.rect.left = paddle_rect.right


def draw_center_line(surface):
    # Garis tengah putus-putus
    dash_height = 16
    gap = 10
    x = WIDTH // 2 - 1
    for y in range(0, HEIGHT, dash_height + gap):
        pygame.draw.rect(surface, WHITE, (x, y, 2, dash_height))


def main():
    pygame.init()
    pygame.display.set_caption("Pong")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Buat objek paddle & bola
    player = Paddle(x=30, y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
                    width=PADDLE_WIDTH, height=PADDLE_HEIGHT, speed=PLAYER_SPEED)
    ai = Paddle(x=WIDTH - 30 - PADDLE_WIDTH, y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
                width=PADDLE_WIDTH, height=PADDLE_HEIGHT, speed=AI_SPEED)
    ball = Ball(x=WIDTH // 2 - BALL_SIZE // 2, y=HEIGHT // 2 - BALL_SIZE // 2,
                size=BALL_SIZE, speed_x=BALL_SPEED_X, speed_y=BALL_SPEED_Y)

    # Skor
    score_player = 0
    score_ai = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_w]:
            direction -= 1
        if keys[pygame.K_s]:
            direction += 1

        # Update pemain
        player.move(direction, HEIGHT)

        # Update AI (ikuti bola)
        ai.ai_follow(ball.rect.centery, HEIGHT)

        # Update bola
        ball.update()

        # Cek tabrakan dengan paddle
        if ball.rect.colliderect(player.rect) and ball.vel_x < 0:
            ball.paddle_bounce(player.rect)
        elif ball.rect.colliderect(ai.rect) and ball.vel_x > 0:
            ball.paddle_bounce(ai.rect)

        # Cek skor: bola keluar kiri/kanan
        if ball.rect.right < 0:
            # AI mendapat poin
            score_ai += 1
            ball.reset(center_to_right=True)  # arah ke kanan (ke AI)
        elif ball.rect.left > WIDTH:
            # Pemain mendapat poin
            score_player += 1
            ball.reset(center_to_right=False)  # arah ke kiri (ke pemain)

        # Render
        screen.fill(BLACK)
        draw_center_line(screen)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = font.render(f"{score_player}   {score_ai}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, SCORE_MARGIN_TOP))
        screen.blit(score_text, score_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
