import pygame
import sys
import random
from collections import deque

# =============================
# Constants and Configuration
# =============================
TILE_SIZE = 24
GRID_WIDTH = 28
GRID_HEIGHT = 31
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + 60  # extra space for UI
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
YELLOW = (255, 204, 0)
WHITE = (255, 255, 255)
RED = (255, 51, 51)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (180, 180, 180)
NAVY = (12, 12, 75)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
    STOP: STOP,
}

# Speeds (pixels per frame)
PACMAN_SPEED = 2
GHOST_SPEED = 2
FRIGHTENED_SPEED = 1

POWER_DURATION = 6.0  # seconds of frightened mode
RESPAWN_TIME = 3.0    # ghost re-entry after being eaten

# =============================
# Maze Layout (28 x 31) similar to Pac-Man, simplified
# Legend:
#   '#': wall
#   '.': pellet
#   'o': power pellet
#   ' ': empty path
#   'G': ghost house door (treated as path for ghosts only)
# =============================
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
    "     #.## ###GG### ##.#     ",
    "######.## #      # ##.######",
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
    "                            ",
    "                            ",
]

# Ensure layout dimensions
assert len(MAZE_LAYOUT) == GRID_HEIGHT, "MAZE_LAYOUT height mismatch"
for row in MAZE_LAYOUT:
    assert len(row) == GRID_WIDTH, "MAZE_LAYOUT width mismatch"


def grid_to_pixel(grid_pos):
    gx, gy = grid_pos
    return gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2


def pixel_to_grid(px, py):
    return px // TILE_SIZE, py // TILE_SIZE


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.pellets = set()
        self.power_pellets = set()
        self.walls = set()
        self.ghost_door = set()
        self.parse_layout()

    def parse_layout(self):
        for y, line in enumerate(self.layout):
            for x, ch in enumerate(line):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))
                elif ch == 'G':
                    self.ghost_door.add((x, y))
        # Tunnels: wrap from left to right at specific rows
        self.tunnels = [(0, 14), (27, 14), (0, 10), (27, 10)]

    def is_wall(self, grid_pos):
        return grid_pos in self.walls

    def is_ghost_door(self, grid_pos):
        return grid_pos in self.ghost_door

    def valid_move(self, grid_pos, for_ghost=False):
        if grid_pos in self.walls:
            return False
        # Ghost door can be crossed by ghosts, not by player
        if (not for_ghost) and grid_pos in self.ghost_door:
            return False
        x, y = grid_pos
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT - 3  # avoid UI rows

    def draw(self, surface):
        surface.fill(BLACK)
        # Draw walls
        for (x, y) in self.walls:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, NAVY, rect)
            pygame.draw.rect(surface, BLUE, rect, 2)
        # Draw pellets
        for (x, y) in self.pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, WHITE, (cx, cy), 3)
        # Draw power pellets
        for (x, y) in self.power_pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, WHITE, (cx, cy), 8, 2)

    def eat_pellet_at(self, grid_pos):
        if grid_pos in self.pellets:
            self.pellets.remove(grid_pos)
            return 10
        return 0

    def eat_power_pellet_at(self, grid_pos):
        if grid_pos in self.power_pellets:
            self.power_pellets.remove(grid_pos)
            return 50
        return 0

    def pellets_remaining(self):
        return len(self.pellets) + len(self.power_pellets)

    def neighbors(self, pos, for_ghost=False):
        x, y = pos
        options = [(x + dx, y + dy) for dx, dy in [UP, DOWN, LEFT, RIGHT]]
        valid = []
        for o in options:
            if self.valid_move(o, for_ghost=for_ghost):
                valid.append(o)
        return valid

    def shortest_next_step(self, start, goal, for_ghost=False):
        # BFS to get the next step towards goal
        if start == goal:
            return start
        q = deque([start])
        came_from = {start: None}
        while q:
            cur = q.popleft()
            for nb in self.neighbors(cur, for_ghost=for_ghost):
                if nb not in came_from:
                    came_from[nb] = cur
                    if nb == goal:
                        q.clear()
                        break
                    q.append(nb)
        if goal not in came_from:
            return start
        # reconstruct first step
        cur = goal
        while came_from[cur] != start:
            cur = came_from[cur]
            if cur is None:
                break
        return cur


class Entity:
    def __init__(self, maze, grid_pos):
        self.maze = maze
        self.grid_pos = grid_pos
        self.pixel_pos = list(grid_to_pixel(grid_pos))
        self.direction = STOP
        self.speed = 2

    def update_pixel(self):
        self.pixel_pos[0] = self.grid_pos[0] * TILE_SIZE + TILE_SIZE // 2
        self.pixel_pos[1] = self.grid_pos[1] * TILE_SIZE + TILE_SIZE // 2

    def at_center_of_tile(self):
        cx, cy = grid_to_pixel(self.grid_pos)
        return abs(self.pixel_pos[0] - cx) < 1 and abs(self.pixel_pos[1] - cy) < 1

    def draw(self, surface):
        pass


