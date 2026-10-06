# Pong AI (Pygame)

Game Pong sederhana dengan AI menggunakan Pygame.

## Cara Menjalankan

1. Buat virtual environment (opsional tapi disarankan):
   
   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .venv\\Scripts\\Activate.ps1
   ```

2. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```

3. Jalankan game:
   ```powershell
   python pong_ai.py
   ```

## Kontrol
- W / Panah Atas: Gerak ke atas
- S / Panah Bawah: Gerak ke bawah
- ESC: Keluar

## Catatan
- AI mengikuti posisi Y bola dengan kecepatan sedikit di bawah pemain agar permainan seimbang.
- Bola akan di-reset ke tengah ketika salah satu sisi kebobolan dan skor bertambah.
