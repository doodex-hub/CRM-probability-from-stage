# Migration Intake — crm_probability_from_stage

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✔️ Gate lulus (2026-09-24) — dijalankan dalam mode "jalan terus sampai Step 9" atas instruksi eksplisit dev di awal sesi; semua asumsi yang belum dikonfirmasi verbatim dicatat di Ringkasan + `FINDINGS.md`, dev bisa koreksi kapan saja.

---

## 0. Folder Referensi

**Checklist (sumber jawaban: instruksi awal sesi dev 2026-09-24 + CLAUDE.md conditioning 2026-09-24):**

- [x] `native-target` (Community 20.0) — `D:\Kuncoro\doodex\repo\odoo20`. Disebut eksplisit oleh dev di instruksi sesi. `odoo/release.py` → `version_info = (20, 0, 0, FINAL, 0, '')`.
- [x] `native-source` (Community 19.0) — `D:\Kuncoro\doodex\repo\odoo19` (dari CLAUDE.md conditioning). `odoo/release.py` → `(19, 0, 0, FINAL, 0, '')`.
- [x] `native-target-enterprise` — `D:\Kuncoro\doodex\repo\enterprise20` (disebut eksplisit dev, addons-only). **Auto-scan manifest tidak menemukan dependency Enterprise** (`depends: ['base', 'crm']`, keduanya Community). Dev menyebut path ini tanpa menyebut dependency Enterprise tambahan → diperlakukan sebagai "jaga-jaga", tidak wajib dianalisis aktif di Step 2 kecuali ditemukan dependency baru. Dicek ringan di Step 2: tidak ada addon Enterprise yang mendefinisikan `revenue_probability`/`show_probability`/`crm.manual.compute.probability` (cek tabrakan nama).
- [x] `native-source-enterprise` — `D:\Kuncoro\doodex\repo\enterprise19` (dari CLAUDE.md), tidak dipakai aktif.
- [x] `third-party-source`/`third-party-target` — **tidak ada** (manifest cuma `base`+`crm`; sama seperti 17→18 dan 18→19; dev tidak menyebut dependency OCA/vendor apapun di instruksi sesi).

> Struktur native dicek: model dua-clone standar — `odoo19`/`odoo20` repo Community penuh (`odoo/`, `addons/`, `odoo-bin`), `enterprise19`/`enterprise20` addons-only terpisah. Bukan folder gabungan seperti project 18→19.

### 0a. Konfirmasi Branch/Versi

- [x] **Source** — branch `migration/19.0` (hasil akhir migrasi 18→19, HEAD `ab189bf`) di repo ini, dirujuk lewat `git show`/`git diff` — tidak ada folder `source-codebase` fisik terpisah (keputusan conditioning). Dikonfirmasi dev verbatim di instruksi sesi: "Source branch: migration/19.0".
- [x] **Target** — branch `migration/20.0` di folder ini (`D:\Kuncoro\doodex\repo\crm-probability-from-stage-migration-20`). Dikonfirmasi dev verbatim: "target branch: migration/20.0 (sudah dibuat saat conditioning)".
- [x] Kode modul di `migration/20.0` saat Step 1 dimulai **identik** dengan `migration/19.0` (`git diff migration/19.0 migration/20.0 -- crm_probability_from_stage docker-env` kosong) — perbedaan cuma CLAUDE.md, `.claude/settings.json`, skeleton `doc-dev/migration_19.0_20.0/`.
- [x] Versi semantik: **19.0 → 20.0**, dikonfirmasi dev verbatim ("Lakukan migrasi 19→20").

### 0b. Gate: Placeholder Path Absolut `.claude/settings.json`

- [x] Tidak ada placeholder `{{ABS_PATH_...}}` tersisa (`grep -c "{{" .claude/settings.json` = 0) — sudah diisi saat conditioning 2026-09-24: deny `Edit` untuk `odoo19`, `enterprise19`, `odoo20`, `enterprise20`, `migration-tool/knowledge/**`, `migration-tool/templates/**`.
- [x] `ABS_PATH_SOURCE_CODEBASE` — N/A (tidak ada folder source terpisah; source = branch di repo yang sama, git hanya read-only `show`/`diff`).
- [x] Third-party — baris deny tidak ada (tidak dipakai).

