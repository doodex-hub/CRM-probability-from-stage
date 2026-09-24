# Diff & Compatibility Analysis — crm_probability_from_stage

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/19-to-20.md` | Ya (5 baris: `/web/session/logout` POST-only, `logOutItem` tidak exported, `ir.model.access.csv`→`ir.access`, `res.partner` self-write, `computeOptionalActiveFields`/`list_optional_show`, fitur pin pesan native) | dibaca penuh |
| `dependency-compat/crm/19-to-20.md` | **Tidak** — cuma ada `crm/18-to-19.md` (PLS tuple, `team_id`→`team_ids`) sebagai konteks | analisis baru di §1 |
| `dependency-compat/base/...` | Tidak ada | analisis baru (DIFF-01/02) |

**Applicability `19-to-20.md`:** tidak ada baris yang applicable. Grep modul untuk `session/logout`, `log_out`, `user_menu_items`, `computeOptionalActiveFields`, `_to_store`, `easy_edit` → 0 hit. Baris `ir.access`: modul punya `security/ir.model.access.csv` tapi **ter-comment di manifest** (BSL-016) → tidak pernah dimuat, N/A.

**Temuan terbesar project ini TIDAK ada di knowledge base:** `ir.config_parameter.get_param()`/`set_param()` **dihapus total** di 20.0 (DIFF-01) — kandidat entry baru `version-diffs/19-to-20.md`, lihat §3.

## 0b. Gate Community vs Enterprise

- [x] `01a` §2: tidak ada baris "Native Enterprise" (`base`, `crm` Community).
- [x] Analisis §1 memakai `native-source` `odoo19` vs `native-target` `odoo20` (Community). `enterprise20` dicek hanya untuk tabrakan nama field/param (`grep -rn "revenue_probability\|show_probability\|crm.manual.compute.probability"` di `odoo20/addons`, `odoo20/odoo/addons`, `enterprise20` → 0 hit).

## 0c. Gate Transitive Dependency

- [x] Tidak ada `depends` yang dihapus → N/A.

## 0d. Gate Grep Menyeluruh

Knowledge base `crm/18-to-19.md` (PLS tuple, `team_id`) sudah ter-fix di 19.0 dan dicek ulang tetap valid di 20.0 (DIFF-03). Untuk temuan baru DIFF-01, grep menyeluruh `get_param|set_param|config_parameter` ke seluruh modul (`.py`/`.xml`/`.js`, termasuk `tests/`):

| Kemunculan | File:baris | Jenis | DIFF |
|---|---|---|---|
| `get_param('crm.manual.compute.probability', False)` | `models/crm_lead.py:27` | produksi (compute `is_automated_probability`) | DIFF-01 |
| `get_param('crm.manual.compute.probability', False)` | `models/crm_stage.py:16` | produksi (compute `show_probability`) | DIFF-01 |
| `set_param(...)` helper `_set_toggle` | `tests/test_crm_probability_from_stage.py:20` | test | DIFF-01 |
| `get_param(...)` assert ×2 | `tests/test_crm_probability_from_stage.py:40,44` | test | DIFF-01 + DIFF-02 |
| `get_param(...)` assert | `tests/test_crm_probability_tour.py:26` | test | DIFF-01 + DIFF-02 |
| `config_parameter="crm.manual.compute.probability"` | `models/res_config_settings.py:11` | produksi (deklaratif) | DIFF-02 (tetap valid, cara simpan berubah) |

## 0e. Gate Silent-Regression per Tipe Override

| Override | Kategori | Hasil cek |
|---|---|---|
| `crm.lead._compute_is_automated_probability` (tanpa `super()`) | (a) Python, entry point tidak langsung (`@api.depends`, dibaca saat field dirender/diakses) | Method core 20.0 byte-identik dengan 19.0 (`odoo20/addons/crm/models/crm_lead.py:501-506`). **Body modul memanggil `get_param` → `AttributeError` saat compute jalan** (DIFF-01). Install (G1) tidak menangkapnya kalau tidak ada lead yang dibaca saat install — wajib test yang membaca `is_automated_probability`. |
| `crm.lead._compute_probabilities` (tanpa `super()`) | (a) Python, entry point `@api.depends` + `crm.stage.write()` (toggle `is_won`) + cron PLS | Core 20.0 body & decorator byte-identik 19.0 (`:508-516`); `_pls_get_naive_bayes_probabilities()` byte-identik (`diff` blok 19 `:2194-2368` vs 20 `:2174-2348` kosong) → return tetap tuple di jalur sukses, dict di early-return. Override tetap benar. `crm.stage.write()` 20.0 identik (cascade `_compute_probabilities()`). |
| `crm.stage._compute_show_probability` | (a) Python, compute non-stored (dibaca saat form stage dirender) | **`get_param` → `AttributeError` saat form stage dibuka** (DIFF-01). |
| `crm.crm_stage_form` xpath `field[@name='is_won']` before | (b) XML | Resolve (descendant search), posisi berubah — DIFF-05 |
| `crm.crm_case_tree_view_oppor` xpath `expected_revenue` after | (b) XML | Tidak berubah — DIFF-07 |
| `base.res_config_settings_view_form` xpath `//app[@name='crm']/block[2]` inside | (b) XML | Tidak berubah index — DIFF-08 |
| Tour test import `@web_tour/tour_utils` | (c)/(d) JS | Path & `stepUtils.showAppsMenuItem` masih ada — DIFF-09 |

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/crm_lead.py:27`, `models/crm_stage.py:16` (`get_param(key, False)`); tests (`set_param`/`get_param`) | `ir.config_parameter.get_param()` / `set_param()` | **DIHAPUS total — BREAKING.** 20.0 hanya punya API bertipe: `get_bool/get_int/get_float/get_str(key, default)` dan `set_bool/set_int/set_float/set_str(key, value)` (`odoo20/odoo/addons/base/models/ir_config_parameter.py:66-130`). Tidak ada alias/shim; `upgrade_code/` 20.0 tidak punya skrip otomatis untuk ini. Core sendiri memigrasikan pola identik: `crm_lead.py` 19.0 `get_param('crm.lead.auto.assignment', False)` → 20.0 `get_bool('crm.lead.auto.assignment')` (`odoo20/addons/crm/models/crm_lead.py:2043`). Bahkan 2 addon core 20.0 masih tertinggal memanggil `get_param` (`account_edi_ubl_cii/models/account_edi_common.py:2001`, `mail_plugin/controllers/authenticate.py:84`) — bukti tidak ada backward-compat. | **Kritis — modul rusak saat dipakai** (bukan saat install): membuka form/kanban/list lead yang membaca `is_automated_probability`, atau form stage (`show_probability`) → `AttributeError: 'ir.config_parameter' object has no attribute 'get_param'`. Juga setiap `_compute_probabilities` yang membaca `is_automated_probability`. **Wajib fix Step 6.** Pengganti yang mempertahankan behavior: `get_bool(key)` — lihat DIFF-02 kenapa BUKAN `get_str`. | Verifikasi langsung `odoo19/.../ir_config_parameter.py:60-103` vs `odoo20/.../ir_config_parameter.py` (analisis baru) |
| DIFF-02 | `models/res_config_settings.py:11` (`config_parameter=`); BSL-001; asersi test | `res.config.settings.set_values()` / `default_get()` untuk field `config_parameter` | **Behavior berubah.** 19.0: `set_param(icp, value)` → ON simpan `'True'`, OFF **hapus record** (`odoo19/.../res_config.py:328-349`). 20.0: `match field.type: case 'boolean': set_bool(icp, value)` (`odoo20/.../res_config.py:322-345`) → ON simpan `'True'`, OFF simpan **string `'False'` (record dipertahankan)** (`_set`: `value_ = str(value)`). Baca balik: 20.0 `default_get` pakai `get_bool` (`str2bool`). | (1) Kode produksi: kalau DIFF-01 di-fix dengan `get_str`/truthiness string, OFF (`'False'`) terbaca **truthy → modul terus menganggap toggle ON** = regresi behavior BSL-004/009. Dengan `get_bool`: `'True'`→True, `'False'`→False, tidak ada → False = identik 19.0 untuk semua nilai yang bisa dihasilkan UI. (2) Test `test_toggle_saves_config_parameter` (asersi "OFF = key dihapus/`False`") dan tour (asersi `== 'True'`) harus disesuaikan ke kontrak 20.0 tanpa mengubah maksudnya. (3) Edge case non-UI: nilai manual via System Parameters (mis. `'0'`, `'no'`, `'abc'`) — 19.0 truthy (ON), 20.0 `get_bool` → False (`'abc'` invalid → default False + warning log). Dicatat MF-03. | Analisis baru |
| DIFF-03 | `models/crm_lead.py` `_compute_probabilities()` (override tanpa `super()`) | `crm.lead._pls_get_naive_bayes_probabilities()`, `_compute_probabilities()`, `_pls_get_safe_fields()` | **Tidak berubah** — PLS byte-identik 19↔20 (return tuple jalur sukses). `_compute_probabilities` core identik. `_pls_get_safe_fields` cuma internal `get_param`→`get_str('crm.pls_fields')`. Decorator `@api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())` masih identik core. | Tidak ada tindakan. Fix 18→19 (unpack tuple) tetap benar. Mock test `return_value=({lead.id: X}, {})` tetap merepresentasikan signature 20.0. | `diff` blok `odoo19/addons/crm/models/crm_lead.py:2194-2368` vs `odoo20/...:2174-2348` = identik |
| DIFF-04 | `models/crm_lead.py` `_compute_is_automated_probability` + field `probability` redefinisi | `crm.lead.probability`, `automated_probability`, `is_automated_probability` | **Tidak berubah** — definisi field (`aggregator="avg"`, compute `_compute_probabilities`) dan compute core identik; `diff` semua baris mengandung "probability" di `crm_lead.py` 19↔20 cuma beda 1 baris SQL internal (`SQL("probability")`→`table.probability`). Atribut field `depends=`/`aggregator=`/`related=` masih didukung ORM 20.0 (`odoo20/odoo/orm/fields.py:513-516`). `tools.float_compare(a, b, 2)` signature sama (`precision_digits` posisional). | Tidak ada tindakan (selain DIFF-01 di body). | Analisis baru |
| DIFF-05 | `views/crm_views.xml` `crm_stage_form_inherit_crm_stage_probability` (`<field name="is_won" position="before">`) | View `crm.crm_stage_form` | **Struktur form berubah lagi.** 19.0: grup-1 `fold`/`color`/`team_ids`, grup-2 `is_won`/`rotting_threshold_days`. 20.0 (`odoo20/addons/crm/views/crm_stage_views.xml:32-65`): grup-1 `team_ids` → **`is_won`** → label+div `rotting_threshold_days` ("Rotting in … days"); grup-2 `fold` ("Fold by Default"). Field `crm.stage.color` dihapus dari model & view. Judul `h1` dapat class `o_outlined`. | **Tidak breaking** — xpath descendant tetap resolve ke `is_won` (masih `<field name="is_won"/>` tunggal). Konten modul (label + div probability) kini muncul di **grup pertama** antara `team_ids` dan `is_won` (di 19.0: grup kedua). Pola label+div di dalam `<group>` identik pola native `rotting_threshold_days` → render 2-kolom konsisten. Perubahan tata-letak kosmetik yang disebabkan native, bukan modul → **tidak diubah** (larangan redesign). Verifikasi visual Step 10 (MF-02). | `odoo19/.../crm_stage_views.xml` vs `odoo20/...` |
| DIFF-06 | `models/crm_stage.py` (tidak override `write`) | `crm.stage.write()`, `_onchange_is_won` | `write()` identik 19.0 (cascade `probability=100` saat jadi won / `_compute_probabilities()` saat bukan won). `_onchange_is_won` dapat early-return untuk record baru (cuma warning UI). Model dapat `_explanation`, `_get_visible_stages_domain`, `_auto_init` (reset sequence). | Tidak ada dampak — modul tidak memakai simbol baru. | `odoo19/.../crm_stage.py` vs `odoo20/...` |
| DIFF-07 | `views/crm_views.xml` `probability_crm_lead_inherit_tree_view` (`//field[@name='expected_revenue']` after) | View `crm.crm_case_tree_view_oppor` | Field `expected_revenue` identik (`sum="Expected Revenues" optional="show" widget="monetary" options="{'currency_field': 'company_currency'}"`), `company_currency` masih `column_invisible`. `<list>` dapat `js_class="crm_list"` baru. | Tidak ada dampak — xpath resolve sama; `crm_list` tidak menyentuh kolom custom. | `odoo20/addons/crm/views/crm_lead_views.xml:707-742` vs `odoo19/...:753-786` |
| DIFF-08 | `views/res_config_settings.xml` (`//app[@name='crm']/block[2]` inside) | View `crm.res_config_settings_view_form` | Masih 5 `<block>` urutan sama. Isi `block[2]` 20.0: "Multi Teams", `partnership_settings`, `website_partnership_settings` (baru); "Ringover VOIP" dihapus. `<setting>` tag tetap. | Kosmetik — setting modul tetap di block kedua, tetangga berubah. | `odoo20/addons/crm/views/res_config_settings_views.xml:11-101` vs `odoo19/...` |
| DIFF-09 | `static/tests/tours/*.js` (`import { stepUtils } from "@web_tour/tour_utils"`, `/** @odoo-module **/`, run `edit`/`click`/`drag_and_drop`) | `web_tour` | Path `odoo20/addons/web_tour/static/src/tour_utils.js` tetap, `stepUtils.showAppsMenuItem()` ada; helper `click`/`edit`/`drag_and_drop` ada (`tour_helpers_hoot.js:53,134,171`); tour core `crm` 20.0 memakai pola sama (`crm_rainbowman.js`: `o-kanban-button-new`, `button.o_kanban_add`). Anotasi `@odoo-module` masih dikenali transpiler (`odoo20/odoo/tools/js_transpiler.py`), meski core 20.0 tidak lagi menulisnya. Route `/odoo` dan `/odoo/<path>` ada (`web/controllers/home.py:49`); DOM Settings `input[placeholder='Search...']`, `.o_setting_box` ada. | Diperkirakan tidak ada dampak — **dibuktikan eksekusi G2/Step 9** (pelajaran CAND-03: masalah path JS cuma ketahuan saat dijalankan). | Analisis baru |
| DIFF-10 | Manifest `version: '19.0.1.0'` | Konvensi versi | Wajib `20.0.x` | Wajib ubah → `20.0.1.0`. | Konvensi |
| DIFF-11 | `security/ir.model.access.csv` (ter-comment di manifest) | `ir.model.access` → `ir.access` (knowledge base) | Unifikasi ACL 20.0 | N/A — file tidak dimuat (BSL-016), dipertahankan apa adanya. | `version-diffs/19-to-20.md` |
| DIFF-12 | `from odoo import _, api, fields, models, tools` | Namespace `odoo` 20.0 | `odoo` jadi namespace package (tanpa `__init__.py`, init di `odoo/init.py`) yang tetap mengekspor `_`, `api`, `fields`, `models`, `tools` (pola import identik dipakai `odoo20/addons/crm/models/crm_stage.py:3`) | Tidak ada dampak. | `odoo20/odoo/init.py` |
| DIFF-14 | `models/crm_lead.py` field `probability` (redefinisi `related='stage_id.probability'` di atas field core yang `compute='_compute_probabilities'`) | ORM `Field._setup_attrs__` | **Behavior sama, warning baru.** *(Ditambahkan Step 6, ditemukan G1 #1 — tidak terlihat dari analisis statis.)* 20.0 `odoo20/odoo/orm/fields.py:477-479`: kalau atribut hasil merge punya `related` DAN `compute`, `compute` di-pop + `UserWarning "Field crm.lead.probability is both compute and related. Set one of them to None."`. 19.0 tidak warning, tapi `setup_related` juga menimpa `self.compute = self._compute_related` (`odoo19/.../fields.py:632`) — related menang di kedua versi. | Tidak ada dampak fungsional (AC-02-01, tour 880 PASS). Warning tiap registry load. Tidak diubah (MF-04). | G1 #1 + analisis `fields.py` 19/20 |
| DIFF-13 | Test framework (`TransactionCase`, `HttpCase`, `tagged`, `start_tour`, `unittest.mock.patch.object`) | `odoo.tests` | Tetap ada (`odoo20/odoo/tests/common.py:1305,2603,2981,3137`) | Tidak ada dampak. | Analisis baru |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| — | N/A | Tidak ada dependency OCA/third-party | — |

## 3. Temuan Baru — Ditulis ke Migration Records

- [x] DIFF-01 + DIFF-02 (`get_param`/`set_param` dihapus; Boolean settings OFF kini disimpan `'False'` — pengganti `get_str`/truthiness membalik perilaku, wajib `get_bool`) → kandidat **version-diff** (general `base`, severity tinggi, berlaku modul APAPUN yang membaca `ir.config_parameter`) di `migration-tool/migration-records/crm_probability_from_stage_19.0_20.0/SUMMARY.md`.
- [x] DIFF-03/05/06/07/08 → kandidat **dependency-compat** `crm/19-to-20.md` (PLS stabil, form stage restrukturisasi, `crm.stage.color` dihapus) di SUMMARY yang sama.
- [x] Promosi ke `knowledge/` tidak dilakukan (menunggu sesi curation).

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 — `get_param`/`set_param` dihapus | **Kritis** | Crash runtime di dua compute yang dibaca UI (form stage, lead). Install mungkin tetap PASS → G1 saja tidak cukup; wajib test yang membaca `is_automated_probability`/`show_probability` (sudah ada: AC-01-02, AC-02-02/03). |
| DIFF-02 — OFF disimpan `'False'` | **Tinggi** (kalau salah pilih pengganti) | Pilihan pengganti menentukan apakah toggle OFF bekerja. `get_bool` = aman; `get_str` = regresi silent. Test harus assert nilai hasil (bukan cuma "tidak error") — pakai test toggle OFF eksplisit. |
| DIFF-02 edge — nilai manual non-kanonik | Rendah | Cuma lewat System Parameters (mode developer). MF-03. |
| DIFF-05 — layout form stage | Rendah | Kosmetik (grup pertama, bukan kedua). Verifikasi visual Step 10. |
| DIFF-09 — tour JS | Rendah–Sedang | Diperkirakan aman; bukti lewat eksekusi Step 9. |
| DIFF-03/04/06/07/08/10–13 | Sangat rendah / N/A | DIFF-10 wajib mekanis. |
