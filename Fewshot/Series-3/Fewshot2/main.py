import sys
import math
import random
import time
import pygame

# ---------------
# Game Constants
# ---------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
YELLOW = (255, 204, 0)
RED = (220, 20, 60)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 102, 255)

# Maze legend
# 1 = Wall, 0 = Empty path, 2 = Small pellet, 3 = Power pellet
MAZE_LAYOUT = [
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
TILE_SIZE = 64  # Each tile is 64x64 px
MAZE_PIXEL_W = COLS * TILE_SIZE
MAZE_PIXEL_H = ROWS * TILE_SIZE
# Center the maze within the screen
OFFSET_X = (SCREEN_WIDTH - MAZE_PIXEL_W) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAZE_PIXEL_H) // 2

# Gameplay settings
PACMAN_SPEED = 3.0   # pixels per frame
GHOST_SPEED = 2.5    # pixels per frame
FRIGHTENED_SPEED = 1.5
POWER_DURATION = 6.0  # seconds
START_LIVES = 3

# Utility
DIR_VECTORS = {
    'STOP': pygame.Vector2(0, 0),
    'UP': pygame.Vector2(0, -1),
    'DOWN': pygame.Vector2(0, 1),
    'LEFT': pygame.Vector2(-1, 0),
    'RIGHT': pygame.Vector2(1, 0),
}
OPPOSITE = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}


def grid_to_pixel(gx, gy):
    return pygame.Vector2(OFFSET_X + gx * TILE_SIZE + TILE_SIZE / 2,
                          OFFSET_Y + gy * TILE_SIZE + TILE_SIZE / 2)


