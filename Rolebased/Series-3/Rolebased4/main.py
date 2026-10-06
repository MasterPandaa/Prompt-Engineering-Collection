import sys
import math
import random
import pygame
from collections import deque

# -----------------------------
# Config
# -----------------------------
TILE_SIZE = 24
FPS = 60
SCREEN_COLS = 28
SCREEN_ROWS = 31
SCREEN_WIDTH = SCREEN_COLS * TILE_SIZE
SCREEN_HEIGHT = SCREEN_ROWS * TILE_SIZE + 48  # extra UI bar

# Colors
BLACK = (0, 0, 0)
NAVY = (10, 10, 40)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
BLUE = (66, 135, 245)
RED = (220, 60, 60)
PINK = (255, 100, 180)
ORANGE = (255, 160, 60)
CYAN = (60, 220, 220)
GREY = (120, 120, 120)

# Ghost states
GHOST_NORMAL = "normal"
GHOST_VULNERABLE = "vulnerable"
GHOST_EATEN = "eaten"

# Directions
DIRS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'STOP': (0, 0),
}
OPPOSITE = {
    'UP': 'DOWN',
    'DOWN': 'UP',
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT',
    'STOP': 'STOP'
}


class Maze:
    def __init__(self):
        # Hardcoded 2D layout: # = wall, . = pellet, o = power, ' ' = empty, P = player start, C = chaser ghost, R = random ghost
        layout = [
            "############################",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#o####.#####.##.#####.####o#",
            "#.####.#####.##.#####.####.#",
            "#..........................#",
            "#.####.##.########.##.####.#",
            "#.####.##.########.##.####.#",
            "#......##....##....##......#",
            "######.##### ## #####.######",
            "     #.##### ## #####.#     ",
            "     #.##          ##.#     ",
            "     #.## ###--### ##.#     ",
            "######.## # C  R # ##.######",
            "      .   #      #   .      ",
            "######.## #      # ##.######",
            "     #.## ######## ##.#     ",
            "     #.##          ##.#     ",
            "     #.## ######## ##.#     ",
            "######.## ######## ##.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#o..##................##..o#",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#..........................#",
            "############################",
            "                            ",
            "            P               ",
            "                            ",
        ]
        self.grid = [list(row) for row in layout]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.pellet_count = 0
        self.power_positions = set()
        self.player_start = None
        self.ghost_starts = []  # list of (x, y, type)
        # parse
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                if ch == '.':
                    self.pellet_count += 1
                elif ch == 'o':
                    self.pellet_count += 1
                    self.power_positions.add((x, y))
                elif ch == 'P':
                    self.player_start = (x, y)
                    self.grid[y][x] = ' '
                elif ch == 'C':
                    self.ghost_starts.append((x, y, 'chaser'))
                    self.grid[y][x] = ' '
                elif ch == 'R':
                    self.ghost_starts.append((x, y, 'random'))
                    self.grid[y][x] = ' '
        # tunnels: allow wrapping when hitting empty on opposite side

    def is_wall(self, gx, gy):
        if gx < 0 or gx >= self.cols or gy < 0 or gy >= self.rows:
            return True
        return self.grid[gy][gx] == '#'

    def has_pellet(self, gx, gy):
        if gx < 0 or gx >= self.cols or gy < 0 or gy >= self.rows:
            return False
        return self.grid[gy][gx] == '.' or self.grid[gy][gx] == 'o'

    def eat_pellet(self, gx, gy):
        if self.grid[gy][gx] == '.':
            self.grid[gy][gx] = ' '
            self.pellet_count -= 1
            return 'pellet'
        if self.grid[gy][gx] == 'o':
            self.grid[gy][gx] = ' '
            self.pellet_count -= 1
            return 'power'
        return None

    def wrap_pos(self, gx, gy):
        # horizontal wrap tunnels through empty spaces in row 10-12 roughly; allow wrap on any empty border
        if gx < 0:
            gx = self.cols - 1
        elif gx >= self.cols:
            gx = 0
        if gy < 0:
            gy = self.rows - 1
        elif gy >= self.rows:
            gy = 0
        return gx, gy

    def draw(self, surface):
        # draw walls
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE + 48, TILE_SIZE, TILE_SIZE)
                cell = self.grid[y][x]
                if cell == '#':
                    pygame.draw.rect(surface, NAVY, rect)
                    pygame.draw.rect(surface, BLUE, rect, 2)
                elif cell == '.' or cell == 'o':
                    # draw pellet
                    color = WHITE
                    r = 3 if cell == '.' else 6
                    pygame.draw.circle(surface, color, rect.center, r)


