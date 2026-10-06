# Pong AI (Pygame)

Game Pong sederhana dengan satu pemain melawan AI, dibangun menggunakan Pygame.

## Fitur
- Gerakan paddle pemain dengan tombol `W` (naik) dan `S` (turun)
- Paddle AI mengikuti posisi bola dengan kecepatan yang dapat diatur
- Pantulan bola pada dinding atas/bawah dan paddle, dengan sudut dinamis berdasarkan titik tabrakan
- Sistem skor sederhana
- Peningkatan kecepatan bola bertahap pada setiap pantulan paddle

## Persyaratan
- Python 3.8+
- Pygame (otomatis terpasang via `requirements.txt`)

## Cara Menjalankan (Windows)
1. Buat virtual environment (opsional tapi disarankan):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Jika perintah `python` tidak tersedia, coba gunakan `py -3`.

2. Instal dependensi:
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Jalankan game:
   ```powershell
   python pong_ai.py
   ```

## Kontrol
- `W`: Gerakkan paddle pemain ke atas
- `S`: Gerakkan paddle pemain ke bawah
- `Esc`: Keluar dari game

## Penyesuaian
Ubah nilai pada bagian konfigurasi di `pong_ai.py`:
- `AI_SPEED` untuk tingkat kesulitan AI
- `BALL_SPEED`, `BALL_SPEED_INCREMENT`, `BALL_SPEED_MAX` untuk kecepatan bola
- `WIDTH`, `HEIGHT`, ukuran paddle/bola

Selamat bermain!
