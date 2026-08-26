# Spec Completeness Review — crm_probability_from_stage

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `source-codebase` (`D:\Kuncoro\doodex\repo\CRM-probability-from-stage-migration-18-source\crm_probability_from_stage`)
**Tanggal:** 2026-08-24

---

## Tabel Cakupan

Enumerasi LENGKAP tiap file di `source-codebase` (bukan cuma yang "kelihatan penting") — dicek langsung via listing folder.

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | Ya, §2 baris 1 | ✅ Covered | Version bump `18.0.1.0` |
| `__init__.py` (root) | Tidak eksplisit di §2 | ✅ Covered (implisit) | `from . import models` — trivial, tidak ada perubahan versi-terkait apapun, port 1:1 tanpa modifikasi |
| `models/__init__.py` | Tidak eksplisit di §2 | ✅ Covered (implisit) | `from . import crm_stage, crm_lead, res_config_settings` — trivial, port 1:1 |
| `models/crm_lead.py` | Ya, §2 baris 2-3 | ✅ Covered | DIFF-01 (rename `aggregator`), sisanya 1:1 |
| `models/crm_stage.py` | Ya, §2 baris 4 | ✅ Covered | Port 1:1 |
| `models/res_config_settings.py` | Ya, §2 baris 5 | ✅ Covered | Port 1:1, termasuk dead import (BSL-013) |
| `views/crm_views.xml` | Ya, §2 baris 6 | ✅ Covered | DIFF-02, DIFF-03, port 1:1 |
| `views/res_config_settings.xml` | Ya, §2 baris 7 | ✅ Covered | DIFF-04, port 1:1 |
| `security/ir.model.access.csv` | Ya, §2 baris 8 | ✅ Covered | Port 1:1 apa adanya (rusak, comment-out) — MF-01 |
| `i18n/*.po` (es, fr, id, nl, pt) | Ya, §2 baris 9 | ✅ Covered | Port 1:1, tidak ada string baru yang butuh terjemahan (tidak ada perubahan UI-facing) |
| `static/description/icon.png`, `banner.png`, `index.html`, `assets/*.png(.bak)` | Tidak eksplisit di §2 (bukan kode) | ✅ Covered (implisit) | Aset deskripsi Apps store — tidak ada logic/versi-spesifik, port 1:1 |
| `README.md` | Tidak eksplisit di §2 (bukan kode) | ✅ Covered (implisit) | Konten marketing, tidak ada elemen teknis versi-spesifik. Baris "Compatibility: Odoo version: 17.0" (source) perlu diupdate ke `18.0` saat port — ditambahkan sebagai item eksplisit di §Verdict di bawah |
| `LICENSE` | Tidak eksplisit di §2 (bukan kode) | ✅ Covered (implisit) | Port 1:1, tidak ada perubahan (larangan ubah copyright/lisensi tanpa alasan) |

**Elemen struktural yang TIDAK ada di source module ini** (dicek eksplisit supaya jelas bukan terlewat): `controllers/`, `data/`, `report/`, `wizard/`, `static/src/` (JS/Owl/CSS), `tests/`. Semua N/A — dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b.

## Gap Ditemukan Saat Review Ini

- **README.md — baris "Compatibility: Odoo version: 17.0"** tidak disebutkan eksplisit di `03_MIGRATION_SPEC.md` §4 (Termasuk). Ini bukan celah risiko teknis (tidak mempengaruhi install/runtime), tapi tetap bagian dari "port kode saja" yang seharusnya konsisten — ditambahkan ke §4 Migration Spec sebagai item kecil tambahan (lihat update di bawah).

## Verdict

- [x] ✅ Lulus — semua elemen Covered (13 file/folder dicek, 0 gap teknis; 1 gap dokumentasi minor ditemukan & diperbaiki langsung di bawah), lanjut ke step 5.
