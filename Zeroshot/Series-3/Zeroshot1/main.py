import pygame
import random
import math
import sys
from typing import List, Tuple

# -----------------------------
# Game Constants
# -----------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 20  # 800x600 -> 40x30 grid
COLS = SCREEN_WIDTH // TILE_SIZE
ROWS = SCREEN_HEIGHT // TILE_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 90, 190)
NAVY = (0, 40, 100)
YELLOW = (255, 210, 0)
ORANGE = (255, 130, 0)
PINK = (255, 105, 180)
RED = (220, 50, 50)
CYAN = (0, 220, 220)
GREY = (180, 180, 180)

# Gameplay
PACMAN_SPEED = 2.0  # pixels per frame (grid aligned logic controls turning)
GHOST_SPEED = 1.8
VULNERABLE_TIME = 8.0  # seconds
GHOST_RESPAWN_POS = (COLS // 2, ROWS // 2)
START_LIVES = 3
SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST = 200

# Tile Types
WALL = '1'
EMPTY = '0'
DOT = '2'
POWER = '3'


def make_level() -> List[List[str]]:
    """Create a 40x30 grid level.
    '1' = wall, '0' = path (no pellet), '2' = dot, '3' = power pellet
    Layout is hardcoded by placing rectangles and corridors.
    """
    # Start with all dots
    grid = [[DOT for _ in range(COLS)] for _ in range(ROWS)]

    # Outer walls and blank corners for power pellets
    for r in range(ROWS):
        for c in range(COLS):
            if r == 0 or r == ROWS - 1 or c == 0 or c == COLS - 1:
                grid[r][c] = WALL

    # Carve main tunnels (no pellets to guide paths)
    def carve_rect(x1, y1, x2, y2, value=WALL):
        for r in range(y1, y2 + 1):
            for c in range(x1, x2 + 1):
                if 0 <= r < ROWS and 0 <= c < COLS:
                    grid[r][c] = value

    def carve_hallway(c1, r1, c2, r2, value=EMPTY):
        if r1 == r2:
            for c in range(min(c1, c2), max(c1, c2) + 1):
                if 0 <= r1 < ROWS and 0 <= c < COLS:
                    grid[r1][c] = value
        elif c1 == c2:
            for r in range(min(r1, r2), max(r1, r2) + 1):
                if 0 <= r < ROWS and 0 <= c1 < COLS:
                    grid[r][c1] = value

    # Create some wall blocks
    carve_rect(5, 4, 10, 6, WALL)
    carve_rect(29, 4, 34, 6, WALL)
    carve_rect(5, 23, 10, 25, WALL)
    carve_rect(29, 23, 34, 25, WALL)

    carve_rect(18, 4, 21, 8, WALL)
    carve_rect(18, 21, 21, 25, WALL)

    carve_rect(10, 12, 14, 17, WALL)
    carve_rect(25, 12, 29, 17, WALL)

    # Ghost house (center box)
    carve_rect(COLS // 2 - 3, ROWS // 2 - 2, COLS // 2 + 3, ROWS // 2 + 2, WALL)
    # Door to ghost house (remove a wall tile to make a door)
    grid[ROWS // 2 + 2][COLS // 2] = EMPTY

    # Horizontal and vertical corridors
    carve_hallway(2, 8, COLS - 3, 8, EMPTY)
    carve_hallway(2, ROWS - 9, COLS - 3, ROWS - 9, EMPTY)
    carve_hallway(8, 2, 8, ROWS - 3, EMPTY)
    carve_hallway(COLS - 9, 2, COLS - 9, ROWS - 3, EMPTY)

    # Center cross corridors
    carve_hallway(COLS // 2, 2, COLS // 2, ROWS - 3, EMPTY)
    carve_hallway(2, ROWS // 2, COLS - 3, ROWS // 2, EMPTY)

    # Create tunnels (wrap) left-right in middle row
    middle_row = ROWS // 2
    grid[middle_row][0] = EMPTY
    grid[middle_row][COLS - 1] = EMPTY

    # Turn empty spaces into paths without pellets, keep remaining dots where walkable
    # Ensure walls remain walls
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] not in (WALL, EMPTY):
                # Non-wall cells default to dots (pellets)
                grid[r][c] = DOT

    # Place power pellets at four corners inside the borders
    corners = [(1, 1), (1, COLS - 2), (ROWS - 2, 1), (ROWS - 2, COLS - 2)]
    for rr, cc in corners:
        grid[rr][cc] = POWER

    # Clear pellets inside ghost house
    for r in range(ROWS // 2 - 2, ROWS // 2 + 3):
        for c in range(COLS // 2 - 3, COLS // 2 + 4):
            if grid[r][c] != WALL:
                grid[r][c] = EMPTY

    return grid


def tile_to_pixels(tc: Tuple[int, int]) -> Tuple[int, int]:
    return tc[0] * TILE_SIZE + TILE_SIZE // 2, tc[1] * TILE_SIZE + TILE_SIZE // 2


def pixels_to_tile(px: float, py: float) -> Tuple[int, int]:
    return int(px // TILE_SIZE), int(py // TILE_SIZE)


def is_wall(grid: List[List[str]], col: int, row: int) -> bool:
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return True
    return grid[row][col] == WALL


class Pacman:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = TILE_SIZE // 2 - 2
        self.dir = (0, 0)  # current direction as (dc, dr)
        self.next_dir = (0, 0)  # buffered input
        self.speed = PACMAN_SPEED
        self.mouth_angle = 0.0
        self.mouth_opening = 1

    def reset(self, x: int, y: int):
        self.x = x
        self.y = y
        self.dir = (0, 0)
        self.next_dir = (0, 0)

    def update(self, grid: List[List[str]]):
        # Try to turn if requested and possible
        if self.next_dir != self.dir and self.can_move(grid, self.next_dir):
            # Allow turning only near tile centers to keep alignment
            if self.at_center_of_tile():
                self.dir = self.next_dir

        # Move forward if possible; if blocked, stop at next tile boundary
        if self.can_move(grid, self.dir):
            self.x += self.dir[0] * self.speed
            self.y += self.dir[1] * self.speed
            self._wrap_tunnel()
        else:
            # Snap to center if drifting into a wall
            self.snap_to_center()

        # Animate mouth
        self.mouth_angle += 0.2 * self.mouth_opening
        if self.mouth_angle > 1.2 or self.mouth_angle < 0.1:
            self.mouth_opening *= -1

    def _wrap_tunnel(self):
        # wrap horizontally at middle row ends
        col, row = pixels_to_tile(self.x, self.y)
        if row == ROWS // 2:
            if self.x < 0:
                self.x = SCREEN_WIDTH - 1
            elif self.x >= SCREEN_WIDTH:
                self.x = 0

    def can_move(self, grid: List[List[str]], d: Tuple[int, int]) -> bool:
        if d == (0, 0):
            return True
        nx = self.x + d[0] * self.speed
        ny = self.y + d[1] * self.speed
        # Check next tile based on direction
        # Use a small offset so that movement remains grid aligned
        look_x = nx + d[0] * (self.radius - 2)
        look_y = ny + d[1] * (self.radius - 2)
        c, r = pixels_to_tile(look_x, look_y)
        return not is_wall(grid, c, r)

    def at_center_of_tile(self) -> bool:
        cx = (self.x - TILE_SIZE // 2) % TILE_SIZE
        cy = (self.y - TILE_SIZE // 2) % TILE_SIZE
        return abs(cx) < 2 and abs(cy) < 2

    def snap_to_center(self):
        c, r = pixels_to_tile(self.x, self.y)
        self.x = c * TILE_SIZE + TILE_SIZE // 2
        self.y = r * TILE_SIZE + TILE_SIZE // 2

    def draw(self, surface: pygame.Surface):
        # Draw Pac-Man with mouth animation
        angle = 30 + int(math.sin(self.mouth_angle) * 20)
        direction_angle = {
            (1, 0): 0,
            (-1, 0): 180,
            (0, -1): 90,
            (0, 1): 270,
            (0, 0): 0,
        }[self.dir]
        start_angle = math.radians(direction_angle - angle)
        end_angle = math.radians(direction_angle + angle)
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        # Erase mouth wedge
        mouth_rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)
        pygame.draw.polygon(surface, BLACK, [
            (self.x, self.y),
            (self.x + math.cos(start_angle) * self.radius, self.y - math.sin(start_angle) * self.radius),
            (self.x + math.cos(end_angle) * self.radius, self.y - math.sin(end_angle) * self.radius)
        ])


class Ghost:
    NORMAL = 0
    VULNERABLE = 1
    EYES = 2  # returning to base

    def __init__(self, color: Tuple[int, int, int], start_tile: Tuple[int, int]):
        self.color = color
        self.start_tile = start_tile
        px, py = tile_to_pixels(start_tile)
        self.x = float(px)
        self.y = float(py)
        self.radius = TILE_SIZE // 2 - 2
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.state = Ghost.NORMAL
        self.vulnerable_timer = 0.0
        self.speed = GHOST_SPEED

    def reset(self):
        px, py = tile_to_pixels(self.start_tile)
        self.x = float(px)
        self.y = float(py)
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.state = Ghost.NORMAL
        self.vulnerable_timer = 0.0

    def set_vulnerable(self):
        if self.state != Ghost.EYES:
            self.state = Ghost.VULNERABLE
            self.vulnerable_timer = VULNERABLE_TIME

    def eaten(self):
        self.state = Ghost.EYES

    def at_center_of_tile(self) -> bool:
        cx = (self.x - TILE_SIZE // 2) % TILE_SIZE
        cy = (self.y - TILE_SIZE // 2) % TILE_SIZE
        return abs(cx) < 2 and abs(cy) < 2

    def possible_directions(self, grid: List[List[str]]) -> List[Tuple[int, int]]:
        c, r = pixels_to_tile(self.x, self.y)
        dirs = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nc = c + d[0]
            nr = r + d[1]
            if not is_wall(grid, nc, nr):
                dirs.append(d)
        return dirs

    def choose_dir(self, grid: List[List[str]], target: Tuple[float, float]):
        # Simple greedy choice at intersections (prefer not reversing unless dead end)
        dirs = self.possible_directions(grid)
        if not dirs:
            return (0, 0)

        # Avoid reversing unless necessary
        reverse = (-self.dir[0], -self.dir[1])
        if len(dirs) > 1 and reverse in dirs:
            dirs.remove(reverse)

        # In vulnerable mode, try to run away from target
        best_d = None
        best_score = None
        for d in dirs:
            nx = self.x + d[0] * TILE_SIZE
            ny = self.y + d[1] * TILE_SIZE
            dist = (nx - target[0]) ** 2 + (ny - target[1]) ** 2
            score = -dist if self.state == Ghost.NORMAL else dist
            if best_score is None or score > best_score:
                best_score = score
                best_d = d
        # Add small randomness
        if random.random() < 0.1 and len(dirs) > 1:
            best_d = random.choice(dirs)
        return best_d

    def update(self, grid: List[List[str]], pac_pos: Tuple[float, float], base_tile: Tuple[int, int], dt: float):
        # State timers
        if self.state == Ghost.VULNERABLE:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.state = Ghost.NORMAL

        # Choose target
        if self.state == Ghost.EYES:
            target_px, target_py = tile_to_pixels(base_tile)
            speed = self.speed * 1.5
        else:
            target_px, target_py = pac_pos
            speed = self.speed

        # Move; turn only at centers for tidy grid movement
        if self.at_center_of_tile():
            new_dir = self.choose_dir(grid, (target_px, target_py))
            if new_dir:
                self.dir = new_dir

        self.x += self.dir[0] * speed
        self.y += self.dir[1] * speed

        # Wrap through tunnel similar to Pacman
        c, r = pixels_to_tile(self.x, self.y)
        if r == ROWS // 2:
            if self.x < 0:
                self.x = SCREEN_WIDTH - 1
            elif self.x >= SCREEN_WIDTH:
                self.x = 0

        # If eyes reached base, return to normal at start tile
        if self.state == Ghost.EYES:
            bc, br = base_tile
            if (c, r) == (bc, br):
                self.reset()

    def draw(self, surface: pygame.Surface):
        if self.state == Ghost.VULNERABLE:
            color = GREY if self.vulnerable_timer < 2.0 and int(self.vulnerable_timer * 10) % 2 == 0 else CYAN
        elif self.state == Ghost.EYES:
            color = WHITE
        else:
            color = self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        # simple eyes
        eye_offset_x = 4 if self.dir[0] >= 0 else -4
        pygame.draw.circle(surface, WHITE, (int(self.x - 4 + eye_offset_x), int(self.y - 4)), 3)
        pygame.draw.circle(surface, WHITE, (int(self.x + 4 + eye_offset_x), int(self.y - 4)), 3)
        pygame.draw.circle(surface, NAVY, (int(self.x - 4 + eye_offset_x), int(self.y - 4)), 1)
        pygame.draw.circle(surface, NAVY, (int(self.x + 4 + eye_offset_x), int(self.y - 4)), 1)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Pygame")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 40, bold=True)

        self.grid = make_level()
        self.base_tile = (COLS // 2, ROWS // 2 + 1)

        # Place Pacman near bottom center
        pac_start = (COLS // 2, ROWS - 3)
        px, py = tile_to_pixels(pac_start)
        self.pacman = Pacman(px, py)

        # Ghosts with different colors and starting tiles
        self.ghosts = [
            Ghost(RED, (COLS // 2 - 2, ROWS // 2)),
            Ghost(PINK, (COLS // 2 + 2, ROWS // 2)),
            Ghost(ORANGE, (COLS // 2 - 2, ROWS // 2 + 2)),
            Ghost(BLUE, (COLS // 2 + 2, ROWS // 2 + 2)),
        ]

        self.score = 0
        self.lives = START_LIVES
        self.game_over = False
        self.win = False

        # Count initial pellets
        self.total_pellets = sum(1 for r in range(ROWS) for c in range(COLS) if self.grid[r][c] in (DOT, POWER))

    def reset_positions_after_death(self):
        # Reset Pacman and ghosts but keep pellets and score
        pac_start = (COLS // 2, ROWS - 3)
        px, py = tile_to_pixels(pac_start)
        self.pacman.reset(px, py)
        for g in self.ghosts:
            g.reset()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman.next_dir = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.pacman.next_dir = (1, 0)
        elif keys[pygame.K_UP]:
            self.pacman.next_dir = (0, -1)
        elif keys[pygame.K_DOWN]:
            self.pacman.next_dir = (0, 1)

    def update(self, dt: float):
        if self.game_over:
            return

        self.pacman.update(self.grid)

        # Pacman pellet consumption
        c, r = pixels_to_tile(self.pacman.x, self.pacman.y)
        if 0 <= r < ROWS and 0 <= c < COLS:
            if self.grid[r][c] == DOT:
                self.grid[r][c] = EMPTY
                self.score += SCORE_DOT
                self.total_pellets -= 1
            elif self.grid[r][c] == POWER:
                self.grid[r][c] = EMPTY
                self.score += SCORE_POWER
                for g in self.ghosts:
                    g.set_vulnerable()
                self.total_pellets -= 1

        # Win condition
        if self.total_pellets <= 0:
            self.game_over = True
            self.win = True

        # Update ghosts
        pac_pos = (self.pacman.x, self.pacman.y)
        for g in self.ghosts:
            g.update(self.grid, pac_pos, self.base_tile, dt)

        # Collisions Pacman-Ghost
        for g in self.ghosts:
            if self._collide_circle(self.pacman.x, self.pacman.y, self.pacman.radius, g.x, g.y, g.radius):
                if g.state == Ghost.VULNERABLE:
                    g.eaten()
                    self.score += SCORE_GHOST
                elif g.state == Ghost.NORMAL:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self.win = False
                    else:
                        self.reset_positions_after_death()
                    break

    @staticmethod
    def _collide_circle(x1, y1, r1, x2, y2, r2) -> bool:
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2

    def draw_grid(self):
        # Draw walls
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                if tile == WALL:
                    pygame.draw.rect(self.screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # draw pellets
                    if tile == DOT:
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 3)
                    elif tile == POWER:
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 6)

    def draw_hud(self):
        score_surf = self.font.render(f"Skor: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Nyawa: {self.lives}", True, WHITE)
        self.screen.blit(score_surf, (10, 5))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 5))

    def draw_center_text(self, text: str, color=WHITE, y_offset=0):
        surf = self.big_font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.screen.blit(surf, rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if self.game_over and event.key == pygame.K_r:
                        # Restart the whole game
                        self.__init__()

            if not self.game_over:
                self.handle_input()
                self.update(dt)

            # Draw
            self.screen.fill(BLACK)
            self.draw_grid()
            for g in self.ghosts:
                g.draw(self.screen)
            self.pacman.draw(self.screen)
            self.draw_hud()

            if self.game_over:
                if self.win:
                    self.draw_center_text("MENANG!", YELLOW, -20)
                else:
                    self.draw_center_text("GAME OVER", RED, -20)
                self.draw_center_text("Tekan R untuk restart", WHITE, 30)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
