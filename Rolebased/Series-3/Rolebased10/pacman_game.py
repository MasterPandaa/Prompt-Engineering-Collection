import sys
import math
import random
from enum import Enum
from typing import List, Tuple, Optional, Set

import pygame

# ----------------------------
# Config
# ----------------------------
TILE_SIZE = 24
GRID_WIDTH = 28
GRID_HEIGHT = 31
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREY = (120, 120, 120)

# Timings
POWER_DURATION = 7.0  # seconds ghosts remain vulnerable
GHOST_RESPAWN_TIME = 3.0  # seconds in house after eaten

# Movement
PLAYER_SPEED = 4.0  # tiles per second
GHOST_SPEED = 3.5   # tiles per second
VULNERABLE_GHOST_SPEED = 2.4

Vec2 = Tuple[int, int]


class GhostState(Enum):
    NORMAL = 0
    VULNERABLE = 1
    EATEN = 2


def grid_to_px(cell: Vec2) -> Tuple[int, int]:
    x, y = cell
    return int(x * TILE_SIZE + TILE_SIZE / 2), int(y * TILE_SIZE + TILE_SIZE / 2)


def px_to_grid(pos: Tuple[float, float]) -> Vec2:
    x, y = pos
    return int(x // TILE_SIZE), int(y // TILE_SIZE)


# ----------------------------
# Maze
# ----------------------------
class Maze:
    """
    Handles map layout, walls, pellets, power-pellets, and rendering helpers.
    Layout legend:
      '#' = wall
      '.' = pellet
      'o' = power pellet
      ' ' = empty path
      'H' = ghost house door (treat as wall for player, passable for eaten ghosts)
    """

    def __init__(self, layout: List[str]):
        self.layout = layout
        self.width = len(layout[0])
        self.height = len(layout)
        self.walls: Set[Vec2] = set()
        self.doors: Set[Vec2] = set()
        self.pellets: Set[Vec2] = set()
        self.power_pellets: Set[Vec2] = set()

        for y, row in enumerate(layout):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == 'H':
                    self.doors.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))

    def in_bounds(self, cell: Vec2) -> bool:
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, cell: Vec2) -> bool:
        return cell in self.walls

    def is_door(self, cell: Vec2) -> bool:
        return cell in self.doors

    def passable_for(self, cell: Vec2, allow_door: bool = False) -> bool:
        if not self.in_bounds(cell):
            return False
        if self.is_wall(cell):
            return False
        if self.is_door(cell) and not allow_door:
            return False
        return True

    def neighbors(self, cell: Vec2, allow_door: bool = False) -> List[Vec2]:
        x, y = cell
        options = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [c for c in options if self.passable_for(c, allow_door)]

    def eat_pellet(self, cell: Vec2) -> int:
        # returns score gained
        if cell in self.pellets:
            self.pellets.remove(cell)
            return 10
        if cell in self.power_pellets:
            self.power_pellets.remove(cell)
            return 50
        return 0

    def remaining_pellets(self) -> int:
        return len(self.pellets) + len(self.power_pellets)

    def draw(self, surf: pygame.Surface):
        # draw walls
        for (x, y) in self.walls:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, BLUE, rect)
        # draw doors
        for (x, y) in self.doors:
            cx, cy = grid_to_px((x, y))
            pygame.draw.line(surf, GREY, (cx - TILE_SIZE // 2, cy), (cx + TILE_SIZE // 2, cy), 2)
        # draw pellets
        for (x, y) in self.pellets:
            cx, cy = grid_to_px((x, y))
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)
        # draw power pellets
        for (x, y) in self.power_pellets:
            cx, cy = grid_to_px((x, y))
            pygame.draw.circle(surf, WHITE, (cx, cy), 6)


# ----------------------------
# Player
# ----------------------------
class Player:
    def __init__(self, start_cell: Vec2):
        self.cell = start_cell
        self.pos = list(grid_to_px(start_cell))  # pixel pos center
        self.dir: Vec2 = (0, 0)
        self.next_dir: Vec2 = (0, 0)  # input buffer
        self.speed = PLAYER_SPEED * TILE_SIZE  # pixels per second
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.next_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.next_dir = (1, 0)
            elif event.key == pygame.K_UP:
                self.next_dir = (0, -1)
            elif event.key == pygame.K_DOWN:
                self.next_dir = (0, 1)

    def at_center_of_cell(self) -> bool:
        cx, cy = grid_to_px(px_to_grid(self.pos))
        return abs(self.pos[0] - cx) < 1 and abs(self.pos[1] - cy) < 1

    def update(self, maze: Maze, dt: float):
        # attempt to switch direction when centered
        if self.next_dir != self.dir and self.at_center_of_cell():
            target_cell = (px_to_grid(self.pos)[0] + self.next_dir[0], px_to_grid(self.pos)[1] + self.next_dir[1])
            if maze.passable_for(target_cell):
                self.dir = self.next_dir
        # move
        dx = self.dir[0] * self.speed * dt
        dy = self.dir[1] * self.speed * dt
        new_pos = [self.pos[0] + dx, self.pos[1] + dy]

        # wrap tunnels
        grid_x, grid_y = px_to_grid(new_pos)
        if grid_y == 14 and grid_x < 0:
            new_pos[0] = (maze.width - 1) * TILE_SIZE + TILE_SIZE / 2
        elif grid_y == 14 and grid_x >= maze.width:
            new_pos[0] = TILE_SIZE / 2

        # collision with walls: only allow moving into passable cells
        next_cell = (px_to_grid(self.pos)[0] + self.dir[0], px_to_grid(self.pos)[1] + self.dir[1])
        if maze.passable_for(next_cell):
            self.pos = new_pos
        else:
            # snap to center when blocked
            self.pos = list(grid_to_px(px_to_grid(self.pos)))
            self.dir = (0, 0)

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, YELLOW, (int(self.pos[0]), int(self.pos[1])), self.radius)


