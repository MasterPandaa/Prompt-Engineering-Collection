# Pong (Pygame)

Game Pong sederhana dengan Player vs AI menggunakan Python dan Pygame.

## Spesifikasi
- Layar: 800x600
- Kontrol Player (kiri): W (atas), S (bawah)
- Paddle AI (kanan): mengikuti sumbu-Y bola (dengan batas kecepatan agar masih bisa dikalahkan)
- Bola: memantul pada dinding atas/bawah dan pada paddle
- Skor: bola melewati sisi kiri -> AI +1; melewati sisi kanan -> Player +1

## Persiapan
1. Pastikan Python 3.8+
2. Install dependency:
   
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan
```bash
python pong.py
```

## Catatan
- Kecepatan bola bertambah tipis saat memukul paddle, dan arah vertikal dipengaruhi posisi benturan (memberi efek "spin").
- Kecepatan vertikal AI dibatasi agar permainan tetap fair.