class Entity:
    def __init__(self, gx, gy, color, speed=4):
        self.gx = gx  # grid x
        self.gy = gy  # grid y
        self.x = gx * TILE_SIZE + TILE_SIZE // 2
        self.y = gy * TILE_SIZE + TILE_SIZE // 2
        self.color = color
        self.dir = 'STOP'
        self.next_dir = 'STOP'
        self.speed = speed  # pixels per frame

    def set_dir(self, d):
        self.next_dir = d

    def grid_pos(self):
        return int(round(self.x / TILE_SIZE)), int(round((self.y - 48) / TILE_SIZE))

    def at_center_of_tile(self):
        cx = self.gx * TILE_SIZE + TILE_SIZE // 2
        cy = self.gy * TILE_SIZE + TILE_SIZE // 2
        return abs(self.x - cx) < 2 and abs(self.y - cy) < 2

    def move_pixels(self, dx, dy):
        self.x += dx
        self.y += dy

    def snap_to_grid(self):
        self.x = self.gx * TILE_SIZE + TILE_SIZE // 2
        self.y = self.gy * TILE_SIZE + TILE_SIZE // 2

    def draw_circle(self, surface, radius=10):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y) + 48), radius)


class Player(Entity):
    def __init__(self, gx, gy):
        super().__init__(gx, gy, YELLOW, speed=4)
        self.lives = 3
        self.score = 0
        self.power_timer = 0

    def update(self, maze: Maze):
        # handle direction changes at tile center when possible
        if self.at_center_of_tile():
            self.gx, self.gy = maze.wrap_pos(self.gx, self.gy)
            if self.next_dir != 'STOP':
                ndx, ndy = DIRS[self.next_dir]
                if not maze.is_wall(self.gx + ndx, self.gy + ndy):
                    self.dir = self.next_dir
            dx, dy = DIRS[self.dir]
            if maze.is_wall(self.gx + dx, self.gy + dy):
                self.dir = 'STOP'
            # update grid if moving
            self.gx += DIRS[self.dir][0]
            self.gy += DIRS[self.dir][1]
            self.snap_to_grid()
        else:
            # continue moving towards center
            dx, dy = DIRS[self.dir]
            self.move_pixels(dx * self.speed, dy * self.speed)

    def eat(self, maze: Maze):
        # eat pellets on current grid
        ate = None
        if maze.has_pellet(self.gx, self.gy):
            kind = maze.eat_pellet(self.gx, self.gy)
            if kind == 'pellet':
                self.score += 10
                ate = 'pellet'
            elif kind == 'power':
                self.score += 50
                ate = 'power'
        return ate

    def draw(self, surface):
        # simple animated mouth using direction
        radius = TILE_SIZE // 2 - 2
        mouth_angle = 30
        dir_angle = {'RIGHT': 0, 'LEFT': 180, 'UP': 90, 'DOWN': 270, 'STOP': 0}[self.dir]
        # Pac-Man body
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y) + 48), radius)
        # simple eye
        eye_offset = {
            'RIGHT': (6, -6),
            'LEFT': (-6, -6),
            'UP': (-6, -6),
            'DOWN': (-6, 6),
            'STOP': (6, -6)
        }[self.dir]
        pygame.draw.circle(surface, BLACK, (int(self.x + eye_offset[0]), int(self.y + 48 + eye_offset[1])), 3)


