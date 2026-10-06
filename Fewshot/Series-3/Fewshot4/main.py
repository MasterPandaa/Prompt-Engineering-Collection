import pygame
import sys
import random
import math
from typing import List, Tuple

# -------------------------------
# Konfigurasi Game
# -------------------------------
# 1 = Dinding, 0 = Jalur Kosong, 2 = Pelet Kecil, 3 = Power Pellet
maze_layout: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

TILE_SIZE = 48  # Masing-masing kotak 48px agar terlihat besar
PACMAN_SPEED = 3  # pixel per frame
GHOST_SPEED = 2.5
POWER_DURATION_MS = 6000
FPS = 60

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 222)
YELLOW = (255, 210, 0)
RED = (222, 33, 33)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
NAVY = (0, 0, 128)

ROWS = len(maze_layout)
COLS = len(maze_layout[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 80  # Tambah ruang HUD di bawah
HUD_HEIGHT = 80

def grid_to_pixel(rc: Tuple[int, int]) -> Tuple[int, int]:
    r, c = rc
    x = c * TILE_SIZE + TILE_SIZE // 2
    y = r * TILE_SIZE + TILE_SIZE // 2
    return x, y


def is_wall(r: int, c: int) -> bool:
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return True
    return maze_layout[r][c] == 1


def available_dirs(r: int, c: int) -> List[Tuple[int, int]]:
    dirs = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if not is_wall(r + dr, c + dc):
            dirs.append((dr, dc))
    return dirs


def at_tile_center(x: float, y: float) -> bool:
    return (int(x) - TILE_SIZE // 2) % TILE_SIZE == 0 and (int(y) - TILE_SIZE // 2) % TILE_SIZE == 0


class Pacman:
    def __init__(self, start_rc: Tuple[int, int]):
        self.start_rc = start_rc
        sx, sy = grid_to_pixel(start_rc)
        self.x = float(sx)
        self.y = float(sy)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.radius = TILE_SIZE // 2 - 6
        self.powered = False
        self.power_end_time = 0

    def reset(self):
        sx, sy = grid_to_pixel(self.start_rc)
        self.x = float(sx)
        self.y = float(sy)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.powered = False
        self.power_end_time = 0

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.next_dir = (-1, 0)
        elif keys[pygame.K_DOWN]:
            self.next_dir = (1, 0)
        elif keys[pygame.K_LEFT]:
            self.next_dir = (0, -1)
        elif keys[pygame.K_RIGHT]:
            self.next_dir = (0, 1)

    def update(self, dt_ms: int):
        # Power timer
        if self.powered and pygame.time.get_ticks() > self.power_end_time:
            self.powered = False

        # Turning at centers
        r = int((self.y - TILE_SIZE // 2) // TILE_SIZE)
        c = int((self.x - TILE_SIZE // 2) // TILE_SIZE)
        if at_tile_center(self.x, self.y):
            # Try to turn if next_dir is available
            nr, nc = r + self.next_dir[0], c + self.next_dir[1]
            if self.next_dir != (0, 0) and not is_wall(nr, nc):
                self.dir = self.next_dir

            # If current dir blocked, stop
            nr, nc = r + self.dir[0], c + self.dir[1]
            if is_wall(nr, nc):
                self.dir = (0, 0)

        # Move with collision clamp
        speed = PACMAN_SPEED
        dx = self.dir[1] * speed
        dy = self.dir[0] * speed
        nx = self.x + dx
        ny = self.y + dy

        # Horizontal collision check
        if dx != 0:
            future_c = int((nx - TILE_SIZE // 2) // TILE_SIZE)
            if self.dir[1] > 0:  # moving right, check right edge
                tile_edge_x = (future_c) * TILE_SIZE + TILE_SIZE // 2
                if is_wall(r, future_c):
                    nx = c * TILE_SIZE + TILE_SIZE // 2  # clamp to center
                    self.dir = (0, 0)
            else:  # moving left, check left edge
                if is_wall(r, future_c):
                    nx = c * TILE_SIZE + TILE_SIZE // 2
                    self.dir = (0, 0)

        # Vertical collision check
        if dy != 0:
            future_r = int((ny - TILE_SIZE // 2) // TILE_SIZE)
            if self.dir[0] > 0:  # moving down
                if is_wall(future_r, c):
                    ny = r * TILE_SIZE + TILE_SIZE // 2
                    self.dir = (0, 0)
            else:  # moving up
                if is_wall(future_r, c):
                    ny = r * TILE_SIZE + TILE_SIZE // 2
                    self.dir = (0, 0)

        self.x = nx
        self.y = ny

    def draw(self, surf):
        color = YELLOW if not self.powered else ORANGE
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)


class Ghost:
    def __init__(self, start_rc: Tuple[int, int], color: Tuple[int, int, int]):
        self.start_rc = start_rc
        sx, sy = grid_to_pixel(start_rc)
        self.x = float(sx)
        self.y = float(sy)
        self.dir = (0, 0)
        self.radius = TILE_SIZE // 2 - 8
        self.base_color = color
        self.frightened = False
        self.dead = False  # Saat dimakan Pacman powered, ghost respawn

    def reset(self):
        sx, sy = grid_to_pixel(self.start_rc)
        self.x = float(sx)
        self.y = float(sy)
        self.dir = (0, 0)
        self.frightened = False
        self.dead = False

    def choose_dir(self):
        r = int((self.y - TILE_SIZE // 2) // TILE_SIZE)
        c = int((self.x - TILE_SIZE // 2) // TILE_SIZE)
        dirs = available_dirs(r, c)
        if not dirs:
            self.dir = (0, 0)
            return
        # Hindari putar balik jika ada opsi lain
        reverse = (-self.dir[0], -self.dir[1])
        filtered = [d for d in dirs if d != reverse]
        choice_pool = filtered if filtered else dirs
        self.dir = random.choice(choice_pool)

    def update(self, powered: bool):
        # Status frightened mengikuti powered Pacman (dari luar)
        self.frightened = powered

        # Putuskan arah saat di tengah tile atau buntu
        if at_tile_center(self.x, self.y):
            r = int((self.y - TILE_SIZE // 2) // TILE_SIZE)
            c = int((self.x - TILE_SIZE // 2) // TILE_SIZE)
            nr, nc = r + self.dir[0], c + self.dir[1]
            if self.dir == (0, 0) or is_wall(nr, nc):
                self.choose_dir()
            else:
                # Kadang pilih ulang di persimpangan
                dirs = available_dirs(r, c)
                if len(dirs) >= 3:
                    # 30% peluang ganti arah di persimpangan
                    if random.random() < 0.3:
                        self.choose_dir()

        speed = GHOST_SPEED * (0.8 if self.frightened else 1.0)
        dx = self.dir[1] * speed
        dy = self.dir[0] * speed
        nx = self.x + dx
        ny = self.y + dy

        # Collision sederhana: bila menabrak, berhenti dan pilih arah baru
        r = int((self.y - TILE_SIZE // 2) // TILE_SIZE)
        c = int((self.x - TILE_SIZE // 2) // TILE_SIZE)
        future_r = int((ny - TILE_SIZE // 2) // TILE_SIZE)
        future_c = int((nx - TILE_SIZE // 2) // TILE_SIZE)

        blocked = False
        if self.dir[1] != 0 and is_wall(r, future_c):
            blocked = True
        if self.dir[0] != 0 and is_wall(future_r, c):
            blocked = True
        if blocked:
            self.dir = (0, 0)
            self.choose_dir()
        else:
            self.x = nx
            self.y = ny

    def draw(self, surf):
        color = CYAN if self.frightened else self.base_color
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)
        # Mata sederhana
        eye_offset = 6
        pygame.draw.circle(surf, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(surf, NAVY, (int(self.x - eye_offset), int(self.y - eye_offset)), 2)
        pygame.draw.circle(surf, NAVY, (int(self.x + eye_offset), int(self.y - eye_offset)), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman Pygame - Contoh")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # Inisialisasi entity
        self.pacman = Pacman(start_rc=(3, 3))
        # Tempatkan ghost di dua sudut jalur
        self.ghosts = [
            Ghost(start_rc=(1, 1), color=RED),
            Ghost(start_rc=(5, 5), color=PINK),
        ]

        # Hitung pelet tersisa & skor
        self.score = 0
        self.lives = 3
        self.level_complete = False
        self.game_over = False

        # Duplikasi layout untuk pelet yang dapat termakan
        self.pellet_map = [row[:] for row in maze_layout]

    def reset_positions(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()

    def pellets_remaining(self) -> int:
        count = 0
        for r in range(ROWS):
            for c in range(COLS):
                if self.pellet_map[r][c] in (2, 3):
                    count += 1
        return count

    def handle_collisions(self):
        # Pacman makan pelet
        r = int((self.pacman.y - TILE_SIZE // 2) // TILE_SIZE)
        c = int((self.pacman.x - TILE_SIZE // 2) // TILE_SIZE)
        if 0 <= r < ROWS and 0 <= c < COLS:
            if self.pellet_map[r][c] == 2:
                self.pellet_map[r][c] = 0
                self.score += 10
            elif self.pellet_map[r][c] == 3:
                self.pellet_map[r][c] = 0
                self.score += 50
                self.pacman.powered = True
                self.pacman.power_end_time = pygame.time.get_ticks() + POWER_DURATION_MS

        # Cek tabrakan Pacman vs Ghost
        for g in self.ghosts:
            dist = math.hypot(self.pacman.x - g.x, self.pacman.y - g.y)
            if dist < self.pacman.radius + g.radius - 6:
                if self.pacman.powered:
                    # Makan ghost -> respawn dan poin
                    self.score += 200
                    g.reset()
                else:
                    # Pacman kena -> kehilangan nyawa
                    self.lives -= 1
                    self.reset_positions()
                    if self.lives <= 0:
                        self.game_over = True
                    break

        # Level selesai jika semua pelet habis
        if self.pellets_remaining() == 0:
            self.level_complete = True

    def draw_maze(self, surf):
        # Latar belakang area maze
        maze_surface = pygame.Surface((WIDTH, ROWS * TILE_SIZE))
        maze_surface.fill(BLACK)
        # Gambar dinding, pelet
        for r in range(ROWS):
            for c in range(COLS):
                cell = maze_layout[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                if cell == 1:
                    pygame.draw.rect(maze_surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                # Pelet/power dari pellet_map
                p = self.pellet_map[r][c]
                if p == 2:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(maze_surface, WHITE, (cx, cy), 5)
                elif p == 3:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(maze_surface, WHITE, (cx, cy), 9)
        surf.blit(maze_surface, (0, 0))

    def draw_hud(self, surf):
        hud_rect = pygame.Rect(0, ROWS * TILE_SIZE, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surf, (20, 20, 20), hud_rect)
        # Teks skor dan nyawa
        score_s = self.font.render(f"Skor: {self.score}", True, WHITE)
        lives_s = self.font.render(f"Nyawa: {self.lives}", True, WHITE)
        surf.blit(score_s, (16, ROWS * TILE_SIZE + 16))
        surf.blit(lives_s, (WIDTH - 16 - lives_s.get_width(), ROWS * TILE_SIZE + 16))

        # Status
        status_text = "" if not self.pacman.powered else "POWER!"
        if self.level_complete:
            status_text = "LEVEL SELESAI! Tekan Enter untuk reset."
        elif self.game_over:
            status_text = "GAME OVER! Tekan Enter untuk mulai ulang."
        if status_text:
            st_surf = self.font.render(status_text, True, ORANGE if self.pacman.powered else WHITE)
            surf.blit(st_surf, (16, ROWS * TILE_SIZE + 44))

    def game_loop(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.level_complete or self.game_over:
                        # Reset level/new game
                        self.pellet_map = [row[:] for row in maze_layout]
                        self.level_complete = False
                        self.game_over = False
                        self.score = 0
                        self.lives = 3
                        self.reset_positions()

            if not (self.level_complete or self.game_over):
                keys = pygame.key.get_pressed()
                self.pacman.handle_input(keys)
                self.pacman.update(dt)
                for g in self.ghosts:
                    g.update(self.pacman.powered)
                self.handle_collisions()

            # Render
            self.screen.fill(BLACK)
            self.draw_maze(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.pacman.draw(self.screen)
            self.draw_hud(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    Game().game_loop()
