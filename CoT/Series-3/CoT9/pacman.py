import sys
import math
import random
import pygame
from pygame import Rect

# ==========================
# Konfigurasi Global
# ==========================
TILE_SIZE = 24
FPS = 60
PACMAN_SPEED = 2.0  # pixel per frame
GHOST_SPEED_NORMAL = 1.8
GHOST_SPEED_FRIGHT = 1.2
GHOST_SPEED_EATEN = 3.0
POWER_DURATION = 7.0  # detik
SCREEN_BG = (0, 0, 0)
WALL_COLOR = (33, 33, 222)
PELLET_COLOR = (255, 200, 200)
POWER_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 0)
PACMAN_COLOR = (255, 255, 0)
GHOST_COLORS = [(255, 0, 0), (255, 128, 255), (0, 255, 255), (255, 128, 0)]
FRIGHTENED_COLOR = (40, 40, 255)

# Maze layout: #=wall, .=pellet, o=power, P=pacman spawn, G=ghost spawn
MAZE_LAYOUT = [
    "#############################",
    "#........##.........##......#",
    "#.####...##.#####...##.####.#",
    "#o#  #.................#  #o#",
    "#.####.###.#######.###.####.#",
    "#......# #...###...# #......#",
    "######.# ###.###.### #.######",
    "     #.#   # GPG #   #.#     ",
    "######.# ### ### ### #.######",
    "#......# #.........# #......#",
    "#.####.###.#######.###.####.#",
    "#o#  #.................#  #o#",
    "#.####...##.#####...##.####.#",
    "#........##.........##......#",
    "#############################",
]

# Catatan: Spasi ' ' dianggap jalan (bukan dinding), untuk area rumah ghost/tunnel


def grid_to_pixel(grid_pos):
    gx, gy = grid_pos
    return (int(gx * TILE_SIZE + TILE_SIZE / 2), int(gy * TILE_SIZE + TILE_SIZE / 2))


