"""Konstruksi data & feature engineering (SKKNI Unit 7).

Membangun dataset pemodelan pada level agregasi **(koridor x tanggal x jam)**
dengan target ``passenger_count`` (jumlah tap-in). Ditambahkan fitur waktu &
koridor yang relevan untuk memprediksi demand.

Prinsip anti-kebocoran (leakage):
    * Fitur demografi per-slot (rata-rata usia, rasio gender) TIDAK dipakai
      sebagai prediktor, karena informasi tsb baru diketahui SETELAH penumpang
      tap -> merupakan bagian dari target itu sendiri.
    * "Demand historis koridor" tidak dihitung manual (rawan bocor), melainkan
      ditangani lewat ``TargetEncoder`` (cross-fitting) di pipeline training.
"""
from __future__ import annotations

import pandas as pd

from src import config

# --------------------------------------------------------------------------- #
# DEFINISI FITUR & TARGET  (dipakai bersama oleh training & app)
# --------------------------------------------------------------------------- #
TARGET = "passenger_count"

# Koridor: kardinalitas tinggi (~216) -> target encoding (cross-fitted).
TARGET_ENCODE_FEATURES = ["corridorID"]

# Kategorikal kardinalitas rendah -> one-hot encoding.
ONEHOT_FEATURES = ["corridor_type", "day_name", "part_of_day"]

# Numerik / biner -> passthrough (di-scale untuk model linier).
NUMERIC_FEATURES = ["hour", "day_of_week", "is_weekend", "is_peak", "week_of_month"]

ALL_FEATURES = TARGET_ENCODE_FEATURES + ONEHOT_FEATURES + NUMERIC_FEATURES

# Nama hari (urut) untuk tampilan konsisten.
DAY_NAMES = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


# --------------------------------------------------------------------------- #
# FITUR WAKTU
# --------------------------------------------------------------------------- #
def _part_of_day(hour: int) -> str:
    if hour < 6:
        return "Dini hari"
    if hour < 11:
        return "Pagi"
    if hour < 15:
        return "Siang"
    if hour < 19:
        return "Sore"
    return "Malam"


def _is_peak(hour: int) -> int:
    return int(hour in config.MORNING_PEAK or hour in config.EVENING_PEAK)


def add_time_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Tambahkan fitur waktu dari kolom ``date`` (datetime) dan ``hour`` (int)."""
    frame = frame.copy()
    dt = pd.to_datetime(frame["date"])
    frame["day_of_week"] = dt.dt.dayofweek                      # 0=Senin ... 6=Minggu
    frame["day_name"] = frame["day_of_week"].map(dict(enumerate(DAY_NAMES)))
    frame["is_weekend"] = (frame["day_of_week"] >= 5).astype(int)
    frame["week_of_month"] = ((dt.dt.day - 1) // 7 + 1).astype(int)
    frame["part_of_day"] = frame["hour"].map(_part_of_day)
    frame["is_peak"] = frame["hour"].map(_is_peak).astype(int)
    return frame


# --------------------------------------------------------------------------- #
# AGREGASI -> DATASET PEMODELAN
# --------------------------------------------------------------------------- #
def build_demand_dataset(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Agregasi transaksi bersih -> dataset demand per (koridor x tanggal x jam).

    Parameters
    ----------
    df_clean : DataFrame
        Output ``preprocessing.clean_data`` (punya kolom ``corridor_type``).

    Returns
    -------
    DataFrame
        Satu baris = satu slot koridor-jam-tanggal yang aktif (demand >= 1),
        berisi ``passenger_count`` (target) + seluruh fitur di ``ALL_FEATURES``.
    """
    df = df_clean.copy()
    df["date"] = df["tapInTime"].dt.normalize()
    df["hour"] = df["tapInTime"].dt.hour

    # corridor_type konstan per koridor -> ambil nilai pertama tiap grup.
    grouped = (
        df.groupby(["corridorID", "date", "hour"], observed=True)
        .agg(
            passenger_count=("transID", "size"),
            corridor_type=("corridor_type", "first"),
        )
        .reset_index()
    )

    modeling = add_time_features(grouped)

    # Susun urutan kolom: identitas -> fitur -> target (tanpa duplikasi).
    ordered = ["corridorID", "corridor_type", "date"] + ALL_FEATURES + [TARGET]
    seen: set[str] = set()
    unique_cols = [
        c for c in ordered if c in modeling.columns and not (c in seen or seen.add(c))
    ]
    modeling = modeling[unique_cols]
    return modeling


def feature_target_split(modeling: pd.DataFrame):
    """Pisahkan matriks fitur X dan target y untuk training."""
    x = modeling[ALL_FEATURES].copy()
    y = modeling[TARGET].copy()
    return x, y


def make_prediction_row(
    corridor_id: str,
    corridor_type: str,
    day_of_week: int,
    hour: int,
    week_of_month: int = 3,
) -> pd.DataFrame:
    """Bangun 1 baris fitur (sesuai ``ALL_FEATURES``) dari input pengguna.

    Dipakai halaman "Simulasi Prediksi" di aplikasi Streamlit.
    """
    row = {
        "corridorID": corridor_id,
        "corridor_type": corridor_type,
        "day_name": DAY_NAMES[day_of_week],
        "part_of_day": _part_of_day(hour),
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": int(day_of_week >= 5),
        "is_peak": _is_peak(hour),
        "week_of_month": week_of_month,
    }
    return pd.DataFrame([row])[ALL_FEATURES]
