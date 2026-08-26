# Test Plan (Migrasi) — crm_probability_from_stage

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

> Modul tidak punya Owl/JS produksi (`01a_MIGRATION_INTAKE.md` §2b) — kolom Tour N/A untuk AC unit/integration biasa, tapi 2 test HttpCase Tour (`test_crm_probability_pipeline_tour`/`test_crm_probability_settings_tour`) tetap wajib di-re-run terhadap 19.0.
>
> **Beda dari `05b` migrasi 17→18:** source 17.0 TIDAK punya test sama sekali (ditulis baru di project itu). Source 18.0 (project INI) **sudah membawa test suite lengkap** (12 method unit/integration + 2 HttpCase tour, lihat `01b_BASELINE_SPEC.md` §9) — tugas Step 6/9 di sini bukan "tulis test baru", tapi (1) fix DIFF-01 di kode produksi, (2) update 2 mock test yang terikat langsung ke signature `_pls_get_naive_bayes_probabilities()`, (3) jalankan ulang seluruh suite terhadap 19.0 dan pastikan semua PASS.

---

## Step 9 — Dev Testing

> Eksekusi: `odoo-bin -i crm_probability_from_stage --test-enable --test-tags /crm_probability_from_stage --stop-after-init`. **Environment CLI Windows/Git Bash — prefix `MSYS_NO_PATHCONV=1` WAJIB** sebelum command ini (lesson tercatat modul ini sendiri di migrasi 17→18, `09_DEV_TESTING.md` §gotcha) supaya argumen `/crm_probability_from_stage` tidak di-mangle jadi path Windows.

| AC | Deskripsi | Unit | Integration | Tour | Perlu diubah Step 6? |
|---|---|---|---|---|---|
| AC-01-01 | Toggle tersimpan sebagai ir.config_parameter | — | ✅ `test_toggle_saves_config_parameter` | N/A | Tidak |
| AC-01-02/02b | `show_probability` computed benar sesuai toggle | ✅ `test_show_probability_computed` | — | N/A | Tidak |
| AC-01-03 | Probability stage tanpa validasi range (bug dipertahankan) | ✅ `test_stage_probability_no_range_validation` | — | N/A | Tidak |
| AC-01-04 | Posisi setting di halaman Settings | — | — | N/A (lihat Step 10 — visual) | Tidak |
| AC-02-01 | `probability` ikut `stage_id.probability` (related-field) | — | ✅ `test_probability_follows_stage_change` | N/A | Tidak |
| AC-02-02 | `is_automated_probability` True kalau toggle off & angka sama | ✅ `test_is_automated_probability_toggle_off` | — | N/A | Tidak |
| AC-02-03 | `is_automated_probability` selalu False kalau toggle on | ✅ `test_is_automated_probability_toggle_on` | — | N/A | Tidak |
| AC-02-04 | PLS re-compute: `probability` ikut stage saat toggle on | — | ✅ `test_pls_recompute_toggle_on_follows_stage` | N/A | **Ya — mock `return_value` jadi tuple (DIFF-01)** |
| AC-02-05 | PLS re-compute: `probability` ikut PLS saat toggle off & was_automated | — | ✅ `test_pls_recompute_toggle_off_follows_pls` | N/A | **Ya — mock `return_value` jadi tuple (DIFF-01)** |
| AC-02-06 | Toggle berubah TIDAK auto-recompute `is_automated_probability` existing | ✅ `test_toggle_change_no_auto_recompute` | — | N/A | Tidak |
| AC-03-01 | `revenue_probability` = expected_revenue × probability% | ✅ `test_revenue_probability_calculation` | — | N/A | Tidak |
| AC-03-02 | `revenue_probability` recompute (no-op value) saat `partner_id` berubah | ✅ `test_revenue_probability_recompute_on_partner_change` | — | N/A | Tidak |
| AC-03-03 | Kolom "Probability Revenue" di list view Opportunities | — | — | N/A (visual, Step 10) | Tidak |
| AC-04-01 | Install sukses walau dead import ada | ✅ (implisit — G1 install test) | — | N/A | Tidak |
| AC-04-02 | Install sukses walau `ir.model.access.csv` rusak (tetap comment-out) | ✅ (implisit — G1 install test) | — | N/A | Tidak |
| (pipeline flow) | Tour: buat stage → opportunity → cek `revenue_probability` di kanban | — | — | ✅ `test_crm_probability_pipeline_tour` | Tidak (kode tour tidak pakai API yang berubah) |
| (settings flow) | Tour: toggle di Settings → CRM, verifikasi server-side tersimpan | — | — | ✅ `test_crm_probability_settings_tour` | Tidak |

