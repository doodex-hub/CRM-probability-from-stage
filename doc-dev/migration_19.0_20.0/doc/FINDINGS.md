# Findings — crm_probability_from_stage (migrasi 19.0 → 20.0)

> Dokumen konsolidasi tunggal untuk gap/bug/ambiguitas yang butuh keputusan manusia (template
> `migration-tool/templates/FINDINGS.md`). ID `MF-NNN` tidak pernah dipakai ulang. Step 4 dan Step 8
> wajib membaca file ini sebagai bagian gate.

**Modul:** crm_probability_from_stage
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-24 (akhir Step 9)

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | Aset App Store di branch rilis `19.0` tidak ada di `migration/19.0` | 1 | `[PERLU-KEPUTUSAN]` | Rendah | ✅ RESOLVED 2026-09-24 — dev setuju: tidak di-port di migrasi ini |
| MF-02 | Baseline visual 19.0 belum pernah diverifikasi mata manusia (gate 11 18→19 via waiver) | 1 | `[DIWARISI-SOURCE]` | Sedang | 🟡 OPEN — diteruskan ke Step 10 |
| MF-03 | `get_param`/`set_param` dihapus di 20.0 — pengganti `get_bool` mengubah tafsiran nilai toggle non-kanonik yang diisi manual | 2 | `[GAP-MIGRASI]` | Rendah | ✅ RESOLVED (keputusan AI, rekomendasi berisiko rendah) — pakai `get_bool`; dev boleh koreksi. Bukti: kontrol negatif Step 6 |
| MF-04 | Warning ORM 20.0 "Field crm.lead.probability is both compute and related" di tiap registry load | 6 | `[GAP-MIGRASI]` | Rendah | ✅ RESOLVED 2026-09-24 — dev pilih opsi 2: `compute=None` ditambahkan, warning hilang |
| MF-05 | Tour `crm_probability_pipeline_tour` flaky di 20.0 (race klik "New" sebelum kanban siap) | 9 (rerun) | `[GAP-MIGRASI]` | Sedang | ✅ RESOLVED 2026-09-24 — trigger pola core diterapkan, 5/5 run PASS |

---

## Detail

### MF-01 — Aset App Store di branch rilis `19.0` tidak ada di `migration/19.0`
**Ditemukan di:** Step 1 (2026-09-24), dicatat awal saat conditioning.
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `01a_MIGRATION_INTAKE.md` Ringkasan poin 3.
**Lokasi:** `git diff --stat migration/19.0 origin/19.0 -- crm_probability_from_stage` (47 file).
**Deskripsi:** Branch rilis `19.0` (merge `staging/19.0`, HEAD `b0bca89`) berisi commit pasca-migrasi: `banner.gif` (45 MB) menggantikan `banner.png`, `icon.png` baru, `index.html` ditulis ulang (+1531 baris), folder `static/description/assets/{gifs,icons,screenshots}/`, manifest `images` → `banner.gif`+`icon.png`, dan commit "cleaning" yang **menghapus** `tests/`, `LICENSE`, `step_*.png(.bak)`, `doodex_odoo.png`.
**Dampak:** Tidak ada dampak fungsional (semua di `static/description/` + manifest `images`). Kalau di-port ke `migration/20.0`, penghapusan `tests/` justru menghilangkan dasar Step 9.
**Rekomendasi (dipakai sebagai default):** jangan di-port di branch migrasi. Saat branch rilis `20.0` dibuat dari `migration/20.0`, ulangi packaging store yang sama (aset + cleaning) seperti di 19.0.
**Keputusan pemilik modul:** OK — tidak di-port di branch migrasi (kuncoro@doodex.net, 2026-09-24, via chat CLI). Packaging store diulang saat membuat branch rilis 20.0.

