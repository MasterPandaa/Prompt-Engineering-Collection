import sys
import math
import random
import pygame
from pygame import Rect

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GREEN = (0, 200, 0)
GREY = (100, 100, 100)
NAVY = (0, 0, 80)
VULN_BLUE = (0, 0, 255)
VULN_WHITE = (255, 255, 255)

# Maze legend
# '1' = wall
# '0' = empty corridor (no dot)
# '2' = dot (pellet)
# '3' = power pellet
# 'H' = ghost house door (treated as wall for Pacman, open for ghosts returning)

# A 28x31 maze inspired by classic layout (simplified)
# Ensures outer border walls and corridors with dots/power pellets
MAZE_LAYOUT = [
    "1111111111111111111111111111",
    "1222222222111222222222222221",
    "1211112112111211112111111121",
    "1320002112222211002110000121",
    "1211112112111211112111111121",
    "1222222222222222222222222221",
    "121111211111H1111112111111121",
    "1211112111111111112111111121",
    "1222222222111222222222222221",
    "1111112111111111111112111111",
    "0000012112222222222112110000",
    "1111012112111111112112111111",
    "1222212112133333312112222221",
    "1111012112111111112112011111",
    "0000012112222222222112000000",
    "1111112111111111111112111111",
    "1222222222111222222222222221",
    "1211112112111211112111111121",
    "1320002112222211002110000121",
    "1211112112111211112111111121",
    "1222222222222222222222222221",
    "121111211111H1111112111111121",
    "1211112111111111112111111121",
    "1222222222111222222222222221",
    "1111111111111111111111111111",
    "1000000000000000000000000001",
    "1333333333333333333333333331",
    "1222222222222222222222222221",
    "1211111111111111111111111121",
    "1222222222222222222222222221",
    "1111111111111111111111111111",
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])

