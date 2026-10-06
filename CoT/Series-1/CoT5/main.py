import pygame
import random
from typing import Optional

# Konstanta dasar
WIDTH, HEIGHT = 800, 480
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

PADDLE_W, PADDLE_H = 12, 90
BALL_SIZE = 14

PLAYER_SPEED = 7
AI_SPEED = 6
BALL_SPEED = 6
MAX_BALL_VY = 7.5  # batas vertikal agar tidak terlalu curam

FIELD_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)

def reset_ball(ball, to_right: Optional[bool] = None):
    ball.center = (WIDTH // 2, HEIGHT // 2)
    # Tentukan arah horizontal bola
    if to_right is None:
        dir_x = random.choice([-1, 1])
    else:
        dir_x = 1 if to_right else -1
    # Variasikan kecepatan vertikal awal
    dir_y = random.choice([-1, 1])
    vy = dir_y * random.uniform(BALL_SPEED * 0.3, BALL_SPEED * 0.8)
    vx = dir_x * BALL_SPEED
    return vx, vy

def clamp_paddle(rect: pygame.Rect):
    if rect.top < 0:
        rect.top = 0
    if rect.bottom > HEIGHT:
        rect.bottom = HEIGHT

def draw_center_line(surface):
    dash_h = 14
    gap = 10
    x = WIDTH // 2 - 1
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, GREY, (x, y, 2, dash_h))
        y += dash_h + gap

def main():
    pygame.init()
    pygame.display.set_caption("Pong AI - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Objek permainan
    player = pygame.Rect(20, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    ai = pygame.Rect(WIDTH - 20 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

    # Kecepatan bola
    ball_vx, ball_vy = reset_ball(ball)

    # Skor
    score_player = 0
    score_ai = 0
    font = pygame.font.Font(None, 64)

    running = True
    while running:
        _dt = clock.tick(FPS)  # menjaga FPS
        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input pemain
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player.y += PLAYER_SPEED
        clamp_paddle(player)

        # AI sederhana: kejar Y bola dengan deadzone
        dead_zone = 6
        if ai.centery < ball.centery - dead_zone:
            ai.y += AI_SPEED
        elif ai.centery > ball.centery + dead_zone:
            ai.y -= AI_SPEED
        clamp_paddle(ai)

        # Gerakkan bola
        ball.x += int(ball_vx)
        ball.y += int(ball_vy)

        # Pantulan dinding atas/bawah
        if ball.top <= 0:
            ball.top = 0
            ball_vy *= -1
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vy *= -1

        # Pantulan dengan paddle
        def reflect_from_paddle(paddle: pygame.Rect, current_vx, current_vy):
            # Pastikan hanya memantul jika bola bergerak menuju paddle tsb
            if paddle is player and current_vx > 0:
                return current_vx, current_vy
            if paddle is ai and current_vx < 0:
                return current_vx, current_vy

            # Offset untuk menentukan sudut pantulan
            offset = (ball.centery - paddle.centery) / (PADDLE_H / 2)
            offset = max(-1.0, min(1.0, offset))
            new_vx = -current_vx
            new_vy = offset * MAX_BALL_VY
            # Jika new_vy terlalu kecil, beri sedikit variasi agar tidak datar
            if abs(new_vy) < 1.0:
                new_vy = 1.0 * (1 if random.random() < 0.5 else -1)
            # Dorong bola keluar dari paddle supaya tidak “lengket”
            if new_vx > 0:
                ball.left = paddle.right + 1
            else:
                ball.right = paddle.left - 1
            return new_vx, new_vy

        if ball.colliderect(player) and ball_vx < 0:
            ball_vx, ball_vy = reflect_from_paddle(player, ball_vx, ball_vy)
        elif ball.colliderect(ai) and ball_vx > 0:
            ball_vx, ball_vy = reflect_from_paddle(ai, ball_vx, ball_vy)

        # Cek gol kiri/kanan
        if ball.left <= 0:
            # Poin untuk AI
            score_ai += 1
            ball_vx, ball_vy = reset_ball(ball, to_right=True)
        elif ball.right >= WIDTH:
            # Poin untuk Player
            score_player += 1
            ball_vx, ball_vy = reset_ball(ball, to_right=False)

        # Gambar
        screen.fill(BLACK)
        draw_center_line(screen)

        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, ai)
        pygame.draw.ellipse(screen, WHITE, ball)

        # Render skor
        score_text = font.render(f"{score_player}   {score_ai}", True, WHITE)
        # Letakkan skor di tengah atas
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
