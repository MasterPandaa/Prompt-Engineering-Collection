import pygame
import random

# ---------- Konstanta Dasar ----------
WIDTH, HEIGHT = 800, 480
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
BALL_SIZE = 14

PLAYER_SPEED = 7
AI_SPEED = 6  # sedikit lebih lambat dari pemain agar terasa fair
BALL_SPEED_X = 6
BALL_SPEED_Y = 4
BALL_SPEED_Y_MAX = 7  # batas kecepatan vertikal bola

SCORE_TO_WIN = 11  # opsional, bisa diabaikan jika tidak ingin akhir permainan

# ---------- Kelas ----------
class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # clamp agar tidak keluar layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)


class Ball:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        # arah awal acak
        self.vel_x = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        self.vel_y = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    def reset(self, direction=None):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        # arah horizontal: jika direction ditentukan ('left' atau 'right'), bola diarahkan ke sana
        if direction == "left":
            self.vel_x = -abs(BALL_SPEED_X)
        elif direction == "right":
            self.vel_x = abs(BALL_SPEED_X)
        else:
            self.vel_x = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        self.vel_y = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Pantulan dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


# ---------- Fungsi Utilitas ----------
def handle_paddle_collision(ball: "Ball", paddle: "Paddle"):
    # Tentukan sisi datangnya bola untuk mencegah "nempel"
    coming_from_left = ball.vel_x > 0  # bola bergerak ke kanan
    if ball.rect.colliderect(paddle.rect):
        # Hit offset: seberapa jauh dari tengah paddle (range ~ -1..1)
        paddle_center = paddle.rect.centery
        ball_center = ball.rect.centery
        offset = (ball_center - paddle_center) / (paddle.rect.height / 2)
        # clamp offset
        offset = max(-1.0, min(1.0, offset))

        # Atur kecepatan vertikal berdasarkan offset
        ball.vel_y = int(offset * BALL_SPEED_Y_MAX)

        # Balikkan arah horizontal dan sedikit percepat untuk dynamism
        speed_boost = 0.5
        if coming_from_left:
            # Jika datang dari kiri (ke kanan), pantul ke kiri
            ball.vel_x = -abs(ball.vel_x) - speed_boost
            # geser keluar agar tidak "terperangkap" di dalam paddle
            ball.rect.right = paddle.rect.left
        else:
            # Jika datang dari kanan (ke kiri), pantul ke kanan
            ball.vel_x = abs(ball.vel_x) + speed_boost
            ball.rect.left = paddle.rect.right

        # Batasi vel_y supaya tidak terlalu ekstrem
        if ball.vel_y > BALL_SPEED_Y_MAX:
            ball.vel_y = BALL_SPEED_Y_MAX
        if ball.vel_y < -BALL_SPEED_Y_MAX:
            ball.vel_y = -BALL_SPEED_Y_MAX


def ai_move(ai: "Paddle", ball: "Ball"):
    # Deadzone untuk mengurangi jitter
    deadzone = 6
    if ball.rect.centery < ai.rect.centery - deadzone:
        ai.move(-AI_SPEED)
    elif ball.rect.centery > ai.rect.centery + deadzone:
        ai.move(AI_SPEED)
    # jika dalam deadzone, tidak bergerak


def draw_center_line(surface):
    # Garis tengah putus-putus
    segment_len = 12
    gap = 8
    x = WIDTH // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.line(surface, WHITE, (x, y), (x, min(y + segment_len, HEIGHT)), 2)
        y += segment_len + gap


def main():
    pygame.init()
    pygame.display.set_caption("Pong AI - Pygame")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    # Buat objek
    player = Paddle(
        x=24,
        y=(HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=PLAYER_SPEED,
    )
    ai = Paddle(
        x=WIDTH - 24 - PADDLE_WIDTH,
        y=(HEIGHT - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=AI_SPEED,
    )
    ball = Ball(
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
    )

    score_left = 0
    score_right = 0
    running = True

    while running:
        dt = clock.tick(FPS)  # batas FPS dan dapatkan delta ms

        # ----- Event -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ----- Input Player -----
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(-player.speed)
        if keys[pygame.K_s]:
            player.move(player.speed)

        # ----- AI -----
        ai_move(ai, ball)

        # ----- Update Bola -----
        ball.update()

        # ----- Deteksi Tabrakan Paddle -----
        # Cek arah bola untuk menghindari double-collision aneh saat overlapped
        if ball.vel_x < 0:
            # menuju ke kiri → kemungkinan tabrak player
            handle_paddle_collision(ball, player)
        else:
            # menuju ke kanan → kemungkinan tabrak AI
            handle_paddle_collision(ball, ai)

        # ----- Skor -----
        if ball.rect.right < 0:
            # bola keluar di kiri → poin kanan (AI)
            score_right += 1
            ball.reset(direction="right")
        elif ball.rect.left > WIDTH:
            # bola keluar di kanan → poin kiri (Player)
            score_left += 1
            ball.reset(direction="left")

        # Opsional: periksa pemenang
        if SCORE_TO_WIN and (score_left >= SCORE_TO_WIN or score_right >= SCORE_TO_WIN):
            # reset skor & posisi untuk melanjutkan permainan
            score_left = 0
            score_right = 0
            player.rect.centery = HEIGHT // 2
            ai.rect.centery = HEIGHT // 2
            ball.reset()

        # ----- Render -----
        screen.fill(BLACK)
        draw_center_line(screen)

        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Render skor
        score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(score_text, score_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
