# Diff & Compatibility Analysis — crm_probability_from_stage

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya | §1 (OCA wiki + verifikasi langsung), §1a (temuan project nyata `advanced_sales_analysis`) |
| `dependency-compat/crm/18-to-19.md` | Tidak | Belum ada entry `crm` — ditulis sebagai temuan baru project ini (lihat §3 di bawah) |

Dibaca penuh sebelum analisis ini dimulai. **Tidak ada satupun baris §1/§1a `18-to-19.md` yang applicable ke modul ini** — modul ini tidak pakai `res.groups`, `self._cr`/`_uid`/`_context`, `odoo.osv.expression`, `read_group()` override, `_sql_constraints`, manipulasi timezone manual, `auto_join`, controller `@route`, `search()` custom pada computed field, `toggle_active()`, `from odoo import SUPERUSER_ID`, `@ormcache_context`, `urljoin`, `name_search` override, `@api.returns`, tag `<group string=/expand=>` di search view, `FakeModelLoader`, atau `sale.order.line.tax_id` (§1a). Satu poin §1 yang RELEVAN secara tidak langsung: "Testing — demo data tidak lagi otomatis ter-install" — **sudah compliant**, kedua test file modul ini sudah membuat data sendiri (`setUpClass`/`setUp` bikin `crm.stage` sendiri), tidak bergantung demo data sama sekali.

## 0b. Gate Community vs Enterprise

- [x] Baca ulang `01a_MIGRATION_INTAKE.md` §2 — **TIDAK ADA** baris "Native Enterprise" (cuma `base`+`crm`, keduanya Community).
- [x] Lanjut §1 di bawah cukup pakai `native-target` (Community) — dalam hal ini `native-target`/`native-target-enterprise` sama-sama menunjuk folder gabungan `enterprise19.0`, tapi hanya sisi `odoo/addons/crm` (Community) yang benar-benar dibaca/dicek di step ini.

## 0c. Gate Transitive Dependency

- [x] Tidak ada `depends` yang dihapus dari manifest (`base`+`crm` dipertahankan apa adanya di 19.0) — gate ini **N/A**, tidak perlu enumerasi dependency transitif.

---

## 1. Perubahan Native (Core/Enterprise)

