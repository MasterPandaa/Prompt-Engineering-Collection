import math
import random
import sys
from dataclasses import dataclass
from typing import Tuple

import pygame


# ----- Configuration -----
WIDTH, HEIGHT = 800, 600
FPS = 120

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Gameplay
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 12
MARGIN = 20

PLAYER_SPEED = 420.0  # px/s
AI_MAX_SPEED = 400.0  # px/s
BALL_SPEED = 360.0     # initial speed px/s
BALL_SPEED_INCREMENT = 24.0  # on each paddle hit
BALL_MAX_SPEED = 720.0

AI_REACTION_TIME = 0.12  # seconds
AI_AIM_ERROR = 22  # pixels, base amplitude
AI_RECENTER_SPEED = 200.0  # when ball is going away

SCORE_TO_WIN = 11


@dataclass
class Paddle:
    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: Tuple[int, int, int] = WHITE

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.velocity = 0.0  # signed, for smoothing if needed

    def move_towards(self, target_y: float, max_speed: float, dt: float) -> None:
        center_y = self.rect.centery
        delta = target_y - center_y
        # Proportional control with clamp for fairness
        desired_speed = max(-max_speed, min(max_speed, 6.0 * delta))
        self.velocity = desired_speed
        self.rect.y += int(self.velocity * dt)
        self.clamp_to_screen()

    def player_input(self, up: bool, down: bool, dt: float) -> None:
        vy = 0.0
        if up and not down:
            vy = -PLAYER_SPEED
        elif down and not up:
            vy = PLAYER_SPEED
        self.rect.y += int(vy * dt)
        self.clamp_to_screen()

    def clamp_to_screen(self) -> None:
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)


@dataclass
class Ball:
    x: int
    y: int
    size: int = BALL_SIZE
    color: Tuple[int, int, int] = WHITE

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.vel = pygame.Vector2(BALL_SPEED, 0).rotate(random.uniform(-30, 30))

    def reset(self, direction: int) -> None:
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-30, 30)
        self.vel = pygame.Vector2(direction * BALL_SPEED, 0).rotate(angle)

    def update(self, dt: float) -> None:
        # Move
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)

        # Top/bottom wall collision
        if self.rect.top <= 0 and self.vel.y < 0:
            self.rect.top = 0
            self.vel.y *= -1
        if self.rect.bottom >= HEIGHT and self.vel.y > 0:
            self.rect.bottom = HEIGHT
            self.vel.y *= -1

    def collide_paddle(self, paddle: Paddle) -> bool:
        if self.rect.colliderect(paddle.rect):
            # Determine hit position relative to paddle center to compute bounce angle
            offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
            offset = max(-1.0, min(1.0, offset))

            speed = min(self.vel.length() + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)

            # Determine new angle: max 50 degrees off horizontal
            max_angle = math.radians(50)
            angle = offset * max_angle

            # Set direction based on side of the paddle
            direction = 1 if paddle.rect.centerx < WIDTH // 2 else -1
            self.vel.from_polar((speed, math.degrees(angle)))
            self.vel.x = abs(self.vel.x) * direction

            # Nudge the ball out of the paddle to prevent sticking
            if direction > 0:
                self.rect.left = paddle.rect.right
            else:
                self.rect.right = paddle.rect.left
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)


class PongGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 28)
        self.big_font = pygame.font.SysFont("Consolas", 48)

        # Entities
        self.player = Paddle(MARGIN, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ai = Paddle(WIDTH - MARGIN - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2)

        # Game state
        self.left_score = 0
        self.right_score = 0
        self.serving_dir = random.choice([-1, 1])
        self.waiting_for_serve = True

        # AI state
        self.ai_timer = 0.0
        self.ai_target_y = HEIGHT // 2
        self.ai_error = 0.0
        self.ai_error_timer = 0.0

    def run(self) -> None:
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and self.waiting_for_serve:
                    self.ball.reset(self.serving_dir)
                    self.waiting_for_serve = False
        return True

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.player.player_input(keys[pygame.K_w], keys[pygame.K_s], dt)

        if not self.waiting_for_serve:
            self.ball.update(dt)
            # Collisions
            hit_left = self.ball.collide_paddle(self.player)
            hit_right = self.ball.collide_paddle(self.ai)
            if hit_left or hit_right:
                pass  # handled in collide_paddle

            # Goals
            if self.ball.rect.right < 0:
                self.right_score += 1
                self.serving_dir = 1
                self.waiting_for_serve = True
            elif self.ball.rect.left > WIDTH:
                self.left_score += 1
                self.serving_dir = -1
                self.waiting_for_serve = True

        # Update AI regardless so it recenters during serve
        self.update_ai(dt)

    def update_ai(self, dt: float) -> None:
        # Change the random error slowly over time
        self.ai_error_timer += dt
        if self.ai_error_timer >= 0.6:
            self.ai_error_timer = 0.0
            self.ai_error = random.uniform(-AI_AIM_ERROR, AI_AIM_ERROR)

        ball_moving_towards_ai = self.ball.vel.x > 0
        self.ai_timer += dt

        if ball_moving_towards_ai and not self.waiting_for_serve:
            # Only adjust target after reaction time elapsed
            if self.ai_timer >= AI_REACTION_TIME:
                self.ai_timer = 0.0
                # Predict where the ball will be when it reaches AI's x using simple reflection prediction
                predicted_y = self.predict_ball_y_at_x(self.ai.rect.centerx)
                self.ai_target_y = predicted_y + self.ai_error
            # Move towards target with capped speed
            self.ai.move_towards(self.ai_target_y, AI_MAX_SPEED, dt)
        else:
            # Recenter slowly when ball is moving away or during serve
            self.ai.move_towards(HEIGHT / 2, AI_RECENTER_SPEED, dt)

    def predict_ball_y_at_x(self, target_x: int) -> float:
        # Predict y position when ball reaches target_x, simulating wall bounces in 1D vertical space
        pos = pygame.Vector2(self.ball.rect.center)
        vel = self.ball.vel.copy()
        if vel.x == 0:
            return pos.y

        time_to_x = (target_x - pos.x) / vel.x
        if time_to_x <= 0:
            return pos.y

        projected_y = pos.y + vel.y * time_to_x
        # Reflect off top/bottom walls using modular arithmetic
        period = 2 * (HEIGHT - self.ball.size)
        y_mod = (projected_y - self.ball.size) % period
        if y_mod > (HEIGHT - self.ball.size):
            y_mod = period - y_mod
        return y_mod + self.ball.size / 2

    def draw(self) -> None:
        self.screen.fill(BLACK)

        # Middle line
        for y in range(0, HEIGHT, 24):
            pygame.draw.rect(self.screen, GREY, (WIDTH // 2 - 2, y, 4, 12))

        # Draw entities
        self.player.draw(self.screen)
        self.ai.draw(self.screen)
        self.ball.draw(self.screen)

        # Scores
        left_text = self.big_font.render(str(self.left_score), True, WHITE)
        right_text = self.big_font.render(str(self.right_score), True, WHITE)
        self.screen.blit(left_text, (WIDTH // 2 - 80 - left_text.get_width(), 24))
        self.screen.blit(right_text, (WIDTH // 2 + 80, 24))

        # Serve/help text
        if self.waiting_for_serve:
            msg = "Press SPACE to serve"
            serve_text = self.font.render(msg, True, GREY)
            self.screen.blit(serve_text, (WIDTH // 2 - serve_text.get_width() // 2, HEIGHT // 2 - 40))

        # Win condition
        if self.left_score >= SCORE_TO_WIN or self.right_score >= SCORE_TO_WIN:
            winner = "Player" if self.left_score > self.right_score else "AI"
            win_text = self.big_font.render(f"{winner} Wins!", True, WHITE)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 12))

        pygame.display.flip()


if __name__ == "__main__":
    PongGame().run()
