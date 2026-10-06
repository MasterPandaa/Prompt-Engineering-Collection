import pygame
import random
import sys

# Konfigurasi dasar
WIDTH, HEIGHT = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle & Bola
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

PLAYER_SPEED = 6
AI_SPEED = 5.2  # Dikurangi sedikit agar AI tidak terlalu sempurna
BALL_SPEED = 5
BALL_SPEED_INCREMENT = 0.4  # Sedikit percepatan tiap kena paddle
MAX_BALL_SPEED = 12

# Margin
PADDING = 20

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.vel_y = 0

    def move(self, dy):
        self.rect.y += dy
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)

    def update(self):
        if self.vel_y != 0:
            self.move(self.vel_y)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=6)

class Ball:
    def __init__(self, size, base_speed):
        self.rect = pygame.Rect(WIDTH//2 - size//2, HEIGHT//2 - size//2, size, size)
        self.base_speed = base_speed
        self.vx = 0
        self.vy = 0
        self.serve(direction=random.choice([-1, 1]))

    def serve(self, direction=1):
        # Arah horizontal sesuai parameter, vertikal acak tapi dibatasi
        self.rect.center = (WIDTH//2, HEIGHT//2)
        angle_y = random.uniform(-3.0, 3.0)
        self.vx = direction * self.base_speed
        self.vy = angle_y

    def speed_up(self, amount):
        # Batasi kecepatan maksimum
        mag = (self.vx**2 + self.vy**2) ** 0.5
        if mag == 0:
            return
        new_mag = min(MAX_BALL_SPEED, mag + amount)
        scale = new_mag / mag
        self.vx *= scale
        self.vy *= scale

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Pantul dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy = -self.vy

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)

def reflect_ball_from_paddle(ball: Ball, paddle: Paddle, is_left_paddle: bool):
    # Balik arah horizontal
    if is_left_paddle and ball.vx < 0:
        ball.vx = -ball.vx
    elif (not is_left_paddle) and ball.vx > 0:
        ball.vx = -ball.vx

    # Tambah variasi sudut: berdasarkan jarak dari pusat paddle
    paddle_center = paddle.rect.centery
    ball_center = ball.rect.centery
    offset = ball_center - paddle_center  # positif berarti kena bagian bawah paddle
    norm = offset / (paddle.rect.height / 2)  # -1 .. 1

    # Skala pengaruh ke vy
    ball.vy += norm * 2.5

    # Sedikit percepatan
    ball.speed_up(BALL_SPEED_INCREMENT)

    # Pastikan bola tidak "menempel" di paddle
    if is_left_paddle:
        ball.rect.left = paddle.rect.right
    else:
        ball.rect.right = paddle.rect.left

def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font untuk skor
    try:
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 28)
    except Exception:
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 72)
        small_font = pygame.font.SysFont("Arial", 28)

    # Entity
    player = Paddle(PADDING, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, PLAYER_SPEED)
    ai = Paddle(WIDTH - PADDING - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT, AI_SPEED)
    ball = Ball(BALL_SIZE, BALL_SPEED)

    player_score = 0
    ai_score = 0

    # Untuk jeda singkat setelah skor
    serve_cooldown = 0  # frame

    running = True
    while running:
        dt = clock.tick(FPS)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Kontrol pemain (W/S)
        keys = pygame.key.get_pressed()
        player.vel_y = 0
        if keys[pygame.K_w]:
            player.vel_y = -player.speed
        if keys[pygame.K_s]:
            player.vel_y = player.speed

        # Update
        if serve_cooldown > 0:
            serve_cooldown -= 1
        else:
            ball.update()

        player.update()

        # AI mengikuti bola pada sumbu Y dengan kecepatan terbatas
        # Tambahkan "dead zone" agar pergerakan lebih realistis dan tidak bergetar
        dead_zone = 6
        if ball.rect.centery < ai.rect.centery - dead_zone:
            ai.move(-ai.speed)
        elif ball.rect.centery > ai.rect.centery + dead_zone:
            ai.move(ai.speed)

        # Deteksi tabrakan bola dengan paddle
        if ball.rect.colliderect(player.rect) and ball.vx < 0:
            reflect_ball_from_paddle(ball, player, is_left_paddle=True)

        if ball.rect.colliderect(ai.rect) and ball.vx > 0:
            reflect_ball_from_paddle(ball, ai, is_left_paddle=False)

        # Cek skor
        scored = False
        if ball.rect.right < 0:
            # AI skor
            ai_score += 1
            ball.serve(direction=1)  # serve ke kanan (ke arah AI) setelah AI skor
            # Reset posisi paddle
            player.rect.centery = HEIGHT // 2
            ai.rect.centery = HEIGHT // 2
            serve_cooldown = FPS // 2  # jeda setengah detik
            scored = True

        if ball.rect.left > WIDTH:
            # Player skor
            player_score += 1
            ball.serve(direction=-1)  # serve ke kiri (ke arah Player) setelah Player skor
            # Reset posisi paddle
            player.rect.centery = HEIGHT // 2
            ai.rect.centery = HEIGHT // 2
            serve_cooldown = FPS // 2
            scored = True

        # Render
        screen.fill(BLACK)

        # Garis tengah
        dash_height = 16
        dash_gap = 12
        x = WIDTH // 2 - 1
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(screen, WHITE, (x, y, 2, dash_height))
            y += dash_height + dash_gap

        # Gambar entitas
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = f"{player_score}   {ai_score}"
        text_surface = font.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 60))
        screen.blit(text_surface, text_rect)

        # Petunjuk kontrol
        help_surface = small_font.render("Kontrol: W = Naik, S = Turun. ESC untuk keluar.", True, (200, 200, 200))
        screen.blit(help_surface, (WIDTH // 2 - help_surface.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()

        # Tambah opsi keluar cepat
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
