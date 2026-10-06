import sys
import math
import random
import pygame

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 20  # 40 x 30 grid fits 800x600
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 222)
YELLOW = (255, 204, 0)
RED = (220, 20, 60)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (100, 100, 100)

VULNERABLE_BLUE = (0, 102, 255)
VULNERABLE_FLASH = (255, 255, 255)

# Scores
DOT_SCORE = 10
POWER_DOT_SCORE = 50
GHOST_SCORE = 200

# Timers (in seconds)
POWER_DURATION = 8
FLASH_START = 5.5  # start flashing after this many seconds

# Maze legend: '1' wall, '0' empty path, '2' dot, '3' power pellet, 'B' ghost base
# Layout is 30 rows x 40 cols
MAZE_LAYOUT = [
    "1111111111111111111111111111111111111111",
    "1222222222221111222222222222111122222221",
    "1211112111121111211112111122111121111121",
    "1310002100022222200002000222220002000131",
    "1211112111121111211112111121111211111121",
    "1222222222221111222222222222111122222221",
    "1111112111111111111111111111111112111111",
    "1000012100000000000000000000000012100001",
    "1111012111112111111111111121111121111011",
    "1222012000022100002222000022100002001221",
    "1211111111122111211111111222111211111121",
    "1200000000020000200000000020000200000021",
    "1211112111121111211112111121111211111121",
    "1222212100022222B00000002222200021222221",
    "1111112101111111111111111111111012111111",
    "1000002100000000000000000000000021000001",
    "1011112111112111111111111121111121111101",
    "1022222000022100002222000022100002222201",
    "1011111111122111211111111222111211111101",
    "1000000000020000200000000020000200000001",
    "1111112111121111211112111121111212111111",
    "1222222100022222000000000222220002122221",
    "1211111111111111111111111111111111111121",
    "1200000000000000210000200000000000000021",
    "1211111111111111211112111111111111111121",
    "1222222222221111000000000011112222222221",
    "1111111111121111111111111111111111111111",
    "1200000000020000000000000000000200000021",
    "1222222222222222222222222222222222222221",
    "1111111111111111111111111111111111111111",
]

# Convert '0' paths to dotted paths '2' except special tiles
# Place power pellets at the four outer corners of the inner maze

def prepare_maze(layout):
    grid = [list(row) for row in layout]
    rows = len(grid)
    cols = len(grid[0])
    # Fill paths with dots
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '0':
                grid[r][c] = '2'
    # Ensure power pellets exist in four corners of walkable area
    candidates = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    placed = 0
    for rr, cc in candidates:
        if grid[rr][cc] != '1':
            grid[rr][cc] = '3'
            placed += 1
    # If there is a ghost base 'B', keep it empty path (no dots)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'B':
                grid[r][c] = '0'
    return grid

GRID = prepare_maze(MAZE_LAYOUT)

# Helpers

def grid_to_pixel(c, r):
    return c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2


def pixel_to_grid(x, y):
    return x // TILE_SIZE, y // TILE_SIZE


def is_wall(c, r):
    if 0 <= r < ROWS and 0 <= c < COLS:
        return GRID[r][c] == '1'
    return True


def is_walkable(c, r):
    if 0 <= r < ROWS and 0 <= c < COLS:
        return GRID[r][c] != '1'
    return False


def find_ghost_base():
    # Find center area where 'B' was originally — approximate by looking for open area near center
    center_c, center_r = COLS // 2, ROWS // 2
    # search a small box for a non-wall tile to be base
    for radius in range(1, 6):
        for r in range(center_r - radius, center_r + radius + 1):
            for c in range(center_c - radius, center_c + radius + 1):
                if 0 <= r < ROWS and 0 <= c < COLS and GRID[r][c] != '1':
                    return c, r
    return 1, 1


PACMAN_START = (1, 1)
GHOST_BASE = find_ghost_base()

