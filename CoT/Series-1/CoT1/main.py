import pygame
import random

# -----------------------------
# Konstanta & Konfigurasi
# -----------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 110
BALL_SIZE = 16

PADDLE_SPEED = 9
AI_SPEED = 7
BALL_SPEED = 8  # kecepatan dasar bola (dipecah jadi vx, vy)

# Variasi spin maksimum yang ditambahkan ke vy berdasarkan titik tumbuk
MAX_SPIN = 6


# -----------------------------
# Kelas Paddle
# -----------------------------
class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # Clamp agar tidak keluar layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


# -----------------------------
# Kelas Ball
# -----------------------------
class Ball:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = speed
        self.vx = 0
        self.vy = 0
        self.reset()

    def reset(self):
        # Posisikan di tengah, arah acak ke kiri/kanan dan kecil variasi ke atas/bawah
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        dir_x = random.choice([-1, 1])
        # Beri sudut awal tidak vertikal murni
        angle_choices = [-0.75, -0.5, -0.25, 0.25, 0.5, 0.75]
        angle = random.choice(angle_choices)
        # Proyeksi kecepatan ke sumbu x, y (normalisasi agar magnitudo ~ base_speed)
        self.vx = int(self.base_speed * dir_x)
        self.vy = int(self.base_speed * angle)

        # Pastikan vy tidak nol supaya game tidak terlalu lama lurus
        if self.vy == 0:
            self.vy = random.choice([-2, 2])

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Pantul dari atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy = -self.vy

    def collide_with_paddle(self, paddle_rect, from_left=True):
        # Ketika tabrakan, balik vx
        self.vx = -self.vx

        # Tambahkan "spin" berdasarkan posisi tumbukan relatif ke pusat paddle
        offset = (self.rect.centery - paddle_rect.centery) / (paddle_rect.height / 2)
        # offset di [-1, 1], kalikan dengan MAX_SPIN
        self.vy += int(offset * MAX_SPIN)

        # Hindari "nempel" pada paddle di frame berikutnya
        if from_left:
            self.rect.left = paddle_rect.right
        else:
            self.rect.right = paddle_rect.left

        # Batasi vy agar tidak terlalu ekstrem
        self.vy = max(-self.base_speed - MAX_SPIN, min(self.vy, self.base_speed + MAX_SPIN))

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


# -----------------------------
# Fungsi utama game
# -----------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 64)

    # Buat paddle pemain (kiri) dan AI (kanan)
    player = Paddle(
        x=40,
        y=(HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=PADDLE_SPEED,
    )
    ai = Paddle(
        x=WIDTH - 40 - PADDLE_WIDTH,
        y=(HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=AI_SPEED,
    )

    ball = Ball(
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
        speed=BALL_SPEED,
    )

    score_left = 0   # skor pemain (kiri)
    score_right = 0  # skor AI (kanan)

    running = True
    while running:
        _dt = clock.tick(FPS)  # sinkron FPS
        # -------------------------
        # Event
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # -------------------------
        # Input Pemain (W/S)
        # -------------------------
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_s]:
            dy += player.speed
        player.move(dy)

        # -------------------------
        # Logika AI sederhana
        # -------------------------
        # AI akan menggeser ke arah posisi Y bola dengan batas kecepatan AI_SPEED
        if ai.rect.centery < ball.rect.centery - 6:  # beri deadzone 6 px agar tidak jitter
            ai.move(ai.speed)
        elif ai.rect.centery > ball.rect.centery + 6:
            ai.move(-ai.speed)

        # -------------------------
        # Update Bola
        # -------------------------
        ball.update()

        # Tabrakan bola dengan paddle pemain
        if ball.rect.colliderect(player.rect) and ball.vx < 0:
            ball.collide_with_paddle(player.rect, from_left=True)

        # Tabrakan bola dengan paddle AI
        if ball.rect.colliderect(ai.rect) and ball.vx > 0:
            ball.collide_with_paddle(ai.rect, from_left=False)

        # -------------------------
        # Deteksi Skor
        # -------------------------
        if ball.rect.right < 0:
            # Bola keluar kiri -> AI skor
            score_right += 1
            ball.reset()
        elif ball.rect.left > WIDTH:
            # Bola keluar kanan -> Pemain skor
            score_left += 1
            ball.reset()

        # -------------------------
        # Gambar
        # -------------------------
        screen.fill(BLACK)

        # Garis tengah
        for y in range(0, HEIGHT, 30):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 3, y + 10, 6, 15))

        # Gambar paddle & bola
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = f"{score_left}   {score_right}"
        text_surf = font.render(score_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(text_surf, text_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
