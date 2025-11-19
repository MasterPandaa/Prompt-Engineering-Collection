import math
import random
import sys
from dataclasses import dataclass

import pygame


# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (240, 240, 240)
BLACK = (15, 15, 15)
GREY = (90, 90, 90)
ACCENT = (100, 200, 255)

# Gameplay tuning
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
PADDLE_SPEED = 7
BALL_RADIUS = 10
BALL_SPEED = 6
BALL_SPEED_INCREMENT = 0.15  # small acceleration over time
BALL_MAX_SPEED = 12

# AI tuning (challenging but beatable)
AI_UPDATE_INTERVAL_MS = 120  # how often AI updates its target (reaction delay)
AI_ERROR_MARGIN_RANGE = (-28, 28)  # random offset added to target
AI_RETURN_TO_CENTER = True  # when ball is moving away, AI drifts to center
AI_MAX_SPEED = 6.5  # slightly slower than human paddle


@dataclass
class Paddle:
    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple = WHITE
    speed: float = PADDLE_SPEED

    def __post_init__(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dy: float):
        self.rect.y += dy
        # Clamp to screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def center_y(self) -> float:
        return self.rect.centery

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)


class Ball:
    def __init__(self, x: float, y: float, radius: int = BALL_RADIUS, color: tuple = WHITE):
        self.init_pos = (x, y)
        self.radius = radius
        self.color = color
        self.reset(direction=random.choice([-1, 1]))
        self.last_touch = None  # 'left' or 'right'

    def reset(self, direction: int):
        self.x, self.y = self.init_pos
        # Initial angle biased toward horizontal to start engaging rallies
        angle = random.uniform(-0.35, 0.35)
        self.speed = BALL_SPEED
        self.vx = math.copysign(self.speed * math.cos(angle), direction)
        self.vy = self.speed * math.sin(angle)

    def update(self):
        # Move
        self.x += self.vx
        self.y += self.vy

        # Wall bounce (top/bottom)
        if self.top <= 0 and self.vy < 0:
            self.y = self.radius  # prevent sticking
            self.vy *= -1
        elif self.bottom >= HEIGHT and self.vy > 0:
            self.y = HEIGHT - self.radius
            self.vy *= -1

        # Gradually increase speed up to cap
        if self.speed < BALL_MAX_SPEED:
            self.speed = min(BALL_MAX_SPEED, self.speed + BALL_SPEED_INCREMENT / FPS)
            # Renormalize velocity to new speed while keeping direction
            angle = math.atan2(self.vy, self.vx)
            self.vx = self.speed * math.cos(angle)
            self.vy = self.speed * math.sin(angle)

    def collide_with_paddle(self, paddle: Paddle, side: str):
        # Only process if overlapping
        ball_rect = pygame.Rect(int(self.left), int(self.top), self.radius * 2, self.radius * 2)
        if not ball_rect.colliderect(paddle.rect):
            return False

        # Compute hit offset: -1 at top, +1 at bottom
        offset = (self.y - paddle.center_y()) / (paddle.height / 2)
        offset = max(-1.0, min(1.0, offset))

        # Desired outgoing angle based on offset (max ~50 degrees)
        max_angle = math.radians(50)
        angle = offset * max_angle

        # Ensure ball goes outward horizontally depending on side
        direction = 1 if side == 'left' else -1

        # Slight speed boost on paddle hit to keep rallies exciting
        self.speed = min(BALL_MAX_SPEED, self.speed + 0.25)

        # Recompute velocity components
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

        # Nudge the ball outside the paddle to prevent re-collision sticking
        if side == 'left':
            self.x = paddle.rect.right + self.radius + 1
        else:
            self.x = paddle.rect.left - self.radius - 1

        self.last_touch = side
        return True

    @property
    def left(self) -> float:
        return self.x - self.radius

    @property
    def right(self) -> float:
        return self.x + self.radius

    @property
    def top(self) -> float:
        return self.y - self.radius

    @property
    def bottom(self) -> float:
        return self.y + self.radius

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class AIPaddleController:
    """Simple but fair AI: it updates its target position at intervals,
    adds a small random error, and only aggressively tracks the ball when
    the ball is moving toward it.
    """

    def __init__(self, paddle: Paddle):
        self.paddle = paddle
        self.target_y = paddle.center_y()
        self.timer = 0

    def update(self, dt_ms: int, ball: Ball):
        self.timer += dt_ms

        # Determine if ball is moving toward the AI (AI on the right side)
        ball_toward_ai = ball.vx > 0

        # Update target at intervals to simulate reaction delay
        if self.timer >= AI_UPDATE_INTERVAL_MS:
            self.timer = 0
            if ball_toward_ai:
                error = random.uniform(*AI_ERROR_MARGIN_RANGE)
                self.target_y = ball.y + error
            else:
                # If ball is moving away, optionally drift to center
                if AI_RETURN_TO_CENTER:
                    self.target_y = HEIGHT / 2

        # Move towards target with capped speed
        dy = 0
        if self.paddle.center_y() < self.target_y - 4:
            dy = min(AI_MAX_SPEED, self.target_y - self.paddle.center_y())
        elif self.paddle.center_y() > self.target_y + 4:
            dy = -min(AI_MAX_SPEED, self.paddle.center_y() - self.target_y)

        self.paddle.move(dy)


