import sys
import math
import random
import pygame

# -------------------------------
# Config & Constants
# -------------------------------
TILE_SIZE = 40  # Pixel per grid tile
FPS = 60
PACMAN_SPEED = 3  # pixels per frame
GHOST_SPEED = 2   # pixels per frame (slower than Pacman)
POWER_DURATION = 8.0  # seconds

# Colors
BLACK = (0, 0, 0)
NAVY = (12, 20, 69)
BLUE = (33, 66, 199)
WHITE = (255, 255, 255)
YELLOW = (255, 205, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
ORANGE = (255, 165, 0)
GREY = (120, 120, 120)

# -------------------------------
# Maze Layout (Grid)
# 1 = Wall, 0 = Empty path, 2 = Pellet, 3 = Power pellet
# -------------------------------
maze_layout = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

ROWS = len(maze_layout)
COLS = len(maze_layout[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 60  # extra space for HUD
HUD_HEIGHT = 60

# Directions
DIR_NONE = pygame.Vector2(0, 0)
DIR_UP = pygame.Vector2(0, -1)
DIR_DOWN = pygame.Vector2(0, 1)
DIR_LEFT = pygame.Vector2(-1, 0)
DIR_RIGHT = pygame.Vector2(1, 0)
DIRS = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]


def grid_to_pixel(col: int, row: int) -> pygame.Vector2:
    return pygame.Vector2(col * TILE_SIZE + TILE_SIZE // 2,
                          row * TILE_SIZE + TILE_SIZE // 2)


def pixel_to_grid(pos: pygame.Vector2) -> tuple[int, int]:
    return int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE)


def is_wall(col: int, row: int) -> bool:
    if 0 <= row < ROWS and 0 <= col < COLS:
        return maze_layout[row][col] == 1
    return True  # out of bounds treated as wall


def is_path(col: int, row: int) -> bool:
    if 0 <= row < ROWS and 0 <= col < COLS:
        return maze_layout[row][col] != 1
    return False


class Pacman:
    def __init__(self, start_col, start_row):
        self.pos = grid_to_pixel(start_col, start_row)
        self.dir = DIR_NONE
        self.next_dir = DIR_NONE
        self.radius = TILE_SIZE // 2 - 4
        self.mouth_angle = 0
        self.mouth_opening = True

    def update(self):
        # Try to change direction if aligned to grid center
        if self.is_centered_on_tile():
            if self.can_move(self.next_dir):
                self.dir = self.next_dir
        # Move if possible
        new_pos = self.pos + self.dir * PACMAN_SPEED
        next_col, next_row = pixel_to_grid(new_pos)
        if self.can_move(self.dir, future_pos=new_pos):
            self.pos = new_pos
        else:
            # Snap to center along blocked axis
            center = grid_to_pixel(*pixel_to_grid(self.pos))
            if self.dir.x != 0:
                self.pos.y = center.y
            if self.dir.y != 0:
                self.pos.x = center.x

        # Animate mouth
        if self.dir.length_squared() > 0:
            if self.mouth_opening:
                self.mouth_angle += 8
                if self.mouth_angle >= 40:
                    self.mouth_opening = False
            else:
                self.mouth_angle -= 8
                if self.mouth_angle <= 0:
                    self.mouth_opening = True
        else:
            self.mouth_angle = 0

    def is_centered_on_tile(self) -> bool:
        center = grid_to_pixel(*pixel_to_grid(self.pos))
        return (abs(self.pos.x - center.x) < 2 and abs(self.pos.y - center.y) < 2)

    def can_move(self, direction: pygame.Vector2, future_pos: pygame.Vector2 | None = None) -> bool:
        if direction.length_squared() == 0:
            return True
        probe_pos = future_pos if future_pos is not None else (self.pos + direction * PACMAN_SPEED)
        # Check the tile in the direction of travel near the edge of the tile
        offset = direction * (self.radius - 4)
        test_point = probe_pos + offset
        col, row = pixel_to_grid(test_point)
        return is_path(col, row)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.next_dir = DIR_UP
            elif event.key == pygame.K_DOWN:
                self.next_dir = DIR_DOWN
            elif event.key == pygame.K_LEFT:
                self.next_dir = DIR_LEFT
            elif event.key == pygame.K_RIGHT:
                self.next_dir = DIR_RIGHT

    def draw(self, surface: pygame.Surface):
        # Draw Pacman as a pie (arc) based on direction
        angle_offset = 0
        if self.dir == DIR_RIGHT:
            angle_offset = 0
        elif self.dir == DIR_LEFT:
            angle_offset = 180
        elif self.dir == DIR_UP:
            angle_offset = 90
        elif self.dir == DIR_DOWN:
            angle_offset = 270
        start_angle = math.radians(self.mouth_angle + angle_offset)
        end_angle = math.radians(360 - self.mouth_angle + angle_offset)
        pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Mouth: draw over with background color to simulate mouth
        mouth_radius = self.radius
        pygame.draw.polygon(surface, BLACK, [
            (self.pos.x, self.pos.y),
            (self.pos.x + mouth_radius * math.cos(start_angle), self.pos.y - mouth_radius * math.sin(start_angle)),
            (self.pos.x + mouth_radius * math.cos(end_angle), self.pos.y - mouth_radius * math.sin(end_angle))
        ])


class Ghost:
    def __init__(self, start_col, start_row, color):
        self.pos = grid_to_pixel(start_col, start_row)
        self.dir = random.choice(DIRS)
        self.color = color
        self.radius = TILE_SIZE // 2 - 6
        self.frightened = False
        self.respawn_col = start_col
        self.respawn_row = start_row

    def set_frightened(self, frightened: bool):
        self.frightened = frightened

    def update(self):
        speed = GHOST_SPEED
        # Move forward if possible, otherwise choose a new direction
        new_pos = self.pos + self.dir * speed
        if self.can_move(self.dir, new_pos):
            self.pos = new_pos
        else:
            self.choose_new_direction()
        # At intersections, occasionally pick a new direction
        if self.is_centered_on_tile():
            if random.random() < 0.2:
                self.choose_new_direction(avoid_reverse=True)

    def is_centered_on_tile(self) -> bool:
        center = grid_to_pixel(*pixel_to_grid(self.pos))
        return (abs(self.pos.x - center.x) < 2 and abs(self.pos.y - center.y) < 2)

    def can_move(self, direction: pygame.Vector2, future_pos: pygame.Vector2 | None = None) -> bool:
        if direction.length_squared() == 0:
            return True
        probe_pos = future_pos if future_pos is not None else (self.pos + direction * GHOST_SPEED)
        offset = direction * (self.radius - 4)
        test_point = probe_pos + offset
        col, row = pixel_to_grid(test_point)
        return is_path(col, row)

    def choose_new_direction(self, avoid_reverse: bool = False):
        options = []
        for d in DIRS:
            if avoid_reverse and (d.x == -self.dir.x and d.y == -self.dir.y):
                continue
            if self.can_move(d):
                options.append(d)
        if not options:
            # must reverse
            self.dir = self.dir * -1
        else:
            self.dir = random.choice(options)

    def respawn(self):
        self.pos = grid_to_pixel(self.respawn_col, self.respawn_row)
        self.dir = random.choice(DIRS)
        self.frightened = False

    def draw(self, surface: pygame.Surface):
        color = CYAN if self.frightened else self.color
        x, y = int(self.pos.x), int(self.pos.y)
        # Body
        pygame.draw.circle(surface, color, (x, y - self.radius // 3), self.radius)
        rect = pygame.Rect(x - self.radius, y - self.radius // 3, self.radius * 2, self.radius)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        # Eyes
        eye_offset = 6
        pygame.draw.circle(surface, WHITE, (x - eye_offset, y - eye_offset), 5)
        pygame.draw.circle(surface, WHITE, (x + eye_offset, y - eye_offset), 5)
        pygame.draw.circle(surface, BLACK, (x - eye_offset, y - eye_offset), 2)
        pygame.draw.circle(surface, BLACK, (x + eye_offset, y - eye_offset), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Contoh Pacman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)

        # Game state
        self.reset()

    def reset(self):
        # Deep copy of layout for pellets so we can consume them
        self.grid = [row[:] for row in maze_layout]
        # Find a suitable start for Pacman (first non-wall)
        start_pac = self.find_first_path_cell()
        self.pacman = Pacman(*start_pac)

        # Place two ghosts at different path cells
        path_cells = self.get_all_path_cells()
        random.shuffle(path_cells)
        g1_col, g1_row = path_cells[0]
        g2_col, g2_row = path_cells[1]
        self.ghosts = [
            Ghost(g1_col, g1_row, PINK),
            Ghost(g2_col, g2_row, ORANGE),
        ]

        self.score = 0
        self.game_over = False
        self.win = False
        self.power_timer = 0.0

    def find_first_path_cell(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] in (0, 2, 3):
                    return (c, r)
        return (1, 1)

    def get_all_path_cells(self):
        cells = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] != 1:
                    cells.append((c, r))
        return cells

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.game_over or self.win:
                    if event.key == pygame.K_r:
                        self.reset()
                        continue
            self.pacman.handle_input(event)

    def update(self, dt):
        if self.game_over or self.win:
            return
        # Update Pacman
        self.pacman.update()
        # Pellet consumption
        col, row = pixel_to_grid(self.pacman.pos)
        if 0 <= row < ROWS and 0 <= col < COLS:
            if self.grid[row][col] == 2:
                self.grid[row][col] = 0
                self.score += 10
            elif self.grid[row][col] == 3:
                self.grid[row][col] = 0
                self.score += 50
                self.power_timer = POWER_DURATION
                for g in self.ghosts:
                    g.set_frightened(True)

        # Update ghosts
        for g in self.ghosts:
            g.update()

        # Handle collisions Pacman vs Ghosts
        for g in self.ghosts:
            if self.circle_collision(self.pacman.pos, self.pacman.radius, g.pos, g.radius):
                if self.power_timer > 0 and g.frightened:
                    # Eat ghost
                    self.score += 200
                    g.respawn()
                else:
                    # Pacman dies -> game over
                    self.game_over = True

        # Update timers
        if self.power_timer > 0:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.power_timer = 0
                for g in self.ghosts:
                    g.set_frightened(False)

        # Win condition: all pellets eaten
        if not any(2 in row for row in self.grid) and not any(3 in row for row in self.grid):
            self.win = True

    @staticmethod
    def circle_collision(p1: pygame.Vector2, r1: int, p2: pygame.Vector2, r2: int) -> bool:
        return p1.distance_to(p2) <= (r1 + r2 - 4)

    def draw(self):
        self.screen.fill(BLACK)
        # Draw maze area
        maze_surface = pygame.Surface((WIDTH, HEIGHT - HUD_HEIGHT))
        maze_surface.fill(NAVY)
        self.draw_maze(maze_surface)
        self.pacman.draw(maze_surface)
        for g in self.ghosts:
            g.draw(maze_surface)
        self.screen.blit(maze_surface, (0, 0))

        # Draw HUD
        self.draw_hud(self.screen)

        # Overlays
        if self.game_over:
            self.draw_center_text("Game Over - Press R to Restart", self.big_font, RED)
        elif self.win:
            self.draw_center_text("You Win! - Press R to Restart", self.big_font, YELLOW)

        pygame.display.flip()

    def draw_maze(self, surface: pygame.Surface):
        # Draw tiles
        for row in range(ROWS):
            for col in range(COLS):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                tile = self.grid[row][col]
                if tile == 1:
                    pygame.draw.rect(surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # pellets
                    if tile == 2:
                        pygame.draw.circle(surface, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4)
                    elif tile == 3:
                        pygame.draw.circle(surface, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 8)

    def draw_hud(self, surface: pygame.Surface):
        hud_rect = pygame.Rect(0, HEIGHT - HUD_HEIGHT, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, GREY, hud_rect)
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        surface.blit(score_text, (16, HEIGHT - HUD_HEIGHT + 18))
        # Power timer
        if self.power_timer > 0:
            t = max(0, int(self.power_timer + 0.5))
            power_text = self.font.render(f"Power: {t}s", True, BLACK)
            surface.blit(power_text, (WIDTH - 140, HEIGHT - HUD_HEIGHT + 18))

    def draw_center_text(self, text: str, font: pygame.font.Font, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, (HEIGHT - HUD_HEIGHT) // 2))
        self.screen.blit(surf, rect)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
