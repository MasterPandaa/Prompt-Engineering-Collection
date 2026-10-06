import sys
import random
import time
import pygame
from typing import List, Tuple

# -----------------------------
# Config & Constants
# -----------------------------
# Colors
BLUE = (33, 66, 199)
DARK_BLUE = (20, 38, 120)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
GREY = (50, 50, 50)

# Tile meanings
WALL = 1
PELLET = 2
POWER = 3
EMPTY = 0

# Grid layout (7x7) based on example
MAZE_LAYOUT: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
TILE_SIZE = 60  # nice size on desktop
MARGIN = 24     # margin around maze
SCREEN_WIDTH = COLS * TILE_SIZE + MARGIN * 2
SCREEN_HEIGHT = ROWS * TILE_SIZE + MARGIN * 2 + 60  # extra for UI bar
FPS = 60

# Speeds (pixels per frame)
PACMAN_SPEED = 3
GHOST_SPEED = 2
FRIGHTENED_GHOST_SPEED = 1

# Power up duration (seconds)
POWER_DURATION = 7.0

# Directions
DIR_VECTORS = {
    'STOP': (0, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
}
DIR_KEYS = {
    pygame.K_UP: 'UP',
    pygame.K_DOWN: 'DOWN',
    pygame.K_LEFT: 'LEFT',
    pygame.K_RIGHT: 'RIGHT',
}


def grid_to_pixel(col: int, row: int) -> Tuple[int, int]:
    x = MARGIN + col * TILE_SIZE + TILE_SIZE // 2
    y = MARGIN + row * TILE_SIZE + TILE_SIZE // 2
    return x, y


def is_wall(grid, col, row) -> bool:
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return True
    return grid[row][col] == WALL


def available_dirs(grid, col, row) -> List[str]:
    options = []
    for name, (dx, dy) in DIR_VECTORS.items():
        if name == 'STOP':
            continue
        nc, nr = col + dx, row + dy
        if not is_wall(grid, nc, nr):
            options.append(name)
    return options


def opposite_dir(dir_name: str) -> str:
    mapping = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    return mapping.get(dir_name, 'STOP')


class Actor:
    def __init__(self, start_col: int, start_row: int):
        self.col = start_col
        self.row = start_row
        self.x, self.y = grid_to_pixel(start_col, start_row)
        self.dir = 'STOP'
        self.next_dir = 'STOP'
        self.speed = 0

    def set_dir(self, direction: str):
        self.next_dir = direction

    def at_center_of_tile(self) -> bool:
        cx, cy = grid_to_pixel(self.col, self.row)
        return abs(self.x - cx) <= 2 and abs(self.y - cy) <= 2

    def snap_to_center(self):
        self.x, self.y = grid_to_pixel(self.col, self.row)

    def move_pixel(self, dx: int, dy: int, speed: int):
        self.x += dx * speed
        self.y += dy * speed

        # update tile indices when crossing tile centers
        cx, cy = grid_to_pixel(self.col, self.row)
        # Move to next tile center if passed midpoint in direction of travel
        if dx == 1 and self.x > cx:
            self.col += 1
        elif dx == -1 and self.x < cx:
            self.col -= 1
        elif dy == 1 and self.y > cy:
            self.row += 1
        elif dy == -1 and self.y < cy:
            self.row -= 1


class Pacman(Actor):
    def __init__(self, start_col: int, start_row: int):
        super().__init__(start_col, start_row)
        self.speed = PACMAN_SPEED
        self.alive = True
        self.mouth_phase = 0.0

    def update(self, grid):
        if not self.alive:
            return

        # Try to turn into next_dir if possible at tile center
        if self.at_center_of_tile():
            if self.next_dir != self.dir:
                ndx, ndy = DIR_VECTORS[self.next_dir]
                nc, nr = self.col + ndx, self.row + ndy
                if not is_wall(grid, nc, nr):
                    self.dir = self.next_dir
            # If current direction blocked, stop
            cdx, cdy = DIR_VECTORS[self.dir]
            nc, nr = self.col + cdx, self.row + cdy
            if is_wall(grid, nc, nr):
                self.dir = 'STOP'

        dx, dy = DIR_VECTORS[self.dir]
        if self.dir != 'STOP':
            self.move_pixel(dx, dy, self.speed)

        # Clamp to tile center when close
        if self.at_center_of_tile():
            self.snap_to_center()

        # animate mouth
        self.mouth_phase = (self.mouth_phase + 0.15) % (2 * 3.14159)

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        radius = TILE_SIZE // 2 - 6
        # Simple circle Pacman
        pygame.draw.circle(surface, YELLOW, (px, py), radius)


class Ghost(Actor):
    def __init__(self, start_col: int, start_row: int, color: Tuple[int, int, int]):
        super().__init__(start_col, start_row)
        self.base_speed = GHOST_SPEED
        self.speed = self.base_speed
        self.color = color
        self.spawn = (start_col, start_row)
        self.dir = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        self.frightened = False
        self.eaten = False

    def reset(self):
        self.col, self.row = self.spawn
        self.x, self.y = grid_to_pixel(self.col, self.row)
        self.dir = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        self.frightened = False
        self.eaten = False
        self.speed = self.base_speed

    def update(self, grid):
        # Adjust speed by state
        self.speed = FRIGHTENED_GHOST_SPEED if self.frightened else self.base_speed

        # At tile center, possibly choose new direction
        if self.at_center_of_tile():
            options = available_dirs(grid, self.col, self.row)
            # Do not reverse unless dead end
            if opposite_dir(self.dir) in options and len(options) > 1:
                options.remove(opposite_dir(self.dir))
            if options:
                # Random choice (simple AI)
                self.dir = random.choice(options)

        dx, dy = DIR_VECTORS[self.dir]
        self.move_pixel(dx, dy, self.speed)

        if self.at_center_of_tile():
            self.snap_to_center()

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        radius = TILE_SIZE // 2 - 8
        color = CYAN if self.frightened and not self.eaten else self.color
        pygame.draw.circle(surface, color, (px, py), radius)
        # eyes
        eye_offset = radius // 2
        pygame.draw.circle(surface, WHITE, (px - eye_offset//2, py - eye_offset//2), 4)
        pygame.draw.circle(surface, WHITE, (px + eye_offset//2, py - eye_offset//2), 4)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Contoh Pacman')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 36, bold=True)

        self.grid = [row[:] for row in MAZE_LAYOUT]
        self.score = 0
        self.game_over = False
        self.power_active = False
        self.power_ends_at = 0.0

        # Spawn positions (choose walkable tiles)
        self.pacman = Pacman(1, 1)
        ghost_spawns = [(COLS - 2, 1), (1, ROWS - 2)]
        self.ghosts = [
            Ghost(ghost_spawns[0][0], ghost_spawns[0][1], ORANGE),
            Ghost(ghost_spawns[1][0], ghost_spawns[1][1], PINK),
        ]

        # Count pellets
        self.total_pellets = sum(cell in (PELLET, POWER) for row in self.grid for cell in row)

    def reset(self):
        self.grid = [row[:] for row in MAZE_LAYOUT]
        self.score = 0
        self.game_over = False
        self.power_active = False
        self.power_ends_at = 0.0
        self.pacman = Pacman(1, 1)
        for g in self.ghosts:
            g.reset()
        self.total_pellets = sum(cell in (PELLET, POWER) for row in self.grid for cell in row)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.reset()
                if event.key in DIR_KEYS:
                    self.pacman.set_dir(DIR_KEYS[event.key])

    def update(self):
        if self.game_over:
            return

        # Update Pacman
        self.pacman.update(self.grid)

        # Eat pellets when centered on a tile
        if self.pacman.at_center_of_tile():
            r, c = self.pacman.row, self.pacman.col
            tile = self.grid[r][c]
            if tile == PELLET:
                self.grid[r][c] = EMPTY
                self.score += 10
                self.total_pellets -= 1
            elif tile == POWER:
                self.grid[r][c] = EMPTY
                self.score += 50
                self.total_pellets -= 1
                self.activate_power()

        # Update ghosts
        for g in self.ghosts:
            g.update(self.grid)

        # Power mode timer
        if self.power_active and time.time() > self.power_ends_at:
            self.deactivate_power()

        # Check collisions
        self.check_collisions()

        # Win condition
        if self.total_pellets <= 0:
            self.game_over = True

    def activate_power(self):
        self.power_active = True
        self.power_ends_at = time.time() + POWER_DURATION
        for g in self.ghosts:
            g.frightened = True
            g.eaten = False

    def deactivate_power(self):
        self.power_active = False
        for g in self.ghosts:
            g.frightened = False
            g.eaten = False

    def check_collisions(self):
        # distance-based collision
        px, py = self.pacman.x, self.pacman.y
        for g in self.ghosts:
            gx, gy = g.x, g.y
            dist2 = (px - gx) ** 2 + (py - gy) ** 2
            rad = (TILE_SIZE // 2 - 6) + (TILE_SIZE // 2 - 8)
            if dist2 <= (rad * 0.6) ** 2:  # overlap threshold
                if self.power_active and not g.eaten:
                    # Eat ghost
                    g.eaten = True
                    g.reset()
                    # Keep other ghosts in frightened state until timer ends
                    self.score += 200
                elif not self.power_active:
                    self.pacman.alive = False
                    self.game_over = True

    def draw_maze(self, surface):
        # Fill background
        surface.fill(BLACK)

        # Play area background
        pygame.draw.rect(surface, GREY, (MARGIN - 8, MARGIN - 8, COLS * TILE_SIZE + 16, ROWS * TILE_SIZE + 16), border_radius=8)

        # Draw tiles
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                x = MARGIN + c * TILE_SIZE
                y = MARGIN + r * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                if tile == WALL:
                    pygame.draw.rect(surface, DARK_BLUE, rect)
                    pygame.draw.rect(surface, BLUE, rect, 4)
                elif tile in (PELLET, POWER, EMPTY):
                    # floor
                    pygame.draw.rect(surface, BLACK, rect)
                    # pellets
                    if tile == PELLET:
                        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                        pygame.draw.circle(surface, YELLOW, (cx, cy), 5)
                    elif tile == POWER:
                        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                        pygame.draw.circle(surface, WHITE, (cx, cy), 10)

    def draw_ui(self, surface):
        bar_y = MARGIN + ROWS * TILE_SIZE + 12
        text = f"Score: {self.score}"
        if self.game_over:
            if self.total_pellets <= 0:
                status = "YOU WIN! Press R to restart"
            else:
                status = "GAME OVER! Press R to restart"
        else:
            if self.power_active:
                remaining = max(0, int(self.power_ends_at - time.time()))
                status = f"POWER! {remaining}s"
            else:
                status = ""
        score_surf = self.font.render(text, True, WHITE)
        surface.blit(score_surf, (MARGIN, bar_y))
        if status:
            status_surf = self.font.render(status, True, WHITE)
            surface.blit(status_surf, (MARGIN + 220, bar_y))

    def draw(self):
        self.draw_maze(self.screen)

        # Draw entities
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)

        # UI
        self.draw_ui(self.screen)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            msg = "YOU WIN!" if self.total_pellets <= 0 else "GAME OVER"
            msg2 = "Press R to Restart"
            surf = self.big_font.render(msg, True, WHITE)
            surf2 = self.font.render(msg2, True, WHITE)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(surf2, (SCREEN_WIDTH // 2 - surf2.get_width() // 2, SCREEN_HEIGHT // 2 + 6))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_input()
            self.update()
            self.draw()


if __name__ == '__main__':
    Game().run()
