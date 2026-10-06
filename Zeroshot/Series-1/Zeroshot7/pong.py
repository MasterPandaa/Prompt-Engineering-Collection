import sys
import random
import pygame

# Konstanta layar
WIDTH, HEIGHT = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Paddle
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 100
PLAYER_SPEED = 7
AI_SPEED = 6

# Bola
BALL_SIZE = 14
BALL_SPEED = 6


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self, dy):
        self.rect.y += dy
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self, direction=None):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        # Pilih arah acak; pastikan tidak terlalu datar
        angle = random.uniform(-0.8, 0.8)
        vx = 1 if random.random() < 0.5 else -1
        vy = angle
        # Normalisasi kecepatan
        mag = (vx ** 2 + vy ** 2) ** 0.5
        self.vx = (vx / mag) * BALL_SPEED
        self.vy = (vy / mag) * BALL_SPEED
        if direction == "left":
            self.vx = -abs(self.vx)
        elif direction == "right":
            self.vx = abs(self.vx)

    def update(self):
        # Gerak
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Pantul atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


def reflect_ball_from_paddle(ball: Ball, paddle: Paddle):
    # Ketika bola mengenai paddle, balikkan kecepatan X
    # Tambahkan "spin" berdasarkan posisi tumbukan relatif terhadap tengah paddle
    offset = (ball.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
    offset = clamp(offset, -1.0, 1.0)

    speed = (ball.vx ** 2 + ball.vy ** 2) ** 0.5
    # Sudut baru: X berlawanan arah, Y proporsional offset
    ball.vx = -ball.vx
    ball.vy = offset * speed

    # Normalisasi agar kecepatan tetap konstan (sedikit tambah akselerasi kecil)
    speed *= 1.03
    mag = (ball.vx ** 2 + ball.vy ** 2) ** 0.5
    if mag != 0:
        ball.vx = (ball.vx / mag) * speed
        ball.vy = (ball.vy / mag) * speed

    # Pastikan bola tidak "menempel" pada paddle
    if ball.vx > 0:
        ball.rect.left = paddle.rect.right
    else:
        ball.rect.right = paddle.rect.left


def draw_center_line(surface):
    dash_height = 16
    gap = 12
    y = 0
    x = WIDTH // 2 - 2
    while y < HEIGHT:
        pygame.draw.rect(surface, GREY, pygame.Rect(x, y, 4, dash_height))
        y += dash_height + gap


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font untuk skor
    try:
        font = pygame.font.SysFont("Consolas", 32)
    except Exception:
        font = pygame.font.Font(None, 32)

    # Entity
    player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ai = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    player_score = 0
    ai_score = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # Input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Input pemain (tahan tombol)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s]:
            dy += PLAYER_SPEED
        player.move(dy)

        # Gerak AI: ikuti posisi Y bola dengan kecepatan terbatas
        tolerance = 6  # zona mati kecil untuk mencegah jitter
        if ball.rect.centery < ai.rect.centery - tolerance:
            ai.move(-AI_SPEED)
        elif ball.rect.centery > ai.rect.centery + tolerance:
            ai.move(AI_SPEED)

        # Update bola
        prev_rect = ball.rect.copy()
        ball.update()

        # Cek tabrakan dengan paddle pemain
        if ball.rect.colliderect(player.rect) and prev_rect.left >= player.rect.right:
            reflect_ball_from_paddle(ball, player)
        # Cek tabrakan dengan paddle AI
        if ball.rect.colliderect(ai.rect) and prev_rect.right <= ai.rect.left:
            reflect_ball_from_paddle(ball, ai)

        # Cek skor
        if ball.rect.left <= 0:
            ai_score += 1
            ball.reset(direction="right")
        elif ball.rect.right >= WIDTH:
            player_score += 1
            ball.reset(direction="left")

        # Gambar
        screen.fill(BLACK)
        draw_center_line(screen)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = f"{player_score}    {ai_score}"
        text_surf = font.render(score_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(text_surf, text_rect)

        # Tampilkan bantuan kontrol
        help_surf = font.render("W/S: Up/Down, Esc: Quit", True, GREY)
        help_rect = help_surf.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        screen.blit(help_surf, help_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
