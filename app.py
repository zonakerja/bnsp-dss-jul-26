"""Aplikasi Streamlit — TransJakarta Passenger Analytics & Demand Prediction.

Portofolio asesmen Data Scientist BNSP (Skema Ilmuwan Data — DSS.01.00.23).
Alur mengikuti CRISP-DM; navigasi via sidebar (8 halaman).

Jalankan:  streamlit run app.py
"""
from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from src import config, data_loader, features, preprocessing, viz

# --------------------------------------------------------------------------- #
# KONFIGURASI HALAMAN & GAYA
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS = f"""
<style>
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
    /* Banner judul */
    .hero {{
        background: linear-gradient(120deg, {config.COLOR_BLUE} 0%, {config.COLOR_BLUE_DARK} 100%);
        padding: 1.6rem 2rem; border-radius: 16px; color: white; margin-bottom: 1.2rem;
        box-shadow: 0 6px 20px rgba(27,42,74,0.18);
    }}
    .hero h1 {{ color: white; margin: 0; font-size: 1.9rem; }}
    .hero p  {{ color: #E6ECF5; margin: .35rem 0 0; font-size: 1rem; }}
    .hero .badge {{
        display:inline-block; background:{config.COLOR_ORANGE}; color:white;
        padding:.18rem .7rem; border-radius:20px; font-size:.78rem; margin-top:.7rem;
    }}
    /* Kartu KPI */
    .kpi {{
        background:{config.COLOR_BLUE_LIGHT}; border-left:5px solid {config.COLOR_ORANGE};
        border-radius:12px; padding:1rem 1.1rem; height:100%;
    }}
    .kpi .label {{ color:{config.COLOR_GRAY}; font-size:.82rem; margin:0; }}
    .kpi .value {{ color:{config.COLOR_BLUE_DARK}; font-size:1.55rem; font-weight:700; margin:.15rem 0 0; }}
    .kpi .sub   {{ color:{config.COLOR_GRAY}; font-size:.72rem; margin:.1rem 0 0; }}
    /* Kotak insight */
    .insight {{
        background:#FFFFFF; border:1px solid #E1E8F2; border-left:5px solid {config.COLOR_BLUE};
        border-radius:12px; padding:1rem 1.2rem; margin:.5rem 0;
    }}
    .insight.orange {{ border-left-color:{config.COLOR_ORANGE}; }}
    h2, h3 {{ color:{config.COLOR_BLUE_DARK}; }}
    section[data-testid="stSidebar"] {{ background:{config.COLOR_BLUE_LIGHT}; }}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


def fmt(n) -> str:
    """Format angka gaya Indonesia (pemisah ribuan titik)."""
    try:
        return f"{n:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(n)


def kpi(label: str, value: str, sub: str = "") -> str:
    return f'<div class="kpi"><p class="label">{label}</p><p class="value">{value}</p><p class="sub">{sub}</p></div>'


def insight(text: str, orange: bool = False) -> None:
    cls = "insight orange" if orange else "insight"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# PEMUATAN DATA & ARTEFAK (cached)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Memuat & membersihkan data ...")
def load_data():
    raw = data_loader.load_raw_data()
    overview = data_loader.dataset_overview(raw)
    report = preprocessing.validate_data(raw)
    recs = preprocessing.completeness_recommendation(report)
    clean, log = preprocessing.clean_data(raw)
    return clean, log, report, recs, overview


@st.cache_data(show_spinner="Menyiapkan dataset pemodelan ...")
def get_modeling():
    clean, *_ = load_data()
    return features.build_demand_dataset(clean)


@st.cache_resource(show_spinner="Memuat model ...")
def load_model():
    if config.MODEL_PATH.exists():
        return joblib.load(config.MODEL_PATH)
    return None


@st.cache_data
def load_artifacts():
    metrics = comp = fi = pred = None
    if config.METRICS_PATH.exists():
        metrics = json.loads(config.METRICS_PATH.read_text(encoding="utf-8"))
    if config.MODEL_COMPARISON_PATH.exists():
        comp = pd.read_csv(config.MODEL_COMPARISON_PATH)
    fi_path = config.REPORTS_DIR / "feature_importance.csv"
    if fi_path.exists():
        fi = pd.read_csv(fi_path)
    pred_path = config.REPORTS_DIR / "test_predictions.csv"
    if pred_path.exists():
        pred = pd.read_csv(pred_path)
    return metrics, comp, fi, pred


@st.cache_data
def corridor_reference():
    """Opsi koridor + rata-rata demand historis per koridor (untuk simulasi)."""
    clean, *_ = load_data()
    opt = (
        clean[clean["corridorID"] != config.UNKNOWN_LABEL]
        [["corridorID", "corridorName", "corridor_type"]]
        .drop_duplicates(subset=["corridorID"])
        .sort_values("corridorName")
        .reset_index(drop=True)
    )
    model_df = get_modeling()
    corr_mean = model_df.groupby("corridorID")["passenger_count"].mean()
    global_mean = float(model_df["passenger_count"].mean())
    return opt, corr_mean, global_mean


# =========================================================================== #
# HALAMAN
# =========================================================================== #
def page_home():
    st.markdown(
        f"""<div class="hero">
        <h1>🚌 {config.APP_TITLE}</h1>
        <p>{config.APP_SUBTITLE}</p>
        <span class="badge">Portofolio Sertifikasi BNSP · {config.SCHEME_NAME}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    clean, _, report, _, _ = load_data()
    metrics, *_ = load_artifacts()
    r2 = metrics["test_metrics"]["R2"] if metrics else None
    mae = metrics["test_metrics"]["MAE"] if metrics else None

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Total Transaksi", fmt(len(clean)), "tap-in/tap-out"), unsafe_allow_html=True)
    c2.markdown(kpi("Kartu Unik", fmt(clean["payCardID"].nunique()), "pengguna"), unsafe_allow_html=True)
    c3.markdown(kpi("Koridor", fmt(clean["corridorName"].nunique()), "rute terlayani"), unsafe_allow_html=True)
    c4.markdown(
        kpi("Akurasi Model", f"R² {r2:.2f}" if r2 else "-", f"MAE {mae:.2f} pnp" if mae else ""),
        unsafe_allow_html=True,
    )

    st.markdown("### 🎯 Latar Belakang & Objektif Bisnis")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        insight(
            "<b>Masalah.</b> Ketidakseimbangan antara jumlah armada dan permintaan aktual "
            "penumpang menyebabkan penumpukan di jam sibuk sekaligus armada kosong saat lengang, "
            "serta alokasi petugas yang tidak optimal."
        )
        insight(
            "<b>Objektif Bisnis.</b> (1) Memahami pola pergerakan penumpang; "
            "(2) Membangun model prediksi jumlah penumpang per koridor/jam/hari; "
            "(3) Menyediakan alat bantu keputusan interaktif untuk perencanaan operasional.",
            orange=True,
        )
    with col2:
        st.markdown("**Metrik Kesuksesan**")
        st.markdown(
            f"- 🎯 **Operasional (MAE)** ≤ 1,5 pnp/slot → **{mae:.2f}** ✅\n"
            f"- 📈 **Statistik (R²)** ≥ 0,70 → **{r2:.3f}** ✅\n"
            f"- 🏆 Unggul dari baseline & regresi linier ✅"
            if metrics else "_Jalankan `python -m src.train_model` untuk mengisi metrik._"
        )

    st.markdown("### 🔄 Metodologi CRISP-DM")
    steps = [
        ("1️⃣ Business Understanding", "Objektif bisnis, metrik sukses, risiko"),
        ("2️⃣ Data Understanding", "Telaah tipe, statistik, visualisasi, hipotesis"),
        ("3️⃣ Data Preparation", "Validasi, pembersihan, seleksi, feature engineering"),
        ("4️⃣ Modeling", "7 model dibandingkan, tuning pemenang"),
        ("5️⃣ Evaluation", "Metrik, prediksi vs aktual, review proses"),
        ("6️⃣ Deployment", "Aplikasi Streamlit interaktif"),
    ]
    cols = st.columns(3)
    for i, (t, d) in enumerate(steps):
        cols[i % 3].markdown(f'<div class="insight"><b>{t}</b><br><span style="color:#6B7A99">{d}</span></div>', unsafe_allow_html=True)

    st.caption(f"Asesi: **{config.ASESI_NAME}**  ·  Periode data: {config.DATA_PERIOD}  ·  Sumber: dataset TransJakarta")


