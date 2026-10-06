import math
import random
import sys
from dataclasses import dataclass

import pygame


# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14
PADDLE_SPEED = 420  # pixels per second
BALL_START_SPEED = 360
BALL_SPEED_INCREMENT = 24
BALL_MAX_SPEED = 720
SCORE_TO_WIN = 11

# Colors
WHITE = (240, 240, 240)
BLACK = (15, 15, 15)
ACCENT = (50, 200, 160)
DIM_WHITE = (200, 200, 200)


@dataclass
class Paddle:
    x: int
    y: float
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple = WHITE

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def center_y(self) -> float:
        return self.y + self.height / 2

    def move(self, dy: float):
        self.y += dy
        # Clamp inside screen
        self.y = max(0, min(self.y, HEIGHT - self.height))

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect(), border_radius=6)


class Ball:
    def __init__(self, x: float, y: float, size: int = BALL_SIZE, color: tuple = WHITE):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.vx = 0.0
        self.vy = 0.0
        self.speed = BALL_START_SPEED
        self.reset(direction=random.choice([-1, 1]))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect(), border_radius=6)

    def reset(self, direction: int):
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT / 2 - self.size / 2
        # Launch with a random angle but avoid near-horizontal for better rallies
        angle = math.radians(random.uniform(-35, 35))
        self.speed = BALL_START_SPEED
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Bounce top/bottom
        if self.y <= 0:
            self.y = 0
            self.vy *= -1
        elif self.y + self.size >= HEIGHT:
            self.y = HEIGHT - self.size
            self.vy *= -1

    def collide_with_paddle(self, paddle: Paddle) -> bool:
        if not self.rect().colliderect(paddle.rect()):
            return False
        # Compute hit position relative to paddle center to create angle
        paddle_center = paddle.center_y()
        ball_center = self.y + self.size / 2
        offset = (ball_center - paddle_center) / (paddle.height / 2)  # -1..1
        offset = max(-1.0, min(1.0, offset))

        # Base bounce angle up to ~50 degrees depending on offset
        max_bounce_angle = math.radians(50)
        bounce_angle = offset * max_bounce_angle

        # Determine direction based on which paddle
        direction = 1 if self.x < WIDTH / 2 else -1

        # Increase speed with each hit, clamp to max
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)
        self.vx = direction * self.speed * math.cos(bounce_angle)
        self.vy = self.speed * math.sin(bounce_angle)

        # Nudge ball outside the paddle to prevent sticking
        if direction > 0:
            self.x = paddle.x + paddle.width
        else:
            self.x = paddle.x - self.size
        return True


class AIController:
    """Simple yet beatable AI with reaction delay and aim error.

    - Updates target only every `reaction_time` seconds (adds delay).
    - Adds a small random error margin that scales with ball speed (beatable).
    - Limits paddle velocity to human-like speed.
    """

    def __init__(self, paddle: Paddle):
        self.paddle = paddle
        self.reaction_time = 0.085  # seconds between target updates
        self._timer = 0.0
        self.target_y = paddle.center_y()
        self.max_speed = PADDLE_SPEED * 0.95

    def update(self, dt: float, ball: Ball):
        self._timer += dt
        if self._timer >= self.reaction_time:
            self._timer = 0.0
            # Predict simplistic intercept point when ball moving towards AI
            predict_y = ball.y + ball.size / 2
            if ball.vx > 0:
                time_to_ai = (self.paddle.x - (ball.x + ball.size)) / ball.vx if ball.vx != 0 else 0
                if time_to_ai > 0:
                    predict_y = ball.y + ball.vy * time_to_ai
                    # Reflect prediction on top/bottom bounds to simulate bounces
                    predict_y = self._reflect_predict(predict_y + ball.size / 2) - ball.size / 2

            # Error scales with ball speed (faster ball -> more error) within bounds
            speed_ratio = min(1.0, ball.speed / BALL_MAX_SPEED)
            error = random.uniform(-22, 22) * (0.6 + 0.8 * speed_ratio)
            self.target_y = max(0 + self.paddle.height / 2,
                                 min(HEIGHT - self.paddle.height / 2, predict_y + error))

        # Move toward target with capped speed
        delta = self.target_y - self.paddle.center_y()
        desired = max(-self.max_speed, min(self.max_speed, delta / max(dt, 1e-4)))
        self.paddle.move(desired * dt)

    @staticmethod
    def _reflect_predict(y: float) -> float:
        # Reflect y across top/bottom to account for multiple bounces in prediction
        period = 2 * HEIGHT
        y_mod = y % period
        if y_mod < HEIGHT:
            return y_mod
        return period - y_mod


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Entities
        self.left = Paddle(32, HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.right = Paddle(WIDTH - 32 - PADDLE_WIDTH, HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.ball = Ball(WIDTH / 2 - BALL_SIZE / 2, HEIGHT / 2 - BALL_SIZE / 2)

        # AI
        self.ai = AIController(self.right)

        # Game state
        self.left_score = 0
        self.right_score = 0
        self.font_large = pygame.font.SysFont("Consolas", 72)
        self.font_small = pygame.font.SysFont("Consolas", 24)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            if not self.handle_events():
                break
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit(0)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dy = 0.0
        if keys[pygame.K_w]:
            dy -= PADDLE_SPEED * dt
        if keys[pygame.K_s]:
            dy += PADDLE_SPEED * dt
        if dy != 0:
            self.left.move(dy)

        # AI update
        self.ai.update(dt, self.ball)

        # Ball update and collisions
        self.ball.update(dt)
        # Collide with paddles
        if self.ball.vx < 0:
            self.ball.collide_with_paddle(self.left)
        else:
            self.ball.collide_with_paddle(self.right)

        # Scoring
        if self.ball.x + self.ball.size < 0:
            self.right_score += 1
            self.ball.reset(direction=-1)
        elif self.ball.x > WIDTH:
            self.left_score += 1
            self.ball.reset(direction=1)

    def draw(self):
        self.screen.fill(BLACK)

        # Center dashed line
        dash_height = 18
        gap = 12
        x = WIDTH // 2 - 2
        for y in range(0, HEIGHT, dash_height + gap):
            pygame.draw.rect(self.screen, DIM_WHITE, pygame.Rect(x, y, 4, dash_height), border_radius=2)

        # Draw entities
        self.left.draw(self.screen)
        self.right.draw(self.screen)
        self.ball.draw(self.screen)

        # Score
        left_surf = self.font_large.render(str(self.left_score), True, ACCENT)
        right_surf = self.font_large.render(str(self.right_score), True, ACCENT)
        self.screen.blit(left_surf, (WIDTH * 0.25 - left_surf.get_width() / 2, 24))
        self.screen.blit(right_surf, (WIDTH * 0.75 - right_surf.get_width() / 2, 24))

        # Help text
        help_text = self.font_small.render("W/S: Move  |  ESC: Quit", True, DIM_WHITE)
        self.screen.blit(help_text, (WIDTH / 2 - help_text.get_width() / 2, HEIGHT - 36))

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
