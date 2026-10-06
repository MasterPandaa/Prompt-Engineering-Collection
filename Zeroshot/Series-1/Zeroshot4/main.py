import pygame
import sys
import random

# Konstanta Layar
WIDTH, HEIGHT = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ukuran Paddle dan Bola
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

# Kecepatan
PLAYER_SPEED = 7
AI_SPEED = 6  # Kecepatan maksimum paddle AI mengikuti bola
BALL_SPEED = 6


class Paddle:\n    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self, dy):
        self.rect.y += dy
        # Batasi agar tetap di dalam layar
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update(self):
        self.move(self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.vel_x = 0
        self.vel_y = 0
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction=None):
        # Tempatkan bola di tengah dan beri arah acak
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle_options = [-3, -2, -1, 1, 2, 3]
        self.vel_y = random.choice(angle_options)
        base_speed = BALL_SPEED
        self.vel_x = base_speed * (direction if direction in (-1, 1) else random.choice([-1, 1]))

    def update(self, player_paddle: Paddle, ai_paddle: Paddle):
        # Gerak
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Pantul di dinding atas/bawah
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vel_y *= -1

        # Deteksi tumbukan dengan paddle pemain
        if self.rect.colliderect(player_paddle.rect) and self.vel_x < 0:
            # Sedikit variasi pantulan berdasarkan posisi tumbukan
            offset = (self.rect.centery - player_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
            self.vel_y = int(max(min(offset, 1), -1) * (BALL_SPEED + 2)) or self.vel_y
            self.vel_x *= -1
            # Sesuaikan posisi agar tidak "lengket"
            self.rect.left = player_paddle.rect.right

        # Deteksi tumbukan dengan paddle AI
        if self.rect.colliderect(ai_paddle.rect) and self.vel_x > 0:
            offset = (self.rect.centery - ai_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
            self.vel_y = int(max(min(offset, 1), -1) * (BALL_SPEED + 2)) or self.vel_y
            self.vel_x *= -1
            self.rect.right = ai_paddle.rect.left

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong - Player vs AI")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)

        # Objek permainan
        self.player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ai = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()

        # Skor
        self.player_score = 0
        self.ai_score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.speed = 0
        if keys[pygame.K_w]:
            self.player.speed = -PLAYER_SPEED
        if keys[pygame.K_s]:
            self.player.speed = PLAYER_SPEED

    def update_ai(self):
        # AI mengikuti posisi bola pada sumbu Y dengan kecepatan terbatas
        target_y = self.ball.rect.centery
        if self.ai.rect.centery < target_y - 5:
            self.ai.move(min(AI_SPEED, target_y - self.ai.rect.centery))
        elif self.ai.rect.centery > target_y + 5:
            self.ai.move(-min(AI_SPEED, self.ai.rect.centery - target_y))

    def check_score(self):
        # Bola melewati sisi kiri (AI skor)
        if self.ball.rect.right < 0:
            self.ai_score += 1
            self.ball.reset(direction=1)
        # Bola melewati sisi kanan (Player skor)
        if self.ball.rect.left > WIDTH:
            self.player_score += 1
            self.ball.reset(direction=-1)

    def draw_center_line(self):
        # Garis tengah putus-putus
        segment_height = 20
        gap = 15
        x = WIDTH // 2
        y = 0
        while y < HEIGHT:
            pygame.draw.line(self.screen, WHITE, (x, y), (x, min(y + segment_height, HEIGHT)), 2)
            y += segment_height + gap

    def draw_score(self):
        score_text = f"{self.player_score}   {self.ai_score}"
        text_surface = self.font.render(score_text, True, WHITE)
        rect = text_surface.get_rect(center=(WIDTH // 2, 40))
        self.screen.blit(text_surface, rect)

    def run(self):
        while True:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Input & Update
            self.handle_input()
            self.player.update()
            self.update_ai()
            self.ball.update(self.player, self.ai)
            self.check_score()

            # Render
            self.screen.fill(BLACK)
            self.draw_center_line()
            self.player.draw(self.screen)
            self.ai.draw(self.screen)
            self.ball.draw(self.screen)
            self.draw_score()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
