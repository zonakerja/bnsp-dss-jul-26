# CLAUDE.md — Perencanaan Portofolio Data Science (BNSP)

> **Dokumen ini adalah blueprint proyek.** Tujuannya: memandu pembangunan portofolio
> Data Scientist yang **memenuhi seluruh 11 Unit Kompetensi SKKNI Skema *Ilmuwan Data
> (Data Scientist) — DSS.01.00.23*** sekaligus tampil **modern, menarik, dan memukau
> asesor**. Belum ada kode yang ditulis — file ini disepakati dulu sebelum implementasi.

---

## 1. Ringkasan Eksekutif

| Aspek | Keputusan |
|---|---|
| **Judul Proyek** | **TransJakarta Passenger Analytics & Demand Prediction** |
| **Domain** | Transportasi publik perkotaan (smart-card / tap-in tap-out) |
| **Tipe ML Inti** | **Supervised Regression** — memprediksi jumlah penumpang (demand) |
| **Analisis Pendukung** | EDA mendalam + analisis geospasial halte |
| **Metodologi** | CRISP-DM (Business → Data → Modeling → Evaluation → Deployment) |
| **Deliverable** | (1) Skrip Python modular, (2) Aplikasi **Streamlit** ter-deploy, (3) **PPT** presentasi |
| **Dataset** | `datasets/dfTransjakarta180kRows.csv` — 189.500 baris × 22 kolom |
| **Role Model UI** | Portofolio Indekos DIY (Streamlit) — struktur multi-halaman, bersih, interaktif |

**Pernyataan masalah bisnis (satu kalimat):** *TransJakarta perlu memprediksi lonjakan
jumlah penumpang per koridor dan per jam agar penjadwalan armada, penempatan petugas,
dan mitigasi kepadatan di jam sibuk menjadi lebih efisien.*

---

## 2. Pemahaman Bisnis (SKKNI Unit 1 & 2)

### 2.1 Latar Belakang & Permasalahan Bisnis
TransJakarta melayani jutaan perjalanan/bulan. Ketidakseimbangan antara **jumlah armada
yang tersedia** dan **permintaan aktual penumpang** menyebabkan: (a) penumpukan penumpang
pada jam sibuk, (b) armada kosong/underutilized pada jam lengang, (c) alokasi SDM (petugas
halte) tidak optimal. Operator membutuhkan **estimasi permintaan yang dapat diandalkan**.

### 2.2 Objektif Bisnis
1. Memahami **pola pergerakan penumpang** (jam, hari, koridor, demografi).
2. Membangun model yang **memprediksi jumlah penumpang** pada suatu koridor/jam/hari.
3. Menyediakan **alat bantu keputusan interaktif** (Streamlit) untuk perencanaan operasional.

### 2.3 Metrik Kesuksesan Bisnis
- Model dapat menjelaskan variasi permintaan dengan **R² ≥ 0,80** pada data uji.
- Kesalahan prediksi rata-rata (**MAE**) cukup kecil untuk dipakai perencanaan (target
  MAE relatif rendah terhadap rata-rata demand per koridor-jam).
- Dashboard mampu menampilkan insight yang **actionable** (jam sibuk, koridor tersibuk).

### 2.4 Tujuan Teknis Data Science (Unit 2)
- **Task DS:** *Supervised learning — Regression*.
- **Target (label):** `jumlah_penumpang` = banyaknya tap-in pada unit (koridor × tanggal × jam).
- **Kriteria kesuksesan teknis:** R², MAE, RMSE, MAPE pada test set; model mengungguli
  baseline (rata-rata historis & regresi linier).

### 2.5 Sumber Daya, Asumsi, Batasan, Risiko (Unit 1 — Elemen 2 & 3)
- **Sumber daya:** dataset 1 bulan (April 2023), Python + ekosistem PyData, Streamlit Cloud.
- **Asumsi:** pola April 2023 mewakili pola operasional umum; timestamp valid.
- **Batasan:** data 1 bulan (tidak menangkap musiman tahunan/hari libur nasional); sebagian
  kolom sintetis (mis. *travel time* tidak berkorelasi dengan jarak → **tidak** dijadikan target).
- **Risiko & mitigasi:**
  - *Data sintetis / kolom bocor* → seleksi fitur hati-hati, hindari kebocoran target.
  - *Missing values* (tap-out, koridor) → strategi pembersihan eksplisit (lihat §5).
  - *Overfitting* → cross-validation + regularisasi + hold-out test.
