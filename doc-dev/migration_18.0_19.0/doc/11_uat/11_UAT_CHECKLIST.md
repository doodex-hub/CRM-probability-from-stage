# UAT Checklist — Migrasi crm_probability_from_stage

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya dibanding sebelum migrasi (18.0), kecuali tidak ada satupun perubahan yang disengaja di project ini (murni port kode ke 19.0).
>
> **Dokumen ini didesain sebagai draft test script untuk dijalankan SENDIRI oleh business user/stakeholder (PM/FA/Sales Manager)** — AI tidak pernah mengisi kolom Actual/Status/Sign-off atas eksekusi tangannya sendiri.
>
> **WAIVER eksplisit (2026-08-26):** dev/pemilik project (kuncoro@doodex.net) secara sadar memutuskan MELEWATI eksekusi manual T-01 s.d. T-04 di bawah, dan menerima bukti test otomatis (Step 9 — `09_DEV_TESTING.md`, unit/integration/Tour, headless Chrome nyata bukan simulasi; Step 10 — `10_BUSINESS_FLOW_MIGRATION.md`) sebagai dasar penutupan gate ini. Kolom Actual/Status di bawah diisi **"Waived — diterima dari test otomatis"**, BUKAN "Pass" hasil klik manual — supaya siapapun baca dokumen ini nanti tahu persis apa yang sebenarnya terjadi (business user asli belum pernah mengklik langkah-langkah ini dengan tangan sendiri). Pola waiver ini konsisten dengan migrasi 17→18 modul yang sama (`doc-dev/_archive/migration_17.0_18.0/doc/11_uat/11_UAT_CHECKLIST.md`).

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `crm_probability_from_stage` versi 19.0 sudah terinstall dan bisa diakses di environment UAT.
- [ ] Login sebagai user Sales/Sales Manager (bukan cuma Administrator) — modul ini dipakai sehari-hari oleh role itu.
- [ ] Minimal 2 stage CRM tersedia dengan nilai Probability berbeda (mis. Stage "New" = 20%, Stage "Qualified" = 60%) — supaya perpindahan stage terlihat jelas efeknya.
- [ ] Database yang dipakai UAT sebaiknya salinan/staging, bukan database produksi asli.

## Skenario Test (Test Script)

### T-01: Mengatur nilai Probability per Stage & mengaktifkan fitur

**Data dummy yang perlu dientri:** Stage bernama "UAT Test Stage", Probability = 75.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Settings → CRM, cari pengaturan "Probability from stage", aktifkan (centang), klik Save | Pengaturan tersimpan, tidak ada error | Tour `crm_probability_settings_tour` mengklik checkbox yang SAMA + Save, dikonfirmasi tersimpan server-side (`get_param(...) == 'True'`) | [x] Waived — diterima dari Tour test |
| 2 | Buka Settings → CRM → Stages, buat stage baru bernama "UAT Test Stage" | Stage berhasil dibuat | Unit test `setUpClass` membuat `stage_a`/`stage_b` via mekanisme create yang sama; Tour pipeline membuat stage "QA Tour High" | [x] Waived — diterima dari unit test + Tour test |
| 3 | Di form stage yang baru dibuat, cari field "Probability" (angka + tanda %) | Field terlihat (karena pengaturan di langkah 1 aktif) | Unit test `test_show_probability_computed` mengonfirmasi nilai computed `show_probability` benar saat toggle aktif; Code Review Step 8 mengonfirmasi xpath `invisible="not show_probability"` tetap resolve benar di 19.0 (DIFF-04) | [x] Waived — diterima dari unit test + code review |
| 4 | Isi field Probability dengan angka 75, Save | Nilai 75 tersimpan tanpa error | Unit test `test_stage_probability_no_range_validation` menyimpan nilai -50/150 tanpa error (mekanisme simpan generik, angka 75 pasti tersimpan juga) | [x] Waived — diterima dari unit test |
| 5 | Matikan kembali pengaturan "Probability from stage" di Settings → CRM, Save | Pengaturan tersimpan | Sama seperti baris 1 (toggle dua arah, Tour + unit test `test_toggle_saves_config_parameter`) | [x] Waived — diterima dari Tour test + unit test |
| 6 | Buka lagi stage "UAT Test Stage" | Field "Probability" TIDAK terlihat lagi | Unit test `test_show_probability_computed` mengonfirmasi cabang toggle OFF (`assertFalse`) | [x] Waived — diterima dari unit test |
| 7 | Aktifkan lagi pengaturan "Probability from stage" (persiapan T-02) | Pengaturan aktif | Sama seperti baris 1 | [x] Waived — diterima dari Tour test |