### MF-02 — Baseline visual 19.0 belum pernah diverifikasi mata manusia
**Ditemukan di:** Step 1 (2026-09-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-010`, `BSL-012`; `doc-dev/migration_18.0_19.0/doc/11_uat/11_UAT_CHECKLIST.md` (waiver 2026-08-26); DIFF-04 18→19.
**Deskripsi:** Gate 11 migrasi 18→19 ditutup lewat waiver eksplisit dev, bukan UAT business user. Posisi field "Probability" di form stage (pindah ke grup kedua di 19.0) dan baris setting di Settings → CRM hanya pernah dibuktikan lewat Tour/unit test, tidak pernah dilihat manusia.
**Dampak:** Kalau ada regresi visual yang sudah terjadi di 19.0, 20.0 akan mewarisinya tanpa terdeteksi. Di 20.0 form stage berubah lagi (DIFF-05) — lihat `02_DIFF_ANALYSIS.md`.
**Rekomendasi:** Step 10 wajib memasukkan verifikasi visual live form stage + Settings (screenshot) — bukan `[HASIL-BACA-MURNI]`.
**Keputusan pemilik modul:** *(kosong)*

### MF-03 — `get_param`/`set_param` dihapus di 20.0; pengganti `get_bool` mengubah tafsiran nilai non-kanonik
**Ditemukan di:** Step 2 (2026-09-24)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `DIFF-01`, `DIFF-02` (`02_DIFF_ANALYSIS.md`); `BSL-001`, `BSL-004`, `BSL-009`.
**Lokasi:** `models/crm_lead.py:27`, `models/crm_stage.py:16`, `tests/test_crm_probability_from_stage.py:20,40,44`, `tests/test_crm_probability_tour.py:26`.
**Deskripsi:** API `get_param`/`set_param` tidak ada di 20.0 (wajib ganti). Ada dua pengganti yang "kelihatan" mungkin:
1) `get_str(key)` + truthiness string (paling mirip sintaks lama) — **SALAH**: Settings 20.0 menyimpan OFF sebagai `'False'` (truthy) → toggle OFF tidak pernah bekerja.
2) `get_bool(key)` — `'True'`→True, `'False'`/tidak ada→False. **Identik 19.0 untuk semua nilai yang bisa dihasilkan UI Settings.** Satu-satunya beda: nilai yang diisi manual lewat System Parameters (`'0'`, `'no'`, `'off'`, `'abc'`) — 19.0 menganggap ON (string tak kosong), 20.0 `get_bool` menganggap OFF (`'abc'` + warning log). Checkbox Settings 20.0 sendiri membaca dengan `get_bool`, jadi opsi 2 juga membuat modul konsisten dengan apa yang ditampilkan checkbox.
**Dampak:** Opsi 1 = regresi fitur inti. Opsi 2 = beda hanya di edge case non-UI yang di 19.0 pun sudah tidak konsisten dengan checkbox (checkbox 19.0 akan tampil ter-centang untuk `'0'` juga, jadi di 19.0 konsisten; di 20.0 checkbox tampil tidak ter-centang untuk `'0'` dan modul ikut OFF — tetap konsisten satu sama lain).
**Rekomendasi (dipakai):** opsi 2 `get_bool` — preseden core (`crm.lead.auto.assignment` dimigrasikan persis begini di `odoo20/addons/crm/models/crm_lead.py:2043`). Keputusan teknis berisiko rendah dengan satu opsi jelas lebih aman → diputuskan AI tanpa berhenti (USAGE_GUIDE "Eksekusi Berkelanjutan"), didokumentasikan di `03_MIGRATION_SPEC.md`.
**Keputusan pemilik modul:** *(kosong — boleh koreksi)*
**Bukti eksekusi (Step 6, 2026-09-24):** kode model 19.0 apa adanya di 20.0 → install PASS tapi 6 test `AttributeError: 'ir.config_parameter' object has no attribute 'get_param'` (kedua tour tetap PASS — tidak menangkapnya). Mutasi `get_str` → 5 test FAIL. Kode final `get_bool` → 14/14 PASS.

### MF-04 — Warning ORM "Field crm.lead.probability is both compute and related"
**Ditemukan di:** Step 6 (G1 #1, 2026-09-24)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `DIFF-14`; `BSL-007`.
**Lokasi:** `models/crm_lead.py` definisi `probability`; `odoo20/odoo/orm/fields.py:477-479`.
**Deskripsi:** Redefinisi `probability` sebagai related mewarisi `compute='_compute_probabilities'` dari core. 20.0 mem-pop `compute` dan mencetak `UserWarning` di setiap load registry (5× per start di log G1). Di 19.0 hasil efektifnya sama (related menang lewat `setup_related`), hanya tanpa warning.
**Dampak:** Tidak ada dampak fungsional (AC-02-01 + tour PASS). Log produksi berisik.
**Opsi:** (1) biarkan — identik 19.0, patuh larangan refactor; (2) tambah `compute=None` di definisi field — menghilangkan warning, perilaku sama persis dengan yang ORM lakukan sekarang, perubahan 1 atribut.
**Rekomendasi:** opsi (1) sebagai default migrasi (bukan wajib kompatibilitas); opsi (2) aman kalau dev ingin log bersih.
**Keputusan pemilik modul:** opsi (2) — tambah `compute=None` (kuncoro@doodex.net, 2026-09-24, via chat CLI). Diterapkan `models/crm_lead.py:9-13`.
**Bukti:** 3 run dengan `compute=None` → 0 warning "both compute and related" di semua run; hasil test 1× PASS, 2× FAIL di tour pipeline step 4. 3 run pembanding TANPA `compute=None` → warning 10×/run, hasil 2× PASS, 1× FAIL di step 4 yang sama → kegagalan tour tidak disebabkan `compute=None` (lihat MF-05). Unit test (12) PASS di semua 6 run.

### MF-05 — Tour `crm_probability_pipeline_tour` flaky di 20.0
**Ditemukan di:** rerun Step 9 (2026-09-24), saat verifikasi MF-04.
**Tag:** `[GAP-MIGRASI]`
**Ref:** AC-02-01, AC-03-01, AC-03-03; `09_DEV_TESTING.md`; DIFF-09.
**Lokasi:** `static/tests/tours/crm_probability_pipeline_tour.js` step 3 (`trigger: ".o-kanban-button-new"`).
**Deskripsi:** Total 10 run di 20.0: 7 PASS, 3 FAIL, semua gagal di step 4 (`.o_field_widget[name=name] input` tidak ditemukan dalam 10 detik). Timing log: di run gagal tombol "New" diklik ±0,02–0,07 dtk setelah `web_read_group` kanban kembali, dan view quick-create tidak pernah dimuat; di run lolos jedanya ±0,2–0,3 dtk. Tombol "New" di control panel sudah ada sebelum renderer kanban siap. Tour core `crm` 20.0 untuk alur yang sama (`crm/static/tests/tours/crm_rainbowman.js`) memakai trigger `body:has(.o_kanban_renderer) .o-kanban-button-new` untuk menunggu renderer.
**Dampak:** Bukan bug modul/produk — test otomatis tidak stabil (±30% false-fail). Klaim Step 9 "4/4 PASS" ternyata kebetulan.
**Rekomendasi:** ubah trigger step 3 ke pola core, lalu jalankan suite beberapa kali untuk membuktikan stabil.
**Keputusan pemilik modul:** YA perbaiki (kuncoro@doodex.net, 2026-09-24, via chat CLI). Diterapkan: step 3 trigger → `body:has(.o_kanban_renderer) .o-kanban-button-new` (`static/tests/tours/crm_probability_pipeline_tour.js`). Kode modul tidak disentuh.
**Bukti:** 5 run berturut-turut (DB bersih tiap run, `run-test.sh`) → 5× `0 failed, 0 error(s) of 16 tests`, pipeline tour 11/11 step di tiap run, 0 warning compute+related. Log: `docker-env/logs/run-test_20260924_152221.log` … `_154242.log`.

---

## Cara Pakai

Lihat `migration-tool/templates/FINDINGS.md` §Cara Pakai. Update status (bukan hapus) saat resolved.
