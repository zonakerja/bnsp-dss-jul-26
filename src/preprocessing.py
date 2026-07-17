"""Validasi, seleksi, dan pembersihan data (SKKNI Unit 4, 5, 6).

Alur:
    validate_data(df)  -> laporan validasi & kelengkapan (Unit 4)
    clean_data(df)     -> (df_bersih, log_pembersihan)  (Unit 6)

Fungsi menambah kolom turunan ringan yang dibutuhkan EDA & pemodelan
(``age``, ``is_incomplete``, ``travel_min``, ``corridor_type``) tanpa membuang
informasi mentah.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src import config


# --------------------------------------------------------------------------- #
# VALIDASI DATA (Unit 4 - Memvalidasi Data)
# --------------------------------------------------------------------------- #
def missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """Tabel jumlah & persentase missing per kolom (urut terbanyak)."""
    n = len(df)
    rep = pd.DataFrame(
        {
            "kolom": df.columns,
            "jumlah_missing": df.isna().sum().values,
            "persen_missing": (df.isna().sum().values / n * 100).round(2),
        }
    )
    return rep.sort_values("jumlah_missing", ascending=False).reset_index(drop=True)


def validate_data(df: pd.DataFrame) -> dict[str, Any]:
    """Jalankan pemeriksaan kualitas & kelengkapan data.

    Mengembalikan dict berisi hasil setiap pemeriksaan agar bisa ditampilkan
    di aplikasi (halaman "Kualitas Data") sekaligus menjadi bukti Unit 4.
    """
    n = len(df)
    report: dict[str, Any] = {"n_baris": int(n), "n_kolom": int(df.shape[1])}

    # 1) Kelengkapan
    report["missing_per_kolom"] = (
        df.isna().sum().sort_values(ascending=False).astype(int).to_dict()
    )
    report["persen_baris_lengkap"] = round(
        float(df.dropna().shape[0]) / n * 100, 2
    )

    # 2) Duplikasi transaksi
    report["duplikat_transID"] = int(df.duplicated(subset=["transID"]).sum())

    # 3) Validitas tarif
    if "payAmount" in df.columns:
        fare_valid = df["payAmount"].dropna().isin(config.VALID_FARES)
        report["tarif_tidak_valid"] = int((~fare_valid).sum())

    # 4) Konsistensi waktu: tapOut harus >= tapIn
    if {"tapInTime", "tapOutTime"}.issubset(df.columns):
        both = df.dropna(subset=["tapInTime", "tapOutTime"])
        report["tapout_sebelum_tapin"] = int(
            (both["tapOutTime"] < both["tapInTime"]).sum()
        )

    # 5) Koordinat di luar bounding box wilayah layanan
    lat_lo, lat_hi = config.LAT_BOUNDS
    lon_lo, lon_hi = config.LON_BOUNDS
    if {"tapInStopsLat", "tapInStopsLon"}.issubset(df.columns):
        lat = df["tapInStopsLat"]
        lon = df["tapInStopsLon"]
        out = (~lat.between(lat_lo, lat_hi)) | (~lon.between(lon_lo, lon_hi))
        report["koordinat_diluar_wilayah"] = int(out.fillna(False).sum())

    # 6) Tahun lahir tidak masuk akal
    if "payCardBirthDate" in df.columns:
        yr = df["payCardBirthDate"]
        age = config.REFERENCE_YEAR - yr
        implausible = (age < config.MIN_VALID_AGE) | (age > config.MAX_VALID_AGE)
        report["usia_tidak_masuk_akal"] = int(implausible.fillna(False).sum())

    # 7) Perjalanan tak lengkap (tanpa tap-out)
    if "tapOutTime" in df.columns:
        report["perjalanan_tak_lengkap"] = int(df["tapOutTime"].isna().sum())

    return report


def completeness_recommendation(report: dict[str, Any]) -> list[str]:
    """Rekomendasi hasil penilaian kualitas & kecukupan data (Unit 4 - Elemen 2)."""
    recs: list[str] = []
    inc = report.get("perjalanan_tak_lengkap", 0)
    n = report.get("n_baris", 1)
    if inc:
        recs.append(
            f"{inc:,} perjalanan ({inc / n * 100:.1f}%) tidak memiliki tap-out. "
            "Untuk pemodelan demand (berbasis tap-in) baris ini tetap dipakai; "
            "untuk analisis Origin-Destination baris dipisahkan/dilabeli 'tak lengkap'."
        )
    miss = report.get("missing_per_kolom", {})
    if miss.get("corridorName", 0) or miss.get("corridorID", 0):
        recs.append(
            "Sebagian koridor kosong -> diisi label 'Unknown' agar tetap dapat "
            "diagregasi, dampaknya dievaluasi pada laporan pembersihan."
        )
    recs.append(
        "Data mencakup 1 bulan (April 2023): cukup untuk menangkap pola harian & "
        "mingguan, namun belum menangkap musiman tahunan/hari libur nasional."
    )
    if not report.get("duplikat_transID", 0):
        recs.append("Tidak ada duplikasi transID -> integritas transaksi terjaga.")
    return recs


# --------------------------------------------------------------------------- #
# KOLOM TURUNAN RINGAN
# --------------------------------------------------------------------------- #
def _corridor_type(corridor_id: str) -> str:
    """Petakan prefiks ID koridor -> jenis layanan."""
    if not isinstance(corridor_id, str) or corridor_id == config.UNKNOWN_LABEL:
        return config.UNKNOWN_LABEL
    if corridor_id.upper().startswith("JAK"):
        return "Mikrotrans (JAK)"
    # Koridor angka murni = BRT koridor utama; sisanya = layanan lain/pengumpan.
    if corridor_id[0].isdigit():
        return "BRT Koridor"
    return "Non-BRT / Pengumpan"


def _haversine_km(lat1, lon1, lat2, lon2):
    """Jarak lingkaran besar (km) antar dua titik koordinat (vektorisasi)."""
    r = 6371.0
    p = np.pi / 180.0
    a = (
        0.5
        - np.cos((lat2 - lat1) * p) / 2
        + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    )
    return 2 * r * np.arcsin(np.sqrt(a))


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Tambah kolom turunan ringan yang berguna untuk EDA & pemodelan."""
    df = df.copy()

    # Usia penumpang.
    if "payCardBirthDate" in df.columns:
        df["age"] = (config.REFERENCE_YEAR - df["payCardBirthDate"]).astype("Float64")

    # Penanda perjalanan tak lengkap.
    if "tapOutTime" in df.columns:
        df["is_incomplete"] = df["tapOutTime"].isna()

    # Durasi perjalanan (menit) - hanya untuk EDA, BUKAN target model.
    if {"tapInTime", "tapOutTime"}.issubset(df.columns):
        df["travel_min"] = (
            df["tapOutTime"] - df["tapInTime"]
        ).dt.total_seconds() / 60.0

    # Jenis koridor.
    if "corridorID" in df.columns:
        df["corridor_type"] = (
            df["corridorID"].astype("object").map(_corridor_type)
        )

    # Jarak tap-in -> tap-out (km) untuk EDA geospasial.
    coord_cols = {"tapInStopsLat", "tapInStopsLon", "tapOutStopsLat", "tapOutStopsLon"}
    if coord_cols.issubset(df.columns):
        df["distance_km"] = _haversine_km(
            df["tapInStopsLat"],
            df["tapInStopsLon"],
            df["tapOutStopsLat"],
            df["tapOutStopsLon"],
        )

    return df