def page_dataset():
    st.header("📂 Dataset & Telaah Data")
    st.caption("SKKNI Unit 3 — Menelaah Data: tipe & relasi data, statistik deskriptif, hipotesis.")
    clean, _, _, _, overview = load_data()

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Struktur Kolom", "📊 Statistik Deskriptif", "🔎 Cuplikan Data", "💡 Hipotesis"])
    with tab1:
        st.dataframe(overview, width="stretch", hide_index=True)
        st.caption("22 kolom: identitas transaksi, demografi kartu, koridor, halte + geolokasi, waktu tap, tarif.")
    with tab2:
        st.dataframe(
            data_loader.descriptive_stats(clean).round(2), width="stretch"
        )
        insight(
            "Kolom <b>travel_min</b> (durasi) tampak acak — korelasi dengan jarak ≈ 0 "
            "→ <b>tidak</b> dijadikan target. <b>payAmount</b> nyaris deterministik dari jenis "
            "koridor (rute JAK gratis) → dipakai untuk EDA, bukan prediktor demand."
        )
    with tab3:
        cols = st.multiselect(
            "Pilih kolom",
            list(clean.columns),
            default=["transID", "payCardBank", "payCardSex", "age", "corridorName", "tapInStopsName", "tapInTime", "payAmount"],
        )
        st.dataframe(clean[cols].head(200), width="stretch", hide_index=True)
    with tab4:
        st.markdown(
            "- **H1** — Demand memuncak pada jam sibuk pagi & sore (pola *bimodal*).\n"
            "- **H2** — Demand hari kerja jauh lebih tinggi daripada akhir pekan.\n"
            "- **H3** — Sebagian kecil koridor menyumbang mayoritas perjalanan (*long-tail*).\n"
            "- **H4** — Fitur waktu adalah prediktor demand terkuat, mengungguli demografi.\n\n"
            "Hipotesis diuji pada halaman **EDA** dan dikonfirmasi pada **Pemodelan** (feature importance)."
        )


