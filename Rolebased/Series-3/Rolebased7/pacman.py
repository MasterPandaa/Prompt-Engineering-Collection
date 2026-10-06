import sys
import math
import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional

# -----------------------------
# Config & Constants
# -----------------------------
TILE_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 255)
NAVY = (12, 12, 80)
YELLOW = (255, 210, 0)
RED = (255, 64, 64)
PINK = (255, 128, 200)
CYAN = (64, 255, 255)
ORANGE = (255, 165, 0)
GREY = (180, 180, 180)

# Ghost states
GHOST_NORMAL = "normal"
GHOST_VULNERABLE = "vulnerable"
GHOST_EATEN = "eaten"

# Directions (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)
ALL_DIRS = [UP, DOWN, LEFT, RIGHT]


# -----------------------------
# Maze
# -----------------------------
class Maze:
    def __init__(self, layout: List[str]):
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout[0]) if self.height > 0 else 0
        self.walls: Set[Tuple[int, int]] = set()
        self.pellets: Set[Tuple[int, int]] = set()
        self.power_pellets: Set[Tuple[int, int]] = set()
        self.player_start: Tuple[int, int] = (1, 1)
        self.ghost_starts: List[Tuple[int, int]] = []
        self.house_pos: Tuple[int, int] = (self.width // 2, self.height // 2)
        self._parse()

    def _parse(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))
                elif ch == 'P':
                    self.player_start = (x, y)
                elif ch == 'C':
                    # Chaser ghost start
                    self.ghost_starts.append((x, y))
                elif ch == 'R':
                    # Random ghost start
                    self.ghost_starts.append((x, y))
                elif ch == 'H':
                    self.house_pos = (x, y)

    def in_bounds(self, gx: int, gy: int) -> bool:
        return 0 <= gx < self.width and 0 <= gy < self.height

    def passable(self, gx: int, gy: int) -> bool:
        return (gx, gy) not in self.walls

    def is_intersection(self, gx: int, gy: int) -> bool:
        # Intersection if more than 2 valid neighbors
        valid = 0
        for dx, dy in ALL_DIRS:
            nx, ny = gx + dx, gy + dy
            if self.in_bounds(nx, ny) and self.passable(nx, ny):
                valid += 1
        return valid >= 3

    def draw(self, screen: pygame.Surface):
        # Draw walls and pellets
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if (x, y) in self.walls:
                    pygame.draw.rect(screen, NAVY, rect)
                    pygame.draw.rect(screen, BLUE, rect, 2)
                else:
                    # Floor
                    pygame.draw.rect(screen, BLACK, rect)

        # Pellets
        for (x, y) in self.pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, WHITE, (cx, cy), 3)
        # Power Pellets
        for (x, y) in self.power_pellets:
            cx = x * TILE_SIZE + TILE_SIZE // 2
            cy = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, WHITE, (cx, cy), 6, 2)


# -----------------------------
# Utility
# -----------------------------

def grid_to_px(pos: Tuple[float, float]) -> Tuple[int, int]:
    x, y = pos
    return int(x * TILE_SIZE + TILE_SIZE / 2), int(y * TILE_SIZE + TILE_SIZE / 2)


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# -----------------------------
# Player
# -----------------------------
class Player:
    def __init__(self, maze: Maze, start: Tuple[int, int]):
        self.maze = maze
        self.pos = [float(start[0]), float(start[1])]  # grid coords
        self.dir = STOP
        self.next_dir = STOP
        self.speed = 6.0 / TILE_SIZE  # tiles per frame
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True
        self.lives = 3
        self.score = 0

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.next_dir = UP
        elif keys[pygame.K_DOWN]:
            self.next_dir = DOWN
        elif keys[pygame.K_LEFT]:
            self.next_dir = LEFT
        elif keys[pygame.K_RIGHT]:
            self.next_dir = RIGHT

    def can_move(self, direction: Tuple[int, int]) -> bool:
        gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
        nx, ny = gx + direction[0], gy + direction[1]
        return self.maze.in_bounds(nx, ny) and self.maze.passable(nx, ny)

    def update(self):
        # Apply next_dir at tile centers for snappy turns
        if self.next_dir != self.dir:
            if self._is_centered_on_tile():
                if self.can_move(self.next_dir):
                    self.dir = self.next_dir
        # If current dir blocked, stop at the center
        if not self.can_move(self.dir):
            if self._is_centered_on_tile():
                self.dir = STOP

        # Move
        self.pos[0] += self.dir[0] * self.speed
        self.pos[1] += self.dir[1] * self.speed
        self._clamp_inside_walls()

    def _is_centered_on_tile(self) -> bool:
        return abs(self.pos[0] - round(self.pos[0])) < 0.1 and abs(self.pos[1] - round(self.pos[1])) < 0.1

    def _clamp_inside_walls(self):
        # Prevent slipping into walls by clamping to tile center if near
        if not self._is_centered_on_tile():
            return
        gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
        if (gx, gy) in self.maze.walls:
            self.pos = [float(gx), float(gy)]

    def eat_pellets(self) -> Tuple[int, int]:
        # returns (pellets_eaten, power_pellets_eaten)
        gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
        eaten = 0
        power = 0
        if (gx, gy) in self.maze.pellets:
            self.maze.pellets.remove((gx, gy))
            self.score += 10
            eaten += 1
        if (gx, gy) in self.maze.power_pellets:
            self.maze.power_pellets.remove((gx, gy))
            self.score += 50
            power += 1
        return eaten, power

    def draw(self, screen: pygame.Surface):
        px, py = grid_to_px((self.pos[0], self.pos[1]))
        pygame.draw.circle(screen, YELLOW, (px, py), self.radius)


