# 🎤 Narasi Presentasi — TransJakarta Demand Prediction
### Portofolio Asesmen Data Scientist BNSP · Mohammad Yusuf

> **Cara pakai dokumen ini.** Setiap slide punya tiga bagian: **[Layar]** (apa yang tampak),
> **Naskah** (yang Anda ucapkan — boleh diparafrase, jangan dihafal kaku), dan **[Tips]**.
> Total presentasi ± **13–16 menit** + **live demo 4–5 menit**. Bicara tenang, jeda setelah
> poin penting, dan selalu hubungkan *teknis → nilai bisnis*.

---

## 🎯 Panduan Umum Sebelum Mulai
- **Sikap:** percaya diri, tenang, kontak mata. Anda adalah pemilik proyek ini.
- **Alur cerita:** Masalah → Data → Analisis → Model → Hasil → Dampak. Jaga benang merah ini.
- **Kata kunci yang menunjukkan kematangan:** *"anti-kebocoran data"*, *"dipilih berdasarkan cross-validation"*, *"saya laporkan apa adanya"*, *"perspektif perencanaan transportasi"*.
- **Jangan** membaca slide kata per kata — slide adalah pendukung, Anda adalah narasinya.

---

# BAGIAN 1 — NARASI PER SLIDE

## Slide 1 — Cover
**[Layar]** Judul proyek, nama Anda, skema sertifikasi.
**Naskah (±25 dtk):**
> "Selamat pagi/siang, Bapak/Ibu Asesor. Perkenalkan, saya Mohammad Yusuf. Pada kesempatan ini
> saya akan mempresentasikan portofolio proyek data science saya yang berjudul **TransJakarta
> Passenger Analytics and Demand Prediction** — sebuah proyek untuk menganalisis pola penumpang
> dan memprediksi permintaan transportasi publik menggunakan machine learning. Seluruh proyek ini
> saya kerjakan mengikuti metodologi standar industri, yaitu **CRISP-DM**."

**[Tips]** Buka dengan senyum dan tempo santai. Ini menentukan kesan pertama.

---

## Slide 2 — Latar Belakang & Permasalahan Bisnis
**[Layar]** Tiga masalah + empat statistik dataset.
**Naskah (±45 dtk):**
> "Kita mulai dari **masalahnya**. TransJakarta melayani jutaan perjalanan setiap bulan. Namun ada
> ketidakseimbangan klasik: pada jam sibuk penumpang menumpuk karena armada tidak cukup, sementara
> di jam lengang justru banyak armada berjalan hampir kosong. Petugas pun sering ditempatkan tanpa
> dasar data. **Akar masalahnya satu:** operator tidak punya estimasi permintaan yang andal.
> Untuk menjawab ini, saya menggunakan data nyata sebanyak **189.500 transaksi tap** dari **10.000
> kartu** di **216 koridor** sepanjang April 2023."

**[Tips]** Tekankan angka 189.500 — menunjukkan proyek berbasis data skala nyata.

---

## Slide 3 — Objektif Bisnis, Metrik Sukses & Tujuan Teknis
**[Layar]** Objektif bisnis, tujuan teknis, tiga metrik sukses (semua ✓).
**Naskah (±50 dtk):**
> "Dari masalah tadi, saya turunkan **tiga objektif bisnis**: memahami pola pergerakan penumpang,
> membangun model prediksi jumlah penumpang, dan menyediakan alat bantu keputusan yang interaktif.
> Secara **teknis**, ini saya rumuskan sebagai *supervised regression* — memprediksi jumlah penumpang
> pada level agregasi koridor per jam. Yang penting bagi asesor: saya menetapkan **metrik kesuksesan
> di awal**, sebelum modeling. Metrik operasional MAE di bawah 1,5 penumpang — tercapai di 1,05.
> Metrik statistik R² minimal 0,70 — tercapai 0,715. Dan model harus mengungguli baseline — juga
> tercapai. Jadi keberhasilan proyek ini terukur, bukan klaim."

**[Tips]** Ini menyentuh **SKKNI Unit 1 & 2**. Kalimat "metrik ditetapkan di awal" sangat dihargai asesor.

---

