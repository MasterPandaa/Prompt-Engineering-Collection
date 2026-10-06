# Pacman Clone using Pygame
# Author: Cascade (Expert Arcade Game Developer)
# Requirements: pygame
# Run: python pacman.py

import math
import random
import sys
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional

import pygame

# -----------------------------
# Config and constants
# -----------------------------
TILE_SIZE = 24
FPS = 60
MAZE_ROWS = 27
MAZE_COLS = 28
SCREEN_WIDTH = MAZE_COLS * TILE_SIZE
SCREEN_HEIGHT = MAZE_ROWS * TILE_SIZE

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 232, 0)
PINK = (255, 105, 180)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 200, 90)
NAVY = (0, 0, 80)

# Maze legend
# '#': wall
# '.': pellet
# 'o': power pellet
# ' ': empty path
# 'P': player start
# 'G': ghost spawn (house)

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
    "          # G  G #          ",
    "######.## ######## ##.######",
    "     #.##    P     ##.#     ",
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
    "############################",
]

# Some rows contain spaces for tunnel entrances and ghost house
# We'll treat any non-# as walkable except spaces outside the grid; we keep grid exact length.

@dataclass
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

# Directions
UP = Vec2(0, -1)
DOWN = Vec2(0, 1)
LEFT = Vec2(-1, 0)
RIGHT = Vec2(1, 0)
DIRECTIONS = [UP, LEFT, DOWN, RIGHT]


def grid_to_pix(pos: Vec2) -> Tuple[int, int]:
    return pos.x * TILE_SIZE + TILE_SIZE // 2, pos.y * TILE_SIZE + TILE_SIZE // 2


