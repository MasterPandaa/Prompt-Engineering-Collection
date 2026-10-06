# 📦 Prompt Engineering Collection

> **Research & Experiments Repository** — Kumpulan data kode hasil penelitian evaluasi kualitas kode LLM menggunakan Static Application Security Testing (SAST), berbagai teknik Prompt Engineering, serta eksperimen game generation.

---

## 📄 Publikasi Ilmiah Utama

| Metadata | Keterangan |
|---|---|
| **Judul Jurnal** | **SAST Implementation for Evaluating LLM-Generated Code Quality using Prompt Engineering** |
| **Penulis** | Abdillah |
| **Publikasi** | SISTEMASI: Jurnal Sistem Informasi |
| **Edisi** | Vol. 15, No. 5 (2026) |
| **Akreditasi** | **Sinta 3** |
| **DOI** | [https://doi.org/10.32520/stmsi.v15i5.6395](https://doi.org/10.32520/stmsi.v15i5.6395) |

---

## 📁 Struktur & Organisasi Repository

Repository ini merupakan konsolidasi dari **218 repository eksperimen** (200 dataset penelitian jurnal + 18 eksperimen game generation):

```
Prompt-Engineering-Collection/
│
├── Zeroshot/             # Zero-Shot Prompting (50 Repositories)
│   ├── Series-1/         # Zeroshot1   .. Zeroshot10
│   ├── Series-2/         # 2.Zeroshot1 .. 2.Zeroshot10
│   ├── Series-3/         # 3.Zeroshot1 .. 3.Zeroshot10
│   ├── Series-4/         # 4.Zeroshot1 .. 4.Zeroshot10
│   └── Series-5/         # 5.Zeroshot1 .. 5.Zeroshot10
│
├── Fewshot/              # Few-Shot Prompting (50 Repositories)
│   ├── Series-1/         # Fewshot1   .. Fewshot10
│   ├── Series-2/         # 2.Fewshot1 .. 2.Fewshot10
│   ├── Series-3/         # 3.Fewshot1 .. 3.Fewshot10
│   ├── Series-4/         # 4.Fewshot1 .. 4.Fewshot10
│   └── Series-5/         # 5.Fewshot1 .. 5.Fewshot10
│
├── CoT/                  # Chain-of-Thought Prompting (50 Repositories)
│   ├── Series-1/         # CoT1   .. CoT10
│   ├── Series-2/         # 2.CoT1 .. 2.CoT10
│   ├── Series-3/         # 3.CoT1 .. 3.CoT10
│   ├── Series-4/         # 4.CoT1 .. 4.CotT10
│   └── Series-5/         # 5.CoT1 .. 5.CoT10
│
├── Rolebased/            # Role-Based Prompting (50 Repositories)
│   ├── Series-1/         # Rolebased1   .. Rolebased10
│   ├── Series-2/         # 2.Rolebased1 .. 2.Rolebased10
│   ├── Series-3/         # 3.Rolebased1 .. 3.Rolebased10
│   ├── Series-4/         # 4.Rolebased1 .. 4.Rolebased10
│   └── Series-5/         # 5.Rolebased1 .. 5.Rolebased10
│
└── Game-Experiments/     # LLM Code Generation: Game Projects (18 Repositories)
    ├── Chess/            # zero-chess-1..3, few-chess-1..3
    ├── Pacman/           # zero-pacman-1..3
    ├── Pong/             # zero-pong-1..3
    ├── Snake/            # zero-snake-1..3
    └── Tetris/           # zero-tetris-1..3
```

---

## 🔬 Metodologi Penelitian

1. **Prompt Engineering Strategies:**
   - **Zero-Shot:** Pemberian instruksi langsung tanpa contoh sebelumnya.
   - **Few-Shot:** Penyertaan contoh pasangan input-output yang diharapkan sebelum prompt utama.
   - **Chain-of-Thought (CoT):** Panduan penalaran bertahap untuk menghasilkan logika kode yang runtut.
   - **Role-Based:** Penetapan persona sistem spesifik (misal: *Senior Secure Software Engineer*).

2. **Evaluasi Keamanan & Kualitas Kode:**
   - Implementasi Static Application Security Testing (SAST) menggunakan aturan OWASP Top 10 dan CWE.
   - Analisis kerentanan, False Positive, dan False Negative rate pada kode hasil generasi LLM.

---

## 📜 Sitasi (Citation)

```bibtex
@article{abdillah2026sast,
  title={SAST Implementation for Evaluating LLM-Generated Code Quality using Prompt Engineering},
  author={Abdillah},
  journal={SISTEMASI: Jurnal Sistem Informasi},
  volume={15},
  number={5},
  year={2026},
  doi={10.32520/stmsi.v15i5.6395}
}
```

---

<p align="center">
  <img src="https://img.shields.io/badge/Sinta-3-blue?style=for-the-badge" alt="Sinta 3"/>
  <img src="https://img.shields.io/badge/Journal-SISTEMASI-green?style=for-the-badge" alt="SISTEMASI"/>
  <img src="https://img.shields.io/badge/DOI-10.32520%2Fstmsi.v15i5.6395-orange?style=for-the-badge" alt="DOI"/>
</p>
