# Implementation Log — crm_probability_from_stage

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 | ☐ Tidak | Tidak ada model kompleks/relasi berantai/field JSON/dynamic creation |
| C2 | ☐ Tidak | Tidak ada `attrs=`/`states=`/domain/context dinamis (source 17.0 sudah pakai `invisible=` langsung) |
| D1 | ☐ Tidak | Tidak ada controller |
| D2 | ☐ Tidak | Tidak ada asset/CSS custom |
| E | ☐ Tidak | Tidak ada komponen Owl/JS |
| F | ☐ Tidak | Otomatis N/A (E juga N/A) |

C1 (View Sederhana) **Ya relevan** — modul punya `views/crm_views.xml` + `views/res_config_settings.xml`, keduanya di manifest `data`.

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ | 2026-08-24 |
| A2 | N/A — tidak ada `<tree>` didefinisikan modul ini (DIFF-02/03, lihat `02_DIFF_ANALYSIS.md`) | 2026-08-24 |
| A3 | N/A — tidak ada model baru yang butuh ACL; `ir.model.access.csv` existing rusak/comment-out dipertahankan apa adanya (MF-01) | 2026-08-24 |
| G1 (satu checkpoint — A2/A3 N/A jadi tidak perlu 2 titik terpisah, lihat tabel "Riwayat Percobaan G1" di bawah) | ✅ Pass | 2026-08-24 |
| A4 | ✅ — struktur folder/`__init__.py` sudah konsisten, tidak ada yang hilang | 2026-08-24 |
| A5 | ✅ — `group_operator`→`aggregator` | 2026-08-24 |
| B1 | ✅ — 3 model inherit dicek, tidak ada perubahan | 2026-08-24 |
| B2 | N/A — dikonfirmasi Applicability Check | |
| C1 | ✅ — 2 view inherit dicek (DIFF-02/03/04), tidak ada perubahan | 2026-08-24 |
| C2 | N/A — dikonfirmasi Applicability Check | |
| D1 | N/A — dikonfirmasi Applicability Check | |
| D2 | N/A — dikonfirmasi Applicability Check | |
| E | N/A — dikonfirmasi Applicability Check | |
| F | N/A — dikonfirmasi Applicability Check | |
| G2 (validasi akhir/runtime) | lihat `08_review`/`09_devtest` | |

## Riwayat Percobaan G1 (Install Test)

> Mode C (AI jalankan langsung) — environment Claude Code CLI, shell persisten, Docker terkonfirmasi tersedia (`docker --version` → 29.6.1).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1+A2(N/A)+A3(N/A)+A5 (satu run — A2/A3 N/A jadi tidak perlu 2 checkpoint terpisah) | C | ✅ **Pass** — `docker compose up`, image `odoo:18.0`, `-i crm_probability_from_stage --stop-after-init`. Log (`docker-env/logs/odoo_target.log`, 560 baris): modul ke-37/41, load 0.25s/116 queries, KEDUA view file (`crm_views.xml`, `res_config_settings.xml`) parse sukses, 0 baris ERROR/WARNING/CRITICAL/Traceback di SELURUH log, "41 modules loaded in 15.25s", "Registry loaded in 23.259s". `security/ir.model.access.csv` modul ini terkonfirmasi TIDAK dimuat (sesuai rencana MF-01, comment-out tetap berfungsi). | — | 2026-08-24 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `crm_probability_from_stage/__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 1
- **Aksi:**
  - `__manifest__.py`: `'version': '17.0.1.0'` → `'version': '18.0.1.0'`
- **Secara eksplisit TIDAK dilakukan:** tidak menghapus/mengubah `data`, `depends`, `license`, atau field manifest lain apapun.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List

N/A — dikonfirmasi Applicability Check (modul tidak mendefinisikan `<tree>`/`<list>` sendiri, cuma xpath ke view existing yang tetap valid — DIFF-02, DIFF-03).

## [Fase A3] Security Hardening

N/A — dikonfirmasi Applicability Check (tidak ada model/TransientModel baru yang butuh ACL; `ir.model.access.csv` existing dipertahankan rusak+comment-out apa adanya, MF-01).

## [Fase A4] Skeleton & Folder Integrity

- **Scope:** seluruh struktur folder modul
- **Aksi:** Dicek — struktur `models/`, `views/`, `security/`, `i18n/`, `static/` + `__init__.py` (root & `models/`) konsisten, tidak ada yang hilang/rusak strukturnya (terpisah dari isi `ir.model.access.csv` yang rusak secara DATA, bukan struktur file).
- **Secara eksplisit TIDAK dilakukan:** tidak membuat folder `tests/`/`data/`/`report/`/`wizard/`/`controllers/` — modul source memang tidak punya ini, port 1:1 (P1 — Full Module Fidelity, tidak menambah struktur baru).
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A5] Python API Compatibility

- **Scope:** `models/crm_lead.py`, `models/crm_stage.py`, `models/res_config_settings.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 2 (DIFF-01)
- **Aksi:**
  - `models/crm_lead.py`: `group_operator="avg"` → `aggregator="avg"` (field `probability`)