class Player(Entity):
    def __init__(self, maze, grid_pos):
        super().__init__(maze, grid_pos)
        self.speed = PACMAN_SPEED
        self.next_direction = STOP
        self.lives = 3
        self.alive = True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = RIGHT

    def try_change_direction(self):
        if self.next_direction == STOP:
            return
        nx = self.grid_pos[0] + self.next_direction[0]
        ny = self.grid_pos[1] + self.next_direction[1]
        if self.maze.valid_move((nx, ny), for_ghost=False):
            self.direction = self.next_direction

    def move(self):
        # Tunnel wrapping
        if self.grid_pos in [(0, 14), (0, 10)] and self.direction == LEFT:
            self.grid_pos = (GRID_WIDTH - 1, self.grid_pos[1])
            self.update_pixel()
        if self.grid_pos in [(GRID_WIDTH - 1, 14), (GRID_WIDTH - 1, 10)] and self.direction == RIGHT:
            self.grid_pos = (0, self.grid_pos[1])
            self.update_pixel()

        # Only change direction at tile centers
        if self.at_center_of_tile():
            self.try_change_direction()
            nx = self.grid_pos[0] + self.direction[0]
            ny = self.grid_pos[1] + self.direction[1]
            if self.maze.valid_move((nx, ny), for_ghost=False):
                self.grid_pos = (nx, ny)
                self.update_pixel()
            else:
                self.direction = STOP

    def update(self):
        self.handle_input()
        self.move()

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, self.pixel_pos, TILE_SIZE // 2 - 2)


