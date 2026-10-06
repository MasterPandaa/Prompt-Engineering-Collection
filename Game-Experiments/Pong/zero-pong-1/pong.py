"""
Pong Game Implementation.

This module contains a Pong game built with Pygame. It separates
rendering, logic, and AI into distinct classes to follow the
Single Responsibility Principle.
"""

import sys
import random
import pygame

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
FPS = 60
MAX_SCORE = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Paddle:
    """Represents a paddle entity in the game."""

    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 7

    def move_up(self):
        """Moves the paddle up while keeping it on screen."""
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def move_down(self):
        """Moves the paddle down while keeping it on screen."""
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed


class Ball:
    """Represents the ball entity."""

    def __init__(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE
        )
        self.speed_x = 0
        self.speed_y = 0
        self.reset_position()

    def move(self):
        """Updates the ball's position based on its speed."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def reset_position(self):
        """Resets the ball to the center with a random direction."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])
        self.speed_x = 5 * direction_x
        self.speed_y = 5 * direction_y


class AIController:
    """Controls the AI paddle."""

    def __init__(self, paddle: Paddle):
        self.paddle = paddle

    def update(self, ball: Ball):
        """Updates the AI paddle position based on the ball."""
        # AI Logic: Move down if the ball is below the paddle's center
        if self.paddle.rect.centery < ball.rect.centery:
            self.paddle.move_down()
        # AI Logic: Move up if the ball is above the paddle's center
        elif self.paddle.rect.centery > ball.rect.centery:
            self.paddle.move_up()


class GameLogic:
    """Handles the game rules and state."""

    def __init__(self):
        self.player_paddle = Paddle(
            50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        )
        self.ai_paddle = Paddle(
            SCREEN_WIDTH - 50 - PADDLE_WIDTH,
            SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        )
        self.ball = Ball()
        self.ai_controller = AIController(self.ai_paddle)
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False

    def handle_collisions(self):
        """Handles collisions between the ball, screen edges, and paddles."""
        # Collision Logic: Reverse Y speed if hitting top or bottom edges
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= SCREEN_HEIGHT:
            self.ball.speed_y *= -1

        # Collision Logic: Check intersection with player or AI paddle
        player_collide = self.ball.rect.colliderect(self.player_paddle.rect)
        ai_collide = self.ball.rect.colliderect(self.ai_paddle.rect)
        
        # Collision Logic: Reverse X speed if colliding with either paddle
        if player_collide or ai_collide:
            self.ball.speed_x *= -1

    def update(self):
        """Updates the overall game state."""
        if self.game_over:
            return

        self.ball.move()
        self.ai_controller.update(self.ball)
        self.handle_collisions()

        # Check if ball goes out of bounds (left side)
        if self.ball.rect.left <= 0:
            self.ai_score += 1
            self.check_game_over()
            if not self.game_over:
                self.ball.reset_position()
        # Check if ball goes out of bounds (right side)
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.player_score += 1
            self.check_game_over()
            if not self.game_over:
                self.ball.reset_position()

    def check_game_over(self):
        """Checks if the game has reached the maximum score limit."""
        if self.player_score >= MAX_SCORE or self.ai_score >= MAX_SCORE:
            self.game_over = True


class Renderer:
    """Handles all drawing operations, strictly separated from logic."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        # Cache score surfaces to avoid creating objects in the main loop
        self.score_surfaces = {}
        for i in range(MAX_SCORE + 1):
            self.score_surfaces[i] = self.font.render(str(i), True, WHITE)
            
        self.game_over_text = None

    def _render_game_over(self, logic: GameLogic):
        """Renders the game over screen, cached after first call."""
        if not self.game_over_text:
            text = "Game Over"
            if logic.player_score >= MAX_SCORE:
                text = "Player Wins!"
            elif logic.ai_score >= MAX_SCORE:
                text = "AI Wins!"
            self.game_over_text = self.small_font.render(text, True, WHITE)

        text_rect = self.game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(self.game_over_text, text_rect)

    def draw(self, logic: GameLogic):
        """Draws the game entities and UI."""
        self.screen.fill(BLACK)

        pygame.draw.rect(self.screen, WHITE, logic.player_paddle.rect)
        pygame.draw.rect(self.screen, WHITE, logic.ai_paddle.rect)
        pygame.draw.ellipse(self.screen, WHITE, logic.ball.rect)
        pygame.draw.aaline(
            self.screen, WHITE,
            (SCREEN_WIDTH // 2, 0),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        )

        # Retrieve pre-rendered score text
        p_score_surf = self.score_surfaces.get(
            logic.player_score, self.score_surfaces[0]
        )
        a_score_surf = self.score_surfaces.get(
            logic.ai_score, self.score_surfaces[0]
        )
        
        self.screen.blit(p_score_surf, (SCREEN_WIDTH // 4, 10))
        self.screen.blit(a_score_surf, (SCREEN_WIDTH * 3 // 4, 10))

        if logic.game_over:
            self._render_game_over(logic)

        pygame.display.flip()


def main():
    """Main execution function for the game."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    logic = GameLogic()
    renderer = Renderer(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not logic.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                logic.player_paddle.move_up()
            if keys[pygame.K_DOWN]:
                logic.player_paddle.move_down()

        logic.update()
        renderer.draw(logic)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
