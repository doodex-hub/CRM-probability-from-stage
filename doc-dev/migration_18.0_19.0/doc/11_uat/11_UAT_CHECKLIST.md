# UAT Checklist — Migrasi crm_probability_from_stage

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya dibanding sebelum migrasi (18.0), kecuali tidak ada satupun perubahan yang disengaja di project ini (murni port kode ke 19.0).

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
| 1 | Buka Settings → CRM, cari pengaturan "Probability from stage", aktifkan (centang), klik Save | Pengaturan tersimpan, tidak ada error | | [ ] Pass [ ] Fail |
| 2 | Buka Settings → CRM → Stages, buat stage baru bernama "UAT Test Stage" | Stage berhasil dibuat | | [ ] Pass [ ] Fail |
| 3 | Di form stage yang baru dibuat, cari field "Probability" (angka + tanda %) | Field terlihat (karena pengaturan di langkah 1 aktif) | | [ ] Pass [ ] Fail |
| 4 | Isi field Probability dengan angka 75, Save | Nilai 75 tersimpan tanpa error | | [ ] Pass [ ] Fail |
| 5 | Matikan kembali pengaturan "Probability from stage" di Settings → CRM, Save | Pengaturan tersimpan | | [ ] Pass [ ] Fail |
| 6 | Buka lagi stage "UAT Test Stage" | Field "Probability" TIDAK terlihat lagi | | [ ] Pass [ ] Fail |
| 7 | Aktifkan lagi pengaturan "Probability from stage" (persiapan T-02) | Pengaturan aktif | | [ ] Pass [ ] Fail |

### T-02: Probability opportunity mengikuti Stage saat pipeline berjalan

**Data dummy yang perlu dientri:** Opportunity bernama "UAT Test Opportunity", Expected Revenue = 5000.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka app CRM → Pipeline (kanban) | Pipeline terbuka normal | | [ ] Pass [ ] Fail |
| 2 | Buat opportunity baru "UAT Test Opportunity", Expected Revenue = 5000, taruh di stage manapun | Opportunity berhasil dibuat, muncul di kanban | | [ ] Pass [ ] Fail |
| 3 | Catat nilai Probability opportunity ini saat ini (bisa dilihat di form opportunity) | — | | — |
| 4 | Pindahkan (drag) opportunity ke stage "UAT Test Stage" (Probability = 75, dari T-01) | Opportunity pindah ke stage itu | | [ ] Pass [ ] Fail |
| 5 | Buka form opportunity, cek nilai Probability | Probability sekarang 75% (ikut stage) | | [ ] Pass [ ] Fail |

### T-03: Kolom "Probability Revenue" di daftar Opportunities

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari Pipeline, klik ikon switch ke tampilan List | Daftar opportunity muncul dalam bentuk tabel/list | | [ ] Pass [ ] Fail |
| 2 | Cari kolom "Probability Revenue", posisinya tepat setelah kolom "Expected Revenue" | Kolom ada dan terlihat | | [ ] Pass [ ] Fail |
| 3 | Cek baris "UAT Test Opportunity" (dari T-02) | Nilai = 5000 × 75% = 3750 | | [ ] Pass [ ] Fail |
| 4 | Scroll ke baris total di bawah tabel | Kolom "Probability Revenue" ikut dijumlahkan (total) | | [ ] Pass [ ] Fail |

### T-04: Update Probability otomatis (fitur yang terkait langsung risiko migrasi ini)

> Skenario ini spesifik untuk migrasi 18.0→19.0 — memverifikasi tombol/aksi "Update Probabilities" (perhitungan otomatis) tetap berfungsi setelah migrasi.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Matikan pengaturan "Probability from stage" di Settings → CRM (supaya opportunity pakai perhitungan otomatis, bukan mengikuti stage) | Pengaturan nonaktif | | [ ] Pass [ ] Fail |
| 2 | Buka salah satu opportunity, cari tombol/aksi "Update Probabilities" (biasanya di menu Action atau tombol di form) dan jalankan | Aksi berjalan tanpa error | | [ ] Pass [ ] Fail |
| 3 | Cek nilai "Automated Probability" pada opportunity itu | Angka berubah/ter-update (bukan tetap diam di nilai lama) | | [ ] Pass [ ] Fail |

### T-05: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Struktur file `security/ir.model.access.csv` yang rusak/tidak terpakai (BSL-016)** — ini file internal modul yang sengaja tidak pernah dimuat Odoo (di-nonaktifkan di konfigurasi modul), tidak ada cara mengujinya lewat tampilan aplikasi. Tidak berdampak ke pemakaian sehari-hari.
- **Import Python yang tidak terpakai (BSL-013)** — murni kode internal, tidak ada gejala yang terlihat di aplikasi.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Toggle & konfigurasi probability per stage | T-01 | [ ] Pass [ ] Fail | |
| 2 | Perhitungan probability opportunity | T-02, T-04 | [ ] Pass [ ] Fail | |
| 3 | Revenue probability | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima bahwa TIDAK ADA perubahan fitur/perilaku yang disengaja di project migrasi ini (`03_MIGRATION_SPEC.md` §4) — semua perubahan kode murni untuk kompatibilitas teknis dengan Odoo 19.0 (dua titik: cara baca hasil perhitungan otomatis probability, dan path import satu file test), bukan perubahan fitur.

- [ ] Dikonfirmasi stakeholder — tidak ada keberatan terhadap posisi visual field "Probability" di form Stage yang sedikit berbeda dari sebelumnya (sekarang di grup kedua form, bukan pertama) — ini perubahan bawaan Odoo 19.0 sendiri, bukan sesuatu yang project ini putuskan.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan (kalau ada instance produksi 18.0 nyata yang akan di-upgrade ke 19.0) — **belum dilakukan di project ini**, project ini port kode ke instalasi baru (belum ada data produksi, lihat `01a_MIGRATION_INTAKE.md` §3). Kalau modul ini akan dipasang di instance produksi existing, jalankan rehearsal upgrade di staging terlebih dahulu sebelum go-live.
- [ ] Backup database produksi sebelum upgrade nyata (kalau berlaku).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 s.d. T-04 dengan tangan sendiri dan menyetujui.
