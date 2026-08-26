# Migration Spec (Teknis) — crm_probability_from_stage

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

---

## 1. Ringkasan Strategi

Port kode 1:1 dari `source-codebase` (17.0). Diff analysis (Step 2) menemukan risiko keseluruhan **Rendah** — tidak ada Critical Migration Blocker. Satu-satunya perubahan kode yang direkomendasikan: rename `group_operator` → `aggregator` (DIFF-01, kosmetik/deprecation, bukan wajib untuk install berhasil). Manifest version bump `17.0.1.0` → `18.0.1.0`. Tidak ada perubahan XML/view apapun yang diperlukan (semua xpath target byte-identical atau tetap valid, lihat DIFF-02/03/04). Tidak ada Fase Owl/JS/Controller/Assets — semua N/A (`01a_MIGRATION_INTAKE.md` §2b).

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` | — | Update `'version': '18.0.1.0'` | Tidak ada | — |
| `models/crm_lead.py` — field `probability` | DIFF-01 | Rename param `group_operator="avg"` → `aggregator="avg"` | Tidak ada (non-breaking baik sebelum/sesudah) | BSL-007 |
| `models/crm_lead.py` — sisanya (`revenue_probability`, `_compute_revenue_probability`, `_compute_is_automated_probability`, `_compute_probabilities`) | DIFF-05, DIFF-06 | Port 1:1, tanpa perubahan sama sekali | Tidak ada | BSL-004, 005, 006, 008 |
| `models/crm_stage.py` | — | Port 1:1, tanpa perubahan | Tidak ada | BSL-009 |
| `models/res_config_settings.py` | — | Port 1:1, tanpa perubahan (termasuk dead import `timedelta`/`relativedelta` — dipertahankan) | Tidak ada | BSL-013 |
| `views/crm_views.xml` | DIFF-02, DIFF-03 | Port 1:1, tanpa perubahan | Tidak ada | BSL-010, BSL-011 |
| `views/res_config_settings.xml` | DIFF-04 | Port 1:1, tanpa perubahan (xpath `block[2]`/`inside` tetap valid meski posisi tampil bergeser — kosmetik, lihat DIFF-04) | Sangat rendah (kosmetik) | BSL-012 |
| `security/ir.model.access.csv` | — | Port 1:1 apa adanya (rusak + comment-out) — **jangan diperbaiki** | Tidak ada (tidak dimuat) | BSL-016 (MF-01) |
| `i18n/*.po` | — | Port 1:1, tanpa perubahan | Tidak ada | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `18.0.x` | `__manifest__.py` | `knowledge/version-diffs/17-to-18.md` |

**Tidak ada blocker lain** — dikonfirmasi Step 2: tidak ada `<tree>`/`<list>` yang didefinisikan modul ini, tidak ada dependency Enterprise yang dihapus, tidak ada API core yang di-override dengan signature yang berubah.

**Priority:** HIGH (manifest) — perbaiki sebelum runtime testing apapun. Tidak ada isu lain di kategori ini.

### OWL Widget yang Butuh Rewrite/Review

N/A — modul tidak punya komponen Owl/JS sama sekali (`01a_MIGRATION_INTAKE.md` §2b).

### Controller & Route

N/A — modul tidak punya controller.

### Assets & Dependency

N/A — modul tidak punya asset registration (`static/src/`, key `assets`).

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Tidak ada — semua field/model yang di-inherit (`crm.lead`, `crm.stage`, `res.config.settings`) stabil 17.0↔18.0 (DIFF-02, 03, 05, 06) | — | — | — |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | DIFF-04 — setting custom akan tampil setelah "Ringover VOIP Phone" (baru di 18.0) bukan lagi tepat setelah "Assign salespersons into multiple Sales Teams" | `views/res_config_settings.xml` | Low (kosmetik, verifikasi visual di Step 10) |

### Urutan Prioritas Testing

1. Install & startup — manifest version, dependency `base`/`crm` resolve normal (tidak ada `create()` custom yang perlu `@api.model_create_multi`, modul tidak override `create`)
2. Core user flow — set probability per stage (Settings → CRM Stages), toggle Settings → CRM "Probability from stage", buat/pindah stage opportunity, cek `probability`/`revenue_probability` di form & list Opportunities
3. Persistensi data — `probability`/`revenue_probability`/`show_probability`/`crm_manual_compute_probability` (config_parameter) tersimpan benar
4. Widget backend — N/A (tidak ada Owl)
5. Interaksi PLS (BSL-006/007, MF-02) — pindah stage TANPA toggle vs DENGAN toggle aktif, cross-check `is_automated_probability`

### View List (dulu Tree) Checklist

N/A — modul tidak mendefinisikan `<tree>`/`<list>` standalone apapun, cuma xpath ke view existing (DIFF-02, DIFF-03). Tidak ada `view_mode` di action yang didefinisikan modul ini (modul tidak punya `ir.actions.act_window` sendiri).

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Code migration (Step 6) | Sangat rendah | 1 baris kode berubah (`group_operator`→`aggregator`) + 1 baris manifest version |
| Testing (Step 9/10) | Rendah-sedang | Modul kecil, tapi interaksi PLS (MF-02) butuh 2 skenario terpisah, bukan 1 |

## 3. Data Migration

N/A — sifat migrasi "port kode saja" (`01a_MIGRATION_INTAKE.md` §3), belum ada data produksi. Step 7 tidak dijalankan.

## 4. Scope

### Termasuk
- Rename `group_operator` → `aggregator` di `models/crm_lead.py` (DIFF-01)
- Update `__manifest__.py` versi ke `18.0.1.0`
- Update `README.md` baris "Compatibility: Odoo version: 17.0" → `18.0` (ditemukan Step 4 Spec Completeness Review — konsistensi dokumentasi, bukan risiko teknis)

### Di Luar Scope (sengaja, disetujui di intake)
- Memperbaiki `security/ir.model.access.csv` yang rusak (MF-01) — dipertahankan apa adanya
- Memperbaiki dead import (`timedelta`/`relativedelta`, BSL-013) dan dead dependency (`partner_id` di `_compute_revenue_probability`, BSL-015)
- Menambah validasi range 0-100 untuk field `probability` di `crm.stage` (BSL-014)
- Mengubah posisi tampil setting custom di Settings → CRM (DIFF-04) — kosmetik, tidak masuk scope perbaikan