- **Biaya–keuntungan:** biaya komputasi minim (data ~45 MB, model tree ringan); keuntungan
  potensial besar (efisiensi armada & SDM).

---

## 3. Dataset — Struktur & Temuan Awal

**File:** `datasets/dfTransjakarta180kRows.csv` — **189.500 baris × 22 kolom**, periode
**1–30 April 2023**, **10.000 kartu unik**.

| Kolom | Tipe | Keterangan | Missing |
|---|---|---|---|
| `transID` | str | ID transaksi unik | 0 |
| `payCardID` | int | ID kartu (10.000 unik) | 0 |
| `payCardBank` | cat | Penerbit kartu: dki, emoney, brizzi, bni, online, flazz | 0 |
| `payCardName` | str | Nama pemegang (sintetis) | 0 |
| `payCardSex` | cat | F (101.790) / M (87.710) | 0 |
| `payCardBirthDate` | int | Tahun lahir (1946–2012) → untuk fitur **usia** | 0 |
| `corridorID` / `corridorName` | cat | Koridor/rute (216 nama unik) | 6.980 / 13.528 |
| `direction` | bin | Arah 0/1 (seimbang) | 0 |
| `tapInStops`, `tapInStopsName`, `tapInStopsLat/Lon`, `stopStartSeq`, `tapInTime` | mix | Data **tap masuk** (+ geolokasi) | tapInStops 7.241 |
| `tapOutStops`, ...Name/Lat/Lon, `stopEndSeq`, `tapOutTime` | mix | Data **tap keluar** | ~6.720–12.369 |
| `payAmount` | num | Tarif: **0** (rute JAK/Mikrotrans gratis), **3500** (BRT), **20000** (premium) | 3.718 |

### Temuan yang menentukan desain model
1. **Pola jam sangat kuat** → puncak pagi (jam **6–7**) & sore (jam **16–17**), lengang siang.
2. **Hari kerja vs akhir pekan** → ~34.200 tap/hari kerja vs ~9.250/akhir pekan (**±3,7×**). Sinyal kuat.
3. **Travel time acak** (korelasi ≈ 0,006 dengan jarak) → **BUKAN** target. Digunakan hanya untuk EDA.
4. **Tarif deterministik** dari jenis koridor (JAK ⇒ 0) → berisiko *leakage*, dipakai untuk EDA/insight saja, bukan target utama.
5. **182.780 perjalanan lengkap** (punya tap-out) → cukup untuk analisis O–D & geospasial.

### Hipotesis awal (Unit 3 — Elemen 3)
- H1: Demand jam sibuk pagi/sore jauh lebih tinggi (**bimodal**).
- H2: Demand hari kerja > akhir pekan secara signifikan.
- H3: Sebagian kecil koridor menyumbang mayoritas perjalanan (distribusi *long-tail*).
- H4: Fitur waktu (jam, hari) adalah prediktor demand terkuat, mengungguli fitur demografi.

---

## 4. Peta Kompetensi SKKNI → Bagian Portofolio

> Prinsip: kompetensi **tercakup secara alami** dalam alur CRISP-DM, tidak perlu poin-per-poin eksplisit.

| # | Kode Unit | Judul Unit | Dibuktikan di |
|---|---|---|---|
| 1 | J.62DMI00.001.1 | Menentukan Objektif Bisnis | §2 + Halaman **Beranda** (masalah, objektif, metrik, risiko, biaya) |
| 2 | J.62DMI00.002.1 | Menentukan Tujuan Teknis DS | §2.4 + Beranda (task DS = regresi, kriteria sukses teknis) |
| 3 | J.62DMI00.005.1 | Menelaah Data | Halaman **Dataset & Telaah** + **EDA** (tipe/relasi data, statistik, visualisasi, hipotesis) |
| 4 | J.62DMI00.006.1 | Memvalidasi Data | Halaman **Kualitas Data** (kelengkapan, cek missing, rekomendasi) |
| 5 | J.62DMI00.007.1 | Menentukan Objek Data | §5 seleksi atribut & records (kriteria + teknik pemilihan) |
| 6 | J.62DMI00.008.1 | Membersihkan Data | §5 pembersihan (strategi, koreksi, laporan & evaluasi) |
| 7 | J.62DMI00.009.1 | Mengkonstruksi Data | §6 Feature Engineering (transformasi + fitur baru + dokumentasi) |
| 8 | J.62DMI00.012.1 | Membangun Skenario Model | §7 (teknik pemodelan, skenario uji, metrik evaluasi) |
| 9 | J.62DMI00.013.1 | Membangun Model | §7 (parameter, tools, algoritma, optimasi/tuning) |
| 10 | J.62DMI00.014.1 | Mengevaluasi Hasil Pemodelan | §8 (uji data hold-out, penilaian metrik, dokumentasi) |
| 11 | J.62DMI00.015.1 | Melakukan Proses Review Pemodelan | §8.3 (review kesesuaian & kualitas proses vs rencana) |

