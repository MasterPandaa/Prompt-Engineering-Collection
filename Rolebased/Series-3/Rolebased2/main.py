import sys
import math
import random
import time
from collections import deque

import pygame

# -----------------------------
# Constants
# -----------------------------
TILE_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
NAVY = (6, 6, 40)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 208, 0)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREY = (150, 150, 150)

# Tile definitions in layout
WALL = '#'
PELLET = '.'
POWER = 'o'
EMPTY = ' '
PLAYER_START = 'P'
GHOST_SPAWN = 'G'


class Maze:
    """Maze holds the grid, walls, pellets, and rendering."""

    def __init__(self):
        # Simple compact maze (28x31 style proportions but smaller for demo)
        # Legend: '#' wall, '.' pellet, 'o' power pellet, 'P' player start, 'G' ghost spawn
        self.layout = [
            "#########################",
            "#o.........##.........o#",
            "#.###.####.##.####.###.#",
            "#.# #.#  #.##.#  #.# #.#",
            "#.###.####.##.####.###.#",
            "#.......................#",
            "#.###.##.######.##.###.#",
            "#.....##....##....##...#",
            "#####.##### ## #####.###",
            "    #.#   G PP   G #.#  ",
            "#####.# ## #### ## #.###",
            "#...........##........#",
            "#.###.####.##.####.###.#",
            "#o..#......  G  ......#o",
            "###.#.##.######.##.#.###",
            "#.....##....##....##...#",
            "#.#########.##.#########",
            "#.......................#",
            "#########################",
        ]
        # Normalize rows to equal length
        max_w = max(len(r) for r in self.layout)
        self.grid = [list(r.ljust(max_w)) for r in self.layout]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

        self.pellets = set()
        self.power_pellets = set()
        self.walls = set()
        self.player_start = None
        self.ghost_spawns = []

        self._parse_layout()

    def _parse_layout(self):
        for r in range(self.rows):
            for c in range(self.cols):
                ch = self.grid[r][c]
                pos = (c, r)
                if ch == WALL:
                    self.walls.add(pos)
                elif ch == PELLET:
                    self.pellets.add(pos)
                elif ch == POWER:
                    self.power_pellets.add(pos)
                elif ch == PLAYER_START:
                    self.player_start = pos
                    self.grid[r][c] = EMPTY
                elif ch == GHOST_SPAWN:
                    self.ghost_spawns.append(pos)
                    self.grid[r][c] = EMPTY

    def in_bounds(self, col, row):
        return 0 <= col < self.cols and 0 <= row < self.rows

    def passable(self, col, row):
        # Treat spaces and paths as passable
        if not self.in_bounds(col, row):
            return False
        return (col, row) not in self.walls

    def neighbors(self, col, row):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        result = []
        for dx, dy in dirs:
            nc, nr = col + dx, row + dy
            if self.passable(nc, nr):
                result.append((nc, nr))
        return result

    def draw(self, surf):
        surf.fill(NAVY)
        # Draw walls
        for (c, r) in self.walls:
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, BLUE, rect)
        # Draw pellets
        for (c, r) in self.pellets:
            x = c * TILE_SIZE + TILE_SIZE // 2
            y = r * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, WHITE, (x, y), 3)
        # Draw power pellets
        for (c, r) in self.power_pellets:
            x = c * TILE_SIZE + TILE_SIZE // 2
            y = r * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surf, WHITE, (x, y), 6)


class Entity:
    def __init__(self, maze: Maze, col, row, color):
        self.maze = maze
        self.col = col
        self.row = row
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE + TILE_SIZE // 2
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.speed = 2
        self.color = color
        self.radius = TILE_SIZE // 2 - 2

    def grid_pos(self):
        return int(round(self.x / TILE_SIZE - 0.5)), int(round(self.y / TILE_SIZE - 0.5))

    def pixel_center_of_tile(self, col, row):
        return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2

    def at_center_of_tile(self):
        col, row = self.grid_pos()
        cx, cy = self.pixel_center_of_tile(col, row)
        return abs(self.x - cx) < 0.5 and abs(self.y - cy) < 0.5

    def move_step(self):
        # Apply tunnel wrap horizontally
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed
        # Wrap
        if self.x < -TILE_SIZE // 2:
            self.x = self.maze.width + TILE_SIZE // 2
        elif self.x > self.maze.width + TILE_SIZE // 2:
            self.x = -TILE_SIZE // 2

    def can_move_dir(self, dcol, drow):
        # Check tile ahead
        col, row = self.grid_pos()
        target = (col + dcol, row + drow)
        return self.maze.passable(*target)

    def try_turn(self):
        if self.next_dir != (0, 0) and self.at_center_of_tile():
            if self.can_move_dir(*self.next_dir):
                self.dir = self.next_dir
                self.next_dir = (0, 0)

    def update(self):
        self.try_turn()
        # Stop if heading into wall
        if not self.can_move_dir(*self.dir) and self.at_center_of_tile():
            self.dir = (0, 0)
        self.move_step()

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), TILE_SIZE // 2 - 2)