# ----------------------------
# Ghosts
# ----------------------------
class Ghost:
    def __init__(self, start_cell: Vec2, color: Tuple[int, int, int], name: str = "ghost"):
        self.name = name
        self.start_cell = start_cell
        self.cell = start_cell
        self.pos = list(grid_to_px(start_cell))
        self.dir: Vec2 = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = color
        self.state = GhostState.NORMAL
        self.state_timer = 0.0
        self.radius = TILE_SIZE // 2 - 2

    def speed_px(self) -> float:
        if self.state == GhostState.VULNERABLE:
            return VULNERABLE_GHOST_SPEED * TILE_SIZE
        return GHOST_SPEED * TILE_SIZE

    def set_vulnerable(self):
        if self.state == GhostState.EATEN:
            return
        self.state = GhostState.VULNERABLE
        self.state_timer = POWER_DURATION

    def eaten(self):
        self.state = GhostState.EATEN
        self.state_timer = GHOST_RESPAWN_TIME
        # move to house center quickly
        self.pos = list(grid_to_px(self.start_cell))
        self.dir = (0, 0)

    def update(self, maze: Maze, player_cell: Vec2, dt: float):
        # handle timers
        if self.state in (GhostState.VULNERABLE, GhostState.EATEN):
            self.state_timer -= dt
            if self.state == GhostState.VULNERABLE and self.state_timer <= 0:
                self.state = GhostState.NORMAL
            elif self.state == GhostState.EATEN and self.state_timer <= 0:
                self.state = GhostState.NORMAL
                self.dir = (0, -1)  # leave house

        # Movement lock if eaten (waiting)
        if self.state == GhostState.EATEN and self.state_timer > 0:
            return

        # Try to turn at cell centers
        if self.at_center_of_cell():
            self.choose_direction(maze, player_cell)

        # move
        speed = self.speed_px()
        dx = self.dir[0] * speed * dt
        dy = self.dir[1] * speed * dt
        new_pos = [self.pos[0] + dx, self.pos[1] + dy]

        # wrap tunnels like player
        grid_x, grid_y = px_to_grid(new_pos)
        if grid_y == 14 and grid_x < 0:
            new_pos[0] = (maze.width - 1) * TILE_SIZE + TILE_SIZE / 2
        elif grid_y == 14 and grid_x >= maze.width:
            new_pos[0] = TILE_SIZE / 2

        next_cell = (px_to_grid(self.pos)[0] + self.dir[0], px_to_grid(self.pos)[1] + self.dir[1])
        allow_door = (self.state == GhostState.EATEN)
        if maze.passable_for(next_cell, allow_door=allow_door):
            self.pos = new_pos
        else:
            # stop at wall and pick new direction
            self.pos = list(grid_to_px(px_to_grid(self.pos)))
            self.dir = (0, 0)

    def at_center_of_cell(self) -> bool:
        cx, cy = grid_to_px(px_to_grid(self.pos))
        return abs(self.pos[0] - cx) < 1 and abs(self.pos[1] - cy) < 1

    def choose_direction(self, maze: Maze, player_cell: Vec2):
        raise NotImplementedError

    def current_cell(self) -> Vec2:
        return px_to_grid(self.pos)

    def draw(self, surf: pygame.Surface):
        if self.state == GhostState.VULNERABLE:
            color = BLUE
        elif self.state == GhostState.EATEN:
            color = GREY
        else:
            color = self.color
        pygame.draw.circle(surf, color, (int(self.pos[0]), int(self.pos[1])), self.radius)


