import pygame
import sys
import random

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
PADDLE_SPEED = 7
AI_MAX_SPEED = 6  # cap AI vertical speed so it's beatable

# Ball settings
BALL_SIZE = 12
BALL_SPEED = 6
BALL_SPEED_INCREMENT = 0.3  # small speed up on each paddle hit
MAX_BALL_VY = 7.5


def reset_ball(ball_rect, direction=None):
    """Reset the ball to the center with a random direction.
    direction: None=random, 'left' or 'right' to bias initial horizontal direction.
    """
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)

    # Randomize vertical speed with slight bias
    vy = random.uniform(-3.5, 3.5)
    if abs(vy) < 1.0:
        vy = 1.0 * (1 if vy >= 0 else -1)

    # Horizontal velocity based on direction
    if direction == 'left':
        vx = -BALL_SPEED
    elif direction == 'right':
        vx = BALL_SPEED
    else:
        vx = BALL_SPEED * (1 if random.random() < 0.5 else -1)

    return [vx, vy]


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    font = pygame.font.SysFont("consolas", 36)
    small_font = pygame.font.SysFont("consolas", 20)

    # Game objects
    player = pygame.Rect(30, (HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

    ball_vel = reset_ball(ball)

    player_score = 0
    ai_score = 0

    show_instructions_timer = 180  # ~3 seconds at 60 FPS

    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Player movement (W/S)
        if keys[pygame.K_w]:
            player.y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            player.y += PADDLE_SPEED

        # Keep paddles on screen
        player.y = clamp(player.y, 0, HEIGHT - PADDLE_HEIGHT)

        # AI movement: track ball's Y with capped speed
        # Target is to align paddle center with ball center
        ai_target_y = ball.centery - ai.height // 2
        if ai.y < ai_target_y:
            ai.y += AI_MAX_SPEED
        elif ai.y > ai_target_y:
            ai.y -= AI_MAX_SPEED
        ai.y = clamp(ai.y, 0, HEIGHT - PADDLE_HEIGHT)

        # Move ball
        ball.x += ball_vel[0]
        ball.y += ball_vel[1]

        # Ball collision with top/bottom walls
        if ball.top <= 0:
            ball.top = 0
            ball_vel[1] *= -1
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vel[1] *= -1

        # Ball collision with paddles
        if ball.colliderect(player) and ball_vel[0] < 0:
            # Reflect and add spin based on impact position
            offset = (ball.centery - player.centery) / (PADDLE_HEIGHT / 2)
            ball_vel[0] = -ball_vel[0] + (BALL_SPEED_INCREMENT)  # ensure it doesn't slow down
            ball_vel[1] += offset * 2.5
            # Cap vertical speed
            ball_vel[1] = clamp(ball_vel[1], -MAX_BALL_VY, MAX_BALL_VY)
        elif ball.colliderect(ai) and ball_vel[0] > 0:
            offset = (ball.centery - ai.centery) / (PADDLE_HEIGHT / 2)
            ball_vel[0] = -ball_vel[0] - (BALL_SPEED_INCREMENT)
            ball_vel[1] += offset * 2.5
            ball_vel[1] = clamp(ball_vel[1], -MAX_BALL_VY, MAX_BALL_VY)

        # Scoring
        if ball.right < 0:
            # AI scores
            ai_score += 1
            ball_vel = reset_ball(ball, direction='right')
        elif ball.left > WIDTH:
            # Player scores
            player_score += 1
            ball_vel = reset_ball(ball, direction='left')

        # Draw
        screen.fill(BLACK)

        # Middle dashed line
        dash_height = 20
        dash_gap = 15
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(screen, GREY, (WIDTH // 2 - 2, y, 4, dash_height))
            y += dash_height + dash_gap

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Scores
        score_text = font.render(f"{player_score}", True, WHITE)
        score_text_ai = font.render(f"{ai_score}", True, WHITE)
        screen.blit(score_text, (WIDTH * 0.25 - score_text.get_width() // 2, 20))
        screen.blit(score_text_ai, (WIDTH * 0.75 - score_text_ai.get_width() // 2, 20))

        # Instructions (briefly on start)
        if show_instructions_timer > 0:
            show_instructions_timer -= 1
            info1 = small_font.render("Gerakkan paddle kiri: W/S", True, GREY)
            info2 = small_font.render("Paddle kanan (AI) mengikuti bola", True, GREY)
            screen.blit(info1, (WIDTH // 2 - info1.get_width() // 2, HEIGHT - 70))
            screen.blit(info2, (WIDTH // 2 - info2.get_width() // 2, HEIGHT - 45))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
