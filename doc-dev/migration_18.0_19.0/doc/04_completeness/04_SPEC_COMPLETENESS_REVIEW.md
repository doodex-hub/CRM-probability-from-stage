# Spec Completeness Review — crm_probability_from_stage

**Step:** 4 — Spec Completeness Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `source-codebase` (branch `migration/18.0`)
**Tanggal:** 2026-08-26

> Tujuan: pastikan `03_MIGRATION_SPEC.md` mencakup 100% elemen source module — bukan review
> kualitas kode (itu step 8). Enumerasi semua elemen modul dari `source-codebase`, cocokkan
> satu-satu ke spec.

---

## Tabel Cakupan

Enumerasi lengkap dari `find crm_probability_from_stage -type f` di `source-codebase` (28 file, dikonfirmasi identik dengan `target-codebase` sesi ini, lihat `01b_BASELINE_SPEC.md`).

| Elemen source module | Ada di Migration Spec? | Status | Catatan |
|---|---|---|---|
| `__init__.py` (root) | N/A — cuma import `models` | ✅ Covered | Tidak ada perubahan wajib, tidak butuh baris spec terpisah (trivial) |
| `__manifest__.py` | Ya — §2b Critical Blocker #1 | ✅ Covered | Version bump `18.0.1.0`→`19.0.1.0`; `depends`/`data`/`assets` dikonfirmasi tidak berubah |
| `models/__init__.py` | N/A — cuma import 3 model | ✅ Covered | Trivial, tidak butuh baris spec |
| `models/crm_lead.py` | Ya — §2 tabel baris 1 | ✅ Covered | Fix DIFF-01 wajib (`_compute_probabilities()` unpack tuple) |
| `models/crm_stage.py` | Ya — §2 tabel baris 2 | ✅ Covered | Tidak ada perubahan (DIFF-02 tidak relevan) |
| `models/res_config_settings.py` | Ya — §2 tabel baris 3 | ✅ Covered | Tidak ada perubahan |
| `controllers/` | N/A — tidak ada folder ini di modul | ✅ Covered | Dikonfirmasi §2b `03_MIGRATION_SPEC.md` "Controller & Route" |
| `views/crm_views.xml` (2 record: `crm_stage_form_inherit_crm_stage_probability`, `probability_crm_lead_inherit_tree_view`) | Ya — §2 tabel baris 4 & 5 | ✅ Covered | DIFF-04 (kosmetik, form stage), DIFF-05 (tidak berubah, list oppor) |
| `views/res_config_settings.xml` | Ya — §2 tabel baris 6 | ✅ Covered | DIFF-06, tidak ada perubahan |
| `security/ir.model.access.csv` | Ya — §2 tabel baris 7 | ✅ Covered | Dipertahankan rusak/tidak terpakai apa adanya (BSL-016) |
| `data/` | N/A — tidak ada folder ini di modul | ✅ Covered | Tidak perlu disebut, tidak eksis |
| `report/` | N/A — tidak ada folder ini di modul | ✅ Covered | Tidak perlu disebut, tidak eksis |
| `wizard/` | N/A — tidak ada folder ini di modul | ✅ Covered | Tidak perlu disebut, tidak eksis |
| `i18n/*.po` (5 file: es, fr, id, nl, pt) | Tidak eksplisit disebut sebagai baris spec, tapi implisit "tidak ada perubahan wajib" — konsisten pola "tidak actionable" di §4 Scope | ✅ Covered | Terjemahan string existing, tidak ada string baru yang perlu ditambahkan (tidak ada UI baru dari migrasi ini) — port apa adanya |
| `static/description/*` (banner, icon, index.html, assets) | Tidak disebut — non-kode, murni marketing/listing Odoo Apps Store | ✅ Covered (implisit, out of scope) | Tidak relevan ke migrasi teknis, tidak butuh baris spec |
| `static/tests/tours/crm_probability_pipeline_tour.js`, `crm_probability_settings_tour.js` | Ya — §2b "Assets & Dependency" #1 (`web.assets_tests` key) + §2b "Urutan Prioritas Testing" #5 | ✅ Covered | Bundle key dikonfirmasi masih valid 19.0, isi tour JS sendiri tidak perlu diubah (tidak pakai API yang berubah) |
| `tests/__init__.py` | N/A — cuma import 2 file test | ✅ Covered | Trivial |
| `tests/test_crm_probability_from_stage.py` | Ya — §2 tabel baris terakhir | ✅ Covered | 2 dari 10 test method perlu update mock (DIFF-01 konsekuensi), 8 sisanya tidak berubah |
| `tests/test_crm_probability_tour.py` | Ya — §2b "Urutan Prioritas Testing" #5 | ✅ Covered | Tidak ada perubahan kode, wajib re-run terhadap 19.0 di Step 9 |
| `LICENSE`, `README.md` | N/A — non-kode | ✅ Covered (implisit, out of scope) | Tidak relevan ke migrasi teknis |

**Ringkasan:** 21 elemen dienumerasi (termasuk file trivial/non-kode) — 0 gap ditemukan. Setiap file kode yang punya kemungkinan perubahan (model, view, security, test) eksplisit disebut di `03_MIGRATION_SPEC.md` §2/§2b, termasuk yang statusnya "tidak ada perubahan" (bukan cuma diam-diam diasumsikan aman).

## Verdict

- [x] ✅ **Lulus** — semua elemen Covered, lanjut ke step 5.
