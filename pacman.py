import sys
import random
import math
import pygame
from typing import List, Tuple, Set

# =============================
# Konfigurasi Utama
# =============================
pygame.init()

# 1 = Dinding, 0 = Jalur Kosong, 2 = Pelet Kecil, 3 = Power Pellet
MAZE_LAYOUT: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

TILE_SIZE = 48
ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 80  # ruang HUD
FPS = 60

# Warna
BLACK = (0, 0, 0)
NAVY = (0, 0, 80)
BLUE = (33, 150, 243)
WHITE = (255, 255, 255)
YELLOW = (255, 208, 0)
RED = (233, 30, 99)
PINK = (255, 105, 180)
ORANGE = (255, 152, 0)
CYAN = (0, 188, 212)
GREEN = (76, 175, 80)

# Skor dan Gameplay
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
EAT_GHOST_SCORE = 200
POWER_DURATION_SEC = 8.0
INITIAL_LIVES = 3

# Arah
DIR_VECS = {
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1)
}
OPPOSITE = {
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT',
    'UP': 'DOWN',
    'DOWN': 'UP'
}


def grid_to_pix(cell: Tuple[int, int]) -> Tuple[int, int]:
    cx, cy = cell
    return cx * TILE_SIZE + TILE_SIZE // 2, cy * TILE_SIZE + TILE_SIZE // 2


def pix_to_grid(px: float, py: float) -> Tuple[int, int]:
    return int(px // TILE_SIZE), int(py // TILE_SIZE)


class Maze:
    def __init__(self, layout: List[List[int]]):
        self.layout = [row[:] for row in layout]
        self.rows = len(layout)
        self.cols = len(layout[0])
        # kumpulkan pelet dan power pellete sebagai set grid posisi
        self.pellets: Set[Tuple[int, int]] = set()
        self.power_pellets: Set[Tuple[int, int]] = set()
        for y in range(self.rows):
            for x in range(self.cols):
                if self.layout[y][x] == 2:
                    self.pellets.add((x, y))
                elif self.layout[y][x] == 3:
                    self.power_pellets.add((x, y))

    def is_wall(self, grid_pos: Tuple[int, int]) -> bool:
        x, y = grid_pos
        if x < 0 or y < 0 or x >= self.cols or y >= self.rows:
            return True
        return self.layout[y][x] == 1

    def draw(self, surface: pygame.Surface):
        # Latar belakang arena
        surface.fill(BLACK)
        # dinding
        for y in range(self.rows):
            for x in range(self.cols):
                if self.layout[y][x] == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, NAVY, rect)
                    # border dinding
                    pygame.draw.rect(surface, BLUE, rect, 3)
        # pelet
        for (x, y) in self.pellets:
            cx, cy = grid_to_pix((x, y))
            pygame.draw.circle(surface, WHITE, (cx, cy), 5)
        # power pellet
        for (x, y) in self.power_pellets:
            cx, cy = grid_to_pix((x, y))
            pygame.draw.circle(surface, ORANGE, (cx, cy), 9)


class Entity:
    def __init__(self, x: int, y: int, speed: float):
        self.grid_x = x
        self.grid_y = y
        self.x, self.y = grid_to_pix((x, y))
        self.dir = 'LEFT'
        self.next_dir = None
        self.speed = speed  # pixel per frame

    def at_center_of_tile(self) -> bool:
        cx, cy = grid_to_pix(pix_to_grid(self.x, self.y))
        return abs(self.x - cx) < 1 and abs(self.y - cy) < 1

    def set_dir(self, d: str):
        self.next_dir = d

    def update_position(self, maze: Maze):
        # coba ganti arah saat di pusat tile
        if self.next_dir and self.at_center_of_tile():
            vx, vy = DIR_VECS[self.next_dir]
            nx = self.grid_x + vx
            ny = self.grid_y + vy
            if not maze.is_wall((nx, ny)):
                self.dir = self.next_dir
                self.next_dir = None
        # gerak sesuai dir jika tidak menabrak dinding
        vx, vy = DIR_VECS[self.dir]
        next_x = self.x + vx * self.speed
        next_y = self.y + vy * self.speed
        next_grid = pix_to_grid(next_x, next_y)
        # Untuk mencegah nembus dinding, izinkan jalan hanya jika tidak wall
        if not maze.is_wall(next_grid):
            self.x = next_x
            self.y = next_y
            self.grid_x, self.grid_y = pix_to_grid(self.x, self.y)
        else:
            # snap ke center tile agar belok mulus
            cx, cy = grid_to_pix((self.grid_x, self.grid_y))
            self.x, self.y = cx, cy

    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int]):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), TILE_SIZE // 2 - 6)