Simbol yang dipakai/di-inherit modul ini, dicek langsung terhadap `native-target` (`enterprise19.0/odoo/addons/crm`) vs `native-source` (`odoo18/addons/crm`).

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/crm_lead.py` `_compute_probabilities()` (override, no `super()`) — baris `lead_probabilities = self._pls_get_naive_bayes_probabilities()` | `crm.lead._pls_get_naive_bayes_probabilities()` | **Signature berubah — BREAKING.** 18.0: return `lead_probabilities` (dict) di SEMUA jalur. 19.0: jalur sukses utama (baris akhir method) sekarang return **tuple** `lead_probabilities, tooltip_data` — TAPI dua jalur early-return (self kosong / `leads_values_dict` kosong) TETAP return dict polos (inkonsistensi bawaan core 19.0 sendiri, bukan sesuatu yang kita perbaiki). Modul ini meng-copy body 18.0 apa adanya (`lead_probabilities = self._pls_get_naive_bayes_probabilities()` lalu `if lead.id in lead_probabilities`) — di jalur sukses 19.0, `lead_probabilities` jadi tuple 2-elemen, `lead.id in lead_probabilities` mengecek apakah `lead.id` (int) sama dengan salah satu dari dua elemen tuple (dict/tooltip_data) — **selalu `False`**. Efek: `automated_probability`/`probability` TIDAK PERNAH ter-update lewat jalur PLS manapun (silent, tidak ada exception) begitu ada lead di hasil PLS. | **Kritis — wajib fix di Step 6.** Fix: `lead_probabilities, _tooltip = self._pls_get_naive_bayes_probabilities()` (unpack tuple, buang elemen kedua — konsisten dengan cara core 19.0 sendiri memanggilnya di `crm_lead.py:2448`/`2833`). | Verifikasi langsung `enterprise19.0/odoo/addons/crm/models/crm_lead.py:175` (`return lead_probabilities, tooltip_data`) vs `odoo18/addons/crm/models/crm_lead.py` (return dict polos) |
| DIFF-02 | `models/crm_stage.py` (tidak baca `team_id` sama sekali) | `crm.stage.team_id` (Many2one) | **Dihapus**, diganti `team_ids` (Many2many, `ondelete='restrict'`) di 19.0. | **Tidak berdampak ke modul ini** — `crm_probability_from_stage/models/crm_stage.py` cuma nambah `probability`/`show_probability`, tidak pernah baca/tulis `team_id`. Dicatat untuk kelengkapan analisis, bukan tindakan wajib. | `enterprise19.0/odoo/addons/crm/models/crm_stage.py` vs `odoo18/.../crm_stage.py` |
| DIFF-03 | `models/crm_stage.py` (tidak override `write()`) | `crm.stage.write()` (baru di 19.0, tidak ada di 18.0) | **Baru ditambahkan** — kalau `is_won` sebuah stage berubah, core sekarang otomatis memanggil `won_leads.write({'probability': 100, 'automated_probability': 100})` (kalau jadi won) atau `won_leads._compute_probabilities()` (kalau bukan won lagi) untuk SEMUA lead di stage itu. | **Interaksi baru dengan DIFF-01** — jalur `won_leads._compute_probabilities()` ini memanggil METHOD YANG SAMA yang di-override modul ini (resolusi MRO standar Odoo, bukan bypass override kita). Kalau DIFF-01 belum di-fix, toggle `is_won` pada stage yang bukan-won-lagi (dengan lead existing) juga akan diam-diam gagal update probability. Setelah DIFF-01 di-fix, path baru ini otomatis ikut benar — tidak perlu penanganan terpisah. | `enterprise19.0/odoo/addons/crm/models/crm_stage.py` (method `write`, baru) vs `odoo18/.../crm_stage.py` (tidak ada `write()` override sama sekali) |
| DIFF-04 | `views/crm_views.xml` `crm_stage_form_inherit_crm_stage_probability` (inherit `crm.crm_stage_form`, xpath `field[@name='is_won']` position `before`) | View `crm.crm_stage_form` | **Struktur form berubah** (bukan cuma field): 18.0 — `is_won` ada di `<group>` pertama bareng `fold`/`team_id`. 19.0 — `is_won` dipindah ke `<group>` KEDUA (baru) bareng `rotting_threshold_days` (field baru); `<group>` pertama sekarang isi `fold`/`color`/`team_ids`. `is_won` tetap ADA sebagai `<field name="is_won"/>` sibling tunggal (bukan di dalam nested tag tambahan). | **Tidak breaking secara teknis** — xpath `//field[@name='is_won']` adalah pencarian descendant dari root arch (bukan path relatif ke parent tertentu), jadi tetap resolve ke element yang benar terlepas grup mana yang membungkusnya. Konten kita (label + div `probability` + `show_probability`) akan disisipkan tepat sebelum `is_won` di grup KEDUA (bukan grup pertama seperti di 18.0) — **perubahan visual/tata-letak**, bukan functional break. Verifikasi visual disarankan di Step 9/10 (screenshot sebelum/sesudah). | `enterprise19.0/odoo/addons/crm/views/crm_stage_views.xml:33-65` vs `odoo18/.../crm_stage_views.xml:31-56` |
| DIFF-05 | `views/crm_views.xml` `probability_crm_lead_inherit_tree_view` (inherit `crm.crm_case_tree_view_oppor`, xpath `field[@name='expected_revenue']` position `after`) | View `crm.crm_case_tree_view_oppor` | **Tidak berubah** — field `expected_revenue` tetap ada, atribut sama (`sum="Expected Revenues" optional="show" widget="monetary" options="{'currency_field': 'company_currency'}"`), posisi relatif di view sama. | Tidak ada dampak — xpath tetap resolve ke field yang sama. | `enterprise19.0/odoo/addons/crm/views/crm_lead_views.xml:786` vs `odoo18/.../crm_lead_views.xml:740` |
| DIFF-06 | `views/res_config_settings.xml` (xpath `//app[@name='crm']/block[2]` position `inside`) | View `base.res_config_settings_view_form` (app block `crm`) | **Tidak berubah struktur** — `<app name="crm">` tetap ada 5 `<block>` di urutan yang sama, `block[2]` (block tanpa title, awalnya cuma `is_membership_multi` + "Ringover VOIP") sekarang JUGA berisi setting baru `module_partnership`/`partnership_settings` di 19.0 — tapi index urutan blok itu sendiri tidak berubah. | Tidak ada dampak fungsional — setting kita akan muncul di block yang sama, sekarang bertetangga dengan 1 setting tambahan (`module_partnership`). Kosmetik saja. | `enterprise19.0/odoo/addons/crm/views/res_config_settings_views.xml:1-40` vs `odoo18/.../res_config_settings_views.xml:1-36` |
| DIFF-07 | (tidak dipakai modul ini — dicatat untuk kelengkapan §1 saja) | `res.config.settings` (`crm`) — `set_values()` | `self.env.user.groups_id` → `self.env.user.all_group_ids` (rename, konsisten dengan `groups_id`→`group_ids` §1 `18-to-19.md`) | **Tidak berdampak** — modul ini tidak override `set_values()` maupun baca `groups_id`/`all_group_ids` di manapun. | `enterprise19.0/odoo/addons/crm/models/res_config_settings.py` vs `odoo18/.../res_config_settings.py` |

