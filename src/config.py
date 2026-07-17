"""Konfigurasi terpusat: path, konstanta domain, dan palet warna aplikasi.

Semua modul lain mengambil path & konstanta dari sini agar konsisten dan mudah
dipelihara (single source of truth).
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# PATH
# --------------------------------------------------------------------------- #
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "datasets"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
ASSETS_DIR = ROOT_DIR / "assets"

RAW_DATA_PATH = DATA_DIR / "dfTransjakarta180kRows.csv"
MODEL_PATH = MODELS_DIR / "demand_model.pkl"
METRICS_PATH = MODELS_DIR / "metrics.json"
MODEL_COMPARISON_PATH = REPORTS_DIR / "model_comparison.csv"
CLEANING_REPORT_PATH = REPORTS_DIR / "cleaning_report.json"

# Pastikan folder output tersedia
for _d in (MODELS_DIR, REPORTS_DIR, ASSETS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# METADATA APLIKASI  (silakan sesuaikan)
# --------------------------------------------------------------------------- #
APP_TITLE = "TransJakarta Demand Prediction"
APP_SUBTITLE = "Analisis Pola Penumpang & Prediksi Permintaan Transportasi Publik"
ASESI_NAME = "Mohammad Yusuf"
SCHEME_NAME = "Ilmuwan Data (Data Scientist) — DSS.01.00.23"
DATA_PERIOD = "1–30 April 2023"

# --------------------------------------------------------------------------- #
# KONSTANTA DOMAIN
# --------------------------------------------------------------------------- #
# Dataset merekam perjalanan pada April 2023 -> tahun acuan hitung usia.
REFERENCE_YEAR = 2023

# Jam sibuk (peak) berdasarkan temuan EDA: puncak pagi & sore.
MORNING_PEAK = range(6, 10)   # 06:00-09:59
EVENING_PEAK = range(16, 20)  # 16:00-19:59

# Batas usia yang dianggap masuk akal untuk validasi.
MIN_VALID_AGE = 5
MAX_VALID_AGE = 90

# Bounding box kasar wilayah layanan (Jabodetabek) untuk validasi koordinat.
LAT_BOUNDS = (-6.5, -5.9)
LON_BOUNDS = (106.5, 107.1)

# Nilai tarif yang valid pada sistem TransJakarta.
VALID_FARES = {0.0, 3500.0, 20000.0}

# Label placeholder untuk kategori yang hilang.
UNKNOWN_LABEL = "Unknown"

# --------------------------------------------------------------------------- #
# PALET WARNA APLIKASI  (Biru - Putih - Jingga)
# --------------------------------------------------------------------------- #
COLOR_BLUE = "#1E5AA8"        # Biru utama (brand)
COLOR_BLUE_DARK = "#1B2A4A"   # Biru tua (teks/heading)
COLOR_BLUE_LIGHT = "#EAF2FB"  # Biru muda (latar kartu)
COLOR_ORANGE = "#F26522"      # Jingga (aksen/CTA/highlight)
COLOR_ORANGE_LIGHT = "#FBE3D5"
COLOR_WHITE = "#FFFFFF"
COLOR_GRAY = "#6B7A99"

# Urutan warna kategori untuk grafik Plotly (konsisten di seluruh app).
CATEGORICAL_COLORS = [
    COLOR_BLUE,
    COLOR_ORANGE,
    "#4A90D9",
    "#F59E5B",
    COLOR_BLUE_DARK,
    COLOR_GRAY,
]

# Skala warna sekuensial (biru) untuk heatmap/peta kepadatan.
SEQUENTIAL_BLUES = [
    [0.0, "#EAF2FB"],
    [0.5, "#4A90D9"],
    [1.0, COLOR_BLUE_DARK],
]