## Slide 4 — Dataset & Telaah Data
**[Layar]** Enam kelompok kolom + temuan penting.
**Naskah (±45 dtk):**
> "Mari telaah datanya. Data ini kaya: ada **demografi** penumpang, **koridor**, **geolokasi** halte
> asal dan tujuan, **waktu** tap, dan **tarif**. Yang ingin saya soroti — dan ini bukti ketelitian —
> saya menemukan dua hal saat telaah. Pertama, kolom **durasi perjalanan ternyata acak**: korelasinya
> dengan jarak nyaris nol. Maka saya **tidak** menjadikannya target, karena tidak mungkin dipelajari.
> Kedua, **tarif bersifat deterministik** dari jenis koridor, sehingga saya pakai hanya untuk analisis,
> bukan sebagai prediktor. Keputusan ini menyelamatkan proyek dari model yang menyesatkan."

**[Tips]** Ini **SKKNI Unit 3**. Menunjukkan Anda *memahami* data, bukan sekadar memakainya.

---

## Slide 5 — Pola Permintaan Penumpang (EDA)
**[Layar]** Grafik pola per jam + hari kerja vs akhir pekan.
**Naskah (±40 dtk):**
> "Dari eksplorasi data, dua pola langsung terlihat kuat. **Pertama**, permintaan bersifat *bimodal* —
> memuncak tajam pada jam 6–7 pagi dan 16–17 sore, persis pola komuter berangkat dan pulang kerja.
> **Kedua**, hari kerja sekitar **3,7 kali lebih ramai** daripada akhir pekan. Dua pola ini nanti
> menjadi sinyal utama yang dipelajari model."

**[Tips]** Tunjuk puncak jingga di grafik saat bilang "jam 6–7 dan 16–17".

---

## Slide 6 — Konsentrasi Koridor & Kepadatan Waktu
**[Layar]** Koridor tersibuk + heatmap jam×hari.
**Naskah (±35 dtk):**
> "Berikutnya, distribusi koridor bersifat *long-tail* — artinya **sebagian kecil koridor menyerap
> mayoritas penumpang**. Heatmap di sebelah kanan mempertegasnya: blok tergelap terkonsentrasi di
> jam sibuk hari kerja. Bagi operator, ini langsung menunjukkan **di mana dan kapan** sumber daya
> paling dibutuhkan."

---

## Slide 7 — Analisis Origin-Destination (OD)
**[Layar]** Konsep bangkitan/tarikan + grafik net flow.
**Naskah (±55 dtk):**
> "Slide ini adalah nilai tambah proyek saya dari sisi **perencanaan transportasi**. Saya tidak berhenti
> di statistik umum, tapi masuk ke analisis **Origin-Destination**. Dua konsep kuncinya: **Bangkitan
> atau produksi** — perjalanan yang berangkat dari sebuah halte; dan **Tarikan atau atraksi** —
> perjalanan yang menuju sebuah halte. Dari selisih keduanya — *net flow* — saya bisa mengklasifikasi
> setiap halte. Yang menarik, hasilnya **masuk akal secara nyata**: halte seperti **Terminal Senen,
> Tanah Abang, dan Ragunan** muncul sebagai *penarik* — memang pusat kegiatan dan terminal. Sementara
> kawasan permukiman seperti **Penjaringan** menjadi *penghasil* perjalanan. Informasi ini konkret:
> ia memandu di mana armada harus disiapkan pada jam berangkat."

**[Tips]** Ini pembeda portofolio Anda. Sampaikan dengan bangga — ini menunjukkan Anda paham *domain*, bukan hanya *algoritma*.

---

## Slide 8 — Validasi & Pembersihan Data
**[Layar]** Empat indikator kualitas + empat langkah pembersihan.
**Naskah (±45 dtk):**
> "Sebelum modeling, data harus bersih dan tervalidasi. Hasil validasi: **81% baris lengkap**, **nol
> duplikat**, koordinat semuanya valid. Untuk masalah yang ada, saya terapkan strategi eksplisit —
> misalnya koridor kosong saya isi label 'Unknown' agar tetap bisa diagregasi, dan perjalanan tanpa
> tap-out tetap saya pakai untuk model demand karena model ini berbasis tap-in. Yang penting, **setiap
> langkah saya dokumentasikan dengan log sebelum-dan-sesudah**, sehingga seluruh proses dapat ditelusuri."

**[Tips]** Ini **SKKNI Unit 4–6**. "Log sebelum-dan-sesudah" adalah frasa emas.

---