# --------------------------------------------------------------------------- #
# PEMBERSIHAN DATA (Unit 6 - Membersihkan Data)
# --------------------------------------------------------------------------- #
def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Bersihkan data sesuai strategi dan hasilkan log before/after.

    Strategi (didokumentasikan sbg bukti Unit 6):
      1. Buang duplikasi transID (integritas transaksi).
      2. Buang baris tanpa ``tapInTime`` valid (tak bisa diagregasi ke jam).
      3. Isi koridor kosong dengan label 'Unknown'.
      4. Tandai & koreksi usia tidak masuk akal -> NaN (tidak dibuang barisnya).
      5. Tandai perjalanan tak lengkap (kolom ``is_incomplete``).

    Returns
    -------
    (df_bersih, log)  di mana log = list langkah dengan jumlah baris sebelum/sesudah.
    """
    log: list[dict[str, Any]] = []

    def _record(step: str, desc: str, before: int, after: int, note: str = "") -> None:
        log.append(
            {
                "langkah": step,
                "deskripsi": desc,
                "baris_sebelum": int(before),
                "baris_sesudah": int(after),
                "baris_terdampak": int(before - after),
                "catatan": note,
            }
        )

    df = add_derived_columns(df)
    n0 = len(df)

    # 1) Duplikasi transID
    before = len(df)
    df = df.drop_duplicates(subset=["transID"])
    _record(
        "hapus_duplikat", "Buang duplikasi transID", before, len(df),
        "Menjaga satu baris per transaksi.",
    )

    # 2) Baris tanpa tapInTime valid
    before = len(df)
    df = df[df["tapInTime"].notna()]
    _record(
        "buang_tapin_kosong",
        "Buang baris tanpa waktu tap-in valid",
        before,
        len(df),
        "tapInTime wajib untuk agregasi demand per jam.",
    )

    # 3) Isi koridor kosong -> 'Unknown'
    filled = 0
    for col in ("corridorID", "corridorName"):
        if col in df.columns:
            n_missing = int(df[col].isna().sum())
            filled += n_missing
            if isinstance(df[col].dtype, pd.CategoricalDtype):
                if config.UNKNOWN_LABEL not in df[col].cat.categories:
                    df[col] = df[col].cat.add_categories([config.UNKNOWN_LABEL])
            df[col] = df[col].fillna(config.UNKNOWN_LABEL)
    _record(
        "isi_koridor_unknown",
        "Isi koridor kosong dengan label 'Unknown'",
        len(df),
        len(df),
        f"{filled:,} sel koridor kosong diisi (baris dipertahankan).",
    )

    # 4) Koreksi usia tidak masuk akal -> NaN
    if "age" in df.columns:
        implausible = (df["age"] < config.MIN_VALID_AGE) | (
            df["age"] > config.MAX_VALID_AGE
        )
        n_bad = int(implausible.fillna(False).sum())
        df.loc[implausible.fillna(False), "age"] = np.nan
        _record(
            "koreksi_usia",
            "Set usia di luar rentang wajar menjadi NaN",
            len(df),
            len(df),
            f"{n_bad:,} nilai usia dikoreksi (di luar {config.MIN_VALID_AGE}-{config.MAX_VALID_AGE} th).",
        )

    # 5) Ringkasan penanda perjalanan tak lengkap
    if "is_incomplete" in df.columns:
        n_inc = int(df["is_incomplete"].sum())
        _record(
            "tandai_tak_lengkap",
            "Tandai perjalanan tanpa tap-out",
            len(df),
            len(df),
            f"{n_inc:,} perjalanan ditandai 'is_incomplete' (dipertahankan).",
        )

    # Ringkasan total
    _record(
        "TOTAL",
        "Ringkasan akhir pembersihan",
        n0,
        len(df),
        f"{n0 - len(df):,} baris dibuang dari {n0:,} baris awal.",
    )

    df = df.reset_index(drop=True)
    return df, log