class Ghost(Entity):
    NORMAL = 'normal'
    FRIGHTENED = 'frightened'
    EATEN = 'eaten'

    def __init__(self, maze, grid_pos, color=RED, home=(13, 13)):
        super().__init__(maze, grid_pos)
        self.base_speed = GHOST_SPEED
        self.speed = self.base_speed
        self.color = color
        self.state = Ghost.NORMAL
        self.frightened_timer = 0.0
        self.respawn_timer = 0.0
        self.home = home
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def set_frightened(self):
        if self.state == Ghost.EATEN:
            return
        self.state = Ghost.FRIGHTENED
        self.frightened_timer = POWER_DURATION
        self.speed = FRIGHTENED_SPEED

    def update_state(self, dt):
        if self.state == Ghost.FRIGHTENED:
            self.frightened_timer -= dt
            if self.frightened_timer <= 0:
                self.state = Ghost.NORMAL
                self.speed = self.base_speed
        elif self.state == Ghost.EATEN:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.grid_pos = self.home
                self.update_pixel()
                self.state = Ghost.NORMAL
                self.speed = self.base_speed

    def move(self):
        # Tunnel wrapping
        if self.grid_pos in [(0, 14), (0, 10)] and self.direction == LEFT:
            self.grid_pos = (GRID_WIDTH - 1, self.grid_pos[1])
            self.update_pixel()
        if self.grid_pos in [(GRID_WIDTH - 1, 14), (GRID_WIDTH - 1, 10)] and self.direction == RIGHT:
            self.grid_pos = (0, self.grid_pos[1])
            self.update_pixel()

        if self.at_center_of_tile():
            self.choose_direction()
            nx = self.grid_pos[0] + self.direction[0]
            ny = self.grid_pos[1] + self.direction[1]
            if self.maze.valid_move((nx, ny), for_ghost=True):
                self.grid_pos = (nx, ny)
                self.update_pixel()
            else:
                # try any valid direction
                options = [d for d in [UP, DOWN, LEFT, RIGHT]
                           if self.maze.valid_move((self.grid_pos[0] + d[0], self.grid_pos[1] + d[1]), for_ghost=True)]
                if options:
                    self.direction = random.choice(options)

    def choose_direction(self):
        # Overridden by subclasses
        pass

    def draw(self, surface):
        color = self.color
        if self.state == Ghost.FRIGHTENED:
            color = BLUE
        elif self.state == Ghost.EATEN:
            color = GREY
        pygame.draw.circle(surface, color, self.pixel_pos, TILE_SIZE // 2 - 2)


class ChaserGhost(Ghost):
    def __init__(self, maze, grid_pos, color=RED, home=(13, 13)):
        super().__init__(maze, grid_pos, color, home)

    def choose_direction(self, target=None):
        if self.state == Ghost.EATEN:
            target = self.home
        if target is None:
            # default: keep moving
            return
        # Avoid reversing direction unless necessary
        candidates = []
        for d in [UP, DOWN, LEFT, RIGHT]:
            if d == OPPOSITE.get(self.direction, STOP):
                continue
            nx = self.grid_pos[0] + d[0]
            ny = self.grid_pos[1] + d[1]
            if self.maze.valid_move((nx, ny), for_ghost=True):
                candidates.append((d, (nx, ny)))
        if not candidates:
            # allow reversal if stuck
            for d in [UP, DOWN, LEFT, RIGHT]:
                nx = self.grid_pos[0] + d[0]
                ny = self.grid_pos[1] + d[1]
                if self.maze.valid_move((nx, ny), for_ghost=True):
                    candidates.append((d, (nx, ny)))
        # Choose the neighbor that is next step on shortest path towards target
        best_dir = self.direction
        best_dist = 1e9
        for d, np_ in candidates:
            next_step = self.maze.shortest_next_step(np_, target, for_ghost=True)
            dist = abs(next_step[0] - target[0]) + abs(next_step[1] - target[1])
            if dist < best_dist:
                best_dist = dist
                best_dir = d
        self.direction = best_dir


class RandomGhost(Ghost):
    def __init__(self, maze, grid_pos, color=PINK, home=(14, 13)):
        super().__init__(maze, grid_pos, color, home)

    def choose_direction(self):
        # At intersections, choose random non-reversing direction
        options = []
        for d in [UP, DOWN, LEFT, RIGHT]:
            if d == OPPOSITE.get(self.direction, STOP):
                continue
            nx = self.grid_pos[0] + d[0]
            ny = self.grid_pos[1] + d[1]
            if self.maze.valid_move((nx, ny), for_ghost=True):
                options.append(d)
        if options:
            self.direction = random.choice(options)
        else:
            # if dead-end, allow reverse
            options = []
            for d in [UP, DOWN, LEFT, RIGHT]:
                nx = self.grid_pos[0] + d[0]
                ny = self.grid_pos[1] + d[1]
                if self.maze.valid_move((nx, ny), for_ghost=True):
                    options.append(d)
            if options:
                self.direction = random.choice(options)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Pacman Clone - OOP')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 36, bold=True)

        self.maze = Maze(MAZE_LAYOUT)
        self.player = Player(self.maze, (13, 23))
        self.ghosts = [
            ChaserGhost(self.maze, (13, 11), RED, home=(13, 13)),
            RandomGhost(self.maze, (14, 11), PINK, home=(14, 13)),
        ]

        self.score = 0
        self.game_over = False
        self.win = False

    def reset_level(self):
        self.player.grid_pos = (13, 23)
        self.player.update_pixel()
        self.player.direction = STOP
        for g in self.ghosts:
            g.grid_pos = g.home
            g.update_pixel()
            g.direction = random.choice([UP, DOWN, LEFT, RIGHT])
            g.state = Ghost.NORMAL
            g.speed = g.base_speed
            g.frightened_timer = 0.0
            g.respawn_timer = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over or self.win:
                    if event.key == pygame.K_SPACE:
                        self.__init__()

    def update(self, dt):
        if self.game_over or self.win:
            return

        self.player.update()

        # Eat pellets
        gained = self.maze.eat_pellet_at(self.player.grid_pos)
        if gained:
            self.score += gained
        gained = self.maze.eat_power_pellet_at(self.player.grid_pos)
        if gained:
            self.score += gained
            for g in self.ghosts:
                g.set_frightened()

        # Ghosts logic
        for g in self.ghosts:
            # Determine target for chaser
            if isinstance(g, ChaserGhost):
                target = self.player.grid_pos if g.state != Ghost.FRIGHTENED else (0, 0)
                g.choose_direction(target=target)
            g.update_state(dt)
            g.move()

        # Collisions
        for g in self.ghosts:
            if g.grid_pos == self.player.grid_pos:
                if g.state == Ghost.FRIGHTENED:
                    # eat ghost
                    self.score += 200
                    g.state = Ghost.EATEN
                    g.respawn_timer = RESPAWN_TIME
                    g.speed = FRIGHTENED_SPEED
                elif g.state == Ghost.NORMAL:
                    # lose life
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_level()
                    break

        if self.maze.pellets_remaining() == 0:
            self.win = True

    def draw_ui(self):
        ui_rect = pygame.Rect(0, GRID_HEIGHT * TILE_SIZE, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, BLACK, ui_rect)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(score_text, (10, GRID_HEIGHT * TILE_SIZE + 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, GRID_HEIGHT * TILE_SIZE + 10))

        if self.game_over:
            msg = self.big_font.render("GAME OVER - Press SPACE", True, ORANGE)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        elif self.win:
            msg = self.big_font.render("YOU WIN! - Press SPACE", True, CYAN)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

    def draw(self):
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == '__main__':
    Game().run()