| DIFF-08 | `static/tests/tours/crm_probability_pipeline_tour.js` — `import { stepUtils } from "@web_tour/tour_service/tour_utils"` | `web_tour` JS module `tour_utils.js` | **Path pindah — BREAKING.** 18.0: `web_tour/static/src/tour_service/tour_utils.js` → import path `@web_tour/tour_service/tour_utils`. 19.0: file dipindah ke `web_tour/static/src/tour_utils.js` (naik satu level, keluar dari folder `tour_service/`) → import path baru `@web_tour/tour_utils` (dikonfirmasi dari cara `crm` module 19.0 sendiri import `stepUtils` di tour-nya, mis. `crm/static/tests/tours/crm_rainbowman.js`). **Ditemukan lewat eksekusi nyata Step 9** (bukan dari static analysis) — import yang gagal resolve membuat SELURUH bundle `web.assets_tests` gagal load (`modules needed by other modules but have not been defined: ['@web_tour/tour_service/tour_utils']`), yang mengakibatkan KEDUA tour test gagal (1 ERROR di tour yang mengimpornya langsung, 1 FAIL kolateral di tour lain yang cuma satu bundle sama-sama). | **Kritis untuk Step 9 — wajib fix.** Fix: ganti import jadi `@web_tour/tour_utils`. | Verifikasi langsung `enterprise19.0/odoo/addons/web_tour/static/src/tour_utils.js` (baru) vs `odoo18/addons/web_tour/static/src/tour_service/tour_utils.js` (lama), dikonfirmasi silang dari `enterprise19.0/odoo/addons/crm/static/tests/tours/*.js` yang sudah pakai path baru |

