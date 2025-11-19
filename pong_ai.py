import sys
import random
import pygame

# -----------------------------
# Konfigurasi utama
# -----------------------------
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong dengan AI - Pygame")

FPS = 60
WHITE = (255, 255, 255)
BG = (20, 20, 20)
MIDLINE_COLOR = (80, 80, 80)

FONT = pygame.font.SysFont("consolas", 36)
SCORE_FONT = pygame.font.SysFont("consolas", 48)

# -----------------------------
# Class Paddle
# -----------------------------
class Paddle:
    def __init__(self, x, y, width=12, height=100, speed=7):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy):
        self.rect.y += dy
        # Clamp agar tetap di layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def follow_y(self, target_y_center, max_speed=None):
        # Gerak AI mengikuti posisi Y bola (target center)
        # max_speed membatasi kecepatan AI agar tidak terlalu sempurna
        if max_speed is None:
            max_speed = self.speed

        # Hitung selisih posisi
        offset = target_y_center - self.rect.centery

        # Terapkan kecepatan terbatas
        if abs(offset) > max_speed:
            offset = max_speed if offset > 0 else -max_speed

        self.move(offset)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


# -----------------------------
# Class Ball
# -----------------------------
class Ball:
    def __init__(self, x, y, size=14, speed=6):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = speed
        self.reset()

    def reset(self, to_left=None):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # Arah acak: kiri/kanan, atas/bawah
        dir_x = -1 if (to_left is True) else 1 if (to_left is False) else random.choice([-1, 1])
        dir_y = random.choice([-1, 1])
        # Variasi sudut awal
        angle_variation = random.uniform(0.6, 1.0)
        self.vx = dir_x * self.base_speed * angle_variation
        self.vy = dir_y * self.base_speed * (2 - angle_variation) * 0.6

        # Pastikan vy tidak terlalu kecil (agar game seru)
        if abs(self.vy) < 1.8:
            self.vy = 1.8 if self.vy >= 0 else -1.8

    def move(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def bounce_vertical(self):
        self.vy *= -1

    def bounce_horizontal(self, impact_factor=0.25, speedup=1.05):
        # Balik arah X
        self.vx *= -1
        # Sedikit percepat bola setelah kena paddle
        self.vx *= speedup
        self.vy *= speedup
        # Variasikan sudut berdasarkan titik tumbukan (impact factor)
        # impact_factor ~ seberapa tajam perubahan sudut berdasarkan offset
        # offset: seberapa jauh dari tengah paddle
        # (nilai ini akan diatur dari luar menggunakan offset aktual)
        # Di sini hanya hook; offset diproses oleh collider di luar.
        # Dibiarkan untuk konsistensi antarmuka.


# -----------------------------
# Fungsi utilitas
# -----------------------------
def draw_midline(surface):
    # Garis tengah putus-putus
    segment_height = 16
    gap = 12
    x = SCREEN_WIDTH // 2 - 2
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(surface, MIDLINE_COLOR, (x, y, 4, segment_height))
        y += segment_height + gap

def draw_score(surface, left_score, right_score):
    left_text = SCORE_FONT.render(str(left_score), True, WHITE)
    right_text = SCORE_FONT.render(str(right_score), True, WHITE)
    surface.blit(left_text, (SCREEN_WIDTH // 2 - 80 - left_text.get_width(), 20))
    surface.blit(right_text, (SCREEN_WIDTH // 2 + 80, 20))

def handle_ball_collisions(ball, player, ai):
    # Tabrak dinding atas/bawah
    if ball.rect.top <= 0 or ball.rect.bottom >= SCREEN_HEIGHT:
        ball.bounce_vertical()
        # Pastikan bola tidak nempel di luar boundary
        if ball.rect.top < 0:
            ball.rect.top = 0
        if ball.rect.bottom > SCREEN_HEIGHT:
            ball.rect.bottom = SCREEN_HEIGHT

    # Tabrak paddle kiri (player)
    if ball.rect.colliderect(player.rect):
        # Geser bola keluar paddle agar tidak "menempel"
        ball.rect.left = player.rect.right

        # Hitung offset tumbukan relatif terhadap pusat paddle
        offset = (ball.rect.centery - player.rect.centery) / (player.rect.height / 2)
        # Clamp offset ke [-1, 1]
        offset = max(-1, min(1, offset))
        # Sesuaikan vy berdasarkan offset
        ball.vy += offset * 4.0
        # Pantulkan horizontal + percepat
        ball.bounce_horizontal()
    # Tabrak paddle kanan (AI)
    elif ball.rect.colliderect(ai.rect):
        ball.rect.right = ai.rect.left
        offset = (ball.rect.centery - ai.rect.centery) / (ai.rect.height / 2)
        offset = max(-1, min(1, offset))
        ball.vy += offset * 4.0
        ball.bounce_horizontal()


def main():
    clock = pygame.time.Clock()

    # Objek permainan
    paddle_margin = 24
    paddle_width, paddle_height = 12, 100
    player = Paddle(
        x=paddle_margin,
        y=SCREEN_HEIGHT // 2 - paddle_height // 2,
        width=paddle_width,
        height=paddle_height,
        speed=7
    )
    ai = Paddle(
        x=SCREEN_WIDTH - paddle_margin - paddle_width,
        y=SCREEN_HEIGHT // 2 - paddle_height // 2,
        width=paddle_width,
        height=paddle_height,
        speed=7
    )

    ball = Ball(
        x=SCREEN_WIDTH // 2 - 7,
        y=SCREEN_HEIGHT // 2 - 7,
        size=14,
        speed=6
    )

    left_score = 0
    right_score = 0
    max_score = 10  # Boleh diubah; set ke None jika tak ingin kondisi menang

    # Parameter AI
    ai_max_speed = 6.2    # Kecepatan maksimal AI mengikuti bola
    ai_reaction_delay = 0 # Frame delay; bisa set >0 untuk menurunkan reaksi AI
    ai_track_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)  # dt tidak terlalu dipakai di sini, tetapi berguna jika ingin time-based movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_s]:
            dy += player.speed
        player.move(dy)

        # Gerak bola
        ball.move()

        # Logika AI (ikuti Y bola dengan sedikit batasan)
        ai_track_timer += 1
        if ai_track_timer >= ai_reaction_delay:
            ai.follow_y(ball.rect.centery, max_speed=ai_max_speed)
            ai_track_timer = 0

        # Tabrakan bola
        handle_ball_collisions(ball, player, ai)

        # Cek skor: jika bola melewati kiri/kanan
        if ball.rect.right < 0:
            right_score += 1
            ball.reset(to_left=False)  # serve ke kanan (kembali ke pemain)
        elif ball.rect.left > SCREEN_WIDTH:
            left_score += 1
            ball.reset(to_left=True)   # serve ke kiri (kembali ke AI)

        # Kondisi menang (opsional)
        winner_text = None
        if max_score is not None:
            if left_score >= max_score:
                winner_text = "Pemain Kiri Menang!"
            elif right_score >= max_score:
                winner_text = "AI (Kanan) Menang!"

        # Gambar
        WIN.fill(BG)
        draw_midline(WIN)
        player.draw(WIN)
        ai.draw(WIN)
        ball.draw(WIN)
        draw_score(WIN, left_score, right_score)

        if winner_text:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            WIN.blit(overlay, (0, 0))
            text_surface = FONT.render(winner_text + "  (Tekan R untuk ulang)", True, WHITE)
            WIN.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2,
                                    SCREEN_HEIGHT // 2 - text_surface.get_height() // 2))

            # Tahan permainan hingga R ditekan untuk reset skor
            if keys[pygame.K_r]:
                left_score = 0
                right_score = 0
                winner_text = None
                ball.reset()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