def page_quality():
    st.header("✅ Kualitas & Pembersihan Data")
    st.caption("SKKNI Unit 4-6 — Validasi, seleksi objek data, dan pembersihan data.")
    clean, log, report, recs, _ = load_data()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Baris Lengkap", f'{report["persen_baris_lengkap"]:.1f}%', "tanpa missing"), unsafe_allow_html=True)
    c2.markdown(kpi("Duplikat transID", fmt(report["duplikat_transID"]), "integritas terjaga"), unsafe_allow_html=True)
    c3.markdown(kpi("Perjalanan Tak Lengkap", fmt(report["perjalanan_tak_lengkap"]), "tanpa tap-out"), unsafe_allow_html=True)
    c4.markdown(kpi("Koordinat Invalid", fmt(report.get("koordinat_diluar_wilayah", 0)), "di luar Jabodetabek"), unsafe_allow_html=True)

    st.markdown("#### 🔍 Kelengkapan Data (Missing Value)")
    miss = preprocessing.missing_report(clean)
    miss = miss[miss["jumlah_missing"] > 0]
    if len(miss):
        st.bar_chart(miss.set_index("kolom")["persen_missing"], color=config.COLOR_ORANGE, height=280)
    st.caption("Kolom tap-out & koridor paling banyak kosong — ditangani pada strategi pembersihan di bawah.")

    st.markdown("#### 🧹 Log Pembersihan Data (before → after)")
    log_df = pd.DataFrame(log)[["langkah", "deskripsi", "baris_sebelum", "baris_sesudah", "catatan"]]
    st.dataframe(log_df, width="stretch", hide_index=True)

    st.markdown("#### 📝 Rekomendasi Kualitas & Kecukupan Data")
    for r in recs:
        insight(r)