### 0c. Pre-flight Mode Git (USAGE_GUIDE "Mode Git")

- [x] `git rev-parse` OK, `.git/index.lock` tidak ada, `git fetch origin` dijalankan sebelum klaim branch apapun.
- [x] Working tree: bersih kecuali `.claude/skills/` (untracked — skill library Odoo yang dev salin ke repo, bukan bagian migrasi; **tidak pernah di-stage** oleh AI di commit manapun).
- [ ] Pertanyaan "GUI git client sudah ditutup?" — **tidak ditanyakan interaktif** karena dev menginstruksikan jalan terus tanpa henti sampai Step 9. Asumsi: tertutup. Semua commit dilakukan satu per step, tidak ada push.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Sifat migrasi = port kode saja** (diwarisi dari 17→18 dan 18→19, tidak dikoreksi dev di instruksi sesi) → Step 7 N/A. Kalau ternyata ada instance produksi 19.0 yang akan di-upgrade, beri tahu — ada satu catatan data di `02_DIFF_ANALYSIS.md` (nilai `ir.config_parameter` yang tersimpan tetap kompatibel, lihat MF-03).
2. **Source tidak aktif dikembangkan** (asumsi, sama seperti CLAUDE.md) → `SYNC_POLICY.md` tidak dipakai.
3. **Aset store di branch rilis `19.0`/`staging/19.0` TIDAK di-port** (MF-01). Branch rilis berisi 5+ commit pasca-migrasi (`banner.gif` 45 MB, `index.html` baru, `icon.png` baru, folder `assets/gifs|icons|screenshots`) sekaligus **menghapus** `tests/` dan `LICENSE` (commit "cleaning") — itu packaging App Store, bukan kode fungsional. Source of truth tetap `migration/19.0` (instruksi dev + CLAUDE.md). Rekomendasi: sinkronkan aset store saat membuat branch rilis `20.0`, terpisah dari migrasi ini.
4. **Baseline 19.0 untuk aspek visual belum pernah diverifikasi mata manusia** (MF-02) — gate 11 migrasi 18→19 ditutup via waiver dev. Baseline behavior tetap valid (16 klaim, dicek ulang ke kode 19.0 aktual), tapi posisi field Probability di form stage (DIFF-04 lama) dan tampilan toggle Settings hanya pernah diverifikasi lewat Tour/unit test. Relevan untuk Step 10.
5. **Tidak ada `FUNCTIONAL_SPEC.md`/dokumen pelengkap lain** selain dokumentasi migrasi 17→18 dan 18→19 di `doc-dev/` (carry-over; dev tidak menyebut dokumen lain). Test lama ADA di lokasi yang sama dengan source (`crm_probability_from_stage/tests/`, 11 `TransactionCase` + 2 `HttpCase` tour) — bukan di repo lain.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `crm_probability_from_stage` (satu modul).
- Fungsi: admin menetapkan probability tetap per stage CRM (`crm.stage.probability`); toggle Settings → CRM "Probability from stage" (`ir.config_parameter` `crm.manual.compute.probability`) membuat `crm.lead.probability` mengikuti stage alih-alih PLS (Predictive Lead Scoring) bawaan. Menambah kolom `revenue_probability` (expected_revenue × probability %) di list Opportunities.
- Saling depend dengan modul lain: N/A.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (`odoo20/odoo/addons/base`) | `ir.config_parameter` API berubah total di 20.0 — lihat `02_DIFF_ANALYSIS.md` DIFF-01 |
| `crm` | Native Community | Ya (`odoo20/addons/crm`) | Dipakai lewat inheritance `crm.lead`/`crm.stage`/`res.config.settings` + 2 view |

