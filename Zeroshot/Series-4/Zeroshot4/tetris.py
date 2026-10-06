import pygame
import sys
import random
from typing import List, Tuple, Optional

# --- Konfigurasi Permainan ---
COLS, ROWS = 10, 20
BLOCK_SIZE = 30  # piksel per blok
BORDER = 10      # margin di sekitar playfield
FPS = 60

# Warna
BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
GRAY = (50, 50, 50)
LIGHT_GRAY = (90, 90, 90)

# Warna Tetromino
COLORS = {
    'I': (0, 240, 240),   # Cyan
    'O': (240, 240, 0),   # Yellow
    'T': (160, 0, 240),   # Purple
    'S': (0, 240, 0),     # Green
    'Z': (240, 0, 0),     # Red
    'J': (0, 0, 240),     # Blue
    'L': (240, 160, 0),   # Orange
}

# Bentuk Tetromino didefinisikan sebagai rotasi-rotasi dengan koordinat (x, y)
# relatif terhadap pivot (kita gunakan kotak 4x4 dengan origin di kiri-atas bentuk)
# Setiap rotasi: daftar 4 posisi blok (x, y)
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# Skor per jumlah baris yang dibersihkan sekaligus
LINE_CLEAR_SCORES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}


class Piece:
    def __init__(self, kind: str):
        self.kind = kind
        self.rot = 0
        # posisi di grid (x, y), x kolom (0..COLS-1), y baris (0..ROWS-1)
        # spawn di atas tengah layar
        self.x = COLS // 2 - 2
        self.y = 0

    @property
    def color(self) -> Tuple[int, int, int]:
        return COLORS[self.kind]

    def blocks(self, rot: Optional[int] = None, pos: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        r = self.rot if rot is None else rot
        px, py = (self.x, self.y) if pos is None else pos
        coords = SHAPES[self.kind][r % 4]
        return [(px + cx, py + cy) for (cx, cy) in coords]


class Tetris:
    def __init__(self):
        pygame.init()
        self.play_width = COLS * BLOCK_SIZE
        self.play_height = ROWS * BLOCK_SIZE

        sidebar = 200
        width = self.play_width + BORDER * 2 + sidebar
        height = self.play_height + BORDER * 2

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Tetris - Pygame')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 22)
        self.big_font = pygame.font.SysFont('consolas', 48, bold=True)

        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current: Piece = self.random_piece()
        self.next_piece: Piece = self.random_piece()
        self.fall_timer = 0.0
        self.fall_interval = 0.8  # detik per turun otomatis
        self.soft_drop_multiplier = 10.0  # percepatan saat panah bawah ditahan
        self.game_over = False
        self.score = 0
        self.lines_cleared_total = 0

        # input repeat management
        self.move_delay = 0.12
        self.move_cooldown = 0.0

    def random_piece(self) -> Piece:
        kind = random.choice(list(SHAPES.keys()))
        return Piece(kind)

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < COLS and y < ROWS

    def valid(self, piece: Piece, rot: Optional[int] = None, pos: Optional[Tuple[int, int]] = None) -> bool:
        for (x, y) in piece.blocks(rot=rot, pos=pos):
            if not self.inside(x, y):
                return False
            if y >= 0:  # hanya cek tabrakan untuk baris yang terlihat
                if y < ROWS and self.grid[y][x] is not None:
                    return False
        return True

    def lock_piece(self, piece: Piece):
        for (x, y) in piece.blocks():
            if 0 <= y < ROWS:
                self.grid[y][x] = piece.color
        cleared = self.clear_lines()
        self.score += LINE_CLEAR_SCORES.get(cleared, 0)
        self.lines_cleared_total += cleared
        # Sedikit percepat kejatuhan seiring garis dibersihkan
        if cleared:
            self.fall_interval = max(0.1, self.fall_interval - 0.02 * cleared)

        # Spawn piece baru
        self.current = self.next_piece
        self.next_piece = self.random_piece()
        # Jika segera tidak valid => game over
        if not self.valid(self.current):
            self.game_over = True

    def clear_lines(self) -> int:
        new_grid: List[List[Optional[Tuple[int, int, int]]]] = []
        cleared = 0
        for y in range(ROWS):
            if all(self.grid[y][x] is not None for x in range(COLS)):
                cleared += 1
            else:
                new_grid.append(self.grid[y][:])
        while len(new_grid) < ROWS:
            new_grid.insert(0, [None for _ in range(COLS)])
        self.grid = new_grid
        return cleared

    def hard_drop(self):
        # Turunkan hingga mentok, lalu kunci
        y = self.current.y
        while True:
            if self.valid(self.current, pos=(self.current.x, y + 1)):
                y += 1
            else:
                break
        self.current.y = y
        self.lock_piece(self.current)

    def try_move(self, dx: int, dy: int) -> bool:
        nx, ny = self.current.x + dx, self.current.y + dy
        if self.valid(self.current, pos=(nx, ny)):
            self.current.x, self.current.y = nx, ny
            return True
        return False

    def try_rotate(self, dr: int):
        new_rot = (self.current.rot + dr) % 4
        # Kick sederhana: coba posisi sekarang, lalu geser kiri/kanan bila perlu
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)]
        for (kx, ky) in kicks:
            nx, ny = self.current.x + kx, self.current.y + ky
            if self.valid(self.current, rot=new_rot, pos=(nx, ny)):
                self.current.rot = new_rot
                self.current.x, self.current.y = nx, ny
                return
        # jika semua gagal, tidak berputar

    def ghost_position(self) -> int:
        # Kembalikan y posisi ghost untuk current.x
        y = self.current.y
        while self.valid(self.current, pos=(self.current.x, y + 1)):
            y += 1
        return y

    def draw_block(self, surf, x: int, y: int, color: Tuple[int, int, int], alpha: Optional[int] = None):
        px = BORDER + x * BLOCK_SIZE
        py = BORDER + y * BLOCK_SIZE
        rect = pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE)
        if alpha is None:
            pygame.draw.rect(surf, color, rect)
        else:
            # gambar dengan transparansi untuk ghost
            tmp = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            tmp.fill((*color, alpha))
            surf.blit(tmp, (px, py))
        # border blok
        pygame.draw.rect(surf, GRAY, rect, 1)

    def draw_grid(self):
        # background playfield
        play_rect = pygame.Rect(BORDER, BORDER, self.play_width, self.play_height)
        pygame.draw.rect(self.screen, BLACK, play_rect)
        # garis grid vertikal
        for x in range(COLS + 1):
            px = BORDER + x * BLOCK_SIZE
            pygame.draw.line(self.screen, LIGHT_GRAY, (px, BORDER), (px, BORDER + self.play_height))
        # garis grid horizontal
        for y in range(ROWS + 1):
            py = BORDER + y * BLOCK_SIZE
            pygame.draw.line(self.screen, LIGHT_GRAY, (BORDER, py), (BORDER + self.play_width, py))

        # gambar blok terkunci
        for y in range(ROWS):
            for x in range(COLS):
                color = self.grid[y][x]
                if color is not None:
                    self.draw_block(self.screen, x, y, color)

        # ghost piece
        gy = self.ghost_position()
        for (x, y) in self.current.blocks(pos=(self.current.x, gy)):
            if y >= 0:
                self.draw_block(self.screen, x, y, self.current.color, alpha=60)

        # current piece
        for (x, y) in self.current.blocks():
            if y >= 0:
                self.draw_block(self.screen, x, y, self.current.color)

    def draw_sidebar(self):
        sidebar_x = BORDER * 2 + self.play_width
        # judul
        title_surf = self.big_font.render('TETRIS', True, WHITE)
        self.screen.blit(title_surf, (sidebar_x, BORDER))

        # skor
        score_lbl = self.font.render('Skor:', True, WHITE)
        self.screen.blit(score_lbl, (sidebar_x, BORDER + 80))
        score_val = self.font.render(f'{self.score}', True, WHITE)
        self.screen.blit(score_val, (sidebar_x, BORDER + 105))

        # lines
        lines_lbl = self.font.render('Lines:', True, WHITE)
        self.screen.blit(lines_lbl, (sidebar_x, BORDER + 140))
        lines_val = self.font.render(f'{self.lines_cleared_total}', True, WHITE)
        self.screen.blit(lines_val, (sidebar_x, BORDER + 165))

        # next piece preview
        next_lbl = self.font.render('Next:', True, WHITE)
        self.screen.blit(next_lbl, (sidebar_x, BORDER + 210))

        # gambar preview di kotak 6x6 blok
        preview_top = BORDER + 240
        preview_left = sidebar_x
        preview_cell = BLOCK_SIZE // 1
        box_rect = pygame.Rect(preview_left, preview_top, preview_cell * 6, preview_cell * 6)
        pygame.draw.rect(self.screen, (15, 15, 15), box_rect)
        pygame.draw.rect(self.screen, GRAY, box_rect, 1)

        for (x, y) in self.next_piece.blocks(pos=(2, 2)):
            px = preview_left + x * preview_cell
            py = preview_top + y * preview_cell
            rect = pygame.Rect(px, py, preview_cell, preview_cell)
            pygame.draw.rect(self.screen, self.next_piece.color, rect)
            pygame.draw.rect(self.screen, GRAY, rect, 1)

        # kontrol
        controls_y = preview_top + 6 * preview_cell + 20
        controls = [
            'Kontrol:',
            'Panah Kiri/Kanan: Gerak',
            'Panah Atas: Rotasi',
            'Panah Bawah: Soft Drop',
            'SPACE: Hard Drop',
            'R: Restart',
            'ESC: Keluar',
        ]
        for i, text in enumerate(controls):
            surf = self.font.render(text, True, WHITE)
            self.screen.blit(surf, (sidebar_x, controls_y + i * 24))

    def reset(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current = self.random_piece()
        self.next_piece = self.random_piece()
        self.fall_timer = 0.0
        self.fall_interval = 0.8
        self.game_over = False
        self.score = 0
        self.lines_cleared_total = 0

    def update(self, dt: float):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()

        # gerak kiri/kanan dengan repeat sederhana
        self.move_cooldown -= dt
        horizontal = 0
        if keys[pygame.K_LEFT]:
            horizontal = -1
        elif keys[pygame.K_RIGHT]:
            horizontal = 1
        if horizontal != 0 and self.move_cooldown <= 0:
            if self.try_move(horizontal, 0):
                self.move_cooldown = self.move_delay
            else:
                self.move_cooldown = 0.05

        # jatuh otomatis, percepat jika soft drop
        interval = self.fall_interval
        if keys[pygame.K_DOWN]:
            interval = max(0.02, self.fall_interval / self.soft_drop_multiplier)

        self.fall_timer += dt
        if self.fall_timer >= interval:
            self.fall_timer -= interval
            if not self.try_move(0, 1):
                # kunci jika tidak bisa turun
                self.lock_piece(self.current)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    self.reset()
                if self.game_over:
                    continue
                if event.key == pygame.K_UP:
                    self.try_rotate(1)
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()

    def draw(self):
        self.screen.fill((25, 25, 25))
        self.draw_grid()
        self.draw_sidebar()

        if self.game_over:
            overlay = pygame.Surface((self.play_width, self.play_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (BORDER, BORDER))
            text = self.big_font.render('GAME OVER', True, WHITE)
            hint = self.font.render('Tekan R untuk restart', True, WHITE)
            tx = BORDER + (self.play_width - text.get_width()) // 2
            ty = BORDER + self.play_height // 2 - 40
            hx = BORDER + (self.play_width - hint.get_width()) // 2
            hy = ty + 60
            self.screen.blit(text, (tx, ty))
            self.screen.blit(hint, (hx, hy))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == '__main__':
    game = Tetris()
    game.run()