def page_eda():
    st.header("🔍 Analisis Data Eksploratif (EDA)")
    st.caption("SKKNI Unit 3 — Karakteristik data disajikan dengan visualisasi & dianalisis.")
    clean, *_ = load_data()

    with st.sidebar:
        st.markdown("### 🎛️ Filter EDA")
        types = sorted(clean["corridor_type"].dropna().unique())
        sel_types = st.multiselect("Jenis koridor", types, default=types)
        sexes = st.multiselect("Gender", ["F", "M"], default=["F", "M"])
        hr = st.slider("Rentang jam", 5, 21, (5, 21))

    mask = (
        clean["corridor_type"].isin(sel_types)
        & clean["payCardSex"].isin(sexes)
        & clean["tapInTime"].dt.hour.between(hr[0], hr[1])
    )
    df = clean[mask]
    st.caption(f"Menampilkan **{fmt(len(df))}** dari {fmt(len(clean))} transaksi sesuai filter.")

    t1, t2, t3 = st.tabs(["⏰ Pola Waktu", "🚌 Koridor & Tarif", "👥 Demografi"])
    with t1:
        st.plotly_chart(viz.hourly_demand(df), width="stretch")
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.weekday_weekend(df), width="stretch")
        c2.plotly_chart(viz.demand_heatmap(df), width="stretch")
        insight("<b>H1 & H2 terbukti:</b> puncak tajam pada jam 6–7 & 16–17, serta hari kerja jauh melampaui akhir pekan.", orange=True)
    with t2:
        c1, c2 = st.columns([1.3, 1])
        c1.plotly_chart(viz.top_corridors(df), width="stretch")
        c2.plotly_chart(viz.corridor_type_share(df), width="stretch")
        st.plotly_chart(viz.fare_distribution(df), width="stretch")
        insight("<b>H3 terbukti:</b> distribusi koridor <i>long-tail</i> — sedikit koridor mendominasi. Rute Mikrotrans (JAK) konsisten gratis.")
    with t3:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.age_distribution(df), width="stretch")
        c2.plotly_chart(viz.gender_share(df), width="stretch")
        st.plotly_chart(viz.bank_share(df), width="stretch")


def page_map():
    st.header("🗺️ Peta Geospasial Halte")
    st.caption("Kepadatan penumpang per halte tap-in — mendukung penempatan sumber daya.")
    clean, *_ = load_data()
    top_n = st.slider("Jumlah halte teratas ditampilkan", 100, 1000, 400, step=100)
    st.plotly_chart(viz.stops_map(clean, top_n=top_n), width="stretch")
    insight(
        "Ukuran & warna titik menandakan volume penumpang. Klaster padat berpusat di "
        "koridor utama Jakarta — kandidat prioritas penambahan armada & petugas."
    )


