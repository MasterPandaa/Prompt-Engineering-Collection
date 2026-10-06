"""
Two-player Snake Game (Player vs AI) using Pygame.

Features include scoring, collision detection, and growth.
This code strictly follows PEP 8 standards, utilizes collections.deque
for performance, and implements separation of concerns.
"""

import sys
import random
from collections import deque
import pygame

# Constants for grid and screen dimensions
CELL_SIZE = 20
GRID_WIDTH = 40
GRID_HEIGHT = 30
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

# Color definitions (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakePlayer:
    """
    Class representing the human-controlled snake.

    Attributes:
        body (deque): The coordinates of the snake's body parts.
        body_set (set): A set of body coordinates for O(1) collision check.
        direction (tuple): Current movement direction vector.
        color (tuple): RGB color of the snake.
        score (int): Current score of the player.
    """

    def __init__(self, start_pos, color):
        """Initialize the player snake at the given starting position."""
        self.body = deque([start_pos])
        self.body_set = {start_pos}
        self.direction = RIGHT
        self.color = color
        self.score = 0

    def change_direction(self, new_dir):
        """
        Change the snake's direction safely.

        Args:
            new_dir (tuple): The new direction vector.
        """
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def move(self, grow=False):
        """
        Move the snake in the current direction.

        Args:
            grow (bool): Whether the snake should grow on this turn.
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.appendleft(new_head)
        self.body_set.add(new_head)

        if not grow:
            if self.body:
                tail = self.body.pop()
                if tail in self.body_set and tail != new_head:
                    # In case tail equals new_head, don't remove
                    # But since we just added new_head, wait
                    pass
                # Recalculate set to avoid bugs when tail and head overlap
                self.body_set.remove(tail)

    def check_collision(self, bounds_x, bounds_y, other_body_set):
        """
        Check if the snake has collided with walls, itself, or another snake.

        Args:
            bounds_x (int): Maximum x coordinate.
            bounds_y (int): Maximum y coordinate.
            other_body_set (set): The body coordinates of the other snake.

        Returns:
            bool: True if a collision occurred, False otherwise.
        """
        if not self.body:
            return True

        head = self.body[0]

        # Wall collision
        if head[0] < 0 or head[0] >= bounds_x:
            return True
        if head[1] < 0 or head[1] >= bounds_y:
            return True

        # Self collision (excluding the head itself from the check)
        # We check if the count in the deque is more than 1 for the head
        if self.body.count(head) > 1:
            return True

        # Other snake collision
        if head in other_body_set:
            return True

        return False


class SnakeAI:
    """
    Class representing the AI-controlled snake.

    Attributes:
        body (deque): The coordinates of the snake's body parts.
        body_set (set): A set of body coordinates for O(1) collision check.
        direction (tuple): Current movement direction vector.
        color (tuple): RGB color of the snake.
        score (int): Current score of the AI.
    """

    def __init__(self, start_pos, color):
        """Initialize the AI snake at the given starting position."""
        self.body = deque([start_pos])
        self.body_set = {start_pos}
        self.direction = LEFT
        self.color = color
        self.score = 0

    def compute_next_move(self, food_pos, other_body_set):
        """
        Compute the next movement direction using a greedy approach.

        The AI calculates the Manhattan distance to the food for all
        valid adjacent cells and chooses the one that minimizes the distance,
        while avoiding walls, itself, and the other snake.

        Args:
            food_pos (tuple): The coordinate of the food.
            other_body_set (set): The body coordinates of the other snake.
        """
        if not self.body:
            return

        head_x, head_y = self.body[0]
        possible_moves = [UP, DOWN, LEFT, RIGHT]
        best_move = self.direction
        min_dist = float('inf')

        for move in possible_moves:
            # Prevent 180-degree turns
            if (move[0] * -1, move[1] * -1) == self.direction:
                continue

            next_x = head_x + move[0]
            next_y = head_y + move[1]
            next_pos = (next_x, next_y)

            # Check wall collision
            if next_x < 0 or next_x >= GRID_WIDTH:
                continue
            if next_y < 0 or next_y >= GRID_HEIGHT:
                continue

            # Check self collision
            if next_pos in self.body_set:
                continue

            # Check other snake collision
            if next_pos in other_body_set:
                continue

            # Greedy approach: minimize Manhattan distance to food
            dist = abs(next_x - food_pos[0]) + abs(next_y - food_pos[1])
            if dist < min_dist:
                min_dist = dist
                best_move = move

        self.direction = best_move

    def move(self, grow=False):
        """
        Move the AI snake in the computed direction.

        Args:
            grow (bool): Whether the snake should grow on this turn.
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.appendleft(new_head)
        self.body_set.add(new_head)

        if not grow:
            if self.body:
                tail = self.body.pop()
                if tail in self.body_set:
                    self.body_set.remove(tail)

    def check_collision(self, bounds_x, bounds_y, other_body_set):
        """
        Check if the AI snake has collided with walls, itself, or others.

        Args:
            bounds_x (int): Maximum x coordinate.
            bounds_y (int): Maximum y coordinate.
            other_body_set (set): The body coordinates of the other snake.

        Returns:
            bool: True if a collision occurred, False otherwise.
        """
        if not self.body:
            return True

        head = self.body[0]

        if head[0] < 0 or head[0] >= bounds_x:
            return True
        if head[1] < 0 or head[1] >= bounds_y:
            return True

        if self.body.count(head) > 1:
            return True

        if head in other_body_set:
            return True

        return False


