import sys
import random
from dataclasses import dataclass

import pygame


# Window configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Gameplay constants
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 100
PADDLE_MARGIN = 30
PADDLE_SPEED = 6.0

BALL_SIZE = 14
BALL_SPEED_START = 5.0
BALL_SPEED_INCREMENT = 0.25
BALL_SPEED_MAX = 12.0

SCORE_TO_WIN = 11
COUNTDOWN_TIME = 1200  # ms between point and serve


@dataclass
class Bounds:
    width: int
    height: int

    @property
    def center(self) -> pygame.Vector2:
        return pygame.Vector2(self.width / 2, self.height / 2)


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, speed: float) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.velocity = 0.0

    def update(self, dt: float, bounds: Bounds) -> None:
        # Move paddle vertically; clamp to screen bounds
        dy = self.velocity * dt
        self.rect.y += int(dy)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > bounds.height:
            self.rect.bottom = bounds.height

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=4)

    def center_y(self) -> float:
        return self.rect.centery


class AIPaddle(Paddle):
    def __init__(self, x: int, y: int, width: int, height: int, speed: float) -> None:
        super().__init__(x, y, width, height, speed)
        # AI parameters tuned to be challenging but beatable
        self.reaction_delay = 0.10  # seconds before adjusting target
        self.error_margin = 18      # pixels of target jitter
        self.track_smooth = 0.18    # lerp factor toward target per update
        self._time_since_react = 0.0
        self._target_y = float(self.rect.centery)

    def _predict_target(self, ball_rect: pygame.Rect, ball_vel: pygame.Vector2, bounds: Bounds) -> float:
        # Basic prediction: where ball will be when it reaches AI x, with wall bounces
        if ball_vel.x <= 0:
            # Ball moving away; drift back to center slowly
            return bounds.height / 2

        time_to_reach = (self.rect.left - ball_rect.centerx) / ball_vel.x
        if time_to_reach <= 0:
            return ball_rect.centery

        # Predict y with vertical bounces
        predicted_y = ball_rect.centery + ball_vel.y * time_to_reach
        # Reflect off top/bottom bounds
        h = bounds.height
        # Mirror reflection within [0, h]
        while predicted_y < 0 or predicted_y > h:
            if predicted_y < 0:
                predicted_y = -predicted_y
            if predicted_y > h:
                predicted_y = 2 * h - predicted_y

        # Add a small error so AI is not perfect
        jitter = random.uniform(-self.error_margin, self.error_margin)
        return predicted_y + jitter

    def update_ai(self, dt: float, ball_rect: pygame.Rect, ball_vel: pygame.Vector2, bounds: Bounds) -> None:
        self._time_since_react += dt
        if self._time_since_react >= self.reaction_delay:
            self._time_since_react = 0.0
            self._target_y = self._predict_target(ball_rect, ball_vel, bounds)

        # Smooth tracking towards target
        desired = self._target_y - self.rect.centery
        move = desired * self.track_smooth
        # Convert to a velocity capped by paddle speed
        max_step = self.speed
        move = max(-max_step, min(max_step, move))
        self.velocity = move
        super().update(dt, bounds)