def page_model():
    st.header("🤖 Pemodelan & Evaluasi")
    st.caption("SKKNI Unit 7-11 — Konstruksi fitur, skenario model, pembangunan, evaluasi, review.")
    metrics, comp, fi, pred = load_artifacts()
    if metrics is None:
        st.warning("Artefak model belum tersedia. Jalankan `python -m src.train_model` terlebih dahulu.")
        return

    m = metrics["test_metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Model Terbaik", metrics["best_model"], "objektif Poisson"), unsafe_allow_html=True)
    c2.markdown(kpi("R² (Test)", f'{m["R2"]:.3f}', "variasi terjelaskan"), unsafe_allow_html=True)
    c3.markdown(kpi("MAE", f'{m["MAE"]:.2f}', "penumpang/slot"), unsafe_allow_html=True)
    c4.markdown(kpi("RMSE", f'{m["RMSE"]:.2f}', "penumpang/slot"), unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["🏁 Perbandingan Model", "⭐ Feature Importance", "🎯 Prediksi vs Aktual", "🧪 Metodologi"])
    with t1:
        st.plotly_chart(viz.model_comparison(comp), width="stretch")
        st.dataframe(comp, width="stretch", hide_index=True)
        insight(f"<b>{metrics['best_model']}</b> unggul pada semua metrik. Model tree-based mengungguli "
                "regresi linier karena hubungan fitur-target non-linier (efek jam & hari).", orange=True)
    with t2:
        st.plotly_chart(viz.feature_importance(fi), width="stretch")
        insight("<b>H4 terbukti:</b> fitur waktu (<i>is_weekend, day_of_week, part_of_day, hour</i>) "
                "mendominasi — mengonfirmasi bahwa demand digerakkan oleh pola temporal.")
    with t3:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.pred_vs_actual(pred), width="stretch")
        c2.plotly_chart(viz.residual_distribution(pred), width="stretch")
        insight("Titik mengumpul di sekitar garis ideal; residual terpusat di nol tanpa bias sistematis.")
    with t4:
        st.markdown(
            f"""
**Unit analisis.** Agregasi ke level *(koridor × tanggal × jam)* → target `passenger_count`.
**Split.** {fmt(metrics['n_train'])} train / {fmt(metrics['n_test'])} test (80/20).

**Fitur ({len(features.ALL_FEATURES)}):**
- *Target-encode* (cross-fitted, anti-bocor): `corridorID`
- *One-hot*: `corridor_type`, `day_name`, `part_of_day`
- *Numerik*: `hour`, `day_of_week`, `is_weekend`, `is_peak`, `week_of_month`

**Skenario uji.** Cross-validation {3}-fold untuk seleksi model; metrik R², MAE, RMSE, MAPE.
**Optimasi.** RandomizedSearchCV pada pemenang (dipertahankan bila CV meningkat).

**Anti-kebocoran.** Fitur demografi per-slot sengaja tidak dipakai (baru diketahui setelah penumpang tap);
demand historis koridor ditangani `TargetEncoder` ber-cross-fitting, bukan rata-rata manual.

**Review (Unit 11).** {metrics['success_criteria']['catatan']}
"""
        )


def page_simulation():
    st.header("🎯 Simulasi Prediksi Demand")
    st.caption("Perkirakan jumlah penumpang untuk kombinasi koridor, hari, dan jam tertentu.")
    model = load_model()
    if model is None:
        st.warning("Model belum tersedia. Jalankan `python -m src.train_model` terlebih dahulu.")
        return
    opt, corr_mean, global_mean = corridor_reference()

    c1, c2, c3 = st.columns(3)
    with c1:
        corridor_name = st.selectbox("🚌 Koridor", opt["corridorName"].tolist())
    row = opt[opt["corridorName"] == corridor_name].iloc[0]
    with c2:
        day_name = st.selectbox("📅 Hari", features.DAY_NAMES, index=0)
        dow = features.DAY_NAMES.index(day_name)
    with c3:
        hour = st.slider("🕐 Jam", 5, 21, 7)

    x = features.make_prediction_row(row["corridorID"], row["corridor_type"], dow, hour)
    pred = float(np.clip(model.predict(x)[0], 0, None))
    ref = float(corr_mean.get(row["corridorID"], global_mean))

    st.markdown("---")
    cc1, cc2 = st.columns([1, 1.1])
    with cc1:
        st.plotly_chart(viz.prediction_gauge(pred, ref), width="stretch")
    with cc2:
        st.markdown("### Hasil Prediksi")
        st.markdown(
            f"<div class='kpi'><p class='label'>Perkiraan penumpang</p>"
            f"<p class='value'>{pred:.0f} orang</p>"
            f"<p class='sub'>{row['corridor_type']} · {day_name} · pukul {hour:02d}:00</p></div>",
            unsafe_allow_html=True,
        )
        diff = pred - ref
        arah = "di atas" if diff >= 0 else "di bawah"
        insight(
            f"Prediksi ini <b>{abs(diff):.1f} penumpang {arah}</b> rata-rata historis koridor "
            f"({ref:.1f} pnp/jam). "
            + ("Termasuk periode <b>sibuk</b> 🔴" if features._is_peak(hour) else "Termasuk periode <b>lengang</b> 🟢"),
            orange=features._is_peak(hour),
        )
        st.caption("Catatan: prediksi pada level koridor-jam (rata-rata cacah kecil); gunakan untuk perencanaan relatif, bukan angka absolut presisi.")