# -----------------------------
# Ghosts
# -----------------------------
class Ghost:
    def __init__(self, maze: Maze, start: Tuple[int, int], color: Tuple[int, int, int]):
        self.maze = maze
        self.start = start
        self.pos = [float(start[0]), float(start[1])]  # grid
        self.dir = random.choice(ALL_DIRS)
        self.speed_normal = 5.0 / TILE_SIZE
        self.speed_vulnerable = 3.5 / TILE_SIZE
        self.speed_eaten = 7.0 / TILE_SIZE
        self.state = GHOST_NORMAL
        self.color = color
        self.radius = TILE_SIZE // 2 - 3
        self.last_valid_dir = self.dir

    def reset(self):
        self.pos = [float(self.start[0]), float(self.start[1])]
        self.dir = random.choice(ALL_DIRS)
        self.state = GHOST_NORMAL

    def set_vulnerable(self):
        if self.state != GHOST_EATEN:
            self.state = GHOST_VULNERABLE

    def set_eaten(self):
        self.state = GHOST_EATEN

    def update(self, player_tile: Tuple[int, int]):
        # Decide direction at intersections or when blocked
        if self._at_center():
            choices = self._valid_neighbors(avoid_reverse=True)
            if not choices:
                choices = self._valid_neighbors(avoid_reverse=False)
            target = self._target_tile(player_tile)
            self.dir = self._choose_dir(choices, target)

        # Move
        speed = self._current_speed()
        self.pos[0] += self.dir[0] * speed
        self.pos[1] += self.dir[1] * speed
        
        # If eaten and reached the house tile center, revert to normal
        if self.state == GHOST_EATEN and self._at_center():
            gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
            if (gx, gy) == self.maze.house_pos:
                self.state = GHOST_NORMAL
                # pick a new direction away from reversing to leave the house
                choices = self._valid_neighbors(avoid_reverse=False)
                if choices:
                    self.dir = random.choice(choices)

    def _current_speed(self) -> float:
        if self.state == GHOST_VULNERABLE:
            return self.speed_vulnerable
        if self.state == GHOST_EATEN:
            return self.speed_eaten
        return self.speed_normal

    def _at_center(self) -> bool:
        return abs(self.pos[0] - round(self.pos[0])) < 0.1 and abs(self.pos[1] - round(self.pos[1])) < 0.1

    def _valid_neighbors(self, avoid_reverse=True) -> List[Tuple[int, int]]:
        gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
        choices = []
        for d in ALL_DIRS:
            if avoid_reverse and (d[0] == -self.dir[0] and d[1] == -self.dir[1]):
                continue
            nx, ny = gx + d[0], gy + d[1]
            if self.maze.in_bounds(nx, ny) and self.maze.passable(nx, ny):
                choices.append(d)
        return choices

    def _target_tile(self, player_tile: Tuple[int, int]) -> Tuple[int, int]:
        # Default behavior: go to house if eaten, else chase player
        if self.state == GHOST_EATEN:
            return self.maze.house_pos
        if self.state == GHOST_VULNERABLE:
            # Run away: choose a far corner (opposite of player)
            px, py = player_tile
            far_x = 0 if px > self.maze.width // 2 else self.maze.width - 1
            far_y = 0 if py > self.maze.height // 2 else self.maze.height - 1
            return (far_x, far_y)
        return player_tile

    def _choose_dir(self, choices: List[Tuple[int, int]], target: Tuple[int, int]) -> Tuple[int, int]:
        # Greedy choose direction minimizing Manhattan distance to target
        if not choices:
            return self.dir
        gx, gy = int(round(self.pos[0])), int(round(self.pos[1]))
        best = choices[0]
        best_dist = math.inf
        for d in choices:
            nx, ny = gx + d[0], gy + d[1]
            dist = manhattan((nx, ny), target)
            if dist < best_dist:
                best_dist = dist
                best = d
        return best

    def draw(self, screen: pygame.Surface):
        px, py = grid_to_px((self.pos[0], self.pos[1]))
        if self.state == GHOST_VULNERABLE:
            color = GREY
        elif self.state == GHOST_EATEN:
            color = WHITE
        else:
            color = self.color
        pygame.draw.circle(screen, color, (px, py), self.radius)


class RandomGhost(Ghost):
    def _choose_dir(self, choices: List[Tuple[int, int]], target: Tuple[int, int]) -> Tuple[int, int]:
        # Pick random direction from choices
        if not choices:
            return self.dir
        return random.choice(choices)


