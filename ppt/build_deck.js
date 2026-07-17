// Generator PPT — Portofolio TransJakarta Demand Prediction (BNSP)
// Jalankan: node build_deck.js
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
p.author = "Asesi BNSP";
p.title = "TransJakarta Demand Prediction";

// ---- Palet (biru-putih-jingga) ----
const NAVY = "1B2A4A", BLUE = "1E5AA8", BLUE2 = "4A90D9";
const ORANGE = "F26522", LIGHT = "EAF2FB", WHITE = "FFFFFF", GRAY = "6B7A99";
const HFONT = "Cambria", BFONT = "Calibri";
const ASSET = "../assets/";
const A = (f) => ASSET + f;

const shadow = () => ({ type: "outer", color: "AAB6CC", blur: 9, offset: 3, angle: 90, opacity: 0.35 });
const NUM = (s) => s; // helper

// Kartu rounded dengan shadow
function card(slide, x, y, w, h, fill = WHITE) {
  slide.addShape(p.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { type: "none" }, rectRadius: 0.09, shadow: shadow() });
}
// Badge lingkaran jingga bernomor (motif berulang)
function badge(slide, x, y, txt) {
  slide.addShape(p.ShapeType.ellipse, { x, y, w: 0.5, h: 0.5, fill: { color: ORANGE }, line: { type: "none" } });
  slide.addText(txt, { x, y, w: 0.5, h: 0.5, align: "center", valign: "middle", color: WHITE, bold: true, fontSize: 16, fontFace: BFONT, margin: 0 });
}
function title(slide, txt, sub) {
  slide.addText(txt, { x: 0.6, y: 0.42, w: 12.1, h: 0.7, fontSize: 30, bold: true, color: NAVY, fontFace: HFONT, margin: 0 });
  if (sub) slide.addText(sub, { x: 0.62, y: 1.12, w: 12.1, h: 0.4, fontSize: 14, color: ORANGE, italic: true, fontFace: BFONT, margin: 0 });
}
function bg(slide, color) {
  slide.background = { color };
}

