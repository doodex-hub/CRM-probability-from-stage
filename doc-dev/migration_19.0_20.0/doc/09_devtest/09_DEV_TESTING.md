# Dev Testing — crm_probability_from_stage

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-24

---

> Eksekusi resmi lewat `docker-env/run-test.sh` (instansiasi `templates/run-test.sh.template`, adaptasi didokumentasikan di header script: image source-run 20.0, wipe DB otomatis, `--without-demo` polos, hitungan `Starting <Class>.test_*`, exit non-nol kalau ada failed/error):
> ```
> ./run-test.sh odoo_target target_db crm_probability_from_stage
> ```
> Environment: Odoo 20.0 FINAL dari source `D:\Kuncoro\doodex\repo\odoo20` (mount read-only), `python:3.12-slim-bookworm`, Postgres 16, Google Chrome headless (tour), Docker Desktop, Claude Code CLI (Mode C).

## 9a. Audit Kesiapan Test

1. **Registrasi:** `tests/__init__.py` meng-import kedua file test (`test_crm_probability_from_stage`, `test_crm_probability_tour`) — tidak ada file tidak ter-load.
2. **Isi method** (parse `ast` di dalam container — host tidak punya Python): 14 method, **0 stub**, semua berisi `assert*`/`start_tour`.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | toggle tersimpan | `test_toggle_saves_config_parameter` + settings tour | ✅ Lengkap | 4 asersi (logis + mentah) |
| AC-01-02/02b | show_probability | `test_show_probability_computed` | ✅ Lengkap | ⚠️ risiko tinggi DIFF-02 |
| AC-01-03 | tanpa validasi range | `test_stage_probability_no_range_validation` | ✅ Lengkap | |
| AC-01-04 | setting UI | `crm_probability_settings_tour` | ✅ Lengkap | + asersi server-side |
| AC-01-05 | jalur Settings ON→OFF | `test_settings_toggle_roundtrip_drives_computes` | ✅ Lengkap | ⚠️ risiko tinggi DIFF-02, baru |
| AC-02-01 | ikut stage | `test_probability_follows_stage_change` + pipeline tour | ✅ Lengkap | |
| AC-02-02 | toggle OFF | `test_is_automated_probability_toggle_off` | ✅ Lengkap | |
| AC-02-03 | toggle ON | `test_is_automated_probability_toggle_on` | ✅ Lengkap | ⚠️ risiko tinggi DIFF-01 |
| AC-02-04 | PLS toggle ON | `test_pls_recompute_toggle_on_follows_stage` | ✅ Lengkap | mock tuple |
| AC-02-05 | PLS toggle OFF | `test_pls_recompute_toggle_off_follows_pls` | ✅ Lengkap | mock tuple |
| AC-02-06 | tanpa recompute | `test_toggle_change_no_auto_recompute` | ✅ Lengkap | |
| AC-03-01 | revenue | `test_revenue_probability_calculation` | ✅ Lengkap | |
| AC-03-02 | dead dep partner | `test_revenue_probability_recompute_on_partner_change` | ✅ Lengkap | |
| AC-03-03 | kolom list | `crm_probability_pipeline_tour` | ✅ Lengkap | baris berisi 880 |
| AC-04-01/02 | quirk | — | review Step 8 + G1 install | bukan test otomatis (by design) |

**Verdict audit:** [x] Semua AC risiko tinggi berstatus Lengkap — lanjut eksekusi.

## Baseline

- **Test lama:** `01a` §4 mencatat test ADA di lokasi yang SAMA dengan source (`crm_probability_from_stage/tests/`, bukan repo lain). Hasil run terhadap source 19.0: 13/13 PASS (2026-08-26, `doc-dev/migration_18.0_19.0/doc/09_devtest/09_DEV_TESTING.md`, Docker Odoo 19.0). Semua 13 test lama di-port; 12 tetap sama maksudnya (3 disesuaikan API — `_set_toggle`, `test_toggle_saves_config_parameter`, asersi tour), +1 test baru (AC-01-05).
- **Bukti tambahan kode 19.0 di 20.0** (kontrol negatif Step 6, `06c`): model 19.0 apa adanya → install PASS, 6 ERROR `AttributeError ... get_param`; mutasi `get_str` → 5 FAIL. Test suite genuinely mendeteksi DIFF-01 dan DIFF-02.
- **Applicability Fase E:** Ya (terbatas) — 2 tour test (`crm_probability_pipeline_tour`, `crm_probability_settings_tour`) wajib ada & PASS.

