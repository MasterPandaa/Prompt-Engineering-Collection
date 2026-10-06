import pygame
import sys
import random

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
PADDLE_SPEED = 7
AI_MAX_SPEED = 6  # Limit AI paddle movement speed to keep it fair

BALL_SIZE = 14
BALL_SPEED_X = 6
BALL_SPEED_Y = 4
BALL_SPEED_INCREMENT = 0.4  # Increases slightly after each paddle hit
MAX_BALL_SPEED = 12

SCORE_FONT_SIZE = 48
SCORE_TO_WIN = 11  # Not enforced to stop the game; informational

BG_COLOR = (20, 20, 20)
FG_COLOR = (235, 235, 235)
ACCENT_COLOR = (100, 200, 255)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self, dy):
        self.rect.y += dy
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - PADDLE_HEIGHT)

    def update(self):
        if self.speed != 0:
            self.move(self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, FG_COLOR, self.rect, border_radius=3)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
        )
        self.vel = pygame.Vector2(0, 0)
        self.serve(direction=random.choice([-1, 1]))

    def serve(self, direction=1):
        # Randomize initial Y velocity a bit
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        speed_x = BALL_SPEED_X * direction
        speed_y = random.choice([-1, 1]) * random.uniform(BALL_SPEED_Y * 0.5, BALL_SPEED_Y)
        self.vel.update(speed_x, speed_y)

    def update(self):
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        # Bounce on top/bottom walls
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel.y *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel.y *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, border_radius=3)


def ai_follow_ball(ai_paddle: Paddle, ball: Ball):
    # AI aims for the center of the ball with limited speed
    target_y = ball.rect.centery
    if abs(ai_paddle.rect.centery - target_y) <= AI_MAX_SPEED:
        delta = target_y - ai_paddle.rect.centery
    else:
        delta = AI_MAX_SPEED if target_y > ai_paddle.rect.centery else -AI_MAX_SPEED
    ai_paddle.move(delta)


def handle_player_input(player: Paddle):
    keys = pygame.key.get_pressed()
    move = 0
    if keys[pygame.K_w]:
        move -= PADDLE_SPEED
    if keys[pygame.K_s]:
        move += PADDLE_SPEED
    player.speed = move


def ball_paddle_collision(ball: Ball, paddle: Paddle, is_left_paddle: bool):
    if ball.rect.colliderect(paddle.rect):
        # Push ball outside the paddle to avoid sticking
        if is_left_paddle:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left

        # Reflect X velocity and slightly accelerate
        ball.vel.x *= -1
        if abs(ball.vel.x) < MAX_BALL_SPEED:
            if ball.vel.x > 0:
                ball.vel.x = min(MAX_BALL_SPEED, ball.vel.x + BALL_SPEED_INCREMENT)
            else:
                ball.vel.x = max(-MAX_BALL_SPEED, ball.vel.x - BALL_SPEED_INCREMENT)

        # Add spin based on where the ball hit the paddle
        offset = (ball.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        ball.vel.y += offset * 3.5  # tune for feel
        ball.vel.y = clamp(ball.vel.y, -MAX_BALL_SPEED, MAX_BALL_SPEED)


def draw_center_line(surface):
    dash_height = 14
    gap = 10
    x = WIDTH // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, (80, 80, 80), (x - 2, y, 4, dash_height), border_radius=2)
        y += dash_height + gap


def draw_score(surface, font, player_score, ai_score):
    score_text = f"{player_score}   :   {ai_score}"
    text_surf = font.render(score_text, True, FG_COLOR)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, 40))
    surface.blit(text_surf, text_rect)


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", SCORE_FONT_SIZE, bold=True)

    # Entities
    player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ai = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    player_score = 0
    ai_score = 0

    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Input
        handle_player_input(player)

        # Update
        player.update()
        ai_follow_ball(ai, ball)
        ball.update()

        # Collisions with paddles
        ball_paddle_collision(ball, player, is_left_paddle=True)
        ball_paddle_collision(ball, ai, is_left_paddle=False)

        # Scoring
        if ball.rect.right < 0:
            ai_score += 1
            ball.serve(direction=1)
        elif ball.rect.left > WIDTH:
            player_score += 1
            ball.serve(direction=-1)

        # Draw
        screen.fill(BG_COLOR)
        draw_center_line(screen)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)
        draw_score(screen, font, player_score, ai_score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
