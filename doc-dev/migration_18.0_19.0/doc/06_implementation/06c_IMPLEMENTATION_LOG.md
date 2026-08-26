# Implementation Log — crm_probability_from_stage

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

> Jejak per FASE (A1→G2), bukan cuma per item spec. Kalau ketemu sesuatu di luar spec — STOP,
> jangan improvisasi. Balik ke step 3/4 dulu.

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 | ☐ Tidak | Tidak ada relasi berantai/field JSON/dynamic model creation |
| C2 | ☐ Tidak | Tidak ada `attrs=`/`states=`/domain-context dinamis |
| D1 | ☐ Tidak | Tidak ada folder `controllers/` |
| D2 | ☐ Tidak | Tidak ada `static/src/css`; key `assets` cuma `web.assets_tests` (tour test), tetap valid 19.0 |
| E | ☐ Tidak | Tidak ada komponen Owl custom |
| F | ☐ Tidak | Otomatis N/A (E N/A) |

Detail lengkap: `06a_CODE_MIGRATION_PHASES.md`.

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-26 |
| A2 | N/A (sudah selesai migrasi 17→18) | 2026-08-26 |
| G1 (checkpoint Fase A) | ✅ PASS (Mode C) | 2026-08-26 |
| A3 | N/A (tidak ada perubahan wajib) | 2026-08-26 |
| A4 | ✅ | 2026-08-26 |
| A5 | ✅ | 2026-08-26 |
| B1 | ✅ (dikonfirmasi tidak ada perubahan) | 2026-08-26 |
| B2 | N/A | — |
| C1 | ✅ (dikonfirmasi tidak ada perubahan) | 2026-08-26 |
| C2 | N/A | — |
| D1 | N/A | — |
| D2 | N/A | — |
| E | N/A | — |
| F | N/A | — |
| G2 (validasi akhir/runtime) | ✅ Terpenuhi lewat bukti Tour test Step 9 (lihat entri "Fix DIFF-08" di bawah) | 2026-08-26 |

## Riwayat Percobaan G1 (Install Test)

> Mode C (AI jalankan langsung) — Docker 29.6.1 terdeteksi tersedia di sesi Claude Code CLI ini, dev
> mengkonfirmasi eksplisit Mode C dipilih (bukan A/B). Image `odoo:19.0` + Chrome headless (google-chrome-stable,
> resep dari `Dockerfile.template`, dibutuhkan untuk Tour test). `docker-env/docker-compose.yml` — target-only
> (`odoo_target`+`db_target`), source (18.0) tidak di-spin-up (baseline sudah tervalidasi dari pembacaan kode).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A5 (fix DIFF-01 sudah diterapkan) | C | ✅ Pass | — (45 module loaded, 0 error/critical di log, `crm_probability_from_stage` loaded 0.32s/132 queries) | 2026-08-26 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `__manifest__.py`, §2b Critical Blocker #1
- **Aksi:**
  - `__manifest__.py`: `'version': '18.0.1.0'` → `'version': '19.0.1.0'`
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak ada perubahan `depends` (`base`+`crm` dipertahankan)
  - Tidak ada perubahan `data`/`assets`/field manifest lain
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] N/A — dikonfirmasi Applicability Check (tree→list sudah selesai migrasi 17→18, tidak ada tag `<tree>` tersisa di kedua file view, dikonfirmasi baca langsung sesi ini)

## [Fase A3] N/A — dikonfirmasi Applicability Check (`security/ir.model.access.csv` dipertahankan rusak/tidak terpakai apa adanya, BSL-016; tidak ada TransientModel baru yang butuh ACL)

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** struktur folder modul keseluruhan
- **Item spec (ref):** `04_SPEC_COMPLETENESS_REVIEW.md` (21 elemen dienumerasi)
- **Aksi:** Dikonfirmasi tidak ada perubahan wajib — struktur `models/`, `views/`, `security/`, `static/`, `tests/`, `i18n/` dan `__init__.py` konsisten dengan `source-codebase`.
- **Secara eksplisit TIDAK dilakukan:** Tidak ada file/folder dibuat, dihapus, atau dipindah.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A5] Python API Compatibility