// =================== SLIDE 1 — COVER ===================
{
  const s = p.addSlide(); bg(s, NAVY);
  s.addShape(p.ShapeType.ellipse, { x: 10.6, y: -1.4, w: 4.2, h: 4.2, fill: { color: BLUE }, line: { type: "none" } });
  s.addShape(p.ShapeType.ellipse, { x: 11.8, y: 4.6, w: 3.2, h: 3.2, fill: { color: ORANGE }, line: { type: "none" }, });
  s.addText("🚌", { x: 0.6, y: 0.7, w: 1.2, h: 1.2, fontSize: 54, margin: 0 });
  s.addText("TransJakarta Passenger Analytics\n& Demand Prediction", { x: 0.6, y: 1.9, w: 10.6, h: 1.9, fontSize: 40, bold: true, color: WHITE, fontFace: HFONT, lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("Analisis Pola Penumpang & Prediksi Permintaan Transportasi Publik dengan Machine Learning", { x: 0.62, y: 3.75, w: 9.8, h: 0.7, fontSize: 16, color: "CADCFC", italic: true, fontFace: BFONT, margin: 0 });
  s.addShape(p.ShapeType.roundRect, { x: 0.62, y: 4.6, w: 6.2, h: 0.55, fill: { color: ORANGE }, line: { type: "none" }, rectRadius: 0.27 });
  s.addText("Portofolio Sertifikasi BNSP · Ilmuwan Data (DSS.01.00.23)", { x: 0.62, y: 4.6, w: 6.2, h: 0.55, align: "center", valign: "middle", color: WHITE, bold: true, fontSize: 12.5, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Asesi: ", options: { color: GRAY } },
    { text: "Mohammad Yusuf", options: { color: WHITE, bold: true } },
    { text: "     |     Metodologi: CRISP-DM     |     Periode data: April 2023", options: { color: "CADCFC" } },
  ], { x: 0.62, y: 6.4, w: 12, h: 0.5, fontSize: 13, fontFace: BFONT, margin: 0 });
  s.addNotes("Perkenalan: portofolio Data Scientist BNSP. Proyek memprediksi demand penumpang TransJakarta memakai machine learning, mengikuti siklus CRISP-DM penuh.");
}

// =================== SLIDE 2 — LATAR BELAKANG ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Latar Belakang & Permasalahan Bisnis", "CRISP-DM 1 — Business Understanding · SKKNI Unit 1");
  s.addText("TransJakarta melayani jutaan perjalanan setiap bulan. Ketidakseimbangan antara ketersediaan armada dan permintaan aktual penumpang menimbulkan tiga masalah utama:", { x: 0.6, y: 1.7, w: 6.0, h: 1.2, fontSize: 15, color: NAVY, fontFace: BFONT, margin: 0 });
  const probs = [
    ["Penumpukan di jam sibuk", "Penumpang menumpuk saat armada tak cukup"],
    ["Armada kosong saat lengang", "Utilisasi rendah di luar jam puncak"],
    ["Alokasi SDM tak optimal", "Penempatan petugas halte tidak berbasis data"],
  ];
  probs.forEach((pr, i) => {
    const y = 3.0 + i * 1.15;
    card(s, 0.6, y, 6.0, 1.0, LIGHT);
    badge(s, 0.85, y + 0.25, String(i + 1));
    s.addText(pr[0], { x: 1.5, y: y + 0.13, w: 5.0, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: BFONT, margin: 0 });
    s.addText(pr[1], { x: 1.5, y: y + 0.52, w: 5.0, h: 0.4, fontSize: 12, color: GRAY, fontFace: BFONT, margin: 0 });
  });
  // Stat besar di kanan
  const stats = [["189.500", "Transaksi tap"], ["10.000", "Kartu unik"], ["216", "Koridor"], ["April 2023", "Periode data"]];
  stats.forEach((st, i) => {
    const x = 7.1 + (i % 2) * 3.05, y = 1.85 + Math.floor(i / 2) * 2.35;
    card(s, x, y, 2.8, 2.05, NAVY);
    s.addText(st[0], { x, y: y + 0.4, w: 2.8, h: 0.9, align: "center", fontSize: 30, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
    s.addText(st[1], { x, y: y + 1.35, w: 2.8, h: 0.4, align: "center", fontSize: 13, color: "CADCFC", fontFace: BFONT, margin: 0 });
  });
  s.addNotes("Masalah bisnis: armada vs permintaan tidak seimbang. Dataset: 189.500 transaksi, 10.000 kartu, 216 koridor pada April 2023.");
}

// =================== SLIDE 3 — OBJEKTIF & TUJUAN TEKNIS ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Objektif Bisnis, Metrik Sukses & Tujuan Teknis", "SKKNI Unit 1 & 2 — Business & Technical Goals");
  card(s, 0.6, 1.75, 6.0, 4.9, LIGHT);
  s.addText("🎯  Objektif Bisnis", { x: 0.85, y: 1.95, w: 5.5, h: 0.4, fontSize: 17, bold: true, color: BLUE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Memahami pola pergerakan penumpang (jam, hari, koridor, demografi)", options: { bullet: true, breakLine: true } },
    { text: "Membangun model prediksi jumlah penumpang per koridor/jam/hari", options: { bullet: true, breakLine: true } },
    { text: "Menyediakan alat bantu keputusan interaktif untuk perencanaan operasional", options: { bullet: true } },
  ], { x: 0.9, y: 2.45, w: 5.4, h: 1.7, fontSize: 14, color: NAVY, fontFace: BFONT, paraSpaceAfter: 8, margin: 0 });
  s.addText("🔧  Tujuan Teknis", { x: 0.85, y: 4.25, w: 5.5, h: 0.4, fontSize: 17, bold: true, color: BLUE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Task: Supervised Regression (memprediksi cacah penumpang)", options: { bullet: true, breakLine: true } },
    { text: "Unit analisis: agregasi (koridor × tanggal × jam)", options: { bullet: true, breakLine: true } },
    { text: "Kriteria: R², MAE, RMSE, MAPE pada data hold-out", options: { bullet: true } },
  ], { x: 0.9, y: 4.75, w: 5.4, h: 1.7, fontSize: 14, color: NAVY, fontFace: BFONT, paraSpaceAfter: 8, margin: 0 });

  s.addText("Metrik Kesuksesan", { x: 7.1, y: 1.75, w: 5.6, h: 0.4, fontSize: 17, bold: true, color: NAVY, fontFace: HFONT, margin: 0 });
  const met = [
    ["Operasional — MAE", "≤ 1,5 pnp/slot", "1,05  ✓", ORANGE],
    ["Statistik — R²", "≥ 0,70", "0,715  ✓", BLUE],
    ["Vs Baseline", "harus unggul", "Unggul  ✓", BLUE2],
  ];
  met.forEach((m, i) => {
    const y = 2.35 + i * 1.4;
    card(s, 7.1, y, 5.6, 1.2, WHITE);
    s.addShape(p.ShapeType.ellipse, { x: 7.32, y: y + 0.5, w: 0.2, h: 0.2, fill: { color: m[3] }, line: { type: "none" } });
    s.addText(m[0], { x: 7.65, y: y + 0.14, w: 3.4, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: BFONT, margin: 0 });
    s.addText("Target " + m[1], { x: 7.65, y: y + 0.6, w: 3.4, h: 0.4, fontSize: 12, color: GRAY, fontFace: BFONT, margin: 0 });
    s.addText(m[2], { x: 10.9, y: y + 0.28, w: 1.7, h: 0.7, align: "center", valign: "middle", fontSize: 20, bold: true, color: m[3], fontFace: HFONT, margin: 0 });
  });
  s.addNotes("Tiga objektif bisnis dan tujuan teknis (regresi). Metrik sukses: MAE operasional tercapai 1,05; R² 0,715; unggul dari baseline.");
}

// =================== SLIDE 4 — DATASET ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Dataset & Telaah Data", "CRISP-DM 2 — Data Understanding · SKKNI Unit 3");
  s.addText("Data transaksi smart-card tap-in/tap-out TransJakarta — 22 kolom mencakup identitas transaksi, demografi kartu, koridor, halte + geolokasi, waktu, dan tarif.", { x: 0.6, y: 1.7, w: 12.1, h: 0.7, fontSize: 14.5, color: NAVY, fontFace: BFONT, margin: 0 });
  const groups = [
    ["🪪 Demografi", "Bank, nama, gender, tahun lahir → usia (11–77 th)"],
    ["🚌 Koridor", "216 rute: BRT, Mikrotrans (JAK), pengumpan"],
    ["📍 Geolokasi", "Halte tap-in & tap-out + lintang/bujur"],
    ["🕐 Waktu", "Timestamp tap → jam & hari (fitur kunci)"],
    ["💳 Tarif", "Rp0 (JAK gratis), Rp3.500 (BRT), Rp20.000 (premium)"],
    ["🎯 Target", "Agregasi jumlah penumpang per koridor-jam"],
  ];
  groups.forEach((g, i) => {
    const x = 0.6 + (i % 3) * 4.05, y = 2.6 + Math.floor(i / 3) * 1.55;
    card(s, x, y, 3.85, 1.35, i === 5 ? NAVY : LIGHT);
    const col = i === 5 ? WHITE : NAVY, sub = i === 5 ? "CADCFC" : GRAY;
    s.addText(g[0], { x: x + 0.2, y: y + 0.15, w: 3.5, h: 0.4, fontSize: 15, bold: true, color: col, fontFace: BFONT, margin: 0 });
    s.addText(g[1], { x: x + 0.2, y: y + 0.6, w: 3.5, h: 0.65, fontSize: 12, color: sub, fontFace: BFONT, margin: 0 });
  });
  s.addText("Temuan penting: durasi perjalanan acak (korelasi ≈ 0 dengan jarak) → tidak dijadikan target; tarif deterministik dari koridor → hanya untuk EDA.", { x: 0.6, y: 5.85, w: 12.1, h: 0.6, fontSize: 12.5, italic: true, color: ORANGE, fontFace: BFONT, margin: 0 });
  s.addNotes("Struktur data dan enam kelompok kolom. Dua temuan penting yang menghindarkan salah pilih target.");
}

// =================== SLIDE 5 — POLA PERMINTAAN (EDA) ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Pola Permintaan Penumpang", "EDA — Hipotesis H1 & H2 terbukti");
  s.addImage({ path: A("fig_hourly.png"), x: 0.5, y: 1.65, w: 6.4, h: 3.58 });
  s.addImage({ path: A("fig_weekday.png"), x: 7.0, y: 1.65, w: 5.8, h: 3.25 });
  card(s, 0.5, 5.55, 12.3, 1.35, LIGHT);
  s.addText([
    { text: "H1 — Pola bimodal: ", options: { bold: true, color: BLUE } },
    { text: "puncak tajam jam 6–7 pagi & 16–17 sore.    ", options: { color: NAVY } },
    { text: "H2 — Hari kerja ±3,7× lebih ramai ", options: { bold: true, color: ORANGE } },
    { text: "dibanding akhir pekan.", options: { color: NAVY } },
  ], { x: 0.75, y: 5.75, w: 11.8, h: 0.95, fontSize: 15, fontFace: BFONT, valign: "middle", margin: 0 });
  s.addNotes("Pola jam bimodal dan perbedaan hari kerja vs akhir pekan — dasar utama sinyal prediksi.");
}

