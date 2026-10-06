import pygame
import random
import sys
from typing import List, Tuple, Dict, Optional

# -----------------------------
# Konfigurasi Game
# -----------------------------
COLS = 10
ROWS = 20
BLOCK_SIZE = 30  # pixel per blok

PLAY_WIDTH = COLS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE

SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

FPS = 60

# Kecepatan jatuh (dalam detik per langkah)
GRAVITY_NORMAL = 0.8
GRAVITY_SOFT_DROP = 0.02

# Skor per jumlah baris yang dibersihkan sekaligus
LINE_CLEAR_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (80, 80, 80)

# Warna untuk masing-masing Tetromino
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0)
}

# Definisi Rotasi Tetromino (matriks 4x4)
# Setiap bentuk adalah daftar dari orientasi rotasi
TETROMINO_SHAPES: Dict[str, List[List[List[int]]]] = {
    'I': [
        [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 0]
        ],
    ],
    'O': [
        [
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
    ],
    'T': [
        [
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
    ],
    'S': [
        [
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0]
        ]
    ],
    'Z': [
        [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ]
    ],
    'J': [
        [
            [1, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0]
        ],
    ],
    'L': [
        [
            [0, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        [
            [0, 0, 0, 0],
            [1, 1, 1, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        [
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
    ],
}


class Piece:
    def __init__(self, shape_key: str):
        self.shape_key = shape_key
        self.color = COLORS[shape_key]
        self.rotations = TETROMINO_SHAPES[shape_key]
        self.rotation_index = 0
        # Spawn di atas tengah papan
        # Gunakan bounding box 4x4, posisi mengacu ke grid papan
        self.x = COLS // 2 - 2
        self.y = -2  # mulai sedikit di atas agar muat untuk I dan lain-lain

    @property
    def shape(self) -> List[List[int]]:
        return self.rotations[self.rotation_index]

    def rotate(self):
        self.rotation_index = (self.rotation_index + 1) % len(self.rotations)

    def get_blocks(self) -> List[Tuple[int, int]]:
        blocks = []
        for r in range(4):
            for c in range(4):
                if self.shape[r][c] == 1:
                    blocks.append((self.x + c, self.y + r))
        return blocks


class Board:
    def __init__(self):
        # grid berisi None atau tuple warna
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(COLS)] for _ in range(ROWS)
        ]
        self.score = 0

    def valid_position(self, piece: Piece) -> bool:
        for (x, y) in piece.get_blocks():
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, piece: Piece):
        for (x, y) in piece.get_blocks():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = piece.color
        cleared = self.clear_lines()
        if cleared > 0:
            self.score += LINE_CLEAR_SCORES.get(cleared, cleared * 100)

    def clear_lines(self) -> int:
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(new_grid)
        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(COLS)])
        self.grid = new_grid
        return cleared

    def is_game_over(self) -> bool:
        # Game over jika ada blok pada baris negatif saat spawn yang tidak valid
        # atau baris 0 sudah terisi yang membuat spawn fail
        return any(self.grid[0][c] is not None for c in range(COLS))


class TetrisGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tetris (Python + Pygame)")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 32, bold=True)

        self.board = Board()
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()

        self.drop_timer = 0.0
        self.gravity = GRAVITY_NORMAL
        self.running = True
        self.game_over = False

    def get_new_piece(self) -> Piece:
        return Piece(random.choice(list(TETROMINO_SHAPES.keys())))

    def move_piece(self, dx: int, dy: int) -> bool:
        if self.current_piece is None:
            return False
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not self.board.valid_position(self.current_piece):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        return True

    def rotate_piece(self):
        if self.current_piece is None:
            return
        old_index = self.current_piece.rotation_index
        self.current_piece.rotate()
        # Simple wall kick: coba geser +-1 jika tabrakan
        if not self.board.valid_position(self.current_piece):
            self.current_piece.x += 1
            if not self.board.valid_position(self.current_piece):
                self.current_piece.x -= 2
                if not self.board.valid_position(self.current_piece):
                    # kembalikan
                    self.current_piece.x += 1
                    self.current_piece.rotation_index = old_index

    def hard_drop(self):
        if self.current_piece is None:
            return
        while self.move_piece(0, 1):
            pass
        # tidak bisa turun lagi, kunci
        self.lock_and_spawn()

    def lock_and_spawn(self):
        if self.current_piece is None:
            return
        self.board.lock_piece(self.current_piece)
        # spawn next
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        # jika posisi spawn langsung invalid => game over
        if not self.board.valid_position(self.current_piece):
            self.game_over = True

    def update(self, dt: float):
        if self.game_over:
            return
        self.drop_timer += dt
        # jatuh otomatis
        if self.drop_timer >= self.gravity:
            self.drop_timer = 0.0
            if not self.move_piece(0, 1):
                # kunci jika tidak bisa turun
                self.lock_and_spawn()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over:
                    # tekan Enter untuk restart
                    if event.key == pygame.K_RETURN:
                        self.restart()
                    continue
                if event.key == pygame.K_LEFT:
                    self.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    # soft drop satu langkah
                    self.move_piece(0, 1)
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()

        # Tahan key untuk soft drop cepat
        keys = pygame.key.get_pressed()
        if not self.game_over:
            if keys[pygame.K_DOWN]:
                self.gravity = GRAVITY_SOFT_DROP
            else:
                self.gravity = GRAVITY_NORMAL

    def draw_grid(self):
        # background area playfield
        pygame.draw.rect(self.screen, BLACK, (0, 0, PLAY_WIDTH, PLAY_HEIGHT))
        # grid lines
        for x in range(COLS + 1):
            pygame.draw.line(
                self.screen, LIGHT_GRAY,
                (x * BLOCK_SIZE, 0),
                (x * BLOCK_SIZE, PLAY_HEIGHT), 1
            )
        for y in range(ROWS + 1):
            pygame.draw.line(
                self.screen, LIGHT_GRAY,
                (0, y * BLOCK_SIZE),
                (PLAY_WIDTH, y * BLOCK_SIZE), 1
            )

    def draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = self.board.grid[r][c]
                if color is not None:
                    self.draw_block(c, r, color)

    def draw_piece(self, piece: Piece):
        for (x, y) in piece.get_blocks():
            if y >= 0:
                self.draw_block(x, y, piece.color)

    def draw_block(self, x: int, y: int, color: Tuple[int, int, int]):
        px = x * BLOCK_SIZE
        py = y * BLOCK_SIZE
        rect = pygame.Rect(px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def draw_side_panel(self):
        panel_x = PLAY_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 20), panel_rect)

        # Judul
        title_surf = self.big_font.render("TETRIS", True, WHITE)
        self.screen.blit(title_surf, (panel_x + 20, 20))

        # Skor
        score_surf = self.font.render(f"Score: {self.board.score}", True, WHITE)
        self.screen.blit(score_surf, (panel_x + 20, 80))

        # Next piece preview
        next_surf = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_surf, (panel_x + 20, 120))

        # gambar preview di area kecil
        preview_offset_x = panel_x + 20
        preview_offset_y = 150
        # background preview
        pygame.draw.rect(self.screen, (30, 30, 30), (preview_offset_x, preview_offset_y, 4*BLOCK_SIZE, 4*BLOCK_SIZE))

        # render next piece di tengah area 4x4
        for r in range(4):
            for c in range(4):
                if self.next_piece.shape[r][c] == 1:
                    px = preview_offset_x + c * BLOCK_SIZE + 1
                    py = preview_offset_y + r * BLOCK_SIZE + 1
                    rect = pygame.Rect(px, py, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                    pygame.draw.rect(self.screen, self.next_piece.color, rect, border_radius=3)

        # Help
        help_lines = [
            "Controls:",
            "Left/Right = Move",
            "Down = Soft drop",
            "Up = Rotate",
            "Space = Hard drop",
            "Enter = Restart",
            "Esc = Quit",
        ]
        for i, line in enumerate(help_lines):
            surf = self.font.render(line, True, WHITE)
            self.screen.blit(surf, (panel_x + 20, 320 + i * 22))

    def draw_game_over(self):
        overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        msg1 = self.big_font.render("GAME OVER", True, WHITE)
        msg2 = self.font.render("Press Enter to Restart", True, WHITE)
        self.screen.blit(msg1, (PLAY_WIDTH // 2 - msg1.get_width() // 2, PLAY_HEIGHT // 2 - 40))
        self.screen.blit(msg2, (PLAY_WIDTH // 2 - msg2.get_width() // 2, PLAY_HEIGHT // 2))

    def restart(self):
        self.board = Board()
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.drop_timer = 0.0
        self.gravity = GRAVITY_NORMAL
        self.game_over = False

    def draw(self):
        self.screen.fill(GRAY)
        self.draw_grid()
        self.draw_board()
        if self.current_piece is not None:
            self.draw_piece(self.current_piece)
        self.draw_side_panel()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


def main():
    game = TetrisGame()
    game.run()


if __name__ == "__main__":
    main()