def pix_to_grid(px: float, py: float) -> Vec2:
    return Vec2(int(px // TILE_SIZE), int(py // TILE_SIZE))


class Maze:
    def __init__(self, layout: List[str]):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0]) if layout else 0
        self.pellets = set()
        self.power_pellets = set()
        self.walls = set()
        self.player_start = Vec2(14, 15)
        self.ghost_spawns = []  # type: List[Vec2]
        self.parse_layout()

    def parse_layout(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                pos = Vec2(x, y)
                if ch == '#':
                    self.walls.add(pos.to_tuple())
                elif ch == '.':
                    self.pellets.add(pos.to_tuple())
                elif ch == 'o':
                    self.power_pellets.add(pos.to_tuple())
                elif ch == 'P':
                    self.player_start = Vec2(x, y)
                elif ch == 'G':
                    self.ghost_spawns.append(Vec2(x, y))
        # Ensure spawns exist
        if not self.ghost_spawns:
            # default around the house
            self.ghost_spawns = [Vec2(13, 13), Vec2(14, 13), Vec2(13, 14), Vec2(14, 14)]

    def is_wall(self, grid: Vec2) -> bool:
        return (grid.x, grid.y) in self.walls

    def in_bounds(self, grid: Vec2) -> bool:
        return 0 <= grid.x < self.cols and 0 <= grid.y < self.rows

    def walkable(self, grid: Vec2) -> bool:
        if not self.in_bounds(grid):
            return False
        return (grid.x, grid.y) not in self.walls

    def remove_pellet(self, grid: Vec2) -> int:
        # returns score gained
        if (grid.x, grid.y) in self.pellets:
            self.pellets.remove((grid.x, grid.y))
            return 10
        if (grid.x, grid.y) in self.power_pellets:
            self.power_pellets.remove((grid.x, grid.y))
            return 50
        return 0

    def pellets_remaining(self) -> int:
        return len(self.pellets) + len(self.power_pellets)

    def draw(self, surface: pygame.Surface):
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
            pygame.draw.circle(surface, WHITE, (cx, cy), 7, 2)


class Entity:
    def __init__(self, maze: Maze, start_grid: Vec2, speed: float):
        self.maze = maze
        self.grid = Vec2(start_grid.x, start_grid.y)
        cx, cy = grid_to_pix(start_grid)
        self.pos = [float(cx), float(cy)]  # pixel position center
        self.dir = Vec2(0, 0)
        self.speed = speed  # pixels per frame

    def at_center_of_tile(self) -> bool:
        cx, cy = grid_to_pix(self.grid)
        return abs(self.pos[0] - cx) < 1 and abs(self.pos[1] - cy) < 1

    def set_dir(self, d: Vec2):
        self.dir = d

    def try_move(self):
        # Handle tunnel wrap
        next_px = self.pos[0] + self.dir.x * self.speed
        next_py = self.pos[1] + self.dir.y * self.speed
        next_grid = pix_to_grid(next_px, next_py)

        # allow smooth movement but prevent passing through walls by checking target cell when center aligned
        if self.dir.x != 0:
            # approaching vertical center of tile; check the cell ahead when near tile center
            target = Vec2(self.grid.x + self.dir.x, self.grid.y)
            if self.at_center_of_tile() and not self.maze.walkable(target):
                self.dir = Vec2(0, 0)
                return
        if self.dir.y != 0:
            target = Vec2(self.grid.x, self.grid.y + self.dir.y)
            if self.at_center_of_tile() and not self.maze.walkable(target):
                self.dir = Vec2(0, 0)
                return

        self.pos[0] = next_px
        self.pos[1] = next_py
        self.grid = pix_to_grid(self.pos[0], self.pos[1])

        # Wrap-around tunnels (left/right)
        if self.grid.y in (11, 15):
            if self.grid.x <= 0 and self.dir == LEFT:
                self.pos[0] = (self.maze.cols - 1) * TILE_SIZE + TILE_SIZE // 2
                self.grid = Vec2(self.maze.cols - 1, self.grid.y)
            elif self.grid.x >= self.maze.cols - 1 and self.dir == RIGHT:
                self.pos[0] = TILE_SIZE // 2
                self.grid = Vec2(0, self.grid.y)

    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int]):
        pygame.draw.circle(surface, color, (int(self.pos[0]), int(self.pos[1])), TILE_SIZE // 2 - 2)


class Player(Entity):
    def __init__(self, maze: Maze, start_grid: Vec2):
        super().__init__(maze, start_grid, speed=2.0)
        self.next_dir = Vec2(0, 0)
        self.lives = 3
        self.score = 0
        self.power_timer = 0  # frames remaining

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_dir = UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_dir = DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_dir = LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_dir = RIGHT

    def update(self):
        # Power timer countdown
        if self.power_timer > 0:
            self.power_timer -= 1
        # Direction change only when centered and target is walkable
        if self.at_center_of_tile() and self.next_dir != self.dir:
            target = Vec2(self.grid.x + self.next_dir.x, self.grid.y + self.next_dir.y)
            if self.maze.walkable(target):
                self.dir = self.next_dir
        # Move
        self.try_move()
        # Eat pellets
        if self.at_center_of_tile():
            gained = self.maze.remove_pellet(self.grid)
            if gained:
                self.score += gained
                if gained == 50:
                    # Power pellet eaten: 10 seconds of power at 60 FPS
                    self.power_timer = 10 * FPS

    def is_powered(self) -> bool:
        return self.power_timer > 0


class Ghost(Entity):
    def __init__(self, maze: Maze, start_grid: Vec2, color: Tuple[int, int, int], name: str, mode: str):
        super().__init__(maze, start_grid, speed=1.8)
        self.base_speed = 1.8
        self.fright_speed = 1.2
        self.color = color
        self.name = name
        self.mode = mode  # 'chase' or 'random' or 'frightened' internally handled
        self.vulnerable = False
        self.dead = False
        self.scatter_target = Vec2(1, 1)
        self.respawn_point = start_grid
        self.frightened_timer = 0

    def set_vulnerable(self, frames: int):
        if self.dead:
            return
        self.vulnerable = True
        self.frightened_timer = frames
        self.speed = self.fright_speed
        # reverse direction for effect
        self.dir = Vec2(-self.dir.x, -self.dir.y)

    def clear_vulnerable(self):
        self.vulnerable = False
        self.frightened_timer = 0
        self.speed = self.base_speed

    def neighbors(self, g: Vec2) -> List[Vec2]:
        result = []
        for d in DIRECTIONS:
            n = Vec2(g.x + d.x, g.y + d.y)
            if self.maze.walkable(n):
                result.append(n)
        return result

    def bfs_next_step(self, start: Vec2, goal: Vec2) -> Optional[Vec2]:
        if start.x == goal.x and start.y == goal.y:
            return None
        q = deque()
        q.append(start)
        came = {start.to_tuple(): None}
        while q:
            cur = q.popleft()
            if cur.x == goal.x and cur.y == goal.y:
                break
            for n in self.neighbors(cur):
                if n.to_tuple() not in came:
                    came[n.to_tuple()] = cur
                    q.append(n)
        if (goal.x, goal.y) not in came:
            return None
        # backtrack
        cur = goal
        while came[cur.to_tuple()] and came[cur.to_tuple()].to_tuple() != start.to_tuple():
            cur = came[cur.to_tuple()]
        return cur

    def choose_dir_towards(self, target: Vec2):
        if not self.at_center_of_tile():
            return
        next_cell = self.bfs_next_step(self.grid, target)
        if not next_cell:
            # no path or already at target: choose random valid dir not reversing
            candidates = []
            for d in DIRECTIONS:
                n = Vec2(self.grid.x + d.x, self.grid.y + d.y)
                if self.maze.walkable(n):
                    candidates.append(d)
            if candidates:
                # avoid reversing
                rev = Vec2(-self.dir.x, -self.dir.y)
                candidates = [d for d in candidates if not (d.x == rev.x and d.y == rev.y)] or candidates
                self.dir = random.choice(candidates)
            return
        d = Vec2(next_cell.x - self.grid.x, next_cell.y - self.grid.y)
        self.dir = d

    def choose_random_dir(self):
        if not self.at_center_of_tile():
            return
        candidates = []
        for d in DIRECTIONS:
            n = Vec2(self.grid.x + d.x, self.grid.y + d.y)
            if self.maze.walkable(n):
                candidates.append(d)
        if candidates:
            rev = Vec2(-self.dir.x, -self.dir.y)
            candidates = [d for d in candidates if not (d.x == rev.x and d.y == rev.y)] or candidates
            self.dir = random.choice(candidates)

    def update(self, player: Player):
        # timers
        if self.vulnerable:
            if self.frightened_timer > 0:
                self.frightened_timer -= 1
            else:
                self.clear_vulnerable()
        # decide direction
        if self.dead:
            # go back to house to respawn
            self.choose_dir_towards(self.respawn_point)
            if self.at_center_of_tile() and self.grid.x == self.respawn_point.x and self.grid.y == self.respawn_point.y:
                self.dead = False
                self.clear_vulnerable()
        else:
            if self.vulnerable:
                # move away from player: pick direction that maximizes distance (greedy)
                if self.at_center_of_tile():
                    best = None
                    best_dist = -1
                    for d in DIRECTIONS:
                        n = Vec2(self.grid.x + d.x, self.grid.y + d.y)
                        if self.maze.walkable(n):
                            dist = (n.x - player.grid.x) ** 2 + (n.y - player.grid.y) ** 2
                            if dist > best_dist and not (d.x == -self.dir.x and d.y == -self.dir.y):
                                best_dist = dist
                                best = d
                    if best is None:
                        self.choose_random_dir()
                    else:
                        self.dir = best
            else:
                if self.mode == 'chaser':
                    # chase player grid directly (simple)
                    self.choose_dir_towards(player.grid)
                elif self.mode == 'random':
                    self.choose_random_dir()
                else:
                    self.choose_random_dir()

        # move
        self.try_move()

    def draw(self, surface: pygame.Surface):
        color = CYAN if self.vulnerable and not self.dead else self.color
        super().draw(surface, color)
        # eyes when vulnerable or dead
        if self.vulnerable or self.dead:
            pygame.draw.circle(surface, WHITE, (int(self.pos[0]) - 6, int(self.pos[1]) - 3), 3)
            pygame.draw.circle(surface, WHITE, (int(self.pos[0]) + 6, int(self.pos[1]) - 3), 3)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Cascade")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        self.maze = Maze(MAZE_LAYOUT)
        self.player = Player(self.maze, self.maze.player_start)

        # Create two ghosts with different simple AI
        spawns = self.maze.ghost_spawns
        self.ghosts: List[Ghost] = [
            Ghost(self.maze, spawns[0], RED, "Blinky", mode='chaser'),
            Ghost(self.maze, spawns[1], ORANGE, "Clyde", mode='random'),
        ]

        self.state = 'playing'  # 'playing', 'win', 'gameover'
        self.level = 1

    def reset_positions(self):
        self.player.grid = Vec2(self.maze.player_start.x, self.maze.player_start.y)
        cx, cy = grid_to_pix(self.player.grid)
        self.player.pos = [float(cx), float(cy)]
        self.player.dir = Vec2(0, 0)
        for i, g in enumerate(self.ghosts):
            start = self.maze.ghost_spawns[i % len(self.maze.ghost_spawns)]
            g.grid = Vec2(start.x, start.y)
            cx, cy = grid_to_pix(start)
            g.pos = [float(cx), float(cy)]
            g.dir = random.choice(DIRECTIONS)
            g.dead = False
            g.clear_vulnerable()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if self.state in ('win', 'gameover') and event.key == pygame.K_RETURN:
                    # restart level
                    self.__init__()
        if self.state == 'playing':
            self.player.handle_input()

    def update(self):
        if self.state != 'playing':
            return
        self.player.update()
        # Set ghosts vulnerable when player powers up
        if self.player.is_powered():
            for g in self.ghosts:
                if not g.dead:
                    g.set_vulnerable(frames=max(g.frightened_timer, self.player.power_timer))
        for g in self.ghosts:
            g.update(self.player)

        # collisions player/ghost
        for g in self.ghosts:
            if self.collision(self.player, g):
                if g.vulnerable and not g.dead:
                    # eat ghost
                    g.dead = True
                    g.vulnerable = False
                    self.player.score += 200
                    g.speed = 2.4
                elif not g.dead and not self.player.is_powered():
                    # player loses life
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = 'gameover'
                    else:
                        self.reset_positions()
                    break

        if self.maze.pellets_remaining() == 0:
            self.state = 'win'

    @staticmethod
    def collision(a: Entity, b: Entity) -> bool:
        ax, ay = a.pos
        bx, by = b.pos
        return (ax - bx) ** 2 + (ay - by) ** 2 < (TILE_SIZE // 2) ** 2

    def draw_hud(self):
        score_surf = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        level_surf = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_surf, (10, SCREEN_HEIGHT - 20))
        self.screen.blit(lives_surf, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT - 20))
        self.screen.blit(level_surf, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 20))

    def draw_state_overlay(self):
        if self.state == 'win':
            msg = "YOU WIN! Press Enter to Restart"
        elif self.state == 'gameover':
            msg = "GAME OVER! Press Enter to Restart"
        else:
            return
        surf = self.font.render(msg, True, YELLOW)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(surf, rect)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.maze.draw(self.screen)
            # Draw entities
            self.player.draw(self.screen, YELLOW)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_hud()
            self.draw_state_overlay()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
