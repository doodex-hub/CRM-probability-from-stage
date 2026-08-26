# Migration Intake — crm_probability_from_stage

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** Draft — menunggu review user

---

## 0. Folder Referensi — WAJIB Ditanyakan ke Dev SEKARANG

**Checklist (dikonfirmasi dev, sesi ini, 2026-08-24):**

- [x] `native-target` (Community, checkout 18.0) — ada di disk dev. Path: `D:\Kuncoro\doodex\repo\odoo18`
- [x] `native-source` (Community, checkout 17.0) — ada di disk dev. Path: `D:\Kuncoro\doodex\repo\odoo17`
- [x] `native-target-enterprise` — **dikonfirmasi dev: tidak ada dependency Enterprise.** Manifest cuma `depends: ['base', 'crm']`, keduanya Community. Tidak perlu di-connect.
- [x] `third-party-source`/`third-party-target` — **dikonfirmasi dev: tidak ada dependency OCA/vendor pihak ketiga.** Tidak perlu di-connect.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — branch `staging/17.0` di-checkout, clone terpisah di `D:\Kuncoro\doodex\repo\CRM-probability-from-stage-migration-18-source`. Dikonfirmasi dev.
- [x] Folder `target-codebase` — branch baru `migration/18.0_target` (dibuat dari `origin/staging/17.0` via Mode Git, `git checkout -b migration/18.0_target origin/staging/17.0`), di folder ini (`D:\Kuncoro\doodex\repo\CRM-probability-from-stage-migration-18`). Dikonfirmasi dev.
- [x] Dikonfirmasi dev: dua clone fisik terpisah (bukan symlink/alias satu folder yang sama).
- [x] Versi Odoo semantik: **17.0 → 18.0**, dikonfirmasi eksplisit oleh dev (bukan cuma disimpulkan dari nama branch/manifest).

> Catatan konteks (bukan bagian gate, sekadar riwayat): folder `target-codebase` ini semula (sebelum bootstrap Mode Git sesi ini) checked-out di branch `master`, isi berbeda total — struktur flat (bukan nested `crm_probability_from_stage/`), manifest `16.0.1`. Working tree bersih (tidak ada perubahan belum-commit) saat di-switch, jadi `master` tetap aman/utuh di histori git, cuma tidak checked-out lagi di folder ini.

### 0b. Gate: Placeholder Path Absolut `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` → `D:/Kuncoro/doodex/repo/CRM-probability-from-stage-migration-18-source`
- [x] `ABS_PATH_MIGRATION_TOOL` → `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET` → `D:/Kuncoro/doodex/repo/odoo18`
- [x] `ABS_PATH_NATIVE_SOURCE` → `D:/Kuncoro/doodex/repo/odoo17`
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE` / `ABS_PATH_NATIVE_SOURCE_ENTERPRISE` — tidak dipakai, baris deny dihapus seluruhnya (dikonfirmasi tidak ada dependency Enterprise).
- [x] `ABS_PATH_THIRD_PARTY_SOURCE` / `ABS_PATH_THIRD_PARTY_TARGET` — tidak dipakai, baris deny dihapus seluruhnya (dikonfirmasi tidak ada dependency OCA/vendor).

Gate §0b terpenuhi — tidak ada `{{ABS_PATH_...}}` literal tersisa.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Modul ini punya `security/ir.model.access.csv` yang genuinely rusak/tidak terpakai** — baris di dalamnya merujuk model `model_crm_stage_probability_crm_stage_probability` yang **tidak ada** di modul ini sama sekali (bukan nama model manapun yang didefinisikan `crm_lead.py`/`crm_stage.py`/`res_config_settings.py`). File ini **sudah di-comment-out** di `__manifest__.py` §`data` (`# 'security/ir.model.access.csv'`) — jadi efeknya nol saat install, kemungkinan sisa copy-paste dari modul lain yang tidak pernah dibersihkan. Karena sifat migrasi ini "port kode saja" dan larangan mutlak *"jangan perbaiki bug yang sudah ada"* — file ini akan **dipertahankan apa adanya** (comment-out + isi rusak) di 18.0, bukan dihapus/diperbaiki. Konfirmasi ini yang dimaksud, bukan sesuatu yang perlu diperbaiki sekarang?
2. **Tidak ada `FUNCTIONAL_SPEC.md` atau dokumen pelengkap lain** (dikonfirmasi dev di sesi ini) — `01b_BASELINE_SPEC.md` 100% direkonstruksi dari baca kode langsung, semua klaim bertag `[NO-SPEC]`. Ini bukan kekurangan proses, tapi berarti tidak ada corroboration tertulis independen — acceptance criteria nanti murni bersandar pada pembacaan kode yang akurat.
3. Modul ini **tidak punya** Controllers, Assets/CSS/JS custom, komponen Owl, field JSON/dynamic model, atau `attrs=`/`states=`/domain dinamis apapun di source 17.0 (lihat §2b) — cukup kecil & bersih, konsisten dengan sifatnya sebagai modul kecil (3 model inherit, 2 view inherit, 1 config setting).
4. Tidak ada satupun poin ambigu lain yang genuinely butuh keputusan — intake ini selebihnya straightforward.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `crm_probability_from_stage` (satu modul, tidak ada modul lain yang saling depend)
- Deskripsi singkat fungsi modul: memungkinkan admin menetapkan nilai probability tetap per stage CRM (`crm.stage.probability`), dan lewat toggle Settings → CRM (`crm.manual.compute.probability`) memilih apakah `crm.lead.probability` mengikuti probability stage tersebut (bukan probability otomatis/PLS Naive Bayes bawaan Odoo).
- Apakah modul-modul ini saling depend satu sama lain: N/A — satu modul saja.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (18.0, ada di `native-target`) | Selalu tersedia. |
| `crm` | Native Community | Ya (18.0, ada di `native-target`) | Modul ini `_inherit` 3 model dari sini: `crm.lead`, `crm.stage`, `res.config.settings` (yang di-extend `crm` module juga). |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak terlihat di manifest:

