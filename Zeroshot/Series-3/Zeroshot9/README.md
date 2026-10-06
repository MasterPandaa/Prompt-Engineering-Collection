# Pacman (Python + Pygame)

Game Pacman klasik dengan layar 800x600, maze 2D hardcoded, dots, power-pellets, 4 hantu dengan AI sederhana, skor, dan nyawa.

## Persyaratan
- Python 3.9+
- Pygame

Install dependensi:

```
pip install -r requirements.txt
```

## Menjalankan

```
python main.py
```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Gerakkan Pacman
- Esc: Keluar

## Spesifikasi yang Diimplementasikan
- Layar 800x600
- Maze hardcoded (1 = dinding, 0 = jalur). Dots (2) dan Power-pellets (3) diinisialisasi dari jalur.
- Pacman bergerak grid-based, tidak menembus dinding.
- Dots dan power-pellets dapat dimakan. Power mode membuat hantu rentan beberapa detik.
- 4 Hantu dengan AI sederhana: memilih arah di persimpangan dengan bias mengejar Pacman (atau menghindar saat rentan).
- Menabrak hantu saat normal: nyawa berkurang dan reset posisi. Saat rentan: hantu dikirim ke markas.
- Tampilan skor dan nyawa. Menang jika semua dots dimakan; kalah jika nyawa habis.

## Catatan Teknis
- Ukuran grid 40x30 (tile 20px) agar pas pada 800x600.
- Pellets otomatis ditempatkan pada sel jalur kecuali area markas hantu dan posisi awal.
- Kecepatan dan durasi power mode dapat diubah di bagian konstanta.
