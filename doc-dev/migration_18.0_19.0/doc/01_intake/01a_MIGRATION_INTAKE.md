# Migration Intake — crm_probability_from_stage

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** Draft — menunggu review user

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist (dikonfirmasi dev, sesi ini, 2026-08-26):**

- [x] `native-target` (Community, checkout 19.0) — ada di disk dev. Path: `D:\Kuncoro\doodex\repo\enterprise19.0` (folder GABUNGAN — struktur repo Odoo penuh, `odoo/addons/` berisi modul Community DAN Enterprise sekaligus, bukan addons-only. Lihat catatan struktur di bawah.)
- [x] `native-source` (Community, checkout 18.0) — ada di disk dev. Path: `D:\Kuncoro\doodex\repo\odoo18` (reuse dari project 17→18 sebelumnya, connect-sekali-selamanya)
- [x] `native-target-enterprise` — **dikonfirmasi via manifest: tidak ada dependency Enterprise** (`depends: ['base', 'crm']`, sama seperti migrasi 17→18 sebelumnya yang mengonfirmasi hal sama). Path tersedia untuk jaga-jaga (folder gabungan sama dengan `native-target` di atas — `D:\Kuncoro\doodex\repo\enterprise19.0`), tapi step 2 tidak wajib menganalisis sisi Enterprise-nya kecuali ditemukan dependency baru.
- [x] `native-source-enterprise` — path diketahui (`D:\Kuncoro\doodex\repo\enterprise18`, reuse dari project sebelumnya), sama seperti di atas tidak wajib dipakai aktif kecuali ditemukan dependency Enterprise baru.
- [x] `third-party-source`/`third-party-target` — **dikonfirmasi via manifest + carry-over dari migrasi 17→18: tidak ada dependency OCA/vendor pihak ketiga.** Tidak perlu di-connect.

> **Catatan struktur `native-target` (lesson `advanced_sales_analysis` 18.0→19.0, diterapkan di sini):** `enterprise19.0` di-`ls` dan dikonfirmasi BUKAN addons-only — berisi `odoo/`, `setup.py`, `MANIFEST.in`, dan `odoo/addons/` berisi baik `crm` (Community) maupun `crm_enterprise` (Enterprise) di level yang sama. Folder ini juga **bukan git repo** (`git rev-parse` gagal — hasil extract, bukan clone), jadi tidak ada `git log`/`git diff` yang bisa dijalankan di situ; perannya tetap read-only baca file saja.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — branch `migration/18.0` di-checkout, clone terpisah di `D:\Kuncoro\doodex\repo\crm-probability-from-stage-migration-19-source`. Dikonfirmasi dev (disebutkan eksplisit di instruksi awal sesi).
- [x] Folder `target-codebase` — branch baru `migration/19.0_target` (dibuat dari `origin/migration/18.0` via Mode Git, `git checkout -b migration/19.0_target origin/migration/18.0`), di folder ini (`D:\Kuncoro\doodex\repo\crm-probability-from-stage-migration-19`). Dikonfirmasi dev.
- [x] Dikonfirmasi: dua clone fisik terpisah (bukan symlink/alias satu folder yang sama) — dua proses `git clone`/`checkout -b` independen di sesi ini.
- [x] Versi Odoo semantik: **18.0 → 19.0**, dikonfirmasi eksplisit oleh dev di instruksi awal sesi (bukan cuma disimpulkan dari nama branch/manifest).

> Catatan konteks (bukan bagian gate, sekadar riwayat): folder `target-codebase` ini semula (sebelum bootstrap Mode Git sesi ini) checked-out di branch `master`, isi berbeda — struktur flat (bukan nested `crm_probability_from_stage/`), fresh clone dari GitHub tanpa riwayat migrasi. Working tree bersih (tidak ada perubahan belum-commit selain `.claude`/`.gitignore` untracked) saat di-switch, jadi `master` tetap aman/utuh di histori git, cuma tidak checked-out lagi di folder ini.

