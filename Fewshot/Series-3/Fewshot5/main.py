import sys
import math
import random
import pygame
from typing import List, Tuple

# -----------------------------
# Konfigurasi Game
# -----------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
BLUE = (33, 150, 243)
YELLOW = (255, 214, 0)
RED = (244, 67, 54)
PINK = (255, 105, 180)
GREEN = (76, 175, 80)
ORANGE = (255, 152, 0)

# Maze Layout: 1=Dinding, 0=Kosong, 2=Pelet, 3=Power Pellet
MAZE_LAYOUT: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 3, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 2, 1],
    [1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 3, 1, 1, 1, 2, 1, 2, 2, 1],
    [1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 3, 1],
    [1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 3, 1, 1, 1, 2, 1, 2, 2, 1],
    [1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1],
    [1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Ukuran tile dihitung dari layout dan ukuran layar
GRID_ROWS = len(MAZE_LAYOUT)
GRID_COLS = len(MAZE_LAYOUT[0])
TILE_SIZE = min(SCREEN_WIDTH // GRID_COLS, (SCREEN_HEIGHT - 80) // GRID_ROWS)
MAZE_WIDTH = GRID_COLS * TILE_SIZE
MAZE_HEIGHT = GRID_ROWS * TILE_SIZE
OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2 + 40

# Arah gerak (dx, dy)
DIRS = {
    'STOP': (0, 0),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
}
OPPOSITE = {
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT',
    'UP': 'DOWN',
    'DOWN': 'UP',
}


def grid_to_pixel(grid_pos: Tuple[int, int]) -> Tuple[int, int]:
    gx, gy = grid_pos
    return OFFSET_X + gx * TILE_SIZE + TILE_SIZE // 2, OFFSET_Y + gy * TILE_SIZE + TILE_SIZE // 2


def pixel_to_grid(px: int, py: int) -> Tuple[int, int]:
    gx = int((px - OFFSET_X) // TILE_SIZE)
    gy = int((py - OFFSET_Y) // TILE_SIZE)
    return gx, gy


class Maze:
    def __init__(self, layout: List[List[int]]):
        # Deep copy dan juga set pellet awal
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.grid = [row[:] for row in layout]
        self.wall_rects = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == 1:
                    rect = pygame.Rect(OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.wall_rects.append(rect)

    def is_wall(self, gx: int, gy: int) -> bool:
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return True
        return self.grid[gy][gx] == 1

    def has_pellet(self, gx: int, gy: int) -> bool:
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return False
        return self.grid[gy][gx] == 2

    def has_power(self, gx: int, gy: int) -> bool:
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return False
        return self.grid[gy][gx] == 3

    def eat_at(self, gx: int, gy: int) -> int:
        # Return skor yang didapat
        if gx < 0 or gy < 0 or gx >= self.cols or gy >= self.rows:
            return 0
        if self.grid[gy][gx] == 2:
            self.grid[gy][gx] = 0
            return 10
        elif self.grid[gy][gx] == 3:
            self.grid[gy][gx] = 0
            return 50
        return 0

    def pellets_remaining(self) -> int:
        return sum(1 for y in range(self.rows) for x in range(self.cols) if self.grid[y][x] in (2, 3))

    def draw(self, surface: pygame.Surface):
        # Latar belakang
        pygame.draw.rect(surface, BLACK, (OFFSET_X, OFFSET_Y, MAZE_WIDTH, MAZE_HEIGHT))
        # Grid halus
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(surface, BLUE, rect)
                else:
                    # Gambar pelet
                    if self.grid[y][x] == 2:
                        cx = rect.centerx
                        cy = rect.centery
                        pygame.draw.circle(surface, WHITE, (cx, cy), max(2, TILE_SIZE // 10))
                    elif self.grid[y][x] == 3:
                        cx = rect.centerx
                        cy = rect.centery
                        pygame.draw.circle(surface, ORANGE, (cx, cy), max(4, TILE_SIZE // 5))


class Entity:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], speed: float):
        self.grid_pos = [x, y]  # dalam grid
        self.pixel_pos = list(grid_to_pixel((x, y)))
        self.color = color
        self.radius = TILE_SIZE // 2 - 2
        self.speed = speed  # pixel per frame
        self.dir_name = 'STOP'
        self.next_dir = 'STOP'

    def at_center_of_tile(self) -> bool:
        cx, cy = grid_to_pixel((self.grid_pos[0], self.grid_pos[1]))
        return abs(self.pixel_pos[0] - cx) < 1 and abs(self.pixel_pos[1] - cy) < 1

    def set_dir(self, dir_name: str):
        self.next_dir = dir_name

    def move(self, maze: Maze):
        # Align grid pos dari pixel pos
        gx, gy = pixel_to_grid(self.pixel_pos[0], self.pixel_pos[1])
        self.grid_pos = [gx, gy]

        # Jika di tengah tile, boleh ganti arah jika tidak menabrak dinding
        if self.at_center_of_tile():
            if self.next_dir != 'STOP':
                ndx, ndy = DIRS[self.next_dir]
                nx, ny = gx + ndx, gy + ndy
                if not maze.is_wall(nx, ny):
                    self.dir_name = self.next_dir
            # Cek jika arah sekarang buntu, berhenti
            cdx, cdy = DIRS[self.dir_name]
            if maze.is_wall(gx + cdx, gy + cdy):
                self.dir_name = 'STOP'

        # Gerakkan sesuai arah saat ini
        dx, dy = DIRS[self.dir_name]
        self.pixel_pos[0] += dx * self.speed
        self.pixel_pos[1] += dy * self.speed

        # Clamp agar tetap dalam koridor (hindari goyang floating point)
        cx, cy = grid_to_pixel((gx, gy))
        if dx == 0:
            self.pixel_pos[0] = cx
        if dy == 0:
            self.pixel_pos[1] = cy

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.pixel_pos[0]), int(self.pixel_pos[1])), self.radius)


class Pacman(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, YELLOW, speed=max(1.5, TILE_SIZE / 8))
        self.mouth_angle = 0
        self.mouth_dir = 1

    def update(self, maze: Maze, keys):
        # Input arah
        if keys[pygame.K_LEFT]:
            self.set_dir('LEFT')
        elif keys[pygame.K_RIGHT]:
            self.set_dir('RIGHT')
        elif keys[pygame.K_UP]:
            self.set_dir('UP')
        elif keys[pygame.K_DOWN]:
            self.set_dir('DOWN')
        self.move(maze)

    def draw(self, surface: pygame.Surface):
        # Animasi mulut sederhana
        self.mouth_angle += self.mouth_dir * 2
        if self.mouth_angle > 30 or self.mouth_angle < 0:
            self.mouth_dir *= -1
            self.mouth_angle = max(0, min(30, self.mouth_angle))

        # Tentukan arah mulut
        dir_to_angle = {
            'LEFT': 180,
            'RIGHT': 0,
            'UP': 90,
            'DOWN': 270,
            'STOP': 0,
        }
        facing = dir_to_angle.get(self.dir_name, 0)

        center = (int(self.pixel_pos[0]), int(self.pixel_pos[1]))
        radius = self.radius
        start_angle = math.radians(facing + self.mouth_angle)
        end_angle = math.radians(facing - self.mouth_angle)
        pygame.draw.circle(surface, YELLOW, center, radius)
        # Tutup segitiga mulut
        tip = (
            center[0] + int(math.cos(math.radians(facing)) * radius),
            center[1] - int(math.sin(math.radians(facing)) * radius),
        )
        pygame.draw.polygon(surface, BLACK, [center, tip,
                                             (center[0] + int(math.cos(end_angle) * radius), center[1] - int(math.sin(end_angle) * radius))])


class Ghost(Entity):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        super().__init__(x, y, color, speed=max(1.2, TILE_SIZE / 9))
        self.base_color = color
        self.spawn = (x, y)
        self.frightened = False
        self.frightened_timer = 0.0

    def available_dirs(self, maze: Maze) -> List[str]:
        dirs = []
        gx, gy = self.grid_pos
        for name, (dx, dy) in DIRS.items():
            if name == 'STOP':
                continue
            nx, ny = gx + dx, gy + dy
            if not maze.is_wall(nx, ny):
                # hindari berbalik kecuali buntu
                if OPPOSITE.get(self.dir_name) == name:
                    continue
                dirs.append(name)
        # Jika tidak ada (buntu), izinkan berbalik
        if not dirs:
            for name, (dx, dy) in DIRS.items():
                if name == 'STOP':
                    continue
                nx, ny = gx + dx, gy + dy
                if not maze.is_wall(nx, ny):
                    dirs.append(name)
        return dirs

    def update(self, maze: Maze):
        # Frightened timer
        if self.frightened:
            self.frightened_timer -= 1 / FPS
            if self.frightened_timer <= 0:
                self.frightened = False
                self.color = self.base_color
                self.speed = max(1.2, TILE_SIZE / 9)

        # Pilih arah saat di tengah tile
        if self.at_center_of_tile():
            choices = self.available_dirs(maze)
            if choices:
                self.set_dir(random.choice(choices))
        self.move(maze)

    def scare(self, duration: float):
        self.frightened = True
        self.frightened_timer = duration
        self.color = BLUE
        self.speed = max(1.0, TILE_SIZE / 10)

    def respawn(self):
        self.grid_pos = [self.spawn[0], self.spawn[1]]
        self.pixel_pos = list(grid_to_pixel(self.spawn))
        self.dir_name = 'STOP'
        self.next_dir = 'STOP'
        self.frightened = False
        self.frightened_timer = 0.0
        self.color = self.base_color
        self.speed = max(1.2, TILE_SIZE / 9)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman by Cascade')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 22)
        self.big_font = pygame.font.SysFont('consolas', 48)

        self.reset()

    def reset(self):
        self.maze = Maze(MAZE_LAYOUT)
        # Posisi awal Pacman dan Ghosts (pakai tile kosong)
        self.pacman = Pacman(1, 1)
        self.ghosts = [
            Ghost(14, 1, RED),
            Ghost(14, 14, PINK),
        ]
        self.score = 0
        self.game_over = False
        self.win = False
        self.power_timer = 0.0

    def handle_collisions(self):
        # Makan pelet/power
        pgx, pgy = pixel_to_grid(int(self.pacman.pixel_pos[0]), int(self.pacman.pixel_pos[1]))
        gained = self.maze.eat_at(pgx, pgy)
        if gained:
            self.score += gained
            if gained == 50:
                # aktifkan power up
                self.power_timer = 8.0
                for g in self.ghosts:
                    g.scare(self.power_timer)
        if self.maze.pellets_remaining() == 0:
            self.win = True

        # Tabrakan pacman vs ghost
        for g in self.ghosts:
            dist = math.hypot(self.pacman.pixel_pos[0] - g.pixel_pos[0], self.pacman.pixel_pos[1] - g.pixel_pos[1])
            if dist < (self.pacman.radius + g.radius) * 0.9:
                if g.frightened:
                    # Makan ghost
                    self.score += 200
                    g.respawn()
                else:
                    self.game_over = True

    def update(self):
        keys = pygame.key.get_pressed()
        if not (self.game_over or self.win):
            self.pacman.update(self.maze, keys)
            for g in self.ghosts:
                g.update(self.maze)
            # Power timer
            if self.power_timer > 0:
                self.power_timer -= 1 / FPS
                if self.power_timer <= 0:
                    for g in self.ghosts:
                        g.frightened = False
                        g.color = g.base_color
                        g.speed = max(1.2, TILE_SIZE / 9)
            self.handle_collisions()
        else:
            # Tekan R untuk reset
            if keys[pygame.K_r]:
                self.reset()

    def draw_hud(self):
        # Skor
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (OFFSET_X, OFFSET_Y - 34))
        # Power
        if self.power_timer > 0:
            p_surf = self.font.render(f"POWER: {self.power_timer:0.1f}s", True, ORANGE)
            self.screen.blit(p_surf, (OFFSET_X + 200, OFFSET_Y - 34))
        # Bantuan
        help_text = self.font.render("Arrows: Move | R: Restart | ESC: Quit", True, GRAY)
        self.screen.blit(help_text, (OFFSET_X, OFFSET_Y + MAZE_HEIGHT + 6))

    def draw(self):
        self.screen.fill((12, 12, 12))
        self.maze.draw(self.screen)
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_hud()

        if self.game_over:
            over = self.big_font.render("GAME OVER - Press R to Restart", True, WHITE)
            self.screen.blit(over, over.get_rect(center=(SCREEN_WIDTH // 2, 40)))
        if self.win:
            win = self.big_font.render("YOU WIN! - Press R to Restart", True, GREEN)
            self.screen.blit(win, win.get_rect(center=(SCREEN_WIDTH // 2, 40)))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == '__main__':
    Game().run()
