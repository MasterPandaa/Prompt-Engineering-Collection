import sys
import random
import pygame

# --- Config ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
PLAYER_X = 30
AI_X = SCREEN_WIDTH - 30 - PADDLE_WIDTH

BALL_SIZE = 14
BALL_START_SPEED = 320.0
BALL_SPEED_INCREMENT = 20.0
BALL_MAX_SPEED = 700.0

PLAYER_SPEED = 420.0
AI_MAX_SPEED = 380.0
AI_REACTION_SMOOTHING = 0.18  # 0..1, bigger is snappier

WIN_SCORE = 10


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.vel_y = 0.0

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)

    def move(self, dy, dt):
        self.vel_y = dy * self.speed
        self.rect.y += int(self.vel_y * dt)
        self.clamp_to_bounds()

    def clamp_to_bounds(self):
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def ai_follow(self, target_y, dt):
        # target is the center Y of the ball
        center = self.rect.centery
        error = target_y - center
        desired_vel = max(-AI_MAX_SPEED, min(AI_MAX_SPEED, error))
        # smooth toward desired velocity
        self.vel_y = (1 - AI_REACTION_SMOOTHING) * self.vel_y + AI_REACTION_SMOOTHING * desired_vel
        self.rect.y += int(self.vel_y * dt)
        self.clamp_to_bounds()


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.vel = pygame.Vector2(0, 0)
        self.speed = BALL_START_SPEED
        self.reset(direction=random.choice((-1, 1)))

    def reset(self, direction=1):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        angle = random.uniform(-0.35, 0.35)  # shallow random angle
        self.speed = BALL_START_SPEED
        self.vel.x = direction * self.speed
        self.vel.y = self.speed * angle

    def update(self, dt, paddles):
        # Move with continuous velocity
        move_x = self.vel.x * dt
        move_y = self.vel.y * dt
        self.rect.x += int(move_x)
        self.rect.y += int(move_y)

        # Top/bottom wall collision
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel.y *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel.y *= -1

        # Paddle collisions (AABB simple)
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                # Determine side and correct position
                if self.vel.x < 0:  # moving left, collided with left paddle
                    self.rect.left = paddle.rect.right
                else:  # moving right, collided with right paddle
                    self.rect.right = paddle.rect.left

                # Reflect X and add a bit of spin based on where we hit the paddle
                offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
                offset = max(-1.0, min(1.0, offset))

                self.vel.x *= -1
                self.speed = min(BALL_MAX_SPEED, self.speed + BALL_SPEED_INCREMENT)
                self.vel.scale_to_length(self.speed)

                # Add vertical angle component
                self.vel.y += offset * 140
                # Avoid perfectly horizontal trajectory
                if abs(self.vel.y) < 60:
                    self.vel.y = 60 if self.vel.y >= 0 else -60

                break  # handle one paddle per frame

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)


def draw_center_line(surface):
    dash_h = 16
    gap = 12
    y = 0
    x = SCREEN_WIDTH // 2 - 2
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(surface, GREY, (x, y, 4, dash_h), border_radius=2)
        y += dash_h + gap


def render_text(surface, text, pos, font):
    img = font.render(text, True, WHITE)
    surface.blit(img, pos)


def main():
    pygame.init()

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print("Pygame failed to open a window:", e)
        pygame.quit()
        sys.exit(1)

    pygame.display.set_caption("Pong - Player vs AI")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Consolas", 36)
    small_font = pygame.font.SysFont("Consolas", 20)

    # Create objects
    player = Paddle(PLAYER_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PLAYER_SPEED)
    ai = Paddle(AI_X, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, AI_MAX_SPEED)
    ball = Ball()

    player_score = 0
    ai_score = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input handling
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        player.move(dy, dt)

        # AI follows the ball's center Y
        ai.ai_follow(ball.rect.centery, dt)

        # Update ball
        ball.update(dt, (player, ai))

        # Scoring: ball out of bounds left/right
        scored = None
        if ball.rect.right < 0:
            ai_score += 1
            scored = -1
        elif ball.rect.left > SCREEN_WIDTH:
            player_score += 1
            scored = 1

        if scored is not None:
            # Reset ball towards the one who conceded the goal
            ball.reset(direction=-scored)
            # Give paddles a minor recentre tendency after score
            player.rect.centery = SCREEN_HEIGHT // 2
            ai.rect.centery = SCREEN_HEIGHT // 2

        # Win condition
        if player_score >= WIN_SCORE or ai_score >= WIN_SCORE:
            # Simple win banner for a short moment
            screen.fill(BLACK)
            msg = "You Win!" if player_score > ai_score else "AI Wins!"
            render_text(screen, msg, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20), font)
            pygame.display.flip()
            pygame.time.delay(1800)
            player_score, ai_score = 0, 0
            ball.reset(direction=random.choice((-1, 1)))

        # Draw
        screen.fill(BLACK)
        draw_center_line(screen)

        # Scores
        render_text(screen, str(player_score), (SCREEN_WIDTH // 2 - 60, 20), font)
        render_text(screen, str(ai_score), (SCREEN_WIDTH // 2 + 40, 20), font)

        # Hints
        render_text(screen, "W/S to move", (16, SCREEN_HEIGHT - 30), small_font)

        # Objects
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        # Helpful message if pygame isn't installed
        print("Error:", e)
        print("Tip: install pygame with: pip install pygame")
        sys.exit(1)
