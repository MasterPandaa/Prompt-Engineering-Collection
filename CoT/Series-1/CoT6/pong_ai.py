
import pygame
import random

# ---------- Konfigurasi Dasar ----------
WIDTH, HEIGHT = 900, 540
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

PLAYER_X = 40
AI_X = WIDTH - 40 - PADDLE_WIDTH

PLAYER_SPEED = 7
AI_SPEED = 6  # Turunkan untuk memudahkan pemain, naikkan untuk lebih sulit
BALL_SPEED_X_INIT = 7
BALL_SPEED_Y_MAX = 6  # Batas kecepatan vertikal bola

LINE_COLOR = (200, 200, 200)

def reset_ball(ball, direction=1):
    """
    Reset bola ke tengah. direction = 1 berarti ke kanan (menuju AI),
    direction = -1 berarti ke kiri (menuju pemain).
    """
    ball.center = (WIDTH // 2, HEIGHT // 2)
    # Kecepatan horizontal tetap konstan tapi dengan arah sesuai skor
    vel_x = BALL_SPEED_X_INIT * direction
    # Beri variasi vertikal acak, dibatasi maksimum
    vel_y = random.randint(-BALL_SPEED_Y_MAX, BALL_SPEED_Y_MAX)
    # Pastikan vel_y tidak nol agar permainan dinamis
    if vel_y == 0:
        vel_y = random.choice([-3, 3])
    return vel_x, vel_y

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 56)

    # ---------- Objek Permainan ----------
    player = pygame.Rect(PLAYER_X, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(AI_X, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

    ball_vel_x, ball_vel_y = reset_ball(ball, direction=random.choice([-1, 1]))

    score_player = 0
    score_ai = 0

    running = True
    while running:
        # ---------- Event ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ---------- Input Pemain ----------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player.y += PLAYER_SPEED

        # Batasi paddle pemain dalam layar
        if player.top < 0:
            player.top = 0
        if player.bottom > HEIGHT:
            player.bottom = HEIGHT

        # ---------- AI Sederhana ----------
        # AI melacak posisi Y bola dengan kecepatan terbatas
        if ai.centery < ball.centery:
            ai.y += AI_SPEED
        elif ai.centery > ball.centery:
            ai.y -= AI_SPEED

        # Batasi paddle AI dalam layar
        if ai.top < 0:
            ai.top = 0
        if ai.bottom > HEIGHT:
            ai.bottom = HEIGHT

        # ---------- Gerak Bola ----------
        ball.x += ball_vel_x
        ball.y += ball_vel_y

        # Pantulan dinding atas/bawah
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel_y *= -1
            # Koreksi posisi agar tidak tersangkut di luar
            if ball.top < 0:
                ball.top = 0
            if ball.bottom > HEIGHT:
                ball.bottom = HEIGHT

        # ---------- Tumbukan dengan Paddle ----------
        # Deteksi sisi kiri (paddle pemain), pastikan bola bergerak ke kiri
        if ball.colliderect(player) and ball_vel_x < 0:
            # Hit position relatif terhadap pusat paddle (-1 s/d 1)
            relative_intersect_y = (ball.centery - player.centery) / (player.height / 2)
            # Balik arah X dan atur Y berdasarkan hit
            ball_vel_x *= -1
            ball_vel_y = int(relative_intersect_y * BALL_SPEED_Y_MAX)
            # Geser bola keluar sedikit agar tidak nempel
            ball.left = player.right + 1

        # Deteksi sisi kanan (paddle AI), pastikan bola bergerak ke kanan
        if ball.colliderect(ai) and ball_vel_x > 0:
            relative_intersect_y = (ball.centery - ai.centery) / (ai.height / 2)
            ball_vel_x *= -1
            ball_vel_y = int(relative_intersect_y * BALL_SPEED_Y_MAX)
            ball.right = ai.left - 1

        # ---------- Skor ----------
        # Bola keluar kiri: AI skor
        if ball.right < 0:
            score_ai += 1
            ball_vel_x, ball_vel_y = reset_ball(ball, direction=1)  # serve ke kanan (ke AI)

        # Bola keluar kanan: Pemain skor
        if ball.left > WIDTH:
            score_player += 1
            ball_vel_x, ball_vel_y = reset_ball(ball, direction=-1)  # serve ke kiri (ke pemain)

        # ---------- Render ----------
        screen.fill(BLACK)

        # Garis tengah putus-putus
        dash_height = 12
        gap = 12
        x_center = WIDTH // 2
        for y in range(0, HEIGHT, dash_height + gap):
            pygame.draw.rect(screen, LINE_COLOR, (x_center - 2, y, 4, dash_height))

        # Gambar paddle dan bola
        pygame.draw.rect(screen, WHITE, player, border_radius=6)
        pygame.draw.rect(screen, WHITE, ai, border_radius=6)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Tampilkan skor
        score_text = font.render(f"{score_player}   :   {score_ai}", True, WHITE)
        text_rect = score_text.get_rect(center=(WIDTH // 2, 40))
        screen.blit(score_text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
