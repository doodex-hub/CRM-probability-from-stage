# Diff & Compatibility Analysis — crm_probability_from_stage

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | `migration-tool/knowledge/version-diffs/17-to-18.md` |
| `dependency-compat/<nama>/...` | Tidak relevan | Tidak ada dependency OCA/vendor (dikonfirmasi dev, `01a` §0) |

§1d dari `17-to-18.md` sudah punya entry KHUSUS modul ini (dari project resmi sebelumnya, 2026-07-30): `crm.lead` PLS methods (`_compute_probabilities`, `_compute_is_automated_probability`, `_pls_get_naive_bayes_probabilities`, `_pls_get_safe_fields`) byte-identical 17.0↔18.0. Diverifikasi ulang independen di §1 di bawah (bukan cuma dipercaya dari knowledge base — dicek langsung `native-source` vs `native-target` di sesi ini).

## 0b. Gate Community vs Enterprise

- [x] Baca ulang `01a_MIGRATION_INTAKE.md` §2 — **tidak ada baris "Native Enterprise"**, cuma `base`+`crm` (keduanya Community).
- [x] Lanjut §1 cukup `native-target` (Community) + `native-source` (Community). Tidak perlu `native-target-enterprise`.

## 0c. Gate Transitive Dependency

- [x] Tidak ada dependency yang akan dihapus dari `depends` (`base`+`crm` tetap keduanya) — gate ini N/A, tidak ada yang perlu dicek.

---

## 1. Perubahan Native (Core/Enterprise)

> Semua baris dicek LANGSUNG di `native-source` (`D:\Kuncoro\doodex\repo\odoo17`) vs `native-target` (`D:\Kuncoro\doodex\repo\odoo18`) di sesi ini — bukan cuma dipercaya dari knowledge base/GitHub API.

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/crm_lead.py` — `probability = fields.Float(..., group_operator="avg", ...)` (BSL-007) | `odoo/fields.py` `Field._get_attrs` | Behavior berubah (non-breaking) — `group_operator` di-map otomatis ke `aggregator` oleh ORM, memicu `DeprecationWarning` saja | Rendah. Diverifikasi langsung: `odoo18/odoo/fields.py:482-484` — `if 'group_operator' in attrs: warnings.warn(...); attrs['aggregator'] = attrs.pop('group_operator')`. TIDAK install-blocking, TIDAK ada di 17.0 (param lama masih native ada di kedua versi). **Rekomendasi:** rename ke `aggregator="avg"` di kode migrasi (bersih dari warning), bukan wajib untuk install berhasil. | Analisis baru (dikonfirmasi native-target langsung) + `knowledge/version-diffs/17-to-18.md` §1 |
| DIFF-02 | `views/crm_views.xml` — `crm_stage_form_inherit_crm_stage_probability` (`inherit_id="crm.crm_stage_form"`, xpath `field[@name='is_won']`) (BSL-010) | `addons/crm/views/crm_stage_views.xml` record `crm_stage_form` | **Tidak berubah** — byte-identical 17.0↔18.0 (`diff` langsung: nol perbedaan pada record ini). Field `is_won` tetap ada di posisi & struktur yang sama. | Tidak ada — xpath tetap valid, tidak perlu diubah. | Analisis baru (diff langsung native-source vs native-target) |
| DIFF-03 | `views/crm_views.xml` — `probability_crm_lead_inherit_tree_view` (`inherit_id="crm.crm_case_tree_view_oppor"`, xpath `field[@name='expected_revenue']`) (BSL-011) | `addons/crm/views/crm_lead_views.xml` record `crm_case_tree_view_oppor` | Tag root `<tree>`→`<list>` (kosmetik, XML-ID/view-record-id **tetap** `crm_case_tree_view_oppor` — cuma internal `name` field-nya berubah `crm.lead.tree.opportunity`→`crm.lead.list.opportunity`). Field `expected_revenue` dan `company_currency` yang jadi target xpath modul ini **byte-identical**, tidak berubah sama sekali. Field lain di view ini berubah (mis. `activity_calendar_event_id` dihapus, dua button dapat tambahan `groups=`) — tidak relevan ke xpath modul ini. | Tidak ada — xpath modul ini (`//field[@name='expected_revenue']`, position `after`) tetap match sempurna. `<tree>`→`<list>` adalah **Critical Migration Blocker** general (`knowledge/` §1) TAPI hanya relevan untuk modul yang MENDEFINISIKAN `<tree>` sendiri — modul ini tidak pernah menulis `<tree>`/`<list>` literal, cuma xpath ke view yang sudah ada, jadi tidak terpengaruh. | Analisis baru (diff langsung native-source vs native-target) |
| DIFF-04 | `views/res_config_settings.xml` — `res_config_settings_view_form` (`inherit_id="base.res_config_settings_view_form"`, xpath `//app[@name='crm']/block[2]`, `position="inside"`) (BSL-012) | `addons/crm/views/res_config_settings_views.xml` record `res_config_settings_view_form` | **Nyaris tidak berubah** — satu-satunya diff: 18.0 menambahkan `<setting id="ringover-voip">` baru DI DALAM block ke-2 yang sama (setelah setting `is_membership_multi`), sebelum diff ini block ke-2 cuma berisi `is_membership_multi`. `block[2]` tetap resolve ke block yang sama (urutan block tidak berubah), `position="inside"` tetap valid. | Kosmetik saja: setting `crm_manual_compute_probability` modul ini (disisipkan paling akhir di block 2 lewat `position="inside"`) akan tampil SETELAH setting "Ringover VOIP Phone" yang baru di 18.0, bukan lagi tepat setelah `is_membership_multi` seperti di 17.0. Tidak ada perubahan fungsional/struktural yang wajib di-fix — xpath tetap valid. | Analisis baru (`diff` langsung file lengkap, native-source vs native-target) |
| DIFF-05 | `models/crm_lead.py` — `_compute_is_automated_probability` (override total, tanpa `super()`) (BSL-004/005) | `addons/crm/models/crm_lead.py` — field `automated_probability`/`is_automated_probability`, method `_compute_is_automated_probability` asli, decorator `@api.depends('probability', 'automated_probability')` | **Tidak berubah** — signature, nama field, dan decorator identik 17.0↔18.0 (dikonfirmasi `grep`/pembacaan langsung kedua versi). Override modul ini tetap valid tanpa penyesuaian. | Tidak ada. | Analisis baru + `knowledge/` §1d (entry byte-identical untuk PLS methods lain di model yang sama) |
| DIFF-06 | `models/crm_lead.py` — `_compute_probabilities` (override, decorator `@api.depends(lambda self: [...] + self._pls_get_safe_fields())`), `_pls_get_naive_bayes_probabilities`, `_pls_get_safe_fields` (BSL-006) | `addons/crm/models/crm_lead.py` | **Byte-identical 17.0↔18.0** — sudah dikonfirmasi project sebelumnya (`knowledge/version-diffs/17-to-18.md` §1d), tidak diverifikasi ulang byte-per-byte di sesi ini (redundant, confidence sudah tinggi dari sumber yang sama persis: project migrasi modul ini sendiri). | Tidak ada. | `knowledge/` §1d |

