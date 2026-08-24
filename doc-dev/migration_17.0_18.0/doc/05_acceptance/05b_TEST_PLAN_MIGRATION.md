# Test Plan (Migrasi) — crm_probability_from_stage

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

> Modul tidak punya Owl/JS (`01a_MIGRATION_INTAKE.md` §2b) — kolom Tour N/A untuk semua AC.

---

## Step 9 — Dev Testing

> Eksekusi: `odoo-bin -i crm_probability_from_stage --test-enable --test-tags /crm_probability_from_stage --stop-after-init`. **Environment CLI Windows/Git Bash — prefix `MSYS_NO_PATHCONV=1`WAJIB** sebelum command ini (lesson tercatat modul ini sendiri, `09_DEV_TESTING.md` §gotcha) supaya argumen `/crm_probability_from_stage` tidak di-mangle jadi path Windows.
>
> Modul source 17.0 **tidak punya test file sama sekali** (tidak ada folder `tests/`) — semua test di bawah adalah test BARU yang ditulis project ini sebagai bukti kesetaraan behavior 17.0↔18.0, bukan port dari test lama.

| AC | Deskripsi | Unit | Integration | Tour |
|---|---|---|---|---|
| AC-01-01 | Toggle tersimpan sebagai ir.config_parameter | — | ✅ `test_toggle_saves_config_parameter` | N/A |
| AC-01-02/02b | `show_probability` computed benar sesuai toggle | ✅ `test_show_probability_computed` | — | N/A |
| AC-01-03 | Probability stage tanpa validasi range (bug dipertahankan) | ✅ `test_stage_probability_no_range_validation` | — | N/A |
| AC-01-04 | Posisi setting di halaman Settings | — | — | N/A (lihat Step 10 — visual, bukan cakupan test otomatis) |
| AC-02-01 | `probability` ikut `stage_id.probability` (related-field) | — | ✅ `test_probability_follows_stage_change` | N/A |
| AC-02-02 | `is_automated_probability` True kalau toggle off & angka sama | ✅ `test_is_automated_probability_toggle_off` | — | N/A |
| AC-02-03 | `is_automated_probability` selalu False kalau toggle on | ✅ `test_is_automated_probability_toggle_on` | — | N/A |
| AC-02-04 | PLS re-compute: `probability` ikut stage saat toggle on | — | ✅ `test_pls_recompute_toggle_on_follows_stage` | N/A |
| AC-02-05 | PLS re-compute: `probability` ikut PLS saat toggle off & was_automated | — | ✅ `test_pls_recompute_toggle_off_follows_pls` | N/A |
| AC-02-06 | Toggle berubah TIDAK auto-recompute `is_automated_probability` existing | ✅ `test_toggle_change_no_auto_recompute` | — | N/A |
| AC-03-01 | `revenue_probability` = expected_revenue × probability% | ✅ `test_revenue_probability_calculation` | — | N/A |
| AC-03-02 | `revenue_probability` recompute (no-op value) saat `partner_id` berubah | ✅ `test_revenue_probability_recompute_on_partner_change` | — | N/A |
| AC-03-03 | Kolom "Probability Revenue" di list view Opportunities | — | — | N/A (visual, Step 10) |
| AC-04-01 | Install sukses walau dead import ada | ✅ (implisit — G1 install test) | — | N/A |
| AC-04-02 | Install sukses walau `ir.model.access.csv` rusak (tetap comment-out) | ✅ (implisit — G1 install test) | — | N/A |

**Audit kesiapan test (per `USAGE_GUIDE.md` §5 lesson `totp_enhancement`):** semua method di atas akan ditulis BARU di Step 6/Fase G1 (bukan sekadar nama method tanpa isi) — audit isi (bukan cuma `grep` nama method) dilakukan di `09_DEV_TESTING.md` Fase 9a sebelum diklaim "N test tersedia".

## Step 10 — QA Testing

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-02/02b | Field probability terlihat/tersembunyi di form stage sesuai toggle | — | ✅ (Claude Browser, cek DOM invisible) | — |
| AC-01-04 | Posisi visual setting toggle di Settings → CRM | ✅ | — | — |
| AC-03-03 | Kolom "Probability Revenue" tampil benar di list Opportunities (widget monetary, sum) | — | ✅ (Claude Browser) | — |
| Smoke end-to-end | Buat opportunity → pindah stage → cek probability & revenue_probability di UI | ✅ | ✅ | — |

Tidak ada skenario yang butuh AI+tool eksternal (Playwright dst) — modul terlalu kecil untuk lintas-sistem/browser matrix/load test.

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Toggle & konfigurasi probability per stage | AC-01-01..04 | Admin sales mengatur probability tiap stage pipeline, aktifkan toggle, verifikasi field muncul |
| Perhitungan probability opportunity | AC-02-01..06 | Sales pindah opportunity antar stage, verifikasi probability & revenue mengikuti aturan |
| Revenue probability | AC-03-01..03 | Sales manager cek kolom "Probability Revenue" di Pipeline list + total |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Unit/Integration | Otomatis/background (`MSYS_NO_PATHCONV=1` wajib di CLI Windows) | 14 (12 unit/integration + 2 implisit dari G1) |
| 10 | QA | Manual/AI-interaktif | Campuran | 4 skenario (mencakup 3 AC + 1 smoke end-to-end) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 3 kelompok fitur, mencakup semua 16 AC |
