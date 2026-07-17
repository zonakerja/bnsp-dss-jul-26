# 📘 Panduan Kode & Arsitektur — TransJakarta Demand Prediction

> Dokumen referensi sintaks penting (Python, Machine Learning, Streamlit) **beserta contoh
> nyata dari proyek ini**, plus penjelasan arsitektur folder. Tujuannya: membantu Anda
> memahami & menjelaskan setiap baris kode saat asesmen BNSP.

**Daftar Isi**
1. [Python Dasar](#1-python-dasar)
2. [Pandas & NumPy — Manipulasi Data](#2-pandas--numpy--manipulasi-data)
3. [Machine Learning (scikit-learn + XGBoost)](#3-machine-learning-scikit-learn--xgboost)
4. [Streamlit — Aplikasi Web Data](#4-streamlit--aplikasi-web-data)
5. [Arsitektur Folder Aplikasi](#5-arsitektur-folder-aplikasi)

---

## 1. Python Dasar

### 1.1 Variabel & Tipe Data
```python
nama = "Mohammad Yusuf"     # str  (teks)
jumlah = 189500             # int  (bilangan bulat)
rata2 = 3.07                # float(desimal)
aktif = True                # bool (True/False)
kosong = None               # None (nilai kosong)
```

### 1.2 Struktur Data
```python
# List — koleksi terurut, bisa diubah
koridor = ["BRT", "Mikrotrans", "Pengumpan"]
koridor.append("Feeder")        # tambah elemen
koridor[0]                      # akses -> "BRT"

# Dict — pasangan key:value (dipakai di metrics.json)
metrik = {"R2": 0.715, "MAE": 1.05}
metrik["R2"]                    # akses nilai -> 0.715

# Tuple — seperti list tapi tidak bisa diubah
rentang_jam = (5, 21)

# Set — koleksi unik tanpa urutan
tarif_valid = {0.0, 3500.0, 20000.0}
```

### 1.3 Kontrol Alur
```python
# Percabangan
if hour in range(6, 10):
    kategori = "jam sibuk pagi"
elif hour in range(16, 20):
    kategori = "jam sibuk sore"
else:
    kategori = "lengang"

# Perulangan
for h in range(5, 22):          # 5..21
    print(h)

# List comprehension — cara ringkas membuat list (dipakai di viz.py)
peak = [1 if h in range(6, 10) else 0 for h in range(5, 22)]
```

### 1.4 Fungsi
```python
def hitung_usia(tahun_lahir, tahun_acuan=2023):   # 2023 = nilai default
    """Docstring: menjelaskan fungsi."""
    return tahun_acuan - tahun_lahir

usia = hitung_usia(1997)        # -> 26
```

### 1.5 Import Modul
```python
import pandas as pd            # beri alias
from pathlib import Path       # ambil bagian tertentu
from src import config         # impor modul internal proyek
```

### 1.6 Type Hints & f-string (dipakai di seluruh proyek)
```python
def load_raw_data(path: str | None = None) -> "pd.DataFrame":
    ...

r2 = 0.715
print(f"Akurasi model R² = {r2:.3f}")   # -> "Akurasi model R² = 0.715"
```

---

## 2. Pandas & NumPy — Manipulasi Data

> **pandas** = library utama untuk data tabular (DataFrame). **NumPy** = komputasi numerik/array.

### 2.1 Membaca & Melihat Data
```python
import pandas as pd

df = pd.read_csv("datasets/dfTransjakarta180kRows.csv")
df.head()            # 5 baris pertama
df.shape             # (189500, 22) -> (baris, kolom)
df.info()            # tipe data & memori
df.describe()        # statistik deskriptif kolom numerik
df.columns           # daftar nama kolom
df.dtypes            # tipe tiap kolom
```

### 2.2 Tipe Data & Parsing (dari `data_loader.py`)
```python
# Ubah teks menjadi tanggal-waktu
df["tapInTime"] = pd.to_datetime(df["tapInTime"], errors="coerce")

# Ubah menjadi kategori (hemat memori)
df["payCardBank"] = df["payCardBank"].astype("category")

# Integer nullable (boleh ada nilai kosong)
df["payCardBirthDate"] = pd.to_numeric(df["payCardBirthDate"], errors="coerce").astype("Int64")
```

### 2.3 Memilih & Menyaring (filter)
```python
df["corridorName"]                       # satu kolom (Series)
df[["corridorName", "payAmount"]]        # beberapa kolom

# Filter baris dengan kondisi (boolean masking)
akhir_pekan = df[df["tapInTime"].dt.dayofweek >= 5]

# Beberapa kondisi: & (dan), | (atau) — tiap kondisi dalam kurung
mask = (df["corridor_type"] == "BRT Koridor") & (df["payCardSex"] == "F")
subset = df[mask]
```

### 2.4 Menangani Nilai Kosong (dari `preprocessing.py`)
```python
df.isna().sum()                          # jumlah missing per kolom
df["corridorName"].fillna("Unknown")     # isi kosong dgn label
df.dropna(subset=["tapOutTime"])         # buang baris yg kosong di kolom tsb
df.drop_duplicates(subset=["transID"])   # buang duplikat
```

### 2.5 Kolom Baru & Fitur Waktu (dari `features.py`)
```python
df["age"] = 2023 - df["payCardBirthDate"]          # kolom turunan
df["hour"] = df["tapInTime"].dt.hour               # ekstrak jam
df["day_of_week"] = df["tapInTime"].dt.dayofweek   # 0=Senin..6=Minggu
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

# map() — memetakan nilai (dipakai untuk part_of_day)
df["part_of_day"] = df["hour"].map(lambda h: "Pagi" if h < 11 else "Siang")
```

### 2.6 Agregasi — `groupby` (inti pembentukan target)
```python
# Hitung jumlah penumpang per (koridor, tanggal, jam)
demand = (
    df.groupby(["corridorID", "date", "hour"])
      .size()                          # hitung jumlah baris tiap grup
      .reset_index(name="passenger_count")
)

# Agregasi lain
df.groupby("corridor_type")["payAmount"].mean()    # rata-rata
df["corridorName"].value_counts()                  # frekuensi tiap nilai
pd.crosstab(df["asal"], df["tujuan"])              # tabel silang (matriks OD)
```

### 2.7 NumPy — Operasi Numerik (dari `preprocessing.py` & `train_model.py`)
```python
import numpy as np

np.clip(predictions, 0, None)     # batasi nilai minimal 0 (cacah tak boleh negatif)
np.log1p(x)                       # log(1+x), transformasi
np.sqrt(a)                        # akar kuadrat (dipakai di haversine)
arr.mean(), arr.max(), arr.min()  # statistik array
```

---

## 3. Machine Learning (scikit-learn + XGBoost)

> Pola standar: **Split data → Bangun pipeline (praproses + model) → Latih → Evaluasi → Simpan**.

### 3.1 Membagi Data Latih & Uji
```python
from sklearn.model_selection import train_test_split

X = modeling[FITUR]           # matriks fitur
y = modeling["passenger_count"]  # target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42   # 80% latih, 20% uji; random_state=reproducible
)
```

### 3.2 Praproses dengan `ColumnTransformer` (dari `train_model.py`)
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder

preprocessor = ColumnTransformer([
    # Target encoding untuk kolom kardinalitas tinggi (koridor)
    ("corridor", TargetEncoder(target_type="continuous"), ["corridorID"]),
    # One-hot untuk kategori kardinalitas rendah
    ("onehot", OneHotEncoder(handle_unknown="ignore"), ["corridor_type", "day_name"]),
    # Standarisasi untuk fitur numerik
    ("num", StandardScaler(), ["hour", "day_of_week", "is_weekend"]),
])
```
> **Penting (anti-kebocoran):** `target_type="continuous"` wajib karena target berupa cacah
> integer — mode `auto` bisa salah menganggapnya *multiclass*.

### 3.3 Pipeline — Menggabung Praproses + Model
```python
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

model = Pipeline([
    ("prep", preprocessor),
    ("model", XGBRegressor(objective="count:poisson", n_estimators=500,
                           learning_rate=0.05, max_depth=6, random_state=42)),
])
model.fit(X_train, y_train)          # latih seluruh pipeline sekaligus
y_pred = model.predict(X_test)       # prediksi
```
> `objective="count:poisson"` dipilih karena target **data cacah** (jumlah penumpang).

### 3.4 Model-Model yang Dibandingkan (dari `train_model.py`)
```python
from sklearn.dummy import DummyRegressor              # baseline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
```

### 3.5 Cross-Validation & Metrik
```python
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (mean_absolute_error, root_mean_squared_error,
                             r2_score, mean_absolute_percentage_error)

# CV: rata-rata skor pada 3 lipatan (lebih andal dari 1 kali tes)
cv_r2 = cross_val_score(model, X_train, y_train, cv=3, scoring="r2").mean()

# Metrik pada data uji
mae  = mean_absolute_error(y_test, y_pred)       # rata-rata galat absolut
rmse = root_mean_squared_error(y_test, y_pred)   # akar rata-rata galat kuadrat
r2   = r2_score(y_test, y_pred)                  # proporsi variasi terjelaskan (0..1)
```

### 3.6 Tuning Hyperparameter
```python
from sklearn.model_selection import RandomizedSearchCV

grid = {"model__n_estimators": [300, 500, 700], "model__max_depth": [4, 6, 8]}
search = RandomizedSearchCV(model, grid, n_iter=12, cv=3, scoring="r2", random_state=42)
search.fit(X_train, y_train)
print(search.best_params_, search.best_score_)
```

### 3.7 Menyimpan & Memuat Model
```python
import joblib

joblib.dump(model, "models/demand_model.pkl")   # simpan (latih offline)
model = joblib.load("models/demand_model.pkl")   # muat (dipakai app, cepat)
```
> **Konsep kunci:** model dilatih **offline** lalu disimpan; aplikasi hanya **memuat** artefak
> → ringan & cepat di cloud.

### 3.8 Feature Importance (interpretasi model)
```python
model.named_steps["model"].feature_importances_          # pentingnya tiap fitur
model.named_steps["prep"].get_feature_names_out()        # nama fitur setelah praproses
```

---

## 4. Streamlit — Aplikasi Web Data

> Streamlit mengubah skrip Python menjadi web app. **Skrip dijalankan ulang dari atas
> setiap kali ada interaksi** — itulah mengapa *caching* penting.

### 4.1 Konfigurasi & Menjalankan
```python
import streamlit as st

st.set_page_config(page_title="TransJakarta", page_icon="🚌",
                   layout="wide", initial_sidebar_state="expanded")
```
Jalankan: `streamlit run app.py`

### 4.2 Menampilkan Teks & Elemen
```python
st.title("Judul")           st.header("Header")      st.subheader("Sub")
st.markdown("**tebal**")     st.caption("teks kecil")  st.write(apa_saja)
st.metric("R²", "0.715")     st.dataframe(df)          st.table(df)
st.success("berhasil")       st.warning("peringatan")  st.info("info")
st.markdown(html, unsafe_allow_html=True)   # HTML/CSS kustom (kartu KPI)
```

### 4.3 Tata Letak (Layout)
```python
# Kolom berdampingan
c1, c2, c3 = st.columns(3)
c1.metric("MAE", "1.05")
c2.plotly_chart(fig)

# Tab
t1, t2 = st.tabs(["EDA", "Model"])
with t1:
    st.plotly_chart(fig)

# Sidebar & container
with st.sidebar:
    choice = st.radio("Navigasi", ["Beranda", "EDA"])
with st.container(border=True):
    st.markdown("Filter")

st.expander("Detail")        st.divider()
```

### 4.4 Widget Input (interaktivitas)
```python
koridor = st.selectbox("Koridor", daftar_koridor)      # dropdown
hari    = st.multiselect("Hari", opsi, default=opsi)   # pilih banyak
jam     = st.slider("Jam", 5, 21, 7)                   # penggeser
teks    = st.text_input("Nama")
tombol  = st.button("Prediksi")
st.download_button("Unduh CSV", data_csv, "file.csv")  # unduh file
```

### 4.5 Caching (KUNCI performa) — dari `app.py`
```python
@st.cache_data                # untuk DATA (DataFrame, dict, hasil komputasi)
def load_data():
    return pd.read_csv(...)   # dijalankan sekali, hasilnya disimpan

@st.cache_resource            # untuk RESOURCE (model, koneksi DB)
def load_model():
    return joblib.load("models/demand_model.pkl")
```
> `cache_data` mengembalikan **salinan** (aman diubah); `cache_resource` mengembalikan
> **objek yang sama** (untuk model/koneksi yang berat).

### 4.6 Menampilkan Grafik
```python
st.plotly_chart(fig, width="stretch")   # Plotly (interaktif) — dipakai di proyek ini
st.pyplot(fig)                           # Matplotlib
st.map(df_latlon)                        # peta cepat
```
> Catatan: `width="stretch"` menggantikan `use_container_width=True` yang sudah usang.

### 4.7 Navigasi Multi-Halaman (pola di `app.py`)
```python
PAGES = {
    "🏠 Beranda": page_home,
    "🔄 Analisis OD": page_od,
    "🎯 Simulasi Prediksi": page_simulation,
}
choice = st.sidebar.radio("Navigasi", list(PAGES.keys()))
PAGES[choice]()                          # panggil fungsi halaman terpilih
```

### 4.8 Tema (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#F26522"          # jingga (aksen)
backgroundColor = "#FFFFFF"        # putih
secondaryBackgroundColor = "#EAF2FB"
textColor = "#1B2A4A"
```

---

## 5. Arsitektur Folder Aplikasi

Proyek ini memisahkan **logika** (`src/`), **artefak** (`models/`, `reports/`), dan
**antarmuka** (`app.py`) — pola profesional agar mudah dipelihara & di-deploy.

```
bnsp-sertifikasi-data-science/
│
├── app.py                    # 🖥️ ENTRY POINT aplikasi Streamlit (9 halaman)
├── requirements.txt          # daftar dependensi (untuk deploy)
├── pyproject.toml            # metadata proyek (uv)
│
├── .streamlit/
│   └── config.toml           # 🎨 tema warna biru-putih-jingga
│
├── datasets/
│   └── dfTransjakarta180kRows.csv   # 📊 data mentah (189.500 baris)
│
├── src/                      # 🧠 LOGIKA INTI (modul reusable)
│   ├── config.py             #   ── path, konstanta, palet warna (satu sumber kebenaran)
│   ├── data_loader.py        #   ── muat CSV + tetapkan tipe data (Unit 3)
│   ├── preprocessing.py      #   ── validasi, pembersihan, seleksi (Unit 4–6)
│   ├── features.py           #   ── feature engineering & agregasi target (Unit 7)
│   ├── od_analysis.py        #   ── analisis Origin-Destination (bangkitan/tarikan)
│   ├── train_model.py        #   ── latih & bandingkan 7 model, simpan terbaik (Unit 8–10)
│   └── viz.py                #   ── fungsi grafik Plotly reusable
│
├── models/                   # 🤖 ARTEFAK MODEL (hasil train_model.py)
│   ├── demand_model.pkl      #   ── pipeline model terbaik (dimuat app)
│   └── metrics.json          #   ── metrik & metadata evaluasi
│
├── reports/                  # 📄 LAPORAN & HASIL
│   ├── model_comparison.csv  #   ── tabel perbandingan 7 model
│   ├── feature_importance.csv
│   ├── test_predictions.csv  #   ── prediksi vs aktual (untuk grafik evaluasi)
│   └── review_pemodelan.md   #   ── laporan review proses (Unit 11)
│
├── assets/                   # 🖼️ gambar grafik (PNG) untuk PPT
├── ppt/                      # 📽️ presentasi + generator + narasi
│   ├── TransJakarta_Demand_Prediction_BNSP.pptx
│   ├── build_deck.js         #   ── generator PPT (pptxgenjs/Node)
│   └── NARASI_PRESENTASI.md  #   ── naskah presentasi
│
├── CLAUDE.md                 # 📋 blueprint & pemetaan SKKNI
├── README.md                 # cara menjalankan
├── DEPLOYMENT.md             # panduan deploy ke Streamlit Cloud
└── PANDUAN_KODE.md           # 📘 dokumen ini
```

### 5.1 Alur Data Antar-Modul
```
datasets/*.csv
   │  data_loader.load_raw_data()        → DataFrame mentah (tipe benar)
   ▼
preprocessing.clean_data()               → DataFrame bersih + log (Unit 4–6)
   │
   ▼
features.build_demand_dataset()          → dataset agregasi (koridor×tgl×jam) (Unit 7)
   │
   ├──► train_model.py  → models/demand_model.pkl + reports/*.csv   (offline, sekali)
   │
   └──► app.py  ─ memuat data + model + artefak → tampilkan 9 halaman (online)
                 └─ viz.py & od_analysis.py dipanggil untuk grafik & analisis
```

### 5.2 Prinsip Desain (yang bisa Anda jelaskan ke asesor)
1. **Separation of concerns** — logika (`src/`) terpisah dari tampilan (`app.py`).
   Satu modul = satu tanggung jawab (data_loader hanya memuat, preprocessing hanya
   membersihkan, dst).
2. **Single source of truth** — semua path, konstanta, & warna terpusat di `config.py`;
   ubah sekali, berlaku di seluruh proyek.
3. **Reusable & DRY** (*Don't Repeat Yourself*) — fungsi grafik di `viz.py` dipakai
   berkali-kali oleh `app.py` maupun generator PPT.
4. **Train offline, serve online** — model dilatih sekali (`train_model.py`) lalu disimpan;
   aplikasi hanya **memuat** artefak → deploy ringan & cepat.
5. **Reproducible** — `random_state=42` konsisten; artefak & metrik tersimpan sehingga
   hasil dapat diulang.
6. **Caching** — `@st.cache_data` / `@st.cache_resource` mencegah komputasi berulang
   setiap interaksi.

---

> 💡 **Tips asesmen:** saat ditanya "jelaskan kode Anda", tunjukkan alur di §5.1 — dari data
> mentah, dibersihkan, direkayasa fiturnya, dilatih modelnya, hingga disajikan di aplikasi.
> Ini memperlihatkan Anda memahami **keseluruhan pipeline**, bukan sekadar potongan kode.