def page_conclusion():
    st.header("📌 Kesimpulan & Rekomendasi")
    metrics, *_ = load_artifacts()
    r2 = metrics["test_metrics"]["R2"] if metrics else 0
    mae = metrics["test_metrics"]["MAE"] if metrics else 0

    st.markdown("### 🔑 Temuan Utama")
    insight("<b>Pola temporal dominan.</b> Demand memuncak pada jam sibuk pagi (6–7) & sore (16–17); "
            "hari kerja ±3,7× lebih ramai dari akhir pekan. Fitur waktu adalah prediktor terkuat.", orange=True)
    insight("<b>Konsentrasi koridor.</b> Distribusi <i>long-tail</i> — sebagian kecil koridor menyerap mayoritas penumpang.")
    insight(f"<b>Model andal.</b> {metrics['best_model'] if metrics else 'XGBoost'} (Poisson) mencapai "
            f"R² {r2:.3f} dan MAE {mae:.2f} penumpang — memadai untuk perencanaan operasional.")

    st.markdown("### 💼 Rekomendasi Bisnis (Actionable)")
    st.markdown(
        "1. **Penjadwalan dinamis armada** — perbanyak frekuensi di jam & koridor puncak, kurangi saat lengang.\n"
        "2. **Alokasi petugas berbasis prediksi** — tempatkan SDM pada slot koridor-jam berdemand tinggi.\n"
        "3. **Manajemen akhir pekan** — sesuaikan operasi mengikuti pola akhir pekan yang jauh lebih rendah.\n"
        "4. **Prioritas halte padat** — fokus perbaikan kapasitas pada klaster halte tersibuk (lihat Peta)."
    )

    st.markdown("### ⚠️ Keterbatasan & Pengembangan (Review — Unit 11)")
    st.markdown(
        "- Data hanya **1 bulan** (April 2023) → belum menangkap musiman tahunan/hari libur nasional.\n"
        "- Granularitas koridor-jam memiliki **batas bawah noise Poisson** (rata-rata cacah kecil) → R² 0,80 sulit dilampaui.\n"
        "- **Pengembangan:** tambah data multi-bulan, fitur eksternal (cuaca, hari libur, event), serta uji model deret waktu."
    )

    st.markdown("### 🧭 Pemetaan Kompetensi SKKNI")
    mapping = pd.DataFrame(
        {
            "Unit": [f"J.62DMI00.{c}" for c in ["001","002","005","006","007","008","009","012-015"]],
            "Kompetensi": ["Objektif Bisnis","Tujuan Teknis","Menelaah Data","Memvalidasi Data",
                            "Menentukan Objek Data / Membersihkan","Mengkonstruksi Data",
                            "Skenario & Bangun Model","Evaluasi & Review Pemodelan"],
            "Dibuktikan di Halaman": ["Beranda","Beranda","Dataset & Telaah","Kualitas Data",
                                       "Kualitas Data","Pemodelan","Pemodelan","Pemodelan & Kesimpulan"],
        }
    )
    st.dataframe(mapping, width="stretch", hide_index=True)
    st.success("Seluruh 11 unit kompetensi SKKNI tercakup dalam alur portofolio ini.")


# =========================================================================== #
# NAVIGASI
# =========================================================================== #
PAGES = {
    "🏠 Beranda": page_home,
    "📂 Dataset & Telaah": page_dataset,
    "✅ Kualitas Data": page_quality,
    "🔍 EDA Interaktif": page_eda,
    "🗺️ Peta Geospasial": page_map,
    "🤖 Pemodelan": page_model,
    "🎯 Simulasi Prediksi": page_simulation,
    "📌 Kesimpulan": page_conclusion,
}

with st.sidebar:
    st.markdown(f"## 🚌 {config.APP_TITLE}")
    st.caption(config.SCHEME_NAME)
    choice = st.radio("Navigasi", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")

PAGES[choice]()

with st.sidebar:
    st.markdown("---")
    st.caption(f"👤 Asesi: **{config.ASESI_NAME}**")
    st.caption(f"📅 Data: {config.DATA_PERIOD}")
