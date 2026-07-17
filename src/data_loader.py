"""Pemuatan data mentah TransJakarta dengan penetapan tipe data yang benar.

Modul ini dipakai bersama oleh skrip training maupun aplikasi Streamlit.
Fungsi utama:
    load_raw_data()  -> DataFrame mentah dengan tipe terparsing
    dataset_overview() -> ringkasan struktur dataset (untuk halaman "Telaah Data")
"""
from __future__ import annotations

import pandas as pd

from src import config

# Kolom waktu yang harus diparsing menjadi datetime.
_DATETIME_COLS = ["tapInTime", "tapOutTime"]

# Kolom yang bertipe kategorikal (menghemat memori & memperjelas semantik).
_CATEGORICAL_COLS = [
    "payCardBank",
    "payCardSex",
    "corridorID",
    "corridorName",
]


def load_raw_data(path=None) -> pd.DataFrame:
    """Muat CSV mentah dan tetapkan tipe data yang tepat.

    Parameters
    ----------
    path : str | Path | None
        Lokasi file CSV. Default: ``config.RAW_DATA_PATH``.

    Returns
    -------
    pandas.DataFrame
        Data mentah (belum dibersihkan) dengan kolom waktu ber-tipe datetime
        dan kolom kategori ber-tipe ``category``.
    """
    path = path or config.RAW_DATA_PATH
    df = pd.read_csv(path)

    # Parsing kolom waktu -> datetime (nilai kosong tetap NaT).
    for col in _DATETIME_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Tahun lahir sebagai integer nullable (ada baris tanpa nilai valid).
    if "payCardBirthDate" in df.columns:
        df["payCardBirthDate"] = pd.to_numeric(
            df["payCardBirthDate"], errors="coerce"
        ).astype("Int64")

    # Kolom kategorikal.
    for col in _CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def dataset_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Bangun tabel ringkasan per-kolom untuk telaah data (Unit 3 SKKNI).

    Berisi tipe data, jumlah & persentase missing, dan jumlah nilai unik.
    """
    n = len(df)
    overview = pd.DataFrame(
        {
            "kolom": df.columns,
            "tipe_data": [str(t) for t in df.dtypes],
            "jumlah_missing": df.isna().sum().values,
            "persen_missing": (df.isna().sum().values / n * 100).round(2),
            "nilai_unik": df.nunique(dropna=True).values,
        }
    ).reset_index(drop=True)
    return overview


def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Statistik deskriptif dasar untuk kolom numerik (Unit 3 - Elemen 2)."""
    return df.describe(include="number").T
