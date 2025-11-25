import sys
import math
import random
import time
from dataclasses import dataclass

import pygame
from pygame.math import Vector2 as Vec

# -----------------------------
# Config & Constants
# -----------------------------
TILE_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (10, 10, 40)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
YELLOW = (255, 222, 0)
BLUE = (50, 150, 255)
RED = (255, 60, 60)
PINK = (255, 160, 200)
CYAN = (60, 255, 255)
ORANGE = (255, 170, 60)
GREEN = (60, 255, 120)

# Game states
STATE_PLAYING = "playing"
STATE_POWER = "power"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"

# Power up duration (seconds)
POWER_DURATION = 8.0

# Layout Legend:
# '#': wall, '.': pellet, 'o': power pellet, ' ': empty path
# 'P': pacman start, 'G': ghost start
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
    "######.#####.##.#####.######",
    "     #.#####.##.#####.#     ",
    "     #.##..........##.#     ",
    "     #.##.###GG###.##.#     ",
    "######.##.#      #.##.######",
    "      .   #  PP  #   .      ",
    "######.##.#      #.##.######",
    "     #.##.########.##.#     ",
    "     #.##..........##.#     ",
    "     #.#####.##.#####.#     ",
    "######.#####.##.#####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

# Normalize layout: replace spaces outside maze with walls on edges except the intentional tunnels (kept as spaces).
# We will treat any ' ' within bounds as path, but outside row length as wall.


@dataclass
class Maze:
    grid: list
    width: int
    height: int
    pellets: set
    power_pellets: set
    walls: set
    pacman_start: Vec
    ghost_starts: list

    @staticmethod
    def from_layout(layout):
        grid = [list(row) for row in layout]
        height = len(grid)
        width = max(len(row) for row in grid)
        pellets = set()
        power_pellets = set()
        walls = set()
        pacman_start = None
        ghost_starts = []

        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch == '#':
                    walls.add((x, y))
                elif ch == '.':
                    pellets.add((x, y))
                elif ch == 'o':
                    power_pellets.add((x, y))
                elif ch == 'P':
                    pacman_start = Vec(x, y)
                    grid[y][x] = ' '  # clear tile for movement
                elif ch == 'G':
                    ghost_starts.append(Vec(x, y))
                    grid[y][x] = ' '
                else:
                    # ' ' or others treated as empty path
                    pass
        # Fallback if pacman_start missing
        if pacman_start is None:
            pacman_start = Vec(width // 2, height // 2)
        if not ghost_starts:
            ghost_starts = [Vec(width // 2 - 1, height // 2)]
        return Maze(grid, width, height, pellets, power_pellets, walls, pacman_start, ghost_starts)

    def in_bounds(self, grid_pos):
        x, y = int(grid_pos.x), int(grid_pos.y)
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, grid_pos):
        x, y = int(grid_pos.x), int(grid_pos.y)
        return (x, y) in self.walls

    def wrap_tunnel(self, grid_pos):
        # Allow wrap horizontally through open spaces
        x, y = int(grid_pos.x), int(grid_pos.y)
        if y < 0 or y >= self.height:
            return grid_pos
        if x < 0:
            return Vec(self.width - 1, y)
        if x >= self.width:
            return Vec(0, y)
        return grid_pos

    def draw(self, surf):
        # Draw background
        surf.fill(NAVY)
        # Draw walls
        for (x, y) in self.walls:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, BLUE, rect, border_radius=4)
        # Draw pellets
        for (x, y) in self.pellets:
            cx, cy = x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)
        # Draw power pellets (blink)
        t = pygame.time.get_ticks() / 300.0
        blink_on = int(t) % 2 == 0
        for (x, y) in self.power_pellets:
            cx, cy = x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2
            if blink_on:
                pygame.draw.circle(surf, ORANGE, (cx, cy), 6)


def grid_to_pixel(gpos: Vec) -> Vec:
    return Vec(gpos.x * TILE_SIZE + TILE_SIZE / 2, gpos.y * TILE_SIZE + TILE_SIZE / 2)


