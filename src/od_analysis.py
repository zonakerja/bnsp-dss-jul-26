"""Analisis Origin-Destination (OD) — perspektif perencanaan transportasi.

Konsep:
    * Bangkitan / Produksi (Trip Production)  = jumlah perjalanan yang BERANGKAT
      dari suatu halte (dihitung dari tap-in per halte asal).
    * Tarikan / Atraksi (Trip Attraction)     = jumlah perjalanan yang MENUJU
      suatu halte (dihitung dari tap-out per halte tujuan).
    * Net flow  = Produksi − Tarikan (positif = halte penghasil perjalanan,
      negatif = halte penarik perjalanan).
    * Matriks OD = jumlah perjalanan dari halte asal i ke halte tujuan j.
    * Desire lines = garis keinginan perjalanan (pasangan OD tersibuk).

Hanya perjalanan lengkap (punya tap-in DAN tap-out valid) yang dipakai.
"""
from __future__ import annotations

import pandas as pd

_OD_COLS = [
    "tapInStopsName", "tapInStopsLat", "tapInStopsLon",
    "tapOutStopsName", "tapOutStopsLat", "tapOutStopsLon",
]


def complete_od_trips(df: pd.DataFrame) -> pd.DataFrame:
    """Ambil perjalanan lengkap dengan asal & tujuan valid (asal ≠ tujuan)."""
    d = df.dropna(subset=_OD_COLS).copy()
    d = d[d["tapInStopsName"] != d["tapOutStopsName"]]
    return d


def production_by_stop(od: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Bangkitan (produksi) per halte asal — n halte teratas."""
    g = (
        od.groupby(["tapInStopsName", "tapInStopsLat", "tapInStopsLon"])
        .size()
        .reset_index(name="produksi")
        .rename(columns={"tapInStopsName": "halte", "tapInStopsLat": "lat", "tapInStopsLon": "lon"})
    )
    return g.sort_values("produksi", ascending=False).head(n).reset_index(drop=True)


def attraction_by_stop(od: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Tarikan (atraksi) per halte tujuan — n halte teratas."""
    g = (
        od.groupby(["tapOutStopsName", "tapOutStopsLat", "tapOutStopsLon"])
        .size()
        .reset_index(name="tarikan")
        .rename(columns={"tapOutStopsName": "halte", "tapOutStopsLat": "lat", "tapOutStopsLon": "lon"})
    )
    return g.sort_values("tarikan", ascending=False).head(n).reset_index(drop=True)


def net_flow(od: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """Net flow (produksi − tarikan) per halte; n halte dengan |net| terbesar."""
    prod = od.groupby("tapInStopsName").size().rename("produksi")
    attr = od.groupby("tapOutStopsName").size().rename("tarikan")
    m = pd.concat([prod, attr], axis=1).fillna(0)
    m["net"] = m["produksi"] - m["tarikan"]
    m["total"] = m["produksi"] + m["tarikan"]
    m = m.reset_index(names="halte")
    top = m.reindex(m["net"].abs().sort_values(ascending=False).index).head(n)
    return top.sort_values("net").reset_index(drop=True)


def od_matrix(od: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Matriks OD untuk top_n halte asal × top_n halte tujuan tersibuk."""
    top_o = od["tapInStopsName"].value_counts().head(top_n).index
    top_d = od["tapOutStopsName"].value_counts().head(top_n).index
    sub = od[od["tapInStopsName"].isin(top_o) & od["tapOutStopsName"].isin(top_d)]
    mat = pd.crosstab(sub["tapInStopsName"], sub["tapOutStopsName"])
    return mat


def desire_lines(od: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    """Pasangan OD (asal→tujuan) tersibuk untuk digambar sebagai desire lines."""
    g = (
        od.groupby(_OD_COLS)
        .size()
        .reset_index(name="trips")
        .sort_values("trips", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return g