- **Scope:** `models/crm_lead.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `crm_lead.py` (DIFF-01, DIFF-03)
- **Aksi:**
  - `models/crm_lead.py` `_compute_probabilities()`: baris `lead_probabilities = self._pls_get_naive_bayes_probabilities()` diubah jadi `lead_probabilities, _tooltip_data = self._pls_get_naive_bayes_probabilities()` (unpack tuple, mengikuti pola pemanggilan native 19.0 sendiri di `enterprise19.0/odoo/addons/crm/models/crm_lead.py:560`). Komentar 2 baris ditambahkan menjelaskan alasan (bukan WHAT, tapi WHY — perubahan native yang memicu ini).
  - Sisa body method (`for lead in self`, `was_automated`, kondisi `if`/`else`) **tidak diubah sama sekali** — behavior BSL-006 dipertahankan persis.
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak ada defensive coding tambahan (mis. `isinstance()` check untuk membedakan tuple vs dict pada dua jalur early-return native 19.0 yang inkonsisten, lihat `02_DIFF_ANALYSIS.md` DIFF-01) — mengikuti pola EXACT yang dipakai core 19.0 sendiri (unconditional unpack), bukan menambah robustness di luar apa yang core lakukan. Kalau core 19.0 sendiri punya risiko crash di jalur early-return itu, itu bug core, di luar scope modul ini untuk "diperbaiki".
  - Tidak ada perubahan ke `crm_stage.py`/`res_config_settings.py` (dikonfirmasi tidak perlu, lihat DIFF-02 di `02_DIFF_ANALYSIS.md`).
- **Risiko:** LOW (perubahan 1 baris, well-understood, konsisten pola native)
- **Status:** ✅ Selesai

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/crm_stage.py`, `models/res_config_settings.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris `crm_stage.py`/`res_config_settings.py`
- **Aksi:** Dikonfirmasi ulang (baca kode langsung) — tidak ada perubahan wajib di kedua file. `res_config_settings.py` tetap membawa dead import `timedelta`/`relativedelta` (BSL-013, dipertahankan).
- **Secara eksplisit TIDAK dilakukan:** Tidak ada refactor/cleanup dead import atau dead dependency (larangan "refactor demi readability").
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan)

## [Fase B2] N/A — dikonfirmasi Applicability Check

## [Fase C1] View Sederhana

- **Scope:** `views/crm_views.xml`, `views/res_config_settings.xml`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris kedua file view (DIFF-04, DIFF-05, DIFF-06)
- **Aksi:** Dikonfirmasi ulang (baca kode langsung + cross-check struktur view native 18.0 vs 19.0) — kedua xpath tetap resolve ke target yang benar, tidak ada perubahan kode wajib.
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan XML apapun — posisi visual field kita berubah sebagai konsekuensi native (DIFF-04), bukan sesuatu yang kita "perbaiki" lewat perubahan xpath.
- **Risiko:** LOW
- **Status:** ✅ Selesai (tidak ada perubahan kode, verifikasi visual menyusul di Step 9/10)

## [Fase C2] N/A — dikonfirmasi Applicability Check

## [Fase D1] N/A — dikonfirmasi Applicability Check

## [Fase D2] N/A — dikonfirmasi Applicability Check

## [Fase E] N/A — dikonfirmasi Applicability Check

## [Fase F] N/A — dikonfirmasi Applicability Check (otomatis, E juga N/A)

## [Test Suite] Penyesuaian Mock (konsekuensi DIFF-01, di luar Fase A-G formal tapi bagian Step 6)

- **Scope:** `tests/test_crm_probability_from_stage.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris terakhir tabel
- **Aksi:**
  - `test_pls_recompute_toggle_on_follows_stage`: `patch.object(..., return_value={lead.id: 99.0})` → `return_value=({lead.id: 99.0}, {})`
  - `test_pls_recompute_toggle_off_follows_pls`: `patch.object(..., return_value={lead.id: 42.0})` → `return_value=({lead.id: 42.0}, {})`
  - Docstring class-level `TestCrmProbabilityFromStage` diupdate merujuk `doc-dev/migration_18.0_19.0/...` (sebelumnya `migration_17.0_18.0`) — koreksi referensi path, bukan perubahan logic.
- **Secara eksplisit TIDAK dilakukan:** Assertion (`self.assertEqual(...)`) di kedua test **tidak diubah sama sekali** — ini penyesuaian kompatibilitas terhadap signature native yang berubah, bukan perubahan business logic/expected behavior (AC-02-04/AC-02-05 tetap sama persis).
- **Risiko:** LOW, tapi WAJIB — tanpa ini kedua test jadi false-negative regression guard untuk DIFF-01 (lihat `05b_TEST_PLAN_MIGRATION.md`)
- **Status:** ✅ Selesai

## [G1 + Step 9] Eksekusi Docker Nyata (Mode C) — Install Test + Full Test Suite