---

## 5. Persiapan Data (Unit 4, 5, 6)

### 5.1 Validasi & Kelengkapan (Unit 4)
- Laporan **missing value** per kolom + persentase.
- Cek konsistensi: `tapOutTime` ≥ `tapInTime`; koordinat dalam bounding-box Jabodetabek;
  `payAmount` ∈ {0, 3500, 20000}; tahun lahir masuk akal.
- **Rekomendasi kualitas & kecukupan data** ditulis eksplisit.

### 5.2 Seleksi Objek Data (Unit 5)
- **Kriteria pemilihan:** hanya baris ber-timestamp valid & ber-koridor (untuk model demand
  level koridor); baris tanpa koridor → kategori `Unknown` atau dikeluarkan (didokumentasikan).
- **Atribut (kolom)** relevan model: waktu (`tapInTime`), `corridorID/Name`, demografi
  agregat. **Records (baris)** difilter sesuai kriteria di atas.

### 5.3 Pembersihan Data (Unit 6)
| Masalah | Strategi Koreksi |
|---|---|
| Missing `tapOut*` (perjalanan tak lengkap) | Untuk model demand: **tetap dipakai** (hanya butuh tap-in). Untuk analisis O–D: dipisah/dilabeli "incomplete". |
| Missing `corridorID/Name` | Isi `Unknown` atau keluarkan (didokumentasikan & dievaluasi dampaknya). |
| Missing `payAmount` | Imputasi berdasarkan aturan koridor (JAK=0) atau median grup; hanya untuk EDA tarif. |
| Duplikasi / outlier waktu | Deteksi & tangani; catat di laporan pembersihan. |
| Tipe data | Parse `tapInTime`/`tapOutTime` → datetime; kategorikal → `category`. |

> Setiap langkah → **laporan pembersihan + evaluasi sebelum/sesudah** (Unit 6 Elemen 2).

---

## 6. Konstruksi Data / Feature Engineering (Unit 7)

Unit analisis model = **agregasi (koridor × tanggal × jam)** → target `jumlah_penumpang`.

**Fitur waktu (dari `tapInTime`):**
`hour`, `day_of_week`, `day_name`, `is_weekend`, `is_peak` (pagi 6–9 / sore 16–19),
`part_of_day` (pagi/siang/sore/malam), `week_of_month`, `date`.

**Fitur koridor:**
`corridor_type` (BRT / Mikrotrans-JAK / lainnya, dari prefiks ID), `corridor_mean_demand`
(rata-rata historis — hati-hati leakage, hitung via CV/fold), encoding koridor (target/one-hot).

**Fitur demografi agregat (opsional pada level koridor-jam):**
proporsi penumpang perempuan, rata-rata usia (`age = 2023 − birthYear`), kelompok usia dominan.

**Fitur turunan geospasial (untuk EDA & peta):** jarak *haversine* tap-in→tap-out, kepadatan halte.

> Dokumentasi: setiap transformasi & fitur baru dijelaskan (alasan + rumus) — Unit 7 Elemen 3.

---

## 7. Pemodelan (Unit 8 & 9)

### 7.1 Skenario Model (Unit 8)
- **Asumsi data:** hubungan fitur-target non-linier (efek jam & hari) → model *tree-based* cocok.
- **Kandidat teknik:**
  1. **Linear Regression** — baseline interpretatif.
  2. **Random Forest Regressor** — non-linier, robust.
  3. **Gradient Boosting / XGBoost** — kandidat performa terbaik.
- **Skenario uji:** split **train/test** (mis. berbasis tanggal / stratified), **k-fold CV**
  untuk pemilihan model & tuning.
- **Metrik evaluasi:** **R², MAE, RMSE, MAPE** (didokumentasikan sebelum training).