class Player(Entity):
    def __init__(self, maze: Maze, col, row):
        super().__init__(maze, col, row, YELLOW)
        self.speed = 2
        self.lives = 3
        self.score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        desired = None
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            desired = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            desired = (1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            desired = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            desired = (0, 1)
        if desired:
            if self.at_center_of_tile() and self.can_move_dir(*desired):
                self.dir = desired
            else:
                self.next_dir = desired

    def eat_pellets(self, game):
        col, row = self.grid_pos()
        if (col, row) in self.maze.pellets:
            self.maze.pellets.remove((col, row))
            self.score += 10
        if (col, row) in self.maze.power_pellets:
            self.maze.power_pellets.remove((col, row))
            self.score += 50
            game.trigger_power_mode()

    def update(self, game):
        self.handle_input()
        super().update()
        self.eat_pellets(game)

    def reset_position(self):
        self.x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.row * TILE_SIZE + TILE_SIZE // 2
        self.dir = (0, 0)
        self.next_dir = (0, 0)


class Ghost(Entity):
    STATE_NORMAL = 'normal'
    STATE_FRIGHTENED = 'frightened'
    STATE_EATEN = 'eaten'

    def __init__(self, maze: Maze, col, row, color, name="Ghost"):
        super().__init__(maze, col, row, color)
        self.spawn_col = col
        self.spawn_row = row
        self.base_color = color
        self.state = Ghost.STATE_NORMAL
        self.speed = 2
        self.name = name
        self.frightened_end_time = 0.0

    def set_frightened(self, duration):
        if self.state == Ghost.STATE_EATEN:
            return
        self.state = Ghost.STATE_FRIGHTENED
        self.frightened_end_time = time.time() + duration

    def update_state(self):
        if self.state == Ghost.STATE_FRIGHTENED and time.time() > self.frightened_end_time:
            self.state = Ghost.STATE_NORMAL

    def choose_direction(self, game):
        # To be overridden by subclasses
        pass

    def update(self, game):
        self.update_state()
        if self.at_center_of_tile():
            self.choose_direction(game)
        super().update()

    def draw(self, surf):
        color = self.base_color
        if self.state == Ghost.STATE_FRIGHTENED:
            color = CYAN
        elif self.state == Ghost.STATE_EATEN:
            color = GREY
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), TILE_SIZE // 2 - 2)

    def reset_to_spawn(self):
        self.col = self.spawn_col
        self.row = self.spawn_row
        self.x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.row * TILE_SIZE + TILE_SIZE // 2
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.state = Ghost.STATE_NORMAL


class ChaserGhost(Ghost):
    """Simple BFS-based chaser that targets the player's current tile."""

    def __init__(self, maze, col, row):
        super().__init__(maze, col, row, PINK, name="Chaser")

    def bfs_next_step(self, start, goal):
        # BFS to find next step toward goal
        if start == goal:
            return None
        q = deque([start])
        came_from = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            for nb in self.maze.neighbors(*cur):
                if nb not in came_from:
                    came_from[nb] = cur
                    q.append(nb)
        if goal not in came_from:
            return None
        # Reconstruct path
        cur = goal
        while came_from[cur] != start:
            cur = came_from[cur]
            if cur is None:
                return None
        return cur

    def choose_direction(self, game):
        # If frightened: random at intersections, avoid reversing preference
        if self.state == Ghost.STATE_FRIGHTENED:
            self._random_direction(avoid_reverse=True)
            return
        # If eaten: head to spawn
        if self.state == Ghost.STATE_EATEN:
            target = (self.spawn_col, self.spawn_row)
        else:
            target = game.player.grid_pos()
        start = self.grid_pos()
        next_tile = self.bfs_next_step(start, target)
        if next_tile is None:
            self._random_direction(avoid_reverse=False)
            return
        dc = next_tile[0] - start[0]
        dr = next_tile[1] - start[1]
        # Only change at center
        if self.at_center_of_tile():
            self.dir = (int(math.copysign(1, dc)) if dc != 0 else 0,
                        int(math.copysign(1, dr)) if dr != 0 else 0)

    def _random_direction(self, avoid_reverse=True):
        col, row = self.grid_pos()
        options = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if self.can_move_dir(*d):
                if avoid_reverse and (-d[0], -d[1]) == self.dir:
                    continue
                options.append(d)
        if options:
            self.dir = random.choice(options)


