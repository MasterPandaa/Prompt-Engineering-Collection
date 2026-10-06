import sys
import math
import random
import pygame
from pygame import Rect

# -----------------------------
# Config
# -----------------------------
CELL = 24
FPS = 60
POWER_DURATION = 8.0  # seconds
GHOST_RESPAWN_TIME = 3.0
PLAYER_SPEED = 2.0    # pixels per frame
GHOST_SPEED = 1.8
FRIGHT_SPEED = 1.2

# Colors
BLACK = (0, 0, 0)
NAVY = (0, 0, 80)
WHITE = (255, 255, 255)
YELLOW = (255, 225, 0)
RED = (230, 0, 0)
PINK = (255, 100, 150)
CYAN = (0, 220, 220)
ORANGE = (255, 170, 0)
BLUE = (50, 100, 255)
GREY = (100, 100, 100)

# -----------------------------
# Maze layout
# Legend: # wall, . pellet, o power pellet, P player, G ghost spawn, ' ' empty
# -----------------------------
MAZE_LAYOUT = [
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
    "######.## ###GG### ##.######",
    "       .   #GGGG#   .       ",
    "######.## ######## ##.######",
    "     #.##    PP    ##.#     ",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

# Clean layout width consistency
WIDTH_COLS = max(len(row) for row in MAZE_LAYOUT)
MAZE_LAYOUT = [row.ljust(WIDTH_COLS) for row in MAZE_LAYOUT]
ROWS = len(MAZE_LAYOUT)
COLS = WIDTH_COLS
SCREEN_W = COLS * CELL
SCREEN_H = ROWS * CELL


def grid_to_px(col, row):
    return col * CELL + CELL // 2, row * CELL + CELL // 2


def rect_for_cell(col, row):
    return Rect(col * CELL, row * CELL, CELL, CELL)


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.player_starts = []
        self.ghost_spawns = []
        self.parse_layout()

    def parse_layout(self):
        for r, row in enumerate(self.layout):
            for c, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((c, r))
                elif ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power_pellets.add((c, r))
                elif ch == 'P':
                    self.player_starts.append((c, r))
                elif ch == 'G':
                    self.ghost_spawns.append((c, r))

    def draw(self, surf):
        # Fill background
        surf.fill(BLACK)
        # Draw walls
        for (c, r) in self.walls:
            rect = rect_for_cell(c, r)
            pygame.draw.rect(surf, NAVY, rect)
            # wall inner outline
            pygame.draw.rect(surf, BLUE, rect, 2)
        # Draw pellets
        for (c, r) in self.pellets:
            x, y = grid_to_px(c, r)
            pygame.draw.circle(surf, WHITE, (x, y), 3)
        # Draw power pellets
        for (c, r) in self.power_pellets:
            x, y = grid_to_px(c, r)
            pygame.draw.circle(surf, WHITE, (x, y), 7, width=2)

    def is_wall(self, col, row):
        return (col, row) in self.walls

    def wrap_col(self, col):
        if col < 0:
            return COLS - 1
        if col >= COLS:
            return 0
        return col


DIRS = {
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
}
ORDERED_DIRS = ['LEFT', 'RIGHT', 'UP', 'DOWN']


def opposite(dir_name):
    if dir_name == 'LEFT':
        return 'RIGHT'
    if dir_name == 'RIGHT':
        return 'LEFT'
    if dir_name == 'UP':
        return 'DOWN'
    if dir_name == 'DOWN':
        return 'UP'
    return None


class Entity:
    def __init__(self, x, y, color, radius):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.radius = radius
        self.dir = 'LEFT'
        self.next_dir = None

    def grid_pos(self):
        return int(self.x // CELL), int(self.y // CELL)

    def center_to_grid(self):
        return int(self.x / CELL), int(self.y / CELL)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW, CELL // 2 - 2)
        self.alive = True
        self.score = 0
        self.lives = 3

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.next_dir = 'LEFT'
        elif keys[pygame.K_RIGHT]:
            self.next_dir = 'RIGHT'
        elif keys[pygame.K_UP]:
            self.next_dir = 'UP'
        elif keys[pygame.K_DOWN]:
            self.next_dir = 'DOWN'

    def can_move(self, maze, dir_name):
        dx, dy = DIRS[dir_name]
        # Look slightly ahead from center to edge
        next_x = self.x + dx * PLAYER_SPEED
        next_y = self.y + dy * PLAYER_SPEED
        # Compute tile we are moving into based on destination position
        target_col = int(next_x // CELL)
        target_row = int(next_y // CELL)
        target_col = maze.wrap_col(target_col)
        if maze.is_wall(target_col, target_row):
            return False
        return True

    def update(self, maze):
        self.handle_input()
        # Try to switch direction if possible (without overshoot)
        if self.next_dir and self.next_dir != self.dir:
            if self.can_move(maze, self.next_dir):
                # Align to grid when turning
                gc, gr = self.grid_pos()
                self.x = gc * CELL + CELL / 2
                self.y = gr * CELL + CELL / 2
                self.dir = self.next_dir
        # Move if possible
        if self.can_move(maze, self.dir):
            dx, dy = DIRS[self.dir]
            self.x += dx * PLAYER_SPEED
            self.y += dy * PLAYER_SPEED
        # Tunnel wrap horizontally
        if self.x < 0:
            self.x = SCREEN_W - 1
        elif self.x >= SCREEN_W:
            self.x = 1

    def eat(self, maze):
        col, row = self.grid_pos()
        # Wrap col for pellets
        col = maze.wrap_col(col)
        ate_power = False
        if (col, row) in maze.pellets:
            maze.pellets.remove((col, row))
            self.score += 10
        if (col, row) in maze.power_pellets:
            maze.power_pellets.remove((col, row))
            self.score += 50
            ate_power = True
        return ate_power


class Ghost(Entity):
    def __init__(self, x, y, color, name):
        super().__init__(x, y, color, CELL // 2 - 3)
        self.name = name
        self.spawn = (x, y)
        self.state = 'CHASE'  # CHASE or FRIGHT or EATEN
        self.fright_time = 0.0
        self.respawn_timer = 0.0

    def speed(self):
        if self.state == 'FRIGHT':
            return FRIGHT_SPEED
        elif self.state == 'EATEN':
            return GHOST_SPEED * 1.6
        return GHOST_SPEED

    def at_center_of_cell(self):
        # consider near center to allow turning
        cx = (self.x % CELL) - CELL / 2
        cy = (self.y % CELL) - CELL / 2
        return abs(cx) < 1.5 and abs(cy) < 1.5

    def available_dirs(self, maze):
        # Return available directions excluding walls
        dirs = []
        gc, gr = int(self.x // CELL), int(self.y // CELL)
        gc = maze.wrap_col(gc)
        for name, (dx, dy) in DIRS.items():
            if opposite(self.dir) == name:
                continue
            nc, nr = gc + dx, gr + dy
            nc = maze.wrap_col(nc)
            if not maze.is_wall(nc, nr):
                dirs.append(name)
        return dirs

    def choose_dir(self, maze, target=None):
        # Simple logic: random at intersections; if target provided, pick direction that reduces distance
        dirs = self.available_dirs(maze)
        if not dirs:
            return opposite(self.dir) or self.dir
        if self.state == 'FRIGHT' or target is None:
            return random.choice(dirs)
        # Greedy choice towards target
        best = None
        best_d = 1e9
        for name in dirs:
            dx, dy = DIRS[name]
            nx = self.x + dx * CELL
            ny = self.y + dy * CELL
            d = (nx - target[0]) ** 2 + (ny - target[1]) ** 2
            if d < best_d:
                best_d = d
                best = name
        return best or random.choice(dirs)

    def update(self, maze, player, dt):
        if self.state == 'FRIGHT':
            self.fright_time -= dt
            if self.fright_time <= 0:
                self.state = 'CHASE'
                self.color = self.base_color
        elif self.state == 'EATEN':
            # Move back to spawn, then respawn timer
            sx, sy = self.spawn
            if math.hypot(self.x - sx, self.y - sy) < 2.0:
                self.respawn_timer -= dt
                if self.respawn_timer <= 0:
                    self.state = 'CHASE'
                    self.color = self.base_color
            # continue moving towards spawn
        # Decide direction at intersections
        if self.at_center_of_cell():
            target = (player.x, player.y) if self.state == 'CHASE' else None
            self.dir = self.choose_dir(maze, target)
            # Snap to center to avoid drift
            gc, gr = int(self.x // CELL), int(self.y // CELL)
            self.x = gc * CELL + CELL / 2
            self.y = gr * CELL + CELL / 2
        # Move
        dx, dy = DIRS[self.dir]
        spd = self.speed()
        self.x += dx * spd
        self.y += dy * spd
        # Wrap
        if self.x < 0:
            self.x = SCREEN_W - 1
        elif self.x >= SCREEN_W:
            self.x = 1

    def frighten(self, duration):
        if self.state != 'EATEN':
            self.state = 'FRIGHT'
            self.fright_time = duration
            self.color = BLUE

    def eaten(self):
        self.state = 'EATEN'
        self.color = GREY
        self.respawn_timer = GHOST_RESPAWN_TIME

    @property
    def base_color(self):
        # base color encoded in name
        if self.name == 'blinky':
            return RED
        if self.name == 'pinky':
            return PINK
        if self.name == 'inky':
            return CYAN
        if self.name == 'clyde':
            return ORANGE
        return WHITE


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman - Pygame')
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.bigfont = pygame.font.SysFont('arial', 42, bold=True)

        self.maze = Maze(MAZE_LAYOUT)
        self.player = None
        self.ghosts = []
        self.state = 'PLAY'  # PLAY, POWER, GAMEOVER, WIN
        self.power_timer = 0.0

        self.reset()

    def reset(self):
        # Player start
        if self.maze.player_starts:
            pc, pr = self.maze.player_starts[0]
        else:
            # fallback center
            pc, pr = COLS // 2, ROWS // 2
        px, py = grid_to_px(pc, pr)
        self.player = Player(px, py)
        # Ghosts
        self.ghosts = []
        spawns = self.maze.ghost_spawns or [(COLS // 2, ROWS // 2)] * 4
        colors = [('blinky', RED), ('pinky', PINK), ('inky', CYAN), ('clyde', ORANGE)]
        for (name, base_col), (gc, gr) in zip(colors, spawns[:4]):
            gx, gy = grid_to_px(gc, gr)
            g = Ghost(gx, gy, base_col, name)
            g.color = base_col
            g.dir = random.choice(['LEFT', 'RIGHT'])
            self.ghosts.append(g)
        self.state = 'PLAY'
        self.power_timer = 0.0

    def set_power_mode(self):
        self.state = 'POWER'
        self.power_timer = POWER_DURATION
        for g in self.ghosts:
            g.frighten(POWER_DURATION)

    def update(self, dt):
        if self.state in ('GAMEOVER', 'WIN'):
            return
        # Update player
        self.player.update(self.maze)
        ate_power = self.player.eat(self.maze)
        if ate_power:
            self.set_power_mode()
        # Update power timer
        if self.state == 'POWER':
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.state = 'PLAY'
        # Update ghosts
        for g in self.ghosts:
            g.update(self.maze, self.player, dt)
        # Collisions
        self.handle_collisions()
        # Win condition
        if not self.maze.pellets and not self.maze.power_pellets:
            self.state = 'WIN'

    def handle_collisions(self):
        for g in self.ghosts:
            if math.hypot(self.player.x - g.x, self.player.y - g.y) < CELL * 0.45:
                if g.state == 'FRIGHT':
                    g.eaten()
                    self.player.score += 200
                elif g.state != 'EATEN':
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = 'GAMEOVER'
                        return
                    # Reset positions
                    self.reset_positions_after_death()
                    return

    def reset_positions_after_death(self):
        # Reset player position to start and ghosts to spawn
        if self.maze.player_starts:
            pc, pr = self.maze.player_starts[0]
            self.player.x, self.player.y = grid_to_px(pc, pr)
        for g, (gc, gr) in zip(self.ghosts, self.maze.ghost_spawns):
            g.x, g.y = grid_to_px(gc, gr)
            g.state = 'CHASE'
            g.color = g.base_color
            g.dir = random.choice(['LEFT', 'RIGHT'])

    def draw_hud(self):
        score_s = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_s = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(score_s, (8, 4))
        self.screen.blit(lives_s, (SCREEN_W - lives_s.get_width() - 8, 4))

    def draw(self):
        self.maze.draw(self.screen)
        # Draw ghosts then player on top
        for g in self.ghosts:
            g.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()
        if self.state == 'GAMEOVER':
            txt = self.bigfont.render('GAME OVER - Press R', True, WHITE)
            self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 - 20))
        elif self.state == 'WIN':
            txt = self.bigfont.render('YOU WIN! - Press R', True, YELLOW)
            self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 - 20))

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if e.key == pygame.K_r and self.state in ('GAMEOVER', 'WIN'):
                    # Reset the whole game (keep score?) -> reset maze pellets too by re-parsing
                    self.__init__()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == '__main__':
    Game().run()
