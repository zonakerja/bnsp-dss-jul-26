# 🚌 TransJakarta Passenger Analytics & Demand Prediction

Portofolio asesmen kompetensi **Data Scientist BNSP** — Skema *Ilmuwan Data
(Data Scientist) DSS.01.00.23*. Proyek menerapkan siklus **CRISP-DM** penuh untuk
menganalisis pola penumpang TransJakarta dan membangun model **prediksi jumlah
penumpang (demand)** per koridor/jam/hari, lalu men-deploy-nya sebagai aplikasi
**Streamlit** interaktif.

> Rencana & pemetaan kompetensi lengkap ada di [`CLAUDE.md`](CLAUDE.md).

## 📊 Dataset
`datasets/dfTransjakarta180kRows.csv` — 189.500 transaksi tap-in/tap-out smart-card
(April 2023, 10.000 kartu, 22 kolom).

## 🎨 Tema
Aksen **Biru – Putih – Jingga** (khas TransJakarta) — diatur di `.streamlit/config.toml`.

## 🛠️ Setup (menggunakan `uv`)

```bash
# 1. Install uv (jika belum ada)
python -m pip install uv

# 2. Buat virtual environment + install dependensi
uv venv --python 3.12
uv pip install -r requirements.txt

# 3. Aktifkan environment
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   Linux/Mac:
source .venv/bin/activate
```

## ▶️ Menjalankan

```bash
# Latih & bandingkan model (offline) -> simpan model terbaik + metrik
python -m src.train_model

# Jalankan aplikasi
streamlit run app.py
```

## 📁 Struktur Proyek

```
├── CLAUDE.md                 # Blueprint & pemetaan SKKNI
├── README.md
├── requirements.txt / pyproject.toml
├── .streamlit/config.toml    # Tema biru-putih-jingga
├── datasets/                 # Data mentah
├── src/
│   ├── config.py             # Path, konstanta, palet warna
│   ├── data_loader.py        # Muat data + ringkasan struktur
│   ├── preprocessing.py      # Validasi, seleksi, pembersihan (Unit 4-6)
│   ├── features.py           # Feature engineering (Unit 7)      [Tahap 2]
│   ├── train_model.py        # Latih & bandingkan model (Unit 8-11)[Tahap 3]
│   └── viz.py                # Grafik Plotly reusable            [Tahap 4]
├── models/                   # demand_model.pkl + metrics.json
├── reports/                  # laporan pembersihan & perbandingan model
├── app.py                    # Aplikasi Streamlit                [Tahap 5]
└── ppt/                      # Presentasi
```

## 📈 Ringkasan Model
Model terbaik: **XGBoost (objective=count:poisson)** — Test **R² = 0,715**, **MAE = 1,09**
penumpang/slot, RMSE = 1,47. Dipilih dari 7 kandidat via cross-validation. Unit analisis:
agregasi *(koridor × tanggal × jam)* = 61.730 slot.

## ✅ Status Pengembangan
- [x] **Tahap 0** — Setup environment, struktur, tema
- [x] **Tahap 1** — Data loader + validasi & pembersihan
- [x] **Tahap 2** — Feature engineering
- [x] **Tahap 3** — Training & perbandingan 7 model + tuning
- [x] **Tahap 4** — Modul visualisasi (15 grafik Plotly)
- [x] **Tahap 5** — Aplikasi Streamlit (9 halaman termasuk Analisis OD, teruji AppTest)
- [x] **Tahap 6** — Polish akhir (tema, KPI cards, caching, migrasi API)
- [ ] **Tahap 7** — Deploy ke Streamlit Cloud (lihat `DEPLOYMENT.md` — perlu akun Anda)
- [x] **Tahap 8** — PPT presentasi (`ppt/TransJakarta_Demand_Prediction_BNSP.pptx`, 16 slide)
- [x] **Tahap 9** — Review akhir vs SKKNI (`reports/review_pemodelan.md`)
