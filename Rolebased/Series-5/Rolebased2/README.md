# Mini Chess Engine (Python + Pygame)

Engine catur mini yang playable, dengan pemisahan `Board` (state papan) dan `Rules` (generator langkah), rendering Unicode berbasis font sistem, interaksi klik, dan AI sederhana berbasis evaluasi material.

## Fitur
- Representasi papan dan aturan gerak terpisah (`Board`, `Rules`).
- Rendering Unicode bidak catur dengan `pygame.font.SysFont` (tanpa aset gambar).
- Klik untuk memilih, klik untuk jalan. Highlight petak terpilih dan titik-hint langkah legal.
- AI satu-langkah (greedy) dengan evaluasi material, mencoba capture "gratis" jika tersedia.
- Promosi pion otomatis menjadi Queen.

Catatan: fitur lanjutan seperti rokade dan en passant belum diimplementasikan.

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi & Menjalankan
```bash
pip install -r requirements.txt
python mini_chess.py
```

- Putih (Anda) vs Hitam (AI).
- Klik bidak putih untuk memilih, lalu klik petak tujuan yang disorot titik untuk melangkah.

## Struktur Kode
- `mini_chess.py`:
  - `Piece`, `Move`, `Board` – representasi state dan utilitas material.
  - `Rules` – generator langkah per jenis bidak dan deteksi serangan petak.
  - `SimpleAI` – pemilih langkah sederhana berbasis material dan free capture.
  - `Renderer` – gambar papan, highlight, dan bidak Unicode.
  - `Game` – loop event Pygame dan kontrol input.

## Lisensi
MIT
