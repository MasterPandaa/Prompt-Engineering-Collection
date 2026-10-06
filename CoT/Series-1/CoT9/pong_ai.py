import random
import pygame


# -----------------------------
# Konstanta dasar
# -----------------------------
WIDTH, HEIGHT = 900, 540
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 14, 100
BALL_SIZE = 14

MARGIN = 24
PADDLE_SPEED = 7
AI_SPEED = 6  # Sedikit lebih lambat dari pemain untuk memberi peluang
BALL_BASE_SPEED = 6
BALL_MAX_VY = 7  # Batas kecepatan vertikal agar tidak terlalu ekstrem


def serve_ball(direction: int) -> pygame.Vector2:
    """
    direction: +1 ke kanan (ke pemain AI), -1 ke kiri (ke pemain)
    Menghasilkan kecepatan awal bola dengan sudut acak moderat.
    """
    angle_choices = [-25, -15, -10, 10, 15, 25]
    angle_deg = random.choice(angle_choices)

    vx = BALL_BASE_SPEED * direction
    # Gunakan rotasi vektor untuk variasi vy lalu clamp
    vy = BALL_BASE_SPEED * pygame.math.Vector2(1, 0).rotate(angle_deg).y
    vy = max(-BALL_MAX_VY, min(BALL_MAX_VY, vy))
    # Pastikan vy tidak nol agar tidak terlalu datar
    if abs(vy) < 2:
        vy = 2 if vy >= 0 else -2
    return pygame.Vector2(vx, vy)


def reset_ball(ball: pygame.Rect, direction: int) -> pygame.Vector2:
    ball.center = (WIDTH // 2, HEIGHT // 2)
    return serve_ball(direction)


def handle_player_input(player: pygame.Rect):
    keys = pygame.key.get_pressed()
    dy = 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= PADDLE_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += PADDLE_SPEED
    player.y += dy
    # Clamp di layar
    if player.top < 0:
        player.top = 0
    if player.bottom > HEIGHT:
        player.bottom = HEIGHT


def handle_ai(ai: pygame.Rect, ball: pygame.Rect):
    # AI sederhana: kejar posisi Y bola
    if ai.centery < ball.centery - 4:  # deadzone kecil
        ai.y += AI_SPEED
    elif ai.centery > ball.centery + 4:
        ai.y -= AI_SPEED
    # Clamp di layar
    if ai.top < 0:
        ai.top = 0
    if ai.bottom > HEIGHT:
        ai.bottom = HEIGHT


def reflect_ball_from_paddle(ball: pygame.Rect, paddle: pygame.Rect, vel: pygame.Vector2, is_left_paddle: bool) -> pygame.Vector2:
    """
    Pantulkan bola ketika menabrak paddle.
    Modifikasi vy berdasarkan offset tumbukan relatif terhadap pusat paddle.
    """
    # Tentukan arah x setelah pantulan
    speed_x = abs(vel.x)
    vel.x = speed_x if not is_left_paddle else -speed_x

    # Variasi sudut berdasarkan titik tumbukan
    offset = (ball.centery - paddle.centery) / (PADDLE_HEIGHT / 2)  # -1..1
    vel.y = offset * BALL_MAX_VY
    # Pastikan tidak nol total agar tidak bergerak datar lama
    if abs(vel.y) < 2:
        vel.y = 2 if vel.y >= 0 else -2

    # Jauhkan bola sedikit dari paddle untuk mencegah double-collision
    if is_left_paddle:
        ball.left = paddle.right
    else:
        ball.right = paddle.left

    return vel


def update_ball(ball: pygame.Rect, vel: pygame.Vector2, player: pygame.Rect, ai: pygame.Rect) -> pygame.Vector2:
    # Pergerakan
    ball.x += int(vel.x)
    ball.y += int(vel.y)

    # Pantulan atas/bawah
    if ball.top <= 0:
        ball.top = 0
        vel.y *= -1
    elif ball.bottom >= HEIGHT:
        ball.bottom = HEIGHT
        vel.y *= -1

    # Pantulan dengan paddle
    if ball.colliderect(player) and vel.x < 0:
        vel = reflect_ball_from_paddle(ball, player, vel, is_left_paddle=True)
    elif ball.colliderect(ai) and vel.x > 0:
        vel = reflect_ball_from_paddle(ball, ai, vel, is_left_paddle=False)

    return vel


def draw_center_line(surface: pygame.Surface):
    dash_height = 16
    gap = 12
    x = WIDTH // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, WHITE, (x - 2, y, 4, dash_height))
        y += dash_height + gap


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 64)
    small_font = pygame.font.Font(None, 28)

    # Objek
    player = pygame.Rect(MARGIN, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - MARGIN - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

    # Skor
    score_player = 0
    score_ai = 0

    # Kecepatan awal bola (acak arah servis)
    direction = random.choice([-1, 1])
    ball_vel = reset_ball(ball, direction)

    running = True
    while running:
        # 1) Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Update logika
        handle_player_input(player)
        handle_ai(ai, ball)
        ball_vel = update_ball(ball, ball_vel, player, ai)

        # 3) Skor (bola keluar batas kiri/kanan)
        if ball.right < 0:
            score_ai += 1
            ball_vel = reset_ball(ball, direction=+1)  # servis ke kanan (ke arah pemain)
        elif ball.left > WIDTH:
            score_player += 1
            ball_vel = reset_ball(ball, direction=-1)  # servis ke kiri (ke arah AI)

        # 4) Render
        screen.fill(BLACK)
        draw_center_line(screen)
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Tampilkan skor
        score_text = font.render(f"{score_player}   :   {score_ai}", True, WHITE)
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 40)))

        # Bantuan kontrol
        help_text = small_font.render("Controls: W/S atau Panah Up/Down | ESC tutup window", True, (200, 200, 200))
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 36))

        pygame.display.flip()
        clock.tick(FPS)

        # Keluar dengan ESC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
