# Implementation Log — crm_probability_from_stage

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-09-24

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 | ☑ Ya | 2 file view inherit (`views/crm_views.xml`, `views/res_config_settings.xml`) |
| B2 | ☐ Tidak | tidak ada field JSON/relasi berantai/dynamic model |
| C2 | ☐ Tidak | tidak ada `attrs=`/`states=`/domain dinamis; `invisible="not show_probability"` sudah sintaks 17+ |
| D1 | ☐ Tidak | tidak ada `controllers/` |
| D2 | ☑ Ya (terbatas) | bundle `web.assets_tests` (2 tour) — cek bundle termuat |
| E | ☑ Ya (terbatas) | tidak ada Owl; import path tour `@web_tour/tour_utils` dicek (pelajaran CAND-03 18→19) |
| F | ☐ Tidak | tidak ada template Owl |

## Mode Eksekusi G1/G2

**Mode C — AI jalankan langsung** (Claude Code CLI, shell persisten, Docker Desktop tersedia). Tidak ditanyakan interaktif: instruksi sesi dev = "jalan terus sampai Step 9 selesai dan lulus gate" (mencakup eksekusi test oleh AI; Mode C juga dipakai di 18→19). Environment: `docker-env/` ditulis ulang — `python:3.12-slim-bookworm` + Chrome, Odoo 20.0 dijalankan dari source `odoo20` (mount read-only, belum ada image resmi `odoo:20.0`), Postgres 16, port host 8179. Tiap run diawali `docker compose down -v`.

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-09-24 |
| A2 | N/A — sudah `<list>` sejak 18.0, tidak ada `<tree>` | 2026-09-24 |
| G1 #1 | ✅ PASS | 2026-09-24 |
| A3 | N/A — CSV security ter-comment (BSL-016), tidak ada model/wizard baru | 2026-09-24 |
| A4 | ✅ (tidak ada perubahan) | 2026-09-24 |
| A5 | ✅ | 2026-09-24 |
| A6 | ✅ | 2026-09-24 |
| B1 | ✅ (digabung A5 — satu-satunya perubahan Python) | 2026-09-24 |
| B2 | N/A — Applicability Check | |
| C1 | ✅ (tidak ada perubahan) | 2026-09-24 |
| C2 | N/A — Applicability Check | |
| D1 | N/A — Applicability Check | |
| D2 | ✅ (tidak ada perubahan) | 2026-09-24 |
| E | ✅ (tidak ada perubahan) | 2026-09-24 |
| F | N/A — Applicability Check | |
| G2 | ✅ PASS 14/14 (+2 suite JS `web` no-op) | 2026-09-24 |

## Riwayat Percobaan G1 / G2

| # | Dijalankan setelah fase | Mode | Hasil | Error / catatan | Tanggal |
|---|---|---|---|---|---|
| G1 #1 | A1 (A2/A3 N/A) | C | ☑ Pass | Install bersih, `Modules loaded`, 0 ERROR. 1 warning baru: `Field crm.lead.probability is both compute and related` (lihat Temuan di Luar Spec #1). Log: `docker-env/logs/g1_run1.log` | 2026-09-24 |
| G2 #1 | A1–E (kode final) | C | ☑ Pass | `0 failed, 0 error(s) of 16 tests` — 12 TransactionCase + 2 tour modul + 2 suite JS `web` (no-op). Kedua tour lewat semua step (11/11, 4/4) | 2026-09-24 |
| Kontrol negatif #1 | mutasi `get_bool`→`get_str` di 2 compute | C | ☑ Merah seperti diharapkan | `5 failed` (toggle_off, pls_toggle_off, **settings_roundtrip (AC-01-05)**, show_probability, toggle_change_no_auto_recompute) — membuktikan test menangkap regresi DIFF-02. Kode dikembalikan. Log: `logs/mutation_get_str.log` | 2026-09-24 |
| Kontrol negatif #2 | kode model 19.0 apa adanya (`git show migration/19.0:...`) | C | ☑ Merah seperti diharapkan | Install **PASS**, `6 error(s)` `AttributeError: 'ir.config_parameter' object has no attribute 'get_param'`. **Kedua tour tetap PASS** — alur kanban/list/settings tidak membaca `is_automated_probability`/`show_probability`. Membuktikan DIFF-01 tidak tertangkap G1 maupun tour. Kode dikembalikan. Log: `logs/unmigrated_19_models.log` | 2026-09-24 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 1, DIFF-10
- **Aksi:** `'version': '19.0.1.0'` → `'20.0.1.0'`
- **Secara eksplisit TIDAK dilakukan:** `depends`, `data` (termasuk baris CSV ter-comment), `assets`, `images` (`banner.png`, MF-01), `license`, summary/description tidak diubah.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] N/A — tidak ada `<tree>`/`view_mode tree` (dicek `grep -rn "<tree\|tree," views/` → 0)

## [Fase A3] N/A — `security/ir.model.access.csv` tidak dimuat (BSL-016); modul tidak menambah model/TransientModel

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** struktur folder + `__init__.py`
- **Aksi:** dicek, tidak ada perubahan (`models/`, `views/`, `security/`, `static/`, `tests/`, `i18n/`, `__init__.py` konsisten).
- **Risiko:** LOW — **Status:** ✅

## [Fase A5 + B1] Python API Compatibility

