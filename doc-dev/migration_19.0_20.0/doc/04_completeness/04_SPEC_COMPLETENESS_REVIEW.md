# Spec Completeness Review — crm_probability_from_stage

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, source `migration/19.0` (`git ls-files crm_probability_from_stage`, 31 file)
**Tanggal:** 2026-09-24

> Enumerasi SEMUA file tracked di modul source (bukan cuma yang "kelihatan relevan"), dicocokkan ke spec.

---

## Tabel Cakupan

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__manifest__.py` | Ya — §2 baris 1 | ✅ Covered | version bump; `depends`/`data`/`assets`/`images` tetap |
| `__init__.py`, `models/__init__.py`, `tests/__init__.py` | Implisit (tidak diubah) | ✅ Covered | import relatif standar, tidak terdampak DIFF manapun |
| `models/crm_lead.py` — field `probability`, `revenue_probability` | Ya — §2 | ✅ Covered | DIFF-04, tidak diubah |
| `models/crm_lead.py` — `_compute_revenue_probability` | Ya — §2 | ✅ Covered | BSL-008/015 |
| `models/crm_lead.py` — `_compute_is_automated_probability` | Ya — §2 | ✅ Covered | DIFF-01 → `get_bool` |
| `models/crm_lead.py` — `_compute_probabilities` | Ya — §2 | ✅ Covered | DIFF-03, tidak diubah |
| `models/crm_lead.py` — import `from odoo import _, api, fields, models, tools` | Ya — DIFF-12 (02) | ✅ Covered | tetap valid |
| `models/crm_stage.py` — `probability`, `show_probability`, `_compute_show_probability` | Ya — §2 | ✅ Covered | DIFF-01 → `get_bool` |
| `models/res_config_settings.py` | Ya — §2 | ✅ Covered | tidak diubah (DIFF-02 otomatis `set_bool`) |
| `views/crm_views.xml` — stage form inherit | Ya — §2 | ✅ Covered | DIFF-05, tidak diubah |
| `views/crm_views.xml` — list inherit | Ya — §2 | ✅ Covered | DIFF-07 |
| `views/res_config_settings.xml` | Ya — §2 | ✅ Covered | DIFF-08 |
| `security/ir.model.access.csv` | Ya — §2 | ✅ Covered | DIFF-11/BSL-016, tidak dimuat |
| `i18n/{es,fr,id,nl,pt}.po` | Tidak eksplisit di 03 | ✅ Covered (tidak perlu aksi) | msgid merujuk string view/field yang tidak berubah (`<span class="oe_grey"> %</span>`, label field, help setting). Header `Project-Id-Version: 16.0+e` usang sejak 16.0 — metadata, tidak dipakai loader. Tidak diubah. |
| `static/tests/tours/*.js` (2) | Ya — §2 | ✅ Covered | DIFF-09, verifikasi G2 |
| `tests/test_crm_probability_from_stage.py` | Ya — §2 | ✅ Covered | helper + 1 test disesuaikan + 1 test baru |
| `tests/test_crm_probability_tour.py` | Ya — §2 | ✅ Covered | asersi `get_bool` |
| `static/description/{banner.png,icon.png,index.html,assets/*}` | Ya — §4 Di Luar Scope (MF-01) | ✅ Covered | tidak diubah |
| `README.md` (tertulis "Odoo version: 18.0") | Tidak eksplisit | ✅ Covered (sengaja tidak diubah) | Sudah usang sejak 19.0 (18→19 juga tidak mengubahnya); dokumentasi, bukan behavior. Branch rilis mengurus README-nya sendiri (MF-01). **Koreksi Step 6 (2026-09-24):** template `06a` Fase A6 mewajibkan perbaikan baris versi yang basi → diubah ke "Odoo version: 20.0" (lihat `06c_IMPLEMENTATION_LOG.md` A6). |
| `LICENSE` | — | ✅ Covered | tidak diubah |
| `controllers/`, `data/`, `report/`, `wizard/` | — | N/A | tidak ada di modul |
| `docker-env/` (infra repo, bukan modul) | Tidak di 03 | ✅ Covered di Step 6 | ditulis ulang untuk 20.0 (image resmi `odoo:20.0` belum ada — build-from-source, pola `optional_field_save` 19→20) |

## Cek FINDINGS.md (wajib gate)

| MF | Status | Blocking Step 5+? |
|---|---|---|
| MF-01 | OPEN, default dipakai (tidak di-port) | Tidak — di luar scope kode |
| MF-02 | OPEN, diteruskan ke Step 10 | Tidak untuk Step 5–9 |
| MF-03 | RESOLVED (keputusan AI `get_bool`) | Tidak |

Tidak ada finding `[PERLU-KEPUTUSAN]` yang memblokir implementasi.

## Verdict

- [x] ✅ Lulus — semua elemen Covered, lanjut ke step 5
- [ ] ❌ Ditolak
