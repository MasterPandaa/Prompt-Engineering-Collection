import sys
import random
import pygame

# --------------------------
# Konfigurasi dasar
# --------------------------
pygame.init()
pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong dengan AI - Pygame")

FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ukuran paddle dan bola
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
BALL_SIZE = 14

# Kecepatan
PLAYER_SPEED = 6
AI_MAX_SPEED = 5  # kecepatan maksimum AI per frame
BALL_SPEED = 6

# Font
SCORE_FONT = pygame.font.SysFont("consolas", 36)
INFO_FONT = pygame.font.SysFont("consolas", 18)


class Paddle:
    def __init__(self, x, y, width, height, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)

    def move(self, dy: int):
        self.rect.y += dy
        # Clamp agar tidak keluar layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Ball:
    def __init__(self, x, y, size, color=WHITE):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.vx = 0
        self.vy = 0
        self.speed = BALL_SPEED
        self.serve(direction=random.choice([-1, 1]))

    def serve(self, direction: int = 1):
        # Reset posisi ke tengah dan arah acak
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        angle_choices = [
            random.uniform(-0.8, -0.3),  # sudut ke atas
            random.uniform(0.3, 0.8),    # sudut ke bawah
        ]
        angle = random.choice(angle_choices)
        # Komponen kecepatan berdasarkan arah dan sudut
        self.vx = direction * self.speed * (1.0 / (abs(angle) + 1.0))
        self.vy = self.speed * angle

        # Normalisasi agar magnitudo tidak melebihi speed terlalu jauh
        mag = max(1e-6, (self.vx**2 + self.vy**2) ** 0.5)
        scale = self.speed / mag
        self.vx *= scale
        self.vy *= scale

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Pantul pada atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy *= -1

    def collide_with_paddle(self, paddle: 'Paddle'):
        if self.rect.colliderect(paddle.rect):
            # Geser bola keluar sedikit agar tidak "nempel"
            if self.vx < 0:
                self.rect.left = paddle.rect.right
            else:
                self.rect.right = paddle.rect.left

            # Hit factor: di mana bola menyentuh paddle memengaruhi sudut
            paddle_center = paddle.rect.centery
            ball_center = self.rect.centery
            offset = (ball_center - paddle_center) / (paddle.rect.height / 2)
            offset = max(-1.0, min(1.0, offset))

            # Kecepatan baru: balik arah X, ubah Y berdasar offset
            self.vx *= -1
            self.vy = (self.speed + 1.5) * offset

            # Sedikit akselerasi setelah tiap pantulan untuk dinamika
            speed_up = 1.04
            self.vx *= speed_up
            self.vy *= speed_up

            # Clamp kecepatan total agar tidak tak terkendali
            max_speed = 12
            mag = max(1e-6, (self.vx**2 + self.vy**2) ** 0.5)
            if mag > max_speed:
                scale = max_speed / mag
                self.vx *= scale
                self.vy *= scale


def draw_center_line(surface):
    dash_height = 14
    gap = 10
    x = SCREEN_WIDTH // 2 - 2
    for y in range(0, SCREEN_HEIGHT, dash_height + gap):
        pygame.draw.rect(surface, WHITE, pygame.Rect(x, y, 4, dash_height), border_radius=2)


def ai_follow(ai_paddle: Paddle, ball: Ball):
    # AI sederhana: mengikuti posisi Y bola dengan kecepatan maksimum terbatas
    target_y = ball.rect.centery
    if abs(ai_paddle.rect.centery - target_y) > 6:
        direction = 1 if target_y > ai_paddle.rect.centery else -1
        ai_paddle.move(direction * AI_MAX_SPEED)
    else:
        # fine adjustment
        if ai_paddle.rect.centery < target_y:
            ai_paddle.move(1)
        elif ai_paddle.rect.centery > target_y:
            ai_paddle.move(-1)


def main():
    clock = pygame.time.Clock()

    # Inisialisasi paddle pemain (kiri) dan AI (kanan)
    left_paddle = Paddle(24, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(SCREEN_WIDTH - 24 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

    # Bola
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE)

    # Skor
    left_score = 0
    right_score = 0

    # Countdown setelah skor
    reset_timer_frames = 0  # gunakan frame sebagai timer

    running = True
    while running:
        dt = clock.tick(FPS)

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain
        keys = pygame.key.get_pressed()
        player_move = 0
        if keys[pygame.K_w]:
            player_move -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player_move += PLAYER_SPEED
        left_paddle.move(player_move)

        # AI logic
        if reset_timer_frames == 0:
            ai_follow(right_paddle, ball)

        # Update bola (kecuali saat countdown)
        if reset_timer_frames == 0:
            ball.update()

            # Cek tabrakan dengan paddle
            # Prioritaskan collision pada sisi yang sesuai arah bola
            if ball.vx < 0 and ball.rect.left <= left_paddle.rect.right:
                ball.collide_with_paddle(left_paddle)
            elif ball.vx > 0 and ball.rect.right >= right_paddle.rect.left:
                ball.collide_with_paddle(right_paddle)

            # Skor: keluar kiri/kanan
            if ball.rect.right < 0:
                right_score += 1
                reset_timer_frames = FPS * 1  # 1 detik
                ball.serve(direction=1)
            elif ball.rect.left > SCREEN_WIDTH:
                left_score += 1
                reset_timer_frames = FPS * 1  # 1 detik
                ball.serve(direction=-1)
        else:
            reset_timer_frames = max(0, reset_timer_frames - 1)

        # Gambar
        WIN.fill(BLACK)
        draw_center_line(WIN)

        # Tampilkan skor
        score_text = SCORE_FONT.render(f"{left_score}    {right_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        WIN.blit(score_text, score_rect)

        # Info kontrol
        info_text = INFO_FONT.render("Kontrol: W / S (Pemain Kiri) | Esc untuk keluar", True, WHITE)
        WIN.blit(info_text, (20, SCREEN_HEIGHT - 30))

        # Gambar objek
        left_paddle.draw(WIN)
        right_paddle.draw(WIN)
        ball.draw(WIN)

        # Optional: tampilkan countdown
        if reset_timer_frames > 0:
            secs = (reset_timer_frames // FPS) + 1
            cd_text = SCORE_FONT.render(str(secs), True, WHITE)
            cd_rect = cd_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
            WIN.blit(cd_text, cd_rect)

        pygame.display.flip()

        # Keluar dengan Esc
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