- **Scope:** `models/crm_lead.py`, `models/crm_stage.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 2–3, DIFF-01/02, MF-03
- **Aksi:**
  - `models/crm_lead.py` `_compute_is_automated_probability`: `get_param('crm.manual.compute.probability', False)` → `get_bool('crm.manual.compute.probability')` + komentar 2 baris alasan 20.0.
  - `models/crm_stage.py` `_compute_show_probability`: idem + komentar 1 baris.
- **Secara eksplisit TIDAK dilakukan:** struktur `if not is_manually / else`, `@api.depends`, docstring, `_compute_probabilities`, definisi field `probability` (termasuk warning compute+related — lihat Temuan #1), `revenue_probability`, dead import `res_config_settings.py` (BSL-013), dead dependency `partner_id` (BSL-015). Tidak ada perubahan business logic.
- **Risiko:** MEDIUM (salah pilih pengganti = regresi silent) — dimitigasi kontrol negatif #1.
- **Status:** ✅ Selesai

## [Fase A6] Housekeeping README

- **Scope:** `crm_probability_from_stage/README.md`
- **Aksi:** `Odoo version: 18.0` → `Odoo version: 20.0` (baris "Compatibility" — basi sejak 19.0; branch rilis `19.0` sendiri sudah mengubahnya ke 19.0). *Koreksi atas `04_SPEC_COMPLETENESS_REVIEW.md` yang menulis README "sengaja tidak diubah" — template 06a A6 mewajibkan perbaikan baris versi yang basi.*
- **Secara eksplisit TIDAK dilakukan:** konten marketing/instalasi lain tidak diubah.
- **Risiko:** LOW — **Status:** ✅

## [Fase B2] N/A — Applicability Check (01a §2b)

## [Fase C1] View Sederhana

- **Scope:** `views/crm_views.xml`, `views/res_config_settings.xml`
- **Aksi:** tidak ada perubahan — ketiga xpath resolve di 20.0 (G1 PASS, tour settings & pipeline menemukan elemen). Posisi field probability di form stage pindah ke grup pertama karena native (DIFF-05) — tidak dikoreksi (larangan redesign).
- **Risiko:** LOW — **Status:** ✅

## [Fase C2] N/A — Applicability Check

## [Fase D1] N/A — Applicability Check

## [Fase D2] Assets

- **Scope:** manifest `assets.web.assets_tests`
- **Aksi:** tidak ada perubahan — bundle test termuat (`odoo.isTourReady(...)` true untuk kedua tour).
- **Risiko:** LOW — **Status:** ✅

## [Fase E] JavaScript (tour test)

- **Scope:** `static/tests/tours/*.js`
- **Aksi:** tidak ada perubahan — `@web_tour/tour_utils` resolve, `stepUtils.showAppsMenuItem()`, run `edit`/`click`/`drag_and_drop` jalan di 20.0 (G2 #1). Anotasi `/** @odoo-module **/` dipertahankan (masih didukung).
- **Risiko:** LOW — **Status:** ✅

## [Fase F] N/A — Applicability Check

## [Fase G2] Validasi Akhir (test suite)

- **Scope:** `tests/test_crm_probability_from_stage.py`, `tests/test_crm_probability_tour.py`, `docker-env/`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris test
- **Aksi:**
  - `_set_toggle`: `set_param` → `set_bool` (sama dengan yang dipakai `res.config.settings.set_values` 20.0).
  - `test_toggle_saves_config_parameter`: asersi ke `get_bool` + nilai mentah `get_str` (`'True'`/`'False'`); komentar BSL-001 diperbarui (storage 19.0 vs 20.0).
  - Test BARU `test_settings_toggle_roundtrip_drives_computes` (AC-01-05): ON→OFF lewat `res.config.settings.create(...).execute()`, assert `show_probability` & `is_automated_probability`.
  - Docstring class: rujukan dokumen 18→19 → 19→20.
  - `test_crm_probability_tour.py`: asersi `get_param(...) == 'True'` → `get_bool(...) is True`.
  - `docker-env/Dockerfile.target`, `docker-env/docker-compose.yml` ditulis ulang untuk 20.0; `docker-env/requirements.txt` baru (salinan `odoo20/requirements.txt`).
- **Secara eksplisit TIDAK dilakukan:** 10 test lain tidak diubah (termasuk mock tuple PLS); tour JS tidak diubah.
- **Risiko:** LOW — **Status:** ✅ PASS (G2 #1)

---

## Temuan di Luar Spec

- [x] Ada:
  1. **Warning ORM 20.0 `Field crm.lead.probability is both compute and related. Set one of them to None.`** (`odoo20/odoo/orm/fields.py:478`, muncul tiap registry load). Redefinisi `probability` modul (`related=...`) mewarisi `compute='_compute_probabilities'` dari definisi core. 19.0 dan 20.0 **sama-sama** membuat related menang (`setup_related` → `self.compute = self._compute_related`, `odoo19/.../fields.py:632`, `odoo20/.../fields.py:674`); 20.0 cuma menambah `attrs.pop('compute')` + warning. Behavior BSL-007 identik (AC-02-01 PASS, tour 880 PASS). **Tidak diubah** (bukan wajib kompatibilitas; `compute=None` eksplisit = perubahan kosmetik log). Dicatat `02_DIFF_ANALYSIS.md` DIFF-14 + `FINDINGS.md` MF-04 (keputusan dev, default: biarkan).
  2. **Tour tidak menangkap DIFF-01** (kontrol negatif #2) — diteruskan ke Step 10: skenario live WAJIB membuka form opportunity dan form stage.

## Kontribusi ke Knowledge Base

- [x] Ada — `migration-records/crm_probability_from_stage_19.0_20.0/SUMMARY.md`: CAND-01 diperkuat bukti eksekusi (kontrol negatif #1/#2); CAND-03 baru (warning compute+related untuk redefinisi field lewat `_inherit`).