def pixel_to_grid(pixel_pos):
    px, py = pixel_pos
    return (int(px // TILE_SIZE), int(py // TILE_SIZE))


def opposite_dir(direction):
    return (-direction[0], -direction[1])


DIRS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.h = len(layout)
        self.w = len(layout[0])
        self.walls = set()
        self.pellets = set()
        self.power = set()
        self.pacman_spawn = None
        self.ghost_spawns = []
        self.parse()
        self.wall_rects = self._build_wall_rects()

    def parse(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power.add((x, y))
                elif ch == 'P':
                    self.pacman_spawn = (x, y)
                    self.pellets.add((x, y))  # tile ini juga berisi pellet agar konsisten
                elif ch == 'G':
                    self.ghost_spawns.append((x, y))
                    self.pellets.add((x, y))
                # spasi atau lainnya dianggap jalan kosong

    def _build_wall_rects(self):
        # Gabungkan dinding menjadi rect per tile (sederhana)
        rects = []
        for (x, y) in self.walls:
            rects.append(Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return rects

    def is_wall(self, grid_pos):
        return grid_pos in self.walls

    def valid_tile(self, grid_pos):
        x, y = grid_pos
        return 0 <= x < self.w and 0 <= y < self.h and not self.is_wall((x, y))

    def draw(self, surf, flicker=False):
        # Draw walls
        for (x, y) in self.walls:
            r = Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, WALL_COLOR, r, border_radius=4)
        # Draw pellets
        for (x, y) in self.pellets:
            cx = int(x * TILE_SIZE + TILE_SIZE / 2)
            cy = int(y * TILE_SIZE + TILE_SIZE / 2)
            pygame.draw.circle(surf, PELLET_COLOR, (cx, cy), 3)
        # Draw power pellets (blink)
        for (x, y) in self.power:
            cx = int(x * TILE_SIZE + TILE_SIZE / 2)
            cy = int(y * TILE_SIZE + TILE_SIZE / 2)
            radius = 6 if not flicker else 3
            pygame.draw.circle(surf, POWER_COLOR, (cx, cy), radius)

    def wrap_position(self, pixel_pos):
        # Wrap horizontal untuk tunnel jika keluar batas layar
        x, y = pixel_pos
        max_w = self.w * TILE_SIZE
        if x < 0:
            x = max_w - 1
        elif x >= max_w:
            x = 0
        return (x, y)

    def is_intersection(self, grid_pos):
        # Persimpangan: jumlah arah valid > 2 (atau == 2 tapi bukan lurus)
        x, y = grid_pos
        options = 0
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if self.valid_tile((x + dx, y + dy)):
                options += 1
        return options >= 3


class Entity:
    def __init__(self, maze, grid_pos, color, speed):
        self.maze = maze
        self.pos = pygame.Vector2(*grid_to_pixel(grid_pos))
        self.dir = pygame.Vector2(0, 0)
        self.next_dir = pygame.Vector2(0, 0)
        self.speed = speed
        self.color = color
        self.radius = 9

    def at_tile_center(self):
        # Dianggap center jika jarak ke tengah tile < 0.5 pixel
        gx, gy = pixel_to_grid(self.pos)
        cx, cy = grid_to_pixel((gx, gy))
        return (abs(self.pos.x - cx) < 0.5) and (abs(self.pos.y - cy) < 0.5)

    def snap_to_center(self):
        gx, gy = pixel_to_grid(self.pos)
        cx, cy = grid_to_pixel((gx, gy))
        self.pos.update(cx, cy)

    def can_move_dir(self, direction):
        if direction.length_squared() == 0:
            return False
        gx, gy = pixel_to_grid(self.pos)
        dx, dy = int(direction.x), int(direction.y)
        target = (gx + dx, gy + dy)
        return self.maze.valid_tile(target)

    def move(self, dt, speed=None):
        sp = speed if speed is not None else self.speed
        self.pos += self.dir * sp
        self.pos.xy = self.maze.wrap_position(self.pos.xy)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class Pacman(Entity):
    def __init__(self, maze, grid_pos):
        super().__init__(maze, grid_pos, PACMAN_COLOR, PACMAN_SPEED)
        self.mouth_angle = 0
        self.mouth_dir = 1

    def handle_input(self, keys):
        for key, d in DIRS.items():
            if keys[key]:
                self.next_dir.update(d)

    def update(self):
        # Ganti arah hanya di pusat tile dan jika tile berikutnya tidak dinding
        if self.at_tile_center():
            if self.next_dir.length_squared() and self.can_move_dir(self.next_dir):
                self.dir.update(self.next_dir)
            # Jika arah saat ini menabrak dinding, berhenti
            if not self.can_move_dir(self.dir):
                self.dir.update((0, 0))
        # Gerak
        self.move(1)
        # Animasi mulut sederhana
        self.mouth_angle += 2 * self.mouth_dir
        if self.mouth_angle > 30 or self.mouth_angle < 0:
            self.mouth_dir *= -1
            self.mouth_angle = max(0, min(30, self.mouth_angle))

    def draw(self, surf):
        # Gambar Pacman dengan mulut membuka-menutup
        x, y = int(self.pos.x), int(self.pos.y)
        start_angle = self._dir_angle() + math.radians(self.mouth_angle)
        end_angle = self._dir_angle() - math.radians(self.mouth_angle)
        pygame.draw.circle(surf, PACMAN_COLOR, (x, y), self.radius)
        # segitiga mulut (hapus area)
        mouth_len = self.radius
        p1 = (x, y)
        p2 = (x + int(math.cos(start_angle) * mouth_len), y + int(math.sin(start_angle) * mouth_len))
        p3 = (x + int(math.cos(end_angle) * mouth_len), y + int(math.sin(end_angle) * mouth_len))
        pygame.draw.polygon(surf, SCREEN_BG, [p1, p2, p3])

    def _dir_angle(self):
        if self.dir.x == 1:
            return 0
        if self.dir.x == -1:
            return math.pi
        if self.dir.y == 1:
            return math.pi / 2
        if self.dir.y == -1:
            return -math.pi / 2
        return 0


class Ghost(Entity):
    def __init__(self, maze, grid_pos, color):
        super().__init__(maze, grid_pos, color, GHOST_SPEED_NORMAL)
        self.state = 'normal'  # normal, frightened, eaten
        self.home = grid_pos

    def set_state(self, state):
        self.state = state

    def update(self):
        # Tentukan kecepatan berdasar state
        if self.state == 'frightened':
            speed = GHOST_SPEED_FRIGHT
        elif self.state == 'eaten':
            speed = GHOST_SPEED_EATEN
        else:
            speed = self.speed

        # Di pusat tile -> putuskan arah
        if self.at_tile_center():
            self._choose_direction()
        # Move
        self.move(1, speed)

    def _choose_direction(self):
        gx, gy = pixel_to_grid(self.pos)
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        valid = []
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            if self.maze.valid_tile((nx, ny)):
                # hindari berbalik arah jika memungkinkan
                if self.dir.length_squared() and (dx, dy) == (-int(self.dir.x), -int(self.dir.y)):
                    continue
                valid.append((dx, dy))
        # Jika semua valid ter-filter habis, izinkan berbalik
        if not valid:
            for dx, dy in dirs:
                nx, ny = gx + dx, gy + dy
                if self.maze.valid_tile((nx, ny)):
                    valid.append((dx, dy))
        # Pilih berdasarkan state
        if self.state == 'eaten':
            # Kejar rumah (minimize distance)
            tx, ty = self.home
            best = None
            best_dist = 1e9
            for dx, dy in valid:
                nx, ny = gx + dx, gy + dy
                d = abs(tx - nx) + abs(ty - ny)
                if d < best_dist:
                    best_dist, best = d, (dx, dy)
            if best:
                self.dir.update(best)
            else:
                self.dir.update((0, 0))
        elif self.state == 'frightened':
            # Acak
            if valid:
                self.dir.update(random.choice(valid))
            else:
                self.dir.update((0, 0))
        else:  # normal
            # Sederhana: random di persimpangan, lanjut lurus bila memungkinkan
            if self.maze.is_intersection((gx, gy)) or not self.can_move_dir(self.dir):
                if valid:
                    self.dir.update(random.choice(valid))
                else:
                    self.dir.update((0, 0))
            # else: lanjut arah sekarang

    def draw(self, surf):
        color = FRIGHTENED_COLOR if self.state == 'frightened' else self.color
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        # mata sederhana arah gerak
        eye_offset = pygame.Vector2(self.dir.x, self.dir.y) * 3
        for ex in (-3, 3):
            pygame.draw.circle(surf, (255, 255, 255), (int(self.pos.x + ex/2), int(self.pos.y - 2)), 3)
            pygame.draw.circle(surf, (0, 0, 0), (int(self.pos.x + ex/2 + eye_offset.x), int(self.pos.y - 2 + eye_offset.y)), 1)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman - Pygame')
        self.maze = Maze(MAZE_LAYOUT)
        self.width = self.maze.w * TILE_SIZE
        self.height = self.maze.h * TILE_SIZE + 40  # area UI
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 18)

        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = 'playing'  # playing, dead, gameover
        self.power_timer = 0.0

        self._spawn_entities()

    def _spawn_entities(self):
        pac_spawn = self.maze.pacman_spawn
        if pac_spawn is None:
            # fallback: cari tile jalan pertama
            for y, row in enumerate(self.maze.layout):
                for x, ch in enumerate(row):
                    if ch != '#':
                        pac_spawn = (x, y)
                        break
                if pac_spawn:
                    break
        self.pacman = Pacman(self.maze, pac_spawn)

        self.ghosts = []
        spawns = self.maze.ghost_spawns or [pac_spawn]
        for i in range(4):
            gpos = spawns[i % len(spawns)]
            ghost = Ghost(self.maze, gpos, GHOST_COLORS[i % len(GHOST_COLORS)])
            # awal keluar kandang, arah ke kiri/kanan acak
            ghost.dir.update(random.choice([(1, 0), (-1, 0)]))
            self.ghosts.append(ghost)

    def reset_after_death(self):
        pygame.time.delay(800)
        self._spawn_entities()
        self.state = 'playing'
        self.power_timer = 0.0
        for g in self.ghosts:
            g.set_state('normal')

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()

            if self.state == 'playing':
                self._update_game(dt)
            self._render()

    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.state == 'gameover' and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.__init__()
        keys = pygame.key.get_pressed()
        if self.state == 'playing':
            self.pacman.handle_input(keys)

    def _eat_at_tile(self):
        gx, gy = pixel_to_grid(self.pacman.pos)
        # makan pellet
        if (gx, gy) in self.maze.pellets:
            self.maze.pellets.remove((gx, gy))
            self.score += 10
        # makan power
        if (gx, gy) in self.maze.power:
            self.maze.power.remove((gx, gy))
            self.score += 50
            self.power_timer = POWER_DURATION
            for g in self.ghosts:
                if g.state != 'eaten':
                    g.set_state('frightened')

    def _update_game(self, dt):
        # Update pemain
        self.pacman.update()
        if self.pacman.at_tile_center():
            self._eat_at_tile()

        # Update power timer dan state ghost
        if self.power_timer > 0:
            self.power_timer -= dt
            if self.power_timer <= 0:
                for g in self.ghosts:
                    if g.state != 'eaten':
                        g.set_state('normal')

        # Update ghost
        for g in self.ghosts:
            g.update()

        # Cek collision Pacman-Ghost
        p_rect = Rect(int(self.pacman.pos.x - self.pacman.radius), int(self.pacman.pos.y - self.pacman.radius), self.pacman.radius * 2, self.pacman.radius * 2)
        for g in self.ghosts:
            g_rect = Rect(int(g.pos.x - g.radius), int(g.pos.y - g.radius), g.radius * 2, g.radius * 2)
            if p_rect.colliderect(g_rect):
                if g.state == 'frightened':
                    g.set_state('eaten')
                    self.score += 200
                elif g.state == 'eaten':
                    # abaikan (ghost menuju home)
                    pass
                else:
                    # Pacman mati
                    self.lives -= 1
                    self.state = 'dead'
                    if self.lives < 0:
                        self.state = 'gameover'
                    else:
                        self.reset_after_death()
                    return

        # Jika ghost yang 'eaten' sampai home, kembali normal
        for g in self.ghosts:
            if g.state == 'eaten' and g.at_tile_center():
                if pixel_to_grid(g.pos) == g.home:
                    g.set_state('normal')

        # Menang jika semua pelet + power habis
        if not self.maze.pellets and not self.maze.power:
            self.level += 1
            # reset simple: regenerate pelet dari layout asli
            self.maze = Maze(MAZE_LAYOUT)
            self._spawn_entities()
            self.power_timer = 0.0

    def _render(self):
        self.screen.fill(SCREEN_BG)
        flick = self.power_timer > 0 and (int(pygame.time.get_ticks() / 200) % 2 == 0)
        # Maze dan item
        maze_surface = pygame.Surface((self.maze.w * TILE_SIZE, self.maze.h * TILE_SIZE))
        maze_surface.set_colorkey((0, 0, 0))
        self.maze.draw(maze_surface, flicker=flick)
        self.screen.blit(maze_surface, (0, 0))
        # Entities
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        # UI Bar
        ui_rect = Rect(0, self.maze.h * TILE_SIZE, self.width, 40)
        pygame.draw.rect(self.screen, (10, 10, 10), ui_rect)
        text = self.font.render(f"Score: {self.score}   Lives: {max(self.lives, 0)}   Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(text, (10, self.maze.h * TILE_SIZE + 10))

        if self.state == 'gameover':
            msg = self.font.render("GAME OVER - Tekan SPACE/ENTER untuk restart", True, (255, 80, 80))
            self.screen.blit(msg, (self.width//2 - msg.get_width()//2, self.height//2 - 10))

        pygame.display.flip()


if __name__ == '__main__':
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
