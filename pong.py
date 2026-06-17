"""
Pong Game implementation using Pygame.

This module provides a complete, playable Pong game with an AI opponent.
It strictly adheres to PEP 8 standards and separates concerns into
logic, rendering, and AI control.
"""

import sys
import random
import pygame

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
WINNING_SCORE = 10


class Paddle:
    """Represents a player or AI paddle in the game."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize the paddle with position and dimensions."""
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0

    def move_up(self) -> None:
        """Move the paddle up, ensuring it stays within the screen."""
        self.rect.y -= PADDLE_SPEED
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self) -> None:
        """Move the paddle down, ensuring it stays within the screen."""
        self.rect.y += PADDLE_SPEED
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Ball:
    """Represents the ball in the game."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize the ball with position and default velocity."""
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.velocity_x = BALL_SPEED_X * random.choice((1, -1))
        self.velocity_y = BALL_SPEED_Y * random.choice((1, -1))

    def move(self) -> None:
        """Update the ball's position based on its velocity."""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def reset_position(self) -> None:
        """Reset the ball to the center and reverse its X direction."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.velocity_x *= -1
        # Randomize Y direction slightly to prevent repetitive patterns
        self.velocity_y = BALL_SPEED_Y * random.choice((1, -1))


class GameLogic:
    """Handles core game mechanics, collision detection, and scoring."""

    def __init__(
        self, player: Paddle, ai_paddle: Paddle, ball: Ball
    ) -> None:
        """Initialize game logic with necessary entities."""
        self.player = player
        self.ai_paddle = ai_paddle
        self.ball = ball
        self.game_over = False

    def update(self) -> None:
        """Update the game state, including ball movement and collisions."""
        if self.game_over:
            return

        self.ball.move()

        # Wall collision detection (top and bottom)
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= SCREEN_HEIGHT:
            self.ball.velocity_y *= -1

        # Paddle collision detection
        if self.ball.rect.colliderect(self.player.rect):
            self.ball.velocity_x *= -1
            # Prevent the ball from getting stuck inside the paddle
            self.ball.rect.left = self.player.rect.right

        if self.ball.rect.colliderect(self.ai_paddle.rect):
            self.ball.velocity_x *= -1
            # Prevent the ball from getting stuck inside the paddle
            self.ball.rect.right = self.ai_paddle.rect.left

        # Scoring detection
        if self.ball.rect.left <= 0:
            self.ai_paddle.score += 1
            self.check_win_condition()
            self.ball.reset_position()
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.player.score += 1
            self.check_win_condition()
            self.ball.reset_position()

    def check_win_condition(self) -> None:
        """Check if either player has reached the winning score."""
        if (self.player.score >= WINNING_SCORE or
                self.ai_paddle.score >= WINNING_SCORE):
            self.game_over = True


class AIController:
    """Controls the AI paddle based on the ball's position."""

    def __init__(self, ai_paddle: Paddle, ball: Ball) -> None:
        """Initialize AI controller with the paddle and ball references."""
        self.paddle = ai_paddle
        self.ball = ball

    def update(self) -> None:
        """Move the AI paddle to follow the ball's vertical position."""
        # AI Logic: The paddle tries to align its center with the ball
        if self.paddle.rect.centery < self.ball.rect.centery:
            self.paddle.move_down()
        elif self.paddle.rect.centery > self.ball.rect.centery:
            self.paddle.move_up()


class Renderer:
    """Handles all drawing and rendering operations."""

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Initialize the renderer with the target screen and font."""
        self.screen = screen
        self.font = font

    def render(
        self,
        player: Paddle,
        ai_paddle: Paddle,
        ball: Ball,
        game_logic: GameLogic
    ) -> None:
        """Draw all game elements to the screen."""
        self.screen.fill(BLACK)

        pygame.draw.rect(self.screen, WHITE, player.rect)
        pygame.draw.rect(self.screen, WHITE, ai_paddle.rect)
        pygame.draw.ellipse(self.screen, WHITE, ball.rect)

        # Draw center line
        pygame.draw.aaline(
            self.screen,
            WHITE,
            (SCREEN_WIDTH // 2, 0),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        )

        # Draw scores
        player_score_text = self.font.render(
            str(player.score), True, WHITE
        )
        ai_score_text = self.font.render(
            str(ai_paddle.score), True, WHITE
        )

        self.screen.blit(player_score_text, (SCREEN_WIDTH // 4, 20))
        self.screen.blit(ai_score_text, (SCREEN_WIDTH * 3 // 4, 20))

        if game_logic.game_over:
            self._render_game_over(player.score, ai_paddle.score)

        pygame.display.flip()

    def _render_game_over(self, p_score: int, ai_score: int) -> None:
        """Render the game over text."""
        msg = "Player Wins!" if p_score >= WINNING_SCORE else "AI Wins!"
        text = self.font.render(msg, True, WHITE)
        text_rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(text, text_rect)


def main() -> None:
    """Main game loop and entry point."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()
    
    try:
        font = pygame.font.Font(None, 74)
    except Exception:
        pygame.quit()
        sys.exit()

    # Pre-allocate game objects outside the loop
    player = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ai_paddle = Paddle(
        SCREEN_WIDTH - 30 - PADDLE_WIDTH,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    )
    ball = Ball(
        SCREEN_WIDTH // 2 - BALL_SIZE // 2,
        SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    )

    game_logic = GameLogic(player, ai_paddle, ball)
    ai_controller = AIController(ai_paddle, ball)
    renderer = Renderer(screen, font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_logic.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player.move_up()
            if keys[pygame.K_DOWN]:
                player.move_down()

            ai_controller.update()
            game_logic.update()

        renderer.render(player, ai_paddle, ball, game_logic)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
