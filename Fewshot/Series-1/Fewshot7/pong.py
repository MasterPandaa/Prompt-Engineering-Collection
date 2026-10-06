import sys
import random
import pygame

# --- Configurations ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (180, 180, 180)

# Gameplay settings
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
PLAYER_SPEED = 7
AI_MAX_SPEED = 6
BALL_SIZE = 14
BALL_SPEED = 6
BALL_SPEED_INCREMENT = 0.4  # increase speed slightly after paddle bounce
MAX_BALL_SPEED = 12
CENTER_LINE_SEGMENT = 12
CENTER_LINE_GAP = 8


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, speed: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, dy: float):
        self.rect.y += dy
        # clamp within screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


class Ball:
    def __init__(self, x: int, y: int, size: int, base_speed: float):
        self.rect = pygame.Rect(x, y, size, size)
        self.base_speed = base_speed
        self.vx = 0
        self.vy = 0
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction: int):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        angle = random.uniform(-0.8, 0.8)  # more horizontal angles
        speed = self.base_speed
        # Convert angle to velocity; keep magnitude ~ speed
        self.vx = direction * speed * (1 if random.random() < 0.8 else 0.9)
        self.vy = speed * angle

    def move(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)


def draw_center_line(surface: pygame.Surface):
    x = SCREEN_WIDTH // 2
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.line(surface, GREY, (x, y), (x, y + CENTER_LINE_SEGMENT), 3)
        y += CENTER_LINE_SEGMENT + CENTER_LINE_GAP


def ai_follow_ball(ai: Paddle, ball: Ball):
    # Simple proportional controller towards ball's Y with capped speed
    target_y = ball.rect.centery
    delta = target_y - ai.rect.centery
    if abs(delta) < 2:
        return  # deadzone
    speed = min(AI_MAX_SPEED, max(-AI_MAX_SPEED, delta * 0.25))
    ai.move(speed)


def reflect_ball_from_paddle(ball: Ball, paddle: Paddle):
    # Determine hit position relative to paddle center to add vertical deflection
    offset = (ball.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
    offset = max(-1.0, min(1.0, offset))

    # Reverse X and slightly increase speed
    speed_mag = (ball.vx ** 2 + ball.vy ** 2) ** 0.5
    speed_mag = min(MAX_BALL_SPEED, max(BALL_SPEED, speed_mag + BALL_SPEED_INCREMENT))

    direction = 1 if ball.vx > 0 else -1
    direction *= -1  # reverse X

    # map offset to angle (max ~ 50 degrees)
    max_angle = 0.87  # ~50 degrees in radians
    angle = offset * max_angle

    # Recompose velocity with new direction and angle; keep magnitude
    # bias more horizontal so game is fun
    import math
    ball.vx = direction * speed_mag * math.cos(angle)
    ball.vy = speed_mag * math.sin(angle)

    # Nudge ball outside paddle to avoid sticky collisions
    if direction > 0:
        ball.rect.left = paddle.rect.right
    else:
        ball.rect.right = paddle.rect.left


def handle_collisions(ball: Ball, left: Paddle, right: Paddle):
    # Top/Bottom wall
    if ball.rect.top <= 0:
        ball.rect.top = 0
        ball.vy *= -1
    elif ball.rect.bottom >= SCREEN_HEIGHT:
        ball.rect.bottom = SCREEN_HEIGHT
        ball.vy *= -1

    # Paddles
    if ball.rect.colliderect(left.rect) and ball.vx < 0:
        reflect_ball_from_paddle(ball, left)
    elif ball.rect.colliderect(right.rect) and ball.vx > 0:
        reflect_ball_from_paddle(ball, right)


def draw_score(surface: pygame.Surface, font: pygame.font.Font, left_score: int, right_score: int):
    left_surf = font.render(str(left_score), True, WHITE)
    right_surf = font.render(str(right_score), True, WHITE)

    surface.blit(left_surf, (SCREEN_WIDTH // 2 - 60 - left_surf.get_width(), 20))
    surface.blit(right_surf, (SCREEN_WIDTH // 2 + 60, 20))


def main():
    pygame.init()
    pygame.display.set_caption('Pong with AI')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Font
    try:
        font = pygame.font.Font(None, 64)
    except Exception:
        pygame.font.init()
        font = pygame.font.Font(None, 64)

    # Entities
    left_paddle = Paddle(24, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PLAYER_SPEED)
    right_paddle = Paddle(SCREEN_WIDTH - 24 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, AI_MAX_SPEED)
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SPEED)

    # Scores
    left_score = 0
    right_score = 0

    # Input state
    move_up = False
    move_down = False

    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    move_up = True
                elif event.key == pygame.K_s:
                    move_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    move_up = False
                elif event.key == pygame.K_s:
                    move_down = False

        # Update player paddle
        dy = 0
        if move_up:
            dy -= left_paddle.speed
        if move_down:
            dy += left_paddle.speed
        left_paddle.move(dy)

        # AI movement
        ai_follow_ball(right_paddle, ball)

        # Move ball
        ball.move()

        # Collisions
        handle_collisions(ball, left_paddle, right_paddle)

        # Scoring
        if ball.rect.left <= 0:
            right_score += 1
            ball.reset(direction=-1)  # next serve to left
        elif ball.rect.right >= SCREEN_WIDTH:
            left_score += 1
            ball.reset(direction=1)   # next serve to right

        # Draw
        screen.fill(BLACK)
        draw_center_line(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)
        draw_score(screen, font, left_score, right_score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
