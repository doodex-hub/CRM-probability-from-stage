# Code Review — crm_probability_from_stage

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 20.0
**Diff reviewed:** `git diff migration/19.0 8f8d3c3 -- crm_probability_from_stage` (base `ab189bf` = `migration/19.0`, head `8f8d3c3` = Step 6 commit di `migration/20.0`)
**Files reviewed:** `__manifest__.py`, `README.md`, `models/crm_lead.py`, `models/crm_stage.py`, `tests/test_crm_probability_from_stage.py`, `tests/test_crm_probability_tour.py` (+ file tidak berubah dibaca untuk konteks: `models/res_config_settings.py`, `views/*.xml`, `static/tests/tours/*.js`)
**Tanggal:** 2026-09-24

---

## A. Issues

**Status skill `odoo-review`:**
- [x] Terinstall (`.claude/skills/odoo-review`, `odoo-guidelines`, `odoo-security`, `odoo-web-guidelines`) & sudah dijalankan — hasil digabung ke tabel di bawah.

Pemetaan file → section (skill step 2): `__manifest__.py` → Manifest, Changes in a stable version; `models/*.py` → Imports, Naming and model layout, Computes/onchange/constraints, Batch ORM calls, Performance conventions, Changes in a stable version, security "Don't over-sudo" (`sudo()`); `tests/*.py` → Tests, Imports, Naming; `README.md` → Changes in a stable version (dokumentasi). Tidak ada file `static/` yang berubah.

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🔵 Info | Performance (*Batch ORM calls*) | `models/crm_lead.py` | 29 | `get_bool(...)` dipanggil di dalam `for lead in self` — satu panggilan per record. Pola **diwarisi** dari 19.0 (`get_param` juga di dalam loop). Biaya nyata kecil: `_get` di-`ormcache` (`stable`), tiap iterasi cuma `check_access('read')` + cache hit. | Tidak diubah (larangan refactor, bukan wajib kompatibilitas). Kalau suatu saat dioptimasi: angkat keluar loop. |
| CR-02 | 🔵 Info | Konvensi (*Manifest*) | `__manifest__.py` | 17 | `depends` mencantumkan `base` (guideline: jangan). Diwarisi sejak 16.0. | Tidak diubah (P4 manifest = kontrak; stable rule). |
| CR-03 | 🔵 Info | Code Quality (ORM warning) | `models/crm_lead.py` | 9-11 | Redefinisi `probability` related di atas field core compute → `UserWarning` 20.0 tiap registry load (DIFF-14/MF-04). Efek fungsional nihil. | Keputusan dev (MF-04); opsi `compute=None`. |
| CR-04 | 🔵 Info | Security (*Don't over-sudo*) | `models/crm_lead.py`, `models/crm_stage.py` | 29, 17 | `sudo()` untuk baca `ir.config_parameter` — key literal tetap, tidak ada input penyerang (model/record/field/domain). Aman. Tidak berubah dari 19.0 selain nama method. | — |
| CR-05 | 🔵 Info | Tests | `tests/test_crm_probability_from_stage.py` | 49-63 | Test baru memakai `res.config.settings.create(...).execute()` sebagai superuser (`TransactionCase` env) — cukup untuk jalur `set_values`; tidak menguji hak akses non-admin (di luar scope, BSL tidak mengklaimnya). Guideline menyarankan `BaseCommon` untuk test bisnis baru — class existing tetap `TransactionCase`, test baru mengikuti class-nya (stable: match surrounding code). | — |

**Business Logic (manual):** `get_bool` mengembalikan `bool`; cabang `if not is_manually` identik untuk semua nilai yang bisa dihasilkan UI (`'True'` → ON; `'False'`/tidak ada → OFF). Edge case nilai manual non-kanonik → MF-03 (diputuskan). Recordset kosong: loop tidak jalan, sama seperti 19.0. `show_probability` Boolean menerima `bool` langsung (19.0 menerima string yang di-cast ORM) — nilai efektif sama.

**Merits pass:** (1) klaim commit ("OFF stored 'False'") dicocokkan ke `odoo20/odoo/addons/base/models/ir_config_parameter.py` `_set` dan `res_config.py` `set_values` di checkout `odoo20` (dibaca 2026-09-24) — benar. (2) Test gagal tanpa perubahan: dibuktikan dua kontrol negatif (06c). (3) Konsumen kode yang diubah: tidak ada override `_compute_show_probability`/`_compute_is_automated_probability` modul ini di `odoo20`/`enterprise20` selain core `crm` (yang di-override), key `crm.manual.compute.probability` tidak dipakai modul lain. (4) Kasus "run kedua": `set_bool` idempoten (`_set` tidak write kalau nilai sama).

**Guidelines read:** Manifest; Changes in a stable version; Tests; Batch ORM calls; Performance conventions; Imports; Naming and model layout; Computes, onchange and constraints; odoo-security "Don't over-sudo" (+ tabel pola).

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-10 manifest | `20.0.1.0` | ✅ Match | |
| DIFF-01/02 `crm_lead.py` | `get_bool` | ✅ Match | |
| DIFF-01/02 `crm_stage.py` | `get_bool` | ✅ Match | |
| DIFF-03/04 PLS, field | tidak diubah | ✅ Match | |
| DIFF-05/07/08 view | tidak diubah | ✅ Match | |
| DIFF-09 tour | tidak diubah | ✅ Match | G2 PASS |
| Test `_set_toggle`, `test_toggle_saves_config_parameter`, tour asersi | sesuai spec | ✅ Match | |
| Test baru AC-01-05 | `test_settings_toggle_roundtrip_drives_computes` | ✅ Match | |
| A6 README | `Odoo version: 20.0` | ✅ Match (06a A6) | di luar 03, tercatat 06c + koreksi 04 |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01 | toggle tersimpan/terbaca | ✅ | Settings save → `res_config.set_values` `case 'boolean': set_bool` → record `'True'`/`'False'` → modul `get_bool` → `str2bool` → True/False | test + tour |
| AC-01-02/02b | field probability tampil/tersembunyi | ✅ | buka form stage → view `invisible="not show_probability"` → `_compute_show_probability` → `get_bool` → Boolean | unit test; visual Step 10 (MF-02) |
| AC-01-03 | tanpa validasi range | ✅ | `create({'probability': -50})` → tidak ada constraint di model | unit test |
| AC-01-04 | setting di block kedua | ✅ | xpath `//app[@name='crm']/block[2]` → block "Multi Teams/Partnership" 20.0 | tour settings menemukan & mengklik |
| AC-01-05 | jalur Settings ON→OFF | ✅ | `execute()` → `set_values` → `set_bool(False)` simpan `'False'` → compute `get_bool` False → `show_probability` False, `is_automated_probability` = float_compare | test baru; membunuh mutasi `get_str` |
| AC-02-01 | ikut stage | ✅ | write `stage_id` → related `_compute_related` (related menang di 20.0, DIFF-14) → 60 | unit + tour 880 |
| AC-02-02/03 | is_automated | ✅ | compute → `get_bool` → cabang | unit |
| AC-02-04/05 | PLS dua arah | ✅ | `_compute_probabilities` tidak berubah, PLS tuple identik | unit (mock tuple) |
| AC-02-06 | tanpa recompute | ✅ | depends tidak mencakup param | unit |
| AC-03-01/02/03 | revenue | ✅ | compute tidak berubah; list xpath resolve | unit + tour |
| AC-04-01/02 | quirk | ✅ | dead import & CSV ter-comment tidak disentuh (`git diff` tidak menyentuh `res_config_settings.py`, `security/`) | review |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — deviasi dari 19.0 hanya: nama API baca param (wajib), versi manifest, README versi, test disesuaikan + 1 test baru.

**Empat arah:**
1. Arah 1 — method modul bernama sama dengan core (`_compute_is_automated_probability`, `_compute_probabilities` di `crm.lead`) = override total **disengaja sejak 17.0** (BSL-004/006); core 20.0 kedua method identik 19.0, tidak ada side-effect core baru yang hilang.
2. Arah 2 — `revenue_probability`, `_compute_revenue_probability`, `crm.stage.probability`/`show_probability`/`_compute_show_probability`, `crm_manual_compute_probability`: grep `odoo20/addons/{crm*,sale_crm,website_crm*,sales_team}` + `enterprise20/{crm*,*_crm}` → 0 definisi baru. `crm.stage` 20.0 tidak punya field `probability`.
3. Arah 3 — N/A (tidak ada registry UI JS yang di-replace).
4. Arah 4 — N/A (tidak ada entry registry UI baru). Kapabilitas baru native 20.0 di area "probability per stage": tidak ditemukan (`crm.stage` 20.0 cuma menambah rotting/visible domain).
- [x] Sudah dicek (keempat arah) — tidak ada tabrakan/penyimpangan/tumpang-tindih.

## E. Perubahan Tak Tertelusuri

- [x] Tidak ada (README A6 tertelusur ke `06a` A6 + `06c`).

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di step ini (CAND-01..03 sudah dicatat Step 2/6).

## Cek FINDINGS.md

MF-01 (OPEN, non-kode), MF-02 (OPEN → Step 10), MF-03 (RESOLVED), MF-04 (OPEN, keputusan kosmetik, default tidak diubah). Tidak ada `[PERLU-KEPUTUSAN]` yang memblokir.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 5 🔵
- [x] ✅ Lulus — tidak ada 🔴, lanjut ke step 9
- [ ] ❌ Ditolak
