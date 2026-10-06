import sys
import random
import pygame
from typing import Optional


# --- Configuration Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH = 12
PADDLE_HEIGHT = 110
PADDLE_MARGIN = 30
PADDLE_SPEED = 7  # pixels per frame

BALL_SIZE = 14
BALL_SPEED_INITIAL = 5.0
BALL_SPEED_MAX = 13.0
BALL_SPEED_GAIN = 1.04  # gain on each paddle hit
BALL_SPIN_FACTOR = 0.25  # how much off-center hit affects vertical velocity

SCORE_FONT_SIZE = 48
UI_FONT_SIZE = 20
WIN_SCORE = 10

BG_COLOR = (18, 18, 18)
FG_COLOR = (235, 235, 235)
MID_COLOR = (70, 70, 70)
ACCENT_COLOR = (0, 200, 130)


# --- Helper Functions ---

def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


# --- Game Objects ---

class Paddle:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        # AI-specific state
        self._target_y = self.rect.centery

    def move(self, dy: float) -> None:
        self.rect.y += int(dy)
        self.rect.y = int(clamp(self.rect.y, 0, HEIGHT - self.rect.height))

    def follow_target(self, target_y: float) -> None:
        # Move towards target_y with capped speed
        if abs(target_y - self.rect.centery) <= self.speed:
            self.rect.centery = int(target_y)
        else:
            direction = 1 if target_y > self.rect.centery else -1
            self.rect.centery += direction * self.speed
        # Clamp within bounds
        self.rect.y = int(clamp(self.rect.y, 0, HEIGHT - self.rect.height))

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, FG_COLOR, self.rect, border_radius=6)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.vel = pygame.Vector2(0, 0)
        self.reset(direction=random.choice((-1, 1)))

    def reset(self, direction: int) -> None:
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-0.35, 0.35)  # slight random vertical angle
        speed = BALL_SPEED_INITIAL
        self.vel = pygame.Vector2(direction * speed, speed * angle)

    def update(self) -> None:
        # Advance ball position and handle wall bounces.
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        # Collide with top/bottom
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel.y *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel.y *= -1

        # Scoring is handled externally in Game.update() after paddle collisions.

    def collide_paddle(self, paddle: Paddle, is_left: bool) -> None:
        if not self.rect.colliderect(paddle.rect):
            return
        # Reposition ball outside paddle to avoid tunneling
        if self.vel.x < 0 and is_left:
            self.rect.left = paddle.rect.right
        elif self.vel.x > 0 and not is_left:
            self.rect.right = paddle.rect.left

        # Compute hit factor: -1 (top) to 1 (bottom)
        offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        offset = clamp(offset, -1.0, 1.0)

        # Increase speed slightly and reflect horizontally
        speed = min(self.vel.length() * BALL_SPEED_GAIN, BALL_SPEED_MAX)
        direction = -1 if self.vel.x > 0 else 1  # reverse horizontal

        # Apply spin: blend vertical based on offset
        vx = direction * max(2.0, speed * (1.0 - abs(offset) * 0.15))
        vy = speed * offset * (1.0 + BALL_SPIN_FACTOR)
        self.vel = pygame.Vector2(vx, vy)

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, ACCENT_COLOR, self.rect, border_radius=7)


