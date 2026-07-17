"""Fungsi visualisasi Plotly reusable dengan tema Biru-Putih-Jingga.

Dipakai oleh aplikasi Streamlit. Setiap fungsi mengembalikan objek
``plotly.graph_objects.Figure`` yang siap ditampilkan via ``st.plotly_chart``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src import config, features

# --------------------------------------------------------------------------- #
# TEMA
# --------------------------------------------------------------------------- #
def _apply_theme(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Terapkan gaya konsisten (font, warna, latar) ke figure."""
    fig.update_layout(
        title=title,
        template="plotly_white",
        font=dict(family="Segoe UI, sans-serif", color=config.COLOR_BLUE_DARK, size=13),
        title_font=dict(size=18, color=config.COLOR_BLUE_DARK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50 if title else 20, b=10),
        colorway=config.CATEGORICAL_COLORS,
        hoverlabel=dict(bgcolor="white", font_size=12),
        legend=dict(bgcolor="rgba(255,255,255,0.6)"),
    )
    fig.update_xaxes(gridcolor="#E6ECF5", zeroline=False)
    fig.update_yaxes(gridcolor="#E6ECF5", zeroline=False)
    return fig


# --------------------------------------------------------------------------- #
# EDA — POLA WAKTU
# --------------------------------------------------------------------------- #
def hourly_demand(df: pd.DataFrame) -> go.Figure:
    """Jumlah penumpang per jam (menyoroti puncak pagi & sore)."""
    counts = df["tapInTime"].dt.hour.value_counts().sort_index()
    colors = [
        config.COLOR_ORANGE if features._is_peak(h) else config.COLOR_BLUE
        for h in counts.index
    ]
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=colors,
            hovertemplate="Jam %{x}:00<br>%{y:,} penumpang<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Jam", yaxis_title="Jumlah Tap-in")
    fig.update_xaxes(dtick=1)
    return _apply_theme(fig, "Pola Permintaan per Jam (jingga = jam sibuk)")


