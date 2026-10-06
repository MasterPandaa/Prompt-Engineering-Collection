import sys
import math
import random
import pygame
from enum import Enum
from typing import List, Tuple, Optional, Set


# ------------------------------
# Constants & Config
# ------------------------------
TILE_SIZE = 24
FPS = 60
POWER_DURATION_SEC = 7.0
PLAYER_SPEED = 4.0  # tiles per second (converted to pixels per frame)
GHOST_SPEED = 3.6
VULNERABLE_SPEED = 2.4
SCREEN_MARGIN = 24
FONT_NAME = "arial"

# Colors
BLACK = (0, 0, 0)
NAVY = (10, 10, 40)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
RED = (255, 60, 60)
PINK = (255, 105, 180)
CYAN = (80, 200, 255)
ORANGE = (255, 170, 66)
BLUE = (66, 140, 255)
WALL_BLUE = (0, 90, 200)
PELLET_COLOR = (255, 255, 255)
POWER_COLOR = (0, 255, 200)


# ------------------------------
# Utility helpers
# ------------------------------
Vec2 = Tuple[int, int]


def add(a: Vec2, b: Vec2) -> Vec2:
    return a[0] + b[0], a[1] + b[1]


def mul(a: Vec2, s: float) -> Tuple[float, float]:
    return a[0] * s, a[1] * s


def manhattan(a: Vec2, b: Vec2) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


DIRECTIONS: List[Vec2] = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class GhostState(Enum):
    NORMAL = 0
    VULNERABLE = 1
    EATEN = 2


# ------------------------------
# Maze
# ------------------------------
class Maze:
    def __init__(self) -> None:
        # Map Legend:
        # '#': wall
        # '.': pellet
        # 'o': power pellet
        # ' ': empty
        # 'P': player spawn
        # 'G': ghost spawn
        self.layout: List[str] = [
            "#########################",
            "#..........##..........G#",
            "#.####.###.##.###.####.#",
            "#o#  #.#       #.#  #o#",
            "#.####.#.#####.#.####.#",
            "#......#..P G..#......#",
            "#.####.#.#####.#.####.#",
            "#o#  #.#       #.#  #o#",
            "#.####.###.##.###.####.#",
            "#G.........##.........G#",
            "#########################",
        ]
        self.height = len(self.layout)
        self.width = len(self.layout[0])
        self.walls: Set[Vec2] = set()
        self.pellets: Set[Vec2] = set()
        self.power_pellets: Set[Vec2] = set()
        self.player_spawn: Vec2 = (1, 1)
        self.ghost_spawns: List[Vec2] = []
        self._parse_layout()

    def _parse_layout(self) -> None:
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))
                elif ch == 'P':
                    self.player_spawn = (x, y)
                elif ch == 'G':
                    self.ghost_spawns.append((x, y))

    def in_bounds(self, tile: Vec2) -> bool:
        x, y = tile
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, tile: Vec2) -> bool:
        return tile not in self.walls

    def neighbors(self, tile: Vec2) -> List[Vec2]:
        res: List[Vec2] = []
        for d in DIRECTIONS:
            n = add(tile, d)
            if self.in_bounds(n) and self.passable(n):
                res.append(n)
        return res

    def draw(self, surface: pygame.Surface, offset: Vec2) -> None:
        ox, oy = offset
        for (x, y) in self.walls:
            rect = pygame.Rect(ox + x * TILE_SIZE, oy + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, WALL_BLUE, rect, border_radius=4)
        # pellets
        for (x, y) in self.pellets:
            cx = ox + x * TILE_SIZE + TILE_SIZE // 2
            cy = oy + y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, PELLET_COLOR, (cx, cy), 3)
        # power pellets
        for (x, y) in self.power_pellets:
            cx = ox + x * TILE_SIZE + TILE_SIZE // 2
            cy = oy + y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(surface, POWER_COLOR, (cx, cy), 6)


