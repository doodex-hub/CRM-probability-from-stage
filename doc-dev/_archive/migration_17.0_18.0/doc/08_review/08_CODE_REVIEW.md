# Code Review — crm_probability_from_stage

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 18.0
**Files reviewed:** `__manifest__.py`, `models/crm_lead.py`, `models/crm_stage.py`, `models/res_config_settings.py`, `views/crm_views.xml`, `views/res_config_settings.xml`, `security/ir.model.access.csv`, `README.md`
**Tanggal:** 2026-08-24

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🔵 Info | Konvensi Odoo | `models/res_config_settings.py` | 1-2 | Import `timedelta`/`relativedelta` tidak dipakai (dead import) | **Tidak difix** — bug/quirk pre-existing dari source 17.0 (BSL-013), larangan refactor `CLAUDE.md` §Forbidden Actions. Dicatat, bukan issue baru. |
| CR-02 | 🔵 Info | Business Logic | `models/crm_stage.py` | 11 | Field `probability` tidak punya validasi range 0-100 | **Tidak difix** — pre-existing (BSL-014), sudah diputuskan `03_MIGRATION_SPEC.md` §4 "Di Luar Scope". |
| CR-03 | 🔵 Info | Code Quality | `models/crm_lead.py` | 15 | `@api.depends` `_compute_revenue_probability` menyertakan `partner_id` yang tidak dipakai di body (dead dependency) | **Tidak difix** — pre-existing (BSL-015), di luar scope. |
| CR-04 | 🔵 Info | Konvensi Odoo | `security/ir.model.access.csv` | 2 | Baris ACL merujuk model tidak eksis, tapi file di-comment-out di manifest | **Tidak difix** — pre-existing (BSL-016/MF-01), dipertahankan sengaja sebagai regression guard (AC-04-02). Konfirmasi comment tetap ada di `__manifest__.py` baris 21 — ✅ dicek, masih comment. |

**Tidak ada temuan 🔴 Critical atau 🟡 Warning baru** — dua-duanya kategori kosong. Semua 4 item di atas adalah quirk/bug yang SUDAH ada di source 17.0 (bukan regresi migrasi), sudah dikonfirmasi dev sebagai "dipertahankan" di Step 1 (`FINDINGS.md` MF-01/02/03) dan `03_MIGRATION_SPEC.md` §4 — dicatat di sini sebagai referensi silang, bukan temuan baru yang butuh keputusan.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| A1 — manifest version `18.0.1.0` | `__manifest__.py:16` = `'18.0.1.0'` | ✅ Sesuai | — |
| A5/DIFF-01 — `group_operator`→`aggregator` | `models/crm_lead.py:10` = `aggregator="avg"` | ✅ Sesuai | Terverifikasi juga lewat G1 (tidak ada DeprecationWarning tercetak di log — walau log level INFO tidak selalu menampilkan Python warnings, kode sumbernya sudah benar per baca langsung) |
| README compat string | `README.md` baris "Odoo version: 18.0" | ✅ Sesuai | Ditemukan & diperbaiki di Step 4 |
| C1 — `views/crm_views.xml`, `views/res_config_settings.xml` port 1:1 | Byte-identical dengan `source-codebase` (dicek `diff`) | ✅ Sesuai | DIFF-02/03/04 — tidak ada perubahan diperlukan, dan tidak ada perubahan tidak sengaja |
| `models/crm_stage.py`, `models/res_config_settings.py` port 1:1 | Byte-identical dengan `source-codebase` | ✅ Sesuai | Dicek `diff` langsung |
| `security/ir.model.access.csv`, `i18n/*.po` port 1:1 | Byte-identical | ✅ Sesuai | Dicek `diff` langsung |

**Tidak ada gap** — semua item spec terimplementasi tepat, tidak lebih tidak kurang.

## C. Gap Analysis — Implementasi vs Acceptance Criteria