## Slide 9 — Feature Engineering
**[Layar]** Tiga kelompok fitur + kotak anti-kebocoran.
**Naskah (±50 dtk):**
> "Inilah jantung persiapan model — *feature engineering*. Saya membangun **fitur waktu** seperti jam,
> hari, akhir pekan, dan jam sibuk; serta **fitur koridor**. Data saya agregasi ke level koridor per
> tanggal per jam, menghasilkan 61.730 baris. Tapi poin paling penting ada di kotak bawah:
> **anti-kebocoran data**. Saya sengaja **tidak** memakai fitur demografi per-slot sebagai prediktor,
> karena informasi itu baru diketahui *setelah* penumpang tap — itu artinya bagian dari jawaban.
> Dan demand historis koridor saya tangani dengan *target encoding ber-cross-fitting*, bukan rata-rata
> manual yang bisa bocor. Kedisiplinan inilah yang menjaga model tetap jujur."

**[Tips]** **SKKNI Unit 7**. Konsep anti-kebocoran adalah penanda data scientist yang matang — tekankan.

---

## Slide 10 — Skenario Pemodelan
**[Layar]** Tujuh model + kartu pemenang XGBoost.
**Naskah (±45 dtk):**
> "Saya tidak langsung memilih satu model, tapi **membandingkan tujuh kandidat** — dari baseline dan
> regresi linier hingga Random Forest dan XGBoost — pada pipeline dan pembagian data yang identik.
> Skenario ujinya *cross-validation* 3-fold, dengan metrik R², MAE, RMSE, dan MAPE. Pemenangnya
> **XGBoost dengan objektif Poisson**. Saya memilih objektif Poisson secara sadar, karena target saya
> adalah **data cacah** — jumlah penumpang — dan Poisson secara statistik tepat untuk itu, sekaligus
> menjamin prediksi tidak pernah negatif."

**[Tips]** **SKKNI Unit 8 & 9**. "Objektif Poisson untuk data cacah" menunjukkan pemahaman statistik, bukan asal pakai library.

---

## Slide 11 — Perbandingan Model & Pemilihan Terbaik
**[Layar]** Grafik perbandingan + tabel R².
**Naskah (±35 dtk):**
> "Ini hasil perbandingannya secara transparan. XGBoost unggul di semua metrik dengan R² 0,735 pada
> perbandingan awal. Terlihat jelas model *tree-based* jauh mengungguli regresi linier — ini masuk akal,
> karena hubungan antara waktu dan permintaan bersifat **non-linier**. Pemilihan pemenang pun saya
> dasarkan pada skor **cross-validation**, bukan satu kali tes yang bisa kebetulan bagus."

**[Tips]** Frasa "berdasarkan cross-validation, bukan satu kali tes" menunjukkan Anda paham risiko overfitting seleksi.

---

## Slide 12 — Evaluasi Model pada Data Hold-out
**[Layar]** KPI R²/MAE/RMSE + scatter prediksi-vs-aktual + residual.
**Naskah (±40 dtk):**
> "Model final saya uji pada **data hold-out** yang belum pernah dilihat saat pelatihan. Hasilnya
> R² **0,715** dan MAE **1,05 penumpang**. Pada grafik kiri, titik-titik mengumpul di sekitar garis
> ideal, dan pada grafik kanan, residual terpusat di nol — artinya model **tidak bias sistematis**,
> tidak konsisten terlalu tinggi atau terlalu rendah."

**[Tips]** **SKKNI Unit 10**. Tunjuk garis diagonal dan puncak residual di nol.

---

## Slide 13 — Faktor Pendorong Permintaan (Feature Importance)
**[Layar]** Grafik importance + kotak insight H4.
**Naskah (±35 dtk):**
> "Model yang baik harus bisa dijelaskan. Feature importance mengonfirmasi hipotesis awal saya:
> **fitur waktu mendominasi** — akhir pekan, hari, bagian hari, dan jam adalah pendorong utama.
> Ini bukan sekadar angka; ia **sejalan dengan objektif bisnis** — bahwa permintaan digerakkan oleh
> ritme waktu, sehingga solusinya adalah penjadwalan armada berbasis waktu."

---

## Slide 14 — Review Proses Pemodelan
**[Layar]** Kesesuaian, temuan kontrol kualitas, keterbatasan.
**Naskah (±55 dtk):**
> "Bagian ini menunjukkan kejujuran dan kontrol kualitas saya. Saat review, saya **menemukan dan
> memperbaiki sebuah bug penting**: encoder default salah menganggap target cacah sebagai kategori,
> yang membuat fitur koridor membengkak dan berpotensi bocor. Saya perbaiki dan latih ulang. Saya juga
> **jujur soal keterbatasan**: target aspiratif R² 0,80 tidak tercapai. Alasannya bukan model yang
> lemah, tapi karena pada granularitas koridor-per-jam rata-rata jumlahnya kecil, sehingga ada
> **batas bawah noise statistik** yang alami. Untuk pengembangan, saya usulkan data multi-bulan dan
> fitur eksternal seperti cuaca dan hari libur."