### 7.2 Membangun Model (Unit 9)
- **Parameter & toleransi:** definisikan grid hyperparameter (n_estimators, max_depth,
  learning_rate, dll) + nilai toleransi metrik (mis. target R² ≥ 0,80).
- **Tools:** `scikit-learn` (+ `xgboost` opsional), `Pipeline` (preprocessing + estimator).
- **Optimasi:** `GridSearchCV` / `RandomizedSearchCV` dengan CV.
- **Output:** model terbaik disimpan (`models/demand_model.pkl` via `joblib`) untuk dipakai app.

### 7.3 Baseline & perbandingan
Tabel perbandingan semua model (baseline vs tuned) pada metrik yang sama → dipamerkan di app & PPT.

---

## 8. Evaluasi & Review (Unit 10 & 11)

### 8.1 Evaluasi pada Data Riil / Hold-out (Unit 10)
- Uji model pada **test set** yang tak pernah dilihat saat training.
- Nilai berdasarkan metrik kesuksesan (§2.3 & §7.1); tampilkan:
  **prediksi vs aktual (scatter)**, **distribusi residual**, **feature importance**.

### 8.2 Dokumentasi Hasil
- Ringkasan metrik final + interpretasi bisnis (fitur waktu dominan → sesuai H4).

### 8.3 Review Proses Pemodelan (Unit 11)
- **Checklist kesesuaian** tiap tahap CRISP-DM vs rencana di file ini.
- **Penilaian kualitas** proses (apakah metrik memenuhi target? tindak lanjut bila belum:
  fitur tambahan, data lebih panjang, model lain).
- Catatan keterbatasan & rekomendasi pengembangan.

---

## 9. Aplikasi Streamlit — Struktur & Desain

**Gaya mengikuti role model** (sidebar navigation, bersih, interaktif, banyak grafik),
tetapi dimodernkan: tema konsisten, kartu metrik (KPI), grafik **Plotly** interaktif, peta.

### 9.1 Navigasi (sidebar radio / multipage)
| Halaman | Isi | Kompetensi |
|---|---|---|
| 🏠 **Beranda** | Judul, latar belakang, objektif bisnis, metrik sukses, risiko, ringkasan proyek, profil asesi, alur CRISP-DM | U1, U2 |
| 📂 **Dataset & Telaah** | Deskripsi kolom, tipe data & relasi, statistik deskriptif, preview data, hipotesis | U3 |
| ✅ **Kualitas Data** | Peta missing value, validasi, langkah pembersihan (before/after), rekomendasi | U4, U5, U6 |
| 🔍 **EDA Interaktif** | Filter (koridor/hari/jam/gender). Grafik: pola jam (bimodal), hari kerja vs akhir pekan, top koridor, demografi (usia/gender/bank), tarif, perjalanan tak lengkap | U3 |
| 🗺️ **Peta Geospasial** | Peta halte tap-in/out + kepadatan (pydeck/folium), koridor tersibuk | U3 |
| 🤖 **Pemodelan** | Penjelasan fitur, skenario uji, tabel perbandingan model, metrik, feature importance, prediksi vs aktual, residual | U7–U11 |
| 🎯 **Simulasi Prediksi** | Form input (koridor, hari, jam) → **prediksi jumlah penumpang** + gauge & pembanding rata-rata | U9, U10 (demo) |
| 📌 **Kesimpulan** | Insight bisnis, rekomendasi actionable, keterbatasan, next steps | U1, U11 |

### 9.2 Prinsip Desain (modern & memukau)
- Palet warna konsisten (nuansa TransJakarta: biru–oranye), tipografi jelas, ikon/emoji hemat.
- `st.set_page_config` (wide layout, judul, favicon), CSS ringan untuk kartu KPI.
- **Grafik Plotly** interaktif (hover, zoom) — bukan gambar statis.
- **Caching** (`@st.cache_data`, `@st.cache_resource`) agar cepat; **model di-load dari .pkl**
  (dilatih offline), bukan dilatih saat runtime.
- Responsif & ringan agar mulus di **Streamlit Community Cloud**.

---

## 10. Struktur Folder & Tech Stack