def pixel_to_grid(px, py):
    gx = int((px - OFFSET_X) // TILE_SIZE)
    gy = int((py - OFFSET_Y) // TILE_SIZE)
    return gx, gy


def is_wall(gx, gy):
    if 0 <= gy < ROWS and 0 <= gx < COLS:
        return MAZE_LAYOUT[gy][gx] == 1
    return True


def is_center_of_tile(pos):
    # A position is considered centered if close to tile center
    cx = OFFSET_X + round((pos.x - OFFSET_X) / TILE_SIZE) * TILE_SIZE + TILE_SIZE / 2
    cy = OFFSET_Y + round((pos.y - OFFSET_Y) / TILE_SIZE) * TILE_SIZE + TILE_SIZE / 2
    return (abs(pos.x - cx) < 2) and (abs(pos.y - cy) < 2)


def legal_directions(gpos):
    gx, gy = gpos
    options = []
    for name, vec in [('UP', DIR_VECTORS['UP']), ('DOWN', DIR_VECTORS['DOWN']),
                      ('LEFT', DIR_VECTORS['LEFT']), ('RIGHT', DIR_VECTORS['RIGHT'])]:
        nx, ny = gx + int(vec.x), gy + int(vec.y)
        if not is_wall(nx, ny):
            options.append(name)
    return options


class Pacman:
    def __init__(self, grid_start):
        self.grid = pygame.Vector2(grid_start)
        self.pos = grid_to_pixel(int(self.grid.x), int(self.grid.y))
        self.dir_name = 'STOP'
        self.next_dir = 'STOP'
        self.radius = TILE_SIZE * 0.35
        self.alive = True
        self.lives = START_LIVES
        self.mouth_angle = 0
        self.mouth_opening = True
        self.score = 0

    def reset_to_start(self, grid_start):
        self.grid = pygame.Vector2(grid_start)
        self.pos = grid_to_pixel(int(self.grid.x), int(self.grid.y))
        self.dir_name = 'STOP'
        self.next_dir = 'STOP'

    def update(self, dt):
        # Handle turning at tile centers
        if self.next_dir != self.dir_name and self.next_dir != 'STOP' and is_center_of_tile(self.pos):
            gx, gy = pixel_to_grid(self.pos.x, self.pos.y)
            vec = DIR_VECTORS[self.next_dir]
            if not is_wall(gx + int(vec.x), gy + int(vec.y)):
                self.dir_name = self.next_dir

        # Move forward if possible
        vec = DIR_VECTORS[self.dir_name]
        if vec.length_squared() > 0:
            speed = PACMAN_SPEED
            new_pos = self.pos + vec * speed
            # Check wall collision by peeking ahead from center-based grid
            gx, gy = pixel_to_grid(new_pos.x, new_pos.y)
            # To make movement smooth, prevent crossing wall boundaries by checking next tile from current center
            if not is_wall(gx, gy):
                self.pos = new_pos
            else:
                # Snap to center to avoid jitter
                cx, cy = grid_to_pixel(*pixel_to_grid(self.pos.x, self.pos.y))
                self.pos.update(cx, cy)
                self.dir_name = 'STOP'

        # Update grid coord
        self.grid.update(*pixel_to_grid(self.pos.x, self.pos.y))

        # Animate mouth
        if self.mouth_opening:
            self.mouth_angle += 6
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= 6
            if self.mouth_angle <= 0:
                self.mouth_opening = True

    def draw(self, surface):
        # Draw Pacman as a pie (arc)
        direction = self.dir_name if self.dir_name != 'STOP' else 'RIGHT'
        angle_offset = {
            'RIGHT': 0,
            'LEFT': 180,
            'UP': 90,
            'DOWN': 270,
        }[direction]
        mouth = math.radians(self.mouth_angle)
        start_angle = math.radians(angle_offset) + mouth
        end_angle = math.radians(angle_offset) - mouth + 2 * math.pi
        pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        # Draw mouth by covering with background arc
        pygame.draw.arc(surface, BLACK, pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                                                    self.radius * 2, self.radius * 2),
                        start_angle, end_angle, int(self.radius))


class Ghost:
    def __init__(self, grid_start, color, seed=None):
        self.grid_start = pygame.Vector2(grid_start)
        self.grid = pygame.Vector2(grid_start)
        self.pos = grid_to_pixel(int(self.grid.x), int(self.grid.y))
        self.color = color
        self.dir_name = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        self.radius = TILE_SIZE * 0.35
        self.frightened = False
        self.frightened_timer = 0.0
        self.rng = random.Random(seed)

    def set_frightened(self):
        self.frightened = True
        self.frightened_timer = POWER_DURATION

    def update(self, dt):
        # Update frightened timer
        if self.frightened:
            self.frightened_timer -= dt
            if self.frightened_timer <= 0:
                self.frightened = False

        # Movement logic: random at intersections, avoid reversing unless forced
        vec = DIR_VECTORS.get(self.dir_name, DIR_VECTORS['STOP'])
        speed = FRIGHTENED_SPEED if self.frightened else GHOST_SPEED

        # If at tile center, potentially choose a new direction
        if is_center_of_tile(self.pos):
            gx, gy = int(self.grid.x), int(self.grid.y)
            options = legal_directions((gx, gy))
            # Do not choose to go into a wall; already filtered
            # Avoid immediate reverse unless it's the only choice
            if self.dir_name in options and len(options) > 1:
                options_no_reverse = [d for d in options if d != OPPOSITE.get(self.dir_name, '')]
            else:
                options_no_reverse = options
            if options_no_reverse:
                self.dir_name = self.rng.choice(options_no_reverse)
            elif options:
                self.dir_name = self.rng.choice(options)
            vec = DIR_VECTORS[self.dir_name]

        # Attempt to move
        new_pos = self.pos + vec * speed
        gx, gy = pixel_to_grid(new_pos.x, new_pos.y)
        if not is_wall(gx, gy):
            self.pos = new_pos
        else:
            # Hit wall; pick another direction next frame
            if is_center_of_tile(self.pos):
                gx, gy = int(self.grid.x), int(self.grid.y)
                options = legal_directions((gx, gy))
                options = [d for d in options if d != OPPOSITE.get(self.dir_name, '')] or options
                if options:
                    self.dir_name = self.rng.choice(options)

        self.grid.update(*pixel_to_grid(self.pos.x, self.pos.y))

    def draw(self, surface):
        # Ghost is circle with little rectangle on bottom (simple)
        color = BLUE if self.frightened else self.color
        # Flash when frightened time is almost over
        if self.frightened and self.frightened_timer < 2.0 and int(self.frightened_timer * 4) % 2 == 0:
            color = WHITE
        x, y = int(self.pos.x), int(self.pos.y)
        r = int(self.radius)
        # Body
        pygame.draw.circle(surface, color, (x, y - r // 4), r)
        pygame.draw.rect(surface, color, pygame.Rect(x - r, y - r // 4, 2 * r, r))
        # Eyes (simple)
        eye_color = WHITE if not self.frightened else BLACK
        pygame.draw.circle(surface, eye_color, (x - r // 3, y - r // 8), r // 5)
        pygame.draw.circle(surface, eye_color, (x + r // 3, y - r // 8), r // 5)

    def reset_to_start(self):
        self.grid = self.grid_start.copy()
        self.pos = grid_to_pixel(int(self.grid.x), int(self.grid.y))
        self.dir_name = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        self.frightened = False
        self.frightened_timer = 0.0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Contoh Pacman')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 22)
        self.big_font = pygame.font.SysFont('arial', 36, bold=True)

        # Build pellets from layout
        self.pellets = set()
        self.power_pellets = set()
        for y in range(ROWS):
            for x in range(COLS):
                val = MAZE_LAYOUT[y][x]
                if val == 2:
                    self.pellets.add((x, y))
                elif val == 3:
                    self.power_pellets.add((x, y))

        # Start positions: choose a path tile
        pac_start = (1, 1)
        ghost1_start = (COLS - 2, 1)
        ghost2_start = (COLS - 2, ROWS - 2)

        self.pacman = Pacman(pac_start)
        self.ghosts = [
            Ghost(ghost1_start, RED, seed=1),
            Ghost(ghost2_start, CYAN, seed=2),
        ]

        self.power_timer = 0.0
        self.game_over = False
        self.win = False

    def reset_after_death(self):
        # Reset positions but keep pellets/score/lives
        pac_start = (1, 1)
        self.pacman.reset_to_start(pac_start)
        for g in self.ghosts:
            g.reset_to_start()
        self.power_timer = 0.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pacman.next_dir = 'UP'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pacman.next_dir = 'DOWN'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pacman.next_dir = 'LEFT'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pacman.next_dir = 'RIGHT'

    def update(self, dt):
        if self.game_over or self.win:
            return

        self.pacman.update(dt)
        for g in self.ghosts:
            g.update(dt)

        # Eating pellets
        gx, gy = int(self.pacman.grid.x), int(self.pacman.grid.y)
        if (gx, gy) in self.pellets:
            self.pellets.remove((gx, gy))
            self.pacman.score += 10
        if (gx, gy) in self.power_pellets:
            self.power_pellets.remove((gx, gy))
            self.pacman.score += 50
            self.power_timer = POWER_DURATION
            for g in self.ghosts:
                g.set_frightened()

        # Update power timer
        if self.power_timer > 0:
            self.power_timer -= dt

        # Collisions with ghosts
        for g in self.ghosts:
            if (self.pacman.pos - g.pos).length() < (self.pacman.radius + g.radius) * 0.8:
                if g.frightened:
                    # Eat ghost
                    self.pacman.score += 200
                    g.reset_to_start()
                else:
                    # Pacman dies
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.game_over = True
                    self.reset_after_death()
                    break

        # Win condition
        if not self.pellets and not self.power_pellets:
            self.win = True

    def draw_maze(self, surface):
        # Draw background
        surface.fill(BLACK)
        # Draw maze walls and tiles
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if MAZE_LAYOUT[y][x] == 1:
                    pygame.draw.rect(surface, BLUE, rect, border_radius=8)
                else:
                    # draw a subtle grid background
                    pygame.draw.rect(surface, (10, 10, 10), rect)

        # Draw pellets
        for (x, y) in self.pellets:
            center = grid_to_pixel(x, y)
            pygame.draw.circle(surface, WHITE, (int(center.x), int(center.y)), 5)
        # Draw power pellets (blink)
        blink_on = (pygame.time.get_ticks() // 300) % 2 == 0
        for (x, y) in self.power_pellets:
            center = grid_to_pixel(x, y)
            if blink_on:
                pygame.draw.circle(surface, ORANGE, (int(center.x), int(center.y)), 10)
            else:
                pygame.draw.circle(surface, (180, 100, 0), (int(center.x), int(center.y)), 10)

    def draw_hud(self, surface):
        score_text = self.font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        surface.blit(score_text, (20, 20))
        surface.blit(lives_text, (20, 48))
        if self.power_timer > 0:
            power_text = self.font.render(f"Power: {self.power_timer:.1f}s", True, ORANGE)
            surface.blit(power_text, (20, 76))

        if self.game_over:
            over = self.big_font.render("GAME OVER", True, RED)
            surface.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, 20))
        if self.win:
            win = self.big_font.render("YOU WIN!", True, ORANGE)
            surface.blit(win, (SCREEN_WIDTH // 2 - win.get_width() // 2, 20))

    def draw(self):
        self.draw_maze(self.screen)
        # Draw characters
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)
        # HUD
        self.draw_hud(self.screen)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if (self.game_over or self.win) and event.key == pygame.K_r:
                        # Restart
                        self.__init__()

            self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