**[Tips]** **SKKNI Unit 11.** Asesor **sangat** menghargai kejujuran ini. Jangan sembunyikan bahwa 0,80 tidak tercapai — justru jadikan bukti kematangan.

---

## Slide 15 — Insight Bisnis & Rekomendasi
**[Layar]** Empat rekomendasi actionable.
**Naskah (±40 dtk):**
> "Semua analisis ini bermuara pada rekomendasi yang **bisa langsung ditindaklanjuti**: satu,
> penjadwalan dinamis armada mengikuti jam dan koridor puncak; dua, penempatan petugas berdasarkan
> prediksi dan titik bangkitan; tiga, penyesuaian operasi akhir pekan; dan empat, prioritas perbaikan
> kapasitas pada halte tersibuk dan penarik utama. Inilah nilai bisnis dari proyek data science ini."

---

## Slide 16 — Deployment (👉 TITIK LIVE DEMO)
**[Layar]** Daftar 9 halaman + kurva simulasi 24 jam.
**Naskah penghubung (±20 dtk):**
> "Model yang baik tidak boleh berhenti di notebook. Saya sudah men-*deploy* seluruh analisis ini
> menjadi **aplikasi web interaktif dengan Streamlit**, terdiri dari sembilan halaman, dan sudah live
> di internet. **Daripada sekadar bercerita, izinkan saya menunjukkannya langsung.**"

👉 **BERALIH KE BROWSER / LIVE DEMO** (lihat Bagian 2 di bawah).

---

## Slide 17 — Kesimpulan (setelah kembali dari demo)
**[Layar]** Empat poin kesimpulan + terima kasih.
**Naskah (±35 dtk):**
> "Sebagai penutup: permintaan TransJakarta digerakkan oleh pola waktu; analisis OD mengungkap halte
> penghasil dan penarik untuk penempatan sumber daya; model XGBoost-Poisson mencapai akurasi yang
> memadai untuk perencanaan; dan seluruh sebelas unit kompetensi SKKNI tercakup dalam alur CRISP-DM
> proyek ini — mulai dari objektif bisnis hingga deployment. Demikian presentasi saya. **Terima kasih**,
> dan saya siap menerima pertanyaan."

**[Tips]** Akhiri dengan tenang dan penuh keyakinan. Diam sejenak sebelum "Terima kasih".

---

# BAGIAN 2 — NARASI LIVE DEMO STREAMLIT

> Dilakukan saat **Slide 16**. Buka aplikasi live di **https://bnsp-dss-jul-26-yusuf.streamlit.app/**.
> Siapkan tab browser **sebelum** presentasi agar tidak menunggu *loading*. Durasi target **4–5 menit**.
> Prinsip: **klik → jeda → jelaskan**. Jangan klik terlalu cepat.

### Narasi Pembuka Demo (±15 dtk)
> "Ini aplikasinya. Di sebelah kiri ada navigasi sembilan halaman yang mengikuti alur CRISP-DM. Di
> panel ini juga langsung terlihat ringkasan model terbaik. Mari kita telusuri beberapa halaman kunci."

### 1. Halaman Beranda (±25 dtk)
> "Halaman Beranda merangkum keseluruhan proyek: total transaksi, akurasi model, latar belakang bisnis,
> metrik kesuksesan yang semuanya tercapai, dan alur CRISP-DM. Jadi siapa pun yang membuka aplikasi ini
> langsung paham konteksnya dalam sepuluh detik."

### 2. Halaman EDA Interaktif (±40 dtk)
> "Nah, ini yang membuatnya *interaktif*. Perhatikan filter di sini — saya bisa memilih jenis koridor,
> gender, atau rentang jam, dan **semua grafik langsung menyesuaikan**." *(Ubah satu filter, tunjuk
> grafik berubah.)* "Di sini terlihat jelas pola bimodal yang tadi saya sebutkan — dua puncak di pagi
> dan sore hari, serta perbedaan tajam antara hari kerja dan akhir pekan."

### 3. Halaman Analisis OD (±45 dtk)
> "Ini halaman favorit saya, dari sisi perencanaan transportasi. Di tab pertama, kita lihat **bangkitan
> dan tarikan** per halte. Grafik *net flow* ini menunjukkan halte biru sebagai penghasil perjalanan
> dan halte jingga sebagai penarik." *(Pindah ke tab Desire Lines.)* "Dan ini yang paling visual —
> **desire lines**, garis keinginan perjalanan. Setiap garis adalah pasangan asal-tujuan tersibuk;
> makin tebal, makin ramai. Ini memperlihatkan koridor pergerakan utama di jaringan secara langsung
> di atas peta."

