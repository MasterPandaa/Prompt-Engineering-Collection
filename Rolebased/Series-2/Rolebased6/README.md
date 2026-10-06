# Snake (Pygame)

Game Snake sederhana, bersih, dan efisien menggunakan Pygame.

## Spesifikasi
- Resolusi: 600x400
- Grid: ukuran sel 20px (30x20 sel)
- Kontrol: tombol panah (Up, Down, Left, Right)
- Restart: tekan `R` saat Game Over
- Keluar: `Esc` atau tutup jendela

## Struktur Kelas
- `Snake`:
  - Menyimpan posisi tubuh sebagai daftar koordinat grid `(x, y)`.
  - Mendukung pergantian arah dengan guard clause agar tidak langsung berbalik arah.
  - Mengelola pertumbuhan saat makan makanan.
- `Food`:
  - Menempatkan makanan pada sel acak yang tidak ditempati ular.
  - `respawn()` untuk memunculkan ulang makanan setelah dimakan.

## Menjalankan
1. Buat dan aktifkan virtual environment (opsional namun direkomendasikan).
2. Install dependencies.
3. Jalankan game.

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Jika Anda sudah memiliki environment aktif, cukup jalankan:
```powershell
pip install -r requirements.txt
python main.py
```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Mengubah arah ular (tidak bisa langsung berbalik arah)
- R: Restart saat game over
- Esc: Keluar

## Catatan Teknis
- Deteksi tabrakan mencakup tabrakan dinding dan tubuh sendiri.
- Kecepatan default: 10 langkah/detik. Mudah diubah lewat variabel `speed` pada `main()`.
- Penempatan makanan menggunakan set difference dari seluruh sel grid dengan posisi ular untuk efisiensi dan keakuratan.
