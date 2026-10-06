"""
Pong game using Pygame.

Features:
- GUI window
- Scoring system
- AI opponent
"""

import sys
import random
import pygame


# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_RADIUS = 10

PADDLE_SPEED = 7
BALL_SPEED = 5
MAX_SCORE = 10


class Paddle:
    """Represents a player or AI paddle."""

    def __init__(self, x, y):
        """Initialize the paddle."""
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move_up(self):
        """Move the paddle up."""
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.rect.y = 0

    def move_down(self):
        """Move the paddle down."""
        self.rect.y += self.speed
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        """Render the paddle on the given surface."""
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    """Represents the ping-pong ball."""

    def __init__(self, x, y):
        """Initialize the ball at the center."""
        self.rect = pygame.Rect(
            x - BALL_RADIUS, y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2
        )
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))

    def move(self):
        """Move the ball."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Handle top and bottom wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def reset(self, x, y):
        """Reset ball to the center after a score."""
        self.rect.center = (x, y)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))

    def draw(self, surface):
        """Render the ball on the given surface."""
        pygame.draw.ellipse(surface, WHITE, self.rect)


class AIController:
    """Controls the opponent's paddle."""

    def __init__(self, paddle):
        """Initialize AI with a specific paddle."""
        self.paddle = paddle

    def track_ball(self, ball):
        """Move the paddle to track the ball's y position."""
        # AI logic: align paddle center with ball center
        if self.paddle.rect.centery < ball.rect.centery:
            self.paddle.move_down()
        elif self.paddle.rect.centery > ball.rect.centery:
            self.paddle.move_up()


class GameLogic:
    """Handles collision detection and game rules."""

    def __init__(self):
        """Initialize scores."""
        self.player_score = 0
        self.ai_score = 0

    def handle_collisions(self, ball, player, ai):
        """Detect and handle ball-paddle collisions."""
        # Collision detection: if ball hits player paddle from the front
        if ball.rect.colliderect(player.rect) and ball.speed_x < 0:
            ball.speed_x *= -1
            ball.speed_x += 1 if ball.speed_x > 0 else -1  # Increase speed

        # Collision detection: if ball hits AI paddle from the front
        if ball.rect.colliderect(ai.rect) and ball.speed_x > 0:
            ball.speed_x *= -1
            ball.speed_x += 1 if ball.speed_x > 0 else -1

    def check_score(self, ball):
        """Check if a point was scored."""
        if ball.rect.left <= 0:
            self.ai_score += 1
            ball.reset(WIDTH // 2, HEIGHT // 2)
        elif ball.rect.right >= WIDTH:
            self.player_score += 1
            ball.reset(WIDTH // 2, HEIGHT // 2)

    def is_game_over(self):
        """Check if max score is reached."""
        return self.player_score >= MAX_SCORE or self.ai_score >= MAX_SCORE


class PongGame:
    """Main game application class."""

    def __init__(self):
        """Initialize game components."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)

        self.player = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ai_paddle = Paddle(
            WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2
        )
        self.ball = Ball(WIDTH // 2, HEIGHT // 2)

        self.ai_controller = AIController(self.ai_paddle)
        self.logic = GameLogic()

    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move_up()
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move_down()

        return True

    def update(self):
        """Update game state."""
        if not self.logic.is_game_over():
            self.ball.move()
            self.ai_controller.track_ball(self.ball)
            self.logic.handle_collisions(
                self.ball, self.player, self.ai_paddle
            )
            self.logic.check_score(self.ball)

    def render(self):
        """Draw everything on the screen."""
        self.screen.fill(BLACK)
        pygame.draw.line(
            self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT)
        )

        self.player.draw(self.screen)
        self.ai_paddle.draw(self.screen)
        self.ball.draw(self.screen)

        # Draw scores
        player_text = self.font.render(
            str(self.logic.player_score), True, WHITE
        )
        self.screen.blit(player_text, (WIDTH // 4, 20))

        ai_text = self.font.render(str(self.logic.ai_score), True, WHITE)
        self.screen.blit(ai_text, (WIDTH * 3 // 4, 20))

        if self.logic.is_game_over():
            msg = (
                "Player Wins!"
                if self.logic.player_score >= MAX_SCORE
                else "AI Wins!"
            )
            win_text = self.font.render(msg, True, WHITE)
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(win_text, text_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PongGame()
    game.run()
