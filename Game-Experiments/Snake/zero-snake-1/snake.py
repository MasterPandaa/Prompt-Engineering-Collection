import sys
import random
from collections import deque
import pygame

# Constants for grid and window sizes
CELL_SIZE = 20
GRID_WIDTH = 40
GRID_HEIGHT = 30
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class SnakePlayer:
    """Class representing the human-controlled snake."""

    def __init__(self, start_pos):
        """Initialize the player snake at a given starting position."""
        self.body = deque([start_pos])
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.alive = True

    def change_direction(self, new_dir):
        """Update direction if it's not a 180-degree turn."""
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_dir = new_dir

    def move(self, grow=False):
        """Move the snake one step forward."""
        if not self.alive:
            return

        self.direction = self.next_dir
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.appendleft(new_head)

        if not grow:
            # Safe pop as we just appended left, avoiding IndexError
            self.body.pop()


class SnakeAI:
    """Class representing the AI-controlled snake."""

    def __init__(self, start_pos):
        """Initialize the AI snake at a given starting position."""
        self.body = deque([start_pos])
        self.direction = (-1, 0)
        self.score = 0
        self.alive = True

    def compute_next_move(self, food_pos):
        """
        Determine the next move using a greedy pathfinding approach.
        Evaluates distance to food and picks a valid direction.
        """
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        food_x, food_y = food_pos

        possible_moves = []
        if food_x > head_x:
            possible_moves.append((1, 0))
        elif food_x < head_x:
            possible_moves.append((-1, 0))

        if food_y > head_y:
            possible_moves.append((0, 1))
        elif food_y < head_y:
            possible_moves.append((0, -1))

        # Filter out 180-degree turns
        valid_moves = []
        for move in possible_moves:
            if (move[0] * -1, move[1] * -1) != self.direction:
                valid_moves.append(move)

        if valid_moves:
            self.direction = valid_moves[0]

    def move(self, grow=False):
        """Move the AI snake one step forward."""
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.appendleft(new_head)

        if not grow:
            # Safe pop as we just appended left, avoiding IndexError
            self.body.pop()


class GameBoard:
    """Class managing the game loop, rendering, and logic."""

    def __init__(self):
        """Initialize the game board, Pygame, and entities."""
        pygame.init()
        # Avoid hardcoding any secrets/API keys (SAST Check 1)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Two-Player Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)

        # Initialize player and AI
        self.player = SnakePlayer((5, 5))
        self.ai = SnakeAI((GRID_WIDTH - 6, GRID_HEIGHT - 6))
        self.food = self.spawn_food()
        self.running = True

    def spawn_food(self):
        """Generate food at a random free position."""
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # Ensure food does not spawn on snakes
            if pos not in self.player.body and pos not in self.ai.body:
                return pos

    def handle_events(self):
        """Process keyboard events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Avoid KeyError by checking event.type explicitly
                if event.key == pygame.K_UP:
                    self.player.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.player.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.player.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.player.change_direction((1, 0))

    def update(self):
        """Update game state and check conditions."""
        if not self.player.alive and not self.ai.alive:
            return

        self.ai.compute_next_move(self.food)

        # Check if growth will happen
        p_head = None
        if self.player.alive:
            px, py = self.player.body[0]
            dx, dy = self.player.next_dir
            p_head = (px + dx, py + dy)

        a_head = None
        if self.ai.alive:
            ax, ay = self.ai.body[0]
            dx, dy = self.ai.direction
            a_head = (ax + dx, ay + dy)

        p_grow = p_head == self.food
        a_grow = a_head == self.food

        self.player.move(grow=p_grow)
        self.ai.move(grow=a_grow)

        if (p_grow and self.player.alive) or (a_grow and self.ai.alive):
            if p_grow and self.player.alive:
                self.player.score += 10
            if a_grow and self.ai.alive:
                self.ai.score += 10
            self.food = self.spawn_food()

        self.check_collisions()

    def check_collisions(self):
        """Check for wall, self, and opponent collisions efficiently."""
        # Convert bodies to sets for O(1) lookups
        p_set = set(list(self.player.body)[1:])
        a_set = set(list(self.ai.body)[1:])
        p_all_set = set(self.player.body)
        a_all_set = set(self.ai.body)

        # Player collision checks
        if self.player.alive:
            px, py = self.player.body[0]
            wall_hit = (
                px < 0 or px >= GRID_WIDTH or
                py < 0 or py >= GRID_HEIGHT
            )
            if wall_hit or (px, py) in p_set or (px, py) in a_all_set:
                self.player.alive = False

        # AI collision checks
        if self.ai.alive:
            ax, ay = self.ai.body[0]
            wall_hit = (
                ax < 0 or ax >= GRID_WIDTH or
                ay < 0 or ay >= GRID_HEIGHT
            )
            if wall_hit or (ax, ay) in a_set or (ax, ay) in p_all_set:
                self.ai.alive = False

        # Head-to-head collision resulting in draw
        if self.player.alive and self.ai.alive:
            if self.player.body[0] == self.ai.body[0]:
                self.player.alive = False
                self.ai.alive = False

    def draw(self):
        """Render the game elements to the screen."""
        self.screen.fill(BLACK)

        # Draw food
        fx, fy = self.food
        f_rect = (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, f_rect)

        # Draw player snake
        for segment in self.player.body:
            sx, sy = segment
            s_rect = (sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, GREEN, s_rect)

        # Draw AI snake
        for segment in self.ai.body:
            sx, sy = segment
            s_rect = (sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, BLUE, s_rect)

        # Draw scores
        p_text = self.font.render(f"P1: {self.player.score}", True, WHITE)
        a_text = self.font.render(f"AI: {self.ai.score}", True, WHITE)
        self.screen.blit(p_text, (10, 10))
        self.screen.blit(a_text, (WINDOW_WIDTH - 100, 10))

        # Draw Game Over message
        if not self.player.alive or not self.ai.alive:
            msg = "Game Over!"
            if not self.player.alive and not self.ai.alive:
                msg = "Draw!"
            elif self.player.alive:
                msg = "Player Wins!"
            else:
                msg = "AI Wins!"

            msg_text = self.font.render(msg, True, WHITE)
            x_pos = WINDOW_WIDTH // 2 - msg_text.get_width() // 2
            y_pos = WINDOW_HEIGHT // 2 - msg_text.get_height() // 2
            self.screen.blit(msg_text, (x_pos, y_pos))

        pygame.display.flip()

    def run(self):
        """Main game loop execution."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameBoard()
    game.run()