- **Secara eksplisit TIDAK dilakukan:** tidak menambah `@api.model_create_multi` (modul tidak override `create()` di manapun — tidak relevan); tidak menyentuh dead import (`timedelta`/`relativedelta` di `res_config_settings.py`, BSL-013) atau dead dependency (`partner_id` di `_compute_revenue_probability`, BSL-015) — keduanya dipertahankan sesuai larangan refactor.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase B1] Model Risiko Rendah

- **Scope:** `models/crm_lead.py`, `models/crm_stage.py`, `models/res_config_settings.py`
- **Aksi:** Dicek ulang kelengkapan `@api.depends` (BSL-004..009), keamanan relasi (`related='stage_id.probability'`), tidak ada onchange/constraint di modul ini — tidak ada perubahan diperlukan (DIFF-05, DIFF-06 sudah konfirmasi byte-identical di Step 2).
- **Secara eksplisit TIDAK dilakukan:** tidak melengkapi dead dependency `partner_id` (BSL-015) atau menambah validasi range `probability` (BSL-014) — keduanya bug/quirk source yang dipertahankan, bukan gap migrasi.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase B2] Model Kompleks

N/A — dikonfirmasi Applicability Check.

## [Fase C1] View Sederhana

- **Scope:** `views/crm_views.xml`, `views/res_config_settings.xml`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 6-7 (DIFF-02, DIFF-03, DIFF-04)
- **Aksi:** Dicek ulang xpath target (`is_won`, `expected_revenue`, `//app[@name='crm']/block[2]`) terhadap `native-target` 18.0 langsung — semua tetap valid, tidak ada perubahan kode diperlukan. DIFF-04 (reorder kosmetik setting) dicatat, tidak ditindak (bukan breaking).
- **Secara eksplisit TIDAK dilakukan:** tidak mengubah xpath `res_config_settings.xml` ke pola lain (mis. `//setting[field[@name='is_membership_multi']]`) walau itu akan menghindari reorder kosmetik DIFF-04 — di luar scope "port kode saja", xpath source dipertahankan 1:1.
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase C2] Semantik XML & Konsistensi UX

N/A — dikonfirmasi Applicability Check.

## [Fase D1] Controllers

N/A — dikonfirmasi Applicability Check.

## [Fase D2] Assets & CSS Stabilization

N/A — dikonfirmasi Applicability Check.

## [Fase E] JavaScript (Owl versi baru)

N/A — dikonfirmasi Applicability Check.

## [Fase F] Upgrade Template

N/A — dikonfirmasi Applicability Check (otomatis, E juga N/A).

---

## Temuan di Luar Spec

- [x] Tidak ada — semua perubahan (A1, A5) sudah tercakup di `03_MIGRATION_SPEC.md` §2/§4 sejak Step 3, tidak ada temuan baru yang butuh balik ke step 3/4.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat di sesi implementasi ini — temuan version-diff (DIFF-04) sudah dicatat di Step 2 (`migration-records/crm_probability_from_stage_17_18/SUMMARY.md`).