**Cek general `knowledge/version-diffs/17-to-18.md` §1/§1b/§1c yang TIDAK relevan ke modul ini** (dicek satu-satu, dicatat supaya jelas ini sengaja di-skip bukan terlewat):

| Item general | Kenapa N/A untuk modul ini |
|---|---|
| `<tree>`→`<list>` (definisi langsung) | Modul tidak pernah mendefinisikan `<tree>`/`<list>` sendiri (lihat DIFF-03) |
| `user_has_groups` dihapus | Tidak dipakai di manapun (grep 3 file model: nol match) |
| `check_access_rights`/`check_access_rule`/`_filter_access_rules*` | Tidak di-override |
| `_name_search`, `_check_recursion` | Tidak dipakai |
| `copy`/`copy_data` override | Tidak di-override |
| Search di related field non-stored → exception | `probability` adalah related field TAPI `store=True` — aturan ini cuma untuk non-stored |
| `<div class="oe_chatter">`→`<chatter/>` | Tidak ada markup chatter di modul ini |
| Kanban arch changes | Tidak ada kanban view custom |
| JS `/** @odoo-module **/`, `odoo.define`, Owl `Component.extend`, dst (§1b/§1c) | Modul tidak punya file JS/Owl sama sekali (dikonfirmasi `01a` §2b) |
| Manifest `assets` key | Tidak ada asset registration apapun (tidak ada `static/src/`) |
| `@api.model_create_multi` untuk `create()` | Modul tidak override `create()` di manapun |
| `@api.depends` kelengkapan | Sudah dicek per-method (§4/5 baseline spec) — tidak ada gap kurang-lengkap, hanya kelebihan (`partner_id` di BSL-015, sudah didokumentasikan, tidak berdampak error) |
| `ir.config_parameter.get_param()` sebaiknya `.sudo()` | **Sudah** dipakai `.sudo()` di kedua tempat (`crm_lead.py`, `crm_stage.py`) sejak 17.0 — tidak perlu perubahan |
| `fields.function()` API lama | Tidak dipakai |
| Test setup/impersonation pattern | Modul tidak punya test sama sekali |
| Owl `useService("rpc")` (§1c) | N/A, tidak ada Owl |
| Enterprise dependency dihapus (§1c) | N/A, tidak depend Enterprise sama sekali |
| CSP/SCSS ketat (§2, lower confidence) | Tidak ada inline script/CDN/SCSS custom |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

N/A — dikonfirmasi dev tidak ada dependency OCA/vendor pihak ketiga (`01a_MIGRATION_INTAKE.md` §0).

## 3. Temuan Baru — Migration Records

Ditulis ke `migration-tool/migration-records/crm_probability_from_stage_17_18/SUMMARY.md` (folder sudah ada dari project sebelumnya — entry baru ditambahkan, bukan menimpa):

- **[version-diff]** DIFF-04 (`res_config_settings.xml` xpath `block[2]`/`position="inside"`) — kasus konkret pertama yang benar-benar memverifikasi bagaimana penambahan `<setting>` baru oleh core Odoo di 18.0 mempengaruhi urutan tampil setting custom yang di-insert via `position="inside"` di block yang sama. Kesimpulan: tidak breaking, cuma reorder visual. Berguna untuk modul migrasi lain yang menambah setting lewat pola ini.
- **[dependency-compat]** Tidak ada (tidak ada dependency OCA/Enterprise di modul ini).

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 (`group_operator`→`aggregator`) | Rendah | Non-breaking, tapi akan diperbaiki di Step 6 untuk kebersihan kode (hilangkan `DeprecationWarning`) |
| DIFF-02, DIFF-03, DIFF-05, DIFF-06 | Tidak ada risiko | Byte-identical/xpath tetap valid, tidak ada perubahan kode diperlukan |
| DIFF-04 (`res_config_settings.xml` reorder) | Sangat rendah | Kosmetik saja (posisi tampil setting baru), tidak ada tindakan wajib |
| **Kesimpulan keseluruhan** | **Rendah** | Modul ini sudah di source 17.0 dengan pola kode modern (bukan pola v16 lama) — diff ke 18.0 minimal, hanya 1 perubahan kode yang direkomendasikan (DIFF-01), tidak ada yang install-blocking |
