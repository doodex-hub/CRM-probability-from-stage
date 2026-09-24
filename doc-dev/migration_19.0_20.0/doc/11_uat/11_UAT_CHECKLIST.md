# UAT Checklist — Migrasi crm_probability_from_stage

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-09-24

> Kriteria sukses: user TIDAK merasakan bedanya dibanding 19.0. Satu-satunya perbedaan yang terlihat adalah tata letak bawaan Odoo 20.0 (posisi field "Probability" di form Stage, tetangga baris di Settings) — bukan keputusan project ini.
>
> **Dokumen ini didesain sebagai test script untuk dijalankan SENDIRI oleh business user/stakeholder (PM/FA/Sales Manager).** AI tidak mengisi kolom Actual/Status/Sign-off atas eksekusinya sendiri.
>
> **WAIVER eksplisit (2026-09-24):** dev/pemilik project (kuncoro@doodex.net) memutuskan lewat chat CLI ("lanjut step 11 pakai waiver seperti 18→19") untuk MELEWATI eksekusi manual T-01 s.d. T-05 di bawah, dan menerima bukti otomatis + AI-interaktif sebagai dasar penutupan gate: Step 9 (`09_DEV_TESTING.md` — 12 unit test + 2 tour Chrome headless, 5/5 run berturut-turut hijau, plus kontrol negatif) dan Step 10 (`10_BUSINESS_FLOW_MIGRATION.md` — 6 skenario live Playwright MCP, semua `[DIKONFIRMASI]`, nilai dicek langsung ke database, 8 screenshot). Kolom Actual/Status diisi **"Waived — diterima dari Step 9/10"**, BUKAN "Pass" hasil klik manual — business user asli belum pernah menjalankan langkah-langkah ini dengan tangan sendiri. Pola sama dengan migrasi 17→18 dan 18→19 modul ini.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `crm_probability_from_stage` versi 20.0 (`20.0.1.0`) terinstall di environment UAT.
- [ ] Login sebagai user Sales Manager (bukan cuma Administrator). Catatan: pengaturan di Settings hanya bisa diubah oleh admin/Sales Manager.
- [ ] Minimal 2 stage CRM dengan Probability berbeda (akan diisi di T-02: "Qualified" = 75, "Proposition" = 40).
- [ ] Satu opportunity uji: nama "UAT Opportunity", Expected Revenue 1000, di stage "New".
- [ ] Database UAT = salinan/staging, bukan produksi asli.

## Skenario Test (Test Script)

### T-01: Fitur mati (kondisi awal) — tidak ada yang rusak

**Data dummy:** "UAT Opportunity", Expected Revenue 1000.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Settings → CRM: pastikan "Probability from stage" TIDAK dicentang | Tidak dicentang | Step 10 S-01 (install baru, belum pernah dicentang) | [x] Waived — diterima dari Step 10 S-01 |
| 2 | CRM → Configuration → Stages → buka "Qualified" | Form terbuka tanpa error, TIDAK ada field "Probability" | Step 10 S-01: tanpa error, field tidak dirender (`S01_stage_form_toggle_off.png`); unit test `test_show_probability_computed` | [x] Waived — diterima dari Step 9/10 |
| 3 | CRM → Pipeline → New → isi "UAT Opportunity", Expected Revenue 1000 → Save | Tersimpan tanpa error | Step 10 S-01: tersimpan, 0 error (`S01_lead_form_toggle_off.png`) | [x] Waived — diterima dari Step 10 S-01 |

### T-02: Mengaktifkan fitur & mengisi Probability per stage

**Data dummy:** Qualified = 75, Proposition = 40.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Settings → CRM → centang "Probability from stage" (blok kedua, dekat "Multi Teams") → Save | Tetap tercentang setelah refresh | Step 10 S-02: tercentang, DB `'True'` (`S02_settings_toggle_on.png`); tour `crm_probability_settings_tour` | [x] Waived — diterima dari Step 9/10 |
| 2 | Buka stage "Qualified" | Ada field "Probability" dengan "%" di kolom kiri, di atas "Is Won Stage?" | Step 10 S-03 (`S03_stage_form_toggle_on.png`) | [x] Waived — diterima dari Step 10 S-03 |
| 3 | Isi 75 → Save; buka "Proposition", isi 40 → Save | Tersimpan tanpa error | Step 10 S-03/S-05: tersimpan 75.00 % dan 40 | [x] Waived — diterima dari Step 10 |

### T-03: Opportunity mengikuti Probability stage

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka "UAT Opportunity" → klik "Qualified" di bar stage → Save | Probability = 75.00 | Step 10 S-04: 75.00, DB `probability=75` | [x] Waived — diterima dari Step 10 S-04 |
| 2 | Pipeline → tampilan list | Kolom "Probability Revenue" setelah "Expected Revenue" = $ 750.00, ada total di bawah | Step 10 S-04: $750.00, footer $750.00 (`S04_list_probability_revenue.png`); tour pipeline (880) | [x] Waived — diterima dari Step 9/10 |
| 3 | Pindahkan ke "Proposition" → Save | Probability = 40.00, Probability Revenue = $ 400.00 | Step 10 S-05: DB `probability=40`, `revenue_probability=400` | [x] Waived — diterima dari Step 10 S-05 |

### T-04: Probability tetap ikut stage walau Predictive Lead Scoring aktif

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | (Butuh minimal 1 opportunity Won dan 1 Lost.) Settings → CRM → "Update Probabilities" → Update | Selesai tanpa error | Step 10 S-05: tanpa error | [x] Waived — diterima dari Step 10 S-05 |
| 2 | Pindahkan "UAT Opportunity" ke stage lain → Save | Probability = angka stage, bukan angka prediksi | Step 10 S-05 (probability 40 vs prediksi 91.67); cabang logika dibuktikan unit test `test_pls_recompute_toggle_on_follows_stage` | [x] Waived — diterima dari Step 9/10 |

