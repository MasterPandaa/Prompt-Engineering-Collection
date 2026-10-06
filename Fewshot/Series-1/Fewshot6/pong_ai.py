import pygame
import random

# --- Konstanta ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (180, 180, 180)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

PLAYER_SPEED = 420  # pixels/sec
AI_MAX_SPEED = 380   # batasi kecepatan AI agar fair
BALL_SPEED_INITIAL = 360
BALL_SPEED_INCREMENT = 18  # setiap benturan paddle
MAX_BALL_SPEED = 720

WIN_SCORE = 10  # opsional: tujuan skor


class Paddle:
    def __init__(self, x, y, width, height, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 0  # untuk info kecepatan terakhir (membantu pantulan)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)

    def move(self, dy, dt):
        # dy dalam satuan pixels/sec, jadi kalikan dt
        self.rect.y += int(dy * dt)
        self.speed = dy
        # clamp ke layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Ball:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.color = WHITE
        self.vx = 0.0
        self.vy = 0.0

    def reset(self, direction=None):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        speed = BALL_SPEED_INITIAL
        # arah acak kiri/kanan dan sudut kecil agar tidak lurus
        if direction is None:
            direction = random.choice([-1, 1])
        angle = random.uniform(-0.35, 0.35)  # radian ~20 derajat
        # konversi ke vektor
        self.vx = direction * speed * (1.0)
        self.vy = speed * angle
        # normalisasi agar kecepatan total wajar
        self._normalize_speed(speed)

    def _normalize_speed(self, target_speed):
        import math
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            return
        scale = target_speed / mag
        self.vx *= scale
        self.vy *= scale

    def increase_speed(self, inc=BALL_SPEED_INCREMENT):
        import math
        speed = min(MAX_BALL_SPEED, math.hypot(self.vx, self.vy) + inc)
        self._normalize_speed(speed)

    def update(self, dt):
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)
        # Pantulan dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vy *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)


def handle_paddle_collision(ball: Ball, paddle: Paddle, from_left: bool):
    # Pastikan bola keluar di sisi yang benar untuk menghindari tersangkut
    if from_left:
        ball.rect.left = paddle.rect.right
    else:
        ball.rect.right = paddle.rect.left

    # Hit position: -1 (atas paddle) ke +1 (bawah paddle)
    paddle_center = paddle.rect.centery
    offset = (ball.rect.centery - paddle_center) / (paddle.rect.height / 2)
    offset = max(-1.0, min(1.0, offset))

    # Arah horizontal dibalik
    speed_x = abs(ball.vx)
    if from_left:
        ball.vx = abs(speed_x)
    else:
        ball.vx = -abs(speed_x)

    # Tambahkan komponen vertikal berdasarkan offset dan sedikit pengaruh kecepatan paddle
    ball.vy = (ball.vy * 0.2) + (offset * 0.8 * abs(ball.vx)) * 0.6 + paddle.speed * 0.1

    # Sedikit naikkan kecepatan bola setelah menyentuh paddle
    ball.increase_speed(BALL_SPEED_INCREMENT)


def ai_follow(ai: Paddle, ball: Ball, dt):
    # AI mengikuti posisi Y bola dengan batas kecepatan
    target_y = ball.rect.centery
    center = ai.rect.centery
    dy = 0
    if center < target_y - 8:
        dy = AI_MAX_SPEED
    elif center > target_y + 8:
        dy = -AI_MAX_SPEED
    else:
        dy = 0
    ai.move(dy, dt)


def draw_center_line(surface):
    # Garis tengah putus-putus
    dash_height = 18
    gap = 12
    x = SCREEN_WIDTH // 2 - 1
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(surface, GREY, pygame.Rect(x, y, 2, dash_height))
        y += dash_height + gap


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Pong dengan AI - Pygame')
    clock = pygame.time.Clock()

    # Font untuk skor
    try:
        font = pygame.font.SysFont('Consolas', 36)
    except Exception:
        font = pygame.font.Font(None, 36)

    # Inisialisasi objek
    left_paddle = Paddle(28, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(SCREEN_WIDTH - 28 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE)
    ball.reset(direction=random.choice([-1, 1]))

    left_score = 0
    right_score = 0

    running = True
    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain (W/S)
        keys = pygame.key.get_pressed()
        player_dy = 0
        if keys[pygame.K_w]:
            player_dy -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player_dy += PLAYER_SPEED
        left_paddle.move(player_dy, dt)

        # AI
        ai_follow(right_paddle, ball, dt)

        # Update bola
        ball.update(dt)

        # Cek skor: bola melewati kiri/kanan
        if ball.rect.right < 0:
            right_score += 1
            ball.reset(direction=1)
        elif ball.rect.left > SCREEN_WIDTH:
            left_score += 1
            ball.reset(direction=-1)

        # Deteksi tabrakan bola dengan paddle
        if ball.rect.colliderect(left_paddle.rect) and ball.vx < 0:
            handle_paddle_collision(ball, left_paddle, from_left=True)
        elif ball.rect.colliderect(right_paddle.rect) and ball.vx > 0:
            handle_paddle_collision(ball, right_paddle, from_left=False)

        # Gambar
        screen.fill(BLACK)
        draw_center_line(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = f"{left_score}   {right_score}"
        text_surf = font.render(score_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(text_surf, text_rect)

        # Opsi: tampilkan instruksi singkat
        hint_surf = font.render("W/S untuk gerak", True, GREY)
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(hint_surf, hint_rect)

        # Opsi: tampilkan pemenang
        if WIN_SCORE and (left_score >= WIN_SCORE or right_score >= WIN_SCORE):
            winner = 'Pemain' if left_score > right_score else 'AI'
            win_text = font.render(f"{winner} Menang! Tekan R untuk reset", True, WHITE)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_text, win_rect)
            # Freeze bola dan paddle sampai reset
            ball.vx = 0
            ball.vy = 0
            if keys[pygame.K_r]:
                left_score = 0
                right_score = 0
                ball.reset(direction=random.choice([-1, 1]))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
