import sys
import random
import math
import pygame
from typing import List, Tuple, Optional

# -----------------------------
# Constants
# -----------------------------
TILE_SIZE = 24
FPS = 60
MAZE_ROWS = 23
MAZE_COLS = 21
SCREEN_WIDTH = MAZE_COLS * TILE_SIZE
SCREEN_HEIGHT = (MAZE_ROWS * TILE_SIZE) + 40  # extra UI area
UI_HEIGHT = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 222)
YELLOW = (255, 207, 0)
RED = (222, 33, 33)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
NAVY = (12, 12, 64)
GREY = (180, 180, 180)
VULNERABLE_BLUE = (33, 144, 255)

# Movement
SPEED_PIXELS = 2  # pixels per frame for player
GHOST_SPEED = 2
VULNERABLE_SPEED = 1
POWER_DURATION = 8.0  # seconds
RESPAWN_TIME = 3.0

# Maze legend
# # = wall
# . = pellet
# o = power pellet
# ' ' = empty

MAZE_LAYOUT = [
    "#####################",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#o###.###.#.###.###o#",
    "#.###.###.#.###.###.#",
    "#...................#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#####.### # ###.#####",
    "    #.#   G   #.#    ",
    "#####.# ##-## #.#####",
    "     .  #123#  .     ",
    "#####.# ##### #.#####",
    "    #.#       #.#    ",
    "#####.# ##### #.#####",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#o..#.....P.....#..o#",
    "###.#.#.#####.#.#.###",
    "#.....#...#...#.....#",
    "#.#######.#.#######.#",
    "#...................#",
    "#####################",
]


def grid_to_pixel(cell: Tuple[int, int]) -> Tuple[int, int]:
    r, c = cell
    return c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT


def pixel_to_grid(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = pos
    c = x // TILE_SIZE
    r = (y - UI_HEIGHT) // TILE_SIZE
    return int(r), int(c)


class Maze:
    def __init__(self, layout: List[str]):
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.grid = [list(row) for row in layout]
        self.pellet_count = sum(row.count('.') for row in layout) + sum(row.count('o') for row in layout)

    def is_wall(self, r: int, c: int) -> bool:
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return True
        return self.grid[r][c] == '#'

    def is_junction(self, r: int, c: int) -> bool:
        # A simple junction detection: count available non-wall neighbors
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        open_neighbors = 0
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.is_wall(nr, nc):
                open_neighbors += 1
        return open_neighbors >= 3

    def eat_pellet(self, r: int, c: int) -> Optional[str]:
        # returns '.' or 'o' if eaten, else None
        if self.grid[r][c] in ('.', 'o'):
            ch = self.grid[r][c]
            self.grid[r][c] = ' '
            self.pellet_count -= 1
            return ch
        return None

    def draw(self, surface: pygame.Surface):
        # draw background
        surface.fill(NAVY)
        # draw walls and pellets
        for r in range(self.rows):
            for c in range(self.cols):
                ch = self.grid[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE + UI_HEIGHT
                if ch == '#':
                    pygame.draw.rect(surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE), border_radius=4)
                elif ch == '.':
                    pygame.draw.circle(surface, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 3)
                elif ch == 'o':
                    pygame.draw.circle(surface, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 6, 2)


class Entity:
    def __init__(self, maze: Maze, row: int, col: int):
        self.maze = maze
        self.row = row
        self.col = col
        self.x, self.y = grid_to_pixel((row, col))
        self.dir = (0, 0)  # current dir vector in grid units
        self.next_dir = (0, 0)

    def at_center_of_tile(self) -> bool:
        cx, cy = grid_to_pixel((self.row, self.col))
        return abs(self.x - cx) < 2 and abs(self.y - cy) < 2

    def align_to_center(self):
        self.x, self.y = grid_to_pixel((self.row, self.col))

    def set_dir(self, d: Tuple[int, int]):
        self.next_dir = d

    def can_move(self, d: Tuple[int, int]) -> bool:
        r, c = self.row + d[0], self.col + d[1]
        return not self.maze.is_wall(r, c)

    def move_pixels(self, speed: int):
        self.x += self.dir[1] * speed
        self.y += self.dir[0] * speed
        # wrap tunnel horizontally
        if self.x < -TILE_SIZE//2:
            self.x = SCREEN_WIDTH + TILE_SIZE//2
        elif self.x > SCREEN_WIDTH + TILE_SIZE//2:
            self.x = -TILE_SIZE//2
        # update grid coords when crossing centers
        new_row, new_col = pixel_to_grid((self.x, self.y))
        if 0 <= new_row < self.maze.rows and 0 <= new_col < self.maze.cols:
            self.row, self.col = new_row, new_col

    def draw(self, surface: pygame.Surface):
        pass


class Player(Entity):
    def __init__(self, maze: Maze, row: int, col: int):
        super().__init__(maze, row, col)
        self.lives = 3
        self.score = 0
        self.power_timer = 0.0
        self.radius = TILE_SIZE // 2 - 2

    def update(self, dt: float):
        # handle direction changes at tile centers
        if self.at_center_of_tile():
            # try to take the queued direction if possible
            if self.next_dir != self.dir and self.can_move(self.next_dir):
                self.dir = self.next_dir
            # if current direction blocked, stop
            if not self.can_move(self.dir):
                self.dir = (0, 0)
            self.align_to_center()
        self.move_pixels(SPEED_PIXELS)

        # pellet consumption
        if 0 <= self.row < self.maze.rows and 0 <= self.col < self.maze.cols:
            eaten = self.maze.eat_pellet(self.row, self.col)
            if eaten == '.':
                self.score += 10
            elif eaten == 'o':
                self.score += 50
                self.power_timer = POWER_DURATION

        # power timer countdown
        if self.power_timer > 0:
            self.power_timer = max(0.0, self.power_timer - dt)

    def is_powered(self) -> bool:
        return self.power_timer > 0

    def draw(self, surface: pygame.Surface):
        color = YELLOW
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)