### 4. Halaman Simulasi Prediksi (±60 dtk — KLIMAKS DEMO)
> "Dan inilah puncaknya — **simulasi prediksi**. Misalkan seorang perencana operasional ingin tahu:
> berapa penumpang di koridor tertentu, pada hari Senin, jam 7 pagi?" *(Pilih koridor, set hari Senin,
> jam 7.)* "Model langsung memberi estimasi, lengkap dengan perbandingan terhadap rata-rata historis.
> Tapi yang lebih kuat ada di bawah ini — **kurva prediksi sepanjang hari**." *(Tunjuk kurva.)*
> "Perhatikan, model menghasilkan **pola bimodal** dengan puncak di jam sibuk. Sekarang, mari saya
> ubah harinya menjadi **Minggu**." *(Ganti ke Minggu, kurva berubah jadi datar.)* "Kurvanya langsung
> menjadi **datar dan rendah** — persis perilaku akhir pekan. Ini bukti bahwa model benar-benar
> **menangkap ritme operasional nyata**, bukan sekadar menghasilkan satu angka."

**[Tips]** Bagian "ubah Senin → Minggu" adalah momen paling memukau. Lakukan perlahan, biarkan asesor melihat kurvanya berubah, lalu diam sejenak.

### Narasi Penutup Demo & Kembali ke PPT (±10 dtk)
> "Aplikasi ini juga menyediakan tombol unduh artefak dan dokumentasi lengkap. Baik, itu demonstrasinya —
> **izinkan saya kembali ke slide untuk menutup presentasi.**"

👉 **KEMBALI KE SLIDE 17.**

---

# BAGIAN 3 — ANTISIPASI PERTANYAAN ASESOR

Siapkan jawaban singkat untuk pertanyaan yang mungkin muncul:

**"Kenapa R² hanya 0,715, tidak lebih tinggi?"**
> "Karena analisisnya di level koridor-per-jam, di mana rata-rata jumlah penumpang kecil, sehingga ada
> batas bawah *noise* statistik yang alami — dikenal sebagai noise Poisson. R² 0,715 sudah sangat baik
> untuk data cacah bergranularitas halus. Metrik operasional yang lebih relevan, MAE, hanya 1 penumpang."

**"Kenapa memilih XGBoost, bukan model lain?"**
> "Saya tidak memilih di awal — saya bandingkan tujuh model secara adil, dan XGBoost menang di semua
> metrik lewat cross-validation. Saya juga memakai objektif Poisson karena targetnya data cacah."

**"Bagaimana Anda memastikan tidak terjadi kebocoran data (data leakage)?"**
> "Tiga cara: fitur demografi per-slot tidak dipakai karena baru diketahui setelah kejadian;
> target encoding dilakukan dengan cross-fitting; dan durasi/tarif tidak dipakai sebagai prediktor."

**"Apa manfaat nyata proyek ini bagi TransJakarta?"**
> "Prediksi demand memungkinkan penjadwalan armada dan penempatan petugas berbasis data, mengurangi
> penumpukan di jam sibuk sekaligus pemborosan di jam lengang. Analisis OD menambah dimensi *di mana*
> sumber daya harus disiapkan."

**"Apa yang akan Anda kembangkan jika ada waktu lebih?"**
> "Menambah data multi-bulan untuk menangkap musiman, memasukkan fitur eksternal seperti cuaca dan
> hari libur nasional, serta menguji model deret waktu seperti SARIMA atau Prophet."

**"Kenapa durasi perjalanan tidak diprediksi saja?"**
> "Saya sudah mengeceknya — durasi pada data ini tidak berkorelasi dengan jarak, korelasinya nyaris nol,
> yang menandakan datanya tidak mengandung sinyal yang bisa dipelajari. Memaksakannya justru akan
> menghasilkan model yang menyesatkan. Maka saya memilih target yang benar-benar dapat dipelajari."

---

## ✅ Checklist Kesiapan Presentasi
- [ ] Tab browser aplikasi live **sudah terbuka** dan halaman sudah termuat (hindari cold start).
- [ ] PPT dalam mode *Presenter View* agar bisa melihat catatan.
- [ ] Latihan transisi PPT ↔ demo minimal **1 kali**.
- [ ] Simulasi skenario "Senin → Minggu" sudah dicoba agar lancar.
- [ ] Total waktu diukur — target **≤ 20 menit** termasuk demo.