# Determine tile size to fit within 800x600 while keeping aspect
TILE_SIZE = min(SCREEN_WIDTH // COLS, SCREEN_HEIGHT // ROWS)
MAZE_WIDTH = COLS * TILE_SIZE
MAZE_HEIGHT = ROWS * TILE_SIZE
OFFSET_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2

# Gameplay settings
PACMAN_SPEED = 100  # pixels per second
GHOST_SPEED = 90    # normal ghost speed
VULNERABLE_SPEED = 70
POWER_DURATION = 7.0  # seconds
START_LIVES = 3
DOT_SCORE = 10
POWER_SCORE = 50
GHOST_SCORE = 200


def grid_to_world(col, row):
    return OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2, OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2


def rect_for_cell(col, row):
    return Rect(OFFSET_X + col * TILE_SIZE, OFFSET_Y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)


def is_wall(col, row):
    if 0 <= row < ROWS and 0 <= col < COLS:
        return MAZE_LAYOUT[row][col] == '1' or MAZE_LAYOUT[row][col] == 'H'
    return True


def is_door(col, row):
    if 0 <= row < ROWS and 0 <= col < COLS:
        return MAZE_LAYOUT[row][col] == 'H'
    return False


def is_inside_grid(col, row):
    return 0 <= row < ROWS and 0 <= col < COLS


def neighbors(col, row):
    for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nc, nr = col + dc, row + dr
        if is_inside_grid(nc, nr) and not is_wall(nc, nr):
            yield (nc, nr)


class Entity:
    def __init__(self, col, row, color, radius):
        self.col = col
        self.row = row
        x, y = grid_to_world(col, row)
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.radius = radius
        self.dir = (0, 0)
        self.target_dir = (0, 0)

    @property
    def rect(self):
        return Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def grid_pos(self):
        return (int((self.x - OFFSET_X) // TILE_SIZE), int((self.y - OFFSET_Y) // TILE_SIZE))

    def center_in_cell(self):
        self.x, self.y = grid_to_world(self.col, self.row)


class Pacman(Entity):
    def __init__(self, col, row):
        super().__init__(col, row, YELLOW, TILE_SIZE // 2 - 2)
        self.lives = START_LIVES
        self.score = 0
        self.power_timer = 0.0

    def set_direction(self, dc, dr):
        self.target_dir = (dc, dr)

    def update(self, dt, walls):
        # Try to update direction when near center of a cell
        cx, cy = grid_to_world(self.col, self.row)
        if abs(self.x - cx) <= 2 and abs(self.y - cy) <= 2:
            # snap to center
            self.x, self.y = cx, cy
            self.dir = try_change_dir(self.col, self.row, self.target_dir)

        speed = PACMAN_SPEED
        dx = self.dir[0] * speed * dt
        dy = self.dir[1] * speed * dt

        # Move axis-aligned with collision against walls
        self.x += dx
        if hits_wall(self.rect):
            # undo and stop x
            self.x -= dx
        self.y += dy
        if hits_wall(self.rect):
            self.y -= dy

        # Update logical grid cell
        self.col, self.row = self.grid_pos()

        # Power timer decay
        if self.power_timer > 0:
            self.power_timer = max(0.0, self.power_timer - dt)

    def draw(self, surface):
        # Simple pacman circle. Optionally animate mouth by direction
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class Ghost(Entity):
    MODES = ('normal', 'vulnerable', 'eyes')

    def __init__(self, col, row, color, home_col, home_row, behavior='chase'):
        super().__init__(col, row, color, TILE_SIZE // 2 - 3)
        self.spawn = (col, row)
        self.home = (home_col, home_row)
        self.mode = 'normal'
        self.behavior = behavior  # 'chase' or 'random'
        self.flash_timer = 0.0

    def set_vulnerable(self):
        if self.mode != 'eyes':
            self.mode = 'vulnerable'
            self.flash_timer = 0.0

    def set_normal(self):
        self.mode = 'normal'

    def set_eyes(self):
        self.mode = 'eyes'

    def speed(self):
        if self.mode == 'vulnerable':
            return VULNERABLE_SPEED
        return GHOST_SPEED

    def update(self, dt, pacman):
        # If eyes, path back to home
        if self.mode == 'eyes':
            target = self.home
            self._move_towards(dt, target)
            # If close to home, respawn to spawn and normal mode
            if (self.col, self.row) == self.home:
                self.col, self.row = self.spawn
                self.center_in_cell()
                self.set_normal()
            return

        # At cell center, maybe decide new direction
        cx, cy = grid_to_world(self.col, self.row)
        at_center = abs(self.x - cx) <= 2 and abs(self.y - cy) <= 2
        if at_center:
            self.x, self.y = cx, cy
            options = []
            for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc, nr = self.col + d[0], self.row + d[1]
                if not is_wall(nc, nr):
                    # avoid reversing unless no other option
                    if (-d[0], -d[1]) != self.dir or len(options) == 0:
                        options.append(d)
            chosen = self._choose_dir(options, pacman)
            self.dir = chosen

        # Move
        speed = self.speed()
        dx = self.dir[0] * speed * dt
        dy = self.dir[1] * speed * dt
        self.x += dx
        if hits_wall(self.rect):
            self.x -= dx
            self.dir = (0, 0)
        self.y += dy
        if hits_wall(self.rect):
            self.y -= dy
            self.dir = (0, 0)
        self.col, self.row = self.grid_pos()

    def _choose_dir(self, options, pacman):
        if not options:
            return (0, 0)
        if self.mode == 'vulnerable':
            # move away from Pacman: maximize distance
            best = None
            best_dist = -1
            for d in options:
                nc, nr = self.col + d[0], self.row + d[1]
                dist = (nc - pacman.col) ** 2 + (nr - pacman.row) ** 2
                if dist > best_dist:
                    best_dist = dist
                    best = d
            return best
        if self.behavior == 'random':
            return random.choice(options)
        # chase behavior: minimize distance to Pacman
        best = None
        best_dist = 1e9
        for d in options:
            nc, nr = self.col + d[0], self.row + d[1]
            dist = (nc - pacman.col) ** 2 + (nr - pacman.row) ** 2
            if dist < best_dist:
                best_dist = dist
                best = d
        return best

    def _move_towards(self, dt, target_cell):
        tx, ty = target_cell
        # Simple greedy movement to home
        options = []
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nc, nr = self.col + d[0], self.row + d[1]
            # Eyes can pass through door 'H'
            if is_inside_grid(nc, nr) and MAZE_LAYOUT[nr][nc] != '1':
                options.append(d)
        if options:
            best = None
            best_dist = 1e9
            for d in options:
                nc, nr = self.col + d[0], self.row + d[1]
                dist = (nc - tx) ** 2 + (nr - ty) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best = d
            self.dir = best
        speed = GHOST_SPEED + 30
        dx = self.dir[0] * speed * dt
        dy = self.dir[1] * speed * dt
        self.x += dx
        if hits_wall_eyes(self.rect):
            self.x -= dx
            self.dir = (0, 0)
        self.y += dy
        if hits_wall_eyes(self.rect):
            self.y -= dy
            self.dir = (0, 0)
        self.col, self.row = self.grid_pos()

    def draw(self, surface, t):
        if self.mode == 'vulnerable':
            # flash near end of power timer
            color = VULN_BLUE if int(t * 6) % 2 == 0 else WHITE
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        elif self.mode == 'eyes':
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, BLUE, (int(self.x) - 4, int(self.y) - 2), 3)
            pygame.draw.circle(surface, BLUE, (int(self.x) + 4, int(self.y) - 2), 3)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


def try_change_dir(col, row, target_dir):
    dc, dr = target_dir
    if dc == 0 and dr == 0:
        return (0, 0)
    nc, nr = col + dc, row + dr
    if not is_wall(nc, nr):
        return (dc, dr)
    return (0, 0)


def hits_wall(rect):
    # Check against wall cells only
    # Expand check by overlapping rect with tiles
    left = max(0, (rect.left - OFFSET_X) // TILE_SIZE)
    right = min(COLS - 1, (rect.right - 1 - OFFSET_X) // TILE_SIZE)
    top = max(0, (rect.top - OFFSET_Y) // TILE_SIZE)
    bottom = min(ROWS - 1, (rect.bottom - 1 - OFFSET_Y) // TILE_SIZE)
    for r in range(int(top), int(bottom) + 1):
        for c in range(int(left), int(right) + 1):
            if MAZE_LAYOUT[r][c] == '1' or MAZE_LAYOUT[r][c] == 'H':
                if rect.colliderect(rect_for_cell(c, r)):
                    return True
    return False


def hits_wall_eyes(rect):
    # Eyes phase can go through 'H' door
    left = max(0, (rect.left - OFFSET_X) // TILE_SIZE)
    right = min(COLS - 1, (rect.right - 1 - OFFSET_X) // TILE_SIZE)
    top = max(0, (rect.top - OFFSET_Y) // TILE_SIZE)
    bottom = min(ROWS - 1, (rect.bottom - 1 - OFFSET_Y) // TILE_SIZE)
    for r in range(int(top), int(bottom) + 1):
        for c in range(int(left), int(right) + 1):
            if MAZE_LAYOUT[r][c] == '1':
                if rect.colliderect(rect_for_cell(c, r)):
                    return True
    return False


def load_dots():
    dots = set()
    power = set()
    for r in range(ROWS):
        for c in range(COLS):
            ch = MAZE_LAYOUT[r][c]
            if ch == '2':
                dots.add((c, r))
            elif ch == '3':
                power.add((c, r))
    return dots, power


def draw_maze(surface):
    # Fill background
    surface.fill(BLACK)
    # Draw maze walls
    for r in range(ROWS):
        for c in range(COLS):
            cell = MAZE_LAYOUT[r][c]
            rect = rect_for_cell(c, r)
            if cell == '1':
                pygame.draw.rect(surface, BLUE, rect)
            elif cell == 'H':
                pygame.draw.rect(surface, NAVY, rect)
    # Grid outline for aesthetics (optional)
    # for r in range(ROWS):
    #     for c in range(COLS):
    #         pygame.draw.rect(surface, (20, 20, 20), rect_for_cell(c, r), 1)


def draw_dots(surface, dots, power):
    for (c, r) in dots:
        x, y = grid_to_world(c, r)
        pygame.draw.circle(surface, WHITE, (x, y), max(2, TILE_SIZE // 8))
    for (c, r) in power:
        x, y = grid_to_world(c, r)
        pygame.draw.circle(surface, WHITE, (x, y), max(5, TILE_SIZE // 3))


def handle_pacman_eats(pacman, dots, power):
    # Eat dot or power pellet when centered in a cell
    cell = (pacman.col, pacman.row)
    ate = False
    if cell in dots:
        dots.remove(cell)
        pacman.score += DOT_SCORE
        ate = True
    if cell in power:
        power.remove(cell)
        pacman.score += POWER_SCORE
        pacman.power_timer = POWER_DURATION
        ate = True
    return ate


def check_collisions(pacman, ghosts):
    pac_rect = pacman.rect
    result = []
    for g in ghosts:
        if pac_rect.colliderect(g.rect):
            result.append(g)
    return result


def reset_positions(pacman, ghosts):
    pacman.center_in_cell()
    pacman.dir = (0, 0)
    pacman.target_dir = (0, 0)
    for g in ghosts:
        g.col, g.row = g.spawn
        g.center_in_cell()
        g.dir = (0, 0)
        g.set_normal()


def create_ghosts():
    # Define ghost spawn and home positions (roughly center around H door rows)
    # Find a door 'H' to mark home
    homes = []
    spawns = []
    for r in range(ROWS):
        for c in range(COLS):
            if MAZE_LAYOUT[r][c] == 'H':
                homes.append((c, r))
                # spawn adjacent inside house if possible
                spawns.append((c, r + 1 if r + 1 < ROWS and MAZE_LAYOUT[r + 1][c] != '1' else r))
    if not homes:
        homes = [(COLS // 2, ROWS // 2)]
        spawns = [(COLS // 2, ROWS // 2 + 1)]

    # Select up to 4 ghosts
    ghost_defs = [
        (RED, 'chase'),
        (PINK, 'random'),
        (CYAN, 'chase'),
        (ORANGE, 'random'),
    ]
    ghosts = []
    for i, (color, beh) in enumerate(ghost_defs):
        s = spawns[min(i, len(spawns) - 1)]
        h = homes[min(i, len(homes) - 1)]
        g = Ghost(s[0], s[1], color, h[0], h[1], behavior=beh)
        ghosts.append(g)
    return ghosts


def draw_hud(surface, font, pacman, remaining):
    score_surf = font.render(f"Score: {pacman.score}", True, WHITE)
    lives_surf = font.render(f"Lives: {pacman.lives}", True, WHITE)
    dots_surf = font.render(f"Dots left: {remaining}", True, WHITE)
    surface.blit(score_surf, (10, 10))
    surface.blit(lives_surf, (10, 10 + score_surf.get_height() + 4))
    surface.blit(dots_surf, (10, 10 + score_surf.get_height() + lives_surf.get_height() + 8))


def main():
    pygame.init()
    pygame.display.set_caption("Pacman - Pygame")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # Initialize game state
    # Find a starting position for Pacman (first corridor cell near bottom center)
    start_col, start_row = COLS // 2, ROWS - 2
    # Seek leftwards for a corridor
    for dc in range(COLS):
        c = COLS // 2 - dc
        if c < 1:
            break
        if MAZE_LAYOUT[start_row][c] != '1':
            start_col = c
            break
    pacman = Pacman(start_col, start_row)
    dots, power = load_dots()
    ghosts = create_ghosts()

    running = True
    game_over = False
    win = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over or win:
                    if event.key == pygame.K_r:
                        # reset game
                        pacman = Pacman(start_col, start_row)
                        dots, power = load_dots()
                        ghosts = create_ghosts()
                        game_over = False
                        win = False
                        continue
                if event.key == pygame.K_LEFT:
                    pacman.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.set_direction(1, 0)
                elif event.key == pygame.K_UP:
                    pacman.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    pacman.set_direction(0, 1)

        if not (game_over or win):
            # Update pacman
            pacman.update(dt, None)

            # Eat dots/power
            if handle_pacman_eats(pacman, dots, power):
                # Set ghosts vulnerable when power pellet eaten
                if pacman.power_timer > 0:
                    for g in ghosts:
                        g.set_vulnerable()

            # Update ghosts
            for g in ghosts:
                g.update(dt, pacman)

            # Toggle ghosts back to normal when power ends
            if pacman.power_timer == 0:
                for g in ghosts:
                    if g.mode == 'vulnerable':
                        g.set_normal()

            # Collisions
            hits = check_collisions(pacman, ghosts)
            for g in hits:
                if g.mode == 'vulnerable':
                    g.set_eyes()
                    pacman.score += GHOST_SCORE
                elif g.mode == 'normal':
                    # lose life and reset positions
                    pacman.lives -= 1
                    if pacman.lives <= 0:
                        game_over = True
                    reset_positions(pacman, ghosts)
                    break

            # Win condition
            if len(dots) + len(power) == 0:
                win = True

        # Draw
        draw_maze(screen)
        draw_dots(screen, dots, power)
        pacman.draw(screen)
        t = pygame.time.get_ticks() / 1000.0
        for g in ghosts:
            g.draw(screen, t)
        draw_hud(screen, font, pacman, len(dots) + len(power))

        # Messages
        if game_over:
            msg = font.render("Game Over! Press R to Restart or ESC to Quit", True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))
        elif win:
            msg = font.render("You Win! Press R to Restart or ESC to Quit", True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