class Ghost(Entity):
    NORMAL = 'normal'
    VULNERABLE = 'vulnerable'
    EATEN = 'eaten'  # returning to house

    def __init__(self, maze: Maze, row: int, col: int, color: Tuple[int, int, int]):
        super().__init__(maze, row, col)
        self.base_color = color
        self.state = Ghost.NORMAL
        self.radius = TILE_SIZE // 2 - 2
        self.respawn_timer = 0.0
        self.home = (row, col)

    def speed(self) -> int:
        if self.state == Ghost.VULNERABLE:
            return VULNERABLE_SPEED
        return GHOST_SPEED

    def set_vulnerable(self):
        if self.state != Ghost.EATEN:
            self.state = Ghost.VULNERABLE

    def eaten(self):
        self.state = Ghost.EATEN
        self.respawn_timer = RESPAWN_TIME

    def update(self, dt: float, player: Player):
        # manage eaten state respawn
        if self.state == Ghost.EATEN:
            # simple return to home behavior
            if self.at_center_of_tile():
                target = self.home
                self.dir = self.choose_dir_towards(target)
                if (self.row, self.col) == self.home:
                    # respawn to normal
                    self.state = Ghost.NORMAL
            self.move_pixels(self.speed())
            if self.respawn_timer > 0:
                self.respawn_timer = max(0.0, self.respawn_timer - dt)
            return

        # choose direction at junctions or tile center
        if self.at_center_of_tile():
            self.align_to_center()
            self.dir = self.choose_direction(player)
        self.move_pixels(self.speed())

    def neighbors(self) -> List[Tuple[int, int]]:
        options = []
        for d in [(1,0), (-1,0), (0,1), (0,-1)]:
            if not self.maze.is_wall(self.row + d[0], self.col + d[1]):
                options.append(d)
        return options

    def choose_dir_towards(self, target: Tuple[int, int]) -> Tuple[int, int]:
        best = (0, 0)
        best_dist = 1e9
        for d in self.neighbors():
            # avoid reversing unless forced
            if (-d[0], -d[1]) == self.dir and len(self.neighbors()) > 1:
                continue
            nr, nc = self.row + d[0], self.col + d[1]
            dist = abs(target[0] - nr) + abs(target[1] - nc)
            if dist < best_dist:
                best_dist = dist
                best = d
        if best == (0, 0) and self.neighbors():
            best = random.choice(self.neighbors())
        return best

    def choose_direction(self, player: Player) -> Tuple[int, int]:
        # Default behavior: random at junctions, otherwise continue
        opts = self.neighbors()
        # remove reverse unless forced
        opts_no_reverse = [d for d in opts if (-d[0], -d[1]) != self.dir]
        if not opts_no_reverse:
            opts_no_reverse = opts
        return random.choice(opts_no_reverse) if opts_no_reverse else (0, 0)

    def color(self) -> Tuple[int, int, int]:
        if self.state == Ghost.VULNERABLE:
            return VULNERABLE_BLUE
        return self.base_color

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color(), (int(self.x), int(self.y)), self.radius)
        # eyes (simple)
        eye_offset = 4
        pygame.draw.circle(surface, WHITE, (int(self.x) - eye_offset, int(self.y) - eye_offset), 3)
        pygame.draw.circle(surface, WHITE, (int(self.x) + eye_offset, int(self.y) - eye_offset), 3)


