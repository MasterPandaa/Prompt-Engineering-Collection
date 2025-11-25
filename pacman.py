import sys
import math
import random
import time
from collections import deque

import pygame


# --- Constants ---
TILE_SIZE = 24
FPS = 60
POWER_DURATION = 8.0  # seconds
PLAYER_SPEED = 4  # pixels per frame
GHOST_SPEED = 3
GHOST_VULN_SPEED = 2

# Colors
BLACK = (0, 0, 0)
NAVY = (12, 12, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
RED = (220, 38, 38)
PINK = (236, 72, 153)
CYAN = (34, 197, 218)
ORANGE = (245, 158, 11)
BLUE = (59, 130, 246)  # vulnerable
GREY = (120, 120, 120)


class Maze:
    """
    Parses and renders a hardcoded 2D layout.
    Legend:
      # wall
      . dot (1 point)
      o power pellet (10 points)
      P player spawn
      G ghost spawn
      space empty path
    """

    def __init__(self):
        self.layout = self._generate_layout()
        self.height = len(self.layout)
        self.width = len(self.layout[0])
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE

        self.walls = set()
        self.dots = set()
        self.power_pellets = set()
        self.player_spawn = None
        self.ghost_spawns = []

        self._parse_layout()

    def _generate_layout(self):
        # 28x31 inspired layout, simplified and symmetric
        raw = [
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
            "######.##### ## #####.######",
            "######.##          ##.######",
            "######.## ######## ##.######",
            "#     .   ########   .     #",
            "#.####.## ######## ##.####.#",
            "#.####.##    GG    ##.####.#",
            "#......## ######## ##......#",
            "######.## ######## ##.######",
            "######.##          ##.######",
            "######.##### ## #####.######",
            "######.##### ## #####.######",
            "#......##....##....##......#",
            "#.####.##.########.##.####.#",
            "#.####.##.########.##.####.#",
            "#...P....................o.#",
            "#.####.#####.##.#####.####.#",
            "#o.... ....................#",
            "#######.##.########.##.#####",
            "#######.##.########.##.#####",
            "#............##............#",
            "############################",
        ]
        return raw

    def _parse_layout(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                pos = (x, y)
                if ch == '#':
                    self.walls.add(pos)
                elif ch == '.':
                    self.dots.add(pos)
                elif ch == 'o':
                    self.power_pellets.add(pos)
                elif ch == 'P':
                    self.player_spawn = pos
                elif ch == 'G':
                    self.ghost_spawns.append(pos)
                elif ch == ' ':
                    # empty path
                    pass
                else:
                    # treat other characters like dots when within paths
                    if ch == ' ':  # already handled
                        pass
        # If no explicit player spawn, choose center-ish open cell
        if not self.player_spawn:
            self.player_spawn = self._find_first_open()
        # If no ghost spawns, choose nearby cells
        if not self.ghost_spawns:
            gx, gy = self.player_spawn
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                p = (gx + dx, gy + dy)
                if p not in self.walls:
                    self.ghost_spawns.append(p)

    def _find_first_open(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch != '#':
                    return (x, y)
        return (1, 1)

    def is_wall(self, cell):
        return cell in self.walls

    def in_bounds(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def draw(self, surface):
        surface.fill(NAVY)
        # Draw walls as rectangles
        for (x, y) in self.walls:
            pygame.draw.rect(
                surface,
                CYAN,
                pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                border_radius=4,
            )
        # Draw dots
        for (x, y) in self.dots:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, WHITE, (cx, cy), 3)
        # Draw power pellets
        for (x, y) in self.power_pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, ORANGE, (cx, cy), 6)


def add_pos(a, b):
    return (a[0] + b[0], a[1] + b[1])


def pixel_to_cell(px, py):
    return (px // TILE_SIZE, py // TILE_SIZE)


def cell_to_pixel_center(cell):
    x, y = cell
    return (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)


DIRS = {
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
}
DIR_ORDER = ['LEFT', 'RIGHT', 'UP', 'DOWN']


class Player:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.spawn_cell = maze.player_spawn
        self.reset()

    def reset(self):
        self.dir = 'LEFT'
        self.next_dir = None
        self.cell = self.spawn_cell
        self.px, self.py = cell_to_pixel_center(self.cell)
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True

    def can_move(self, direction):
        dx, dy = DIRS[direction]
        next_cell = (self.cell[0] + dx, self.cell[1] + dy)
        return self.maze.in_bounds(next_cell) and not self.maze.is_wall(next_cell)

    def set_next_dir(self, direction):
        self.next_dir = direction

    def update(self):
        # Align to grid for turns
        cx, cy = cell_to_pixel_center(self.cell)
        if abs(self.px - cx) < PLAYER_SPEED and abs(self.py - cy) < PLAYER_SPEED:
            self.px, self.py = cx, cy
            self.cell = pixel_to_cell(self.px, self.py)
            if self.next_dir and self.can_move(self.next_dir):
                self.dir = self.next_dir
                self.next_dir = None
            if not self.can_move(self.dir):
                return
        # Move in current dir
        dx, dy = DIRS[self.dir]
        self.px += dx * PLAYER_SPEED
        self.py += dy * PLAYER_SPEED
        self.cell = pixel_to_cell(self.px, self.py)

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (self.px, self.py), self.radius)


class Ghost:
    NORMAL = 'normal'
    VULNERABLE = 'vulnerable'
    EATEN = 'eaten'

    def __init__(self, maze: Maze, spawn_cell, color):
        self.maze = maze
        self.spawn_cell = spawn_cell
        self.base_color = color
        self.radius = TILE_SIZE // 2 - 3
        self.reset()

    def reset(self):
        self.cell = self.spawn_cell
        self.px, self.py = cell_to_pixel_center(self.cell)
        self.dir = random.choice(DIR_ORDER)
        self.state = Ghost.NORMAL
        self.vulnerable_until = 0.0
        self.respawn_time = 0.0

    def set_vulnerable(self, now, duration):
        if self.state != Ghost.EATEN:
            self.state = Ghost.VULNERABLE
            self.vulnerable_until = now + duration

    def update_state(self, now):
        if self.state == Ghost.VULNERABLE and now >= self.vulnerable_until:
            self.state = Ghost.NORMAL
        if self.state == Ghost.EATEN and now >= self.respawn_time:
            # respawn at spawn cell
            self.cell = self.spawn_cell
            self.px, self.py = cell_to_pixel_center(self.cell)
            self.state = Ghost.NORMAL
            self.dir = random.choice(DIR_ORDER)

    def eaten(self, now, respawn_delay=3.0):
        self.state = Ghost.EATEN
        self.respawn_time = now + respawn_delay

    def speed(self):
        if self.state == Ghost.VULNERABLE:
            return GHOST_VULN_SPEED
        return GHOST_SPEED

    def neighbors(self, cell):
        nbs = []
        for d in DIR_ORDER:
            dx, dy = DIRS[d]
            nxt = (cell[0] + dx, cell[1] + dy)
            if self.maze.in_bounds(nxt) and not self.maze.is_wall(nxt):
                nbs.append(nxt)
        return nbs

    def at_intersection(self):
        # Number of open directions excluding backtrack
        open_dirs = 0
        for d in DIR_ORDER:
            dx, dy = DIRS[d]
            nxt = (self.cell[0] + dx, self.cell[1] + dy)
            if self.maze.in_bounds(nxt) and not self.maze.is_wall(nxt):
                open_dirs += 1
        return open_dirs >= 3

    def choose_dir(self, target_cell):
        # Default behavior: go straight if possible; else choose a direction toward target
        options = []
        for d in DIR_ORDER:
            dx, dy = DIRS[d]
            nxt = (self.cell[0] + dx, self.cell[1] + dy)
            if not self.maze.in_bounds(nxt) or self.maze.is_wall(nxt):
                continue
            # avoid reversing if multiple options
            if self.opposite(self.dir) == d and self.at_intersection():
                continue
            options.append((d, nxt))
        if not options:
            return self.opposite(self.dir)
        # Greedy by distance to target
        best = min(options, key=lambda t: self.manhattan(t[1], target_cell))
        return best[0]

    def opposite(self, direction):
        return {
            'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 'UP': 'DOWN', 'DOWN': 'UP'
        }[direction]

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def update_move(self, target_cell):
        # Align and pick direction
        cx, cy = cell_to_pixel_center(self.cell)
        spd = self.speed()
        if abs(self.px - cx) < spd and abs(self.py - cy) < spd:
            self.px, self.py = cx, cy
            self.cell = pixel_to_cell(self.px, self.py)
            # Decide new dir
            self.dir = self.choose_dir(target_cell)
            # If blocked, try any
            dx, dy = DIRS[self.dir]
            nxt = (self.cell[0] + dx, self.cell[1] + dy)
            if self.maze.is_wall(nxt):
                for d in DIR_ORDER:
                    dx, dy = DIRS[d]
                    nxt = (self.cell[0] + dx, self.cell[1] + dy)
                    if not self.maze.is_wall(nxt):
                        self.dir = d
                        break
        # Move
        dx, dy = DIRS[self.dir]
        self.px += dx * spd
        self.py += dy * spd
        self.cell = pixel_to_cell(self.px, self.py)

    def draw(self, surface):
        color = BLUE if self.state == Ghost.VULNERABLE else self.base_color
        if self.state == Ghost.EATEN:
            color = GREY
        pygame.draw.circle(surface, color, (self.px, self.py), self.radius)


class ChaserGhost(Ghost):
    """Chases player using BFS pathfinding target selection."""

    def bfs_next_target(self, start, goal):
        # Compute first step toward goal using BFS
        if start == goal:
            return start
        q = deque([start])
        came_from = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            for nb in self.neighbors(cur):
                if nb not in came_from:
                    came_from[nb] = cur
                    q.append(nb)
        if goal not in came_from:
            return start  # no path
        # Reconstruct back to start to find next step
        cur = goal
        while came_from[cur] != start and came_from[cur] is not None:
            cur = came_from[cur]
        return cur

    def choose_dir(self, target_cell):
        # Use BFS to choose next step toward target then convert to direction
        next_cell = self.bfs_next_target(self.cell, target_cell)
        dx = next_cell[0] - self.cell[0]
        dy = next_cell[1] - self.cell[1]
        for name, v in DIRS.items():
            if v == (dx, dy):
                # Avoid reversing if intersection preference applies
                if self.opposite(self.dir) == name and self.at_intersection():
                    # fall back to base behavior
                    return super().choose_dir(target_cell)
                return name
        return super().choose_dir(target_cell)


class WanderGhost(Ghost):
    """Moves randomly at intersections, prefers continuing direction otherwise."""

    def choose_dir(self, target_cell):
        options = []
        for d in DIR_ORDER:
            dx, dy = DIRS[d]
            nxt = (self.cell[0] + dx, self.cell[1] + dy)
            if not self.maze.in_bounds(nxt) or self.maze.is_wall(nxt):
                continue
            if self.opposite(self.dir) == d and self.at_intersection():
                continue
            options.append(d)
        if not options:
            return self.opposite(self.dir)
        if self.at_intersection():
            return random.choice(options)
        # Try to keep going straight if possible
        if self.dir in options:
            return self.dir
        return random.choice(options)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (OOP)")
        self.maze = Maze()
        self.screen = pygame.display.set_mode((self.maze.pixel_width, self.maze.pixel_height))
        self.clock = pygame.time.Clock()

        self.player = Player(self.maze)
        spawns = self.maze.ghost_spawns
        # Ensure at least two ghosts
        g1_spawn = spawns[0] if spawns else self.player.spawn_cell
        g2_spawn = spawns[1] if len(spawns) > 1 else self.player.spawn_cell
        self.ghosts = [
            ChaserGhost(self.maze, g1_spawn, RED),
            WanderGhost(self.maze, g2_spawn, PINK),
        ]

        self.score = 0
        self.lives = 3
        self.font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        self.running = True
        self.game_over = False
        self.win = False

    def reset_round(self):
        self.player.reset()
        for g in self.ghosts:
            g.reset()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.set_next_dir('LEFT')
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.set_next_dir('RIGHT')
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.set_next_dir('UP')
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.set_next_dir('DOWN')

    def handle_collisions(self):
        # Dot consumption
        if self.player.cell in self.maze.dots:
            self.maze.dots.remove(self.player.cell)
            self.score += 10
        # Power pellet
        if self.player.cell in self.maze.power_pellets:
            self.maze.power_pellets.remove(self.player.cell)
            self.score += 50
            now = time.time()
            for g in self.ghosts:
                g.set_vulnerable(now, POWER_DURATION)

        # Ghost interactions
        now = time.time()
        for g in self.ghosts:
            # If overlapped sufficiently treat as collision
            if self.cells_close(self.player.cell, g.cell):
                if g.state == Ghost.VULNERABLE:
                    g.eaten(now)
                    self.score += 200
                elif g.state == Ghost.NORMAL:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_round()
                    break

    def cells_close(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 0

    def update(self):
        if self.game_over:
            return
        self.handle_input()
        self.player.update()
        # Update ghosts
        now = time.time()
        for g in self.ghosts:
            g.update_state(now)
            target = self.player.cell
            if g.state == Ghost.VULNERABLE:
                # Run away: target opposite vector cell
                px, py = self.player.cell
                gx, gy = g.cell
                away = (px + (gx - px) * 4, py + (gy - py) * 4)
                # clamp into bounds
                ax = min(max(0, away[0]), self.maze.width - 1)
                ay = min(max(0, away[1]), self.maze.height - 1)
                target = (ax, ay)
            elif g.state == Ghost.EATEN:
                target = g.spawn_cell
            g.update_move(target)

        self.handle_collisions()
        # Win condition
        if not self.maze.dots and not self.maze.power_pellets:
            self.win = True
            self.game_over = True

    def draw_hud(self, surface):
        text = f"Score: {self.score}   Lives: {self.lives}"
        img = self.font.render(text, True, WHITE)
        surface.blit(img, (8, 4))

    def draw_overlay(self, surface):
        if self.game_over:
            msg = "YOU WIN!" if self.win else "GAME OVER"
            img = self.big_font.render(msg, True, WHITE)
            rect = img.get_rect(center=(self.maze.pixel_width // 2, self.maze.pixel_height // 2))
            surface.blit(img, rect)
            sub = self.font.render("Press Enter to restart or Esc to quit", True, WHITE)
            sub_rect = sub.get_rect(center=(self.maze.pixel_width // 2, self.maze.pixel_height // 2 + 40))
            surface.blit(sub, sub_rect)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if self.game_over and event.key == pygame.K_RETURN:
                        # restart
                        self.__init__()

            self.update()

            # Draw
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_hud(self.screen)
            self.draw_overlay(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