class ChaserGhost(Ghost):
    """Simple greedy chaser: at intersections, choose the move that minimizes Manhattan distance to player."""

    def choose_direction(self, maze: Maze, player_cell: Vec2):
        options = []
        cx, cy = self.current_cell()
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            # avoid reversing unless no other choice
            if (-d[0], -d[1]) == self.dir:
                continue
            nc = (cx + d[0], cy + d[1])
            allow_door = (self.state == GhostState.EATEN)
            if maze.passable_for(nc, allow_door=allow_door):
                options.append(d)
        if not options:
            # allow reverse if blocked
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc = (cx + d[0], cy + d[1])
                allow_door = (self.state == GhostState.EATEN)
                if maze.passable_for(nc, allow_door=allow_door):
                    options.append(d)
        if not options:
            self.dir = (0, 0)
            return

        # If vulnerable, prefer moving away from player
        def manhattan(c: Vec2) -> int:
            return abs(c[0] - player_cell[0]) + abs(c[1] - player_cell[1])

        best = None
        best_score = None
        cx, cy = self.current_cell()
        for d in options:
            nc = (cx + d[0], cy + d[1])
            score = manhattan(nc)
            if self.state == GhostState.VULNERABLE:
                score = -score
            if best is None or (score < best_score if self.state != GhostState.VULNERABLE else score > best_score):
                best = d
                best_score = score
        self.dir = best


class RandomGhost(Ghost):
    """Chooses random valid turn at intersections, avoiding immediate reverse when possible."""

    def choose_direction(self, maze: Maze, player_cell: Vec2):
        cx, cy = self.current_cell()
        options = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if (-d[0], -d[1]) == self.dir:
                continue
            nc = (cx + d[0], cy + d[1])
            allow_door = (self.state == GhostState.EATEN)
            if maze.passable_for(nc, allow_door=allow_door):
                options.append(d)
        if not options:
            # allow reverse
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc = (cx + d[0], cy + d[1])
                allow_door = (self.state == GhostState.EATEN)
                if maze.passable_for(nc, allow_door=allow_door):
                    options.append(d)
        if options:
            # If vulnerable, bias away from player by choosing the dir that increases distance 70% of time
            if self.state == GhostState.VULNERABLE and random.random() < 0.7:
                def dist(dir):
                    nc = (cx + dir[0], cy + dir[1])
                    return abs(nc[0] - player_cell[0]) + abs(nc[1] - player_cell[1])
                options.sort(key=lambda d: dist(d), reverse=True)
                self.dir = options[0]
            else:
                self.dir = random.choice(options)
        else:
            self.dir = (0, 0)