- **Scope:** `docker-env/Dockerfile.target`, `docker-env/docker-compose.yml` (baru), eksekusi terhadap `crm_probability_from_stage` di image `odoo:19.0`
- **Item spec (ref):** `06a_CODE_MIGRATION_PHASES.md` Checkpoint G1 + Fase G2; `05b_TEST_PLAN_MIGRATION.md` Step 9
- **Aksi:**
  - Docker environment disiapkan: `odoo:19.0` + Chrome headless (resep `google-chrome-stable`, dibutuhkan 2 Tour test modul ini), target-only (tidak spin up 18.0 — baseline sudah tervalidasi statis).
  - **Percobaan 1** (`docker compose up -d --build`): install bersih, G1 PASS (lihat tabel di atas).
  - **Percobaan test suite 1** (`-u ... --test-enable --test-tags`, logfile `step9_test.log`): hasil **1 failed, 1 error dari 13 test** — KEDUA gagal di test Tour (`test_crm_probability_pipeline_tour` ERROR, `test_crm_probability_settings_tour` FAIL). Root cause diselidiki: `import { stepUtils } from "@web_tour/tour_service/tour_utils"` di `crm_probability_pipeline_tour.js` gagal resolve — file itu sudah pindah ke `@web_tour/tour_utils` di 19.0 (dikonfirmasi grep source `enterprise19.0/odoo/addons/web_tour/static/src/tour_utils.js` vs `odoo18/addons/web_tour/static/src/tour_service/tour_utils.js`, dan cross-check ke tour asli `crm` 19.0 yang sudah pakai path baru). Kegagalan resolve modul ini membuat SELURUH bundle `web.assets_tests` gagal load, jadi KEDUA tour ikut gagal walau cuma satu file yang salah import — **dicatat sebagai DIFF-08 baru** di `02_diff/02_DIFF_ANALYSIS.md`.
  - **Fix diterapkan:** `static/tests/tours/crm_probability_pipeline_tour.js` — import diubah ke `@web_tour/tour_utils`.
  - **Percobaan test suite 2** (logfile `step9_test2.log`): hasil **0 failed, 2 error** — FAIL sudah hilang, tapi 2 ERROR baru muncul: `web.assets_web.min.css`/`.min.js` return HTTP 500 (`FileNotFoundError` di filestore Odoo). **Diagnosis:** ini artefak setup Docker sesi ini sendiri (bukan temuan migrasi) — `docker-compose.yml` awal tidak memberi volume persisten untuk `/var/lib/odoo` (filestore), jadi tiap `docker compose run --rm` (kontainer efemeral terpisah dari kontainer `up` yang persisten) punya filesystem lokalnya sendiri; `ir.attachment` (cache asset bundle) yang ditulis kontainer A tidak terlihat kontainer B walau sama-sama connect ke `db_target` yang sama. **Fix:** tambah named volume `target_filestore:/var/lib/odoo` di `docker-compose.yml`, lalu `docker compose down -v` + `up -d` (reset bersih DB+filestore selaras) sebelum re-test.
  - **Percobaan test suite 3** (logfile `step9_test3.log`, setelah reset volume): hasil **0 failed, 0 error dari 13 test** — SEMUA PASS (12 unit/integration `test_crm_probability_from_stage.py` + 2 Tour `test_crm_probability_tour.py`).
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan ke `crm_probability_settings_tour.js` (file itu sendiri tidak pernah salah — gagalnya kolateral dari bundle, bukan importnya sendiri). Tidak ada perubahan business logic apapun dari temuan DIFF-08 — murni path import.
- **Risiko:** DIFF-08 sendiri: sudah LOW setelah fix+verifikasi. Setup Docker filestore: N/A untuk kode modul (isu tooling sesi ini, tidak masuk deliverable migrasi).
- **Status:** ✅ Selesai — G1 PASS, Step 9 full suite PASS (13/13), server 19.0 tetap hidup di `localhost:8178` untuk Step 10.

---

## Temuan di Luar Spec (kalau ada)

- [x] Ada satu — DIFF-08 (import `stepUtils` pindah path) TIDAK terdeteksi di analisis statis Step 2/3, baru ketahuan dari eksekusi Step 9 nyata. **Ditangani langsung** (bukan ditunda balik ke step 2/3 secara formal) karena scope-nya sempit (1 baris import, sudah tercakup pola "Python API Compatibility"/A5 secara analog untuk JS) dan sudah didokumentasikan retroaktif di `02_DIFF_ANALYSIS.md` (DIFF-08) + `03_MIGRATION_SPEC.md` §2 sebelum dinyatakan selesai di sini — konsisten prinsip "boleh pilih sendiri kalau ada rekomendasi jelas berisiko rendah, dokumentasikan, lanjut" (`CLAUDE.md` "Eksekusi Berkelanjutan").

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat di Step 2 (`02_DIFF_ANALYSIS.md` §3): `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` CAND-01 (`_pls_get_naive_bayes_probabilities()` tuple return) dan CAND-02 (`crm.stage.team_id`→`team_ids` + `write()` baru). **Ditambah CAND-03 di Step 6** (temuan baru dari eksekusi nyata): `web_tour` `tour_utils.js` pindah path (DIFF-08) — general untuk modul manapun dengan Tour test yang import `stepUtils` langsung. Detail lengkap: `migration-records/crm_probability_from_stage_18_19/SUMMARY.md`.