Dependency implisit (tidak di manifest): `web_tour` (hanya tour test, `@web_tour/tour_utils`) dan `web` (settings form DOM, dipakai tour) — keduanya ditarik transitif oleh `crm`/`base`. Tidak ada `'x' in self.env` runtime check.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 |
|---|---|---|---|
| Controllers (route custom) | ☐ Ya / ☑ Tidak | tidak ada folder `controllers/` | D1 → N/A |
| Assets/CSS/JS custom | ☑ Ya (terbatas) / ☐ Tidak | key `assets` → `web.assets_tests` saja (2 file tour test); tidak ada asset runtime | D2 (cek bundle test), E (cek import path tour) |
| Komponen Owl/JavaScript custom | ☐ Ya / ☑ Tidak | tidak ada `static/src/` | E/F → N/A untuk komponen; **import path tour tetap dicek** (pelajaran CAND-03 18→19) |
| Field JSON, relasi berantai, dynamic model | ☐ Ya / ☑ Tidak | — | B2 → N/A |
| View `attrs=`/`states=`/domain dinamis | ☐ Ya / ☑ Tidak | cuma `invisible="not show_probability"` (sintaks 17+) | C2 → cek ringan |

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target) — asumsi warisan, lihat Ringkasan poin 1
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] `FUNCTIONAL_SPEC.md` lama: **tidak ada** di repo. Sumber baseline = `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (16 BSL `[MATCH]`), di-cross-check ulang terhadap kode `migration/19.0` sesi ini.
- [x] Test lama: **ada**, lokasi SAMA dengan source (`crm_probability_from_stage/tests/`). 11 `TransactionCase` (`test_crm_probability_from_stage.py`) + 2 `HttpCase` tour (`test_crm_probability_tour.py` + 2 file JS di `static/tests/tours/`). Riwayat: ditulis di migrasi 17→18, disesuaikan di 18→19 (mock tuple PLS, import `stepUtils`). 13/13 PASS di 19.0 (Docker, 2026-08-26, `doc-dev/migration_18.0_19.0/doc/09_devtest/09_DEV_TESTING.md`).
- [x] `01b_BASELINE_SPEC.md` sudah diisi (lihat file itu).

### 4a. Dokumen Pelengkap Lain

- [x] Tidak ada dokumen pelengkap di luar `doc-dev/` (carry-over konfirmasi 17→18/18→19; dev tidak menyebut dokumen baru di instruksi sesi). Dokumen yang dibaca: `doc-dev/_archive/migration_17.0_18.0/doc/FINDINGS.md` (MF-01..MF-04), `doc-dev/migration_18.0_19.0/doc/` (01b, 02, 11), `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` (CAND-01/02/03).

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak (asumsi — `migration/19.0` adalah hasil akhir 18→19 yang sudah tuntas; commit pasca-migrasi di branch rilis `19.0` cuma aset store, lihat MF-01)
- [ ] Ya

## 5. Scope Boundary

- **Harus identik pasca migrasi:** seluruh 16 klaim `BSL-001..016` — toggle global, visibility field probability di form stage, override `_compute_is_automated_probability` (toggle ON → selalu False), override `_compute_probabilities` (was_automated False → probability = stage), related-field `probability`, `revenue_probability` + kolom list (sum, monetary, optional show), setting di block kedua app CRM, dan semua quirk (dead import, dead dependency `partner_id`, tanpa validasi range, CSV rusak ter-comment).
- **Sengaja diubah:** hanya yang WAJIB untuk kompatibilitas 20.0 (manifest version; pemanggilan `ir.config_parameter` yang API-nya dihapus — lihat `02_DIFF_ANALYSIS.md`). Test disesuaikan ke API 20.0 tanpa mengubah apa yang diverifikasi.
- **Di-drop:** tidak ada.

## 6. Constraint

- Deadline: tidak disebut — belum relevan, dilewati.
- Owner: Step 1–9 AI (Claude Code CLI, Mode Git). **Step 10 menunggu slot dari dev** (instruksi sesi: maks. 2 repo kecil bersamaan di Step 10, kontensi browser/Docker MF-46). Step 11 business user / dev.
