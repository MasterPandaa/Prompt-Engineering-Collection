import pygame
import random
import math

# ---------- Konstanta ----------
WIDTH, HEIGHT = 900, 540
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 14, 100
BALL_SIZE = 14

PLAYER_SPEED = 8
AI_SPEED = 7  # sedikit lebih lambat dari player agar fair
BALL_SPEED = 7
BALL_MAX_SPEED = 12

SCORE_FONT_SIZE = 48
COUNTDOWN_FONT_SIZE = 64

# ---------- Kelas ----------
class Paddle:
    def __init__(self, x, y, width, height, speed, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = color

    def move(self, dy):
        self.rect.y += dy
        # Clamp ke batas layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update_ai(self, target_y, deadzone=6):
        # target_y adalah posisi y (center) dari bola
        delta = target_y - self.rect.centery
        if abs(delta) <= deadzone:
            dy = 0
        else:
            dy = max(-self.speed, min(self.speed, delta))
        self.move(dy)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)


class Ball:
    def __init__(self, x, y, size, speed, max_speed, color=WHITE):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.base_speed = speed
        self.speed = speed
        self.max_speed = max_speed
        self.color = color
        # Arah awal acak
        self.vx = random.choice([-1, 1]) * speed
        self.vy = random.uniform(-0.6, 0.6) * speed

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def bounce_y(self):
        self.vy = -self.vy

    def bounce_x(self, offset_ratio=0.0):
        # offset_ratio di kisaran [-1, 1], mempengaruhi sudut pantul
        self.vx = -self.vx

        # Modifikasi vy berdasarkan offset terhadap pusat paddle
        max_angle = math.radians(50)  # batasi sudut maksimum
        target_angle = offset_ratio * max_angle
        speed = min(self.speed * 1.03, self.max_speed)  # sedikit percepat
        self.speed = speed

        # vektor kecepatan dengan sudut target
        # vx arah ditentukan oleh tanda saat ini (setelah dibalik)
        direction_x = 1 if self.vx > 0 else -1
        self.vx = math.cos(target_angle) * speed * direction_x
        self.vy = math.sin(target_angle) * speed

        # Pastikan tidak terlalu datar (agar permainan menarik)
        if abs(self.vy) < 1.2:
            self.vy = 1.2 if self.vy >= 0 else -1.2

        # Nudge supaya bola tidak "terjebak" di dalam paddle
        if direction_x > 0:
            self.rect.left = max(self.rect.left, 0)
        else:
            self.rect.right = min(self.rect.right, WIDTH)

    def reset(self, direction=None):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = self.base_speed
        dir_x = random.choice([-1, 1]) if direction is None else direction
        self.vx = dir_x * self.base_speed
        self.vy = random.uniform(-0.6, 0.6) * self.base_speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=7)


# ---------- Utilitas ----------
def draw_center_line(surface, color=WHITE, dash_len=12, gap=12, width=4):
    y = 0
    x = WIDTH // 2 - width // 2
    while y < HEIGHT:
        pygame.draw.rect(surface, color, (x, y, width, dash_len))
        y += dash_len + gap


def render_text_center(surface, text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()

    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE, bold=True)
    countdown_font = pygame.font.SysFont(None, COUNTDOWN_FONT_SIZE, bold=True)

    # Buat objek
    player = Paddle(
        x=30,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=PLAYER_SPEED,
    )
    ai = Paddle(
        x=WIDTH - 30 - PADDLE_WIDTH,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=AI_SPEED,
    )
    ball = Ball(
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
        speed=BALL_SPEED,
        max_speed=BALL_MAX_SPEED,
    )

    score_player = 0
    score_ai = 0

    running = True
    # Opsi: countdown awal
    start_ticks = pygame.time.get_ticks()
    show_countdown = True

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        # Gerak pemain (W/S)
        if keys[pygame.K_w]:
            player.move(-player.speed)
        if keys[pygame.K_s]:
            player.move(player.speed)

        # Update bola hanya jika tidak sedang countdown
        now = pygame.time.get_ticks()
        elapsed = (now - start_ticks) / 1000.0

        if show_countdown:
            # Tampilkan 3..2..1 di layar selama 1.0 detik per angka
            if elapsed >= 3.0:
                show_countdown = False
            # Tidak update bola/pantulan saat countdown, tapi paddle boleh digerakkan
        else:
            # AI tracking
            ai.update_ai(ball.rect.centery, deadzone=6)

            # Update bola
            ball.update()

            # Pantulan dinding atas/bawah
            if ball.rect.top <= 0:
                ball.rect.top = 0
                ball.bounce_y()
            elif ball.rect.bottom >= HEIGHT:
                ball.rect.bottom = HEIGHT
                ball.bounce_y()

            # Pantulan paddle pemain
            if ball.rect.colliderect(player.rect) and ball.vx < 0:
                offset = (ball.rect.centery - player.rect.centery) / (player.rect.height / 2)
                offset = max(-1.0, min(1.0, offset))
                ball.rect.left = player.rect.right  # nudge keluar
                ball.bounce_x(offset)

            # Pantulan paddle AI
            if ball.rect.colliderect(ai.rect) and ball.vx > 0:
                offset = (ball.rect.centery - ai.rect.centery) / (ai.rect.height / 2)
                offset = max(-1.0, min(1.0, offset))
                ball.rect.right = ai.rect.left  # nudge keluar
                ball.bounce_x(offset)

            # Skor: keluar kiri/kanan
            if ball.rect.right < 0:
                score_ai += 1
                ball.reset(direction=1)  # arah ke pemain
                start_ticks = pygame.time.get_ticks()
                show_countdown = True
            elif ball.rect.left > WIDTH:
                score_player += 1
                ball.reset(direction=-1)  # arah ke AI
                start_ticks = pygame.time.get_ticks()
                show_countdown = True

        # ---------- Render ----------
        screen.fill(BLACK)
        draw_center_line(screen)

        # Gambar objek
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = f"{score_player}    {score_ai}"
        render_text_center(screen, score_text, score_font, WHITE, 40)

        # Tampilkan countdown jika perlu
        if show_countdown:
            count = int(max(0, 3 - elapsed)) + (1 if elapsed < 3 else 0)
            if count > 0 and count <= 3:
                render_text_center(screen, str(count), countdown_font, WHITE, HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
