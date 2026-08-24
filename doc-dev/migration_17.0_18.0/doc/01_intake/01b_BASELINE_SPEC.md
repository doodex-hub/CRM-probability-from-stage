# Baseline Spec — crm_probability_from_stage

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 17.0.
**Tanggal:** 2026-08-24
**Sumber:** Direkonstruksi dari kode langsung (tidak ada `FUNCTIONAL_SPEC.md` lama, dikonfirmasi dev)

> Semua klaim di dokumen ini bertag `[NO-SPEC]` (ref: —) karena tidak ada dokumen lama manapun untuk cross-check.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally provenance: 0 `[MATCH]`, 0 `[GAP]`, **12 `[NO-SPEC]`** (BSL-001 s/d BSL-012).

1. `[BSL-004]`/`[BSL-005]` — **Override `_compute_is_automated_probability` mengubah behavior inti fitur PLS (Predictive Lead Scoring) bawaan Odoo `crm`**, bukan cuma menambah fitur baru di samping. Kalau toggle setting aktif, field `is_automated_probability` DIPAKSA selalu `False` — efek berantai: PLS bawaan Odoo (`_compute_probabilities`, lihat BSL-006) tidak akan pernah menimpa `probability` dengan angka otomatis-nya sendiri untuk lead manapun selama toggle ini aktif secara global. Ini bug-atau-fitur yang harus dipertahankan persis, bukan diperbaiki.
2. `[BSL-007]` — **Quirk penting:** `probability` adalah `related='stage_id.probability'` DENGAN `store=True, readonly=False` — artinya field ini technically SELALU mengikuti `stage_id.probability` di level ORM related-field (setiap kali `stage_id` berubah), TERLEPAS dari toggle setting `crm.manual.compute.probability`. Toggle itu sendiri cuma mempengaruhi field `is_automated_probability` (BSL-004) — bukan `probability` langsung. Efek praktisnya: PLS asli (`_compute_probabilities`, BSL-006) tetap bisa menimpa `probability` dengan nilai `automated_probability` kalau `was_automated` True (dan `was_automated` cuma `False` kalau toggle aktif — lihat BSL-004) — jadi interaksi dua mekanisme ini (`related` field vs override PLS) yang menentukan nilai akhir, bukan satu aturan sederhana "toggle ON = probability selalu dari stage".
3. `[BSL-011]` — `security/ir.model.access.csv` rusak/tidak terpakai (rujuk model yang tidak ada) — dipertahankan apa adanya, lihat `01a_MIGRATION_INTAKE.md` Ringkasan poin 1.
4. Semua 12 klaim `[NO-SPEC]` — tidak ada corroboration tertulis independen. Acceptance criteria (`05a`) dan test plan (`05b`) akan sepenuhnya bersandar pada ketepatan pembacaan kode di dokumen ini.

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
- `probability` (`Float`, redefinisi dari `crm` core) — jadi `related='stage_id.probability', readonly=False, store=True, depends=['stage_id.probability'], group_operator="avg", copy=False`. **`readonly=False` pada related field artinya user tetap bisa override manual nilainya** (related field biasanya read-only kecuali eksplisit di-set `readonly=False`) — behavior ini WAJIB dipertahankan.
- `revenue_probability` (`Float`, computed `_compute_revenue_probability`, `store=True`, default `0.0`) — `= (probability / 100) * expected_revenue`.

### `res.config.settings`
- `crm_manual_compute_probability` (`Boolean`, `config_parameter="crm.manual.compute.probability"`) — toggle global (bukan per-user/per-company khusus, memakai `ir.config_parameter` biasa).

## 4. Business Workflow / State Transition

### Toggle "Probability from stage" (Settings → CRM)
- `[BSL-001]` `[NO-SPEC]` (ref: —) Admin membuka Settings → CRM, mencentang/uncheck field `crm_manual_compute_probability`. Field ini tersimpan sebagai `ir.config_parameter` key `crm.manual.compute.probability` (string `"True"`/`"False"` seperti config_parameter Boolean pada umumnya) — bukan per-company, satu nilai global untuk seluruh instance.
- `[BSL-002]` `[NO-SPEC]` (ref: —) Saat toggle aktif, field `probability` di form `crm.stage` (dan label-nya, lihat §6) jadi terlihat — dikontrol oleh `show_probability` (§3) yang membaca config_parameter yang sama.

