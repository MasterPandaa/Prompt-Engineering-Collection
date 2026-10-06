import pygame
import random

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Paddle and ball settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_MARGIN = 30
PLAYER_SPEED = 7
AI_SPEED = 6
BALL_SIZE = 12
BALL_SPEED = 6
MAX_BALL_DY = 6


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def reset_ball(ball_rect, ball_vel, direction=None):
    """
    Reset the ball to the center with a fresh velocity.
    direction: None (random), 1 (to the right), -1 (to the left)
    """
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    dir_x = random.choice([-1, 1]) if direction is None else (1 if direction > 0 else -1)
    # choose a non-zero y direction and clamp
    dir_y = random.uniform(-1, 1)
    while abs(dir_y) < 0.2:
        dir_y = random.uniform(-1, 1)
    # normalize to BALL_SPEED preserving direction
    # Scale components so that |vx| + |vy| roughly equals BALL_SPEED*something consistent
    # Simpler: set vx from dir_x and vy from dir_y scaled
    vx = dir_x * BALL_SPEED
    vy = clamp(int(dir_y * BALL_SPEED), -MAX_BALL_DY, MAX_BALL_DY)
    if vy == 0:
        vy = random.choice([-2, 2])
    ball_vel[0] = vx
    ball_vel[1] = vy


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font for score
    font = pygame.font.SysFont(None, 48)

    # Game objects
    player = pygame.Rect(PADDLE_MARGIN, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_vel = [0, 0]
    reset_ball(ball, ball_vel, direction=random.choice([-1, 1]))

    player_score = 0
    ai_score = 0

    running = True
    while running:
        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player_move = 0
        if keys[pygame.K_w]:
            player_move -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player_move += PLAYER_SPEED

        # Update player paddle
        player.y += player_move
        player.y = clamp(player.y, 0, HEIGHT - PADDLE_HEIGHT)

        # Simple AI: follow the ball's y position with limited speed
        if ball.centery < ai.centery - 5:
            ai.y -= AI_SPEED
        elif ball.centery > ai.centery + 5:
            ai.y += AI_SPEED
        ai.y = clamp(ai.y, 0, HEIGHT - PADDLE_HEIGHT)

        # Move ball
        ball.x += ball_vel[0]
        ball.y += ball_vel[1]

        # Wall collision (top/bottom)
        if ball.top <= 0:
            ball.top = 0
            ball_vel[1] *= -1
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vel[1] *= -1

        # Paddle collisions
        if ball.colliderect(player) and ball_vel[0] < 0:
            # Nudge outside and reflect
            ball.left = player.right
            ball_vel[0] *= -1
            # add some spin depending on where it hits the paddle
            offset = (ball.centery - player.centery) / (PADDLE_HEIGHT / 2)
            ball_vel[1] += int(offset * 4)
            ball_vel[1] = clamp(ball_vel[1], -MAX_BALL_DY, MAX_BALL_DY)
        elif ball.colliderect(ai) and ball_vel[0] > 0:
            ball.right = ai.left
            ball_vel[0] *= -1
            offset = (ball.centery - ai.centery) / (PADDLE_HEIGHT / 2)
            ball_vel[1] += int(offset * 4)
            ball_vel[1] = clamp(ball_vel[1], -MAX_BALL_DY, MAX_BALL_DY)

        # Scoring
        if ball.right < 0:
            # AI scores
            ai_score += 1
            reset_ball(ball, ball_vel, direction=1)  # serve to the right (towards AI)
        elif ball.left > WIDTH:
            # Player scores
            player_score += 1
            reset_ball(ball, ball_vel, direction=-1)  # serve to the left (towards Player)

        # Drawing
        screen.fill(BLACK)

        # Middle dashed line
        dash_height = 20
        dash_gap = 15
        for y in range(0, HEIGHT, dash_height + dash_gap):
            pygame.draw.rect(screen, GREY, (WIDTH // 2 - 2, y, 4, dash_height))

        # Paddles and ball
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Scores
        score_text = f"{player_score}   :   {ai_score}"
        text_surf = font.render(score_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(text_surf, text_rect)

        # Controls hint (small)
        hint_font = pygame.font.SysFont(None, 24)
        hint = hint_font.render("Controls: W = Up, S = Down | Esc to Quit", True, GREY)
        screen.blit(hint, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

        # Quit on Esc
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
