import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_w, K_s

# -----------------------------
# Konfigurasi Umum
# -----------------------------
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (18, 18, 18)
FG_COLOR = (240, 240, 240)
MIDLINE_COLOR = (80, 80, 80)

WIN_SCORE = 10  # Anda bisa ubah target skor kemenangan

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong dengan AI (Pygame)")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 36)
SMALL_FONT = pygame.font.SysFont("consolas", 22)


# -----------------------------
# Class Paddle
# -----------------------------
class Paddle:
    def __init__(self, x, y, width, height, speed=8):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.vel_y = 0  # untuk kontrol pemain; AI akan mengatur ini sendiri

    def draw(self, surface):
        pygame.draw.rect(surface, FG_COLOR, self.rect)

    def update(self):
        self.rect.y += self.vel_y
        # batasi dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def ai_follow(self, target_y, follow_speed_factor=1.0):
        # AI mencoba mengikuti posisi Y bola dengan kecepatan terbatas
        center_y = self.rect.centery
        desired = 0
        if center_y < target_y:
            desired = self.speed * follow_speed_factor
        elif center_y > target_y:
            desired = -self.speed * follow_speed_factor
        else:
            desired = 0
        self.rect.y += int(desired)

        # batasi dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


# -----------------------------
# Class Ball
# -----------------------------
class Ball:
    def __init__(self, x, y, size=14, speed=6):
        self.rect = pygame.Rect(x, y, size, size)
        self.start_speed = speed
        self.speed_x = speed
        self.speed_y = speed * 0.5

    def draw(self, surface):
        pygame.draw.rect(surface, FG_COLOR, self.rect)

    def reset(self, serve_dir=1):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = self.start_speed * serve_dir
        self.speed_y = self.start_speed * 0.5

    def update(self):
        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)

        # pantulan atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y *= -1

    def collide_paddle(self, paddle: Paddle):
        if self.rect.colliderect(paddle.rect):
            # Tentukan sisi tabrakan dan pantulkan
            # Geser bola keluar sedikit agar tidak "menempel"
            if self.speed_x > 0:
                # datang dari kiri ke kanan: tabrak paddle kanan
                self.rect.right = paddle.rect.left
            else:
                # datang dari kanan ke kiri: tabrak paddle kiri
                self.rect.left = paddle.rect.right

            # Pantulkan horizontal
            self.speed_x *= -1

            # Tambahkan variasi sudut berdasarkan titik kontak
            offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
            max_angle_speed = 7.5
            self.speed_y = max(-max_angle_speed, min(max_angle_speed, offset * max_angle_speed))

            # Sedikit percepatan tiap mengenai paddle
            if self.speed_x > 0:
                self.speed_x = min(self.speed_x + 0.5, 12)
            else:
                self.speed_x = max(self.speed_x - 0.5, -12)


# -----------------------------
# Helper: Gambar Midline
# -----------------------------
def draw_midline(surface):
    dash_height = 16
    gap = 12
    x = SCREEN_WIDTH // 2 - 2
    for y in range(0, SCREEN_HEIGHT, dash_height + gap):
        pygame.draw.rect(surface, MIDLINE_COLOR, (x, y, 4, dash_height))


# -----------------------------
# Game Loop
# -----------------------------
def main():
    # Buat objek
    paddle_width, paddle_height = 12, 100
    margin = 24

    player = Paddle(margin, SCREEN_HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height, speed=9)
    ai = Paddle(SCREEN_WIDTH - margin - paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height, speed=8)

    ball = Ball(SCREEN_WIDTH // 2 - 7, SCREEN_HEIGHT // 2 - 7, size=14, speed=6)

    player_score = 0
    ai_score = 0

    w_held = False
    s_held = False

    serve_dir = 1  # arah servis bola setelah skor (1 ke kanan, -1 ke kiri)
    ball.reset(serve_dir=serve_dir)

    running = True
    while running:
        dt = clock.tick(60)  # 60 FPS

        # -------------------------
        # Input
        # -------------------------
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_w:
                    w_held = True
                elif event.key == K_s:
                    s_held = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == KEYUP:
                if event.key == K_w:
                    w_held = False
                elif event.key == K_s:
                    s_held = False

        # Update kecepatan pemain berdasarkan input
        player.vel_y = 0
        if w_held and not s_held:
            player.vel_y = -player.speed
        elif s_held and not w_held:
            player.vel_y = player.speed

        # -------------------------
        # Update Game Objects
        # -------------------------
        player.update()

        # AI mengikuti Y bola (bisa diberi faktor agar tidak terlalu sempurna)
        ai.ai_follow(ball.rect.centery, follow_speed_factor=0.95)

        # Update bola
        ball.update()

        # Cek tabrakan dengan paddle
        ball.collide_paddle(player)
        ball.collide_paddle(ai)

        # Cek skor: keluar kiri/kanan
        if ball.rect.left <= 0:
            ai_score += 1
            serve_dir = -1  # servis ke arah pemain (bola mulai menuju kiri)
            ball.reset(serve_dir=serve_dir)
        elif ball.rect.right >= SCREEN_WIDTH:
            player_score += 1
            serve_dir = 1  # servis ke arah AI (bola mulai menuju kanan)
            ball.reset(serve_dir=serve_dir)

        # -------------------------
        # Render
        # -------------------------
        screen.fill(BG_COLOR)
        draw_midline(screen)

        # Gambar objek
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        # Teks skor
        score_text = FONT.render(f"{player_score}   {ai_score}", True, FG_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(score_text, score_rect)

        # Bantuan kontrol
        help_text = SMALL_FONT.render("Kontrol: W/S untuk naik/turun, ESC atau tutup jendela untuk keluar", True, (180, 180, 180))
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, SCREEN_HEIGHT - 32))

        # Info menang
        if player_score >= WIN_SCORE or ai_score >= WIN_SCORE:
            winner = "Pemain" if player_score > ai_score else "AI"
            win_text = FONT.render(f"{winner} menang! Tekan R untuk restart atau tutup untuk keluar.", True, FG_COLOR)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_text, win_rect)

            # Freeze gerak sampai restart
            pygame.display.flip()
            waiting_restart = True
            while waiting_restart:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit(0)
                    elif event.type == KEYDOWN:
                        if event.key == pygame.K_r:
                            # reset skor dan posisi
                            player_score = 0
                            ai_score = 0
                            serve_dir = 1
                            ball.reset(serve_dir=serve_dir)
                            waiting_restart = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit(0)
                clock.tick(30)
        else:
            pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
