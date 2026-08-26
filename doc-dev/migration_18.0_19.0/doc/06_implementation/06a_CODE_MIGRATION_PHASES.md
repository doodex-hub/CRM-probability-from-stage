# Code Migration Phases — crm_probability_from_stage

**Step:** 6 — Code Migration (breakdown granular)
**Ref:** `03_spec/03_MIGRATION_SPEC.md` §2b (Risk Analysis)
**Tanggal:** 2026-08-26

---

## Applicability Check (dari `01a_MIGRATION_INTAKE.md` §2b)

| Fase | Relevan untuk modul ini? | Kalau TIDAK relevan |
|---|---|---|
| C1 — View Sederhana | ☑ Ya (modul punya `views/crm_views.xml` + `views/res_config_settings.xml`, dideklarasikan di manifest `data`) | — |
| B2 — Model Kompleks | ☐ Tidak | Tidak ada relasi berantai >2 level, field JSON, atau dynamic model creation (§2b intake) — N/A |
| C2 — Semantik XML & UX | ☐ Tidak | Tidak ada `attrs=`/`states=`/domain/context dinamis (§2b intake, sudah pakai `invisible="..."` modern sejak 17→18) — N/A |
| D1 — Controllers | ☐ Tidak | Tidak ada folder `controllers/` — N/A |
| D2 — Assets & CSS | ☐ Tidak | Tidak ada `static/src/css/**`; key `assets` manifest cuma `web.assets_tests` untuk tour test (dikonfirmasi tetap valid 19.0, `02_DIFF_ANALYSIS.md` §2b Assets) — tidak butuh perubahan | N/A |
| E — JavaScript (Owl) | ☐ Tidak | Tidak ada komponen Owl custom, cuma 2 file tour test (`registry.category("web_tour.tours")`) — N/A |
| F — Upgrade Template | ☐ Tidak | Otomatis N/A karena E N/A | N/A |

Fase A1-A5 dan B1 berlaku tanpa syarat (semua modul punya manifest & model).

---

## Fase A — Fondasi

### A1 — Manifest Bootstrap
- **Aksi:** `version: '18.0.1.0'` → `'19.0.1.0'`. Tidak ada perubahan lain (`depends`/`data`/`assets` sudah valid 19.0, dikonfirmasi `03_MIGRATION_SPEC.md` §2b Assets & Kompatibilitas Data Model).
- **Status:** ✅ Selesai.

### A2 — XML Tree → List
- **Status:** N/A — dikonfirmasi `knowledge/version-diffs/18-to-19.md` §2: perubahan `<tree>`→`<list>` terjadi di 17.0, SUDAH selesai di migrasi 17→18 sebelumnya. Modul ini tidak punya `<tree>` tersisa (dikonfirmasi baca `views/crm_views.xml`/`views/res_config_settings.xml` sesi ini — keduanya cuma pakai `<xpath>`/inline field, tidak ada tag `<tree>`/`<list>` standalone).

### A3 — Security Hardening
- **Status:** N/A untuk perubahan — `security/ir.model.access.csv` dipertahankan rusak/tidak terpakai apa adanya (BSL-016, di-comment-out di manifest). Tidak ada TransientModel baru yang butuh ACL (satu-satunya TransientModel, `res.config.settings`, sudah punya ACL native dari `base`).

### A4 — Skeleton & Folder Integrity
- **Status:** ✅ Dikonfirmasi — struktur folder (`models/`, `views/`, `security/`, `static/`, `tests/`, `i18n/`) dan `__init__.py` konsisten, tidak ada yang hilang/perlu dibuat.

### A5 — Python API Compatibility
- **Aksi:** Fix DIFF-01 — `models/crm_lead.py` `_compute_probabilities()`: `lead_probabilities = self._pls_get_naive_bayes_probabilities()` → `lead_probabilities, _tooltip_data = self._pls_get_naive_bayes_probabilities()` (unpack tuple, mengikuti pola pemanggilan yang SAMA persis dengan cara core 19.0 sendiri memanggilnya, lihat `enterprise19.0/odoo/addons/crm/models/crm_lead.py:560`).
- **Status:** ✅ Selesai. Detail lengkap: `06c_IMPLEMENTATION_LOG.md`.

### Checkpoint G1 — Install Test
- **Status:** ⏳ Belum dijalankan — menunggu konfirmasi dev soal mode eksekusi (A/B/C). Lihat `06c_IMPLEMENTATION_LOG.md` "Riwayat Percobaan G1".

---

## Fase B — Python Models (Semantik)

### B1 — Model Risiko Rendah
- **Scope:** `crm_stage.py`, `res_config_settings.py` (keduanya model sederhana).
- **Status:** ✅ Dikonfirmasi tidak ada perubahan wajib — `02_DIFF_ANALYSIS.md` DIFF-02 (tidak dipakai), tidak ada perubahan API relevan di kedua file.

### B2 — Model Kompleks
- **Status:** N/A (Applicability Check).

---

## Fase C — XML Views (Non-OWL)

### C1 — View Sederhana
- **Status:** ✅ Dikonfirmasi tidak ada perubahan kode wajib — kedua xpath (`crm_views.xml`, `res_config_settings.xml`) tetap resolve ke target yang benar di 19.0 (DIFF-04, DIFF-05, DIFF-06 — semua "Tidak berubah"/"kosmetik", lihat `02_DIFF_ANALYSIS.md`).

### C2 — Semantik XML & Konsistensi UX
- **Status:** N/A (Applicability Check).

---

## Fase D — Controllers & Assets
- **Status:** N/A (Applicability Check, D1 & D2).

## Fase E — JavaScript (Owl)
- **Status:** N/A (Applicability Check).

## Fase F — Upgrade Template
- **Status:** N/A (otomatis, karena E N/A).

## Fase G2 — Validasi Akhir
- **Status:** ⏳ Menunggu server hidup (setelah G1) — scope sempit, cuma verifikasi DIFF-01 valid di runtime (lihat `06c_IMPLEMENTATION_LOG.md`).
