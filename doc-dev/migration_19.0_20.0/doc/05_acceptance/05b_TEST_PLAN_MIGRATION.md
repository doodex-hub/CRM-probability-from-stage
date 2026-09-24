# Test Plan (Migrasi) — crm_probability_from_stage

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-24

---

## Step 9 — Dev Testing

> Eksekusi otomatis di Docker (Odoo 20.0 build-from-source `odoo20`, Postgres 16, Chrome headless untuk tour):
> `odoo-bin -d <db> -i crm_probability_from_stage --test-enable --test-tags /crm_probability_from_stage --stop-after-init` — **selalu `docker compose down -v` sebelum tiap run** (gotcha G1 silent no-op, `version-diffs/19-to-20.md`).

| AC | Deskripsi | Unit (TransactionCase) | Integration | Tour |
|---|---|---|---|---|
| AC-01-01 | Toggle tersimpan & terbaca balik | `test_toggle_saves_config_parameter` | — | `test_crm_probability_settings_tour` (asersi server-side `get_bool`) |
| AC-01-02 / 02b | `show_probability` ON/OFF | `test_show_probability_computed` | — | — |
| AC-01-03 | Tanpa validasi range | `test_stage_probability_no_range_validation` | — | — |
| AC-01-04 | Setting tampil & bisa disimpan | — | — | `crm_probability_settings_tour` |
| AC-01-05 | Jalur `res.config.settings.execute()` ON→OFF | `test_settings_toggle_roundtrip_drives_computes` (BARU) | ya (melalui `set_values` core) | — |
| AC-02-01 | probability ikut stage | `test_probability_follows_stage_change` | — | `crm_probability_pipeline_tour` (drag ke stage 88) |
| AC-02-02 | toggle OFF → float_compare | `test_is_automated_probability_toggle_off` | — | — |
| AC-02-03 | toggle ON → False | `test_is_automated_probability_toggle_on` | — | — |
| AC-02-04 | PLS, toggle ON → stage | `test_pls_recompute_toggle_on_follows_stage` | — | — |
| AC-02-05 | PLS, toggle OFF → PLS | `test_pls_recompute_toggle_off_follows_pls` | — | — |
| AC-02-06 | toggle tidak recompute | `test_toggle_change_no_auto_recompute` | — | — |
| AC-03-01 | revenue_probability | `test_revenue_probability_calculation` | — | `crm_probability_pipeline_tour` |
| AC-03-02 | dead dependency partner | `test_revenue_probability_recompute_on_partner_change` | — | — |
| AC-03-03 | Kolom list | — | — | `crm_probability_pipeline_tour` (baris berisi 880) |
| AC-04-01/02 | Quirk | Review kode Step 8 + G1 install | — | — |

Total: 12 TransactionCase + 2 HttpCase tour = **14 test**.

## Step 10 — QA Testing (menunggu slot dari dev)

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-02/02b | Field probability di form stage terlihat/tersembunyi sesuai toggle — **posisi baru grup pertama (DIFF-05)**, screenshot (MF-02) | — | ✅ Playwright MCP, live | — |
| AC-01-04 | Setting di Settings → CRM block kedua (DIFF-08) | — | ✅ screenshot | — |
| AC-01-05 | Toggle OFF lewat UI → buka stage → field hilang (DIFF-02 end-to-end) | — | ✅ | — |
| AC-03-03 | Kolom Probability Revenue + sum | — | ✅ | — |
| Smoke | Buat opportunity → pindah stage → probability & revenue di UI | — | ✅ | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Toggle & stage | AC-01-* | Manual business user |
| Probability vs PLS | AC-02-* | Manual |
| Revenue | AC-03-* | Manual |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer (AI) | Unit/Integration/Tour | Otomatis, Docker | 17 (14 test) |
| 10 | QA | AI-interaktif (Playwright MCP) | Live, menunggu slot | 5 skenario |
| 11 | PM/FA/User | UAT | Manual | 3 kelompok |
