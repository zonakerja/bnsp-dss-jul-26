# Laporan Review Proses Pemodelan (SKKNI Unit 11 — J.62DMI00.015.1)

Dokumen ini menilai **kesesuaian** dan **kualitas** proses pemodelan terhadap rencana
proyek (CLAUDE.md), sebagai bukti Unit Kompetensi 11.

## 1. Penilaian Kesesuaian Proses (Elemen 1)

Pemeriksaan tiap tahap CRISP-DM terhadap tahapan yang direncanakan:

| Tahap Direncanakan | Dilaksanakan | Status | Bukti |
|---|---|---|---|
| Objektif bisnis & metrik sukses | Ya | ✅ Sesuai | CLAUDE.md §2, halaman Beranda |
| Tujuan teknis (task = regresi) | Ya | ✅ Sesuai | metrics.json, halaman Beranda |
| Telaah data (tipe, statistik, hipotesis) | Ya | ✅ Sesuai | halaman Dataset & Telaah |
| Validasi & kelengkapan data | Ya | ✅ Sesuai | validate_data(), halaman Kualitas Data |
| Seleksi objek data (atribut & records) | Ya | ✅ Sesuai | preprocessing.clean_data() |
| Pembersihan data + log | Ya | ✅ Sesuai | log before/after, halaman Kualitas Data |
| Konstruksi fitur (agregasi + fitur waktu) | Ya | ✅ Sesuai | features.build_demand_dataset() |
| Skenario model (7 kandidat, metrik, uji) | Ya | ✅ Sesuai | model_comparison.csv |
| Bangun & optimasi model | Ya | ✅ Sesuai | RandomizedSearchCV, demand_model.pkl |
| Evaluasi pada data hold-out | Ya | ✅ Sesuai | test_predictions.csv, halaman Pemodelan |

**Tindak lanjut dari pemeriksaan:** Ditemukan & diperbaiki satu isu teknis penting saat
review — `TargetEncoder` mode `auto` salah mendeteksi target cacah sebagai *multiclass*
(koridor meledak menjadi 55 kolom, berpotensi bocor). Dikoreksi dengan
`target_type="continuous"` lalu model dilatih ulang. Ini contoh kontrol kualitas yang
menemukan dan menutup potensi kebocoran sebelum finalisasi.

## 2. Penilaian Kualitas Proses (Elemen 2)

| Aspek Kualitas | Penilaian |
|---|---|
| **Anti-kebocoran (leakage)** | ✅ Fitur demografi per-slot sengaja diabaikan; encoding koridor cross-fitted; travel_time & payAmount tidak dipakai sbg prediktor |
| **Reproducibility** | ✅ `random_state=42` konsisten; artefak model & metrik tersimpan |
| **Perbandingan adil** | ✅ 7 model dievaluasi pada pipeline & split identik; baseline disertakan |
| **Pemilihan model** | ✅ Berdasarkan CV (bukan test tunggal); tuning hanya dipertahankan bila CV membaik |
| **Metrik memenuhi target** | ✅ MAE 1,05 ≤ 1,5 (utama); R² 0,715 ≥ 0,70 (sekunder) |
| **Kejujuran evaluasi** | ✅ Target aspiratif R²≥0,80 dilaporkan tidak tercapai + alasan (noise Poisson) |

## 3. Kesimpulan Review

Proses pemodelan **sesuai rencana** dan **berkualitas baik**. Model final
(**XGBoost, objective=count:poisson**) memenuhi kriteria kesuksesan operasional dan
statistik, unggul jauh dari baseline & regresi linier.

**Keterbatasan yang diakui:**
1. Data hanya 1 bulan → belum menangkap musiman tahunan / hari libur nasional.
2. Granularitas koridor-jam memiliki batas bawah *noise Poisson* (rata-rata cacah ~3).
3. Sebagian kolom dataset bersifat sintetis (durasi perjalanan acak).

**Rekomendasi pengembangan:**
- Tambah rentang data (multi-bulan/tahun) untuk pola musiman.
- Fitur eksternal: cuaca, hari libur, event besar.
- Uji model deret waktu (SARIMA/Prophet) & model cacah lanjutan (Negative Binomial).
- Evaluasi berkala (monitoring) setelah deployment untuk deteksi *drift*.