**Audit kesiapan test (per `USAGE_GUIDE.md` §5 lesson `totp_enhancement`, Fase 9a):** SEMUA 14 method di atas (12 unit/integration + 2 tour) sudah ADA dan LENGKAP di `source-codebase`/`target-codebase` (bukan stub) — dikonfirmasi baca isi penuh sesi ini (`01b_BASELINE_SPEC.md` §9), bukan cuma `grep` nama method. **Item wajib sebelum eksekusi Step 9 dianggap sah:** terapkan fix DIFF-01 di `models/crm_lead.py` DAN update 2 mock (`test_pls_recompute_toggle_on_follows_stage`/`_toggle_off_follows_pls`) di Step 6 — baru jalankan suite. Kalau suite dijalankan SEBELUM fix DIFF-01 diterapkan, AC-02-04/AC-02-05 diperkirakan **FAIL** (memvalidasi bahwa regression guard ini genuinely mendeteksi masalah, bukan cuma dekorasi) — hasil FAIL di titik itu justru diharapkan/benar, bukan tanda test rusak.

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-02/02b | Field probability terlihat/tersembunyi di form stage sesuai toggle (perhatikan DIFF-04 — posisi grup form berubah) | — | ✅ (Claude Browser, cek DOM invisible + posisi baru) | — |
| AC-01-04 | Posisi visual setting toggle di Settings → CRM (perhatikan DIFF-06 — tetangga baru `module_partnership`) | ✅ | — | — |
| AC-03-03 | Kolom "Probability Revenue" tampil benar di list Opportunities (widget monetary, sum) | — | ✅ (Claude Browser) | — |
| Smoke end-to-end | Buat opportunity → pindah stage → cek probability & revenue_probability di UI | ✅ | ✅ | — |
| Smoke DIFF-01 (khusus 18→19) | Toggle ON → jalankan action "Update Probabilities" (PLS) pada opportunity → verifikasi `automated_probability` berubah (bukti nyata DIFF-01 sudah ter-fix di jalur UI, bukan cuma unit test) | ✅ | ✅ | — |

Tidak ada skenario yang butuh AI+tool eksternal (Playwright dst) — modul terlalu kecil untuk lintas-sistem/browser matrix/load test.

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Toggle & konfigurasi probability per stage | AC-01-01..04 | Admin sales mengatur probability tiap stage pipeline, aktifkan toggle, verifikasi field muncul |
| Perhitungan probability opportunity (termasuk regresi DIFF-01) | AC-02-01..06 | Sales pindah opportunity antar stage, verifikasi probability & revenue mengikuti aturan; sales manager jalankan "Update Probabilities" dan verifikasi angka PLS benar-benar berubah |
| Revenue probability | AC-03-01..03 | Sales manager cek kolom "Probability Revenue" di Pipeline list + total |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration/Tour | Otomatis/background (`MSYS_NO_PATHCONV=1` wajib di CLI Windows), Mode D untuk tour | 16 (14 unit/integration/implisit + 2 tour) |
| 10 | QA | Manual/AI-interaktif | Campuran | 5 skenario (mencakup 3 AC + 1 smoke end-to-end + 1 smoke khusus DIFF-01) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 3 kelompok fitur, mencakup semua 16 AC |