class ChaserGhost(Ghost):
    pass  # Uses base Ghost greedy chasing


# -----------------------------
# Game
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - OOP Clone")
        self.maze = self._build_maze()
        self.screen = pygame.display.set_mode((self.maze.width * TILE_SIZE, self.maze.height * TILE_SIZE + 40))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        self.player = Player(self.maze, self.maze.player_start)
        # Identify ghost spawns: first chaser, second random (if two exist)
        colors = [RED, CYAN, ORANGE, PINK]
        self.ghosts: List[Ghost] = []
        starts = self.maze.ghost_starts[:]
        if len(starts) >= 1:
            self.ghosts.append(ChaserGhost(self.maze, starts[0], colors[0]))
        if len(starts) >= 2:
            self.ghosts.append(RandomGhost(self.maze, starts[1], colors[1]))
        # Fill remaining as random ghosts if desired
        for i in range(2, len(starts)):
            self.ghosts.append(RandomGhost(self.maze, starts[i], colors[i % len(colors)]))

        self.power_timer: int = 0  # frames remaining for vulnerability
        self.power_duration_sec = 7

        self.running = True
        self.win = False

    def _build_maze(self) -> Maze:
        # Legend: '#' wall, '.' pellet, 'o' power, 'P' player, 'C' chaser ghost, 'R' random ghost, 'H' ghost house
        layout = [
            "#########################",
            "#P...........##.........#",
            "#.###.#####.##.#####.###",
            "#o# #.#   #.##.#   #.#o#",
            "#.###.#####.##.#####.###",
            "#.......................#",
            "#.###.##.########.##.###",
            "#.....##....H.....##....#",
            "#####.######..######.####",
            "    #.R    C  C    R.#   ",
            "#####.######..######.####",
            "#.....##..........##....#",
            "#.###.##.########.##.###",
            "#o.....................o#",
            "#########################",
        ]
        # Replace spaces with walls at edges if needed; keep inner spaces as paths
        width = max(len(r) for r in layout)
        fixed = []
        for r in layout:
            r = r.ljust(width)
            fixed.append(r)
        return Maze(fixed)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

    def _update(self):
        self.player.update()
        pel, power = self.player.eat_pellets()
        if power > 0:
            self.power_timer = int(self.power_duration_sec * FPS)
            for g in self.ghosts:
                g.set_vulnerable()

        # Update ghosts
        player_tile = (int(round(self.player.pos[0])), int(round(self.player.pos[1])))
        for g in self.ghosts:
            g.update(player_tile)

        # Power timer countdown
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                for g in self.ghosts:
                    if g.state == GHOST_VULNERABLE:
                        g.state = GHOST_NORMAL

        # Collisions
        self._check_collisions()

        # Win condition
        if len(self.maze.pellets) == 0 and len(self.maze.power_pellets) == 0:
            self.win = True
            self.running = False

    def _check_collisions(self):
        pp = grid_to_px((self.player.pos[0], self.player.pos[1]))
        for g in self.ghosts:
            gp = grid_to_px((g.pos[0], g.pos[1]))
            dist = math.hypot(pp[0] - gp[0], pp[1] - gp[1])
            if dist < TILE_SIZE * 0.6:
                if g.state == GHOST_VULNERABLE:
                    g.set_eaten()
                    self.player.score += 200
                elif g.state == GHOST_EATEN:
                    # no effect
                    pass
                else:
                    # Player loses a life
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.running = False
                    else:
                        # Reset positions
                        self.player.pos = [float(self.maze.player_start[0]), float(self.maze.player_start[1])]
                        for gg in self.ghosts:
                            gg.reset()
                        self.power_timer = 0

    def _draw_hud(self):
        hud_height = 40
        hud_rect = pygame.Rect(0, self.maze.height * TILE_SIZE, self.maze.width * TILE_SIZE, hud_height)
        pygame.draw.rect(self.screen, BLACK, hud_rect)
        text = f"Score: {self.player.score}   Lives: {self.player.lives}"
        if self.power_timer > 0:
            text += f"   Power: {self.power_timer // FPS}s"
        if self.win:
            text += "   YOU WIN!"
        surf = self.font.render(text, True, WHITE)
        self.screen.blit(surf, (10, self.maze.height * TILE_SIZE + 10))

    def draw(self):
        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self._draw_hud()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self.draw()
            pygame.display.flip()

        # End screen brief
        end_text = "YOU WIN!" if self.win else "GAME OVER"
        self.screen.fill(BLACK)
        surf = self.font.render(end_text + "  Press any key to exit", True, WHITE)
        rect = surf.get_rect(center=(self.maze.width * TILE_SIZE // 2, self.maze.height * TILE_SIZE // 2))
        self.screen.blit(surf, rect)
        pygame.display.flip()
        # Wait for key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in (pygame.KEYDOWN, pygame.QUIT):
                    waiting = False
            self.clock.tick(30)
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
