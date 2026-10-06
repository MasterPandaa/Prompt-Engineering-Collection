import pygame
import sys
import random
import math

# Inisialisasi Pygame
pygame.init()
pygame.display.set_caption("Pong dengan AI - Pygame")

# Konstanta layar
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Font
FONT = pygame.font.SysFont("consolas", 32)

class Paddle:
    def __init__(self, x, y, width, height, speed=7):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def move(self, dy):
        self.rect.y += dy
        # Batasi agar tidak keluar layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Ball:
    def __init__(self, size=14, base_speed=6.0, max_angle_deg=45):
        self.size = size
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - size // 2,
            SCREEN_HEIGHT // 2 - size // 2,
            size,
            size
        )
        self.base_speed = base_speed
        self.speed = base_speed
        self.max_angle = math.radians(max_angle_deg)
        self.vel_x = 0.0
        self.vel_y = 0.0
        # Arah awal acak
        self.reset(start_to_right=random.choice([True, False]))

    def reset(self, start_to_right: bool):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = self.base_speed
        angle = random.uniform(-self.max_angle, self.max_angle)
        direction = 1 if start_to_right else -1
        self.vel_x = direction * self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

    def update(self, left_paddle: Paddle, right_paddle: Paddle):
        # Gerakkan bola
        self.rect.x += int(round(self.vel_x))
        self.rect.y += int(round(self.vel_y))

        # Pantulan dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y = -self.vel_y
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = -self.vel_y

        # Deteksi skor
        scorer = None  # "left" atau "right"
        if self.rect.left <= 0:
            scorer = "right"
        elif self.rect.right >= SCREEN_WIDTH:
            scorer = "left"

        # Tumbukan dengan paddle kiri
        if self.rect.colliderect(left_paddle.rect) and self.vel_x < 0:
            self._bounce_from_paddle(left_paddle, is_left=True)

        # Tumbukan dengan paddle kanan
        if self.rect.colliderect(right_paddle.rect) and self.vel_x > 0:
            self._bounce_from_paddle(right_paddle, is_left=False)

        return scorer

    def _bounce_from_paddle(self, paddle: Paddle, is_left: bool):
        # Hit position relatif terhadap tengah paddle
        paddle_center_y = paddle.rect.centery
        ball_center_y = self.rect.centery
        offset = (ball_center_y - paddle_center_y) / (paddle.rect.height / 2)
        offset = max(-1.0, min(1.0, offset))

        # Sudut pantulan
        angle = offset * self.max_angle

        # Tingkatkan kecepatan sedikit setiap kali memantul paddle
        self.speed *= 1.03

        # Arah X setelah pantulan: ke kanan jika dari kiri, ke kiri jika dari kanan
        dir_x = 1 if is_left else -1
        self.vel_x = dir_x * self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

        # Sesuaikan posisi agar bola tidak "menempel" pada paddle
        if is_left:
            self.rect.left = paddle.rect.right
        else:
            self.rect.right = paddle.rect.left

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

def draw_center_line(surface):
    dash_height = 10
    gap = 10
    x = SCREEN_WIDTH // 2
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.line(surface, GREY, (x, y), (x, min(y + dash_height, SCREEN_HEIGHT)), 2)
        y += dash_height + gap

def ai_move(ai_paddle: Paddle, ball: Ball):
    # AI sederhana: kejar pusat Y bola dengan kecepatan terbatas
    target_y = ball.rect.centery
    paddle_center = ai_paddle.rect.centery
    if paddle_center < target_y - 4:
        ai_paddle.move(ai_paddle.speed)
    elif paddle_center > target_y + 4:
        ai_paddle.move(-ai_paddle.speed)
    # batas layar ditangani oleh move()

def main():
    # Objek permainan
    paddle_width, paddle_height = 12, 100
    player_speed = 7
    ai_speed = 6

    left_paddle = Paddle(
        x=30,
        y=SCREEN_HEIGHT // 2 - paddle_height // 2,
        width=paddle_width,
        height=paddle_height,
        speed=player_speed
    )
    right_paddle = Paddle(
        x=SCREEN_WIDTH - 30 - paddle_width,
        y=SCREEN_HEIGHT // 2 - paddle_height // 2,
        width=paddle_width,
        height=paddle_height,
        speed=ai_speed
    )
    ball = Ball(size=14, base_speed=6.0, max_angle_deg=45)

    score_left = 0
    score_right = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= left_paddle.speed
        if keys[pygame.K_s]:
            dy += left_paddle.speed
        left_paddle.move(dy)

        # AI gerakkan paddle kanan
        ai_move(right_paddle, ball)

        # Update bola dan cek skor
        scorer = ball.update(left_paddle, right_paddle)
        if scorer == "left":
            score_left += 1
            ball.reset(start_to_right=True)   # servis dari kiri ke kanan
        elif scorer == "right":
            score_right += 1
            ball.reset(start_to_right=False)  # servis dari kanan ke kiri

        # Gambar
        screen.fill(BLACK)
        draw_center_line(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Tampilkan skor
        score_text = FONT.render(f"{score_left}   {score_right}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(score_text, score_rect)

        # Instruksi kecil
        hint_text = FONT.render("W/S untuk bergerak • ESC untuk keluar", True, GREY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(hint_text, hint_rect)

        # Keluar dengan ESC
        if keys[pygame.K_ESCAPE]:
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
