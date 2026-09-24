# Migration Spec (Teknis) — crm_probability_from_stage

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-09-24

> Dokumen ini memandu IMPLEMENTASI (step 6). Dasar testing/acceptance = `01b_BASELINE_SPEC.md` + kode 19.0 (step 5).

---

## 1. Ringkasan Strategi

Port langsung dengan **2 perubahan wajib** di kode produksi: (1) manifest version, (2) ganti `ir.config_parameter.get_param()` (dihapus di 20.0) dengan `get_bool()` di dua compute. Test disesuaikan ke API `set_bool`/`get_bool` dan ke storage 20.0 (OFF = `'False'`), tanpa mengubah perilaku yang diverifikasi. View, PLS override, tour JS: tidak diubah (DIFF-03/05/07/08/09 tidak breaking). Tidak ada refactor lain — dead import (BSL-013), dead dependency (BSL-015), CSV rusak (BSL-016) dipertahankan.

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` `version` | DIFF-10 | `'19.0.1.0'` → `'20.0.1.0'`. `images` tetap `banner.png` (MF-01). | Rendah | — |
| `models/crm_lead.py:27` `_compute_is_automated_probability` | DIFF-01, DIFF-02 | `get_param('crm.manual.compute.probability', False)` → `get_bool('crm.manual.compute.probability')`. Struktur `if not is_manually … else …` tidak diubah. Docstring/komentar tidak diubah; tambah satu komentar singkat alasan 20.0 (sepola komentar tuple 19.0 di method sebelah). | Sedang — salah pilih pengganti = regresi silent (MF-03) | BSL-004, BSL-005 |
| `models/crm_stage.py:16` `_compute_show_probability` | DIFF-01, DIFF-02 | `get_param(..., False)` → `get_bool(...)`. | Sedang (sama) | BSL-002, BSL-009 |
| `models/crm_lead.py` `_compute_probabilities` | DIFF-03 | Tidak diubah. | Rendah | BSL-006 |
| `models/crm_lead.py` field `probability`/`revenue_probability`, `_compute_revenue_probability` | DIFF-04 | Tidak diubah. | Rendah | BSL-007, BSL-008, BSL-015 |
| `models/res_config_settings.py` | DIFF-02 | Tidak diubah (`config_parameter=` tetap valid; `set_values` 20.0 otomatis `set_bool`). Dead import dipertahankan. | Rendah | BSL-001, BSL-013 |
| `views/crm_views.xml` (stage form + list) | DIFF-05, DIFF-07 | Tidak diubah. Posisi field probability pindah ke grup pertama karena native — diterima (larangan redesign). | Rendah | BSL-010, BSL-011 |
| `views/res_config_settings.xml` | DIFF-08 | Tidak diubah. | Rendah | BSL-012 |
| `security/ir.model.access.csv` | DIFF-11 | Tidak diubah, tetap ter-comment. | — | BSL-016 |
| `tests/test_crm_probability_from_stage.py` `_set_toggle` | DIFF-01 | `set_param(key, value)` → `set_bool(key, value)` (tipe sesuai field Boolean — mereplikasi persis yang dilakukan Settings 20.0). | Rendah | — |
| `tests/test_crm_probability_from_stage.py` `test_toggle_saves_config_parameter` | DIFF-01, DIFF-02 | Maksud test (AC-01-01): toggle tersimpan & terbaca balik dua arah. Asersi disesuaikan ke kontrak 20.0: ON → `get_bool` True **dan** nilai mentah `get_str == 'True'`; OFF → `get_bool` False **dan** nilai mentah `'False'` (storage 20.0, bukan lagi "key dihapus"). Komentar BSL-001 diperbarui menjelaskan beda storage 19→20. | Rendah | BSL-001 |
| `tests/test_crm_probability_tour.py` asersi param | DIFF-01 | `get_param(...) == 'True'` → `get_bool(...)` is True (server-side, tetap membuktikan klik tersimpan). | Rendah | BSL-001 |
| **Tambahan test regresi DIFF-02** | DIFF-02 | Tambah 1 test: set toggle ON lalu OFF lewat `res.config.settings` sungguhan (`create({...}).execute()`), lalu assert `show_probability` False dan `is_automated_probability` kembali ikut `float_compare`. Test existing (setelah helper jadi `set_bool`) juga akan menangkap regresi "OFF disimpan `'False'` terbaca truthy" di `test_show_probability_computed`/`test_is_automated_probability_toggle_off`, tapi hanya lewat helper — test baru ini membuktikan jalur yang sebenarnya dipakai user (form Settings → `set_values`), independen dari helper test. | Rendah | BSL-001, BSL-004, BSL-009 |
| `static/tests/tours/*.js` | DIFF-09 | Tidak diubah (verifikasi via G2). | Rendah–Sedang | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan |
|---|---|---|---|
| 1 | Manifest version `20.0.x` | `__manifest__.py` | DIFF-10 |
| 2 | `get_param` → `AttributeError` saat compute | `crm_lead.py:27`, `crm_stage.py:16` | DIFF-01 (kandidat KB baru, `migration-records/crm_probability_from_stage_19.0_20.0/SUMMARY.md` CAND-01) |
| 3 | `set_param`/`get_param` di test (G2 merah) | 2 file test | DIFF-01 |

**Priority:** HIGH — semua di Fase A/B.

### OWL Widget yang Butuh Rewrite/Review
Tidak ada (tidak ada `static/src/`). Tour test JS: cek import path saja (DIFF-09).

### Controller & Route
N/A.

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Bundle `web.assets_tests` glob `static/tests/tours/**/*` | manifest | Rendah — pola sama dipakai 20.0 |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Nilai param tersimpan dari 19.0 (`'True'` atau tidak ada) terbaca benar oleh `get_bool` — relevan cuma kalau suatu saat instance di-upgrade | `ir_config_parameter` | Rendah | BSL-001 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `crm.stage.write()` (toggle `is_won`) memanggil override `_compute_probabilities` → membaca `is_automated_probability` → compute yang diperbaiki di DIFF-01 | `crm.stage` core | Sedang — tercover setelah fix |

### Urutan Prioritas Testing

1. Install & startup (G1) — manifest, load view inherit.
2. Toggle ON/OFF lewat Settings sungguhan → `show_probability`/`is_automated_probability` (DIFF-02).
3. PLS recompute dua arah (BSL-006).
4. Related probability & revenue_probability (BSL-007/008).
5. Tour pipeline + settings (UI).

### View List (dulu Tree) Checklist
Sudah `<list>`/`list` sejak 18.0 — modul tidak punya list view standalone/action. N/A.

## 3. Data Migration

Tidak ada (port kode saja). Lihat §2b Kompatibilitas Data Model #1.

## 4. Scope

### Termasuk
- Manifest version, 2 pemanggilan `get_param` di produksi, penyesuaian test ke API/storage 20.0, 1 test regresi DIFF-02.

### Di Luar Scope (sengaja)
- Aset App Store branch rilis (MF-01).
- Perbaikan quirk BSL-005/013/014/015/016.
- Penyesuaian tata-letak form stage (DIFF-05).
- Hapus anotasi `/** @odoo-module **/` di tour (masih didukung; bukan wajib kompatibilitas).