class GameBoard:
    """
    Class managing game state, main loop, and rendering.

    Attributes:
        screen: Pygame display surface.
        clock: Pygame time clock.
        player (SnakePlayer): The human player.
        ai (SnakeAI): The AI opponent.
        food_pos (tuple): The coordinate of the current food.
        running (bool): Game loop state.
    """

    def __init__(self):
        """Initialize the game board, Pygame, and game entities."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Two-Player Snake: Player vs AI")
        self.clock = pygame.time.Clock()

        # Initialize player and AI at opposite sides
        self.player = SnakePlayer((5, GRID_HEIGHT // 2), GREEN)
        self.ai = SnakeAI((GRID_WIDTH - 6, GRID_HEIGHT // 2), BLUE)

        self.food_pos = self._generate_food()
        self.running = True

    def _generate_food(self):
        """
        Generate a new food position not occupied by any snake.

        Returns:
            tuple: A valid (x, y) coordinate for the food.
        """
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if pos not in self.player.body_set and pos not in self.ai.body_set:
                return pos

    def handle_events(self):
        """Process Pygame events including keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Use dictionary for O(1) lookup to prevent KeyError chains
                key_map = {
                    pygame.K_UP: UP,
                    pygame.K_DOWN: DOWN,
                    pygame.K_LEFT: LEFT,
                    pygame.K_RIGHT: RIGHT,
                    pygame.K_w: UP,
                    pygame.K_s: DOWN,
                    pygame.K_a: LEFT,
                    pygame.K_d: RIGHT
                }
                new_dir = key_map.get(event.key)
                if new_dir:
                    self.player.change_direction(new_dir)

    def update(self):
        """Update game state: movement, collisions, and scoring."""
        # Check food consumption
        player_grow = False
        ai_grow = False

        # Compute AI move
        self.ai.compute_next_move(self.food_pos, self.player.body_set)

        # Predict next heads for food check
        p_hx, p_hy = self.player.body[0]
        p_dx, p_dy = self.player.direction
        p_next = (p_hx + p_dx, p_hy + p_dy)

        a_hx, a_hy = self.ai.body[0]
        a_dx, a_dy = self.ai.direction
        a_next = (a_hx + a_dx, a_hy + a_dy)

        if p_next == self.food_pos:
            player_grow = True
            self.player.score += 10
            self.food_pos = self._generate_food()
        elif a_next == self.food_pos:
            ai_grow = True
            self.ai.score += 10
            self.food_pos = self._generate_food()

        # Move snakes
        self.player.move(grow=player_grow)
        self.ai.move(grow=ai_grow)

        # Check collisions
        p_col = self.player.check_collision(
            GRID_WIDTH, GRID_HEIGHT, self.ai.body_set
        )
        a_col = self.ai.check_collision(
            GRID_WIDTH, GRID_HEIGHT, self.player.body_set
        )

        if p_col and a_col:
            print("Draw! Both snakes collided.")
            self.running = False
        elif p_col:
            print("AI Wins! Player collided.")
            self.running = False
        elif a_col:
            print("Player Wins! AI collided.")
            self.running = False

    def draw(self):
        """Render the game entities and UI to the screen."""
        self.screen.fill(BLACK)

        # Draw food
        food_rect = pygame.Rect(
            self.food_pos[0] * CELL_SIZE,
            self.food_pos[1] * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(self.screen, RED, food_rect)

        # Draw player snake
        for segment in self.player.body:
            rect = pygame.Rect(
                segment[0] * CELL_SIZE,
                segment[1] * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.player.color, rect)

        # Draw AI snake
        for segment in self.ai.body:
            rect = pygame.Rect(
                segment[0] * CELL_SIZE,
                segment[1] * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.ai.color, rect)

        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(
            f"Player: {self.player.score}  AI: {self.ai.score}",
            True, WHITE
        )
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def run(self):
        """Start and manage the main game loop."""
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