### Penetapan probability per stage
- `[BSL-003]` `[NO-SPEC]` (ref: —) Admin membuka stage CRM (Settings → CRM → Stages, atau kanban pipeline → edit stage), mengisi field `probability` (0-100, tanpa validasi range eksplisit di kode — bug/quirk, lihat §8).

## 5. Server-Side Logic dengan Side Effect

> Lanjut penomoran dari §4.

### `crm.lead`
- `[BSL-004]` `[NO-SPEC]` (ref: —) **`_compute_is_automated_probability` (override)** — method ini ADA di `crm` core Odoo (bagian dari sistem PLS), modul ini meng-override-nya total (tidak `super()`). Logika: baca `ir.config_parameter` `crm.manual.compute.probability`.
  - Kalau param **falsy** (termasuk belum pernah di-set) → `is_automated_probability = float_compare(probability, automated_probability, precision=2) == 0` (behavior default Odoo: True kalau kedua angka itu sama).
  - Kalau param **truthy** → `is_automated_probability` **selalu `False`**, apapun nilai `probability`/`automated_probability`-nya.
- `[BSL-005]` `[NO-SPEC]` (ref: —) `@api.depends('probability', 'automated_probability')` — TIDAK depends ke `ir.config_parameter` (tidak bisa, config_parameter bukan field) — artinya kalau admin mengubah toggle setting SETELAH lead sudah ada, `is_automated_probability` lead-lead existing TIDAK otomatis dihitung ulang sampai salah satu dari dua field itu (`probability`/`automated_probability`) berubah lagi (mis. lewat `_compute_probabilities`, BSL-006, atau write manual). Ini bug/quirk konsekuensi dari mekanisme `@api.depends` — dipertahankan, bukan diperbaiki.
- `[BSL-006]` `[NO-SPEC]` (ref: —) **`_compute_probabilities` (override, TIDAK ada `super()`, tapi body identik dipanggil ulang persis pola core `crm`)** — decorator `@api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())` sama persis dengan core. Logika: panggil `_pls_get_naive_bayes_probabilities()` (PLS asli, tidak diubah). Untuk tiap lead yang ada di hasil PLS:
  - `was_automated = lead.active and lead.is_automated_probability` (dibaca SEBELUM di-update di baris ini — nilai dari compute sebelumnya/BSL-004).
  - `automated_probability` di-set ke hasil PLS.
  - Kalau `was_automated` True → `probability = automated_probability` (ikuti PLS).
  - Kalau `was_automated` False → **`probability = stage_id.probability`** (bukan dibiarkan/di-skip seperti core asli yang biasanya tidak menyentuh `probability` kalau bukan automated — ini bagian INTI fitur modul: begitu `is_automated_probability` False, PLS trigger apapun akan memaksa `probability` ikut stage).
- `[BSL-007]` `[NO-SPEC]` (ref: —) `probability` field itu sendiri `related='stage_id.probability', store=True, readonly=False` (§3) — jadi di LUAR trigger PLS manapun (BSL-006), begitu `stage_id` sebuah lead berubah (pindah stage), `probability` otomatis ikut nilai `stage_id.probability` yang baru lewat mekanisme related-field standar ORM, TIDAK PERLU toggle setting aktif maupun PLS jalan. Toggle setting (BSL-001) HANYA mempengaruhi `is_automated_probability` (BSL-004), yang baru berefek ke `probability` lewat jalur BSL-006 (saat PLS re-compute jalan). Interaksi dua mekanisme independen ini (related-field vs PLS override) yang menentukan nilai akhir `probability` — lihat Ringkasan poin 2.
- `[BSL-008]` `[NO-SPEC]` (ref: —) **`_compute_revenue_probability`** — `@api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')`. Untuk tiap record: `revenue_probability = (probability / 100) * expected_revenue`. Catatan: `partner_id` ada di `@api.depends` tapi TIDAK dipakai di body method — dead dependency, quirk (lihat §8).

### `crm.stage`
- `[BSL-009]` `[NO-SPEC]` (ref: —) **`_compute_show_probability`** — non-stored, dihitung ulang tiap kali dibaca (tidak ada `@api.depends` sama sekali, karena tidak depend ke field model manapun — cuma `ir.config_parameter`). `show_probability = bool(ir.config_parameter.get_param('crm.manual.compute.probability', False))`.

## 6. Client-Side Behavior (Views)

