# Catur Pygame: Manusia vs AI

Game catur sederhana dengan Pygame tanpa aset eksternal (menggunakan Unicode untuk bidak). Manusia bermain putih, AI bermain hitam. AI memilih langkah yang menangkap bidak bernilai tertinggi; jika tidak ada, memilih langkah acak.

## Fitur
- Representasi papan 8x8 dengan list 2D
- Generator langkah pseudo-legal (pion, kuda, gajah, benteng, menteri, raja)
- Pion bisa maju 2 petak dari posisi awal, promosi otomatis menjadi menteri
- Tidak ada rokade, en passant, atau deteksi skak/mate
- Highlight seleksi dan langkah legal, tanda khusus untuk capture

## Prasyarat
- Python 3.9+

## Instalasi
```
pip install -r requirements.txt
```

## Menjalankan
```
python main.py
```

## Kontrol
- Klik kiri untuk memilih bidak putih dan klik lagi pada petak tujuan yang valid.
- Setelah kamu melangkah, AI akan bergerak otomatis.

## Catatan
Ini adalah implementasi edukatif dan sederhana. Untuk engine catur lengkap, perlu penambahan logika legal-move (tidak meninggalkan raja sendiri terskak), rokade, en passant, evaluasi dan pencarian yang lebih kuat, dll.