### 0b. Gate: Placeholder Path Absolut `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` → `D:/Kuncoro/doodex/repo/crm-probability-from-stage-migration-19-source`
- [x] `ABS_PATH_MIGRATION_TOOL` → `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET` → `D:/Kuncoro/doodex/repo/enterprise19.0`
- [x] `ABS_PATH_NATIVE_SOURCE` → `D:/Kuncoro/doodex/repo/odoo18`
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE` → `D:/Kuncoro/doodex/repo/enterprise19.0` (SAMA dengan `ABS_PATH_NATIVE_TARGET` — folder gabungan, lihat catatan §0 di atas)
- [x] `ABS_PATH_NATIVE_SOURCE_ENTERPRISE` → `D:/Kuncoro/doodex/repo/enterprise18`
- [x] `ABS_PATH_THIRD_PARTY_SOURCE` / `ABS_PATH_THIRD_PARTY_TARGET` — tidak dipakai, baris deny dihapus seluruhnya (dikonfirmasi tidak ada dependency OCA/vendor).

Gate §0b terpenuhi — tidak ada `{{ABS_PATH_...}}` literal tersisa (sudah dilakukan di commit bootstrap `8101d0f`).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Baseline behavior modul ini SUDAH pernah didokumentasikan penuh** di migrasi 17→18 sebelumnya (`doc-dev/_archive/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md`, 16 klaim `BSL-001`..`BSL-016`, plus koreksi Step 9 nyata dari test yang gagal). Kode `crm_lead.py`/`crm_stage.py`/`res_config_settings.py`/kedua view/`ir.model.access.csv` di `source-codebase` (branch `migration/18.0`) sudah di-cross-check baris-per-baris sesi ini terhadap dokumen lama itu — **identik persis**, tidak ada drift. `01b_BASELINE_SPEC.md` project ini ditulis sebagai carry-over `[MATCH]` dari dokumen lama (bukan `[NO-SPEC]` dari nol) — konfirmasi ini yang dimaksud, bukan sesuatu yang perlu dibaca ulang dari awal?
2. **`security/ir.model.access.csv` tetap rusak/tidak terpakai** (BSL-016) — merujuk model `model_crm_stage_probability_crm_stage_probability` yang tidak eksis, tapi di-comment-out di `__manifest__.py` §`data` sehingga tidak pernah dimuat. Dipertahankan apa adanya di 19.0 (larangan "jangan perbaiki bug lama").
3. **Tidak ada `FUNCTIONAL_SPEC.md` atau dokumen pelengkap lain** di `source-codebase` — sama seperti migrasi 17→18. Belum ditanyakan ulang eksplisit ke dev di sesi ini (carry-over dari konfirmasi migrasi sebelumnya) — kalau ternyata ADA dokumen baru yang muncul sejak itu, tolong beri tahu sebelum Step 2 mulai.
4. Modul ini **tidak punya** Controllers, Assets/CSS/JS runtime custom, komponen Owl custom, field JSON/dynamic model, atau `attrs=`/`states=`/domain dinamis apapun (lihat §2b) — modul kecil (3 model inherit, 2 view inherit, 1 config setting). Satu-satunya JS di modul ini adalah 2 file tour test (`static/tests/tours/`, dimuat via `web.assets_tests`) — dipakai Step 9 (Mode D, Tour headless) bukan Fase E/F (Owl UI component) di Step 6.
5. Tidak ada satupun poin ambigu lain yang genuinely butuh keputusan — intake ini selebihnya straightforward, hasil carry-over migrasi 17→18 yang polanya sudah tervalidasi.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `crm_probability_from_stage` (satu modul, tidak ada modul lain yang saling depend)
- Deskripsi singkat fungsi modul: memungkinkan admin menetapkan nilai probability tetap per stage CRM (`crm.stage.probability`), dan lewat toggle Settings → CRM (`crm.manual.compute.probability`) memilih apakah `crm.lead.probability` mengikuti probability stage tersebut (bukan probability otomatis/PLS Naive Bayes bawaan Odoo).
- Apakah modul-modul ini saling depend satu sama lain: N/A — satu modul saja.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (19.0, ada di `native-target`) | Selalu tersedia. |
| `crm` | Native Community | Ya (19.0, ada di `native-target`, `odoo/addons/crm`) | Modul ini `_inherit` 3 model dari sini: `crm.lead`, `crm.stage`, `res.config.settings` (yang di-extend `crm` module juga). |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak terlihat di manifest:

- Tidak ditemukan pemanggilan `in self.env` atau `try/except ImportError` yang mengindikasikan dependency opsional apapun di ketiga file model (dikonfirmasi ulang sesi ini, sama seperti temuan migrasi 17→18).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | — | N/A |
| Assets/CSS/JS custom | ☑ Sebagian — cuma test tour | `static/tests/tours/crm_probability_pipeline_tour.js` + `crm_probability_settings_tour.js`, dimuat via key `assets`/`web.assets_tests` di manifest. Bukan asset runtime UI produk (tidak ada `static/src/`). | D2 (assets manifest key) relevan minor, E/F (Owl component produksi) N/A |
| Komponen Owl/JavaScript custom | ☐ Tidak | Kedua file `.js` di atas adalah tour script (`registry.category("web_tour.tours")`), bukan komponen Owl/widget custom | N/A untuk fase E/F Owl; tour test sendiri relevan ke Step 9 Mode D |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Semua field: `Float`/`Boolean`, related sederhana 1 level (`related='stage_id.probability'`) | N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ Tidak | `views/crm_views.xml` sudah pakai `invisible="not show_probability"` langsung (sintaks modern, bukan `attrs=`); tidak ada `states=`; `views/res_config_settings.xml` tidak ada domain/context dinamis | N/A |

**Semua kolom "Ada di modul?" = Tidak, kecuali satu baris "Sebagian" (test tour only, bukan UI produksi)** — step 6 (Code Migration) menyatakan fase B2/C2/D1/E/F N/A di Applicability Check untuk kode PRODUK; fase D2 (manifest assets key) tetap dicek ringan karena ada key `assets` di manifest, dan tour test (bukan fase A-G, tapi Step 9 Mode D) tetap wajib dijalankan ulang pasca migrasi.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Tidak ada** (carry-over konfirmasi migrasi 17→18 — tidak ditemukan file baru dengan nama itu di `source-codebase` sesi ini).
  - **TIDAK ADA** — `01b_BASELINE_SPEC.md` diisi dari carry-over `01b_BASELINE_SPEC.md` migrasi 17→18 (`doc-dev/_archive/migration_17.0_18.0/`), yang sudah di-cross-check ulang terhadap kode `source-codebase` 18.0 sesi ini dan dikonfirmasi **identik** (semua klaim jadi provenance `[MATCH]`, bukan `[NO-SPEC]` lagi).
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain

- [ ] **Belum ditanyakan ulang eksplisit ke dev di sesi ini** — carry-over dari konfirmasi "tidak ada dokumen pelengkap lain" di migrasi 17→18. Kalau ada dokumen baru (manual guide, PRD, spec) yang muncul sejak migrasi 17→18 selesai, beri tahu sebelum Step 2 mulai (lihat Ringkasan poin 3).

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan (dikonfirmasi dev sesi ini).

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business logic di §1 (baca `01b_BASELINE_SPEC.md`) — termasuk `security/ir.model.access.csv` yang rusak/tidak terpakai (lihat Ringkasan poin 2) dan struktur nested `crm_probability_from_stage/` (bukan flat) yang sudah dipakai di `source-codebase` 18.0.
- Yang sengaja diubah/di-drop selama migrasi: tidak ada — hanya perubahan yang wajib untuk kompatibilitas 19.0 (lihat `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md`, belum ditulis).

## 6. Constraint

- Deadline: tidak disebutkan — tidak diminta eksplisit.
- Owner tiap step: dev (Kuncoro), AI sebagai migration copilot.