class Ball:
    def __init__(self, x: int, y: int, size: int, speed: float) -> None:
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (x, y)
        self.velocity = pygame.Vector2(speed, 0)
        self.speed = speed
        self.serve_cooldown = 0  # ms until movement resumes

    def reset(self, center: pygame.Vector2, to_left: bool | None = None) -> None:
        self.rect.center = (int(center.x), int(center.y))
        # Randomize initial direction
        angle_choices = [random.uniform(-25, 25), random.uniform(155, 205)]
        angle = random.choice(angle_choices)
        direction = pygame.Vector2(1, 0).rotate(angle)
        if to_left is True:
            direction.x = -abs(direction.x)
        elif to_left is False:
            direction.x = abs(direction.x)
        # Normalize and scale to current speed
        self.velocity = direction.normalize() * self.speed
        self.serve_cooldown = COUNTDOWN_TIME

    def update(self, dt_ms: float, bounds: Bounds, paddles: tuple[Paddle, Paddle]) -> int | None:
        # Returns: None for no score, 0 if left scores, 1 if right scores
        if self.serve_cooldown > 0:
            self.serve_cooldown -= int(dt_ms)
            return None

        dt = dt_ms / (1000.0 / FPS)  # normalize to frame-tick movement units
        move = self.velocity * dt
        self.rect.x += int(move.x)
        self.rect.y += int(move.y)

        # Top/bottom collision
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y *= -1
        elif self.rect.bottom >= bounds.height:
            self.rect.bottom = bounds.height
            self.velocity.y *= -1

        # Paddle collisions
        left, right = paddles
        scored: int | None = None
        if self.rect.right < 0:
            scored = 1  # right scores
        elif self.rect.left > bounds.width:
            scored = 0  # left scores

        if scored is not None:
            # Speed up slightly on each score to keep tension
            self.speed = min(BALL_SPEED_MAX, self.speed + BALL_SPEED_INCREMENT)
            return scored

        # Check collisions only if ball is on screen
        if self.rect.colliderect(left.rect) and self.velocity.x < 0:
            self._bounce_off_paddle(left)
        elif self.rect.colliderect(right.rect) and self.velocity.x > 0:
            self._bounce_off_paddle(right)

        return None

    def _bounce_off_paddle(self, paddle: Paddle) -> None:
        # Position correction: place ball outside the paddle to prevent sticking
        if self.velocity.x < 0:
            self.rect.left = paddle.rect.right
        else:
            self.rect.right = paddle.rect.left

        # Compute bounce angle based on hit position (relative to paddle center)
        offset = (self.rect.centery - paddle.rect.centery)
        norm = offset / (paddle.rect.height / 2)
        norm = max(-1.0, min(1.0, norm))

        # Map to angle range (-60 to 60 degrees) to keep play flowing
        angle = norm * 60
        direction = 1 if self.velocity.x > 0 else -1
        new_dir = pygame.Vector2(direction, 0).rotate(angle)

        # Slight speed-up on paddle hit
        self.speed = min(BALL_SPEED_MAX, self.speed + BALL_SPEED_INCREMENT)
        self.velocity = new_dir.normalize() * self.speed

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=self.rect.width // 2)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.bounds = Bounds(WIDTH, HEIGHT)

        # Fonts
        self.font_score = pygame.font.SysFont("consolas", 48)
        self.font_small = pygame.font.SysFont("consolas", 20)

        # Entities
        self.left_paddle = Paddle(
            PADDLE_MARGIN,
            HEIGHT // 2 - PADDLE_HEIGHT // 2,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            PADDLE_SPEED,
        )
        self.right_paddle = AIPaddle(
            WIDTH - PADDLE_MARGIN - PADDLE_WIDTH,
            HEIGHT // 2 - PADDLE_HEIGHT // 2,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            PADDLE_SPEED * 0.95,
        )
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SPEED_START)
        self.ball.reset(self.bounds.center)

        # Scores
        self.score = [0, 0]
        self.winner: int | None = None

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        vel = 0.0
        if keys[pygame.K_w]:
            vel -= self.left_paddle.speed
        if keys[pygame.K_s]:
            vel += self.left_paddle.speed
        self.left_paddle.velocity = vel

    def update(self, dt_ms: float) -> None:
        if self.winner is not None:
            return

        self.handle_input()
        self.left_paddle.update(self._dt_px(dt_ms), self.bounds)
        self.right_paddle.update_ai(self._dt_px(dt_ms), self.ball.rect, self.ball.velocity, self.bounds)

        scored = self.ball.update(dt_ms, self.bounds, (self.left_paddle, self.right_paddle))
        if scored is not None:
            self.score[scored] += 1
            if self.score[scored] >= SCORE_TO_WIN:
                self.winner = scored
            # Serve towards the player who conceded the point
            self.ball.reset(self.bounds.center, to_left=(scored == 1))

    def draw_center_line(self) -> None:
        seg_h = 20
        gap = 16
        x = WIDTH // 2 - 2
        for y in range(0, HEIGHT, seg_h + gap):
            pygame.draw.rect(self.screen, GREY, pygame.Rect(x, y, 4, seg_h), border_radius=2)

    def draw_hud(self) -> None:
        left = self.font_score.render(str(self.score[0]), True, WHITE)
        right = self.font_score.render(str(self.score[1]), True, WHITE)
        self.screen.blit(left, (WIDTH * 0.25 - left.get_width() // 2, 20))
        self.screen.blit(right, (WIDTH * 0.75 - right.get_width() // 2, 20))

        if self.ball.serve_cooldown > 0 and self.winner is None:
            secs = max(0, int(self.ball.serve_cooldown / 400) + 1)
            text = self.font_small.render(f"Serve in {secs}", True, GREY)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))

        if self.winner is not None:
            msg = f"Player {'Left' if self.winner == 0 else 'Right'} Wins!"
            text = self.font_score.render(msg, True, WHITE)
            sub = self.font_small.render("Press R to restart or ESC to quit", True, GREY)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
            self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

    def _dt_px(self, dt_ms: float) -> float:
        # Convert milliseconds delta to pixel movement per frame baseline
        return (dt_ms / (1000.0 / FPS)) * 1.0

    def run(self) -> None:
        while True:
            dt_ms = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                    if event.key == pygame.K_r and self.winner is not None:
                        self.score = [0, 0]
                        self.winner = None
                        self.ball.speed = BALL_SPEED_START
                        self.ball.reset(self.bounds.center)

            self.update(dt_ms)

            # Render
            self.screen.fill(BLACK)
            self.draw_center_line()
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
