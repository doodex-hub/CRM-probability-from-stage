# Baseline Spec — crm_probability_from_stage

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 18.0.
**Tanggal:** 2026-08-26
**Sumber:** Carry-over dari `doc-dev/_archive/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (16 klaim BSL-001..BSL-016, termasuk 1 koreksi Step 9 nyata dari test yang gagal di migrasi sebelumnya) — di-cross-check ulang baris-per-baris terhadap `crm_lead.py`/`crm_stage.py`/`res_config_settings.py`/`views/crm_views.xml`/`views/res_config_settings.xml`/`security/ir.model.access.csv` di `source-codebase` (branch `migration/18.0`) sesi ini. **Hasil: identik persis, tidak ada drift** — kode 18.0 mereproduksi behavior 17.0 apa adanya, sesuai definisi migrasi ("harus identik").

> Semua klaim di dokumen ini bertag `[MATCH]` (ref: `doc-dev/_archive/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md`, BSL-NNN yang sama) — kode aktual dibaca ulang dan cocok persis dengan dokumen lama, bukan disalin buta. ID `BSL-NNN` dipertahankan sama (bukan dinomori ulang) supaya rujukan silang dari `tests/test_crm_probability_from_stage.py` (yang sudah memakai ID ini) tetap valid.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally provenance: **16 `[MATCH]`** (BSL-001 s/d BSL-016), 0 `[GAP]`, 0 `[NO-SPEC]`.

1. `[BSL-004]`/`[BSL-005]` — **Override `_compute_is_automated_probability` mengubah behavior inti fitur PLS (Predictive Lead Scoring) bawaan Odoo `crm`**, bukan cuma menambah fitur baru di samping. Kalau toggle setting aktif, field `is_automated_probability` DIPAKSA selalu `False` — efek berantai: PLS bawaan Odoo (`_compute_probabilities`, lihat BSL-006) tidak akan pernah menimpa `probability` dengan angka otomatis-nya sendiri untuk lead manapun selama toggle ini aktif secara global. Ini bug-atau-fitur yang harus dipertahankan persis, bukan diperbaiki — termasuk kalau `crm` di 19.0 mengubah signature/behavior PLS-nya (lihat `02_DIFF_ANALYSIS.md`, belum ditulis).
2. `[BSL-007]` — **Quirk penting:** `probability` adalah `related='stage_id.probability'` DENGAN `store=True, readonly=False` — artinya field ini technically SELALU mengikuti `stage_id.probability` di level ORM related-field (setiap kali `stage_id` berubah), TERLEPAS dari toggle setting `crm.manual.compute.probability`. Toggle itu sendiri cuma mempengaruhi field `is_automated_probability` (BSL-004) — bukan `probability` langsung.
3. `[BSL-016]` — `security/ir.model.access.csv` rusak/tidak terpakai (rujuk model yang tidak ada) — dipertahankan apa adanya, lihat `01a_MIGRATION_INTAKE.md` Ringkasan poin 2.
4. `[BSL-001]` sudah pernah dikoreksi nyata di migrasi 17→18 (Step 9, dari test asli yang gagal) — `set_param(key, False)` MENGHAPUS key config parameter sepenuhnya (bukan menyimpan string `'False'`), asimetri storage vs `get_param(key, False)` yang mengembalikan Python `False`. Koreksi ini sudah tertanam di baseline ini (bukan perlu ditemukan ulang), dan sudah punya test eksplisit (`test_toggle_saves_config_parameter`) yang akan langsung jadi regression check kalau perilaku `ir.config_parameter` berubah di 19.0.
5. Semua 16 klaim `[MATCH]` — tidak ada penyimpangan ditemukan. `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`/`05b_TEST_PLAN_MIGRATION.md` (step 5, belum ditulis) bisa langsung reuse AC-NN-NN yang sudah ada di test suite (`tests/test_crm_probability_from_stage.py` sudah eksplisit merujuk `AC-01-01` s/d `AC-03-02`) sebagai starting point, dikonfirmasi ulang terhadap `crm` 19.0 di step 2/5.

---

## 1. Tujuan Modul

Modul menambahkan kemampuan menetapkan **probability tetap per stage** CRM pipeline, dan memberi admin cara memilih (via Settings → CRM) apakah probability sebuah opportunity (`crm.lead`) mengikuti nilai stage tersebut, alih-alih (atau berinteraksi dengan) mekanisme *Predictive Lead Scoring* (PLS, Bayesian) bawaan Odoo `crm`. Modul juga menambahkan kolom `revenue_probability` (expected_revenue × probability%) yang tampil di list view Opportunities.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `crm.stage` (`_inherit`) | Menyimpan nilai `probability` tetap per stage + flag `show_probability` (apakah field ini ditampilkan di form stage). |
| `crm.lead` (`_inherit`) | Menyimpan `revenue_probability` (computed) dan meng-override cara `is_automated_probability` dihitung. `probability` sendiri tidak ditambah field baru, cuma diubah definisinya jadi `related='stage_id.probability'`. |
| `res.config.settings` (`_inherit`) | Menyimpan toggle `crm_manual_compute_probability` → `ir.config_parameter` key `crm.manual.compute.probability`. |

## 3. Field dengan Makna Bisnis

### `crm.stage`
- `probability` (`Float`, default `0.0`) — nilai probability (0-100) yang ditetapkan admin untuk stage ini.
- `show_probability` (`Boolean`, computed, non-store) — `True` kalau `ir.config_parameter` `crm.manual.compute.probability` bernilai truthy. Mengontrol visibility field `probability` di form stage (lihat §6).

### `crm.lead`
- `probability` (`Float`, redefinisi dari `crm` core) — jadi `related='stage_id.probability', readonly=False, store=True, depends=['stage_id.probability'], aggregator="avg", copy=False`. **`readonly=False` pada related field artinya user tetap bisa override manual nilainya** (related field biasanya read-only kecuali eksplisit di-set `readonly=False`) — behavior ini WAJIB dipertahankan.
- `revenue_probability` (`Float`, computed `_compute_revenue_probability`, `store=True`, default `0.0`) — `= (probability / 100) * expected_revenue`.

### `res.config.settings`
- `crm_manual_compute_probability` (`Boolean`, `config_parameter="crm.manual.compute.probability"`) — toggle global (bukan per-user/per-company khusus, memakai `ir.config_parameter` biasa).

## 4. Business Workflow / State Transition

### Toggle "Probability from stage" (Settings → CRM)
- `[BSL-001]` `[MATCH]` (ref: BSL-001, migrasi 17→18) Admin membuka Settings → CRM, mencentang/uncheck field `crm_manual_compute_probability`. Field ini tersimpan sebagai `ir.config_parameter` key `crm.manual.compute.probability` — bukan per-company, satu nilai global untuk seluruh instance. **Catatan storage asimetris (dikoreksi nyata di migrasi 17→18, Step 9, dari test `test_toggle_saves_config_parameter`):** ON tersimpan sebagai string `'True'`, tapi OFF berarti `set_param()` MENGHAPUS key sepenuhnya (perilaku umum `ir.config_parameter` Odoo core, bukan spesifik modul ini) — `get_param(key, False)` lalu mengembalikan default Python `False` (bool), bukan string `'False'`. Konsisten dengan cara `_compute_show_probability`/`_compute_is_automated_probability` membaca param (selalu pakai `get_param(key, False)`), jadi tidak mempengaruhi behavior modul.
- `[BSL-002]` `[MATCH]` (ref: BSL-002) Saat toggle aktif, field `probability` di form `crm.stage` (dan label-nya, lihat §6) jadi terlihat — dikontrol oleh `show_probability` (§3) yang membaca config_parameter yang sama.

### Penetapan probability per stage
- `[BSL-003]` `[MATCH]` (ref: BSL-003) Admin membuka stage CRM (Settings → CRM → Stages, atau kanban pipeline → edit stage), mengisi field `probability` (0-100, tanpa validasi range eksplisit di kode — bug/quirk, lihat §8).

## 5. Server-Side Logic dengan Side Effect

> Lanjut penomoran dari §4.

### `crm.lead`
- `[BSL-004]` `[MATCH]` (ref: BSL-004) **`_compute_is_automated_probability` (override)** — method ini ADA di `crm` core Odoo (bagian dari sistem PLS), modul ini meng-override-nya total (tidak `super()`). Logika: baca `ir.config_parameter` `crm.manual.compute.probability`.
  - Kalau param **falsy** (termasuk belum pernah di-set) → `is_automated_probability = float_compare(probability, automated_probability, precision=2) == 0` (behavior default Odoo: True kalau kedua angka itu sama).
  - Kalau param **truthy** → `is_automated_probability` **selalu `False`**, apapun nilai `probability`/`automated_probability`-nya.
- `[BSL-005]` `[MATCH]` (ref: BSL-005) `@api.depends('probability', 'automated_probability')` — TIDAK depends ke `ir.config_parameter` (tidak bisa, config_parameter bukan field) — artinya kalau admin mengubah toggle setting SETELAH lead sudah ada, `is_automated_probability` lead-lead existing TIDAK otomatis dihitung ulang sampai salah satu dari dua field itu (`probability`/`automated_probability`) berubah lagi (mis. lewat `_compute_probabilities`, BSL-006, atau write manual). Ini bug/quirk konsekuensi dari mekanisme `@api.depends` — dipertahankan, bukan diperbaiki.
- `[BSL-006]` `[MATCH]` (ref: BSL-006) **`_compute_probabilities` (override, TIDAK ada `super()`, tapi body identik dipanggil ulang persis pola core `crm`)** — decorator `@api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())` sama persis dengan core. Logika: panggil `_pls_get_naive_bayes_probabilities()` (PLS asli, tidak diubah). Untuk tiap lead yang ada di hasil PLS:
  - `was_automated = lead.active and lead.is_automated_probability` (dibaca SEBELUM di-update di baris ini — nilai dari compute sebelumnya/BSL-004).
  - `automated_probability` di-set ke hasil PLS.
  - Kalau `was_automated` True → `probability = automated_probability` (ikuti PLS).
  - Kalau `was_automated` False → **`probability = stage_id.probability`** (bukan dibiarkan/di-skip seperti core asli yang biasanya tidak menyentuh `probability` kalau bukan automated — ini bagian INTI fitur modul: begitu `is_automated_probability` False, PLS trigger apapun akan memaksa `probability` ikut stage).
- `[BSL-007]` `[MATCH]` (ref: BSL-007) `probability` field itu sendiri `related='stage_id.probability', store=True, readonly=False` (§3) — jadi di LUAR trigger PLS manapun (BSL-006), begitu `stage_id` sebuah lead berubah (pindah stage), `probability` otomatis ikut nilai `stage_id.probability` yang baru lewat mekanisme related-field standar ORM, TIDAK PERLU toggle setting aktif maupun PLS jalan. Toggle setting (BSL-001) HANYA mempengaruhi `is_automated_probability` (BSL-004), yang baru berefek ke `probability` lewat jalur BSL-006 (saat PLS re-compute jalan). Interaksi dua mekanisme independen ini (related-field vs PLS override) yang menentukan nilai akhir `probability` — lihat Ringkasan poin 2.
- `[BSL-008]` `[MATCH]` (ref: BSL-008) **`_compute_revenue_probability`** — `@api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')`. Untuk tiap record: `revenue_probability = (probability / 100) * expected_revenue`. Catatan: `partner_id` ada di `@api.depends` tapi TIDAK dipakai di body method — dead dependency, quirk (lihat §8).

