import pygame
import random

# -----------------------------
# Konstanta & Konfigurasi
# -----------------------------
WIDTH, HEIGHT = 900, 540
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

LINE_THICKNESS = 4
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 90
BALL_SIZE = 14

MARGIN = 24
PLAYER_SPEED = 8
AI_SPEED = 7  # sedikit lebih lambat dari pemain agar fair
BALL_SPEED_X = 7
BALL_SPEED_Y = 5

SCORE_FONT_SIZE = 48


# -----------------------------
# Kelas Paddle & Ball
# -----------------------------
class Paddle:
    def __init__(self, x, y, width, height, speed, boundary_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.boundary_height = boundary_height

    def move(self, dy):
        self.rect.y += dy
        # Batasi agar tetap di dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.boundary_height:
            self.rect.bottom = self.boundary_height

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


class Ball:
    def __init__(self, x, y, size, vel_x, vel_y, boundary_width, boundary_height):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.boundary_width = boundary_width
        self.boundary_height = boundary_height
        self.start_speed_x = vel_x
        self.start_speed_y = vel_y
        self.vel_x = vel_x
        self.vel_y = vel_y

    def reset(self):
        self.rect.center = (self.boundary_width // 2, self.boundary_height // 2)
        # Arah acak ke kiri/kanan dan sedikit variasi vertikal
        self.vel_x = self.start_speed_x * random.choice([-1, 1])
        self.vel_y = random.choice([-self.start_speed_y, self.start_speed_y])

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Pantulan dinding atas/bawah
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y *= -1
        elif self.rect.bottom >= self.boundary_height:
            self.rect.bottom = self.boundary_height
            self.vel_y *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


# -----------------------------
# Fungsi Util
# -----------------------------
def draw_center_line(surface):
    # Garis net putus-putus di tengah
    segment_height = 16
    gap = 12
    x = WIDTH // 2 - LINE_THICKNESS // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, GRAY, (x, y, LINE_THICKNESS, segment_height))
        y += segment_height + gap


def render_score(surface, font, left_score, right_score):
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    # Tempatkan skor di kiri-tengah dan kanan-tengah bagian atas
    surface.blit(left_text, (WIDTH // 2 - 80 - left_text.get_width(), 20))
    surface.blit(right_text, (WIDTH // 2 + 80, 20))


# -----------------------------
# Main Game Loop
# -----------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Pong with AI - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

    # Objek
    player = Paddle(
        x=MARGIN,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=PLAYER_SPEED,
        boundary_height=HEIGHT,
    )

    ai = Paddle(
        x=WIDTH - MARGIN - PADDLE_WIDTH,
        y=HEIGHT // 2 - PADDLE_HEIGHT // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        speed=AI_SPEED,
        boundary_height=HEIGHT,
    )

    ball = Ball(
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        size=BALL_SIZE,
        vel_x=BALL_SPEED_X,
        vel_y=BALL_SPEED_Y,
        boundary_width=WIDTH,
        boundary_height=HEIGHT,
    )
    ball.reset()

    # Skor
    left_score = 0   # Player
    right_score = 0  # AI

    running = True
    while running:
        clock.tick(FPS)  # membatasi FPS

        # 1) Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Input pemain (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_s]:
            dy += player.speed
        player.move(dy)

        # 3) AI sederhana: kejar posisi Y bola
        dead_zone = 8
        if ai.rect.centery < ball.rect.centery - dead_zone:
            ai.move(ai.speed)
        elif ai.rect.centery > ball.rect.centery + dead_zone:
            ai.move(-ai.speed)

        # 4) Update bola
        ball.update()

        # 5) Pantulan pada paddle
        # Cek kolisi dengan player
        if ball.rect.colliderect(player.rect) and ball.vel_x < 0:
            ball.rect.left = player.rect.right  # lepas dari paddle
            ball.vel_x *= -1
            # Variasi sudut pantulan berdasarkan posisi benturan
            offset = (ball.rect.centery - player.rect.centery) / (PADDLE_HEIGHT / 2)
            ball.vel_y = int(max(min(offset * BALL_SPEED_Y * 1.2, 10), -10))

        # Cek kolisi dengan AI
        if ball.rect.colliderect(ai.rect) and ball.vel_x > 0:
            ball.rect.right = ai.rect.left
            ball.vel_x *= -1
            offset = (ball.rect.centery - ai.rect.centery) / (PADDLE_HEIGHT / 2)
            ball.vel_y = int(max(min(offset * BALL_SPEED_Y * 1.2, 10), -10))

        # 6) Skor & reset bola
        scored = False
        if ball.rect.left <= 0:
            right_score += 1
            scored = True
        elif ball.rect.right >= WIDTH:
            left_score += 1
            scored = True

        if scored:
            ball.reset()
            pygame.time.delay(500)

        # -----------------------------
        # Render
        # -----------------------------
        screen.fill(BLACK)
        draw_center_line(screen)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)
        render_score(screen, font, left_score, right_score)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