class RandomGhost(Ghost):
    """Chooses random direction at intersections, keeps going otherwise."""

    def __init__(self, maze, col, row):
        super().__init__(maze, col, row, ORANGE, name="Random")

    def choose_direction(self, game):
        # If eaten: go back to spawn using simple greedy choice
        if self.state == Ghost.STATE_EATEN:
            self._greedy_to((self.spawn_col, self.spawn_row))
            return
        # If frightened: random, avoid reverse
        avoid_reverse = self.state == Ghost.STATE_FRIGHTENED
        col, row = self.grid_pos()
        # Count exits
        exits = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if self.can_move_dir(*d):
                exits.append(d)
        if len(exits) >= 3 or self.dir == (0, 0) or not self.can_move_dir(*self.dir):
            options = []
            for d in exits:
                if avoid_reverse and (-d[0], -d[1]) == self.dir:
                    continue
                options.append(d)
            if options:
                self.dir = random.choice(options)
        # else keep current direction

    def _greedy_to(self, target):
        sx, sy = self.grid_pos()
        best = None
        best_dist = 1e9
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if self.can_move_dir(*d):
                nx, ny = sx + d[0], sy + d[1]
                dist = abs(nx - target[0]) + abs(ny - target[1])
                if dist < best_dist:
                    best_dist = dist
                    best = d
        if best is not None:
            self.dir = best


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman OOP Clone")
        self.maze = Maze()
        self.screen = pygame.display.set_mode((self.maze.width, self.maze.height + 40))
        self.clock = pygame.time.Clock()
        # Entities
        ps = self.maze.player_start or (1, 1)
        self.player = Player(self.maze, ps[0], ps[1])
        # Place ghosts: from spawns or fallback
        spawns = self.maze.ghost_spawns or [(self.maze.cols // 2, self.maze.rows // 2)]
        self.ghosts = []
        if spawns:
            s0 = spawns[0]
            self.ghosts.append(ChaserGhost(self.maze, s0[0], s0[1]))
        if len(spawns) > 1:
            s1 = spawns[1]
            self.ghosts.append(RandomGhost(self.maze, s1[0], s1[1]))
        else:
            # spawn a second ghost near the center
            self.ghosts.append(RandomGhost(self.maze, spawns[0][0] + 1, spawns[0][1]))

        self.font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 36)

        # Game state
        self.power_mode = False
        self.power_duration = 7.0
        self.level_complete = False
        self.game_over = False

    def trigger_power_mode(self):
        self.power_mode = True
        for g in self.ghosts:
            g.set_frightened(self.power_duration)

    def update(self):
        if self.game_over:
            return
        self.player.update(self)
        for g in self.ghosts:
            g.update(self)
        self.handle_collisions()
        self.check_level_complete()

    def handle_collisions(self):
        px, py = self.player.x, self.player.y
        for g in self.ghosts:
            gx, gy = g.x, g.y
            dist = math.hypot(px - gx, py - gy)
            if dist < TILE_SIZE * 0.6:
                if g.state == Ghost.STATE_FRIGHTENED:
                    # Eat ghost
                    g.state = Ghost.STATE_EATEN
                    self.player.score += 200
                elif g.state == Ghost.STATE_EATEN:
                    # ignore
                    pass
                else:
                    # Player hit
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    self.reset_positions()
                    break
        # When a ghost in eaten state reaches spawn, revive
        for g in self.ghosts:
            if g.state == Ghost.STATE_EATEN and g.at_center_of_tile():
                if g.grid_pos() == (g.spawn_col, g.spawn_row):
                    g.state = Ghost.STATE_NORMAL

    def reset_positions(self):
        # Reset player to start
        self.player.reset_position()
        # Reset ghosts to spawn if not eaten (eaten continue to spawn)
        for g in self.ghosts:
            if g.state != Ghost.STATE_EATEN:
                g.reset_to_spawn()

    def check_level_complete(self):
        if not self.maze.pellets and not self.maze.power_pellets:
            self.level_complete = True

    def draw_hud(self):
        hud_rect = pygame.Rect(0, self.maze.height, self.maze.width, 40)
        pygame.draw.rect(self.screen, BLACK, hud_rect)
        text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(text, (10, self.maze.height + 10))
        # Lives
        for i in range(self.player.lives):
            x = self.maze.width - 20 - i * 20
            y = self.maze.height + 20
            pygame.draw.circle(self.screen, YELLOW, (x, y), 8)

    def draw_overlays(self):
        if self.game_over:
            surf = self.big_font.render("GAME OVER", True, RED)
            rect = surf.get_rect(center=(self.maze.width // 2, self.maze.height // 2))
            self.screen.blit(surf, rect)
        elif self.level_complete:
            surf = self.big_font.render("LEVEL COMPLETE!", True, WHITE)
            rect = surf.get_rect(center=(self.maze.width // 2, self.maze.height // 2))
            self.screen.blit(surf, rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # restart
                    self.__init__()

            if not self.game_over and not self.level_complete:
                self.update()

            # Draw
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.draw_hud()
            self.draw_overlays()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