```
bnsp-sertifikasi-data-science/
├── CLAUDE.md                     # dokumen ini
├── README.md                     # cara menjalankan + ringkasan proyek
├── requirements.txt              # dependensi
├── datasets/
│   └── dfTransjakarta180kRows.csv
├── src/                          # logika inti (reusable)
│   ├── data_loader.py            # load + parsing tipe (cached)
│   ├── preprocessing.py          # validasi, cleaning, seleksi
│   ├── features.py               # feature engineering (agregasi koridor×jam)
│   ├── train_model.py            # skrip training + simpan .pkl + laporan metrik
│   └── viz.py                    # fungsi grafik Plotly reusable
├── models/
│   ├── demand_model.pkl          # model terbaik (hasil train_model.py)
│   └── metrics.json              # metrik final untuk ditampilkan app
├── app.py                        # entry-point Streamlit (sidebar nav)
├── pages/                        # (opsi multipage native Streamlit)
├── notebooks/                    # opsional: 01_eda.ipynb, 02_modeling.ipynb (bukti kerja)
├── assets/                       # logo, css, gambar
└── ppt/                          # outline + file presentasi (.pptx)
```

**Tech stack:** Python 3.12 · pandas · numpy · scikit-learn · (xgboost opsional) ·
plotly · pydeck/folium + streamlit-folium · streamlit · joblib.

**Alur kerja:** `train_model.py` dijalankan sekali (offline) → hasilkan `.pkl` + `metrics.json`
→ `app.py` hanya **memuat** artefak (cepat, cocok untuk cloud).

---

## 11. Struktur PPT Presentasi (untuk Asesor)

Alur mengikuti CRISP-DM (≈13–15 slide):
1. **Cover** — judul, nama asesi, skema sertifikasi.
2. **Profil & Latar Belakang** masalah transportasi.
3. **Business Understanding** — masalah, objektif, metrik sukses, risiko & mitigasi (U1).
4. **Tujuan Teknis DS** — task = regresi, kriteria sukses teknis (U2).
5. **Dataset Overview** — sumber, ukuran, kolom kunci.
6. **Telaah Data** — statistik, visualisasi pola, hipotesis (U3).
7. **Validasi & Pembersihan Data** — missing, strategi, before/after (U4–U6).
8. **Feature Engineering** — fitur waktu/koridor/demografi (U7).
9. **Skenario Pemodelan** — teknik, skenario uji, metrik (U8).
10. **Pembangunan Model** — pipeline, tuning, tools (U9).
11. **Evaluasi** — tabel metrik, prediksi vs aktual, feature importance (U10).
12. **Review Pemodelan** — kesesuaian & kualitas proses vs rencana (U11).
13. **Insight Bisnis & Rekomendasi** — actionable.
14. **Deployment** — demo aplikasi Streamlit (screenshot + link).
15. **Kesimpulan & Penutup** — pencapaian metrik, keterbatasan, pengembangan.

---

## 12. Rencana Eksekusi (Tahapan Implementasi)

- [ ] **Tahap 0** — Setup: `requirements.txt`, struktur folder, `README.md`.
- [ ] **Tahap 1** — `data_loader.py` + `preprocessing.py` (validasi & cleaning) + laporan.
- [ ] **Tahap 2** — `features.py`: agregasi koridor×tanggal×jam + fitur.
- [ ] **Tahap 3** — `train_model.py`: baseline → RF/GBM → tuning → simpan `.pkl` + `metrics.json`.
- [ ] **Tahap 4** — `viz.py`: fungsi grafik Plotly + peta.
- [ ] **Tahap 5** — `app.py`: 8 halaman Streamlit sesuai §9.
- [ ] **Tahap 6** — Polish UI (tema, KPI cards, caching), uji lokal.
- [ ] **Tahap 7** — Deploy ke Streamlit Community Cloud + `README` link.
- [ ] **Tahap 8** — Susun **PPT** sesuai §11.
- [ ] **Tahap 9** — Review akhir vs checklist SKKNI (§4).

---

## 13. Catatan Penting (Aturan Main untuk Implementasi)

1. **Hindari kebocoran target (leakage):** jangan pakai `travel time` / `payAmount` sebagai
   prediktor demand; hitung `corridor_mean_demand` secara out-of-fold.
2. **Reproducible:** set `random_state`; simpan artefak model & metrik.
3. **Model dilatih offline**, app hanya memuat — agar deploy cloud ringan & cepat.
4. **Tetap fokus & tidak over-engineer** (sesuai arahan): satu model inti yang kuat +
   EDA/geospasial yang rapi, bukan banyak model setengah matang.
5. **Semua klaim di app/PPT harus jujur** terhadap hasil metrik aktual.