def draw_center_line(surface: pygame.Surface):
    dash_height = 12
    gap = 8
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, GREY, (WIDTH // 2 - 2, y, 4, dash_height), border_radius=2)
        y += dash_height + gap


def render_score(surface: pygame.Surface, font: pygame.font.Font, left_score: int, right_score: int):
    left_surf = font.render(str(left_score), True, WHITE)
    right_surf = font.render(str(right_score), True, WHITE)

    surface.blit(left_surf, (WIDTH * 0.25 - left_surf.get_width() / 2, 30))
    surface.blit(right_surf, (WIDTH * 0.75 - right_surf.get_width() / 2, 30))


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 48)
    small_font = pygame.font.SysFont("consolas", 22)

    # Entities
    left_paddle = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball(WIDTH / 2, HEIGHT / 2)

    ai = AIPaddleController(right_paddle)

    left_score = 0
    right_score = 0

    # Serve control
    serving = False
    serve_cooldown = 900  # ms
    serve_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and not serving:
                    # Manual serve (after score or at start)
                    serving = True
                    serve_timer = 0

        # Input (Player)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= PADDLE_SPEED
        if keys[pygame.K_s]:
            dy += PADDLE_SPEED
        left_paddle.move(dy)

        # AI update
        ai.update(dt, ball)

        # Update ball
        if serving:
            serve_timer += dt
            if serve_timer >= serve_cooldown:
                serving = False
        else:
            ball.update()

            # Paddle collisions
            if ball.vx < 0 and ball.left <= left_paddle.rect.right:
                ball.collide_with_paddle(left_paddle, 'left')
            if ball.vx > 0 and ball.right >= right_paddle.rect.left:
                ball.collide_with_paddle(right_paddle, 'right')

            # Scoring
            if ball.right < 0:
                right_score += 1
                ball.reset(direction=1)  # send towards right (player who conceded previously)
                serving = True
                serve_timer = 0
            elif ball.left > WIDTH:
                left_score += 1
                ball.reset(direction=-1)
                serving = True
                serve_timer = 0

        # --- Render ---
        screen.fill(BLACK)
        draw_center_line(screen)

        # Draw entities
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # HUD
        render_score(screen, font, left_score, right_score)

        if serving:
            msg = small_font.render("Press SPACE to serve", True, ACCENT)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
            countdown = max(0, int((serve_cooldown - serve_timer) / 100)) / 10
            cd = small_font.render(f"Auto-serve in {countdown:.1f}s", True, GREY)
            screen.blit(cd, (WIDTH // 2 - cd.get_width() // 2, HEIGHT // 2 - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
