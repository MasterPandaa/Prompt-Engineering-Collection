"""
Pacman Game Implementation using Pygame.
Adheres to SAST DeepSource requirements:
- No secrets or hardcoded credentials.
- Prevents IndexError/KeyError via boundary checks.
- SOLID principles (Pacman, Ghost, Maze, Pellet, GameManager).
- No eval() or pickle.
- BFS pathfinding with collections.deque.
- PEP 8 compliant, < 79 chars per line.
- Comprehensive docstrings.
"""

import sys
from enum import Enum, auto
from collections import deque
from typing import List, Tuple, Optional, Dict

import pygame

# Constants
CELL_SIZE = 40
FPS = 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Direction(Enum):
    """Enumeration for movement directions."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


class GhostState(Enum):
    """Enumeration for Ghost behavioral states."""
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()


class PelletType(Enum):
    """Enumeration for Pellet types."""
    NORMAL = auto()
    POWER = auto()


class Pellet:
    """Represents a collectible pellet in the maze."""
    def __init__(self, x: int, y: int, p_type: PelletType):
        """Initialize pellet with grid coordinates and type."""
        self.x = x
        self.y = y
        self.type = p_type


class Maze:
    """Handles the grid structure, walls, and coordinate validation."""
    def __init__(self, layout: List[str]):
        """Initialize maze with a string layout."""
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout[0]) if self.height > 0 else 0

    def is_valid_pos(self, x: int, y: int) -> bool:
        """Check if grid coordinates are within bounds and not a wall."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.layout[y][x] != '#'


class Pacman:
    """Player-controlled character."""
    def __init__(self, start_x: int, start_y: int):
        """Initialize Pacman at the starting grid coordinates."""
        self.x = start_x
        self.y = start_y
        self.direction = Direction.NONE
        self.next_dir = Direction.NONE

    def update(self, maze: Maze):
        """Update Pacman's position based on direction."""
        nx, ny = self._get_next_pos(self.x, self.y, self.next_dir)
        if maze.is_valid_pos(nx, ny):
            self.direction = self.next_dir
            self.x, self.y = nx, ny
        else:
            nx, ny = self._get_next_pos(self.x, self.y, self.direction)
            if maze.is_valid_pos(nx, ny):
                self.x, self.y = nx, ny

    def _get_next_pos(
        self, x: int, y: int, d: Direction
    ) -> Tuple[int, int]:
        """Calculate next coordinates for a given direction."""
        if d == Direction.UP:
            return x, y - 1
        if d == Direction.DOWN:
            return x, y + 1
        if d == Direction.LEFT:
            return x - 1, y
        if d == Direction.RIGHT:
            return x + 1, y
        return x, y