def pixel_to_grid(ppos: Vec) -> Vec:
    return Vec(int(ppos.x // TILE_SIZE), int(ppos.y // TILE_SIZE))


def is_centered(ppos: Vec) -> bool:
    # Check if the pixel position is near the center of its grid cell
    cx = (ppos.x - TILE_SIZE / 2) % TILE_SIZE
    cy = (ppos.y - TILE_SIZE / 2) % TILE_SIZE
    return abs(cx) < 1.0 and abs(cy) < 1.0


class Pacman:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.grid_pos = maze.pacman_start.copy()
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = Vec(0, 0)
        self.next_dir = Vec(0, 0)
        self.speed = 6.0  # tiles per second
        self.radius = TILE_SIZE * 0.45
        self.alive = True

    def set_dir_from_input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_dir = Vec(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_dir = Vec(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_dir = Vec(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_dir = Vec(0, 1)

    def can_move(self, direction: Vec) -> bool:
        gpos = pixel_to_grid(self.pixel_pos)
        target = self.maze.wrap_tunnel(gpos + direction)
        return not self.maze.is_wall(target)

    def update(self, dt):
        # Try to turn if centered and next_dir is available
        if self.next_dir.length_squared() > 0 and is_centered(self.pixel_pos):
            if self.can_move(self.next_dir):
                self.dir = self.next_dir
        # If current direction hits a wall, stop or try next_dir
        if not self.can_move(self.dir):
            if self.next_dir.length_squared() > 0 and self.can_move(self.next_dir) and is_centered(self.pixel_pos):
                self.dir = self.next_dir
            else:
                self.dir = Vec(0, 0)
        # Move
        if self.dir.length_squared() > 0:
            step = self.dir * (self.speed * dt * TILE_SIZE)
            self.pixel_pos += step
            # Handle tunnel wrapping in pixels
            if self.pixel_pos.x < -TILE_SIZE / 2:
                self.pixel_pos.x = self.maze.width * TILE_SIZE - TILE_SIZE / 2
            elif self.pixel_pos.x > self.maze.width * TILE_SIZE + TILE_SIZE / 2:
                self.pixel_pos.x = TILE_SIZE / 2
        # Update grid pos (snapped)
        self.grid_pos = self.maze.wrap_tunnel(pixel_to_grid(self.pixel_pos))

    def consume(self):
        # Eat pellets or power pellets if on cell center
        if not is_centered(self.pixel_pos):
            return 0, False
        x, y = int(self.grid_pos.x), int(self.grid_pos.y)
        gained = 0
        powered = False
        if (x, y) in self.maze.pellets:
            self.maze.pellets.remove((x, y))
            gained += 10
        if (x, y) in self.maze.power_pellets:
            self.maze.power_pellets.remove((x, y))
            gained += 50
            powered = True
        return gained, powered

    def draw(self, surf, mouth_phase):
        x, y = int(self.pixel_pos.x), int(self.pixel_pos.y)
        # Pacman mouth animation
        mouth_open = (math.sin(mouth_phase) + 1) / 2  # 0..1
        mouth_angle = 30 + 30 * mouth_open  # 30..60 degrees
        direction_angle = 0
        if self.dir.x > 0:
            direction_angle = 0
        elif self.dir.x < 0:
            direction_angle = 180
        elif self.dir.y < 0:
            direction_angle = 90
        elif self.dir.y > 0:
            direction_angle = 270
        start_angle = math.radians(direction_angle - mouth_angle)
        end_angle = math.radians(direction_angle + mouth_angle)
        pygame.draw.circle(surf, YELLOW, (x, y), int(self.radius))
        # Draw mouth by overdrawing a pie slice with background color
        pygame.draw.polygon(
            surf,
            NAVY,
            [
                (x, y),
                (x + math.cos(start_angle) * self.radius, y - math.sin(start_angle) * self.radius),
                (x + math.cos(end_angle) * self.radius, y - math.sin(end_angle) * self.radius),
            ],
        )


class Ghost:
    COLORS = [RED, PINK, CYAN, ORANGE]

    MODE_NORMAL = "normal"
    MODE_FRIGHT = "fright"
    MODE_EYES = "eyes"  # returning to base

    def __init__(self, maze: Maze, idx: int, start: Vec):
        self.maze = maze
        self.idx = idx
        self.color = Ghost.COLORS[idx % len(Ghost.COLORS)]
        self.spawn = start.copy()
        self.grid_pos = start.copy()
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = Vec(1, 0)
        self.speed = 5.0
        self.mode = Ghost.MODE_NORMAL

    def reset(self):
        self.grid_pos = self.spawn.copy()
        self.pixel_pos = grid_to_pixel(self.grid_pos)
        self.dir = Vec(1, 0)
        self.mode = Ghost.MODE_NORMAL

    def available_dirs(self):
        gpos = pixel_to_grid(self.pixel_pos)
        dirs = [Vec(1, 0), Vec(-1, 0), Vec(0, 1), Vec(0, -1)]
        candidates = []
        for d in dirs:
            target = self.maze.wrap_tunnel(gpos + d)
            if not self.maze.is_wall(target):
                candidates.append(d)
        return candidates

    def choose_dir(self, pacman_pos: Vec):
        # Only choose at center of cell
        if not is_centered(self.pixel_pos):
            return
        options = self.available_dirs()
        reverse = self.dir * -1
        # Prefer not to reverse unless no other option
        options = [d for d in options if d != reverse] or options

        if self.mode == Ghost.MODE_EYES:
            # Go back to spawn - pick direction that minimizes distance to spawn
            best = min(options, key=lambda d: (grid_to_pixel(self.maze.wrap_tunnel(pixel_to_grid(self.pixel_pos) + d)) - grid_to_pixel(self.spawn)).length_squared())
            self.dir = best
            return

        if self.mode == Ghost.MODE_FRIGHT:
            # Run away: maximize distance to pacman
            best = max(options, key=lambda d: (grid_to_pixel(self.maze.wrap_tunnel(pixel_to_grid(self.pixel_pos) + d)) - pacman_pos).length_squared())
            self.dir = best
            return

        # Normal: random at intersections (simple AI)
        self.dir = random.choice(options)

    def update(self, dt, pacman_pixel_pos: Vec):
        # Adjust speed by mode
        spd = self.speed
        if self.mode == Ghost.MODE_FRIGHT:
            spd = self.speed * 0.6
        elif self.mode == Ghost.MODE_EYES:
            spd = self.speed * 1.4

        # Decide direction at intersections
        self.choose_dir(pacman_pixel_pos)

        # Move
        if self.dir.length_squared() > 0:
            step = self.dir * (spd * dt * TILE_SIZE)
            self.pixel_pos += step
            # Tunnel wrap
            if self.pixel_pos.x < -TILE_SIZE / 2:
                self.pixel_pos.x = self.maze.width * TILE_SIZE - TILE_SIZE / 2
            elif self.pixel_pos.x > self.maze.width * TILE_SIZE + TILE_SIZE / 2:
                self.pixel_pos.x = TILE_SIZE / 2
        self.grid_pos = self.maze.wrap_tunnel(pixel_to_grid(self.pixel_pos))

        # If eyes reached spawn center, revert to normal
        if self.mode == Ghost.MODE_EYES and is_centered(self.pixel_pos) and self.grid_pos == self.spawn:
            self.mode = Ghost.MODE_NORMAL

    def frighten(self):
        if self.mode != Ghost.MODE_EYES:
            self.mode = Ghost.MODE_FRIGHT

    def set_normal(self):
        if self.mode != Ghost.MODE_EYES:
            self.mode = Ghost.MODE_NORMAL

    def eaten(self):
        # Turn into eyes to go back to spawn
        self.mode = Ghost.MODE_EYES

    def draw(self, surf, tick):
        x, y = int(self.pixel_pos.x), int(self.pixel_pos.y)
        r = int(TILE_SIZE * 0.45)
        if self.mode == Ghost.MODE_FRIGHT:
            body_color = BLUE if int(tick / 200) % 2 == 0 else WHITE
        elif self.mode == Ghost.MODE_EYES:
            body_color = WHITE
        else:
            body_color = self.color
        # Draw ghost body (simple)
        pygame.draw.circle(surf, body_color, (x, y), r)
        # Eyes
        eye_color = BLACK if self.mode != Ghost.MODE_EYES else BLUE
        pygame.draw.circle(surf, eye_color, (x - r // 3, y - r // 4), 3)
        pygame.draw.circle(surf, eye_color, (x + r // 3, y - r // 4), 3)


class Game:
    def __init__(self):
        pygame.init()
        maze = Maze.from_layout(MAZE_LAYOUT)
        self.maze = maze
        self.width = maze.width * TILE_SIZE
        self.height = maze.height * TILE_SIZE + 40  # extra UI bar
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pacman - Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)

        self.pacman = Pacman(maze)
        self.ghosts = [Ghost(maze, i, start) for i, start in enumerate(maze.ghost_starts)]

        self.state = STATE_PLAYING
        self.score = 0
        self.lives = 3
        self.power_timer = 0.0
        self.mouth_phase = 0.0
        self.level_start_time = time.time()

    def reset_positions(self, death=False):
        # Reset positions after death or level reset
        self.pacman.grid_pos = self.maze.pacman_start.copy()
        self.pacman.pixel_pos = grid_to_pixel(self.pacman.grid_pos)
        self.pacman.dir = Vec(0, 0)
        self.pacman.next_dir = Vec(0, 0)
        for g, start in zip(self.ghosts, self.maze.ghost_starts):
            g.spawn = start.copy()
            g.reset()
        if death:
            pygame.time.delay(800)

    def handle_power(self, powered_event):
        if powered_event:
            self.state = STATE_POWER
            self.power_timer = POWER_DURATION
            for g in self.ghosts:
                g.frighten()

    def update_power(self, dt):
        if self.state == STATE_POWER:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.state = STATE_PLAYING
                for g in self.ghosts:
                    g.set_normal()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.pacman.set_dir_from_input(keys)
        self.pacman.update(dt)

        # Consume pellets
        gained, powered = self.pacman.consume()
        if gained:
            self.score += gained
        self.handle_power(powered)
        self.update_power(dt)

        # Update ghosts
        for g in self.ghosts:
            g.update(dt, self.pacman.pixel_pos)

        # Check collisions Pacman vs Ghosts
        self.check_collisions()

        # Win condition: all pellets eaten
        if not self.maze.pellets and not self.maze.power_pellets and self.state not in (STATE_GAMEOVER, STATE_WIN):
            self.state = STATE_WIN

        # Mouth animation phase
        self.mouth_phase += dt * 10

    def check_collisions(self):
        if self.state == STATE_GAMEOVER:
            return
        for g in self.ghosts:
            if (g.pixel_pos - self.pacman.pixel_pos).length() < TILE_SIZE * 0.6:
                if g.mode == Ghost.MODE_FRIGHT:
                    # Eat ghost
                    g.eaten()
                    self.score += 200
                elif g.mode != Ghost.MODE_EYES:
                    # Pacman dies
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = STATE_GAMEOVER
                    self.reset_positions(death=True)
                    break

    def draw_hud(self):
        # HUD bar background
        hud_rect = pygame.Rect(0, self.maze.height * TILE_SIZE, self.width, 40)
        pygame.draw.rect(self.screen, BLACK, hud_rect)
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        state_text = "POWER" if self.state == STATE_POWER else ("WIN" if self.state == STATE_WIN else ("GAME OVER" if self.state == STATE_GAMEOVER else ""))
        state_surf = self.font.render(state_text, True, ORANGE if self.state == STATE_POWER else WHITE)
        self.screen.blit(score_surf, (10, self.maze.height * TILE_SIZE + 10))
        self.screen.blit(lives_surf, (170, self.maze.height * TILE_SIZE + 10))
        if state_text:
            self.screen.blit(state_surf, (320, self.maze.height * TILE_SIZE + 10))

    def draw(self):
        # Draw maze and entities
        play_surface = self.screen.subsurface(pygame.Rect(0, 0, self.maze.width * TILE_SIZE, self.maze.height * TILE_SIZE))
        self.maze.draw(play_surface)
        # Draw ghosts
        tick = pygame.time.get_ticks()
        for g in self.ghosts:
            g.draw(play_surface, tick)
        # Draw pacman
        self.pacman.draw(play_surface, self.mouth_phase)
        # HUD
        self.draw_hud()

    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Restart level
                    self.__init__()

            if self.state in (STATE_PLAYING, STATE_POWER):
                self.update(dt)
            # Allow pressing N to start new game after win or gameover
            keys = pygame.key.get_pressed()
            if self.state in (STATE_GAMEOVER, STATE_WIN) and keys[pygame.K_n]:
                self.__init__()

            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