### `crm.stage`
- `[BSL-009]` `[MATCH]` (ref: BSL-009) **`_compute_show_probability`** — non-stored, dihitung ulang tiap kali dibaca (tidak ada `@api.depends` sama sekali, karena tidak depend ke field model manapun — cuma `ir.config_parameter`). `show_probability = bool(ir.config_parameter.get_param('crm.manual.compute.probability', False))`.

## 6. Client-Side Behavior (Views)

### Backend
- `[BSL-010]` `[MATCH]` (ref: BSL-010) **Form `crm.stage`** (`crm_stage_form_inherit_crm_stage_probability`, inherit `crm.crm_stage_form`) — sebelum field `is_won`, disisipkan: label "Probability" + `<div>` berisi field `probability` (widget `float`, class `oe_inline o_input_6ch`) + suffix teks " %" (`<span class="oe_grey">`). Baik label maupun div dibungkus `invisible="not show_probability"` — field `show_probability` sendiri disisipkan sebagai `invisible="1"` (dibaca client-side untuk evaluasi kondisi invisible, tidak pernah tampil).
- `[BSL-011]` `[MATCH]` (ref: BSL-011) **List view Opportunities** (`probability_crm_lead_inherit_tree_view`, inherit `crm.crm_case_tree_view_oppor`) — kolom `revenue_probability` disisipkan tepat setelah kolom `expected_revenue` (xpath `//field[@name='expected_revenue']` position `after`), `optional="show"` (kolom ini defaultnya tampil tapi bisa disembunyikan user lewat opsi kolom), widget `monetary` dengan `currency_field: company_currency`, `sum="Probability Revenue"` (ikut ditotal di baris footer list).
- `[BSL-012]` `[MATCH]` (ref: BSL-012) **Settings form** (`res_config_settings_view_form`, inherit `base.res_config_settings_view_form`) — field `crm_manual_compute_probability` disisipkan sebagai `<setting>` baru di dalam `<app name="crm">` block kedua (`//app[@name='crm']/block[2]`, `position="inside"`), dengan `help="Make lead probability computation manually base probability from the stage."` — muncul sebagai satu baris setting tambahan di halaman Settings → CRM milik Odoo core (bukan section terpisah).

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'crm']` — keduanya Community, native ke Odoo (lihat `01a_MIGRATION_INTAKE.md` §2).

### Implisit/Inferred
- Tidak ditemukan dependency implisit (tidak ada `self.env[...]` dinamis, tidak ada cek `'x' in self.env`, tidak ada import library eksternal selain modul standar Python `datetime`/`dateutil.relativedelta` di `res_config_settings.py` — keduanya TIDAK dipakai sama sekali di file itu, dead import, lihat §8).
- Bergantung pada API internal `crm` yang tidak dideklarasikan di manifest (implisit lewat inheritance) tapi wajib ada persis nama & signature-nya: `_pls_get_naive_bayes_probabilities()`, `_pls_get_safe_fields()`, field `automated_probability`, `is_automated_probability`, `active`, `team_id` di `crm.lead`; view `crm.crm_stage_form`, `crm.crm_case_tree_view_oppor`; app-block `res.config.settings` dengan `name="crm"`. **Ini adalah area utama yang perlu di-diff terhadap `crm` 19.0 di step 2** — kalau nama/signature salah satu berubah, migrasi ini pecah.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-013]` `[MATCH]` (ref: BSL-013) `res_config_settings.py` meng-import `timedelta` (dari `datetime`) dan `relativedelta` (dari `dateutil.relativedelta`) tapi **tidak memakai keduanya sama sekali** di file itu — dead import, sisa copy-paste. Dipertahankan (larangan "refactor demi readability" di `CLAUDE.md`).
- `[BSL-014]` `[MATCH]` (ref: BSL-014) Field `probability` di `crm.stage` **tidak punya validasi range** (bukan `0 <= probability <= 100`) — admin bisa mengisi angka negatif atau di atas 100, akan ikut dipakai apa adanya di `revenue_probability` (BSL-008) dan di related-field `crm.lead.probability` (BSL-007). Bug yang sudah ada sejak 17.0, dipertahankan.
- `[BSL-015]` `[MATCH]` (ref: BSL-015) `@api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')` di `_compute_revenue_probability` menyertakan `partner_id` sebagai dependency padahal method body tidak pernah membaca `partner_id` — dead dependency (BSL-008 catatan). Efek: `revenue_probability` akan di-recompute setiap kali `partner_id` sebuah lead berubah, walau hasilnya tidak akan berubah dari perubahan itu sendiri — overhead kecil, bukan bug yang mempengaruhi correctness, dipertahankan apa adanya.
- `[BSL-016]` `[MATCH]` (ref: BSL-016) `security/ir.model.access.csv` berisi satu baris yang merujuk `model_crm_stage_probability_crm_stage_probability` (model yang tidak eksis di modul ini) — file ini di-comment-out di `__manifest__.py` §`data`, jadi tidak pernah dimuat/divalidasi Odoo saat install (kalau tidak di-comment, install akan **gagal total** karena `model_id:id` tidak resolve). Dipertahankan (comment-out + isi rusak, tidak dihapus/diperbaiki) — lihat `01a_MIGRATION_INTAKE.md` Ringkasan poin 2.

