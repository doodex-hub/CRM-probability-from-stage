# Baseline Spec — crm_probability_from_stage

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 19.0.
**Tanggal:** 2026-09-24
**Sumber:** Direkonsiliasi dari `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (16 klaim BSL-001..BSL-016, semua `[MATCH]`) + cross-check baris-per-baris ke kode branch `migration/19.0` (`git show migration/19.0:crm_probability_from_stage/...`) dan ke native `odoo19` untuk mekanisme core yang dirujuk klaim (mis. `ir.config_parameter.set_param`). Test executable lama (13 test) ada di `crm_probability_from_stage/tests/` — PASS 13/13 di 19.0 (2026-08-26).

> Semua klaim bertag `[MATCH]` (ref: BSL-NNN yang sama di baseline 18→19). ID dipertahankan sama supaya rujukan dari `tests/test_crm_probability_from_stage.py` (`AC-NN-NN`/`BSL-NNN`) tetap valid. Satu-satunya drift kode 18.0→19.0 (unpack tuple di `_compute_probabilities`, fix DIFF-01 lama) sudah tercermin di BSL-006 — itu perubahan kompatibilitas, bukan perubahan behavior.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally provenance: **16 `[MATCH]`**, 0 `[GAP]`, 0 `[NO-SPEC]`.

1. `[BSL-004]`/`[BSL-006]` — Inti fitur: toggle ON memaksa `is_automated_probability = False`, sehingga setiap re-compute PLS menulis `probability = stage_id.probability` (bukan angka PLS). `automated_probability` tetap diisi hasil PLS. Wajib identik di 20.0.
2. `[BSL-001]`/`[BSL-004]`/`[BSL-009]` — Modul membaca toggle dengan **truthiness string** (`get_param(key, False)`): nilai tersimpan apapun yang tidak kosong = ON. Di 19.0 lewat UI Settings nilai hanya pernah `'True'` (ON) atau key dihapus (OFF). **Mekanisme baca ini yang paling terdampak 20.0** (API `get_param` dihapus) — lihat `02_DIFF_ANALYSIS.md` DIFF-01/MF-03.
3. `[BSL-007]` — `probability` = related `stage_id.probability` (`store=True, readonly=False`): pindah stage → probability ikut stage, **terlepas dari toggle**.
4. `[BSL-005]`, `[BSL-013]`..`[BSL-016]` — quirk yang dipertahankan: toggle tidak me-recompute lead existing; dead import; tanpa validasi range; dead dependency `partner_id`; CSV security rusak & ter-comment.
5. Tidak ada klaim ambigu baru — kode 19.0 = baseline 18→19 + fix kompatibilitas.

---

## 1. Tujuan Modul

Menetapkan **probability tetap per stage** CRM, dan (via Settings → CRM) memilih apakah probability opportunity mengikuti nilai stage itu alih-alih PLS bawaan Odoo `crm`. Menambah kolom `revenue_probability` (expected_revenue × probability%) di list view Opportunities.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `crm.stage` (`_inherit`) | Menyimpan `probability` tetap per stage + flag computed `show_probability`. |
| `crm.lead` (`_inherit`) | Redefinisi `probability` jadi related ke stage; field `revenue_probability`; override `_compute_is_automated_probability` & `_compute_probabilities`. |
| `res.config.settings` (`_inherit`) | Toggle `crm_manual_compute_probability` → `ir.config_parameter` `crm.manual.compute.probability`. |

## 3. Field dengan Makna Bisnis

### `crm.stage`
- `probability` (`Float`, default `0.0`).
- `show_probability` (`Boolean`, computed, non-store) — truthy kalau param toggle truthy.

### `crm.lead`
- `probability` (`Float`, redefinisi) — `related='stage_id.probability', readonly=False, store=True, depends=['stage_id.probability'], aggregator="avg", copy=False`.
- `revenue_probability` (`Float`, compute `_compute_revenue_probability`, `store=True`, default `0.0`).

### `res.config.settings`
- `crm_manual_compute_probability` (`Boolean`, `config_parameter="crm.manual.compute.probability"`) — global.

## 4. Business Workflow / State Transition

### Toggle "Probability from stage"
- `[BSL-001]` `[MATCH]` (ref: BSL-001 18→19) Admin centang/uncheck di Settings → CRM → tersimpan ke `ir.config_parameter` `crm.manual.compute.probability` (global). **Storage 19.0 (dicek ulang ke `odoo19/odoo/addons/base/models/res_config.py` `set_values` + `ir_config_parameter.py` `set_param`):** ON → string `'True'`; OFF → `set_param(key, False)` **menghapus record** param; `get_param(key, False)` lalu mengembalikan Python `False`.
- `[BSL-002]` `[MATCH]` (ref: BSL-002) Toggle aktif → field `probability` + label di form `crm.stage` terlihat (via `show_probability`).

### Penetapan probability per stage
- `[BSL-003]` `[MATCH]` (ref: BSL-003) Admin mengisi `probability` di form stage — tanpa validasi range (lihat BSL-014).

## 5. Server-Side Logic dengan Side Effect

### `crm.lead`
- `[BSL-004]` `[MATCH]` (ref: BSL-004) `_compute_is_automated_probability` (override total, tanpa `super()`), dibaca per lead: `is_manually = ir.config_parameter.sudo().get_param('crm.manual.compute.probability', False)`.
  - falsy → `is_automated_probability = float_compare(probability, automated_probability, 2) == 0` (default Odoo).
  - truthy → `is_automated_probability = False` selalu.
- `[BSL-005]` `[MATCH]` (ref: BSL-005) `@api.depends('probability', 'automated_probability')` — tidak depend ke param; mengubah toggle tidak me-recompute lead existing sampai salah satu field itu berubah. Dipertahankan.
- `[BSL-006]` `[MATCH]` (ref: BSL-006) `_compute_probabilities` (override tanpa `super()`, decorator identik core `['stage_id', 'team_id'] + _pls_get_safe_fields()`). Body 19.0: `lead_probabilities, _tooltip_data = self._pls_get_naive_bayes_probabilities()` (unpack tuple — fix kompatibilitas 18→19). Untuk tiap lead di hasil PLS: `was_automated = lead.active and lead.is_automated_probability`; `automated_probability = hasil PLS`; `was_automated` True → `probability = automated_probability`; False → **`probability = stage_id.probability`**.
- `[BSL-007]` `[MATCH]` (ref: BSL-007) `probability` related `stage_id.probability` (store, readonly=False) — pindah stage → ikut stage lewat ORM related, tanpa toggle/PLS.
- `[BSL-008]` `[MATCH]` (ref: BSL-008) `_compute_revenue_probability` — `@api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')`; `revenue_probability = (probability / 100) * expected_revenue`.

