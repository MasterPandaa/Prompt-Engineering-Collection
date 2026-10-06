# Snake Game (Pygame)

Game Snake klasik dibuat dengan Python dan Pygame.

## Spesifikasi
- Ukuran layar: 600 x 400 piksel
- Ukuran sel/grid: 20 piksel
- Ular mulai di tengah layar, bergerak terus-menerus
- Kontrol: Panah (Atas/Bawah/Kiri/Kanan) atau WASD
- Tidak bisa membalik arah 180° secara langsung
- Makanan muncul di posisi acak, tidak menumpuk dengan tubuh ular
- Skor bertambah 1 dan ular bertambah 1 segmen saat memakan makanan
- Game Over jika menabrak dinding atau tubuh sendiri
- Tekan Enter untuk restart, Esc untuk keluar

## Persyaratan
- Python 3.8+

## Instalasi

Disarankan menggunakan virtual environment.

Windows PowerShell:

```powershell
# Dari folder proyek
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Menjalankan Game

```powershell
python snake.py
```

## Kontrol
- Panah Atas / W: Naik
- Panah Bawah / S: Turun
- Panah Kiri / A: Kiri
- Panah Kanan / D: Kanan
- Enter: Restart saat Game Over
- Esc: Keluar

## Catatan
- FPS default adalah 12 (kecepatan ular). Anda dapat mengubah variabel `FPS` di `snake.py` untuk menyesuaikan kecepatan.
- Garis grid halus dapat ditampilkan dengan membuka komentar fungsi `draw_grid(screen)` di bagian gambar (render).
