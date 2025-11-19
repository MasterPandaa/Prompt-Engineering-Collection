import sys
import random
import pygame

# Konfigurasi dasar
WIDTH, HEIGHT = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ukuran objek
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

# Kecepatan
PLAYER_SPEED = 7
AI_SPEED = 6
BALL_SPEED_MIN = 5
BALL_SPEED_MAX = 7

def clamp(val, vmin, vmax):
    return max(vmin, min(vmax, val))

def reset_ball(ball_rect, ball_vel):
    """Tempatkan bola di tengah dan beri arah acak ke kiri/kanan."""
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    speed = random.randint(BALL_SPEED_MIN, BALL_SPEED_MAX)
    angle = random.uniform(-0.8, 0.8)  # variasi sudut pantulan
    dir_x = random.choice([-1, 1])
    vx = dir_x * speed
    vy = speed * angle
    ball_vel[0] = vx
    ball_vel[1] = vy

def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font skor
    font = pygame.font.SysFont(None, 48)

    # Objek paddle dan bola
    player_rect = pygame.Rect(30, (HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai_rect = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_rect = pygame.Rect((WIDTH - BALL_SIZE) // 2, (HEIGHT - BALL_SIZE) // 2, BALL_SIZE, BALL_SIZE)

    # Kecepatan bola
    ball_vel = [0.0, 0.0]
    reset_ball(ball_rect, ball_vel)

    # Skor
    score_player = 0
    score_ai = 0

    # Input state
    move_up = False
    move_down = False

    running = True
    while running:
        _dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    move_up = True
                elif event.key == pygame.K_s:
                    move_down = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    move_up = False
                elif event.key == pygame.K_s:
                    move_down = False

        # Gerakkan paddle pemain
        if move_up and not move_down:
            player_rect.y -= PLAYER_SPEED
        elif move_down and not move_up:
            player_rect.y += PLAYER_SPEED
        player_rect.y = clamp(player_rect.y, 0, HEIGHT - PADDLE_HEIGHT)

        # AI mengikuti bola pada sumbu Y dengan batas kecepatan
        ai_center_y = ai_rect.centery
        if ball_rect.centery < ai_center_y - 5:
            ai_rect.y -= AI_SPEED
        elif ball_rect.centery > ai_center_y + 5:
            ai_rect.y += AI_SPEED
        ai_rect.y = clamp(ai_rect.y, 0, HEIGHT - PADDLE_HEIGHT)

        # Gerakkan bola
        ball_rect.x += int(ball_vel[0])
        ball_rect.y += int(ball_vel[1])

        # Pantulan atas/bawah
        if ball_rect.top <= 0:
            ball_rect.top = 0
            ball_vel[1] *= -1
        elif ball_rect.bottom >= HEIGHT:
            ball_rect.bottom = HEIGHT
            ball_vel[1] *= -1

        # Tabrakan dengan paddle pemain
        if ball_rect.colliderect(player_rect) and ball_vel[0] < 0:
            offset = (ball_rect.centery - player_rect.centery) / (PADDLE_HEIGHT / 2)
            offset = clamp(offset, -1, 1)
            speed = min(BALL_SPEED_MAX + 2, abs(ball_vel[0]) + 0.5)
            ball_vel[0] = abs(speed)
            ball_vel[1] = (BALL_SPEED_MIN + abs(speed) * 0.5) * offset
            ball_rect.left = player_rect.right + 1

        # Tabrakan dengan paddle AI
        if ball_rect.colliderect(ai_rect) and ball_vel[0] > 0:
            offset = (ball_rect.centery - ai_rect.centery) / (PADDLE_HEIGHT / 2)
            offset = clamp(offset, -1, 1)
            speed = min(BALL_SPEED_MAX + 2, abs(ball_vel[0]) + 0.5)
            ball_vel[0] = -abs(speed)
            ball_vel[1] = (BALL_SPEED_MIN + abs(speed) * 0.5) * offset
            ball_rect.right = ai_rect.left - 1

        # Skor
        if ball_rect.right < 0:
            score_ai += 1
            reset_ball(ball_rect, ball_vel)
        elif ball_rect.left > WIDTH:
            score_player += 1
            reset_ball(ball_rect, ball_vel)

        # Render
        screen.fill(BLACK)

        # Garis tengah putus-putus
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))

        pygame.draw.rect(screen, WHITE, player_rect)
        pygame.draw.rect(screen, WHITE, ai_rect)
        pygame.draw.ellipse(screen, WHITE, ball_rect)

        # Tampilkan skor di atas tengah
        score_text = font.render(f"{score_player}   {score_ai}", True, WHITE)
        text_rect = score_text.get_rect(center=(WIDTH // 2, 40))
        screen.blit(score_text, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