### `crm.stage`
- `[BSL-009]` `[MATCH]` (ref: BSL-009) `_compute_show_probability` — non-stored, tanpa `@api.depends`; `show_probability = get_param('crm.manual.compute.probability', False)` (string di-cast ke Boolean oleh ORM).

## 6. Client-Side Behavior (Views)

- `[BSL-010]` `[MATCH]` (ref: BSL-010) Form `crm.stage` (`crm_stage_form_inherit_crm_stage_probability`, inherit `crm.crm_stage_form`, `<field name="is_won" position="before">`): label "Probability" + `<div class="d-inline-block">` berisi `probability` (widget `float`, class `oe_inline o_input_6ch`) + `<span class="oe_grey"> %</span>`, keduanya `invisible="not show_probability"`; `show_probability` `invisible="1"`. Di 19.0, `is_won` ada di `<group>` kedua bareng `rotting_threshold_days` → konten modul muncul di grup kedua (hasil DIFF-04 18→19).
- `[BSL-011]` `[MATCH]` (ref: BSL-011) List Opportunities (`probability_crm_lead_inherit_tree_view`, inherit `crm.crm_case_tree_view_oppor`, `//field[@name='expected_revenue']` `after`): `revenue_probability`, `optional="show"`, widget `monetary` `currency_field: company_currency`, `sum="Probability Revenue"`.
- `[BSL-012]` `[MATCH]` (ref: BSL-012) Settings (`res_config_settings_view_form`, inherit `base.res_config_settings_view_form`, `//app[@name='crm']/block[2]` `inside`): `<setting help="Make lead probability computation manually base probability from the stage.">` berisi `crm_manual_compute_probability`.

## 7. Dependency Eksternal

- Manifest: `depends: ['base', 'crm']` (Community).
- Implisit: API `crm.lead` `_pls_get_naive_bayes_probabilities()` (return tuple di jalur sukses), `_pls_get_safe_fields()`, field `automated_probability`/`is_automated_probability`/`active`/`team_id`/`expected_revenue`/`company_currency`; view `crm.crm_stage_form`, `crm.crm_case_tree_view_oppor`, app-block `crm`; **API `ir.config_parameter.get_param()`** (BSL-004/009) dan (di test) `set_param()`; `odoo.tools.float_compare`; tour: `@web_tour/tour_utils` `stepUtils`.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-013]` `[MATCH]` (ref: BSL-013) `res_config_settings.py` import `timedelta`/`relativedelta` tidak dipakai — dead import, dipertahankan.
- `[BSL-014]` `[MATCH]` (ref: BSL-014) `crm.stage.probability` tanpa validasi range (−50, 150 diterima).
- `[BSL-015]` `[MATCH]` (ref: BSL-015) `partner_id` di `@api.depends` `_compute_revenue_probability` tidak dipakai body — dead dependency.
- `[BSL-016]` `[MATCH]` (ref: BSL-016) `security/ir.model.access.csv` merujuk model tidak eksis, di-comment-out di manifest `data` — tidak pernah dimuat. Dipertahankan.

## 9. Test Coverage Existing

- `tests/test_crm_probability_from_stage.py` — 11 `TransactionCase` (AC-01-01..AC-03-02), memakai `ir.config_parameter.set_param()`/`get_param()` langsung (helper `_set_toggle`, `test_toggle_saves_config_parameter`) dan mock `_pls_get_naive_bayes_probabilities` return tuple.
- `tests/test_crm_probability_tour.py` — 2 `HttpCase`: `crm_probability_pipeline_tour`, `crm_probability_settings_tour` (assert server-side `get_param(...) == 'True'`).
- Semua `@tagged('post_install', '-at_install')`. PASS 13/13 di 19.0.
