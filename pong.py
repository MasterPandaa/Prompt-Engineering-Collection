import pygame
import random
import sys

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 7
AI_MAX_SPEED = 6  # limit AI vertical speed so it feels fair
AI_REACTION_SLOWDOWN = 0.15  # smaller = snappier, larger = lazier

# Ball settings
BALL_SIZE = 12
BALL_SPEED = 6
BALL_SPEED_INCREMENT = 0.5  # increase speed slightly on each paddle hit
BALL_MAX_SPEED = 12


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def reset_ball(ball_rect, direction=None):
    """Reset ball to center with random direction (or specified horizontal direction)."""
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    angle_choices = [
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    dir_x, dir_y = random.choice(angle_choices)
    if direction in (-1, 1):
        dir_x = direction
    # normalize to BALL_SPEED
    vx = dir_x * BALL_SPEED
    vy = dir_y * BALL_SPEED * random.uniform(0.5, 1.0)
    return vx, vy


def draw_center_line(surface):
    dash_height = 20
    gap = 20
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, WHITE, (WIDTH // 2 - 2, y, 4, dash_height))
        y += dash_height + gap


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font
    font = pygame.font.SysFont(None, 48)

    # Paddles
    player = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

    # Ball
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_vx, ball_vy = reset_ball(ball)

    # Scores
    player_score = 0
    ai_score = 0

    running = True
    while running:
        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # Player movement (W/S)
        if keys[pygame.K_w]:
            player.y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            player.y += PADDLE_SPEED
        player.y = clamp(player.y, 0, HEIGHT - PADDLE_HEIGHT)

        # AI movement: follow ball's Y with speed limit and a bit of smoothing
        target_y = ball.centery - ai.height // 2
        dy = target_y - ai.y
        ai.y += int(clamp(dy * AI_REACTION_SLOWDOWN, -AI_MAX_SPEED, AI_MAX_SPEED))
        ai.y = clamp(ai.y, 0, HEIGHT - PADDLE_HEIGHT)

        # Move ball
        ball.x += int(ball_vx)
        ball.y += int(ball_vy)

        # Wall collision (top/bottom)
        if ball.top <= 0:
            ball.top = 0
            ball_vy = -ball_vy
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vy = -ball_vy

        # Paddle collisions
        if ball.colliderect(player) and ball_vx < 0:
            # Compute hit position to add a bit of angle variation
            offset = (ball.centery - player.centery) / (PADDLE_HEIGHT / 2)
            ball_vx = -ball_vx
            ball_vx = clamp(ball_vx + (BALL_SPEED_INCREMENT if ball_vx > 0 else -BALL_SPEED_INCREMENT), -BALL_MAX_SPEED, BALL_MAX_SPEED)
            ball_vy += offset * 2.0
            ball.left = player.right  # avoid sticking
        elif ball.colliderect(ai) and ball_vx > 0:
            offset = (ball.centery - ai.centery) / (PADDLE_HEIGHT / 2)
            ball_vx = -ball_vx
            ball_vx = clamp(ball_vx + (BALL_SPEED_INCREMENT if ball_vx > 0 else -BALL_SPEED_INCREMENT), -BALL_MAX_SPEED, BALL_MAX_SPEED)
            ball_vy += offset * 2.0
            ball.right = ai.left

        # Scoring
        if ball.right < 0:
            # AI scores
            ai_score += 1
            ball_vx, ball_vy = reset_ball(ball, direction=1)
        elif ball.left > WIDTH:
            # Player scores
            player_score += 1
            ball_vx, ball_vy = reset_ball(ball, direction=-1)

        # Render
        screen.fill(BLACK)
        draw_center_line(screen)

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Draw scores
        score_text = f"{player_score}    {ai_score}"
        text_surface = font.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 40))
        screen.blit(text_surface, text_rect)

        # Instructions (small)
        small_font = pygame.font.SysFont(None, 24)
        help_text = small_font.render("Player: W/S | ESC to quit", True, WHITE)
        screen.blit(help_text, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