### T-05: Mematikan fitur harus benar-benar mematikan

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Settings → CRM → hapus centang "Probability from stage" → Save → refresh | Tetap tidak tercentang | Step 10 S-06: DB `'False'` | [x] Waived — diterima dari Step 10 S-06 |
| 2 | Buka stage "Qualified" | Field "Probability" TIDAK tampil | Step 10 S-06 (`S06_stage_form_after_toggle_off.png`); test `test_settings_toggle_roundtrip_drives_computes` | [x] Waived — diterima dari Step 9/10 |
| 3 | Buka "UAT Opportunity" | Terbuka tanpa error | Step 10 S-06: tanpa error | [x] Waived — diterima dari Step 10 S-06 |

### T-06: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- Mengubah toggle tidak menghitung ulang opportunity lama sampai probability-nya berubah lagi (BSL-005) — perilaku lama yang dipertahankan, tidak kelihatan langsung di UI. Dibuktikan unit test `test_toggle_change_no_auto_recompute`.
- Probability stage tanpa batas 0–100 (BSL-014) — bisa diisi −50/150; perilaku lama, dibuktikan unit test.
- Nilai toggle yang diisi manual lewat System Parameters (mode developer) dengan teks selain True/False (mis. `0`) — di 20.0 dibaca OFF, di 19.0 dibaca ON (MF-03). Hanya relevan untuk perubahan manual tingkat teknis.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Toggle & probability per stage | T-01, T-02, T-05 | [x] Waived | bukti Step 9/10 |
| 2 | Opportunity mengikuti stage & Probability Revenue | T-03 | [x] Waived | bukti Step 9/10 |
| 3 | Interaksi dengan Predictive Lead Scoring | T-04 | [x] Waived | bukti Step 9/10 |

## Review Item Out-of-Scope

Stakeholder diminta mengonfirmasi sadar & menerima (dari `03_MIGRATION_SPEC.md` §4 + `FINDINGS.md`):

- Aset App Store (banner.gif, index.html baru, dll.) dari branch rilis 19.0 tidak di-port ke branch migrasi — **disetujui dev** (MF-01), dikerjakan saat packaging rilis 20.0.
- Posisi field "Probability" di form Stage pindah ke kolom kiri atas (bawaan Odoo 20.0, DIFF-05) — tidak diubah.
- Perubahan kecil yang disetujui dev: `compute=None` pada field `probability` (MF-04, menghilangkan warning log, perilaku sama) dan perbaikan stabilitas tour test (MF-05).
- Quirk lama yang dipertahankan: BSL-005, BSL-013, BSL-014, BSL-015, BSL-016.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan — **belum dilakukan**; project ini port kode ke instalasi baru (`01a` §3). Kalau modul akan dipasang di instance produksi 19.0 yang sudah ada, jalankan rehearsal upgrade di staging dulu. Nilai toggle lama (`'True'` atau tidak ada) kompatibel dengan cara baca baru (`03_MIGRATION_SPEC.md` §2b).
- [ ] Backup database produksi sebelum upgrade nyata (kalau berlaku).
- [x] README modul direview — baris kompatibilitas diubah ke "Odoo version: 20.0" (Step 6 A6).
- [ ] Image Docker resmi `odoo:20.0` belum ada saat project ini — environment test memakai source `odoo20`; produksi perlu instalasi Odoo 20.0 resmi.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan | Catatan |
|---|---|---|---|---|
| Waiver (bukan UAT sign-off asli) | kuncoro@doodex.net | 2026-09-24 | — (instruksi tertulis di sesi CLI, bukan tanda tangan formal) | Memutuskan MELEWATI eksekusi manual T-01 s.d. T-05, menerima bukti Step 9 (otomatis) dan Step 10 (AI-interaktif live) sebagai dasar penutupan gate. Skenario di atas TIDAK PERNAH dijalankan tangan oleh business user (PM/FA/Sales Manager) asli. |
| PM | | | | Kosong — belum ada sign-off asli |
| FA | | | | Kosong — belum ada sign-off asli |
| User | | | | Kosong — belum ada sign-off asli |

> **Rekomendasi tetap berlaku:** kalau modul ini dipakai instance produksi sungguhan, sign-off asli oleh PM/FA/Sales Manager (menjalankan T-01 s.d. T-05 sendiri) tetap direkomendasikan sebelum go-live. Ini juga satu-satunya cara menutup sisa MF-02 (tampilan dilihat mata manusia). Waiver di atas menutup gate dokumentasi project ini, bukan pengganti UAT bisnis.
>
> **Catatan ini waiver ketiga berturut-turut** untuk modul ini (17→18, 18→19, 19→20) — belum pernah ada UAT business user asli sejak 17.0.

## Penutupan Migrasi

- [ ] `doc/MIGRATION_CLOSED.md` **belum ditulis** — template mensyaratkan sign-off semua role terisi; di sini hanya waiver (PM/FA/User kosong). Sama dengan 18→19 (juga tidak menulisnya). Konsekuensi: deteksi hotfix otomatis (`HOTFIX_REVIEW.md`) belum punya titik-nol. Kalau dev ingin menutup siklus secara formal atas dasar waiver, `MIGRATION_CLOSED.md` bisa ditulis dengan SHA HEAD `migration/20.0` saat itu.
