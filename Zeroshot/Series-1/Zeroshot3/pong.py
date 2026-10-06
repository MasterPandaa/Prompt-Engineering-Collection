import pygame
import sys
import random
import math

# =========================
# Konfigurasi Permainan
# =========================
WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 16

PLAYER_SPEED = 7
AI_SPEED = 6  # Sedikit lebih lambat agar adil
BALL_SPEED = 6
BALL_SPEED_MAX = 12
BALL_SPEED_INC = 1.03  # Bola sedikit lebih cepat saat kena paddle

SCORE_FONT_SIZE = 48
WIN_SCORE = None  # Set angka (misal 10) jika ingin batas kemenangan

BG_COLOR = (20, 20, 20)
FG_COLOR = (235, 235, 235)
ACCENT_COLOR = (100, 200, 255)


def clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))


def reset_ball(ball_rect, direction=1):
    """
    Reset bola ke tengah dengan arah horizontal ke 'direction' (1 ke kanan, -1 ke kiri)
    dan sedikit variasi sudut vertikal.
    """
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)

    # Pilih sudut acak agar tidak terlalu vertikal/horizontal
    angle_deg = random.uniform(-30, 30)
    angle_rad = math.radians(angle_deg)

    vx = direction * BALL_SPEED * math.cos(angle_rad)
    vy = BALL_SPEED * math.sin(angle_rad)

    # Pastikan komponen horizontal cukup besar agar game dinamis
    if abs(vx) < 3:
        vx = 3 * direction

    return vx, vy


def draw_center_line(surface):
    dash_height = 20
    gap = 16
    x = WIDTH // 2 - 2
    for y in range(0, HEIGHT, dash_height + gap):
        pygame.draw.rect(surface, (70, 70, 70), (x, y, 4, dash_height))


def main():
    pygame.init()
    pygame.display.set_caption("Pong - Player vs AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", SCORE_FONT_SIZE)

    # Inisialisasi paddle
    player = pygame.Rect(40, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai = pygame.Rect(WIDTH - 40 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

    # Inisialisasi bola
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_vx, ball_vy = reset_ball(ball, direction=random.choice([-1, 1]))

    # Skor
    score_player = 0
    score_ai = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Tidak terlalu penting, tapi bisa dipakai jika ingin gerakan berbasis waktu

        # -------------------------
        # Event Handling
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()

        # -------------------------
        # Update - Player Movement
        # -------------------------
        if keys[pygame.K_w]:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            player.y += PLAYER_SPEED
        player.y = clamp(player.y, 0, HEIGHT - PADDLE_HEIGHT)

        # -------------------------
        # Update - AI Movement
        # -------------------------
        # AI mengikuti posisi Y bola dengan sedikit deadzone agar tidak terlalu "sempurna"
        ai_deadzone = 10
        if ball.centery < ai.centery - ai_deadzone:
            ai.y -= AI_SPEED
        elif ball.centery > ai.centery + ai_deadzone:
            ai.y += AI_SPEED
        ai.y = clamp(ai.y, 0, HEIGHT - PADDLE_HEIGHT)

        # -------------------------
        # Update - Ball Movement
        # -------------------------
        ball.x += int(ball_vx)
        ball.y += int(ball_vy)

        # Pantulan dinding atas/bawah
        if ball.top <= 0:
            ball.top = 0
            ball_vy *= -1
        elif ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vy *= -1

        # -------------------------
        # Collision - Ball & Paddles
        # -------------------------
        # Player paddle
        if ball.colliderect(player) and ball_vx < 0:
            # Tempatkan bola di luar paddle untuk menghindari "nempel"
            ball.left = player.right

            # Hit factor: posisi relatif benturan untuk mengubah sudut pantul
            hit_pos = (ball.centery - player.centery) / (PADDLE_HEIGHT / 2)  # -1 .. 1
            hit_pos = clamp(hit_pos, -1, 1)

            speed = math.hypot(ball_vx, ball_vy) * BALL_SPEED_INC
            speed = clamp(speed, 4, BALL_SPEED_MAX)

            angle = hit_pos * (math.pi / 3)  # max ~60 derajat
            ball_vx = speed * math.cos(angle)
            ball_vy = speed * math.sin(angle)

        # AI paddle
        if ball.colliderect(ai) and ball_vx > 0:
            ball.right = ai.left

            hit_pos = (ball.centery - ai.centery) / (PADDLE_HEIGHT / 2)
            hit_pos = clamp(hit_pos, -1, 1)

            speed = math.hypot(ball_vx, ball_vy) * BALL_SPEED_INC
            speed = clamp(speed, 4, BALL_SPEED_MAX)

            angle = hit_pos * (math.pi / 3)
            ball_vx = -speed * math.cos(angle)
            ball_vy = speed * math.sin(angle)

        # -------------------------
        # Scoring - Bola melewati sisi kiri/kanan
        # -------------------------
        if ball.right < 0:
            # AI skor
            score_ai += 1
            ball_vx, ball_vy = reset_ball(ball, direction=1)
            # Optional: reset paddle posisi
            player.centery = HEIGHT // 2
            ai.centery = HEIGHT // 2

        elif ball.left > WIDTH:
            # Player skor
            score_player += 1
            ball_vx, ball_vy = reset_ball(ball, direction=-1)
            player.centery = HEIGHT // 2
            ai.centery = HEIGHT // 2

        # Optional: cek kemenangan
        if WIN_SCORE is not None:
            if score_player >= WIN_SCORE or score_ai >= WIN_SCORE:
                running = False

        # -------------------------
        # Render
        # -------------------------
        screen.fill(BG_COLOR)
        draw_center_line(screen)

        # Gambar paddle dan bola
        pygame.draw.rect(screen, FG_COLOR, player, border_radius=6)
        pygame.draw.rect(screen, FG_COLOR, ai, border_radius=6)
        pygame.draw.ellipse(screen, ACCENT_COLOR, ball)

        # Tampilkan skor
        score_surf_p = font.render(str(score_player), True, FG_COLOR)
        score_surf_ai = font.render(str(score_ai), True, FG_COLOR)
        screen.blit(score_surf_p, (WIDTH * 0.25 - score_surf_p.get_width() // 2, 20))
        screen.blit(score_surf_ai, (WIDTH * 0.75 - score_surf_ai.get_width() // 2, 20))

        # Info kontrol
        info_font = pygame.font.SysFont("Consolas", 20)
        info_text = info_font.render("Controls: W = Up, S = Down, Esc = Quit", True, (160, 160, 160))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
