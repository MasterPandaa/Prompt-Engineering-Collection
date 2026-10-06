# Snake (Pygame)

Game Snake klasik yang diimplementasikan dengan Pygame. Fokus pada kode yang bersih, efisien, dan mudah dipelihara.

## Fitur
- Layar 600x400 dengan grid 20px.
- Class `Snake` dan `Food` untuk struktur rapi.
- Kontrol panah yang responsif dengan guard agar tidak bisa putar balik arah.
- Pertumbuhan yang akurat saat memakan makanan.
- Deteksi tabrakan dinding dan tubuh sendiri (Game Over) + restart dengan Enter.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
1. Buat dan aktifkan virtual environment (opsional namun direkomendasikan).
2. Instal dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan
```bash
python main.py
```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan: Gerak ular
- Enter: Restart saat Game Over
- Esc: Keluar

## Struktur File
- `main.py`: Entry point; loop utama, class `Snake`, class `Food`, render, input, dan logika game.
- `requirements.txt`: Dependensi Python.

## Catatan Teknis
- Grid: 30x20 sel (600x400 dengan ukuran sel 20).
- `Snake.set_direction()` mencegah reverse direction secara langsung.
- `Food.respawn()` memilih sel kosong secara efisien menggunakan set posisi ular.
- Kecepatan game diatur oleh konstanta `FPS` (default 12). Naikkan untuk meningkatkan tingkat kesulitan.
