import sys
import random
import math
import pygame

# -----------------------------
# Config
# -----------------------------
TILE_SIZE = 24
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 255)
YELLOW = (255, 216, 0)
RED = (255, 64, 64)
PINK = (255, 144, 208)
CYAN = (64, 255, 255)
ORANGE = (255, 184, 82)
FRIGHT_BLUE = (30, 90, 255)
GREY = (60, 60, 60)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)
ALL_DIRS = [UP, DOWN, LEFT, RIGHT]

# Map legend: '#' wall, '.' pellet, 'o' power pellet, ' ' empty, 'P' pacman spawn, 'G' ghost spawn
MAZE_LAYOUT = [
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
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###GG### ##.#     ",
    "######.## #      # ##.######",
    "      .   # P  P #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

ROWS = len(MAZE_LAYOUT)
COLS = len(MAZE_LAYOUT[0])
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 60  # extra UI bar at bottom

# -----------------------------
# Helpers
# -----------------------------

def add_tuple(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul_tuple(a, s):
    return (a[0] * s, a[1] * s)


def opposite_dir(d):
    return (-d[0], -d[1])


def grid_to_pix(cell):
    return (cell[0] * TILE_SIZE + TILE_SIZE // 2, cell[1] * TILE_SIZE + TILE_SIZE // 2)


def is_centered(pos):
    # pos in pixels, is in center of its tile?
    cx = (pos[0] - TILE_SIZE // 2) % TILE_SIZE
    cy = (pos[1] - TILE_SIZE // 2) % TILE_SIZE
    return cx == 0 and cy == 0


def pix_to_grid(pos):
    return (pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)


# -----------------------------
# Maze / Level
# -----------------------------
class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.pacman_spawns = []
        self.ghost_spawns = []
        self._parse()

    def _parse(self):
        for y, line in enumerate(self.layout):
            for x, ch in enumerate(line):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.pellets.add((x, y))
                elif ch == 'o':
                    self.power_pellets.add((x, y))
                elif ch == 'P':
                    self.pacman_spawns.append((x, y))
                elif ch == 'G':
                    self.ghost_spawns.append((x, y))
        # If no explicit pacman spawn, default center-ish empty cell
        if not self.pacman_spawns:
            for y, line in enumerate(self.layout):
                for x, ch in enumerate(line):
                    if ch in (' ', '.', 'o'):
                        self.pacman_spawns.append((x, y))
                        return

    def is_wall(self, cell):
        x, y = cell
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return True
        # Support tunnels: spaces (' ') are passable, only '#' are solid
        return (x, y) in self.walls

    def draw(self, surf, font, score, lives, power_time):
        # Draw walls
        for (x, y) in self.walls:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, BLUE, rect)

        # Draw pellets
        for (x, y) in self.pellets:
            cx, cy = grid_to_pix((x, y))
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)

        # Draw power pellets (pulsing)
        pulse = 6 + int(2 * math.sin(pygame.time.get_ticks() * 0.008))
        for (x, y) in self.power_pellets:
            cx, cy = grid_to_pix((x, y))
            pygame.draw.circle(surf, WHITE, (cx, cy), pulse)

        # UI bar
        ui_rect = pygame.Rect(0, ROWS * TILE_SIZE, WIDTH, HEIGHT - ROWS * TILE_SIZE)
        pygame.draw.rect(surf, BLACK, ui_rect)
        text = font.render(f"Score: {score}", True, WHITE)
        surf.blit(text, (10, ROWS * TILE_SIZE + 10))
        text2 = font.render(f"Lives: {lives}", True, WHITE)
        surf.blit(text2, (WIDTH - 150, ROWS * TILE_SIZE + 10))
        if power_time > 0:
            text3 = font.render("POWER!", True, ORANGE)
            surf.blit(text3, (WIDTH // 2 - 40, ROWS * TILE_SIZE + 10))


# -----------------------------
# Entities
# -----------------------------
class Player:
    def __init__(self, maze: Maze):
        spawn = maze.pacman_spawns[0]
        self.grid = spawn
        self.pos = list(grid_to_pix(spawn))  # pixel position
        self.dir = STOP
        self.next_dir = STOP
        self.speed = 2.0  # pixels per frame
        self.alive = True
        self.mouth_phase = 0.0

    def set_next_dir(self, d):
        self.next_dir = d

    def can_move(self, maze: Maze, d):
        # check next cell from current grid center
        gx, gy = pix_to_grid(self.pos)
        nx, ny = gx + d[0], gy + d[1]
        return not maze.is_wall((nx, ny))

    def update(self, maze: Maze):
        # Snap turning only at cell centers
        if is_centered(self.pos):
            if self.next_dir != self.dir and self.can_move(maze, self.next_dir):
                self.dir = self.next_dir
            # If current dir blocked, stop
            if not self.can_move(maze, self.dir):
                self.dir = STOP
        # Move
        self.pos[0] += self.dir[0] * self.speed
        self.pos[1] += self.dir[1] * self.speed

        # Wrap tunnels horizontally (if leaving bounds on empty rows)
        if self.pos[0] < -TILE_SIZE // 2:
            self.pos[0] = COLS * TILE_SIZE - TILE_SIZE // 2
        elif self.pos[0] > COLS * TILE_SIZE - TILE_SIZE // 2:
            self.pos[0] = -TILE_SIZE // 2

        # Eat pellets when centered in a cell that contains them
        if is_centered(self.pos):
            self.grid = pix_to_grid(self.pos)

        # Animate mouth
        self.mouth_phase += 0.15

    def draw(self, surf):
        x, y = int(self.pos[0]), int(self.pos[1])
        # Mouth animation
        mouth = 12 + int(6 * (0.5 + 0.5 * math.sin(self.mouth_phase)))
        angle_map = {
            RIGHT: (0, 360 - mouth),
            LEFT: (180 + mouth // 2, 180 - mouth),
            UP: (90 + mouth // 2, 180 - mouth),
            DOWN: (270 + mouth // 2, 180 - mouth),
            STOP: (0, 360),
        }
        start_angle, sweep = angle_map.get(self.dir, (0, 360))
        rect = pygame.Rect(x - TILE_SIZE // 2, y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
        # Draw as pie (arc fill) using polygon approximation
        pygame.draw.circle(surf, YELLOW, (x, y), TILE_SIZE // 2 - 1)
        if sweep < 360:
            # cut a triangle wedge to simulate mouth
            rad1 = math.radians(start_angle)
            rad2 = math.radians((start_angle + sweep) % 360)
            points = [
                (x, y),
                (x + math.cos(rad1) * TILE_SIZE, y - math.sin(rad1) * TILE_SIZE),
                (x + math.cos(rad2) * TILE_SIZE, y - math.sin(rad2) * TILE_SIZE),
            ]
            pygame.draw.polygon(surf, BLACK, points)


class Ghost:
    def __init__(self, maze: Maze, color, spawn):
        self.color = color
        self.maze = maze
        self.spawn = spawn
        self.grid = spawn
        self.pos = list(grid_to_pix(spawn))
        self.dir = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = 2.0  # similar to pacman
        self.frightened = False
        self.respawn_timer = 0

    def available_dirs(self):
        dirs = []
        gx, gy = pix_to_grid(self.pos)
        for d in ALL_DIRS:
            nx, ny = gx + d[0], gy + d[1]
            if not self.maze.is_wall((nx, ny)):
                dirs.append(d)
        return dirs

    def choose_dir(self, player_grid):
        # only choose at center tiles
        if not is_centered(self.pos):
            return self.dir
        options = [d for d in self.available_dirs() if d != opposite_dir(self.dir)]
        if not options:
            options = self.available_dirs()
            if not options:
                return STOP
        if self.frightened:
            # random move when frightened
            return random.choice(options)
        # Greedy towards player by Manhattan distance
        best_d = None
        best_score = 1e9
        gx, gy = pix_to_grid(self.pos)
        px, py = player_grid
        for d in options:
            nx, ny = gx + d[0], gy + d[1]
            score = abs(px - nx) + abs(py - ny)
            if score < best_score:
                best_score = score
                best_d = d
        return best_d or random.choice(options)

    def update(self, player_grid):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            # stay at spawn while respawning
            self.pos = list(grid_to_pix(self.spawn))
            self.dir = STOP
            return
        # adjust direction at intersections
        new_dir = self.choose_dir(player_grid)
        if new_dir is not None:
            self.dir = new_dir
        # move
        self.pos[0] += self.dir[0] * self.speed
        self.pos[1] += self.dir[1] * self.speed
        # wrap tunnels
        if self.pos[0] < -TILE_SIZE // 2:
            self.pos[0] = COLS * TILE_SIZE - TILE_SIZE // 2
        elif self.pos[0] > COLS * TILE_SIZE - TILE_SIZE // 2:
            self.pos[0] = -TILE_SIZE // 2

    def draw(self, surf):
        x, y = int(self.pos[0]), int(self.pos[1])
        color = FRIGHT_BLUE if self.frightened and self.respawn_timer == 0 else self.color
        radius = TILE_SIZE // 2 - 1
        # body
        pygame.draw.circle(surf, color, (x, y), radius)
        # eyes
        eye_dx = 4 * (1 if self.dir[0] >= 0 else -1 if self.dir[0] < 0 else 0)
        eye_dy = 4 * (1 if self.dir[1] > 0 else -1 if self.dir[1] < 0 else 0)
        pygame.draw.circle(surf, WHITE, (x - 5 + eye_dx, y - 5 + eye_dy), 3)
        pygame.draw.circle(surf, WHITE, (x + 5 + eye_dx, y - 5 + eye_dy), 3)


# -----------------------------
# Game
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pacman (Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 42, bold=True)
        self.reset()

    def reset(self):
        self.maze = Maze(MAZE_LAYOUT)
        self.player = Player(self.maze)
        # Setup ghosts - pick up to 4 spawns; if fewer, use center area
        spawn_cells = self.maze.ghost_spawns or [(COLS // 2 - 1, ROWS // 2), (COLS // 2, ROWS // 2), (COLS // 2 + 1, ROWS // 2), (COLS // 2, ROWS // 2 - 1)]
        colors = [RED, PINK, CYAN, ORANGE]
        self.ghosts = []
        for i in range(min(4, len(spawn_cells))):
            self.ghosts.append(Ghost(self.maze, colors[i % len(colors)], spawn_cells[i]))
        self.score = 0
        self.lives = 3
        self.power_timer = 0
        self.game_over = False
        self.win = False

    def update_power_state(self):
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                for g in self.ghosts:
                    g.frightened = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if self.game_over or self.win:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        return
                if event.key == pygame.K_UP:
                    self.player.set_next_dir(UP)
                elif event.key == pygame.K_DOWN:
                    self.player.set_next_dir(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.player.set_next_dir(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.player.set_next_dir(RIGHT)

    def update_player(self):
        if not self.player.alive:
            return
        self.player.update(self.maze)
        # Eat pellets / power pellets when centered
        if is_centered(self.player.pos):
            cell = pix_to_grid(self.player.pos)
            if cell in self.maze.pellets:
                self.maze.pellets.remove(cell)
                self.score += 10
            if cell in self.maze.power_pellets:
                self.maze.power_pellets.remove(cell)
                self.score += 50
                self.power_timer = FPS * 8  # 8 seconds
                for g in self.ghosts:
                    g.frightened = True
        # win condition
        if not self.maze.pellets and not self.maze.power_pellets:
            self.win = True

    def update_ghosts(self):
        for g in self.ghosts:
            g.update(pix_to_grid(self.player.pos))

    def check_collisions(self):
        if not self.player.alive:
            return
        px, py = self.player.pos
        for g in self.ghosts:
            gx, gy = g.pos
            if abs(px - gx) < TILE_SIZE * 0.6 and abs(py - gy) < TILE_SIZE * 0.6:
                if g.frightened and g.respawn_timer == 0:
                    # eat ghost
                    self.score += 200
                    g.respawn_timer = FPS * 2
                    g.frightened = False
                    g.pos = list(grid_to_pix(g.spawn))
                    g.dir = STOP
                else:
                    # player loses life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self.player.alive = False
                    else:
                        # reset positions
                        self.player = Player(self.maze)
                        for ghost in self.ghosts:
                            ghost.pos = list(grid_to_pix(ghost.spawn))
                            ghost.dir = random.choice(ALL_DIRS)
                            ghost.frightened = False

    def draw(self):
        self.screen.fill(BLACK)
        # Draw maze and UI first (pellets, score, lives)
        self.maze.draw(self.screen, self.font, self.score, self.lives, self.power_timer)
        # Draw ghosts then player so player on top
        for g in self.ghosts:
            g.draw(self.screen)
        self.player.draw(self.screen)
        # Messages
        if self.game_over:
            self._draw_center_text("GAME OVER - Press Enter")
        elif self.win:
            self._draw_center_text("YOU WIN! - Press Enter")
        pygame.display.flip()

    def _draw_center_text(self, msg):
        surf = self.big_font.render(msg, True, WHITE)
        rect = surf.get_rect(center=(WIDTH // 2, ROWS * TILE_SIZE // 2))
        self.screen.blit(surf, rect)

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_input()
            if not (self.game_over or self.win):
                self.update_power_state()
                self.update_player()
                self.update_ghosts()
                self.check_collisions()
            self.draw()


if __name__ == "__main__":
    Game().run()
