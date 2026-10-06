# Pong (Python + Pygame)

Game Pong sederhana dengan satu pemain (kiri) dan AI (kanan).

## Spesifikasi
- Resolusi layar: 800x600 piksel
- Kontrol pemain: `W` (atas) dan `S` (bawah)
- AI mengikuti sumbu-Y bola dengan kecepatan terbatas
- Bola memantul pada dinding atas/bawah dan pada paddle
- Sistem skor: bola lewat kiri → AI +1, lewat kanan → Pemain +1

## Persyaratan
- Python 3.8+ (disarankan)
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan
1. (Opsional) Buat virtual environment
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependensi
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game
   ```powershell
   python pong.py
   ```

## Kontrol
- `W`: Gerak ke atas
- `S`: Gerak ke bawah
- `Esc`: Keluar

## Catatan
- Jika font "Consolas" tidak tersedia, game akan menggunakan font default Pygame.
- Kecepatan AI dibuat tidak sempurna (ada toleransi) agar permainan lebih seimbang.
