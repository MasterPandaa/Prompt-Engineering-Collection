import math
import random
import sys
from dataclasses import dataclass

import pygame


# Game constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Gameplay constants
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 100
PADDLE_MARGIN = 30
PLAYER_SPEED = 7
AI_SPEED = 6  # Slightly slower than player to keep it fair
BALL_SIZE = 14
BALL_SPEED = 6.0
BALL_SPEED_MAX = 12.0
BALL_SPEED_INCREMENT = 0.35  # On paddle hit

# AI behavior tuning
AI_REACTION_MS = 120  # How often AI updates its target
AI_ERROR_BASE = 22  # Base aiming error (pixels)
AI_ERROR_SPEED_SCALE = 1.4  # Error grows with ball speed
AI_RETURN_TO_CENTER_FACTOR = 0.08  # How fast AI recenters when ball moving away


@dataclass
class Paddle:
    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    speed: int = PLAYER_SPEED

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dy: float) -> None:
        self.rect.y += dy
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def center_y(self) -> float:
        return self.rect.centery

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self, size: int = BALL_SIZE, speed: float = BALL_SPEED) -> None:
        self.size = size
        self.base_speed = speed
        self.reset(direction=1)

    def reset(self, direction: int = 1) -> None:
        # direction: 1 to the right, -1 to the left
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        angle = random.uniform(-0.35 * math.pi, 0.35 * math.pi)  # shallow angles
        speed = self.base_speed
        self.vx = math.cos(angle) * speed * direction
        self.vy = math.sin(angle) * speed
        self.rect = pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def clamp_speed(self) -> None:
        s = self.speed()
        if s > BALL_SPEED_MAX:
            scale = BALL_SPEED_MAX / s
            self.vx *= scale
            self.vy *= scale

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy

        # Top/bottom collisions
        if self.top <= 0:
            self.y = self.size / 2
            self.vy = abs(self.vy)
        elif self.bottom >= HEIGHT:
            self.y = HEIGHT - self.size / 2
            self.vy = -abs(self.vy)

        self.sync_rect()

    def collide_with_paddle(self, paddle: Paddle, is_left: bool) -> None:
        if not self.rect.colliderect(paddle.rect):
            return

        # Push ball outside paddle to avoid sticking
        if is_left:
            self.x = paddle.rect.right + self.size / 2
            self.vx = abs(self.vx)
        else:
            self.x = paddle.rect.left - self.size / 2
            self.vx = -abs(self.vx)

        # Add spin based on hit position relative to paddle center
        offset = (self.y - paddle.center_y()) / (paddle.height / 2)
        offset = max(-1.0, min(1.0, offset))
        spin = offset * 4.0  # tweak vertical component
        self.vy += spin

        # Slightly increase speed each hit
        speed_before = self.speed()
        if speed_before < BALL_SPEED_MAX:
            scale = (speed_before + BALL_SPEED_INCREMENT) / max(1e-6, speed_before)
            self.vx *= scale
            self.vy *= scale

        self.clamp_speed()
        self.sync_rect()

    def out_of_bounds(self) -> int | None:
        if self.right < 0:
            return 1  # right player scores
        if self.left > WIDTH:
            return -1  # left player scores
        return None

    def sync_rect(self) -> None:
        self.rect.x = int(self.x - self.size // 2)
        self.rect.y = int(self.y - self.size // 2)

    @property
    def left(self) -> float:
        return self.x - self.size / 2

    @property
    def right(self) -> float:
        return self.x + self.size / 2

    @property
    def top(self) -> float:
        return self.y - self.size / 2

    @property
    def bottom(self) -> float:
        return self.y + self.size / 2

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect)


class AIOpponent:
    def __init__(self, paddle: Paddle) -> None:
        self.paddle = paddle
        self.timer = 0
        self.target_y = paddle.center_y()

    def update(self, dt_ms: int, ball: Ball) -> None:
        self.timer += dt_ms

        # Only choose a new target at reaction intervals
        if self.timer >= AI_REACTION_MS:
            self.timer %= AI_REACTION_MS

            # If ball moving towards the AI (to the right), track with error; otherwise, drift to center
            moving_towards_ai = ball.vx > 0
            if moving_towards_ai:
                # Error increases with ball speed
                error = AI_ERROR_BASE + AI_ERROR_SPEED_SCALE * (ball.speed() - BALL_SPEED)
                error = max(AI_ERROR_BASE, error)
                jitter = random.uniform(-error, error)
                self.target_y = ball.y + jitter
            else:
                # Move back to center gradually
                self.target_y = HEIGHT * 0.5

        # Move towards target
        dy = self.target_y - self.paddle.center_y()
        if abs(dy) > 2:
            step = AI_SPEED if abs(dy) > AI_SPEED else abs(dy)
            self.paddle.move(math.copysign(step, dy))
        else:
            # Small correction towards center when close and ball moves away
            self.paddle.move((HEIGHT * 0.5 - self.paddle.center_y()) * AI_RETURN_TO_CENTER_FACTOR)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 36)

        # Entities
        self.player = Paddle(PADDLE_MARGIN, HEIGHT // 2 - PADDLE_HEIGHT // 2, speed=PLAYER_SPEED)
        self.ai_paddle = Paddle(WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, speed=AI_SPEED)
        self.ball = Ball()
        self.ai = AIOpponent(self.ai_paddle)

        # Scoring
        self.score_left = 0
        self.score_right = 0
        self.serve_dir = random.choice([-1, 1])

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= self.player.speed
        if keys[pygame.K_s]:
            dy += self.player.speed
        self.player.move(dy)

    def update(self, dt_ms: int) -> None:
        self.ball.update()
        self.ball.collide_with_paddle(self.player, is_left=True)
        self.ball.collide_with_paddle(self.ai_paddle, is_left=False)

        self.ai.update(dt_ms, self.ball)

        scorer = self.ball.out_of_bounds()
        if scorer is not None:
            if scorer == 1:
                self.score_right += 1
                self.serve_dir = -1  # serve to left (player) after AI scores
            elif scorer == -1:
                self.score_left += 1
                self.serve_dir = 1  # serve to right (AI) after player scores
            self.ball.reset(direction=self.serve_dir)

    def draw_center_line(self) -> None:
        # Draw dashed center line
        dash_height = 16
        gap = 12
        x = WIDTH // 2 - 2
        for y in range(0, HEIGHT, dash_height + gap):
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(x, y, 4, dash_height))

    def draw_scores(self) -> None:
        left_surf = self.font.render(str(self.score_left), True, WHITE)
        right_surf = self.font.render(str(self.score_right), True, WHITE)
        self.screen.blit(left_surf, (WIDTH * 0.25 - left_surf.get_width() / 2, 20))
        self.screen.blit(right_surf, (WIDTH * 0.75 - right_surf.get_width() / 2, 20))

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.draw_center_line()
        self.player.draw(self.screen)
        self.ai_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.draw_scores()
        pygame.display.flip()

    def run(self) -> None:
        while True:
            dt_ms = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.update(dt_ms)
            self.draw()


if __name__ == "__main__":
    Game().run()