# ----------------------------
# Game
# ----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (Minimal Clone)")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        layout = self.default_layout()
        self.maze = Maze(layout)

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

        self.player = Player(self.player_start())
        house_cell = self.ghost_house()
        self.ghosts: List[Ghost] = [
            ChaserGhost(house_cell, RED, name="Blinky"),
            RandomGhost(house_cell, CYAN, name="Inky"),
        ]

        self.power_active = False
        self.power_timer = 0.0

    # ----- Layout helpers -----
    def default_layout(self) -> List[str]:
        # 28x31 simple Pacman-like maze. 'H' marks the ghost house door.
        # This is a handcrafted, symmetric-ish layout suitable for a small clone.
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
            "     #.##### HH #####.#     ",
            "######.##### ## #####.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#o..##................##..o#",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#..........................#",
            "#.####.#####.##.#####.####.#",
            "#o####..................###.#",
            "#.####.##.########.##.####.#",
            "#......##....##....##......#",
            "######.##### ## #####.######",
            "     #.##### HH #####.#     ",
            "######.##### ## #####.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#............##............#",
            "############################",
        ]
        # Replace spaces with paths (so neighbors work); keep walls '#', pellets '.' and 'o', keep door 'H'
        # We leave spaces as spaces to indicate empty path.
        return layout

    def player_start(self) -> Vec2:
        return (13, 23)

    def ghost_house(self) -> Vec2:
        return (13, 14)

    # ----- Game flow -----
    def reset_after_death(self):
        self.player = Player(self.player_start())
        house_cell = self.ghost_house()
        self.ghosts = [
            ChaserGhost(house_cell, RED, name="Blinky"),
            RandomGhost(house_cell, CYAN, name="Inky"),
        ]
        self.power_active = False
        self.power_timer = 0.0

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            self.player.handle_input(event)
        return True

    def update(self, dt: float):
        if self.game_over:
            return

        # Player update
        self.player.update(self.maze, dt)

        # Pellet consumption
        cell = px_to_grid(self.player.pos)
        gained = self.maze.eat_pellet(cell)
        if gained > 0:
            self.score += gained
            if gained == 50:
                # power pellet
                self.activate_power()

        # Update ghosts
        for g in self.ghosts:
            g.update(self.maze, px_to_grid(self.player.pos), dt)

        # Handle collisions with ghosts
        for g in self.ghosts:
            if self.check_collision(self.player.pos, g.pos):
                if g.state == GhostState.VULNERABLE:
                    g.eaten()
                    self.score += 200
                elif g.state != GhostState.EATEN:
                    # lose life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.reset_after_death()
                    return

        # Power pellet timer
        if self.power_active:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.power_active = False

        # Win condition
        if self.maze.remaining_pellets() == 0:
            self.win = True
            self.game_over = True

    def activate_power(self):
        self.power_active = True
        self.power_timer = POWER_DURATION
        for g in self.ghosts:
            g.set_vulnerable()

    def check_collision(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> bool:
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) < TILE_SIZE * 0.6

    def draw_hud(self):
        text = f"Score: {self.score}   Lives: {self.lives}"
        if self.power_active:
            text += f"   Power: {self.power_timer:0.1f}s"
        surf = self.font.render(text, True, WHITE)
        self.screen.blit(surf, (8, 4))

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()
        if self.game_over:
            msg = "YOU WIN!" if self.win else "GAME OVER"
            surf = self.font.render(msg + "  (Press ESC to quit)", True, WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(surf, rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
