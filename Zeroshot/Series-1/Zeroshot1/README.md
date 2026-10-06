# Pong (Python + Pygame)

Game Pong sederhana melawan AI.

## Spesifikasi
- Resolusi layar: 800 x 600.
- Paddle Kiri (Pemain): kontrol `W` (atas) dan `S` (bawah).
- Paddle Kanan (AI): mengikuti sumbu-Y bola dengan kecepatan maksimum agar tetap adil.
- Bola memantul pada dinding atas/bawah dan paddle.
- Sistem skor: bola melewati kiri -> poin AI, melewati kanan -> poin pemain. Skor ditampilkan di atas.

## Persyaratan
- Python 3.9+ (direkomendasikan)
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan (Windows)
1. Buat virtual environment (opsional tapi disarankan):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python pong.py
   ```

## Kontrol
- W: Gerak ke atas
- S: Gerak ke bawah
- ESC: Keluar

## Catatan
- Kecepatan AI dibatasi agar permainan tetap menantang namun adil.
- Kecepatan bola meningkat sedikit setiap kali mengenai paddle hingga batas tertentu.