class Ghost:
    """AI-controlled enemy using BFS pathfinding."""
    def __init__(self, start_x: int, start_y: int):
        """Initialize Ghost at the starting grid coordinates."""
        self.x = start_x
        self.y = start_y
        self.state = GhostState.CHASE
        self.frightened_timer = 0

    def update(self, maze: Maze, target_x: int, target_y: int):
        """Update Ghost position and state."""
        # Handle state transitions based on frightened timer
        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer == 0:
                self.state = GhostState.CHASE

        # If frightened, target a scatter corner instead of Pacman
        if self.state == GhostState.FRIGHTENED:
            target_x, target_y = 1, maze.height - 2

        next_step = self._find_path_bfs(maze, target_x, target_y)
        if next_step:
            self.x, self.y = next_step

    def _find_path_bfs(
        self, maze: Maze, tx: int, ty: int
    ) -> Optional[Tuple[int, int]]:
        """
        BFS pathfinding to find the shortest path to target.
        Uses collections.deque for efficient O(1) pops from the left.
        """
        start = (self.x, self.y)
        if start == (tx, ty):
            return None

        queue = deque([[start]])
        visited = set([start])

        while queue:
            path = queue.popleft()
            cx, cy = path[-1]

            if cx == tx and cy == ty:
                if len(path) > 1:
                    return path[1]
                return None

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if maze.is_valid_pos(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = list(path)
                    new_path.append((nx, ny))
                    queue.append(new_path)
        return None


class GameManager:
    """Coordinates game entities, game loop, and rendering."""
    def __init__(self):
        """Initialize game window, maze, entities, and state."""
        pygame.init()
        # Initial maze layout configuration
        layout = [
            "##########",
            "#P.......#",
            "#.##.##..#",
            "#.#...#..#",
            "#...O....#",
            "#.##.##..#",
            "#......G.#",
            "##########"
        ]
        self.maze = Maze(layout)
        self.screen = pygame.display.set_mode(
            (self.maze.width * CELL_SIZE, self.maze.height * CELL_SIZE)
        )
        pygame.display.set_caption("Secure Pacman")
        self.clock = pygame.time.Clock()
        self.score = 0
        self.running = True

        self.pacman = None
        self.ghosts: List[Ghost] = []
        self.pellets: Dict[Tuple[int, int], Pellet] = {}

        self._load_entities(layout)

    def _load_entities(self, layout: List[str]):
        """Parse layout to initialize entities and avoid IndexError."""
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                if char == 'P':
                    self.pacman = Pacman(x, y)
                elif char == 'G':
                    self.ghosts.append(Ghost(x, y))
                elif char == '.':
                    self.pellets[(x, y)] = Pellet(x, y, PelletType.NORMAL)
                elif char == 'O':
                    self.pellets[(x, y)] = Pellet(x, y, PelletType.POWER)

    def run(self):
        """Main game loop for event handling, updating, and drawing."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Process Pygame events securely without eval/pickle."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pacman.next_dir = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_dir = Direction.DOWN
                elif event.key == pygame.K_LEFT:
                    self.pacman.next_dir = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_dir = Direction.RIGHT

    def _update(self):
        """Update game logic for all entities."""
        if not self.pacman:
            return

        self.pacman.update(self.maze)

        # Check pellet collision using O(1) dictionary lookup
        p_pos = (self.pacman.x, self.pacman.y)
        if p_pos in self.pellets:
            pellet = self.pellets.pop(p_pos)
            if pellet.type == PelletType.NORMAL:
                self.score += 10
            elif pellet.type == PelletType.POWER:
                self.score += 50
                for ghost in self.ghosts:
                    ghost.state = GhostState.FRIGHTENED
                    ghost.frightened_timer = 50

        # Check win condition: game ends if no pellets remain
        if not self.pellets:
            print(f"You Win! Final Score: {self.score}")
            self.running = False

        # Update ghosts and check collisions
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman.x, self.pacman.y)
            if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                if ghost.state == GhostState.FRIGHTENED:
                    ghost.x, ghost.y = 8, 6  # Simple respawn logic
                    ghost.state = GhostState.CHASE
                    ghost.frightened_timer = 0
                    self.score += 200
                else:
                    print(f"Game Over! Final Score: {self.score}")
                    self.running = False

    def _draw(self):
        """Render all game objects to the screen."""
        self.screen.fill(BLACK)
        
        # Draw maze walls
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.layout[y][x] == '#':
                    rect = pygame.Rect(
                        x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, BLUE, rect)

        # Draw remaining pellets
        for (px, py), pellet in self.pellets.items():
            color = WHITE if pellet.type == PelletType.NORMAL else YELLOW
            radius = 3 if pellet.type == PelletType.NORMAL else 8
            cx = px * CELL_SIZE + CELL_SIZE // 2
            cy = py * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, color, (cx, cy), radius)

        # Draw ghost entities
        for ghost in self.ghosts:
            color = WHITE if ghost.state == GhostState.FRIGHTENED else RED
            gx = ghost.x * CELL_SIZE + CELL_SIZE // 2
            gy = ghost.y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, color, (gx, gy), CELL_SIZE // 2)

        # Draw Pacman
        if self.pacman:
            px = self.pacman.x * CELL_SIZE + CELL_SIZE // 2
            py = self.pacman.y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, YELLOW, (px, py), CELL_SIZE // 2)

        pygame.display.flip()


if __name__ == "__main__":
    game = GameManager()
    game.run()
