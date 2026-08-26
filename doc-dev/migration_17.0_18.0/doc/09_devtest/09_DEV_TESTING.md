# Dev Testing — crm_probability_from_stage

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-24

---

> **Gotcha MSYS/Git Bash diterapkan** (lesson tercatat modul ini sendiri, 2026-07-30): command dijalankan dengan prefix `MSYS_NO_PATHCONV=1` supaya argumen `/crm_probability_from_stage` di `--test-tags` tidak di-mangle jadi path Windows. **Diverifikasi WAJIB:** jumlah baris log `Starting <Class>.<method>` dicocokkan ke jumlah method test yang ditulis — 11 baris `Starting` muncul di run #1/#2 (unit/integration, `tests/test_crm_probability_from_stage.py`, dicek `ast`, §9a), lalu 13 baris `Starting` di run #3 setelah 2 Tour ditambahkan (`tests/test_crm_probability_tour.py`). Bukan false-pass.

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
| AC-01-04, AC-02-01 (browser), AC-03-01 (browser), AC-03-03 | Visual UI real (bukan cuma ORM) | `test_crm_probability_pipeline_tour`, `test_crm_probability_settings_tour` | ✅ Lengkap | **Ditambahkan setelah percobaan awal** — lihat catatan "Mode D — Tour test" di bawah. Tour Odoo asli (Chrome headless sungguhan), bukan browser automation eksternal. |
| AC-04-01/02 | Install sukses walau dead code/ACL rusak | — (implisit) | ✅ Terverifikasi | Lewat G1 install test (Step 6) — bukan test method tersendiri |

**Verdict audit:** Semua 16 AC sekarang punya cakupan test otomatis — 11 lewat unit/integration ORM, 4 lewat 2 Tour test browser asli (ditambahkan setelah kebutuhan verifikasi visual muncul di Step 10, lihat catatan di bawah), 2 lewat G1 install test. Tidak ada AC yang HANYA bisa diverifikasi manual.

### Mode D — Tour Test (ditambahkan setelah Step 10 dimulai, 2026-08-26)

> **Kenapa ditambahkan belakangan, bukan di awal Step 9:** rencana awal (`05b_TEST_PLAN_MIGRATION.md`) menaruh AC-01-04/AC-03-03 (visual UI) di Step 10 dengan mode "AI-interaktif" (Claude Browser/Claude in Chrome). Saat Step 10 dijalankan, **AI-interaktif terbukti tidak reliable** untuk modul ini — Claude Browser gagal total baca DOM webclient (data poin ke-4, sudah tercatat berulang di project lain), dan Claude in Chrome sempat berhasil sebagian (login, render halaman) tapi klik berhenti ter-registrasi setelah 1-2 interaksi (root cause tidak diketahui, kemungkinan besar relay extension, bukan Odoo). Solusi: **Mode D** (`migration-tool` `templates/test/tour_example.js.template` + `Dockerfile.template` resep `google-chrome-stable`, diadaptasi dari lesson `doc-dev-backfill`) — Tour Odoo native yang jalan via `HttpCase.start_tour()`, dikontrol LANGSUNG oleh Odoo test framework lewat Chrome DevTools Protocol, bukan lewat extension/relay eksternal. Hasilnya: **jauh lebih reliable** — 2 Tour (11+4 langkah) sukses 100% percobaan pertama setelah image di-build dengan Chrome.

- `static/tests/tours/crm_probability_pipeline_tour.js` — buat opportunity via kanban quick-create, drag-and-drop ke stage `probability=88` (dibuat di `setUp` Python), switch ke list view, assert kolom "Probability Revenue" = 880 (1000 × 88%). Membuktikan AC-02-01 (probability ikut stage) dan AC-03-01/03-03 (revenue_probability + kolom list) lewat klik browser sungguhan, bukan cuma panggilan ORM.
- `static/tests/tours/crm_probability_settings_tour.js` — filter Settings via search box "Probability", klik checkbox toggle, Save. Companion Python test (`test_crm_probability_settings_tour`) assert server-side `ir.config_parameter` genuinely `'True'` setelah tour selesai — membuktikan AC-01-01/AC-01-04 lewat klik checkbox sungguhan (checkbox yang SAMA yang gagal diklik lewat Claude in Chrome manual, berhasil sempurna lewat Tour).
- Prasyarat: `docker-env/Dockerfile.target` (resep `google-chrome-stable`) + `docker-compose.yml` `odoo_target` diubah dari `image: odoo:18.0` jadi `build:` + `shm_size: '2gb'`.
- `__manifest__.py` `assets.web.assets_tests` ditambahkan supaya kedua file Tour ini ter-load saat `--test-enable`.

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
| AC-01-01, AC-01-04 | — | — | ✅ | ✅ Pass | `test_crm_probability_settings_tour`, checkbox+save via Chrome asli, assert server-side |
| AC-02-01, AC-03-01, AC-03-03 | — | — | ✅ | ✅ Pass | `test_crm_probability_pipeline_tour`, 11 langkah, drag-and-drop + list view |

> **Run #3** (Tour, setelah image di-build dengan `google-chrome-stable`): **0 failed, 0 error(s) of 13 tests** (11 unit/integration + 2 Tour). Log: "Chrome pid: 18"/"218", "Browser version: Chrome/151.0.7922.173", kedua Tour "tour succeeded" dengan seluruh step (11/11 dan 4/4) tercatat lengkap di log — bukan skip/false-pass.

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-records/crm_probability_from_stage_17_18/SUMMARY.md`:
  - **CAND-07** — `ir.config_parameter.set_param(key, False)` menghapus key (bukan simpan string `'False'`), gotcha umum lintas modul apapun yang menyimpan Boolean config_parameter dan mengasumsikan storage simetris string.
  - **CAND-08** — Tour test (Mode D) jauh lebih reliable daripada AI-interactive browser automation (Claude Browser/Claude in Chrome) untuk verifikasi UI Odoo — temuan penting untuk `ai-doc/ROADMAP.md` §3 "RPC vs browser automation".

## Verdict

- [x] ✅ Semua AC (16/16) pass — 11 unit/integration + 2 Tour browser asli (13 test, 0 failed/error) + 2 terverifikasi implisit lewat G1. Lanjut ke step 10.