### Backend
- `[BSL-010]` `[NO-SPEC]` (ref: —) **Form `crm.stage`** (`crm_stage_form_inherit_crm_stage_probability`, inherit `crm.crm_stage_form`) — sebelum field `is_won`, disisipkan: label "Probability" + `<div>` berisi field `probability` (widget `float`, class `oe_inline o_input_6ch`) + suffix teks " %" (`<span class="oe_grey">`). Baik label maupun div dibungkus `invisible="not show_probability"` — field `show_probability` sendiri disisipkan sebagai `invisible="1"` (dibaca client-side untuk evaluasi kondisi invisible, tidak pernah tampil).
- `[BSL-011]` `[NO-SPEC]` (ref: —) **List view Opportunities** (`probability_crm_lead_inherit_tree_view`, inherit `crm.crm_case_tree_view_oppor`) — kolom `revenue_probability` disisipkan tepat setelah kolom `expected_revenue` (xpath `//field[@name='expected_revenue']` position `after`), `optional="show"` (kolom ini defaultnya tampil tapi bisa disembunyikan user lewat opsi kolom), widget `monetary` dengan `currency_field: company_currency`, `sum="Probability Revenue"` (ikut ditotal di baris footer list).
- `[BSL-012]` `[NO-SPEC]` (ref: —) **Settings form** (`res_config_settings_view_form`, inherit `base.res_config_settings_view_form`) — field `crm_manual_compute_probability` disisipkan sebagai `<setting>` baru di dalam `<app name="crm">` block kedua (`//app[@name='crm']/block[2]`, `position="inside"`), dengan `help="Make lead probability computation manually base probability from the stage."` — muncul sebagai satu baris setting tambahan di halaman Settings → CRM milik Odoo core (bukan section terpisah).

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'crm']` — keduanya Community, native ke Odoo (lihat `01a_MIGRATION_INTAKE.md` §2).

### Implisit/Inferred
- Tidak ditemukan dependency implisit (tidak ada `self.env[...]` dinamis, tidak ada cek `'x' in self.env`, tidak ada import library eksternal selain modul standar Python `datetime`/`dateutil.relativedelta` di `res_config_settings.py` — keduanya TIDAK dipakai sama sekali di file itu, dead import, lihat §8).
- Bergantung pada API internal `crm` yang tidak dideklarasikan di manifest (implisit lewat inheritance) tapi wajib ada persis nama & signature-nya: `_pls_get_naive_bayes_probabilities()`, `_pls_get_safe_fields()`, field `automated_probability`, `is_automated_probability`, `active`, `team_id` di `crm.lead`; view `crm.crm_stage_form`, `crm.crm_case_tree_view_oppor`; app-block `res.config.settings` dengan `name="crm"`.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-013]` `[NO-SPEC]` (ref: —) `res_config_settings.py` meng-import `timedelta` (dari `datetime`) dan `relativedelta` (dari `dateutil.relativedelta`) tapi **tidak memakai keduanya sama sekali** di file itu — dead import, sisa copy-paste. Dipertahankan (larangan "refactor demi readability" di `CLAUDE.md`).
- `[BSL-014]` `[NO-SPEC]` (ref: —) Field `probability` di `crm.stage` **tidak punya validasi range** (bukan `0 <= probability <= 100`) — admin bisa mengisi angka negatif atau di atas 100, akan ikut dipakai apa adanya di `revenue_probability` (BSL-008) dan di related-field `crm.lead.probability` (BSL-007). Bug yang sudah ada di 17.0, dipertahankan.
- `[BSL-015]` `[NO-SPEC]` (ref: —) `@api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')` di `_compute_revenue_probability` menyertakan `partner_id` sebagai dependency padahal method body tidak pernah membaca `partner_id` — dead dependency (BSL-008 catatan). Efek: `revenue_probability` akan di-recompute setiap kali `partner_id` sebuah lead berubah, walau hasilnya tidak akan berubah dari perubahan itu sendiri — overhead kecil, bukan bug yang mempengaruhi correctness, dipertahankan apa adanya.
- `[BSL-016]` `[NO-SPEC]` (ref: —) `security/ir.model.access.csv` berisi satu baris yang merujuk `model_crm_stage_probability_crm_stage_probability` (model yang tidak eksis di modul ini) — file ini di-comment-out di `__manifest__.py` §`data`, jadi tidak pernah dimuat/divalidasi Odoo saat install (kalau tidak di-comment, install akan **gagal total** karena `model_id:id` tidak resolve). Dipertahankan (comment-out + isi rusak, tidak dihapus/diperbaiki) — lihat `01a_MIGRATION_INTAKE.md` Ringkasan poin 1.