- Tidak ditemukan pemanggilan `in self.env` atau `try/except ImportError` yang mengindikasikan dependency opsional apapun di ketiga file model.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | — | N/A |
| Assets/CSS/JS custom | ☐ Tidak | Tidak ada `static/src/`, tidak ada key `assets` di manifest (`static/` cuma berisi image description) | N/A |
| Komponen Owl/JavaScript custom | ☐ Tidak | Tidak ada file `.js` di manapun | N/A |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation | ☐ Tidak | Semua field: `Float`/`Boolean`, related sederhana 1 level (`related='stage_id.probability'`) | N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ Tidak | `views/crm_views.xml` sudah pakai `invisible="not show_probability"` langsung (bukan `attrs=`) di source 17.0; tidak ada `states=`; `views/res_config_settings.xml` tidak ada domain/context dinamis | N/A |

**Semua kolom "Ada di modul?" = Tidak** — step 6 (Code Migration) langsung menyatakan fase B2/C2/D1/D2/E/F N/A di Applicability Check, tanpa perlu dikerjakan satu-satu.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Tidak ada** (dikonfirmasi via pencarian file + konfirmasi eksplisit dev).
  - **TIDAK ADA** — `01b_BASELINE_SPEC.md` diisi dari pembacaan kode statis langsung (tidak ada environment executable tersedia di titik intake ini). Semua klaim `[NO-SPEC]`.
- [x] `01b_BASELINE_SPEC.md` sudah diisi.

### 4a. Dokumen Pelengkap Lain

- [x] Ditanya eksplisit ke dev.
- [x] **Dikonfirmasi tidak ada dokumen pelengkap lain** (manual guide, PRD, spec lama format apapun) — dikonfirmasi dev, sesi ini, 2026-08-24.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan (dikonfirmasi dev).

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business logic di §1 (baca `01b_BASELINE_SPEC.md`) — termasuk `security/ir.model.access.csv` yang rusak/tidak terpakai (lihat Ringkasan poin 1) dan struktur nested `crm_probability_from_stage/` (bukan flat) yang sudah dipakai di `source-codebase` 17.0.
- Yang sengaja diubah/di-drop selama migrasi: tidak ada — hanya perubahan yang wajib untuk kompatibilitas 18.0 (lihat `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md`).

## 6. Constraint

- Deadline: tidak disebutkan — tidak diminta eksplisit.
- Owner tiap step: dev (Kuncoro), AI sebagai migration copilot.
