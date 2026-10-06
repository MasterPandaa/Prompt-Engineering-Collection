# Catur Pygame (Huruf)

Implementasi sederhana game Catur menggunakan Pygame dengan representasi bidak sebagai huruf:
- Huruf besar = Putih (manusia)
- Huruf kecil = Hitam (AI)
- '.' = Kotak kosong

## Fitur
- Gerakan lengkap untuk: Pion, Kuda, Gajah, Benteng, Ratu, Raja.
- Validasi dasar: tidak bisa menabrak/capture bidak teman sendiri.
- Promosi pion otomatis menjadi Ratu saat mencapai baris terakhir.
- AI sederhana (greedy / minimax kedalaman 1): memilih langkah yang memaksimalkan keuntungan material setelah satu langkah.
- Render bidak menggunakan `pygame.font` (huruf ditampilkan di petak).

## Batasan (Kesederhanaan)
- Belum ada deteksi skak, skakmat, atau pat.
- Belum ada rokade (castling), en passant, atau aturan 50 langkah.
- Evaluasi hanya material (tanpa posisi).

## Struktur File
- `main.py` — kode utama game.
- `requirements.txt` — dependensi Python.

## Cara Menjalankan
1. Buat dan aktifkan virtual environment (opsional namun direkomendasikan).
2. Instal dependensi.
3. Jalankan game.

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Jika Anda tidak menggunakan virtual environment, Anda bisa langsung:
```powershell
pip install -r requirements.txt
python main.py
```

## Kontrol
- Klik kiri untuk memilih bidak putih dan klik lagi pada petak tujuan.
- Titik kecil menunjukkan petak-petak langkah yang valid untuk bidak yang dipilih.
- Setelah Anda melangkah, AI (hitam) akan melangkah otomatis.

## Catatan Teknis
- Papan 8x8, ukuran jendela 640x640 piksel, ukuran petak 80 piksel.
- Penilaian material menggunakan nilai umum: P=100, N=320, B=330, R=500, Q=900, K=20000.
- Fungsi utama:
  - `get_*_moves()` untuk setiap tipe bidak.
  - `get_all_moves(board, color)` menghasilkan semua langkah untuk satu warna.
  - `apply_move(board, move)` mengeksekusi langkah dan menangani promosi.
  - `choose_ai_move(board, color)` memilih langkah AI.

Selamat bermain! Jika ingin menambahkan fitur (mis. deteksi skak, rokade, en passant), beri tahu saya, saya akan membantu memperluasnya.