class AIController:
    """A fair, beatable AI with reaction delay and error margin.

    - Reacts at discrete intervals to simulate human-like delay.
    - Introduces a small random error so it's not perfect tracking.
    - Limits paddle speed to keep rallies engaging.
    """

    def __init__(self, paddle: Paddle):
        self.paddle = paddle
        self.reaction_timer = 0.0
        self.reaction_interval_range = (0.085, 0.16)
        self.error_margin_range = (-22, 22)
        self.current_target_y = self.paddle.rect.centery

    def update(self, ball: Ball, dt: float) -> None:
        # Count down reaction timer
        self.reaction_timer -= dt
        if self.reaction_timer <= 0.0:
            # Set new target with some error margin
            error = random.uniform(*self.error_margin_range)
            self.current_target_y = ball.rect.centery + error
            self.reaction_timer = random.uniform(*self.reaction_interval_range)

        # Slight anticipation if ball is heading towards AI
        anticipate = 0.0
        if ball.vel.x > 0:
            anticipate = clamp(abs(ball.vel.x) * 2.0, 0.0, 28.0)
            if ball.rect.centerx < WIDTH * 0.65:
                anticipate *= 0.5
        target = self.current_target_y + (anticipate if self.paddle.rect.centery < self.current_target_y else -anticipate)

        # Follow target with capped speed
        self.paddle.follow_target(target)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.score_font = pygame.font.SysFont("consolas", SCORE_FONT_SIZE)
        self.ui_font = pygame.font.SysFont("consolas", UI_FONT_SIZE)

        # Entities
        left_x = PADDLE_MARGIN
        right_x = WIDTH - PADDLE_MARGIN - PADDLE_WIDTH
        start_y = (HEIGHT - PADDLE_HEIGHT) // 2

        self.left = Paddle(left_x, start_y)
        self.right = Paddle(right_x, start_y)
        self.ball = Ball()
        self.ai = AIController(self.right)

        # Game state
        self.score = [0, 0]
        self.paused = False
        self.running = True

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left.move(-self.left.speed)
        if keys[pygame.K_s]:
            self.left.move(self.left.speed)

    def update(self, dt: float) -> None:
        if self.paused:
            return

        # Move ball first
        self.ball.update()
        # Then resolve paddle collisions
        self.ball.collide_paddle(self.left, is_left=True)
        self.ball.collide_paddle(self.right, is_left=False)

        # AI update
        self.ai.update(self.ball, dt)

        # Scoring: check if ball is out of bounds after collisions
        scorer: Optional[int] = None
        if self.ball.rect.right < 0:
            scorer = 1  # right player scores
        elif self.ball.rect.left > WIDTH:
            scorer = 0  # left player scores

        if scorer is not None:
            self.score[scorer] += 1
            # Serve towards the player who conceded the point
            serve_dir = -1 if scorer == 1 else 1
            self.ball.reset(direction=serve_dir)

    def draw_midline(self) -> None:
        dash_h = 18
        gap = 14
        x = WIDTH // 2 - 2
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(self.screen, MID_COLOR, (x, y, 4, dash_h), border_radius=2)
            y += dash_h + gap

    def draw_scores(self) -> None:
        left_s = self.score_font.render(str(self.score[0]), True, FG_COLOR)
        right_s = self.score_font.render(str(self.score[1]), True, FG_COLOR)
        self.screen.blit(left_s, (WIDTH * 0.25 - left_s.get_width() // 2, 32))
        self.screen.blit(right_s, (WIDTH * 0.75 - right_s.get_width() // 2, 32))

    def draw_ui(self) -> None:
        lines = [
            "Controls: W/S to move | P: Pause | R: Reset | Esc: Quit",
            f"First to {WIN_SCORE} wins",
        ]
        for i, text in enumerate(lines):
            surf = self.ui_font.render(text, True, MID_COLOR)
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT - 30 - i * 22))

    def check_win(self) -> None:
        if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
            self.paused = True
            winner = "Left" if self.score[0] > self.score[1] else "Right"
            msg = f"{winner} Player Wins! Press R to play again."
            surf = self.score_font.render(msg, True, ACCENT_COLOR)
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - surf.get_height() // 2))
            pygame.display.flip()

    def reset(self) -> None:
        self.left.rect.y = (HEIGHT - PADDLE_HEIGHT) // 2
        self.right.rect.y = (HEIGHT - PADDLE_HEIGHT) // 2
        self.score = [0, 0]
        self.ball.reset(direction=random.choice((-1, 1)))
        self.paused = False

    def run(self) -> None:
        while self.running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset()

            self.handle_input()
            self.update(dt)

            # Render
            self.screen.fill(BG_COLOR)
            self.draw_midline()
            self.left.draw(self.screen)
            self.right.draw(self.screen)
            self.ball.draw(self.screen)
            self.draw_scores()
            self.draw_ui()
            self.check_win()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