def weekday_weekend(df: pd.DataFrame) -> go.Figure:
    """Rata-rata jumlah penumpang: hari kerja vs akhir pekan."""
    dow = df["tapInTime"].dt.dayofweek
    per_day = df.assign(_dow=dow, _date=df["tapInTime"].dt.date)
    grp = per_day.groupby("_dow").size()
    n_days = per_day.groupby("_dow")["_date"].nunique()
    avg = (grp / n_days).reindex(range(7))
    colors = [
        config.COLOR_ORANGE if d >= 5 else config.COLOR_BLUE for d in range(7)
    ]
    fig = go.Figure(
        go.Bar(
            x=features.DAY_NAMES,
            y=avg.values,
            marker_color=colors,
            hovertemplate="%{x}<br>rata-rata %{y:,.0f} penumpang/hari<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Hari", yaxis_title="Rata-rata Tap-in / Hari")
    return _apply_theme(fig, "Hari Kerja vs Akhir Pekan (jingga = akhir pekan)")


def demand_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap kepadatan penumpang: jam (x) vs hari (y)."""
    tmp = df.assign(hour=df["tapInTime"].dt.hour, dow=df["tapInTime"].dt.dayofweek)
    pivot = (
        tmp.groupby(["dow", "hour"]).size().reset_index(name="n")
        .pivot(index="dow", columns="hour", values="n")
        .reindex(range(7))
    )
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=features.DAY_NAMES,
            colorscale=config.SEQUENTIAL_BLUES,
            hovertemplate="Hari %{y}, Jam %{x}:00<br>%{z:,} penumpang<extra></extra>",
            colorbar=dict(title="Penumpang"),
        )
    )
    fig.update_layout(xaxis_title="Jam", yaxis_title="Hari")
    fig.update_xaxes(dtick=1)
    return _apply_theme(fig, "Heatmap Kepadatan: Jam x Hari")


# --------------------------------------------------------------------------- #
# EDA — KORIDOR & DEMOGRAFI
# --------------------------------------------------------------------------- #
def top_corridors(df: pd.DataFrame, n: int = 12) -> go.Figure:
    """Koridor tersibuk (horizontal bar)."""
    top = (
        df[df["corridorName"] != config.UNKNOWN_LABEL]["corridorName"]
        .value_counts()
        .head(n)
        .sort_values()
    )
    fig = go.Figure(
        go.Bar(
            x=top.values,
            y=top.index,
            orientation="h",
            marker_color=config.COLOR_BLUE,
            hovertemplate="%{y}<br>%{x:,} penumpang<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Jumlah Penumpang", yaxis_title=None, height=420)
    return _apply_theme(fig, f"{n} Koridor Tersibuk")


def corridor_type_share(df: pd.DataFrame) -> go.Figure:
    """Komposisi jenis koridor (donut)."""
    share = df["corridor_type"].value_counts()
    fig = go.Figure(
        go.Pie(
            labels=share.index,
            values=share.values,
            hole=0.55,
            marker=dict(colors=config.CATEGORICAL_COLORS),
            hovertemplate="%{label}<br>%{value:,} (%{percent})<extra></extra>",
        )
    )
    return _apply_theme(fig, "Komposisi Jenis Layanan")


def age_distribution(df: pd.DataFrame) -> go.Figure:
    """Distribusi usia penumpang."""
    ages = df["age"].dropna()
    fig = go.Figure(
        go.Histogram(
            x=ages,
            nbinsx=30,
            marker_color=config.COLOR_BLUE,
            hovertemplate="Usia %{x}<br>%{y:,} penumpang<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Usia (tahun)", yaxis_title="Jumlah Penumpang", bargap=0.05)
    return _apply_theme(fig, "Distribusi Usia Penumpang")


def gender_share(df: pd.DataFrame) -> go.Figure:
    """Proporsi gender penumpang (donut)."""
    mapping = {"F": "Perempuan", "M": "Laki-laki"}
    s = df["payCardSex"].map(mapping).value_counts()
    fig = go.Figure(
        go.Pie(
            labels=s.index,
            values=s.values,
            hole=0.55,
            marker=dict(colors=[config.COLOR_ORANGE, config.COLOR_BLUE]),
            hovertemplate="%{label}<br>%{value:,} (%{percent})<extra></extra>",
        )
    )
    return _apply_theme(fig, "Proporsi Gender")


def bank_share(df: pd.DataFrame) -> go.Figure:
    """Distribusi bank penerbit kartu."""
    s = df["payCardBank"].value_counts().sort_values()
    fig = go.Figure(
        go.Bar(
            x=s.values,
            y=s.index,
            orientation="h",
            marker_color=config.COLOR_BLUE,
            hovertemplate="%{y}<br>%{x:,} transaksi<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Jumlah Transaksi", yaxis_title=None)
    return _apply_theme(fig, "Bank Penerbit Kartu")


def fare_distribution(df: pd.DataFrame) -> go.Figure:
    """Distribusi tarif per jenis koridor (stacked bar)."""
    tmp = df.dropna(subset=["payAmount"]).copy()
    tmp["tarif"] = tmp["payAmount"].map(
        {0.0: "Gratis (Rp0)", 3500.0: "BRT (Rp3.500)", 20000.0: "Premium (Rp20.000)"}
    )
    grp = tmp.groupby(["corridor_type", "tarif"]).size().reset_index(name="n")
    fig = px.bar(
        grp,
        x="corridor_type",
        y="n",
        color="tarif",
        color_discrete_sequence=config.CATEGORICAL_COLORS,
    )
    fig.update_layout(xaxis_title="Jenis Koridor", yaxis_title="Jumlah Transaksi", legend_title="Tarif")
    fig.update_traces(hovertemplate="%{x}<br>%{y:,} transaksi<extra></extra>")
    return _apply_theme(fig, "Struktur Tarif per Jenis Layanan")


# --------------------------------------------------------------------------- #
# GEOSPASIAL
# --------------------------------------------------------------------------- #
def stops_map(df: pd.DataFrame, top_n: int = 400) -> go.Figure:
    """Peta halte tap-in berdasarkan kepadatan penumpang (scatter mapbox)."""
    agg = (
        df.groupby(["tapInStopsName", "tapInStopsLat", "tapInStopsLon"])
        .size()
        .reset_index(name="penumpang")
        .sort_values("penumpang", ascending=False)
        .head(top_n)
    )
    fig = px.scatter_mapbox(
        agg,
        lat="tapInStopsLat",
        lon="tapInStopsLon",
        size="penumpang",
        color="penumpang",
        color_continuous_scale=["#4A90D9", config.COLOR_BLUE_DARK, config.COLOR_ORANGE],
        size_max=22,
        zoom=10,
        hover_name="tapInStopsName",
        hover_data={"tapInStopsLat": False, "tapInStopsLon": False, "penumpang": ":,"},
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=10, b=0),
        height=560,
        coloraxis_colorbar=dict(title="Penumpang"),
    )
    return fig


# --------------------------------------------------------------------------- #
# ANALISIS ORIGIN-DESTINATION (OD)
# --------------------------------------------------------------------------- #
def production_bars(prod_df: pd.DataFrame) -> go.Figure:
    """Bangkitan (produksi) per halte asal."""
    d = prod_df.sort_values("produksi")
    fig = go.Figure(
        go.Bar(
            x=d["produksi"], y=d["halte"], orientation="h",
            marker_color=config.COLOR_BLUE,
            hovertemplate="%{y}<br>Bangkitan %{x:,} perjalanan<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Bangkitan (perjalanan berangkat)", yaxis_title=None, height=420)
    return _apply_theme(fig, "🔵 Bangkitan Tertinggi (Halte Asal)")


def attraction_bars(attr_df: pd.DataFrame) -> go.Figure:
    """Tarikan (atraksi) per halte tujuan."""
    d = attr_df.sort_values("tarikan")
    fig = go.Figure(
        go.Bar(
            x=d["tarikan"], y=d["halte"], orientation="h",
            marker_color=config.COLOR_ORANGE,
            hovertemplate="%{y}<br>Tarikan %{x:,} perjalanan<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Tarikan (perjalanan menuju)", yaxis_title=None, height=420)
    return _apply_theme(fig, "🟠 Tarikan Tertinggi (Halte Tujuan)")


def net_flow_diverging(net_df: pd.DataFrame) -> go.Figure:
    """Diverging bar net flow: halte penghasil (biru) vs penarik (jingga) perjalanan."""
    d = net_df.copy()
    colors = [config.COLOR_BLUE if v >= 0 else config.COLOR_ORANGE for v in d["net"]]
    fig = go.Figure(
        go.Bar(
            x=d["net"], y=d["halte"], orientation="h", marker_color=colors,
            hovertemplate="%{y}<br>Net %{x:,} (produksi−tarikan)<extra></extra>",
        )
    )
    fig.add_vline(x=0, line=dict(color=config.COLOR_GRAY, width=1))
    fig.update_layout(xaxis_title="Net Flow  (◄ penarik   |   penghasil ►)", yaxis_title=None, height=440)
    return _apply_theme(fig, "Keseimbangan Halte: Penghasil vs Penarik Perjalanan")


def od_heatmap(mat: pd.DataFrame) -> go.Figure:
    """Heatmap matriks OD (asal × tujuan)."""
    fig = go.Figure(
        go.Heatmap(
            z=mat.values, x=list(mat.columns), y=list(mat.index),
            colorscale=config.SEQUENTIAL_BLUES,
            hovertemplate="Asal: %{y}<br>Tujuan: %{x}<br>%{z:,} perjalanan<extra></extra>",
            colorbar=dict(title="Perjalanan"),
        )
    )
    fig.update_layout(xaxis_title="Halte Tujuan", yaxis_title="Halte Asal", height=560,
                      xaxis=dict(tickangle=-40))
    return _apply_theme(fig, "Matriks Origin-Destination (Halte Tersibuk)")


def desire_lines_map(lines_df: pd.DataFrame) -> go.Figure:
    """Peta desire lines: garis keinginan perjalanan asal→tujuan tersibuk."""
    maxt = float(lines_df["trips"].max()) if len(lines_df) else 1.0
    fig = go.Figure()
    for _, r in lines_df.iterrows():
        fig.add_trace(
            go.Scattermapbox(
                lat=[r["tapInStopsLat"], r["tapOutStopsLat"]],
                lon=[r["tapInStopsLon"], r["tapOutStopsLon"]],
                mode="lines",
                line=dict(width=1.2 + 5.5 * r["trips"] / maxt, color=config.COLOR_ORANGE),
                opacity=0.45, hoverinfo="skip", showlegend=False,
            )
        )
    fig.add_trace(
        go.Scattermapbox(
            lat=lines_df["tapInStopsLat"], lon=lines_df["tapInStopsLon"], mode="markers",
            marker=dict(size=9, color=config.COLOR_BLUE), name="Asal",
            text=lines_df["tapInStopsName"], hovertemplate="Asal: %{text}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scattermapbox(
            lat=lines_df["tapOutStopsLat"], lon=lines_df["tapOutStopsLon"], mode="markers",
            marker=dict(size=9, color=config.COLOR_BLUE_DARK), name="Tujuan",
            text=lines_df["tapOutStopsName"], hovertemplate="Tujuan: %{text}<extra></extra>",
        )
    )
    clat = float(pd.concat([lines_df["tapInStopsLat"], lines_df["tapOutStopsLat"]]).mean())
    clon = float(pd.concat([lines_df["tapInStopsLon"], lines_df["tapOutStopsLon"]]).mean())
    fig.update_layout(
        mapbox_style="open-street-map", mapbox_zoom=10.2,
        mapbox_center={"lat": clat, "lon": clon},
        margin=dict(l=0, r=0, t=10, b=0), height=560,
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"),
    )
    return fig


# --------------------------------------------------------------------------- #
# PEMODELAN & EVALUASI
# --------------------------------------------------------------------------- #
def model_comparison(comp: pd.DataFrame) -> go.Figure:
    """Bar perbandingan R2 antar model."""
    d = comp.sort_values("test_R2")
    colors = [
        config.COLOR_ORANGE if i == len(d) - 1 else config.COLOR_BLUE
        for i in range(len(d))
    ]
    fig = go.Figure(
        go.Bar(
            x=d["test_R2"],
            y=d["model"],
            orientation="h",
            marker_color=colors,
            text=d["test_R2"].round(3),
            textposition="outside",
            hovertemplate="%{y}<br>Test R2 = %{x:.3f}<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Test R2", yaxis_title=None, xaxis_range=[0, 1])
    return _apply_theme(fig, "Perbandingan Model (jingga = terbaik)")


def feature_importance(fi: pd.DataFrame, n: int = 12) -> go.Figure:
    """Bar pentingnya fitur model terbaik."""
    top = fi.head(n).sort_values("importance")
    fig = go.Figure(
        go.Bar(
            x=top["importance"],
            y=top["fitur"],
            orientation="h",
            marker_color=config.COLOR_BLUE,
            hovertemplate="%{y}<br>importance = %{x:.3f}<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Importance", yaxis_title=None, height=420)
    return _apply_theme(fig, f"{n} Fitur Paling Berpengaruh")


def pred_vs_actual(pred_df: pd.DataFrame, sample: int = 3000) -> go.Figure:
    """Scatter prediksi vs aktual dengan garis ideal."""
    d = pred_df.sample(min(sample, len(pred_df)), random_state=42)
    hi = float(max(d["actual"].max(), d["predicted"].max()))
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=d["actual"],
            y=d["predicted"],
            mode="markers",
            marker=dict(color=config.COLOR_BLUE, size=5, opacity=0.35),
            hovertemplate="aktual %{x}<br>prediksi %{y:.1f}<extra></extra>",
            name="Slot",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, hi],
            y=[0, hi],
            mode="lines",
            line=dict(color=config.COLOR_ORANGE, dash="dash"),
            name="Prediksi = Aktual",
        )
    )
    fig.update_layout(xaxis_title="Aktual (penumpang)", yaxis_title="Prediksi (penumpang)")
    return _apply_theme(fig, "Prediksi vs Aktual (Test Set)")


def residual_distribution(pred_df: pd.DataFrame) -> go.Figure:
    """Distribusi residual (aktual - prediksi)."""
    fig = go.Figure(
        go.Histogram(
            x=pred_df["residual"],
            nbinsx=50,
            marker_color=config.COLOR_BLUE,
            hovertemplate="residual %{x:.1f}<br>%{y:,} slot<extra></extra>",
        )
    )
    fig.add_vline(x=0, line=dict(color=config.COLOR_ORANGE, dash="dash"))
    fig.update_layout(xaxis_title="Residual (Aktual - Prediksi)", yaxis_title="Jumlah Slot", bargap=0.02)
    return _apply_theme(fig, "Distribusi Residual")


def predicted_day_curve(hours, preds) -> go.Figure:
    """Kurva prediksi demand sepanjang hari (menyoroti jam sibuk)."""
    peak = [features._is_peak(int(h)) for h in hours]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(hours),
            y=list(preds),
            mode="lines",
            line=dict(color=config.COLOR_BLUE, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(30,90,168,0.12)",
            hovertemplate="Jam %{x}:00<br>prediksi %{y:.1f} penumpang<extra></extra>",
            name="Prediksi",
        )
    )
    # Titik jam sibuk (jingga)
    fig.add_trace(
        go.Scatter(
            x=[h for h, pk in zip(hours, peak) if pk],
            y=[y for y, pk in zip(preds, peak) if pk],
            mode="markers",
            marker=dict(color=config.COLOR_ORANGE, size=10, line=dict(color="white", width=1)),
            hovertemplate="Jam sibuk %{x}:00<br>%{y:.1f} penumpang<extra></extra>",
            name="Jam sibuk",
        )
    )
    fig.update_layout(xaxis_title="Jam", yaxis_title="Prediksi Penumpang")
    fig.update_xaxes(dtick=1)
    return _apply_theme(fig, "Prediksi Permintaan Sepanjang Hari")


def mae_by_hour(pred_df: pd.DataFrame) -> go.Figure:
    """Diagnostik: rata-rata galat absolut (MAE) per jam pada test set."""
    d = pred_df.assign(abs_err=(pred_df["actual"] - pred_df["predicted"]).abs())
    g = d.groupby("hour")["abs_err"].mean()
    fig = go.Figure(
        go.Bar(
            x=g.index,
            y=g.values,
            marker_color=config.COLOR_BLUE,
            hovertemplate="Jam %{x}:00<br>MAE %{y:.2f} penumpang<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Jam", yaxis_title="MAE (penumpang)")
    fig.update_xaxes(dtick=1)
    return _apply_theme(fig, "Galat Rata-rata (MAE) per Jam")


def prediction_gauge(value: float, avg_reference: float) -> go.Figure:
    """Gauge hasil prediksi demand relatif terhadap rata-rata."""
    upper = max(value, avg_reference) * 1.8 + 5
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={"reference": avg_reference, "increasing": {"color": config.COLOR_ORANGE}},
            number={"suffix": " pnp", "font": {"color": config.COLOR_BLUE_DARK}},
            gauge={
                "axis": {"range": [0, upper]},
                "bar": {"color": config.COLOR_ORANGE},
                "steps": [
                    {"range": [0, avg_reference], "color": config.COLOR_BLUE_LIGHT},
                    {"range": [avg_reference, upper], "color": "#D6E4F5"},
                ],
                "threshold": {
                    "line": {"color": config.COLOR_BLUE_DARK, "width": 3},
                    "value": avg_reference,
                },
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10))
    return _apply_theme(fig)
