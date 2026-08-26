# UAT Checklist — Migrasi crm_probability_from_stage

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user TIDAK merasakan bedanya dibanding versi 17.0 lama, kecuali tidak ada perubahan yang disengaja sama sekali untuk modul ini (port kode saja).
>
> **Dokumen ini adalah draft test script untuk dijalankan SENDIRI oleh business user/stakeholder (PM/FA/Sales Manager) — bukan laporan hasil test AI.** Kolom Actual dan Status di bawah sengaja dikosongkan.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul "CRM Probability From Stage" versi 18.0.1.0 sudah terinstall di environment UAT.
- [ ] Login sebagai user dengan role **Sales Manager** (bukan Administrator) — modul ini menyentuh Settings CRM yang butuh akses admin/manager, tapi Pipeline/Opportunity dipakai role Sales biasa sehari-hari; disarankan uji dengan kedua role kalau memungkinkan.
- [ ] Minimal 2 stage CRM pipeline tersedia (bisa pakai stage default "New"/"Qualified"/"Proposition"/"Won", atau buat stage baru).
- [ ] Database UAT sebaiknya **salinan/staging**, bukan database produksi.

## Skenario Test (Test Script)

### T-01: Mengatur probability tetap per stage

**Data dummy yang perlu dientri:** angka probability 25 untuk satu stage, 75 untuk stage lain.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Settings → CRM, aktifkan toggle "Probability from stage", klik Save | Tersimpan tanpa error | | [ ] Pass [ ] Fail |
| 2 | Buka Settings → CRM → Stages (atau edit stage langsung dari Pipeline), pilih satu stage, isi field "Probability" = 25, Save | Nilai tersimpan | | [ ] Pass [ ] Fail |
| 3 | Ulangi untuk stage lain dengan nilai 75 | Nilai tersimpan | | [ ] Pass [ ] Fail |
| 4 | Nonaktifkan toggle "Probability from stage" di Settings → CRM, buka lagi form stage yang tadi | Field "Probability" TIDAK terlihat lagi di form stage | | [ ] Pass [ ] Fail |

### T-02: Probability opportunity mengikuti stage

**Data dummy yang perlu dientri:** nama opportunity "UAT Test Deal", Expected Revenue 2.000.000.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Aktifkan lagi toggle "Probability from stage" (Settings → CRM) | Tersimpan | | [ ] Pass [ ] Fail |
| 2 | Buka CRM → Pipeline, buat opportunity baru "UAT Test Deal", Expected Revenue = 2.000.000, taruh di stage dengan probability 25 (dari T-01) | Field Probability opportunity menunjukkan 25% | | [ ] Pass [ ] Fail |
| 3 | Pindahkan opportunity "UAT Test Deal" ke stage dengan probability 75 (drag di kanban, atau ubah field Stage) | Field Probability opportunity berubah jadi 75% | | [ ] Pass [ ] Fail |

### T-03: Kolom Probability Revenue di daftar Pipeline

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka CRM → Pipeline, ganti tampilan ke daftar (List, bukan Kanban) | Kolom "Probability Revenue" muncul setelah kolom "Expected Revenue" | | [ ] Pass [ ] Fail |
| 2 | Cari baris "UAT Test Deal" (dari T-02, sekarang di stage probability 75%) | Nilai Probability Revenue = 1.500.000 (2.000.000 × 75%) | | [ ] Pass [ ] Fail |

### Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Tidak ada validasi batas nilai probability (0-100)** — kalau saat T-01 iseng dicoba isi angka negatif atau di atas 100, sistem TIDAK akan menolak. Ini bukan bug baru dari migrasi, perilaku ini sudah ada di versi 17.0 sebelumnya dan sengaja dipertahankan sama (BSL-014) — bukan sesuatu yang perlu dilaporkan sebagai kegagalan.
- **Interaksi dengan "Predictive Lead Scoring"** (fitur bawaan Odoo yang menghitung probability otomatis pakai statistik) — perilaku gabungan kedua fitur ini agak teknis (lihat `FINDINGS.md` MF-02) dan sudah diverifikasi lewat test otomatis (Step 9), tidak dijadikan skenario UAT terpisah supaya tidak membingungkan.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Konfigurasi probability per stage | T-01 | [ ] Pass [ ] Fail | |
| 2 | Probability opportunity otomatis | T-02 | [ ] Pass [ ] Fail | |
| 3 | Tampilan Probability Revenue di Pipeline | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima bahwa migrasi ini **port kode saja** — tidak ada fitur baru, tidak ada perubahan business rule, dan bug/quirk yang sudah ada di 17.0 (tidak ada validasi range probability, dead code kosmetik) sengaja TIDAK diperbaiki:

- [ ] Dikonfirmasi stakeholder — tidak ada perubahan behavior yang disengaja untuk modul ini di migrasi 18.0.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan (clone data produksi → jalankan urutan upgrade nyata → spot-check data) — **belum dilakukan di project ini** (sifat migrasi "port kode saja", belum ada data produksi/instalasi baru di versi target — lihat `01a_MIGRATION_INTAKE.md` §3). Kalau instance produksi 17.0 sudah punya data nyata saat modul ini akan di-deploy ke 18.0, rehearsal upgrade WAJIB dilakukan terpisah sebelum go-live, tidak otomatis tercakup gate-gate project ini.
- [ ] Backup database produksi sebelum upgrade nyata.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 s/d T-03 dengan tangan sendiri dan menyetujui.