// =================== SLIDE 6 — KORIDOR & HEATMAP ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Konsentrasi Koridor & Kepadatan Waktu", "EDA — Hipotesis H3 terbukti (distribusi long-tail)");
  s.addImage({ path: A("fig_top_corridors.png"), x: 0.5, y: 1.7, w: 6.2, h: 3.47 });
  s.addImage({ path: A("fig_heatmap.png"), x: 7.0, y: 1.7, w: 5.8, h: 3.25 });
  card(s, 0.5, 5.5, 12.3, 1.35, LIGHT);
  s.addText([
    { text: "H3 — Long-tail: ", options: { bold: true, color: BLUE } },
    { text: "sebagian kecil koridor menyerap mayoritas penumpang. Heatmap menegaskan blok padat pada jam sibuk hari kerja — kandidat prioritas armada & petugas.", options: { color: NAVY } },
  ], { x: 0.75, y: 5.7, w: 11.8, h: 0.95, fontSize: 15, fontFace: BFONT, valign: "middle", margin: 0 });
  s.addNotes("Distribusi koridor long-tail dan heatmap jam×hari. Membantu prioritisasi sumber daya.");
}

// =================== SLIDE 7 — VALIDASI & PEMBERSIHAN ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Validasi & Pembersihan Data", "CRISP-DM 3 — Data Preparation · SKKNI Unit 4–6");
  const checks = [["81,25%", "Baris lengkap"], ["0", "Duplikat transID"], ["6.720", "Perjalanan tak lengkap"], ["0", "Koordinat invalid"]];
  checks.forEach((c, i) => {
    const x = 0.6 + i * 3.05;
    card(s, x, 1.75, 2.8, 1.5, i === 0 ? NAVY : LIGHT);
    const col = i === 0 ? WHITE : NAVY, sub = i === 0 ? "CADCFC" : GRAY;
    s.addText(c[0], { x, y: 1.95, w: 2.8, h: 0.7, align: "center", fontSize: 26, bold: true, color: i === 0 ? WHITE : BLUE, fontFace: HFONT, margin: 0 });
    s.addText(c[1], { x, y: 2.7, w: 2.8, h: 0.4, align: "center", fontSize: 12.5, color: sub, fontFace: BFONT, margin: 0 });
  });
  s.addText("Strategi Pembersihan (dengan log before → after)", { x: 0.6, y: 3.55, w: 12, h: 0.4, fontSize: 16, bold: true, color: NAVY, fontFace: HFONT, margin: 0 });
  const steps = [
    ["Duplikasi transID", "Dibuang untuk integritas transaksi"],
    ["Koridor kosong (20.508 sel)", "Diisi label 'Unknown' agar tetap teragregasi"],
    ["Usia tidak masuk akal", "Dikoreksi ke NaN (baris dipertahankan)"],
    ["Perjalanan tanpa tap-out", "Ditandai; tetap dipakai untuk model demand (basis tap-in)"],
  ];
  steps.forEach((st, i) => {
    const y = 4.1 + i * 0.72;
    badge(s, 0.62, y, String(i + 1));
    s.addText([{ text: st[0] + " — ", options: { bold: true, color: NAVY } }, { text: st[1], options: { color: GRAY } }], { x: 1.3, y: y + 0.02, w: 11.3, h: 0.5, fontSize: 13.5, fontFace: BFONT, valign: "middle", margin: 0 });
  });
  s.addNotes("Validasi kelengkapan + empat langkah pembersihan terdokumentasi dengan log before/after (bukti Unit 6).");
}

