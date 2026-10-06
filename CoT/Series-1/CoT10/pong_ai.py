import pygame
import random
from typing import Optional

# -----------------------------
# Konfigurasi dasar
# -----------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_W, PADDLE_H = 12, 100
BALL_SIZE = 14

PADDLE_SPEED = 7
AI_SPEED = 6
BALL_SPEED_X_INIT = 6
BALL_SPEED_Y_INIT = 4
BALL_SPEED_MAX = 10  # batas kecepatan agar tetap playable

AI_TOLERANCE = 8  # zona mati agar AI tidak jitter

# -----------------------------
# Helper untuk reset bola
# -----------------------------
def reset_ball(ball_rect: pygame.Rect, toward_left: Optional[bool] = None):
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    # Arah X: jika toward_left True maka ke kiri; jika False maka ke kanan; jika None acak
    if toward_left is None:
        dir_x = random.choice([-1, 1])
    else:
        dir_x = -1 if toward_left else 1
    # Kecepatan awal Y acak kecil agar sudut bervariasi
    vy = random.choice([-BALL_SPEED_Y_INIT, BALL_SPEED_Y_INIT // 2, BALL_SPEED_Y_INIT])
    vx = dir_x * BALL_SPEED_X_INIT
    return vx, vy

# -----------------------------
# Main Game
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Objek
    player = pygame.Rect(20, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    ai = pygame.Rect(WIDTH - 20 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

    # Kecepatan bola
    ball_vel_x, ball_vel_y = reset_ball(ball, toward_left=None)

    score_player = 0
    score_ai = 0

    running = True
    while running:
        # 1) Event handling dasar
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Input dan gerakan player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.y -= PADDLE_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.y += PADDLE_SPEED

        # Batasi agar tidak keluar layar
        if player.top < 0:
            player.top = 0
        if player.bottom > HEIGHT:
            player.bottom = HEIGHT

        # 3) Logika AI: kejar posisi Y bola dengan toleransi
        if ai.centery < ball.centery - AI_TOLERANCE:
            ai.y += AI_SPEED
        elif ai.centery > ball.centery + AI_TOLERANCE:
            ai.y -= AI_SPEED

        # Batasi AI agar tidak keluar layar
        if ai.top < 0:
            ai.top = 0
        if ai.bottom > HEIGHT:
            ai.bottom = HEIGHT

        # 4) Pergerakan bola
        ball.x += ball_vel_x
        ball.y += ball_vel_y

        # 5) Pantulan dinding atas/bawah
        if ball.top <= 0:
            ball.top = 0
            ball_vel_y *= -1
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vel_y *= -1

        # 6) Pantulan pada paddle
        # Cegah multi-collision: setelah deteksi, geser bola sedikit
        if ball.colliderect(player) and ball_vel_x < 0:
            # Hit factor: seberapa jauh dari pusat paddle (range -1..1)
            offset = (ball.centery - player.centery) / (PADDLE_H / 2)
            ball.left = player.right  # keluarkan dari paddle
            ball_vel_x *= -1
            # Sesuaikan sudut pantulan
            ball_vel_y += int(offset * 5)

        elif ball.colliderect(ai) and ball_vel_x > 0:
            offset = (ball.centery - ai.centery) / (PADDLE_H / 2)
            ball.right = ai.left
            ball_vel_x *= -1
            ball_vel_y += int(offset * 5)

        # Clamp kecepatan supaya tidak berlebihan
        ball_vel_x = max(-BALL_SPEED_MAX, min(BALL_SPEED_MAX, ball_vel_x))
        ball_vel_y = max(-BALL_SPEED_MAX, min(BALL_SPEED_MAX, ball_vel_y))

        # 7) Sistem skor: keluar batas kiri/kanan
        if ball.right < 0:
            # AI skor
            score_ai += 1
            ball_vel_x, ball_vel_y = reset_ball(ball, toward_left=False)  # arahkan ke AI (kanan)
        elif ball.left > WIDTH:
            # Player skor
            score_player += 1
            ball_vel_x, ball_vel_y = reset_ball(ball, toward_left=True)  # arahkan ke player (kiri)

        # 8) Gambar
        screen.fill(BLACK)

        # Garis tengah
        dash_h = 10
        gap = 10
        for y in range(0, HEIGHT, dash_h + gap):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, dash_h))

        # Paddle & Bola
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Skor
        score_text_left = font.render(str(score_player), True, WHITE)
        score_text_right = font.render(str(score_ai), True, WHITE)
        screen.blit(score_text_left, (WIDTH // 2 - 60 - score_text_left.get_width(), 20))
        screen.blit(score_text_right, (WIDTH // 2 + 60, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