## Hasil Unit, Integration & Tour Test (target-codebase, `migration/20.0` @ `89eac22` + `run-test.sh`)

Log: `docker-env/logs/run-test_20260924_142245.log` — ringkasan Odoo **`0 failed, 0 error(s) of 16 tests`**; wrapper: `16 test method ter-eksekusi` (14 modul + 2 suite JS `web.tests.test_js` `test_unit_desktop/mobile` yang otomatis ikut dan selesai no-op karena modul tidak punya unit test JS), exit 0.

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | `test_toggle_saves_config_parameter` | — | settings tour (server-side `get_bool` True) | ✅ Pass | |
| AC-01-02/02b | `test_show_probability_computed` | — | — | ✅ Pass | |
| AC-01-03 | `test_stage_probability_no_range_validation` | — | — | ✅ Pass | |
| AC-01-04 | — | — | `crm_probability_settings_tour` 4/4 step | ✅ Pass | |
| AC-01-05 | `test_settings_toggle_roundtrip_drives_computes` | `res.config.settings.execute()` → `set_values` core | — | ✅ Pass | |
| AC-02-01 | `test_probability_follows_stage_change` | — | pipeline tour (drag → stage 88) | ✅ Pass | |
| AC-02-02 | `test_is_automated_probability_toggle_off` | — | — | ✅ Pass | |
| AC-02-03 | `test_is_automated_probability_toggle_on` | — | — | ✅ Pass | |
| AC-02-04 | `test_pls_recompute_toggle_on_follows_stage` | — | — | ✅ Pass | |
| AC-02-05 | `test_pls_recompute_toggle_off_follows_pls` | — | — | ✅ Pass | |
| AC-02-06 | `test_toggle_change_no_auto_recompute` | — | — | ✅ Pass | |
| AC-03-01 | `test_revenue_probability_calculation` | — | pipeline tour | ✅ Pass | |
| AC-03-02 | `test_revenue_probability_recompute_on_partner_change` | — | — | ✅ Pass | |
| AC-03-03 | — | — | `crm_probability_pipeline_tour` 11/11 step (baris 880) | ✅ Pass | |

**Warning di log (bukan kegagalan):** `Field crm.lead.probability is both compute and related` ×5 (DIFF-14/MF-04, perilaku identik 19.0); `markdown2 is not installed` (image test, native `mail`, tidak relevan); `chrome_crashpad zombie` (teardown Chrome headless, infra).

**Riwayat run Step 6/9 (semua di DB bersih):** G1 #1 PASS → G2 #1 16/16 PASS → kontrol negatif `get_str` 5 FAIL → kontrol negatif model 19.0 6 ERROR → **run resmi Step 9 16/16 PASS**. Tidak ada siklus test→fix yang dibutuhkan (kode Step 6 lolos percobaan pertama).

**Catatan untuk Step 10 (dari kontrol negatif #2):** tour kanban/list/settings TIDAK memicu compute `is_automated_probability`/`show_probability` — skenario live Step 10 wajib membuka **form opportunity** dan **form stage** (toggle ON dan OFF), bukan cuma kanban/list.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di step ini (CAND-01..03 sudah di `migration-records/crm_probability_from_stage_19.0_20.0/SUMMARY.md`). Catatan infra: `--without-demo=all` di 20.0 memicu warning "invalid boolean value" — relevan untuk `templates/run-test.sh.template` (dicatat di header `run-test.sh` project ini; kandidat perbaikan template saat curation).

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration/Tour pass — **siap Step 10 (menunggu slot dari dev)**
- [ ] ❌ Ada yang gagal

---

## Addendum 2026-09-24 — MF-04 (`compute=None`) & temuan MF-05 (tour flaky)

- `models/crm_lead.py` field `probability` dapat `compute=None` (keputusan dev, MF-04) → warning "both compute and related" hilang (0 di semua run).
- Verifikasi ulang: 3 run dengan `compute=None` (1 PASS, 2 FAIL) + 3 run pembanding tanpa `compute=None` (2 PASS, 1 FAIL). **Semua kegagalan sama: `crm_probability_pipeline_tour` step 4** (race klik "New" sebelum kanban siap — MF-05). 12 unit test + settings tour PASS di semua run.
- **Status gate Step 9 dibuka ulang (⚠️):** verdict "PASS" di atas didasarkan run yang kebetulan lolos. Pipeline tour tidak stabil (~30% false-fail dari 10 run total). Gate ditutup lagi setelah MF-05 diperbaiki dan suite lolos berulang.