// =================== SLIDE 8 — FEATURE ENGINEERING ===================
{
  const s = p.addSlide(); bg(s, NAVY);
  s.addText("Feature Engineering", { x: 0.6, y: 0.42, w: 12, h: 0.7, fontSize: 30, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
  s.addText("CRISP-DM 3 — Konstruksi Data · SKKNI Unit 7", { x: 0.62, y: 1.12, w: 12, h: 0.4, fontSize: 14, italic: true, color: ORANGE, fontFace: BFONT, margin: 0 });
  const feats = [
    ["🕐 Fitur Waktu", "hour · day_of_week · day_name · is_weekend · is_peak · part_of_day · week_of_month"],
    ["🚌 Fitur Koridor", "corridorID (target-encoded, cross-fitted) · corridor_type (one-hot)"],
    ["⚙️ Transformasi", "Agregasi ke (koridor × tanggal × jam) → target passenger_count = 61.730 slot"],
  ];
  feats.forEach((f, i) => {
    const y = 1.85 + i * 1.4;
    card(s, 0.6, y, 12.1, 1.2, i === 2 ? BLUE : WHITE);
    const col = i === 2 ? WHITE : NAVY, sub = i === 2 ? "E6ECF5" : GRAY;
    s.addText(f[0], { x: 0.9, y: y + 0.18, w: 4.0, h: 0.5, fontSize: 17, bold: true, color: col, fontFace: BFONT, margin: 0 });
    s.addText(f[1], { x: 4.9, y: y + 0.18, w: 7.6, h: 0.85, fontSize: 13.5, color: sub, fontFace: BFONT, valign: "middle", margin: 0 });
  });
  card(s, 0.6, 6.15, 12.1, 0.85, "24344F");
  s.addText([
    { text: "🛡️ Anti-kebocoran: ", options: { bold: true, color: ORANGE } },
    { text: "fitur demografi per-slot sengaja diabaikan (baru diketahui setelah tap); demand historis koridor ditangani TargetEncoder ber-cross-fitting, bukan rata-rata manual.", options: { color: "CADCFC" } },
  ], { x: 0.85, y: 6.28, w: 11.6, h: 0.6, fontSize: 12.5, fontFace: BFONT, valign: "middle", margin: 0 });
  s.addNotes("Fitur waktu & koridor. Penekanan pada strategi anti-kebocoran — poin penting saat asesmen.");
}

// =================== SLIDE 9 — SKENARIO PEMODELAN ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Skenario Pemodelan", "CRISP-DM 4 — Modeling · SKKNI Unit 8 & 9");
  s.addText("Tujuh model kandidat dibandingkan pada pipeline & split identik (80/20), diseleksi via cross-validation 3-fold, lalu pemenang dioptimasi (RandomizedSearchCV).", { x: 0.6, y: 1.7, w: 12.1, h: 0.7, fontSize: 14.5, color: NAVY, fontFace: BFONT, margin: 0 });
  const models = ["Baseline (Rata-rata)", "Regresi Linier", "Ridge", "Decision Tree", "Random Forest", "Gradient Boosting", "XGBoost (Poisson)"];
  models.forEach((m, i) => {
    const x = 0.6 + (i % 4) * 3.05, y = 2.6 + Math.floor(i / 4) * 1.15;
    const best = i === 6;
    card(s, x, y, 2.85, 0.95, best ? ORANGE : LIGHT);
    s.addText(m, { x: x + 0.1, y, w: 2.65, h: 0.95, align: "center", valign: "middle", fontSize: 13.5, bold: best, color: best ? WHITE : NAVY, fontFace: BFONT, margin: 0 });
  });
  card(s, 9.75, 3.75, 2.95, 2.3, NAVY);
  s.addText("⭐ Pemenang", { x: 9.75, y: 3.95, w: 2.95, h: 0.4, align: "center", fontSize: 14, bold: true, color: ORANGE, fontFace: BFONT, margin: 0 });
  s.addText("XGBoost", { x: 9.75, y: 4.35, w: 2.95, h: 0.5, align: "center", fontSize: 22, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
  s.addText("objective =\ncount:poisson", { x: 9.75, y: 4.95, w: 2.95, h: 0.7, align: "center", fontSize: 13, color: "CADCFC", italic: true, fontFace: BFONT, margin: 0 });
  s.addText("Objektif Poisson dipilih karena target berupa data cacah (count) — lebih tepat secara statistik dan tak menghasilkan prediksi negatif.", { x: 0.6, y: 4.05, w: 8.9, h: 1.9, fontSize: 14, color: GRAY, fontFace: BFONT, valign: "top", margin: 0 });
  s.addNotes("Tujuh model dibandingkan secara adil; XGBoost Poisson menang. Objektif Poisson tepat untuk data cacah.");
}

// =================== SLIDE 10 — PERBANDINGAN MODEL ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Perbandingan Model & Pemilihan Terbaik", "SKKNI Unit 9 — evaluasi adil antar kandidat");
  s.addImage({ path: A("fig_model_comp.png"), x: 0.5, y: 1.7, w: 7.6, h: 4.26 });
  const rows = [["XGBoost", "0,735"], ["Random Forest", "0,727"], ["Gradient Boosting", "0,687"], ["Decision Tree", "0,664"], ["Regresi Linier", "0,420"]];
  s.addText("Test R² per Model", { x: 8.4, y: 1.85, w: 4.3, h: 0.4, fontSize: 16, bold: true, color: NAVY, fontFace: HFONT, margin: 0 });
  rows.forEach((r, i) => {
    const y = 2.45 + i * 0.75;
    card(s, 8.4, y, 4.3, 0.62, i === 0 ? ORANGE : LIGHT);
    s.addText(r[0], { x: 8.6, y, w: 2.9, h: 0.62, valign: "middle", fontSize: 13.5, bold: i === 0, color: i === 0 ? WHITE : NAVY, fontFace: BFONT, margin: 0 });
    s.addText(r[1], { x: 11.3, y, w: 1.2, h: 0.62, align: "center", valign: "middle", fontSize: 15, bold: true, color: i === 0 ? WHITE : BLUE, fontFace: HFONT, margin: 0 });
  });
  s.addText("Model tree-based mengungguli regresi linier karena hubungan fitur–target non-linier (efek jam & hari).", { x: 8.4, y: 6.25, w: 4.3, h: 0.7, fontSize: 11.5, italic: true, color: GRAY, fontFace: BFONT, margin: 0 });
  s.addNotes("XGBoost unggul pada semua metrik. Model non-linier jauh melampaui regresi linier.");
}

// =================== SLIDE 11 — EVALUASI ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Evaluasi Model pada Data Hold-out", "CRISP-DM 5 — Evaluation · SKKNI Unit 10");
  const kpis = [["0,715", "R² (Test)"], ["1,05", "MAE (pnp)"], ["1,47", "RMSE (pnp)"]];
  kpis.forEach((k, i) => {
    const x = 0.6 + i * 2.05;
    card(s, x, 1.7, 1.85, 1.4, NAVY);
    s.addText(k[0], { x, y: 1.9, w: 1.85, h: 0.6, align: "center", fontSize: 24, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
    s.addText(k[1], { x, y: 2.55, w: 1.85, h: 0.4, align: "center", fontSize: 12, color: "CADCFC", fontFace: BFONT, margin: 0 });
  });
  s.addImage({ path: A("fig_pred_actual.png"), x: 0.5, y: 3.3, w: 6.2, h: 3.47 });
  s.addImage({ path: A("fig_residual.png"), x: 6.9, y: 3.3, w: 6.0, h: 3.36 });
  s.addText("Titik mengumpul di sekitar garis ideal; residual terpusat di nol tanpa bias sistematis.", { x: 6.85, y: 1.9, w: 6.0, h: 1.1, fontSize: 13.5, color: GRAY, italic: true, fontFace: BFONT, valign: "middle", margin: 0 });
  s.addNotes("Metrik hold-out; prediksi vs aktual dan distribusi residual menunjukkan model tak bias.");
}

// =================== SLIDE 12 — FEATURE IMPORTANCE ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Faktor Pendorong Permintaan", "Feature Importance — Hipotesis H4 terbukti");
  s.addImage({ path: A("fig_importance.png"), x: 0.5, y: 1.7, w: 7.4, h: 4.14 });
  card(s, 8.2, 1.9, 4.6, 4.3, LIGHT);
  s.addText("💡 Insight", { x: 8.45, y: 2.1, w: 4.2, h: 0.4, fontSize: 17, bold: true, color: BLUE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Fitur waktu mendominasi", options: { bold: true, color: NAVY, breakLine: true } },
    { text: "is_weekend, day_of_week, part_of_day, dan hour adalah pendorong utama demand.", options: { color: GRAY, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "H4 terkonfirmasi", options: { bold: true, color: ORANGE, breakLine: true } },
    { text: "Pola temporal jauh lebih menentukan daripada demografi — sejalan dengan objektif bisnis penjadwalan armada.", options: { color: GRAY } },
  ], { x: 8.45, y: 2.6, w: 4.2, h: 3.4, fontSize: 14, fontFace: BFONT, paraSpaceAfter: 6, valign: "top", margin: 0 });
  s.addNotes("Feature importance mengonfirmasi H4: fitur waktu paling berpengaruh, mendukung keputusan penjadwalan.");
}

// =================== SLIDE 13 — REVIEW PEMODELAN ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Review Proses Pemodelan", "CRISP-DM 5 — SKKNI Unit 11");
  card(s, 0.6, 1.75, 6.0, 2.3, LIGHT);
  s.addText("✅ Kesesuaian & Kualitas", { x: 0.85, y: 1.95, w: 5.5, h: 0.4, fontSize: 16, bold: true, color: BLUE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Seluruh tahap CRISP-DM sesuai rencana", options: { bullet: true, breakLine: true } },
    { text: "Reproducible (random_state), perbandingan adil", options: { bullet: true, breakLine: true } },
    { text: "Pemilihan model berbasis CV, bukan test tunggal", options: { bullet: true, breakLine: true } },
    { text: "Evaluasi jujur: target R²≥0,80 dilaporkan tak tercapai", options: { bullet: true } },
  ], { x: 0.9, y: 2.45, w: 5.4, h: 1.5, fontSize: 12.5, color: NAVY, fontFace: BFONT, paraSpaceAfter: 5, margin: 0 });
  card(s, 6.8, 1.75, 5.9, 2.3, NAVY);
  s.addText("🔎 Temuan Kontrol Kualitas", { x: 7.05, y: 1.95, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: ORANGE, fontFace: BFONT, margin: 0 });
  s.addText("Ditemukan & diperbaiki: TargetEncoder mode auto salah mendeteksi target cacah sebagai multiclass (koridor meledak jadi 55 kolom → potensi bocor). Dikoreksi dengan target_type='continuous' lalu dilatih ulang.", { x: 7.05, y: 2.45, w: 5.4, h: 1.5, fontSize: 13, color: "CADCFC", fontFace: BFONT, valign: "top", margin: 0 });
  card(s, 0.6, 4.35, 12.1, 2.15, LIGHT);
  s.addText("⚠️ Keterbatasan & Pengembangan", { x: 0.85, y: 4.55, w: 11.5, h: 0.4, fontSize: 16, bold: true, color: BLUE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Data hanya 1 bulan → belum menangkap musiman tahunan / hari libur nasional", options: { bullet: true, breakLine: true } },
    { text: "Granularitas koridor-jam memiliki batas bawah noise Poisson (rata-rata cacah ~3) → R² 0,80 sulit dilampaui", options: { bullet: true, breakLine: true } },
    { text: "Pengembangan: data multi-bulan, fitur eksternal (cuaca, hari libur, event), uji model deret waktu", options: { bullet: true } },
  ], { x: 0.9, y: 5.05, w: 11.6, h: 1.4, fontSize: 13, color: NAVY, fontFace: BFONT, paraSpaceAfter: 6, margin: 0 });
  s.addNotes("Review Unit 11: proses sesuai & berkualitas; contoh kontrol kualitas menemukan bug leakage; keterbatasan diakui jujur.");
}

// =================== SLIDE 14 — REKOMENDASI BISNIS ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Insight Bisnis & Rekomendasi Actionable", "Dari analisis menuju keputusan operasional");
  const recs = [
    ["🚍", "Penjadwalan Dinamis Armada", "Perbanyak frekuensi di jam & koridor puncak, kurangi saat lengang"],
    ["👷", "Alokasi Petugas Berbasis Prediksi", "Tempatkan SDM pada slot koridor-jam berdemand tinggi"],
    ["📅", "Manajemen Akhir Pekan", "Sesuaikan operasi mengikuti pola akhir pekan yang jauh lebih rendah"],
    ["🏗️", "Prioritas Halte Padat", "Fokus perbaikan kapasitas pada klaster halte tersibuk"],
  ];
  recs.forEach((r, i) => {
    const y = 1.85 + i * 1.2;
    card(s, 0.6, y, 12.1, 1.05, i % 2 === 0 ? LIGHT : WHITE);
    s.addShape(p.ShapeType.ellipse, { x: 0.85, y: y + 0.22, w: 0.62, h: 0.62, fill: { color: i % 2 === 0 ? BLUE : ORANGE }, line: { type: "none" } });
    s.addText(r[0], { x: 0.85, y: y + 0.22, w: 0.62, h: 0.62, align: "center", valign: "middle", fontSize: 20, margin: 0 });
    s.addText(r[1], { x: 1.7, y: y + 0.14, w: 10.7, h: 0.45, fontSize: 16, bold: true, color: NAVY, fontFace: BFONT, margin: 0 });
    s.addText(r[2], { x: 1.7, y: y + 0.56, w: 10.7, h: 0.4, fontSize: 13, color: GRAY, fontFace: BFONT, margin: 0 });
  });
  s.addNotes("Empat rekomendasi bisnis yang dapat langsung ditindaklanjuti dari hasil model & EDA.");
}

// =================== SLIDE 15 — DEPLOYMENT ===================
{
  const s = p.addSlide(); bg(s, WHITE);
  title(s, "Deployment — Aplikasi Streamlit Interaktif", "CRISP-DM 6 — Deployment");
  const pages = ["🏠 Beranda", "📂 Dataset & Telaah", "✅ Kualitas Data", "🔍 EDA Interaktif", "🗺️ Peta Geospasial", "🤖 Pemodelan", "🎯 Simulasi Prediksi", "📌 Kesimpulan"];
  s.addText("8 halaman interaktif mengikuti alur CRISP-DM:", { x: 0.6, y: 1.7, w: 6.0, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: BFONT, margin: 0 });
  pages.forEach((pg, i) => {
    const y = 2.25 + i * 0.55;
    s.addShape(p.ShapeType.roundRect, { x: 0.6, y, w: 5.7, h: 0.46, fill: { color: i % 2 ? WHITE : LIGHT }, line: { color: LIGHT, width: 1 }, rectRadius: 0.06 });
    s.addText(pg, { x: 0.8, y, w: 5.4, h: 0.46, valign: "middle", fontSize: 13.5, color: NAVY, fontFace: BFONT, margin: 0 });
  });
  card(s, 6.7, 1.7, 6.0, 5.1, NAVY);
  s.addText("Arsitektur Deploy", { x: 6.95, y: 1.95, w: 5.5, h: 0.4, fontSize: 17, bold: true, color: ORANGE, fontFace: BFONT, margin: 0 });
  s.addText([
    { text: "Model dilatih offline → disimpan demand_model.pkl", options: { bullet: true, breakLine: true } },
    { text: "Aplikasi hanya memuat artefak → ringan & cepat", options: { bullet: true, breakLine: true } },
    { text: "Caching Streamlit (@st.cache_data / _resource)", options: { bullet: true, breakLine: true } },
    { text: "Tema konsisten biru–putih–jingga", options: { bullet: true, breakLine: true } },
    { text: "Deploy gratis ke Streamlit Community Cloud", options: { bullet: true } },
  ], { x: 7.0, y: 2.55, w: 5.4, h: 2.4, fontSize: 14, color: "CADCFC", fontFace: BFONT, paraSpaceAfter: 9, margin: 0 });
  s.addShape(p.ShapeType.roundRect, { x: 6.95, y: 5.55, w: 5.5, h: 0.95, fill: { color: ORANGE }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("🎯 Fitur unggulan: Simulasi prediksi real-time\npilih koridor + hari + jam → estimasi penumpang", { x: 6.95, y: 5.55, w: 5.5, h: 0.95, align: "center", valign: "middle", fontSize: 12.5, bold: true, color: WHITE, fontFace: BFONT, margin: 0 });
  s.addNotes("Aplikasi 8 halaman. Arsitektur: model offline, app memuat artefak. Demo fitur simulasi real-time.");
}

// =================== SLIDE 16 — PENUTUP ===================
{
  const s = p.addSlide(); bg(s, NAVY);
  s.addShape(p.ShapeType.ellipse, { x: -1.3, y: 5.0, w: 4.0, h: 4.0, fill: { color: BLUE }, line: { type: "none" } });
  s.addShape(p.ShapeType.ellipse, { x: 11.5, y: -1.3, w: 3.4, h: 3.4, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText("Kesimpulan", { x: 0.7, y: 1.1, w: 12, h: 0.9, fontSize: 40, bold: true, color: WHITE, fontFace: HFONT, margin: 0 });
  s.addText([
    { text: "Pola permintaan TransJakarta digerakkan fitur temporal (jam & hari).", options: { bullet: true, color: "CADCFC", breakLine: true } },
    { text: "Model XGBoost-Poisson mencapai R² 0,715 & MAE 1,05 pnp — memadai untuk perencanaan.", options: { bullet: true, color: "CADCFC", breakLine: true } },
    { text: "Seluruh 11 unit kompetensi SKKNI tercakup dalam alur CRISP-DM.", options: { bullet: true, color: "CADCFC", breakLine: true } },
    { text: "Deliverable: skrip Python modular + aplikasi Streamlit interaktif + presentasi ini.", options: { bullet: true, color: "CADCFC" } },
  ], { x: 0.75, y: 2.3, w: 11.4, h: 2.6, fontSize: 16, fontFace: BFONT, paraSpaceAfter: 12, margin: 0 });
  s.addShape(p.ShapeType.roundRect, { x: 0.72, y: 5.3, w: 4.6, h: 0.6, fill: { color: ORANGE }, line: { type: "none" }, rectRadius: 0.3 });
  s.addText("Terima kasih 🙏", { x: 0.72, y: 5.3, w: 4.6, h: 0.6, align: "center", valign: "middle", fontSize: 16, bold: true, color: WHITE, fontFace: BFONT, margin: 0 });
  s.addText("Mohammad Yusuf  ·  Sertifikasi Ilmuwan Data (Data Scientist) — DSS.01.00.23", { x: 0.75, y: 6.5, w: 12, h: 0.4, fontSize: 13, color: GRAY, fontFace: BFONT, margin: 0 });
  s.addNotes("Penutup: rangkuman pencapaian, cakupan SKKNI, dan deliverable. Ucapan terima kasih.");
}

p.writeFile({ fileName: "TransJakarta_Demand_Prediction_BNSP.pptx" }).then((f) => console.log("Deck tersimpan:", f));