### T-02: Probability opportunity mengikuti Stage saat pipeline berjalan

**Data dummy yang perlu dientri:** Opportunity bernama "UAT Test Opportunity", Expected Revenue = 5000.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka app CRM → Pipeline (kanban) | Pipeline terbuka normal | Tour `crm_probability_pipeline_tour` membuka app CRM (`showAppsMenuItem()` + klik) sukses sebagai langkah awal, PASS | [x] Waived — diterima dari Tour test |
| 2 | Buat opportunity baru "UAT Test Opportunity", Expected Revenue = 5000, taruh di stage manapun | Opportunity berhasil dibuat, muncul di kanban | Tour melakukan mekanisme identik (quick-create kanban, isi nama + expected revenue 1000 — angka contoh beda, mekanisme sama), PASS | [x] Waived — diterima dari Tour test (angka contoh berbeda, mekanisme identik) |
| 3 | Catat nilai Probability opportunity ini saat ini (bisa dilihat di form opportunity) | — | — | — |
| 4 | Pindahkan (drag) opportunity ke stage "UAT Test Stage" (Probability = 75, dari T-01) | Opportunity pindah ke stage itu | Tour melakukan drag-and-drop kanban ke stage "QA Tour High" (probability=88, angka contoh beda), PASS | [x] Waived — diterima dari Tour test (angka contoh berbeda, mekanisme identik) |
| 5 | Buka form opportunity, cek nilai Probability | Probability sekarang 75% (ikut stage) | Unit test `test_probability_follows_stage_change` mengonfirmasi mekanisme related-field (20→60 saat pindah stage, angka contoh beda) + Tour (nilai akhir dibaca lewat kolom Probability Revenue di T-03) | [x] Waived — diterima dari unit test + Tour test |

### T-03: Kolom "Probability Revenue" di daftar Opportunities

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari Pipeline, klik ikon switch ke tampilan List | Daftar opportunity muncul dalam bentuk tabel/list | Tour switch ke list view via `button.o_switch_view.o_list`, sukses | [x] Waived — diterima dari Tour test |
| 2 | Cari kolom "Probability Revenue", posisinya tepat setelah kolom "Expected Revenue" | Kolom ada dan terlihat | Dikonfirmasi statis di `02_DIFF_ANALYSIS.md` DIFF-05 (xpath tidak berubah) + Tour membaca nilai langsung dari kolom itu | [x] Waived — diterima dari Tour test + code review |
| 3 | Cek baris "UAT Test Opportunity" (dari T-02) | Nilai = 5000 × 75% = 3750 | Tour assert baris list berisi "880" (= 1000 × 88%, angka contoh beda, formula identik AC-03-01) | [x] Waived — diterima dari Tour test (angka contoh berbeda, formula identik) |
| 4 | Scroll ke baris total di bawah tabel | Kolom "Probability Revenue" ikut dijumlahkan (total) | Dikonfirmasi statis — atribut `sum="Probability Revenue"` tidak berubah dari 18.0 (BSL-011, `02_DIFF_ANALYSIS.md` DIFF-05), tidak diuji ulang via Tour | [x] Waived — diterima dari code review (atribut view tidak berubah) |

### T-04: Update Probability otomatis (fitur yang terkait langsung risiko migrasi ini)

