import sys
import random
import pygame

# ========== Konfigurasi Utama ==========
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 14

PLAYER_SPEED = 6
AI_MAX_SPEED = 5

BALL_BASE_SPEED = 5.0
BALL_SPEED_INCREMENT = 0.2  # percepat sedikit saat kena paddle
BALL_MAX_SPEED = 12.0

SCORE_FONT_SIZE = 48
SERVE_DELAY_MS = 800  # jeda singkat setelah skor sebelum bola bergerak lagi


# ========== Kelas Paddle ==========
class Paddle:
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 0

    def move(self, dy):
        self.rect.y += dy
        # Batasi di dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def follow_y(self, target_y, max_speed):
        # AI mengikuti posisi Y bola dengan kecepatan terbatas
        center_y = self.rect.centery
        if abs(target_y - center_y) <= max_speed:
            self.rect.centery = target_y
        else:
            direction = 1 if target_y > center_y else -1
            self.rect.centery += direction * max_speed

        # Batasi di dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


# ========== Kelas Ball ==========
class Ball:
    def __init__(self, size=BALL_SIZE, color=(255, 255, 255)):
        self.size = size
        self.color = color
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vx = 0.0
        self.vy = 0.0
        self.serve_direction = random.choice([-1, 1])  # arah awal acak (-1 kiri, 1 kanan)
        self.frozen_until = 0  # waktu (ms) sampai bola mulai bergerak (untuk jeda setelah skor)

    def reset(self, serve_direction=None, now_ms=0):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        direction = self.serve_direction if serve_direction is None else serve_direction
        # Kecepatan awal acak dengan arah serve
        angle = random.uniform(-0.4, 0.4)  # sedikit kemiringan
        speed = BALL_BASE_SPEED
        self.vx = direction * speed * (1.0 if random.random() < 0.5 else 1.05)
        self.vy = speed * angle
        self.clamp_speed()
        # Bekukan bola sebentar untuk jeda serve
        self.frozen_until = now_ms + SERVE_DELAY_MS

    def clamp_speed(self):
        # Batasi kecepatan resultant
        import math
        mag = math.hypot(self.vx, self.vy)
        if mag > BALL_MAX_SPEED:
            scale = BALL_MAX_SPEED / mag
            self.vx *= scale
            self.vy *= scale

    def update(self, now_ms):
        # Jika masih dalam masa jeda serve, jangan bergerak
        if now_ms < self.frozen_until:
            return

        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Pantulan atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


# ========== Fungsi Utilitas Gambar ==========
def draw_center_dashed_line(surface, color=(200, 200, 200), dash_height=10, gap=10, width=2):
    x = SCREEN_WIDTH // 2 - width // 2
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(surface, color, (x, y, width, dash_height))
        y += dash_height + gap


def main():
    pygame.init()
    pygame.display.set_caption("Pong dengan AI - Pygame")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

    # Objek permainan
    player = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball()
    ball.reset(now_ms=pygame.time.get_ticks())

    left_score = 0
    right_score = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ========== Input ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s]:
            dy += PLAYER_SPEED
        player.move(dy)

        # ========== AI ==========
        # AI mengikuti posisi Y bola dengan batas kecepatan
        ai_target_y = ball.rect.centery
        ai.follow_y(ai_target_y, AI_MAX_SPEED)

        # ========== Update Bola ==========
        prev_ball_rect = ball.rect.copy()
        ball.update(now)

        # ========== Deteksi Skor ==========
        # Jika bola keluar kiri/kanan, skor dan reset
        scored = None
        if ball.rect.right < 0:
            right_score += 1
            scored = "right"
        elif ball.rect.left > SCREEN_WIDTH:
            left_score += 1
            scored = "left"

        if scored is not None:
            # Tentukan arah serve berikutnya (bola diarahkan ke pihak yang kebobolan)
            if scored == "left":
                serve_dir = -1  # kiri mencetak, bola ke kanan (AI kebobolan)
            else:
                serve_dir = 1   # kanan mencetak, bola ke kiri (pemain kebobolan)
            ball.serve_direction = serve_dir
            ball.reset(serve_direction=serve_dir, now_ms=now)

        # ========== Deteksi Tabrakan Paddle ==========
        # Gunakan rect sebelumnya untuk membantu adjustment agar tidak "nempel"
        if ball.rect.colliderect(player.rect):
            # Pastikan tabrakan terjadi dari arah kanan ke kiri
            if prev_ball_rect.left >= player.rect.right:
                # Tidak masuk skenario umum; paksa keluar di sisi kanan paddle
                ball.rect.left = player.rect.right
            else:
                ball.rect.left = player.rect.right

            # Hit angle berdasarkan offset relatif
            offset = (ball.rect.centery - player.rect.centery) / (player.rect.height / 2)
            # Semakin jauh dari tengah, semakin besar sudut
            ball.vx = abs(ball.vx) + BALL_SPEED_INCREMENT
            ball.vy = (BALL_BASE_SPEED + abs(ball.vx) * 0.3) * offset
            # Arahkan bola ke kanan
            if ball.vx < 1.5:
                ball.vx = 1.5
            ball.clamp_speed()

        elif ball.rect.colliderect(ai.rect):
            # Pastikan tabrakan terjadi dari arah kiri ke kanan
            if prev_ball_rect.right <= ai.rect.left:
                ball.rect.right = ai.rect.left
            else:
                ball.rect.right = ai.rect.left

            offset = (ball.rect.centery - ai.rect.centery) / (ai.rect.height / 2)
            ball.vx = -abs(ball.vx) - BALL_SPEED_INCREMENT
            ball.vy = (BALL_BASE_SPEED + abs(ball.vx) * 0.3) * offset
            if ball.vx > -1.5:
                ball.vx = -1.5
            ball.clamp_speed()

        # ========== Gambar ==========
        screen.fill((15, 15, 20))
        draw_center_dashed_line(screen)

        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Skor
        score_text = f"{left_score}   {right_score}"
        text_surf = font.render(score_text, True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(text_surf, text_rect)

        # Indikator "READY" saat serve delay
        if now < ball.frozen_until:
            ready_surf = font.render("READY", True, (200, 200, 200))
            ready_rect = ready_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(ready_surf, ready_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