class Pacman(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, speed=2.5)
        self.dir = 'LEFT'

    def draw(self, surface: pygame.Surface, mouth_anim_phase: float, color: Tuple[int, int, int] = YELLOW):
        # gambar sederhana: lingkaran dengan mulut animasi based on phase
        radius = TILE_SIZE // 2 - 6
        angle = 25 + int(20 * (0.5 + 0.5 * math.sin(mouth_anim_phase)))
        start_angle = math.radians(angle)
        end_angle = math.radians(360 - angle)
        rect = pygame.Rect(int(self.x - radius), int(self.y - radius), radius * 2, radius * 2)
        # Rotasi arah mulut
        dir_angle = {'RIGHT': 0, 'DOWN': 90, 'LEFT': 180, 'UP': 270}[self.dir]
        pygame.draw.arc(surface, color, rect, math.radians(dir_angle) + start_angle, math.radians(dir_angle) + end_angle, radius)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        # tutup mulut: menggambar segitiga hitam kecil untuk efek mulut
        mx, my = DIR_VECS[self.dir]
        mouth_len = radius
        tip = (int(self.x + mx * mouth_len), int(self.y + my * mouth_len))
        left = (int(self.x + math.cos(math.radians(dir_angle + angle)) * radius), int(self.y + math.sin(math.radians(dir_angle + angle)) * radius))
        right = (int(self.x + math.cos(math.radians(dir_angle - angle)) * radius), int(self.y + math.sin(math.radians(dir_angle - angle)) * radius))
        pygame.draw.polygon(surface, BLACK, [tip, left, right])


