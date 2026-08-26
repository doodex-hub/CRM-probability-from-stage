# Code Review — crm_probability_from_stage

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0
**Files reviewed:** `__manifest__.py`, `models/crm_lead.py`, `models/crm_stage.py`, `models/res_config_settings.py`, `views/crm_views.xml`, `views/res_config_settings.xml`, `security/ir.model.access.csv`, `tests/test_crm_probability_from_stage.py`, `tests/test_crm_probability_tour.py`, `static/tests/tours/*.js`
**Tanggal:** 2026-08-26

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| — | — | — | — | — | Tidak ada issue ditemukan | — |

**Catatan per kategori (semua diperiksa, nihil temuan):**
- **Konvensi Odoo:** `sudo()` dipakai HANYA untuk `ir.config_parameter` (`get_param`/`set_param`) — pola standar Odoo untuk baca setting global lintas-user, bukan privilege escalation berlebihan. `@api.depends` di kedua compute (`_compute_revenue_probability`, `_compute_show_probability`, `_compute_is_automated_probability`) sesuai field yang dibaca. `store=True` pada `probability`/`revenue_probability`/`automated_probability` konsisten dengan pola core (field ini dipakai untuk sort/group/filter di list view). Tidak ada field sensitif yang butuh proteksi group tambahan.
- **Business Logic:** Semua business rule dari `01b_BASELINE_SPEC.md` (BSL-001..016) ter-implementasi identik dengan source 18.0 — dikonfirmasi cross-check kode langsung di Step 1, dan dikonfirmasi ulang lewat 13/13 test PASS di Step 6/9 (termasuk 2 test yang secara eksplisit menguji dua cabang `was_automated` True/False, BSL-006). Tidak ada edge case baru yang relevan (recordset kosong tidak applicable — kedua compute method beroperasi per-record dalam loop `for lead/stage in self`).
- **Security:** Tidak ada input user yang divalidasi (modul tidak punya form input custom di luar field `probability`/toggle boolean, keduanya field Odoo standar dengan validasi tipe bawaan ORM). Tidak ada secret/password yang di-log. Tidak ada akses data lintas-user (semua operasi baca `ir.config_parameter` yang memang global, bukan per-user).
- **Performance:** Tidak ada N+1 — kedua compute method (`_compute_revenue_probability`, `_compute_is_automated_probability`, `_compute_show_probability`) iterasi `for rec in self` murni membaca field yang sudah di-`@api.depends`, tidak ada `search()`/query tambahan di dalam loop. `_compute_probabilities` (override) memanggil `_pls_get_naive_bayes_probabilities()` SEKALI di luar loop (pola sama persis dengan core, tidak diubah).
- **Code Quality:** Semua method di bawah 15 baris. Tidak ada magic number selain `100`/`0` (persentase/default probability, self-explanatory di konteks). Dead import (`timedelta`/`relativedelta` di `res_config_settings.py`, BSL-013) dan dead dependency (`partner_id` di `@api.depends` `_compute_revenue_probability`, BSL-015) **dipertahankan dengan sengaja** (bukan diabaikan/tidak ketahuan) — sudah didokumentasikan eksplisit sebagai quirk yang harus dipertahankan (larangan refactor demi readability), BUKAN kualitas kode yang perlu diperbaiki di migrasi ini.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 — `_pls_get_naive_bayes_probabilities()` tuple unpack | `models/crm_lead.py` `_compute_probabilities()` | ✅ Covered | Diverifikasi PASS lewat AC-02-04/AC-02-05 (test suite Step 9) |
| DIFF-03 — `crm.stage.write()` cascade | Tidak ada perubahan kode (mengikuti DIFF-01) | ✅ Covered | Konsisten — path baru core otomatis benar setelah DIFF-01 fix |
| DIFF-04 — layout form `crm.stage` berubah | Tidak ada perubahan kode (kosmetik) | ✅ Covered | Field kita tetap tampil, posisi grup berubah sebagai konsekuensi native |
| DIFF-08 — `stepUtils` import path pindah | `static/tests/tours/crm_probability_pipeline_tour.js` | ✅ Covered | Ditemukan & di-fix di Step 6 (eksekusi nyata), diverifikasi PASS lewat kedua Tour test |
| Fase A1 — manifest version | `__manifest__.py` | ✅ Covered | `19.0.1.0` |
| DIFF-02, 05, 06, 07 | Tidak ada perubahan (dikonfirmasi tidak actionable) | ✅ Covered | — |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 | Toggle tersimpan sebagai ir.config_parameter | ✅ PASS | `test_toggle_saves_config_parameter` |
| AC-01-02/02b | `show_probability` sesuai toggle | ✅ PASS | `test_show_probability_computed` |
| AC-01-03 | Probability stage tanpa validasi range | ✅ PASS | `test_stage_probability_no_range_validation` |
| AC-01-04 | Posisi setting di Settings → CRM | ✅ PASS (kosmetik, verifikasi visual Step 10) | Terlihat lewat Tour `test_crm_probability_settings_tour` (klik & save toggle sukses) |
| AC-02-01 | `probability` ikut `stage_id.probability` | ✅ PASS | `test_probability_follows_stage_change`, juga diverifikasi Tour pipeline (drag antar stage) |
| AC-02-02 | `is_automated_probability` True (toggle off, angka sama) | ✅ PASS | `test_is_automated_probability_toggle_off` |
| AC-02-03 | `is_automated_probability` selalu False (toggle on) | ✅ PASS | `test_is_automated_probability_toggle_on` |
| AC-02-04 | PLS recompute: probability ikut stage (toggle on) | ✅ PASS | `test_pls_recompute_toggle_on_follows_stage` — **regression guard DIFF-01, dikonfirmasi valid** |
| AC-02-05 | PLS recompute: probability ikut PLS (toggle off, was_automated) | ✅ PASS | `test_pls_recompute_toggle_off_follows_pls` — **regression guard DIFF-01, dikonfirmasi valid** |
| AC-02-06 | Toggle berubah tidak auto-recompute existing | ✅ PASS | `test_toggle_change_no_auto_recompute` |
| AC-03-01 | `revenue_probability` = expected_revenue × probability% | ✅ PASS | `test_revenue_probability_calculation`, juga diverifikasi Tour pipeline (1000×88%=880) |
| AC-03-02 | `revenue_probability` recompute no-op saat `partner_id` berubah | ✅ PASS | `test_revenue_probability_recompute_on_partner_change` |
| AC-03-03 | Kolom "Probability Revenue" di list view Opportunities | ✅ PASS | Diverifikasi Tour pipeline (baca nilai 880 dari kolom itu) |
| AC-04-01 | Install sukses walau dead import ada | ✅ PASS | G1 install bersih |
| AC-04-02 | Install sukses walau `ir.model.access.csv` rusak (comment-out) | ✅ PASS | G1 install bersih |