# ------------------------------
# Player
# ------------------------------
class Player:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.spawn = maze.player_spawn
        self.tile_pos: Tuple[float, float] = (float(self.spawn[0]), float(self.spawn[1]))
        self.pixel_pos: Tuple[float, float] = self._to_pixel(self.tile_pos)
        self.dir: Vec2 = (0, 0)
        self.next_dir: Vec2 = (0, 0)
        self.speed_px_per_frame = PLAYER_SPEED * TILE_SIZE / FPS
        self.radius = TILE_SIZE // 2 - 2
        self.alive = True

    def reset(self) -> None:
        self.tile_pos = (float(self.spawn[0]), float(self.spawn[1]))
        self.pixel_pos = self._to_pixel(self.tile_pos)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.alive = True

    def _to_pixel(self, tile_pos: Tuple[float, float]) -> Tuple[float, float]:
        x, y = tile_pos
        return (x * TILE_SIZE, y * TILE_SIZE)

    def _to_tile(self, pixel_pos: Tuple[float, float]) -> Tuple[int, int]:
        x, y = pixel_pos
        return int(round(x / TILE_SIZE)), int(round(y / TILE_SIZE))

    def set_dir_from_input(self, keys) -> None:
        desired = self.next_dir
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            desired = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            desired = (1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            desired = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            desired = (0, 1)
        self.next_dir = desired

    def can_move(self, direction: Vec2) -> bool:
        tx, ty = self._to_tile(self.pixel_pos)
        target = (tx + direction[0], ty + direction[1])
        return self.maze.in_bounds(target) and self.maze.passable(target)

    def update(self, dt: float) -> None:
        # Try to turn if possible at tile centers
        tx, ty = self._to_tile(self.pixel_pos)
        center_px = (tx * TILE_SIZE, ty * TILE_SIZE)
        # If near center, allow direction change
        if self.next_dir != self.dir:
            if self._at_center(center_px):
                if self.can_move(self.next_dir):
                    self.dir = self.next_dir
        # Move forward if possible
        if self.can_move(self.dir):
            self.pixel_pos = (
                self.pixel_pos[0] + self.dir[0] * self.speed_px_per_frame,
                self.pixel_pos[1] + self.dir[1] * self.speed_px_per_frame,
            )
            # Snap to center to avoid drift
            if self._overshoot(center_px, self.dir):
                self.pixel_pos = (
                    center_px[0] + self.dir[0] * 0.001,
                    center_px[1] + self.dir[1] * 0.001,
                )
        else:
            # stop at wall, snap to center
            self.pixel_pos = (center_px[0], center_px[1])
        # Update tile position
        self.tile_pos = (self.pixel_pos[0] / TILE_SIZE, self.pixel_pos[1] / TILE_SIZE)

    def _overshoot(self, center_px: Tuple[int, int], direction: Vec2) -> bool:
        # determine if we passed center
        if direction[0] != 0:
            return (direction[0] > 0 and self.pixel_pos[0] > center_px[0]) or (
                direction[0] < 0 and self.pixel_pos[0] < center_px[0]
            )
        if direction[1] != 0:
            return (direction[1] > 0 and self.pixel_pos[1] > center_px[1]) or (
                direction[1] < 0 and self.pixel_pos[1] < center_px[1]
            )
        return False

    def _at_center(self, center_px: Tuple[int, int]) -> bool:
        return (
            abs(self.pixel_pos[0] - center_px[0]) < 2 and abs(self.pixel_pos[1] - center_px[1]) < 2
        )

    def eat_at_current_tile(self, pellets: Set[Vec2], power_pellets: Set[Vec2]) -> Tuple[int, bool]:
        # returns (score_gain, power)
        tx, ty = self._to_tile(self.pixel_pos)
        score = 0
        power = False
        if (tx, ty) in pellets:
            pellets.remove((tx, ty))
            score += 10
        if (tx, ty) in power_pellets:
            power_pellets.remove((tx, ty))
            score += 50
            power = True
        return score, power

    def draw(self, surface: pygame.Surface, offset: Vec2) -> None:
        ox, oy = offset
        cx = int(self.pixel_pos[0] + ox + TILE_SIZE // 2)
        cy = int(self.pixel_pos[1] + oy + TILE_SIZE // 2)
        pygame.draw.circle(surface, YELLOW, (cx, cy), self.radius)


# ------------------------------
# Ghost
# ------------------------------
class Ghost:
    def __init__(self, maze: Maze, spawn: Vec2, color: Tuple[int, int, int], ai: str) -> None:
        self.maze = maze
        self.spawn = spawn
        self.color = color
        self.ai = ai  # 'chaser' or 'random'
        self.tile_pos: Tuple[float, float] = (float(spawn[0]), float(spawn[1]))
        self.pixel_pos: Tuple[float, float] = (self.tile_pos[0] * TILE_SIZE, self.tile_pos[1] * TILE_SIZE)
        self.dir: Vec2 = (0, 0)
        self.speed_px_per_frame = GHOST_SPEED * TILE_SIZE / FPS
        self.state = GhostState.NORMAL
        self.vulnerable_timer = 0.0
        self.radius = TILE_SIZE // 2 - 2

    def reset(self) -> None:
        self.tile_pos = (float(self.spawn[0]), float(self.spawn[1]))
        self.pixel_pos = (self.tile_pos[0] * TILE_SIZE, self.tile_pos[1] * TILE_SIZE)
        self.dir = (0, 0)
        self.state = GhostState.NORMAL
        self.vulnerable_timer = 0.0
        self.speed_px_per_frame = GHOST_SPEED * TILE_SIZE / FPS

    def set_vulnerable(self) -> None:
        if self.state != GhostState.EATEN:
            self.state = GhostState.VULNERABLE
            self.vulnerable_timer = POWER_DURATION_SEC
            self.speed_px_per_frame = VULNERABLE_SPEED * TILE_SIZE / FPS

    def update(self, dt: float, player_tile: Vec2) -> None:
        # handle vulnerable timer
        if self.state == GhostState.VULNERABLE:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.state = GhostState.NORMAL
                self.speed_px_per_frame = GHOST_SPEED * TILE_SIZE / FPS
        # choose direction at intersections or if blocked
        self._move_logic(player_tile)
        # move
        self.pixel_pos = (
            self.pixel_pos[0] + self.dir[0] * self.speed_px_per_frame,
            self.pixel_pos[1] + self.dir[1] * self.speed_px_per_frame,
        )
        self.tile_pos = (self.pixel_pos[0] / TILE_SIZE, self.pixel_pos[1] / TILE_SIZE)

    def _move_logic(self, player_tile: Vec2) -> None:
        tx = int(round(self.pixel_pos[0] / TILE_SIZE))
        ty = int(round(self.pixel_pos[1] / TILE_SIZE))
        center_px = (tx * TILE_SIZE, ty * TILE_SIZE)
        at_center = abs(self.pixel_pos[0] - center_px[0]) < 2 and abs(self.pixel_pos[1] - center_px[1]) < 2
        # if blocked, stop at center
        if not self._can_move(self.dir):
            self.pixel_pos = (center_px[0], center_px[1])
            at_center = True
        if at_center:
            options = self._available_dirs((tx, ty), avoid_reverse=True)
            if not options:
                options = self._available_dirs((tx, ty), avoid_reverse=False)
            if options:
                if self.ai == 'chaser' and self.state != GhostState.VULNERABLE:
                    # choose direction minimizing manhattan distance to player
                    best = min(options, key=lambda d: manhattan((tx + d[0], ty + d[1]), player_tile))
                    self.dir = best
                else:
                    self.dir = random.choice(options)

    def _available_dirs(self, tile: Vec2, avoid_reverse: bool) -> List[Vec2]:
        options: List[Vec2] = []
        for d in DIRECTIONS:
            if avoid_reverse and (-d[0], -d[1]) == self.dir and self._can_move(self.dir):
                continue
            target = (tile[0] + d[0], tile[1] + d[1])
            if self.maze.in_bounds(target) and self.maze.passable(target):
                options.append(d)
        return options

    def _can_move(self, direction: Vec2) -> bool:
        if direction == (0, 0):
            return False
        tx = int(round(self.pixel_pos[0] / TILE_SIZE))
        ty = int(round(self.pixel_pos[1] / TILE_SIZE))
        target = (tx + direction[0], ty + direction[1])
        return self.maze.in_bounds(target) and self.maze.passable(target)

    def eaten(self) -> None:
        self.state = GhostState.EATEN
        self.pixel_pos = (self.spawn[0] * TILE_SIZE, self.spawn[1] * TILE_SIZE)
        self.tile_pos = (float(self.spawn[0]), float(self.spawn[1]))
        self.dir = (0, 0)
        # brief delay could be implemented, but we reset to normal immediately for simplicity
        self.state = GhostState.NORMAL
        self.speed_px_per_frame = GHOST_SPEED * TILE_SIZE / FPS

    def draw(self, surface: pygame.Surface, offset: Vec2) -> None:
        ox, oy = offset
        cx = int(self.pixel_pos[0] + ox + TILE_SIZE // 2)
        cy = int(self.pixel_pos[1] + oy + TILE_SIZE // 2)
        color = BLUE if self.state == GhostState.VULNERABLE else self.color
        pygame.draw.circle(surface, color, (cx, cy), self.radius)
        # little eyes
        eye_color = WHITE if self.state != GhostState.VULNERABLE else (240, 240, 255)
        pygame.draw.circle(surface, eye_color, (cx - 4, cy - 3), 3)
        pygame.draw.circle(surface, eye_color, (cx + 4, cy - 3), 3)


# ------------------------------
# Game
# ------------------------------
class Game:
    def __init__(self) -> None:
        pygame.init()
        self.maze = Maze()
        self.width_px = self.maze.width * TILE_SIZE + SCREEN_MARGIN * 2
        self.height_px = self.maze.height * TILE_SIZE + SCREEN_MARGIN * 2 + 40  # HUD area
        self.screen = pygame.display.set_mode((self.width_px, self.height_px))
        pygame.display.set_caption("Pacman (OOP) - Pygame")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(FONT_NAME, 18)
        self.font_big = pygame.font.SysFont(FONT_NAME, 36, bold=True)
        self.offset = (SCREEN_MARGIN, SCREEN_MARGIN + 40)

        self.player = Player(self.maze)

        ghost_spawns = self._select_ghost_spawns()
        # create at least two ghosts: chaser and random
        self.ghosts: List[Ghost] = [
            Ghost(self.maze, ghost_spawns[0], RED, 'chaser'),
            Ghost(self.maze, ghost_spawns[1], CYAN, 'random'),
        ]
        # optional additional ghosts for flavor
        if len(ghost_spawns) > 2:
            self.ghosts.append(Ghost(self.maze, ghost_spawns[2], ORANGE, 'random'))
        if len(ghost_spawns) > 3:
            self.ghosts.append(Ghost(self.maze, ghost_spawns[3], PINK, 'chaser'))

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

    def _select_ghost_spawns(self) -> List[Vec2]:
        if self.maze.ghost_spawns:
            return self.maze.ghost_spawns
        # fallback if none tagged as 'G': use near player spawn
        px, py = self.maze.player_spawn
        candidates = [(px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)]
        return [c for c in candidates if self.maze.in_bounds(c) and self.maze.passable(c)] or [(px, py)]

    def reset_round(self) -> None:
        self.player.reset()
        for g in self.ghosts:
            g.reset()

    def trigger_power(self) -> None:
        for g in self.ghosts:
            g.set_vulnerable()

    def collide(self, a_pos: Tuple[float, float], b_pos: Tuple[float, float]) -> bool:
        ax, ay = a_pos
        bx, by = b_pos
        return math.hypot(ax - bx, ay - by) < TILE_SIZE * 0.6

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        # input
        keys = pygame.key.get_pressed()
        self.player.set_dir_from_input(keys)
        # update entities
        self.player.update(dt)
        player_tile = (
            int(round(self.player.pixel_pos[0] / TILE_SIZE)),
            int(round(self.player.pixel_pos[1] / TILE_SIZE)),
        )
        for g in self.ghosts:
            g.update(dt, player_tile)
        # eat pellets
        add_score, power = self.player.eat_at_current_tile(self.maze.pellets, self.maze.power_pellets)
        self.score += add_score
        if power:
            self.trigger_power()
        # collisions
        for g in self.ghosts:
            if self.collide(self.player.pixel_pos, g.pixel_pos):
                if g.state == GhostState.VULNERABLE:
                    g.eaten()
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self.win = False
                    self.reset_round()
                    break
        # win condition
        if not self.maze.pellets and not self.maze.power_pellets:
            self.game_over = True
            self.win = True

    def draw_hud(self) -> None:
        # top HUD bar
        pygame.draw.rect(self.screen, NAVY, (0, 0, self.width_px, SCREEN_MARGIN + 20))
        score_surf = self.font_small.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font_small.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (SCREEN_MARGIN, 10))
        self.screen.blit(lives_surf, (self.width_px - SCREEN_MARGIN - lives_surf.get_width(), 10))

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.draw_hud()
        self.maze.draw(self.screen, self.offset)
        self.player.draw(self.screen, self.offset)
        for g in self.ghosts:
            g.draw(self.screen, self.offset)
        if self.game_over:
            msg = "YOU WIN!" if self.win else "GAME OVER"
            sub = "Press R to Restart or ESC to Quit"
            text = self.font_big.render(msg, True, WHITE)
            subtext = self.font_small.render(sub, True, WHITE)
            cx = self.width_px // 2
            cy = self.height_px // 2
            self.screen.blit(text, (cx - text.get_width() // 2, cy - 40))
            self.screen.blit(subtext, (cx - subtext.get_width() // 2, cy + 8))
        pygame.display.flip()

    def handle_events(self) -> bool:
        # returns False to quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_r:
                    # rebuild maze pellets for a fresh round
                    self.maze = Maze()
                    self.player = Player(self.maze)
                    ghost_spawns = self._select_ghost_spawns()
                    self.ghosts = [
                        Ghost(self.maze, ghost_spawns[0], RED, 'chaser'),
                        Ghost(self.maze, ghost_spawns[1], CYAN, 'random'),
                    ]
                    if len(ghost_spawns) > 2:
                        self.ghosts.append(Ghost(self.maze, ghost_spawns[2], ORANGE, 'random'))
                    if len(ghost_spawns) > 3:
                        self.ghosts.append(Ghost(self.maze, ghost_spawns[3], PINK, 'chaser'))
                    self.score = 0
                    self.lives = 3
                    self.game_over = False
                    self.win = False
        return True

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