class ChaserGhost(Ghost):
    def choose_direction(self, player: Player) -> Tuple[int, int]:
        # Chase player using greedy Manhattan heuristic
        if self.state == Ghost.VULNERABLE:
            # run away: pick direction that increases distance
            worst = (0, 0)
            worst_dist = -1
            opts = self.neighbors()
            opts = [d for d in opts if (-d[0], -d[1]) != self.dir] or opts
            for d in opts:
                nr, nc = self.row + d[0], self.col + d[1]
                dist = abs(player.row - nr) + abs(player.col - nc)
                if dist > worst_dist:
                    worst_dist = dist
                    worst = d
            return worst
        else:
            # chase towards player tile
            return self.choose_dir_towards((player.row, player.col))


class RandomGhost(Ghost):
    def choose_direction(self, player: Player) -> Tuple[int, int]:
        opts = self.neighbors()
        opts = [d for d in opts if (-d[0], -d[1]) != self.dir] or opts
        # if vulnerable, also random but slower (handled by speed)
        return random.choice(opts) if opts else (0, 0)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - OOP Clone")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.reset()

    def find_spawn(self, ch: str) -> Tuple[int, int]:
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                if MAZE_LAYOUT[r][c] == ch:
                    return r, c
        # fallback center
        return MAZE_ROWS // 2, MAZE_COLS // 2

    def reset(self):
        self.maze = Maze(MAZE_LAYOUT)
        pr, pc = self.find_spawn('P')
        self.player = Player(self.maze, pr, pc)
        # ghosts
        g_home = self.find_spawn('G')
        g1r, g1c = self.find_spawn('1')
        g2r, g2c = self.find_spawn('2')
        g3r, g3c = self.find_spawn('3')
        self.ghosts: List[Ghost] = [
            ChaserGhost(self.maze, g1r, g1c, RED),
            RandomGhost(self.maze, g2r, g2c, CYAN),
            RandomGhost(self.maze, g3r, g3c, ORANGE),
        ]
        # place a decorative G tile as house; not used directly beyond visuals
        self.state_message = ""
        self.game_over = False
        self.win = False

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.game_over or self.win:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        return
        keys = pygame.key.get_pressed()
        if not (self.game_over or self.win):
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.set_dir((0, -1))
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.set_dir((0, 1))
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.set_dir((-1, 0))
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.set_dir((1, 0))

    def update(self, dt: float):
        if self.game_over or self.win:
            return
        self.player.update(dt)
        # set ghosts vulnerable when player powered
        if self.player.is_powered():
            for g in self.ghosts:
                g.set_vulnerable()
        # update ghosts
        for g in self.ghosts:
            g.update(dt, self.player)
        # collisions
        for g in self.ghosts:
            if self.collide(self.player, g):
                if g.state == Ghost.VULNERABLE:
                    g.eaten()
                    self.player.score += 200
                elif g.state == Ghost.NORMAL:
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                        self.state_message = "Game Over - Press Enter to restart"
                    else:
                        # reset player and ghosts positions
                        pr, pc = self.find_spawn('P')
                        self.player.row, self.player.col = pr, pc
                        self.player.align_to_center()
                        for ghost in self.ghosts:
                            ghost.row, ghost.col = ghost.home
                            ghost.align_to_center()
                            ghost.state = Ghost.NORMAL
        # win condition
        if self.maze.pellet_count <= 0:
            self.win = True
            self.state_message = "You Win! - Press Enter to restart"

    def collide(self, a: Entity, b: Entity) -> bool:
        return math.hypot(a.x - b.x, a.y - b.y) < (TILE_SIZE - 6)

    def draw_ui(self):
        # UI background
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        if self.game_over or self.win:
            msg = self.font.render(self.state_message, True, GREY)
            rect = msg.get_rect(center=(SCREEN_WIDTH//2, UI_HEIGHT//2))
            self.screen.blit(msg, rect)

    def draw(self):
        self.maze.draw(self.screen)
        # draw house door visualization near G (optional embellishment)
        # draw entities
        self.player.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_input()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