class Pacman:
    def __init__(self):
        self.grid_c, self.grid_r = PACMAN_START
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.radius = TILE_SIZE // 2 - 2
        self.speed = 2.0
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.alive = True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.next_dir = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.next_dir = (1, 0)
        elif keys[pygame.K_UP]:
            self.next_dir = (0, -1)
        elif keys[pygame.K_DOWN]:
            self.next_dir = (0, 1)

    def update(self):
        # Align to grid center for smooth turns
        target_c = int(round(self.x / TILE_SIZE))
        target_r = int(round(self.y / TILE_SIZE))
        center_x, center_y = grid_to_pixel(target_c, target_r)
        # If close to center, snap a bit
        if abs(self.x - center_x) < 0.2:
            self.x = center_x
        if abs(self.y - center_y) < 0.2:
            self.y = center_y

        # Attempt to change direction if possible (only when aligned sufficiently)
        if self.next_dir != self.dir:
            if abs(self.x - center_x) < 0.5 and abs(self.y - center_y) < 0.5:
                nxc, nyc = target_c + self.next_dir[0], target_r + self.next_dir[1]
                if is_walkable(nxc, nyc):
                    self.dir = self.next_dir

        # Move if the next tile is not a wall
        dx, dy = self.dir
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        ahead_c = int(round(new_x / TILE_SIZE))
        ahead_r = int(round(new_y / TILE_SIZE))

        # Check collision against walls using tile ahead
        if is_walkable(ahead_c, ahead_r):
            self.x, self.y = new_x, new_y
        else:
            # Stop at center of current tile
            self.x, self.y = center_x, center_y
            self.dir = (0, 0)

        # Update grid position
        self.grid_c, self.grid_r = pixel_to_grid(int(self.x), int(self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        self.grid_c, self.grid_r = PACMAN_START
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.alive = True

class Ghost:
    def __init__(self, color, start_cell, name="ghost"):
        self.color = color
        self.name = name
        self.grid_c, self.grid_r = start_cell
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.radius = TILE_SIZE // 2 - 3
        self.speed = 1.6
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.vulnerable = False
        self.vulnerable_timer = 0.0
        self.flash = False

    def set_vulnerable(self):
        self.vulnerable = True
        self.vulnerable_timer = POWER_DURATION
        self.flash = False

    def update(self, dt, pacman_pos):
        # Handle vulnerable timer
        if self.vulnerable:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.vulnerable = False
                self.flash = False
            elif self.vulnerable_timer <= POWER_DURATION - FLASH_START:
                # start flashing
                # alternate color every 0.2s
                self.flash = int(self.vulnerable_timer * 5) % 2 == 0

        # Movement logic
        pc, pr = pacman_pos
        c, r = pixel_to_grid(int(self.x), int(self.y))

        # At intersections (aligned), choose direction
        center_x, center_y = grid_to_pixel(c, r)
        aligned = abs(self.x - center_x) < 0.5 and abs(self.y - center_y) < 0.5
        if aligned:
            self.x, self.y = center_x, center_y
            choices = []
            for d in [(1,0), (-1,0), (0,1), (0,-1)]:
                # avoid reversing unless no other option
                if (-d[0], -d[1]) == self.dir:
                    continue
                nc, nr = c + d[0], r + d[1]
                if is_walkable(nc, nr):
                    choices.append(d)
            if not choices:
                # must reverse if blocked
                rev = (-self.dir[0], -self.dir[1])
                nc, nr = c + rev[0], r + rev[1]
                if is_walkable(nc, nr):
                    self.dir = rev
            else:
                # If vulnerable, try to move away from Pacman, else move towards Pacman
                def dist_after(d):
                    nc, nr = c + d[0], r + d[1]
                    return (nc - pc) ** 2 + (nr - pr) ** 2
                if self.vulnerable:
                    # maximize distance
                    self.dir = max(choices, key=dist_after)
                else:
                    # minimize distance (chase)
                    self.dir = min(choices, key=dist_after)

        # Move
        dx, dy = self.dir
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        ahead_c, ahead_r = pixel_to_grid(int(new_x), int(new_y))
        if is_walkable(ahead_c, ahead_r):
            self.x, self.y = new_x, new_y
        else:
            # stop at center and force re-pick next frame
            self.x, self.y = center_x, center_y

        self.grid_c, self.grid_r = pixel_to_grid(int(self.x), int(self.y))

    def draw(self, surface):
        if self.vulnerable:
            color = VULNERABLE_FLASH if self.flash else VULNERABLE_BLUE
        else:
            color = self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        # eyes (simple)
        eye_offset = 4
        pygame.draw.circle(surface, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
        pygame.draw.circle(surface, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)

    def reset_to_base(self, base_cell):
        self.grid_c, self.grid_r = base_cell
        self.x, self.y = grid_to_pixel(self.grid_c, self.grid_r)
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.vulnerable = False
        self.flash = False
        self.vulnerable_timer = 0.0

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman - Python/Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 48, bold=True)
        # Regenerate the GRID so dots/power-pellets reset on a fresh game
        global GRID
        GRID = prepare_maze(MAZE_LAYOUT)

        self.pacman = Pacman()
        # place ghosts around base
        bc, br = GHOST_BASE
        self.ghosts = [
            Ghost(RED, (bc, br), name="blinky"),
            Ghost(PINK, (max(1, bc - 2), br), name="pinky"),
            Ghost(CYAN, (bc, max(1, br - 2)), name="inky"),
            Ghost(ORANGE, (min(COLS - 2, bc + 2), br), name="clyde"),
        ]

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

    def reset_round(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset_to_base(GHOST_BASE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if self.game_over or self.win:
                    if event.key == pygame.K_RETURN:
                        # Restart full game
                        self.__init__()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        self.pacman.handle_input()

    def update(self, dt):
        if self.game_over or self.win:
            return

        self.pacman.update()

        # Eat dots/power dots
        c, r = self.pacman.grid_c, self.pacman.grid_r
        if GRID[r][c] == '2':
            GRID[r][c] = '0'
            self.score += DOT_SCORE
        elif GRID[r][c] == '3':
            GRID[r][c] = '0'
            self.score += POWER_DOT_SCORE
            for g in self.ghosts:
                g.set_vulnerable()

        # Update ghosts
        for g in self.ghosts:
            g.update(dt, (self.pacman.grid_c, self.pacman.grid_r))

        # Collisions with ghosts
        for g in self.ghosts:
            if self._collide_circle(self.pacman, g):
                if g.vulnerable:
                    # Send ghost to base and add score
                    g.reset_to_base(GHOST_BASE)
                    self.score += GHOST_SCORE
                else:
                    # Pacman loses a life and reset round
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.reset_round()
                    return

        # Win condition: no more dots/power dots
        if not any('2' in row or '3' in row for row in GRID):
            self.win = True

    @staticmethod
    def _collide_circle(a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        dist2 = dx * dx + dy * dy
        r = a.radius + b.radius - 4  # slightly forgiving
        return dist2 <= r * r

    def draw_grid(self, surface):
        # Draw walls and pellets
        for r in range(ROWS):
            for c in range(COLS):
                tile = GRID[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                if tile == '1':
                    pygame.draw.rect(surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    # Path background
                    pygame.draw.rect(surface, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                    if tile == '2':
                        # Dot
                        pygame.draw.circle(surface, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 2)
                    elif tile == '3':
                        # Power pellet
                        pygame.draw.circle(surface, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 5)

    def draw_hud(self, surface):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
        surface.blit(score_surf, (10, 5))
        surface.blit(lives_surf, (WIDTH - lives_surf.get_width() - 10, 5))

    def draw_end_screen(self, surface):
        if self.game_over:
            text = self.big_font.render("GAME OVER", True, WHITE)
        else:
            text = self.big_font.render("YOU WIN!", True, WHITE)
        sub = self.font.render("Press Enter to Restart or Esc to Quit", True, GREY)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)
        self.draw_hud(self.screen)
        if self.game_over or self.win:
            self.draw_end_screen(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