**Ringkasan:** 16/16 AC ter-cover, 0 gap. 13 AC diverifikasi lewat automated test (unit/integration/tour) real execution, sisanya (AC-01-04 posisi visual, dan overlap dengan Tour) diverifikasi tambahan di Step 10.

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`source-codebase`) sudah eksplisit tercatat & disetujui di `03_MIGRATION_SPEC.md` §4 (Scope). Kedua fix kode (DIFF-01, DIFF-08) murni kompatibilitas terhadap API native yang berubah — tidak ada satu baris pun business logic modul ini yang berubah nilainya (dikonfirmasi test suite 13/13 PASS dengan assertion IDENTIK dengan versi 18.0).

**Cek tabrakan nama method dengan Odoo core (kedua arah):**
1. **Arah 1** (override tanpa `super()` menimpa method core): `_compute_is_automated_probability` dan `_compute_probabilities` KEDUANYA override tanpa `super()` — tapi ini SUDAH terdokumentasi sengaja sejak baseline (BSL-004, BSL-006), bukan temuan baru. Tidak ada method LAIN di modul ini yang menimpa method core.
2. **Arah 2** (native 19.0 menambah field/method baru dengan nama sama seperti yang didefinisikan modul ini): dicek langsung via grep `native-target` (`enterprise19.0/odoo/addons/crm/`) — `revenue_probability` **tidak ada** di `crm.lead` 19.0 native. `probability`/`show_probability` **tidak ada** sebagai field baru di `crm.stage` 19.0 native (cuma disebut di docstring prosa, bukan field def). `crm_manual_compute_probability` **tidak ada** di manapun di `crm` 19.0 native. **Tidak ada tabrakan di kedua arah.**

- [x] Sudah dicek (kedua arah) — tidak ada tabrakan nama method/field dengan core/Enterprise

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — DIFF-08 (ditemukan setelah `03_MIGRATION_SPEC.md` draf awal ditulis) SUDAH ditambahkan retroaktif ke `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` sebelum Step 6 dinyatakan selesai (lihat `06c_IMPLEMENTATION_LOG.md` "Temuan di Luar Spec").

## F. Kontribusi ke Knowledge Base

- [x] Ada — sudah dicatat di Step 2/6 (`migration-records/crm_probability_from_stage_18_19/SUMMARY.md`, CAND-01, CAND-02, CAND-03). Tidak ada temuan baru dari review ini sendiri.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 0 🟡 · 0 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9 (sudah dieksekusi nyata di Step 6, lihat `06c_IMPLEMENTATION_LOG.md` — 13/13 test PASS; `09_DEV_TESTING.md` menyusul untuk formalisasi dokumen gate Step 9).

**Issue 🔴 yang wajib difix sebelum lanjut:** Tidak ada.
