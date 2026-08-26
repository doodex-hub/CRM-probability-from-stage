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
| G1 (checkpoint Fase A) | ⏳ Menunggu konfirmasi mode dev | — |
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
| G2 (validasi akhir/runtime) | ⏳ Menunggu G1 | — |

## Riwayat Percobaan G1 (Install Test)

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| — | — | — | Belum dijalankan — menunggu konfirmasi dev soal mode eksekusi (A/B/C) | — | — |

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

---

## Temuan di Luar Spec (kalau ada)

- [x] Tidak ada — semua perubahan tertelusuri ke `03_MIGRATION_SPEC.md`/`02_DIFF_ANALYSIS.md`.

## Kontribusi ke Knowledge Base

- [x] Ada — sudah dicatat SEBELUM Step 6 dimulai (di Step 2, lihat `02_DIFF_ANALYSIS.md` §3): `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` CAND-01 (`_pls_get_naive_bayes_probabilities()` tuple return) dan CAND-02 (`crm.stage.team_id`→`team_ids` + `write()` baru). Tidak ada temuan BARU yang muncul selama eksekusi Fase A1-C1 di luar yang sudah tercatat Step 2 — implementasi berjalan persis sesuai `03_MIGRATION_SPEC.md`.
