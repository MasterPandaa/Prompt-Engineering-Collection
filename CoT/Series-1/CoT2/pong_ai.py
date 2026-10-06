import sys
import math
import random
import pygame

# ---------------------------
# Konfigurasi Dasar
# ---------------------------
WIDTH, HEIGHT = 1000, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 14, 120
BALL_SIZE = 14

MARGIN = 24

PLAYER_SPEED = 8
AI_SPEED = 7  # Bisa disesuaikan untuk kesulitan

BALL_SPEED = 8
BALL_SPEED_MAX = 12
BALL_SPEED_INCREMENT = 0.25  # Sedikit meningkat tiap pantulan paddle

WHITE = (240, 240, 240)
BLACK = (15, 15, 20)
GREY = (80, 80, 90)

# ---------------------------
# Kelas Game Object
# ---------------------------
class Paddle:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # Clamp di layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def ai_follow(self, target_y, deadzone=8):
        # AI bergerak menuju target_y (centery bola) dengan batas kecepatan
        if self.rect.centery < target_y - deadzone:
            self.move(self.speed)
        elif self.rect.centery > target_y + deadzone:
            self.move(-self.speed)
        # Else: dalam deadzone -> diam (mengurangi jitter)


class Ball:
    def __init__(self, x, y, size, base_speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = base_speed
        self.speed = base_speed
        self.vx = 0
        self.vy = 0

    def reset(self, direction=1):
        # direction: +1 ke kanan, -1 ke kiri
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = self.base_speed

        # Sudut acak: hindari terlalu mendekati horizontal/vertikal
        angle = random.uniform(-0.9, 0.9)  # sekitar -~51° s/d ~51°
        # Komponen kecepatan
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        # Pastikan komponen vertikal tidak nol total
        if abs(self.vy) < 2:
            self.vy = 2 if self.vy >= 0 else -2

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def bounce_y(self):
        self.vy = -self.vy

    def bounce_x(self, offset_ratio):
        """
        offset_ratio: [-1, 1], posisi tabrakan relatif terhadap pusat paddle.
        Mengubah arah horizontal dan menyesuaikan sudut vertikal berdasarkan offset.
        Juga sedikit menaikkan kecepatan agar game makin menantang.
        """
        # Balik arah horizontal
        self.vx = -self.vx

        # Sesuaikan vy berdasarkan offset. Semakin jauh dari tengah, semakin besar sudut.
        max_angle = math.radians(50)  # batasi sudut agar tidak terlalu ekstrem
        angle = offset_ratio * max_angle

        # Hitung ulang vektor kecepatan berdasarkan kecepatan saat ini
        # Tanda arah horizontal mengikuti sign(vx) setelah dibalik
        direction = 1 if self.vx >= 0 else -1
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_SPEED_MAX)
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

# ---------------------------
# Fungsi Gambar Net Tengah
# ---------------------------
def draw_center_net(surface):
    segment_h = 16
    gap = 10
    x = WIDTH // 2 - 2
    for y in range(0, HEIGHT, segment_h + gap):
        pygame.draw.rect(surface, GREY, pygame.Rect(x, y, 4, segment_h))

# ---------------------------
# Main Game
# ---------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Consolas", 36)

    # Buat paddle
    player = Paddle(
        x=MARGIN,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        w=PADDLE_WIDTH,
        h=PADDLE_HEIGHT,
        speed=PLAYER_SPEED,
    )
    ai = Paddle(
        x=WIDTH - MARGIN - PADDLE_WIDTH,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        w=PADDLE_WIDTH,
        h=PADDLE_HEIGHT,
        speed=AI_SPEED,
    )

    # Buat bola
    ball = Ball(
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
        base_speed=BALL_SPEED,
    )
    # Serve awal acak ke kiri/kanan
    ball.reset(direction=random.choice([-1, 1]))

    score_player = 0
    score_ai = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # -------- Event --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # -------- Input & Update Paddle Player --------
        move_dy = 0
        if keys[pygame.K_w]:
            move_dy -= player.speed
        if keys[pygame.K_s]:
            move_dy += player.speed
        if move_dy != 0:
            player.move(move_dy)

        # -------- AI Logic --------
        ai.ai_follow(ball.rect.centery, deadzone=8)

        # -------- Update Bola --------
        ball.update()

        # Pantulan dinding atas/bawah
        if ball.rect.top <= 0:
            ball.rect.top = 0
            ball.bounce_y()
        elif ball.rect.bottom >= HEIGHT:
            ball.rect.bottom = HEIGHT
            ball.bounce_y()

        # -------- Collision dengan Paddle --------
        # Paddle kiri (player)
        if ball.rect.colliderect(player.rect) and ball.vx < 0:
            # Koreksi posisi agar tidak masuk ke paddle
            ball.rect.left = player.rect.right
            # Offset relatif -1..1
            offset = (ball.rect.centery - player.rect.centery) / (player.rect.height / 2)
            offset = max(-1.0, min(1.0, offset))
            ball.bounce_x(offset)

        # Paddle kanan (AI)
        if ball.rect.colliderect(ai.rect) and ball.vx > 0:
            ball.rect.right = ai.rect.left
            offset = (ball.rect.centery - ai.rect.centery) / (ai.rect.height / 2)
            offset = max(-1.0, min(1.0, offset))
            ball.bounce_x(offset)

        # -------- Skor --------
        # Bola keluar kiri -> AI skor
        if ball.rect.right < 0:
            score_ai += 1
            ball.reset(direction=1)  # serve ke kanan (ke arah AI), bola mulai dari tengah

        # Bola keluar kanan -> Player skor
        if ball.rect.left > WIDTH:
            score_player += 1
            ball.reset(direction=-1)  # serve ke kiri (ke arah Player)

        # -------- Gambar --------
        screen.fill(BLACK)
        draw_center_net(screen)

        pygame.draw.rect(screen, WHITE, player.rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, ai.rect, border_radius=6)
        pygame.draw.ellipse(screen, WHITE, ball.rect)

        # Tampilkan skor
        score_text = f"{score_player}  :  {score_ai}"
        text_surface = font.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 40))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