class Ghost(Entity):
    def __init__(self, gx, gy, kind='chaser', color=RED):
        super().__init__(gx, gy, color, speed=4)
        self.kind = kind  # 'chaser' or 'random'
        self.state = GHOST_NORMAL
        self.vulnerable_timer = 0
        self.home = (gx, gy)
        self.scatter_target = (0, 0)  # unused but could be corners
        self.random_change_cooldown = 0

    def set_vulnerable(self, duration_frames=FPS*7):
        if self.state == GHOST_EATEN:
            return
        self.state = GHOST_VULNERABLE
        self.vulnerable_timer = duration_frames

    def update(self, maze: Maze, player: Player):
        # handle timers
        if self.state == GHOST_VULNERABLE:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.state = GHOST_NORMAL
        # behavior at center of tile
        if self.at_center_of_tile():
            self.gx, self.gy = maze.wrap_pos(self.gx, self.gy)
            self.choose_direction(maze, player)
            # advance one tile then snap
            dx, dy = DIRS[self.dir]
            if not maze.is_wall(self.gx + dx, self.gy + dy):
                self.gx += dx
                self.gy += dy
            self.snap_to_grid()
        else:
            dx, dy = DIRS[self.dir]
            self.move_pixels(dx * self.speed, dy * self.speed)

        # if eaten, go back to home quickly then revive
        if self.state == GHOST_EATEN and self.gx == self.home[0] and self.gy == self.home[1]:
            self.state = GHOST_NORMAL

    def choose_direction(self, maze: Maze, player: Player):
        # Compute valid directions except reverse unless no other choice
        choices = []
        for d, (dx, dy) in DIRS.items():
            if d == 'STOP':
                continue
            if OPPOSITE.get(d) == self.dir and len(choices) > 0:
                continue
            if not maze.is_wall(self.gx + dx, self.gy + dy):
                choices.append(d)
        if not choices:
            self.dir = OPPOSITE.get(self.dir, 'STOP')
            return

        if self.state == GHOST_EATEN:
            # BFS to home
            target = self.home
            self.dir = self._bfs_next_step(maze, target)
            return

        if self.kind == 'random' or (self.state == GHOST_VULNERABLE):
            # random movement; if vulnerable, also random (appears scared)
            self.random_change_cooldown -= 1
            if self.random_change_cooldown <= 0 or self.dir not in choices:
                self.dir = random.choice(choices)
                self.random_change_cooldown = random.randint(8, 18)
            return

        if self.kind == 'chaser':
            if self.state == GHOST_NORMAL:
                # chase player using BFS shortest step
                target = (player.gx, player.gy)
                self.dir = self._bfs_next_step(maze, target)
            elif self.state == GHOST_VULNERABLE:
                # run away: target opposite corner from player
                px, py = player.gx, player.gy
                far = (maze.cols-1-px, maze.rows-1-py)
                self.dir = self._bfs_next_step(maze, far)
            return

        # fallback
        self.dir = random.choice(choices)

    def _bfs_next_step(self, maze: Maze, target):
        start = (self.gx, self.gy)
        if start == target:
            return self.dir if self.dir != 'STOP' else random.choice(['UP','DOWN','LEFT','RIGHT'])
        q = deque([start])
        came = {start: None}
        while q:
            cx, cy = q.popleft()
            if (cx, cy) == target:
                break
            for d in ['UP','DOWN','LEFT','RIGHT']:
                dx, dy = DIRS[d]
                nx, ny = maze.wrap_pos(cx + dx, cy + dy)
                if (nx, ny) in came:
                    continue
                if maze.is_wall(nx, ny):
                    continue
                came[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
        # reconstruct: from target back to start to get first step
        if target not in came:
            # no path, pick random non-wall
            options = []
            for d in ['UP','DOWN','LEFT','RIGHT']:
                dx, dy = DIRS[d]
                if not maze.is_wall(self.gx + dx, self.gy + dy):
                    options.append(d)
            return random.choice(options) if options else 'STOP'
        cur = target
        while came[cur] is not None and came[cur] != start:
            cur = came[cur]
        # cur is neighbor of start
        dx = cur[0] - start[0]
        dy = cur[1] - start[1]
        for d, v in DIRS.items():
            if v == (dx, dy):
                return d
        return self.dir

    def draw(self, surface):
        # color based on state
        color = self.color
        if self.state == GHOST_VULNERABLE:
            color = BLUE
        elif self.state == GHOST_EATEN:
            color = GREY
        pygame.draw.circle(surface, color, (int(self.x), int(self.y) + 48), TILE_SIZE//2 - 4)
        # eyes
        eye_col = WHITE if self.state != GHOST_VULNERABLE else (230, 230, 255)
        pygame.draw.circle(surface, eye_col, (int(self.x-4), int(self.y+48-4)), 3)
        pygame.draw.circle(surface, eye_col, (int(self.x+4), int(self.y+48-4)), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman Clone - Cascade")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)

        self.maze = Maze()
        ps = self.maze.player_start or (14, 29)
        self.player = Player(*ps)
        # ghosts
        self.ghosts = []
        if self.maze.ghost_starts:
            for x, y, kind in self.maze.ghost_starts:
                color = RED if kind == 'chaser' else PINK
                self.ghosts.append(Ghost(x, y, kind=kind, color=color))
        else:
            # fallback positions
            self.ghosts.append(Ghost(13, 13, 'chaser', RED))
            self.ghosts.append(Ghost(14, 13, 'random', PINK))

        self.state = 'playing'  # playing, win, gameover
        self.power_duration = FPS * 7

    def reset_round(self, death=False):
        ps = self.maze.player_start or (14, 29)
        self.player.gx, self.player.gy = ps
        self.player.snap_to_grid()
        self.player.dir = 'STOP'
        for g in self.ghosts:
            g.gx, g.gy = g.home
            g.snap_to_grid()
            g.state = GHOST_NORMAL
            g.dir = 'STOP'
        if death:
            pygame.time.delay(800)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.state in ('win', 'gameover'):
                    if event.key == pygame.K_RETURN:
                        # restart full game
                        self.__init__()
                        return
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.player.set_dir('UP')
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.player.set_dir('DOWN')
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.player.set_dir('LEFT')
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.player.set_dir('RIGHT')

    def update(self):
        if self.state != 'playing':
            return
        self.player.update(self.maze)
        ate = self.player.eat(self.maze)
        if ate == 'power':
            for g in self.ghosts:
                g.set_vulnerable(self.power_duration)

        # ghosts update
        for g in self.ghosts:
            g.update(self.maze, self.player)

        # collisions
        for g in self.ghosts:
            if abs(g.x - self.player.x) < 12 and abs(g.y - self.player.y) < 12:
                if g.state == GHOST_VULNERABLE:
                    # eat ghost
                    g.state = GHOST_EATEN
                    self.player.score += 200
                elif g.state == GHOST_NORMAL:
                    # player dies
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = 'gameover'
                    self.reset_round(death=True)
                    break

        if self.maze.pellet_count <= 0:
            self.state = 'win'

    def draw_ui(self):
        # top bar background
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 48))
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(score_text, (12, 12))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 12))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_ui()
        self.maze.draw(self.screen)
        # draw entities
        self.player.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)

        if self.state in ('win', 'gameover'):
            msg = 'YOU WIN! Press Enter to Restart' if self.state == 'win' else 'GAME OVER - Press Enter to Restart'
            text = self.big_font.render(msg, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, 24))
            self.screen.blit(text, rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
