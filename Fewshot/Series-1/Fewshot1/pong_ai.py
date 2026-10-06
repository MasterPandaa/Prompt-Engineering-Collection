import sys
import random
import pygame

# -------------------------
# Konfigurasi dasar
# -------------------------
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong dengan AI - Pygame")

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
BALL_SIZE = 14

PLAYER_SPEED = 6
AI_SPEED = 5
BALL_SPEED = 6

FONT = pygame.font.SysFont("consolas", 32)

# -------------------------
# Class Paddle
# -------------------------
class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def move_up(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# -------------------------
# Class Ball
# -------------------------
class Ball:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = speed
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction=None):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # Arah horizontal acak, arah vertikal acak tetapi tidak nol
        if direction is None:
            direction = random.choice([-1, 1])
        angle_choices = [-3, -2, -1, 1, 2, 3]  # hindari 0 agar tidak horizontal murni
        vy = random.choice(angle_choices)
        vx = direction * self.base_speed
        # Normalisasi kecepatan sehingga resultan mendekati base_speed*1.1
        # agar ada variasi sudut tapi kecepatan relatif konsisten
        norm = max(1, (abs(vx) + abs(vy)) / self.base_speed)
        self.vx = int(round(vx / norm * 1.4))
        self.vy = int(round(vy / norm * 1.4))
        if self.vx == 0:
            self.vx = direction * self.base_speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def update(self, left_paddle: Paddle, right_paddle: Paddle):
        # Gerakkan bola
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Pantul dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy *= -1

        # Deteksi tabrakan dengan paddle kiri
        if self.rect.colliderect(left_paddle.rect) and self.vx < 0:
            self._bounce_from_paddle(left_paddle, is_left=True)

        # Deteksi tabrakan dengan paddle kanan
        if self.rect.colliderect(right_paddle.rect) and self.vx > 0:
            self._bounce_from_paddle(right_paddle, is_left=False)

    def _bounce_from_paddle(self, paddle: Paddle, is_left: bool):
        # Tempatkan bola tepat di luar paddle untuk menghindari "lengket"
        if is_left:
            self.rect.left = paddle.rect.right
        else:
            self.rect.right = paddle.rect.left

        # Balik arah horizontal
        self.vx *= -1

        # Variasi sudut pantulan berdasarkan titik kontak
        paddle_center = paddle.rect.centery
        ball_center = self.rect.centery
        offset = ball_center - paddle_center  # positif: kena bagian bawah paddle
        # Skala offset -> pengaruh pada vy
        max_offset = paddle.rect.height / 2
        factor = (offset / max_offset)  # -1 .. 1
        add_vy = int(round(factor * (self.base_speed)))
        # Clamp vy agar tidak terlalu lambat atau terlalu cepat
        self.vy += add_vy
        self.vy = max(-self.base_speed * 2, min(self.base_speed * 2, self.vy))

        # Sedikit percepat bola tiap pantulan untuk meningkatkan tantangan
        if abs(self.vx) < self.base_speed * 2 + 2:
            self.vx += 1 if self.vx > 0 else -1

# -------------------------
# Utilitas gambar
# -------------------------
def draw_center_line(surface):
    dash_height = 10
    gap = 10
    x = SCREEN_WIDTH // 2
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(surface, WHITE, (x - 1, y, 2, dash_height))
        y += dash_height + gap

def draw_score(surface, left_score, right_score):
    score_text = f"{left_score}   {right_score}"
    text_surface = FONT.render(score_text, True, WHITE)
    rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
    surface.blit(text_surface, rect)

# -------------------------
# AI Logic: mengikuti Y bola dengan batas kecepatan
# -------------------------
def ai_control(ai_paddle: Paddle, ball: Ball):
    # Threshold kecil agar AI tidak "gelisah" ketika sudah sejajar
    threshold = 6
    if ball.rect.centery < ai_paddle.rect.centery - threshold:
        ai_paddle.move_up()
    elif ball.rect.centery > ai_paddle.rect.centery + threshold:
        ai_paddle.move_down()
    # Clamp agar tetap di layar (sudah di-handle di move_up/down)

# -------------------------
# Game Loop
# -------------------------
def main():
    clock = pygame.time.Clock()

    # Inisialisasi paddle dan bola
    left_paddle = Paddle(
        x=30,
        y=(SCREEN_HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=PLAYER_SPEED,
    )
    right_paddle = Paddle(
        x=SCREEN_WIDTH - 30 - PADDLE_WIDTH,
        y=(SCREEN_HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=AI_SPEED,
    )
    ball = Ball(
        x=SCREEN_WIDTH // 2 - BALL_SIZE // 2,
        y=SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
        speed=BALL_SPEED,
    )

    left_score = 0
    right_score = 0

    running = True
    while running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain (W/S)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle.move_up()
        if keys[pygame.K_s]:
            left_paddle.move_down()

        # Kontrol AI
        ai_control(right_paddle, ball)

        # Update bola
        ball.update(left_paddle, right_paddle)

        # Cek skor (bola keluar kiri/kanan)
        if ball.rect.left <= 0:
            right_score += 1
            ball.reset(direction=-1)  # luncurkan menuju kiri (ke pemain) setelah AI skor
        elif ball.rect.right >= SCREEN_WIDTH:
            left_score += 1
            ball.reset(direction=1)   # luncurkan menuju kanan (ke AI) setelah pemain skor

        # Gambar semuanya
        WIN.fill(BLACK)
        draw_center_line(WIN)
        left_paddle.draw(WIN)
        right_paddle.draw(WIN)
        ball.draw(WIN)
        draw_score(WIN, left_score, right_score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
