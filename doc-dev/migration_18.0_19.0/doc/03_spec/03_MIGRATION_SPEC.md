# Migration Spec (Teknis) — crm_probability_from_stage

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` (step 1). Lihat step 5.

---

## 1. Ringkasan Strategi

Modul ini kecil (3 model inherit, 2 view inherit, 1 config setting) dan sebagian besar port langsung — **dua titik wajib-fix**: (1) `_compute_probabilities()` di `crm_lead.py` harus di-update untuk unpack return value baru `_pls_get_naive_bayes_probabilities()` (DIFF-01, tuple bukan dict lagi); (2) import `stepUtils` di tour JS harus pindah path (DIFF-08, ditemukan lewat eksekusi Step 9 nyata, bukan analisis statis — lihat catatan proses di `02_DIFF_ANALYSIS.md`). Tidak ada Owl/controller/asset rewrite, tidak ada data migration (port kode saja, belum ada data produksi). Manifest version bump wajib (`18.0.1.0` → `19.0.1.0`). Dua test existing (`test_pls_recompute_toggle_on_follows_stage`, `test_pls_recompute_toggle_off_follows_pls`) perlu disesuaikan mock-nya supaya tetap merepresentasikan signature 19.0 yang benar (bukan business logic yang berubah — kompatibilitas test terhadap API native yang berubah, konsisten larangan "boleh ubah demi kompatibilitas, bukan demi readability/refactor"). **Status:** kedua fix sudah diterapkan dan diverifikasi PASS lewat eksekusi Docker nyata (G1 + Step 9 full suite, 13/13 test PASS) — lihat `06_implementation/06c_IMPLEMENTATION_LOG.md`.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `models/crm_lead.py` — `_compute_probabilities()` | DIFF-01, DIFF-03 | Ubah baris `lead_probabilities = self._pls_get_naive_bayes_probabilities()` jadi `lead_probabilities, _tooltip_data = self._pls_get_naive_bayes_probabilities()` (unpack tuple). Sisa body (loop `for lead in self`, `was_automated`, dst) **tidak berubah sama sekali** — behavior BSL-006 dipertahankan persis, cuma cara membaca return value-nya yang wajib disesuaikan. | Rendah (perubahan 1 baris, well-understood dari verifikasi langsung source 19.0) | BSL-006 |
| `models/crm_stage.py` | DIFF-02 (informational, tidak actionable) | **Tidak ada perubahan** — modul tidak baca `team_id`/`team_ids` sama sekali. | — | BSL-009 |
| `models/res_config_settings.py` | — (tidak ada DIFF terkait) | **Tidak ada perubahan** — `config_parameter` API tidak berubah, dead import (`timedelta`/`relativedelta`, BSL-013) dipertahankan apa adanya (larangan refactor). | — | — |
| `views/crm_views.xml` (`crm_stage_form_inherit_crm_stage_probability`) | DIFF-04 | **Tidak ada perubahan kode** — xpath `field[@name='is_won']` tetap resolve. Posisi visual berubah (field kita sekarang muncul di grup kedua form stage, bukan pertama) sebagai konsekuensi native, bukan sesuatu yang kita kontrol/perlu "perbaiki". Verifikasi visual di Step 9/10. | Rendah (kosmetik) | BSL-010 |
| `views/crm_views.xml` (`probability_crm_lead_inherit_tree_view`) | DIFF-05 | **Tidak ada perubahan** — xpath tetap resolve, atribut field sama. | — | BSL-011 |
| `views/res_config_settings.xml` | DIFF-06 | **Tidak ada perubahan** — xpath `//app[@name='crm']/block[2]` tetap resolve. | — | BSL-012 |
| `security/ir.model.access.csv` | — | **Tidak ada perubahan** — dipertahankan rusak/tidak terpakai apa adanya (BSL-016, larangan "jangan perbaiki bug lama"). | — | BSL-016 |
| `__manifest__.py` | — (Critical Blocker #1 di bawah) | `version: '18.0.1.0'` → `'19.0.1.0'`. Tidak ada perubahan `depends`/`data`/`assets` lain (struktur sudah cocok 19.0, dikonfirmasi §2b intake tidak ada Controllers/Owl/JSON field/attrs dinamis). | Rendah | — |
| `tests/test_crm_probability_from_stage.py` — `test_pls_recompute_toggle_on_follows_stage`, `test_pls_recompute_toggle_off_follows_pls` | DIFF-01 (konsekuensi test) | `patch.object(type(lead), '_pls_get_naive_bayes_probabilities', return_value={lead.id: 99.0})` → `return_value=({lead.id: 99.0}, {})` (tuple, elemen kedua dict kosong meniru `tooltip_data` default). **Ini penyesuaian kompatibilitas terhadap signature native yang berubah, BUKAN perubahan business logic/assertion** — assertion (`self.assertEqual(...)`) tidak berubah sama sekali. Tanpa ini, kedua test akan tetap PASS secara palsu (mock lama tidak merepresentasikan signature 19.0 asli) walau kode produksi (DIFF-01 fix di atas) benar — false negative risk kalau dibiarkan. | Rendah, tapi **wajib** — kalau tidak diubah, test tidak lagi jadi regression-guard valid untuk DIFF-01 | AC-02-04, AC-02-05 |
| `static/tests/tours/crm_probability_pipeline_tour.js` | DIFF-08 (ditemukan Step 9, tidak terlihat di analisis statis Step 2 awal) | `import { stepUtils } from "@web_tour/tour_service/tour_utils"` → `"@web_tour/tour_utils"` (path pindah di `web_tour` 19.0). | Rendah setelah fix, tapi **wajib** — tanpa ini seluruh bundle `web.assets_tests` gagal load, KEDUA tour test gagal | — |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x` | `__manifest__.py` | Konvensi standar Odoo, tidak spesifik ke `knowledge/version-diffs/18-to-19.md` |
| 2 | `_pls_get_naive_bayes_probabilities()` return signature (DIFF-01) — silent functional failure, BUKAN install-blocker (modul tetap install & jalan tanpa error, tapi fitur inti berhenti bekerja diam-diam) | `models/crm_lead.py` `_compute_probabilities()` | `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` CAND-01 (kandidat, belum di-curate ke `knowledge/`) |

**Priority:** HIGH — item 1 wajib sebelum instalasi apapun; item 2 wajib sebelum Step 8/9 (tidak install-blocking, tapi silent functional regression yang harus tertangkap sebelum sign-off).

### OWL Widget yang Butuh Rewrite/Review

N/A — dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b: tidak ada komponen Owl custom di modul ini (cuma 2 file tour test, lihat kategori terpisah di bawah).

**Urutan wajib (N/A untuk modul ini, dicatat untuk kelengkapan template):** migrasi SEMUA JavaScript dulu, baru upgrade template Owl — tidak relevan karena tidak ada JS/Owl produksi di modul ini.

### Controller & Route

N/A — tidak ada controller custom di modul ini (dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b).

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Key manifest `web.assets_tests` — dikonfirmasi masih valid di 19.0 (`enterprise19.0/odoo/addons/web/__manifest__.py:425`, bundle sama persis dengan 18.0) | `__manifest__.py` §`assets` | Rendah — tidak perlu perubahan, dicatat sebagai verifikasi eksplisit |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | `_pls_get_naive_bayes_probabilities()` tuple return (DIFF-01) | `models/crm_lead.py` | **HIGH** | BSL-006 |
| 2 | `crm.stage.write()` baru cascade ke `_compute_probabilities()` (DIFF-03) — otomatis benar setelah item 1 di-fix, tidak perlu penanganan terpisah | `models/crm_stage.py` (tidak ada perubahan kode wajib) | Rendah (mengikuti item 1) | BSL-006 |
| 3 | `crm.stage.team_id`→`team_ids` (DIFF-02) — tidak dipakai modul ini | — | N/A | — |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Test mock signature (lihat §2 tabel di atas) — kalau tidak disesuaikan, false-negative regression guard untuk DIFF-01 | `tests/test_crm_probability_from_stage.py` | Sedang — wajib sebelum Step 9 dianggap valid, tidak install-blocking |

### Urutan Prioritas Testing

1. Install & startup — manifest version, `depends` (`base`+`crm`, tidak berubah)
2. Core user flow — toggle Settings → CRM (`crm_manual_compute_probability`), set `probability` per stage, opportunity pindah stage (`probability` ikut related-field, BSL-007), PLS recompute (BSL-006, **fokus utama regression DIFF-01**)
3. Persistensi data — `ir.config_parameter` (BSL-001), `revenue_probability` computed+store (BSL-008)
4. Widget backend (Owl) — N/A, tidak ada
5. Tour test (Mode D, Step 9) — `crm_probability_pipeline_tour`, `crm_probability_settings_tour` (keduanya HttpCase, sudah ada, wajib re-run terhadap 19.0)

### View List (dulu Tree) Checklist

N/A — modul ini tidak mendefinisikan `<tree>`/`<list>` standalone maupun `view_mode` di action manapun (cuma xpath inherit ke view existing `crm`/`base`). Perubahan `<tree>`→`<list>` sudah selesai di migrasi 17→18 sebelumnya (dikonfirmasi `knowledge/version-diffs/18-to-19.md` §2 — peringatan eksplisit bahwa perubahan ini terjadi di 17.0, bukan 18→19).

### Estimasi Effort (opsional)

| Area | Effort | Catatan |
|---|---|---|
| `models/crm_lead.py` fix (DIFF-01) | ~15 menit | Perubahan 1 baris + verifikasi |
| Manifest version bump | ~2 menit | Trivial |
| Test mock update (2 test) | ~10 menit | Perubahan `return_value=` di 2 tempat |
| Verifikasi visual form `crm.stage` (DIFF-04) | ~10 menit | Screenshot/observasi Step 9-10, bukan kode |
| **Total Step 6** | **~30-40 menit** | Modul kecil, satu breaking change titik tunggal |

## 3. Data Migration (ringkas — detail di step 7)

N/A — port kode saja (`01a_MIGRATION_INTAKE.md` §3), belum ada data produksi. Step 7 tidak berlaku.

## 4. Scope

### Termasuk
- Fix DIFF-01 (`_compute_probabilities()` unpack tuple) — wajib untuk kompatibilitas 19.0.
- Manifest version bump.
- Penyesuaian mock 2 test existing supaya representasi signature 19.0 akurat.

### Di Luar Scope (sengaja, disetujui di intake)
- Rename/refactor `crm.stage.team_id`→`team_ids` — tidak dipakai modul ini, tidak disentuh.
- Perbaikan `security/ir.model.access.csv` yang rusak/tidak terpakai (BSL-016) — dipertahankan apa adanya, bukan bug yang boleh diperbaiki dalam migrasi port-kode.
- Perbaikan dead import (`timedelta`/`relativedelta`, BSL-013) dan dead dependency (`partner_id` di `_compute_revenue_probability`, BSL-015) — dipertahankan apa adanya, larangan refactor demi readability.
- Perbaikan validasi range `probability` yang tidak ada (BSL-014) — bug lama, dipertahankan.
