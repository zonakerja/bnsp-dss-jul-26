# 🚀 Panduan Deployment ke Streamlit Community Cloud

Aplikasi ini siap di-deploy **gratis** ke [Streamlit Community Cloud](https://share.streamlit.io).
Karena model dilatih **offline** (artefak `.pkl` sudah disimpan), aplikasi di cloud hanya
memuat model → ringan & cepat.

## Prasyarat
- Akun **GitHub**
- Akun **Streamlit Community Cloud** (login pakai GitHub)

## Langkah 1 — Persiapan Repository
Pastikan file berikut ikut ter-commit (JANGAN abaikan lewat `.gitignore`):
```
app.py
requirements.txt
src/                       (semua modul)
datasets/dfTransjakarta180kRows.csv
models/demand_model.pkl    ← WAJIB (agar tak perlu training di cloud)
models/metrics.json
reports/*.csv
.streamlit/config.toml     (tema biru-putih-jingga)
```
> Catatan: `.venv/` sudah diabaikan `.gitignore` — jangan di-commit.
> Dataset (~45 MB) & model (~2,5 MB) masih di bawah batas GitHub (100 MB/berkas). Aman.

## Langkah 2 — Push ke GitHub
```bash
git init
git add .
git commit -m "Portofolio TransJakarta Demand Prediction (BNSP)"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```

## Langkah 3 — Deploy
1. Buka https://share.streamlit.io → **New app**.
2. Pilih repository, branch `main`, dan **Main file path**: `app.py`.
3. Klik **Deploy**. Tunggu build (~2–3 menit).
4. Aplikasi live di `https://<nama-app>.streamlit.app`.

## Langkah 4 — Sebelum Presentasi
- Ganti `ASESI_NAME` di `src/config.py` dengan nama Anda, lalu commit & push ulang.
- Uji semua 8 halaman di URL cloud.
- Siapkan tautan untuk dimasukkan ke slide PPT (slide Deployment).

## Troubleshooting
| Masalah | Solusi |
|---|---|
| `ModuleNotFoundError` | Pastikan paket ada di `requirements.txt` |
| Model tidak ditemukan | Pastikan `models/demand_model.pkl` ikut ter-commit |
| App lambat saat pertama | Wajar (cold start); caching mempercepat akses berikutnya |
| Versi library bentrok | `requirements.txt` sudah memakai `>=` versi teruji |