> Verifikasi di sini adalah verifikasi KODE (apakah kode secara struktural memenuhi AC) — verifikasi RUNTIME penuh (eksekusi nyata tiap skenario) ada di Step 9/10.

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 | Toggle → ir.config_parameter | ✅ Kode sesuai | `config_parameter="crm.manual.compute.probability"` di field definition |
| AC-01-02/02b | `show_probability` computed dari config_parameter | ✅ Kode sesuai | `_compute_show_probability`, dibaca `invisible="not show_probability"` di view |
| AC-01-03 | Tidak ada validasi range | ✅ Kode sesuai (sengaja tidak divalidasi) | Konsisten CR-02 |
| AC-01-04 | Setting muncul di block 2 Settings→CRM | ✅ Kode sesuai (posisi tampil kosmetik beda dari 17.0, DIFF-04) | Verifikasi visual di Step 10 |
| AC-02-01 | `probability` related-field ikut `stage_id` | ✅ Kode sesuai | `related='stage_id.probability', store=True` |
| AC-02-02/03 | `is_automated_probability` sesuai toggle | ✅ Kode sesuai | Logika `_compute_is_automated_probability` byte-identical source |
| AC-02-04/05 | PLS re-compute ikut toggle | ✅ Kode sesuai | `_compute_probabilities` byte-identical source (DIFF-06) |
| AC-02-06 | Toggle tidak auto-recompute existing | ✅ Kode sesuai (konsekuensi `@api.depends` yang tidak menyertakan config_parameter) | Konsisten BSL-005/MF-03 |
| AC-03-01/02 | `revenue_probability` calculation | ✅ Kode sesuai | Formula & dependency byte-identical source |
| AC-03-03 | Kolom di list view | ✅ Kode sesuai | xpath byte-identical, DIFF-03 |
| AC-04-01/02 | Install sukses walau dead code/ACL rusak | ✅ **Dikonfirmasi runtime** | G1 install test PASS (bukan cuma analisis statis — lihat `06c_IMPLEMENTATION_LOG.md`) |

**Tidak ada gap** — 16 AC semua ✅ pada level kode; AC-04 bahkan sudah terverifikasi runtime lewat G1.

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — dua perubahan kode (DIFF-01 rename param, README compat string) keduanya eksplisit tercatat & disetujui di `03_MIGRATION_SPEC.md` §4. Tidak ada refactor/fitur baru/bug fix apapun di luar itu (dikonfirmasi `diff` byte-level terhadap `source-codebase` untuk semua file selain `__manifest__.py`, `models/crm_lead.py`, `README.md`).

**Cek tabrakan nama method dengan Odoo core (DUA ARAH):**

1. **Arah 1** — Modul men-define ulang 2 method dengan nama PERSIS sama seperti core `crm` TANPA `super()`: `_compute_is_automated_probability`, `_compute_probabilities`. Ini BUKAN kolisi tak sengaja — ini justru INTI fitur modul (override sengaja untuk mengubah logika PLS), sudah didokumentasikan penuh di `01b_BASELINE_SPEC.md` BSL-004/006 dan `02_DIFF_ANALYSIS.md` DIFF-05/06. Dicek: kedua method core ini byte-identical 17.0↔18.0 (dicek langsung `native-source`/`native-target`), jadi override ini tidak diam-diam kehilangan behavior BARU yang ditambahkan core di 18.0 yang belum ada di 17.0 — aman.
2. **Arah 2** — Grep field/method yang DIDEFINISIKAN modul ini (`probability`+`show_probability` di `crm.stage`; `revenue_probability`+`_compute_revenue_probability` di `crm.lead`; `crm_manual_compute_probability` di `res.config.settings`; `_compute_show_probability`) terhadap `native-target` (`addons/crm/`, `odoo/` core) — **NOL match** untuk nama-nama custom ini di core 18.0. `crm.stage` core 18.0 dikonfirmasi TIDAK punya field `probability` sama sekali (native, murni ditambahkan modul ini). Tidak ada tabrakan.

- [x] Sudah dicek (kedua arah) — tidak ada tabrakan nama method/field dengan core, baik yang disengaja (Arah 1, sudah dianalisis aman) maupun tak disengaja (Arah 2, nol match).

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — dikonfirmasi `diff` byte-level source vs target untuk semua file KECUALI `__manifest__.py` (1 baris version), `models/crm_lead.py` (1 baris `aggregator`), `README.md` (1 baris compat string) — ketiganya eksplisit di `03_MIGRATION_SPEC.md` §4.

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat di step ini — semua temuan (DIFF-04, CAND-06 gitignore) sudah dicatat di Step 2/6.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 4 🔵 (semua pre-existing quirk, sudah diputuskan dipertahankan)
- [x] ✅ Lulus — tidak ada 🔴, lanjut ke step 9

**Issue 🔴 yang wajib difix sebelum lanjut:** tidak ada.