## 9. Test Coverage Existing (carry-over, baru di baseline ini)

Modul sudah membawa test suite dari migrasi 17→18 (bukan ditulis baru di project ini) — dibaca sesi ini untuk konfirmasi baseline, relevan langsung untuk step 5/9:

- `tests/test_crm_probability_from_stage.py` — 10 `TransactionCase` test, masing-masing merujuk eksplisit `AC-NN-NN`/`BSL-NNN` di komentar (mis. `test_toggle_saves_config_parameter` → AC-01-01/BSL-001, `test_pls_recompute_toggle_on_follows_stage` → AC-02-04). Cakupan: toggle config parameter, `show_probability`, validasi range (tidak ada), `probability` mengikuti `stage_id`, `is_automated_probability` kedua arah toggle, `_compute_probabilities` kedua arah `was_automated`, `revenue_probability` termasuk dead-dependency `partner_id`.
- `tests/test_crm_probability_tour.py` — 2 `HttpCase` test dengan `start_tour()`: `crm_probability_pipeline_tour` (pipeline kanban, revenue_probability) dan `crm_probability_settings_tour` (toggle Settings, assert server-side `ir.config_parameter` tersimpan `'True'`).
- Tag `@tagged('post_install', '-at_install')` dipakai konsisten di semua test class.

Test suite ini **bukan bagian scope migrasi kode produk** (business logic-nya), tapi wajib tetap PASS pasca migrasi (dasar Step 9 Dev Testing) — kalau ada test yang gagal karena API `crm`/Odoo core berubah di 19.0 (bukan karena bug modul ini), itu sinyal breaking change yang harus ditangani di `03_MIGRATION_SPEC.md`, bukan tanda modul ini salah.
