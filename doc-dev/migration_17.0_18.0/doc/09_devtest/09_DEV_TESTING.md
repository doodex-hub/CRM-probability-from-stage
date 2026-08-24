# Dev Testing — crm_probability_from_stage

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-24

---

> **Gotcha MSYS/Git Bash diterapkan** (lesson tercatat modul ini sendiri, 2026-07-30): command dijalankan dengan prefix `MSYS_NO_PATHCONV=1` supaya argumen `/crm_probability_from_stage` di `--test-tags` tidak di-mangle jadi path Windows. **Diverifikasi WAJIB:** jumlah baris log `Starting <Class>.<method>` dicocokkan ke jumlah method test yang ditulis — 11 baris `Starting` muncul, PERSIS 11 method di `tests/test_crm_probability_from_stage.py` (dicek `ast`, §9a). Bukan false-pass.

## 9a. Audit Kesiapan Test

Module source 17.0 **tidak punya test sama sekali** — 11 method test di bawah adalah BARU, ditulis untuk project migrasi ini sebagai bukti kesetaraan behavior (bukan port dari test lama).

**Audit isi (via `ast`, bukan `grep` nama) — lihat command di `09_DEV_TESTING.md` template §9a:** dijalankan terhadap `tests/test_crm_probability_from_stage.py` — **hasil: 11/11 method `ok` (tidak ada stub)**.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Toggle → config_parameter | `test_toggle_saves_config_parameter` | ✅ Lengkap | — |
| AC-01-02/02b | `show_probability` computed | `test_show_probability_computed` | ✅ Lengkap | — |
| AC-01-03 | Tidak ada validasi range | `test_stage_probability_no_range_validation` | ✅ Lengkap | — |
| AC-02-01 | `probability` ikut `stage_id` | `test_probability_follows_stage_change` | ✅ Lengkap | — |
| AC-02-02 | `is_automated_probability` toggle off | `test_is_automated_probability_toggle_off` | ✅ Lengkap | — |
| AC-02-03 | `is_automated_probability` toggle on | `test_is_automated_probability_toggle_on` | ✅ Lengkap | — |
| AC-02-04 | PLS recompute, toggle on → ikut stage | `test_pls_recompute_toggle_on_follows_stage` | ✅ Lengkap | `_pls_get_naive_bayes_probabilities` di-mock (`unittest.mock.patch.object`) supaya deterministik — real PLS butuh data training historis yang tidak ada di test DB kosong |
| AC-02-05 | PLS recompute, toggle off → ikut PLS | `test_pls_recompute_toggle_off_follows_pls` | ✅ Lengkap | Sama, PLS di-mock |
| AC-02-06 | Toggle change tidak auto-recompute | `test_toggle_change_no_auto_recompute` | ✅ Lengkap | — |
| AC-03-01 | `revenue_probability` calculation | `test_revenue_probability_calculation` | ✅ Lengkap | — |
| AC-03-02 | `revenue_probability` recompute no-op | `test_revenue_probability_recompute_on_partner_change` | ✅ Lengkap | — |
| AC-01-04, AC-03-03 | Visual/posisi UI | — | N/A di sini | Diverifikasi Step 10 (bukan cakupan unit/integration test, lihat `05b_TEST_PLAN_MIGRATION.md`) |
| AC-04-01/02 | Install sukses walau dead code/ACL rusak | — (implisit) | ✅ Terverifikasi | Lewat G1 install test (Step 6) — bukan test method tersendiri |

**Verdict audit:** Semua AC yang berlaku untuk unit/integration test (11 dari 16 AC total — 3 AC visual dipindah ke Step 10, 2 AC sudah terverifikasi lewat G1) berstatus Lengkap. Lanjut ke eksekusi.

## Baseline

- Characterization test / test asli source module: **tidak ada** (source 17.0 tidak punya folder `tests/` sama sekali, dikonfirmasi `01a_MIGRATION_INTAKE.md` §4).
- Applicability Check Fase E (Owl/JS) dari step 6: **Tidak, N/A** — tidak ada tour test.

## Hasil Unit, Integration & Tour Test (target-codebase)

> Eksekusi nyata: `MSYS_NO_PATHCONV=1 docker compose run --rm odoo_target odoo -d target_db -i crm_probability_from_stage --test-enable --test-tags /crm_probability_from_stage --stop-after-init` (image `odoo:18.0`, db fresh per run).
>
> **Run #1** (sebelum fix): 1 failed, 0 error(s) of 11 tests — `test_toggle_saves_config_parameter` gagal, `AssertionError: False != 'False'`. **Root cause: bug di test, BUKAN di modul** — `ir.config_parameter.set_param(key, False)` menghapus key (perilaku core Odoo untuk value falsy), jadi `get_param(key, False)` mengembalikan default Python `False` (bool), bukan string `'False'`. Test diperbaiki (assert `assertFalse` bukan `assertEqual` ke string), `01b_BASELINE_SPEC.md` BSL-001 dikoreksi (klaim "string True/False simetris" tidak akurat).
>
> **Run #2** (setelah fix): **0 failed, 0 error(s) of 11 tests.** 11 baris log `Starting Test.<method>` dicocokkan ke 11 method — bukan false-pass.

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | ✅ | — | N/A | ✅ Pass (run #2) | Test diperbaiki setelah run #1 gagal karena bug test sendiri |
| AC-01-02/02b | ✅ | — | N/A | ✅ Pass | — |
| AC-01-03 | ✅ | — | N/A | ✅ Pass | — |
| AC-02-01 | — | ✅ | N/A | ✅ Pass | — |
| AC-02-02 | ✅ | — | N/A | ✅ Pass | — |
| AC-02-03 | ✅ | — | N/A | ✅ Pass | — |
| AC-02-04 | — | ✅ | N/A | ✅ Pass | PLS di-mock |
| AC-02-05 | — | ✅ | N/A | ✅ Pass | PLS di-mock |
| AC-02-06 | ✅ | — | N/A | ✅ Pass | — |
| AC-03-01 | ✅ | — | N/A | ✅ Pass | — |
| AC-03-02 | ✅ | — | N/A | ✅ Pass | — |

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-records/crm_probability_from_stage_17_18/SUMMARY.md`: **CAND-07** — `ir.config_parameter.set_param(key, False)` menghapus key (bukan simpan string `'False'`), gotcha umum lintas modul apapun yang menyimpan Boolean config_parameter dan mengasumsikan storage simetris string.

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration pass (11/11 test, 0 failed/error setelah fix) — lanjut ke step 10