class Ghost(Entity):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], name: str):
        super().__init__(x, y, speed=2.0)
        self.base_color = color
        self.name = name
        self.spawn = (x, y)

    def available_directions(self, maze: Maze) -> List[str]:
        dirs = []
        for d, (vx, vy) in DIR_VECS.items():
            nx = self.grid_x + vx
            ny = self.grid_y + vy
            if not maze.is_wall((nx, ny)):
                dirs.append(d)
        return dirs

    def choose_direction(self, maze: Maze):
        # pilih arah acak di pusat tile, hindari reverse kecuali buntu
        if self.at_center_of_tile():
            options = self.available_directions(maze)
            if len(options) > 1 and OPPOSITE[self.dir] in options:
                options.remove(OPPOSITE[self.dir])
            if options:
                self.dir = random.choice(options)

    def update(self, maze: Maze):
        self.choose_direction(maze)
        self.update_position(maze)

    def draw(self, surface: pygame.Surface, frightened: bool = False):
        color = CYAN if frightened else self.base_color
        radius = TILE_SIZE // 2 - 6
        # badan hantu
        pygame.draw.circle(surface, color, (int(self.x), int(self.y - radius // 3)), radius)
        rect = pygame.Rect(int(self.x - radius), int(self.y - radius // 3), radius * 2, radius)
        pygame.draw.rect(surface, color, rect)
        # kaki zigzag
        foot_w = radius // 2
        for i in range(3):
            px = int(self.x - radius + i * foot_w + foot_w // 2)
            py = int(self.y + radius // 3)
            pygame.draw.circle(surface, color, (px, py), foot_w // 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pacman (Pygame)')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 22)
        self.big_font = pygame.font.SysFont('arial', 36, bold=True)

        self.maze = Maze(MAZE_LAYOUT)
        # posisi awal (gunakan salah satu jalur kosong)
        self.pacman = Pacman(3, 5)
        self.ghosts = [
            Ghost(3, 1, RED, 'Blinky'),
            Ghost(5, 5, PINK, 'Pinky')
        ]

        self.score = 0
        self.lives = INITIAL_LIVES
        self.power_timer = 0.0
        self.mouth_phase = 0.0
        self.game_over = False
        self.win = False

    def reset_positions(self):
        # reset tanpa reset skor/pelet
        self.pacman = Pacman(3, 5)
        for g in self.ghosts:
            gx, gy = g.spawn
            self.ghosts[self.ghosts.index(g)] = Ghost(gx, gy, g.base_color, g.name)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman.set_dir('LEFT')
        elif keys[pygame.K_RIGHT]:
            self.pacman.set_dir('RIGHT')
        elif keys[pygame.K_UP]:
            self.pacman.set_dir('UP')
        elif keys[pygame.K_DOWN]:
            self.pacman.set_dir('DOWN')

    def eat_pellets(self):
        gp = (self.pacman.grid_x, self.pacman.grid_y)
        if gp in self.maze.pellets:
            self.maze.pellets.remove(gp)
            self.score += PELLET_SCORE
        elif gp in self.maze.power_pellets:
            self.maze.power_pellets.remove(gp)
            self.score += POWER_PELLET_SCORE
            self.power_timer = POWER_DURATION_SEC

    def check_collisions(self):
        pac_rect = pygame.Rect(0, 0, TILE_SIZE // 2, TILE_SIZE // 2)
        pac_rect.center = (int(self.pacman.x), int(self.pacman.y))
        for i, g in enumerate(self.ghosts):
            ghost_rect = pygame.Rect(0, 0, TILE_SIZE // 2, TILE_SIZE // 2)
            ghost_rect.center = (int(g.x), int(g.y))
            if pac_rect.colliderect(ghost_rect):
                if self.power_timer > 0:
                    # makan hantu
                    self.score += EAT_GHOST_SCORE
                    # respawn ghost ke spawn
                    gx, gy = g.spawn
                    self.ghosts[i] = Ghost(gx, gy, g.base_color, g.name)
                else:
                    # pacman mati
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_positions()
                break

    def update(self, dt: float):
        if self.game_over or self.win:
            return
        self.handle_input()
        self.pacman.update_position(self.maze)
        for g in self.ghosts:
            g.update(self.maze)
        self.eat_pellets()
        self.check_collisions()
        # power-up countdown
        if self.power_timer > 0:
            self.power_timer = max(0.0, self.power_timer - dt)
        # menang jika semua pelet habis
        if not self.maze.pellets and not self.maze.power_pellets:
            self.win = True
        # animasi mulut
        self.mouth_phase += dt * 10

    def draw_hud(self):
        hud_rect = pygame.Rect(0, ROWS * TILE_SIZE, WIDTH, HEIGHT - ROWS * TILE_SIZE)
        pygame.draw.rect(self.screen, (15, 15, 15), hud_rect)
        # skor
        score_surf = self.font.render(f"Skor: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (16, ROWS * TILE_SIZE + 16))
        # nyawa
        lives_surf = self.font.render(f"Nyawa: {self.lives}", True, WHITE)
        self.screen.blit(lives_surf, (WIDTH - 140, ROWS * TILE_SIZE + 16))
        # status power
        if self.power_timer > 0:
            power_surf = self.font.render(f"Power: {self.power_timer:0.1f}s", True, ORANGE)
            self.screen.blit(power_surf, (16, ROWS * TILE_SIZE + 44))

    def draw(self):
        self.maze.draw(self.screen)
        frightened = self.power_timer > 0
        # draw ghosts
        for g in self.ghosts:
            g.draw(self.screen, frightened)
        # draw pacman
        self.pacman.draw(self.screen, self.mouth_phase)
        # HUD
        self.draw_hud()
        # end state
        if self.game_over:
            msg = self.big_font.render('GAME OVER - Tekan R untuk restart', True, RED)
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        elif self.win:
            msg = self.big_font.render('MENANG! - Tekan R untuk restart', True, GREEN)
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    def restart(self):
        # reset total
        self.__init__()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r and (self.game_over or self.win):
                        self.restart()

            self.update(dt)
            self.draw()

            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