> Skenario ini spesifik untuk migrasi 18.0→19.0 — memverifikasi tombol/aksi "Update Probabilities" (perhitungan otomatis) tetap berfungsi setelah migrasi.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Matikan pengaturan "Probability from stage" di Settings → CRM (supaya opportunity pakai perhitungan otomatis, bukan mengikuti stage) | Pengaturan nonaktif | Unit test `test_toggle_saves_config_parameter` mengonfirmasi toggle OFF tersimpan benar | [x] Waived — diterima dari unit test |
| 2 | Buka salah satu opportunity, cari tombol/aksi "Update Probabilities" (biasanya di menu Action atau tombol di form) dan jalankan | Aksi berjalan tanpa error | Unit test `test_pls_recompute_toggle_off_follows_pls` memanggil `_compute_probabilities()` (method yang sama persis yang dipanggil aksi "Update Probabilities") secara langsung, PASS tanpa error — **ini adalah regression test utama untuk DIFF-01**, breaking change asli yang ditemukan & diperbaiki di migrasi ini | [x] Waived — diterima dari unit test (regression guard DIFF-01) |
| 3 | Cek nilai "Automated Probability" pada opportunity itu | Angka berubah/ter-update (bukan tetap diam di nilai lama) | `test_pls_recompute_toggle_off_follows_pls` assert `automated_probability` berubah ke nilai hasil PLS (mock 42.0); `test_pls_recompute_toggle_on_follows_stage` assert cabang sebaliknya (mock 99.0, `probability` ikut stage bukan PLS) — **dua test inilah yang gagal sebelum fix DIFF-01 diterapkan, dan PASS setelahnya**, jadi bukti paling langsung bahwa aksi ini genuinely bekerja di 19.0 | [x] Waived — diterima dari unit test (regression guard DIFF-01) |

### T-05: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Struktur file `security/ir.model.access.csv` yang rusak/tidak terpakai (BSL-016)** — ini file internal modul yang sengaja tidak pernah dimuat Odoo (di-nonaktifkan di konfigurasi modul), tidak ada cara mengujinya lewat tampilan aplikasi. Tidak berdampak ke pemakaian sehari-hari.
- **Import Python yang tidak terpakai (BSL-013)** — murni kode internal, tidak ada gejala yang terlihat di aplikasi.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Toggle & konfigurasi probability per stage | T-01 | [x] Waived | Diterima dari Tour test + unit test, bukan eksekusi manual |
| 2 | Perhitungan probability opportunity | T-02, T-04 | [x] Waived | Diterima dari Tour test + unit test (T-04 = regression guard DIFF-01), bukan eksekusi manual |
| 3 | Revenue probability | T-03 | [x] Waived | Diterima dari Tour test + code review, bukan eksekusi manual |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima bahwa TIDAK ADA perubahan fitur/perilaku yang disengaja di project migrasi ini (`03_MIGRATION_SPEC.md` §4) — semua perubahan kode murni untuk kompatibilitas teknis dengan Odoo 19.0 (dua titik: cara baca hasil perhitungan otomatis probability, dan path import satu file test), bukan perubahan fitur.

- [ ] Dikonfirmasi stakeholder — tidak ada keberatan terhadap posisi visual field "Probability" di form Stage yang sedikit berbeda dari sebelumnya (sekarang di grup kedua form, bukan pertama) — ini perubahan bawaan Odoo 19.0 sendiri, bukan sesuatu yang project ini putuskan.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan (kalau ada instance produksi 18.0 nyata yang akan di-upgrade ke 19.0) — **belum dilakukan di project ini**, project ini port kode ke instalasi baru (belum ada data produksi, lihat `01a_MIGRATION_INTAKE.md` §3). Kalau modul ini akan dipasang di instance produksi existing, jalankan rehearsal upgrade di staging terlebih dahulu sebelum go-live.
- [ ] Backup database produksi sebelum upgrade nyata (kalau berlaku).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan | Catatan |
|---|---|---|---|---|
| Waiver (bukan UAT sign-off asli) | kuncoro@doodex.net | 2026-08-26 | — (instruksi tertulis di sesi CLI, bukan tanda tangan formal) | Memutuskan MELEWATI eksekusi manual T-01 s.d. T-04, menerima bukti test otomatis (Step 9/10) sebagai dasar penutupan gate. Skenario T-01 s.d. T-04 di atas TIDAK PERNAH dijalankan tangan oleh business user (PM/FA/Sales Manager) asli. |
| PM | | | | Kosong — belum ada sign-off asli |
| FA | | | | Kosong — belum ada sign-off asli |
| User | | | | Kosong — belum ada sign-off asli |

> **Rekomendasi tetap berlaku:** kalau modul ini akan dipakai instance produksi sungguhan, sign-off asli oleh PM/FA/Sales Manager (menjalankan T-01 s.d. T-04 dengan tangan sendiri) tetap direkomendasikan sebelum go-live — waiver di atas adalah keputusan dev untuk menutup gate CLI/dokumentasi project ini, bukan pengganti proses UAT bisnis yang sesungguhnya.
