import sys
import random
import pygame

# Konfigurasi
COLS = 10
ROWS = 20
BLOCK = 30  # ukuran blok dalam piksel
BORDER = 2
WIDTH = COLS * BLOCK
HEIGHT = ROWS * BLOCK
FPS = 60

# Warna
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
LIGHT_GRAY = (60, 60, 60)
WHITE = (240, 240, 240)

# Definisi Tetromino: daftar rotasi; tiap rotasi berisi koordinat (x, y) relatif terhadap pivot
# Kita gunakan pivot pada pusat grid 4x4 (0..3). Posisi awal akan di-offset ke tengah papan.
# Warna unik tiap bentuk.
TETROMINOES = {
    'I': {
        'color': (0, 240, 240),
        'rotations': [
            [(0, 1), (1, 1), (2, 1), (3, 1)],  # ---- horizontal
            [(2, 0), (2, 1), (2, 2), (2, 3)],  # | vertikal
        ],
    },
    'O': {
        'color': (240, 240, 0),
        'rotations': [
            [(1, 1), (2, 1), (1, 2), (2, 2)],  # kotak, satu rotasi cukup
        ],
    },
    'T': {
        'color': (160, 0, 240),
        'rotations': [
            [(1, 1), (0, 1), (2, 1), (1, 2)],
            [(1, 1), (1, 0), (1, 2), (2, 1)],
            [(1, 1), (0, 1), (2, 1), (1, 0)],
            [(1, 1), (1, 0), (1, 2), (0, 1)],
        ],
    },
    'S': {
        'color': (0, 240, 0),
        'rotations': [
            [(1, 1), (2, 1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
        ],
    },
    'Z': {
        'color': (240, 0, 0),
        'rotations': [
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(2, 0), (2, 1), (1, 1), (1, 2)],
        ],
    },
    'J': {
        'color': (0, 0, 240),
        'rotations': [
            [(0, 1), (0, 2), (1, 2), (2, 2)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (1, 2), (0, 2)],
        ],
    },
    'L': {
        'color': (240, 160, 0),
        'rotations': [
            [(2, 1), (0, 2), (1, 2), (2, 2)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (0, 2), (1, 1), (2, 1)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    },
}

# Utilitas grid

def create_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS


def can_place(grid, cells):
    for x, y in cells:
        if not in_bounds(x, y):
            return False
        if grid[y][x] is not None:
            return False
    return True


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.defn = TETROMINOES[kind]
        self.color = self.defn['color']
        self.rot_index = 0
        # posisi origin (offset untuk rotasi berbasis grid 4x4)
        # spawn di atas tengah papan
        self.x = COLS // 2 - 2  # grid 4x4, mulai di kolom tengah-2
        self.y = -2  # mulai di atas layar agar I bisa masuk

    def cells(self, rot_index=None, offset=(0, 0)):
        if rot_index is None:
            rot_index = self.rot_index
        rot = self.defn['rotations'][rot_index % len(self.defn['rotations'])]
        ox, oy = offset
        return [(self.x + cx + ox, self.y + cy + oy) for (cx, cy) in rot]

    def try_move(self, grid, dx, dy):
        new_cells = self.cells(offset=(dx, dy))
        # validasi: boleh sebagian di atas layar (y < 0), tapi larang posisi keluar samping/bawah
        for x, y in new_cells:
            if x < 0 or x >= COLS:
                return False
            if y >= ROWS:
                return False
            if y >= 0 and grid[y][x] is not None:
                return False
        self.x += dx
        self.y += dy
        return True

    def try_rotate(self, grid):
        next_rot = (self.rot_index + 1) % len(self.defn['rotations'])
        test = self.cells(rot_index=next_rot)
        # wall kick sederhana: coba beberapa offset
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
        for kx, ky in kicks:
            ok = True
            for x, y in [(x + kx, y + ky) for (x, y) in test]:
                if x < 0 or x >= COLS:
                    ok = False
                    break
                if y >= ROWS:
                    ok = False
                    break
                if y >= 0 and grid[y][x] is not None:
                    ok = False
                    break
            if ok:
                self.rot_index = next_rot
                self.x += kx
                self.y += ky
                return True
        return False


def lock_piece(grid, piece):
    for x, y in piece.cells():
        if y < 0:
            # Menyentuh bagian atas saat lock -> game over
            return False
        grid[y][x] = piece.color
    return True


def clear_lines(grid):
    cleared = 0
    new_rows = []
    for r in range(ROWS):
        if all(grid[r][c] is not None for c in range(COLS)):
            cleared += 1
        else:
            new_rows.append(grid[r])
    while len(new_rows) < ROWS:
        new_rows.insert(0, [None for _ in range(COLS)])
    for r in range(ROWS):
        grid[r] = new_rows[r]
    return cleared


def hard_drop(grid, piece):
    distance = 0
    while piece.try_move(grid, 0, 1):
        distance += 1
    return distance


def draw_grid(surface, grid, font, score):
    surface.fill(BLACK)

    # blok yang sudah terkunci
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color is not None:
                pygame.draw.rect(
                    surface,
                    color,
                    (x * BLOCK + BORDER, y * BLOCK + BORDER, BLOCK - 2 * BORDER, BLOCK - 2 * BORDER),
                    border_radius=4,
                )

    # garis grid
    for x in range(COLS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (x * BLOCK, 0), (x * BLOCK, HEIGHT), 1)
    for y in range(ROWS + 1):
        pygame.draw.line(surface, LIGHT_GRAY, (0, y * BLOCK), (WIDTH, y * BLOCK), 1)

    # teks skor
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (8, 8))


def draw_piece(surface, piece):
    for x, y in piece.cells():
        if y >= 0:
            pygame.draw.rect(
                surface,
                piece.color,
                (x * BLOCK + BORDER, y * BLOCK + BORDER, BLOCK - 2 * BORDER, BLOCK - 2 * BORDER),
                border_radius=4,
            )


def main():
    pygame.init()
    pygame.display.set_caption("Tetris - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    grid = create_grid()
    current = Piece(random.choice(list(TETROMINOES.keys())))
    next_piece = Piece(random.choice(list(TETROMINOES.keys())))

    score = 0
    fall_time = 0.0
    fall_interval = 0.6  # detik per jatuh satu sel
    soft_drop_active = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    current.try_move(grid, -1, 0)
                elif event.key == pygame.K_RIGHT:
                    current.try_move(grid, 1, 0)
                elif event.key == pygame.K_DOWN:
                    # aktifkan soft drop (mempercepat jatuh otomatis)
                    soft_drop_active = True
                    # juga lakukan satu langkah turun segera saat ditekan
                    moved = current.try_move(grid, 0, 1)
                    if moved:
                        score += 1  # opsional: poin untuk soft drop
                elif event.key == pygame.K_UP:
                    current.try_rotate(grid)
                elif event.key == pygame.K_SPACE:
                    dropped = hard_drop(grid, current)
                    score += dropped * 2  # opsional: poin hard drop
                    # kunci segera
                    if not lock_piece(grid, current):
                        running = False
                        break
                    cleared = clear_lines(grid)
                    if cleared:
                        # Skor klasik: 1/2/3/4 garis = 100/300/500/800
                        score += [0, 100, 300, 500, 800][cleared]
                    current = next_piece
                    next_piece = Piece(random.choice(list(TETROMINOES.keys())))
                    # cek spawn collision -> game over
                    if not can_place(grid, [(x, y) for x, y in current.cells() if y >= 0]):
                        running = False
                        break
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop_active = False

        # jatuh otomatis
        current_interval = fall_interval * (0.15 if soft_drop_active else 1.0)
        if fall_time >= current_interval:
            fall_time = 0.0
            if not current.try_move(grid, 0, 1):
                # kunci
                if not lock_piece(grid, current):
                    running = False
                    continue
                cleared = clear_lines(grid)
                if cleared:
                    score += [0, 100, 300, 500, 800][cleared]
                current = next_piece
                next_piece = Piece(random.choice(list(TETROMINOES.keys())))
                # cek spawn collision -> game over
                if not can_place(grid, [(x, y) for x, y in current.cells() if y >= 0]):
                    running = False
                    continue

        # render
        draw_grid(screen, grid, font, score)
        draw_piece(screen, current)
        pygame.display.flip()

    # Game Over screen sederhana
    game_over(screen, font, score)


def game_over(screen, font, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    title = pygame.font.SysFont("consolas", 36, bold=True).render("GAME OVER", True, WHITE)
    info = font.render("Press R to Restart or ESC to Quit", True, WHITE)
    sc = font.render(f"Score: {score}", True, WHITE)

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    main()
                    return

        screen.blit(overlay, (0, 0))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 60))
        screen.blit(sc, ((WIDTH - sc.get_width()) // 2, HEIGHT // 2 - 10))
        screen.blit(info, ((WIDTH - info.get_width()) // 2, HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
