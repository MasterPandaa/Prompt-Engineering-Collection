"""
Two-Player Snake Game with AI.

This module implements a two-player snake game using Pygame,
where one player is controlled via keyboard and the other by AI.
"""

import sys
import random
from collections import deque
import pygame

# Constants for the game
CELL_SIZE = 20
GRID_WIDTH = 40
GRID_HEIGHT = 30
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

# Colors
COLOR_BG = (30, 30, 30)
COLOR_GRID = (50, 50, 50)
COLOR_PLAYER = (0, 255, 0)
COLOR_AI = (255, 0, 0)
COLOR_FOOD = (255, 255, 0)
COLOR_TEXT = (255, 255, 255)

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


class SnakePlayer:
    """Class representing the human-controlled snake."""

    def __init__(self, start_pos, direction, color):
        """Initialize the snake player."""
        self.body = deque([start_pos])
        self.direction = direction
        self.next_dir = direction
        self.color = color
        self.grow = False
        self.alive = True
        self.score = 0

    def set_direction(self, new_dir):
        """
        Validate and set the next direction.

        Ensures the snake cannot perform an invalid 180-degree turn.
        """
        if (self.direction[0] * -1, self.direction[1] * -1) != new_dir:
            self.next_dir = new_dir

    def update(self):
        """Update the snake's position."""
        if not self.alive:
            return

        self.direction = self.next_dir
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.appendleft(new_head)
        if self.grow:
            self.grow = False
            self.score += 10
        else:
            if self.body:
                self.body.pop()

    def draw(self, surface):
        """Draw the snake on the given surface."""
        for segment in self.body:
            rect = pygame.Rect(
                segment[0] * CELL_SIZE,
                segment[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(surface, self.color, rect)


class SnakeAI:
    """Class representing the AI-controlled snake."""

    def __init__(self, start_pos, direction, color):
        """Initialize the snake AI."""
        self.body = deque([start_pos])
        self.direction = direction
        self.color = color
        self.grow = False
        self.alive = True
        self.score = 0

    def compute_next_move(self, food_pos, obstacles):
        """
        Compute the next move using a greedy algorithm.

        The AI tries to move towards the food while avoiding
        obstacles (itself, the other snake, and walls).
        """
        head_x, head_y = self.body[0]
        food_x, food_y = food_pos

        possible_moves = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
        valid_moves = []

        # Filter out invalid moves (walls and obstacles)
        for move in possible_moves:
            next_x = head_x + move[0]
            next_y = head_y + move[1]
            next_pos = (next_x, next_y)

            # Check bounds
            if not (0 <= next_x < GRID_WIDTH and 0 <= next_y < GRID_HEIGHT):
                continue

            # Check obstacles (O(1) lookup if obstacles is a set)
            if next_pos in obstacles:
                continue

            # Prevent 180-degree turns
            reverse_dir = (self.direction[0] * -1, self.direction[1] * -1)
            if move == reverse_dir:
                continue

            valid_moves.append(move)

        if not valid_moves:
            # No valid moves, keep current direction to die gracefully
            return

        # Greedy approach: pick the move that minimizes distance to food
        best_move = valid_moves[0]
        min_dist = float('inf')

        for move in valid_moves:
            next_x = head_x + move[0]
            next_y = head_y + move[1]
            dist = abs(next_x - food_x) + abs(next_y - food_y)
            if dist < min_dist:
                min_dist = dist
                best_move = move

        self.direction = best_move

    def update(self):
        """Update the AI snake's position."""
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.appendleft(new_head)
        if self.grow:
            self.grow = False
            self.score += 10
        else:
            if self.body:
                self.body.pop()

    def draw(self, surface):
        """Draw the AI snake on the given surface."""
        for segment in self.body:
            rect = pygame.Rect(
                segment[0] * CELL_SIZE,
                segment[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(surface, self.color, rect)


class GameBoard:
    """Class managing the game loop, rendering, and logic."""

    def __init__(self):
        """Initialize the game board."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Two-Player Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        self.player = SnakePlayer(
            start_pos=(GRID_WIDTH // 4, GRID_HEIGHT // 2),
            direction=DIR_RIGHT,
            color=COLOR_PLAYER
        )
        self.ai = SnakeAI(
            start_pos=(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2),
            direction=DIR_LEFT,
            color=COLOR_AI
        )

        self.food_pos = self._spawn_food()
        self.game_over = False
        self.winner_text = ""

    def _spawn_food(self):
        """Spawn food in a random empty location."""
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # Ensure food doesn't spawn on snakes
            if pos not in self.player.body and pos not in self.ai.body:
                return pos

    def _handle_events(self):
        """Handle keyboard and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.set_direction(DIR_UP)
                elif event.key == pygame.K_DOWN:
                    self.player.set_direction(DIR_DOWN)
                elif event.key == pygame.K_LEFT:
                    self.player.set_direction(DIR_LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.player.set_direction(DIR_RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    self._quit()

    def _check_collisions(self):
        """Check for collisions with walls, food, and other snakes."""
        # 1. Check food collisions
        if self.player.alive and self.player.body[0] == self.food_pos:
            self.player.grow = True
            self.food_pos = self._spawn_food()

        if self.ai.alive and self.ai.body[0] == self.food_pos:
            self.ai.grow = True
            self.food_pos = self._spawn_food()

        # Build obstacle set for efficient O(1) collision checking
        player_body_set = set(self.player.body)
        ai_body_set = set(self.ai.body)

        player_head = self.player.body[0] if self.player.alive else None
        ai_head = self.ai.body[0] if self.ai.alive else None

        # Check player death
        if self.player.alive and player_head:
            px, py = player_head
            out_of_bounds = not (0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT)
            hit_self = list(self.player.body).count(player_head) > 1
            hit_ai = player_head in ai_body_set

            if out_of_bounds or hit_self or hit_ai:
                self.player.alive = False

        # Check AI death
        if self.ai.alive and ai_head:
            ax, ay = ai_head
            out_of_bounds = not (0 <= ax < GRID_WIDTH and 0 <= ay < GRID_HEIGHT)
            hit_self = list(self.ai.body).count(ai_head) > 1
            hit_player = ai_head in player_body_set

            if out_of_bounds or hit_self or hit_player:
                self.ai.alive = False

        # Determine game over state
        if not self.player.alive and not self.ai.alive:
            self.game_over = True
            self.winner_text = "Draw! Both snakes died."
        elif not self.player.alive:
            self.game_over = True
            self.winner_text = "AI Wins!"
        elif not self.ai.alive:
            self.game_over = True
            self.winner_text = "Player Wins!"

    def _draw(self):
        """Render all game objects to the screen."""
        self.screen.fill(COLOR_BG)

        # Draw food
        food_rect = pygame.Rect(
            self.food_pos[0] * CELL_SIZE,
            self.food_pos[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_FOOD, food_rect)

        # Draw snakes
        self.player.draw(self.screen)
        self.ai.draw(self.screen)

        # Draw scores
        score_text = self.font.render(
            f"Player: {self.player.score}  AI: {self.ai.score}",
            True, COLOR_TEXT
        )
        self.screen.blit(score_text, (10, 10))

        # Draw game over text
        if self.game_over:
            go_text = self.font.render(self.winner_text, True, COLOR_TEXT)
            go_rect = go_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            self.screen.blit(go_text, go_rect)

        pygame.display.flip()

    def _quit(self):
        """Exit the game gracefully."""
        pygame.quit()
        sys.exit()

    def run(self):
        """Main game loop."""
        while True:
            self._handle_events()

            if not self.game_over:
                # Prepare obstacles for AI (O(1) lookup structure)
                obstacles = set(self.player.body) | set(self.ai.body)
                
                # Update logic
                self.ai.compute_next_move(self.food_pos, obstacles)
                self.player.update()
                self.ai.update()
                self._check_collisions()

            self._draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = GameBoard()
    game.run()