**Catatan proses (kenapa DIFF-08 tidak muncul di analisis statis awal):** Applicability Check Step 6 (`01a_MIGRATION_INTAKE.md` §2b) menandai Fase E (JavaScript/Owl) sebagai N/A karena modul ini tidak punya KOMPONEN Owl custom — benar untuk tujuan Fase E (rewrite widget), tapi tidak mencakup kemungkinan file JS lain (tour test) yang **meng-import langsung dari path modul native** yang bisa berubah independen dari Owl. Gap analisis-statis ini baru ketahuan dari eksekusi Step 9 yang sesungguhnya (Mode C/Docker, bukan dugaan) — dicatat sebagai pelajaran proses di `migration-records/crm_probability_from_stage_18_19/SUMMARY.md`.

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| — | N/A | Tidak ada dependency OCA/third-party (lihat `01a_MIGRATION_INTAKE.md` §0/§2) | — |

## 3. Temuan Baru — Ditulis ke Migration Records

- [x] DIFF-01 (breaking, `_pls_get_naive_bayes_probabilities()` return signature) dan DIFF-03 (interaksi `crm.stage.write()` baru) dicatat sebagai kandidat `dependency-compat` untuk `crm` di `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` (dibuat sesi ini, lihat file itu).
- [x] DIFF-02, DIFF-04, DIFF-05, DIFF-06, DIFF-07 dicatat sebagai temuan minor/informational di file yang sama (kategori `version-diff`) — tidak actionable untuk modul ini, tapi berguna kalau ada modul lain yang depend `crm` di project migrasi 18→19 berikutnya.
- [x] Promosi ke `knowledge/` belum dilakukan — menunggu sesi curation terpisah (`templates/CURATION_PROMPT.md`), sesuai kebijakan tool.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 — `_pls_get_naive_bayes_probabilities()` tuple return | **Tinggi** | Silent failure (tidak ada exception) — kalau tidak di-fix, fitur inti modul (probability ikut PLS/stage sesuai toggle) berhenti bekerja tanpa gejala jelas selain angka `automated_probability` tidak pernah berubah. Wajib fix di Step 6, wajib ada regression test eksplisit di Step 9 (test yang sudah ada — `test_pls_recompute_toggle_on_follows_stage`/`test_pls_recompute_toggle_off_follows_pls` — akan menangkap ini KALAU dijalankan terhadap 19.0, karena mereka mock `_pls_get_naive_bayes_probabilities` dengan `return_value={lead.id: 99.0}` bukan tuple — **catatan penting untuk Step 6/9: mock di test existing juga perlu disesuaikan jadi tuple** `(dict, {})` supaya test tetap merepresentasikan signature 19.0 yang benar, bukan cuma "kebetulan lolos" karena mock lama). |
| DIFF-03 — `crm.stage.write()` baru | Rendah (setelah DIFF-01 fix) | Behavior baru dari core (bukan sesuatu yang kita kontrol/perlu tiru) — begitu DIFF-01 diperbaiki, path ini otomatis benar. Tidak ada tindakan tambahan. |
| DIFF-08 — `@web_tour/tour_service/tour_utils` import path pindah | **Tinggi** (ditemukan via eksekusi, bukan statis) | Membuat KEDUA tour test gagal (bundle-level failure). Wajib fix sebelum Step 9 dianggap valid — sudah di-fix & diverifikasi PASS (lihat `06c_IMPLEMENTATION_LOG.md`). |
| DIFF-04 — layout form `crm.stage` berubah | Rendah | Kosmetik — field kita tetap tampil, cuma posisi relatif berubah (grup kedua, bukan pertama). Verifikasi visual di Step 9/10 (screenshot), bukan blocker Step 6. |
| DIFF-02, DIFF-05, DIFF-06, DIFF-07 | Sangat rendah / N/A | Tidak actionable untuk modul ini — dicatat murni untuk kelengkapan dokumentasi dan reuse project migrasi lain. |
| Dependency OCA/third-party | N/A | Tidak ada. |
| Perubahan framework umum (`18-to-19.md` §1) | Tidak ada yang applicable | Modul terlalu kecil/sederhana untuk kena pola-pola yang tercatat di sana (lihat §0 di atas). |
