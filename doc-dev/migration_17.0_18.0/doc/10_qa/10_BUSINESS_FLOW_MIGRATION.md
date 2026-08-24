# Business Flow — Migrasi crm_probability_from_stage

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Catatan Mode Eksekusi — AI-interaktif GAGAL (data poin ke-4, konsisten dengan lesson tercatat sebelumnya)

**Dicoba lebih dulu:** server target dinyalakan hidup (`docker compose up -d db_target` + `docker compose run -d ... odoo_target`, live, bukan `--stop-after-init`), login admin berhasil (network trace: `GET /odoo/settings` → `200 OK`, semua asset 200 OK, `load_menus`/`mail/data` sukses — webclient genuinely render sisi server). **TAPI** `Claude Browser` (`get_page_text`/`read_page` → halaman/body kosong, `screenshot` → "Browser pane is not displayed, so the page is not compositing frames") gagal total membaca DOM webclient — identik dengan gejala yang sudah tercatat di `migration-records/crm_probability_from_stage_17_18/SUMMARY.md` (project sebelumnya, tool berbeda) DAN `ai-doc/ROADMAP.md` §3 (3 data poin lain: `library_loan`, `purchase_product_optional`, project resmi modul ini sendiri). **Ini data poin ke-4** — pola yang sama terus berulang lintas project, memperkuat kesimpulan `ROADMAP.md` §3 bahwa verifikasi RPC/test otomatis (reliable) harus dipisah dari verifikasi visual browser automation (terbukti berulang kali rapuh untuk webclient Odoo Owl).

**Mode yang dipakai untuk skenario di bawah:** Manual (dev) — server tetap dibiarkan hidup untuk dev cek langsung. Detail akses:
```
URL   : http://localhost:8278/odoo/settings
Login : admin / admin
```

## Level skenario

### S-01: Toggle "Probability from stage" muncul & berfungsi
**Level:** Smoke
**Precondition:** Modul terinstall (dikonfirmasi G1, Step 6), server hidup di atas.
**Mode eksekusi:** Manual
**Steps:**
1. Login ke `http://localhost:8278` (admin/admin)
2. Buka Settings → CRM
3. Cari baris setting "Probability from stage" (help text: "Make lead probability computation manually base probability from the stage.")
4. Centang, klik Save
**Expected:** Setting tersimpan tanpa error, halaman tidak crash. Posisi tepat (setelah setting "Assign salespersons...", sebelum/setelah "Ringover VOIP Phone") boleh berbeda dari 17.0 (DIFF-04, kosmetik) — bukan kriteria fail.
**Actual:** *(diisi dev)*
**Status:** [ ] Pass / [ ] Fail

### S-02: Field probability tampil di form stage sesuai toggle
**Level:** Main Flow
**Precondition:** S-01 selesai, toggle aktif.
**Mode eksekusi:** Manual
**Steps:**
1. Settings → CRM → Stages (atau edit stage dari pipeline)
2. Buka salah satu stage
3. Cek field "Probability" (widget %) muncul tepat sebelum field "Won"
4. Isi angka (misal 42), Save
5. Uncheck toggle di Settings → CRM, buka stage yang sama lagi
**Expected:** Langkah 3-4: field terlihat & tersimpan. Langkah 5: field "Probability" TIDAK terlihat lagi di form stage.
**Actual:** *(diisi dev)*
**Status:** [ ] Pass / [ ] Fail

### S-03: Probability opportunity ikut stage & revenue_probability terhitung
**Level:** Main Flow
**Precondition:** Ada minimal 2 stage dengan probability berbeda (mis. 20 dan 60).
**Mode eksekusi:** Manual
**Steps:**
1. Buka CRM → Pipeline, buat opportunity baru, isi Expected Revenue = 1000, set stage ke stage probability=20
2. Cek field Probability di form opportunity = 20
3. Pindahkan opportunity ke stage probability=60 (drag kanban atau ubah field Stage)
4. Cek field Probability berubah jadi 60
5. Buka list view Pipeline, cek kolom "Probability Revenue" muncul setelah "Expected Revenue", nilainya sesuai (`expected_revenue * probability / 100`)
**Expected:** Probability ikut stage otomatis (AC-02-01); kolom Probability Revenue tampil & terhitung benar (AC-03-01/03).
**Actual:** *(diisi dev)*
**Status:** [ ] Pass / [ ] Fail

### S-04: Stage probability tanpa validasi range (quirk dipertahankan)
**Level:** Detail
**Precondition:** Toggle aktif (field probability terlihat di form stage).
**Mode eksekusi:** Manual
**Steps:**
1. Buka form stage, isi Probability = -10, Save
2. Buka lagi, isi Probability = 150, Save
**Expected:** Kedua nilai tersimpan tanpa error validasi (BSL-014, bug pre-existing yang sengaja dipertahankan — BUKAN sesuatu yang harus diperbaiki).
**Actual:** *(diisi dev)*
**Status:** [ ] Pass / [ ] Fail

### Multi-dialog check (WAJIB, `USAGE_GUIDE.md` "Dua Checklist Universal")
- [x] **N/A — dikonfirmasi tidak ada kasus multi-dialog.** Modul ini tidak punya wizard/dialog apapun (tidak ada `TransientModel` baru, tidak ada `target: new` action) — semua interaksi adalah edit field biasa di form/settings.

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03 | 2 |
| Detail | S-04 | 1 |
| Negative | — | 0 (N/A — modul tidak punya guard/keamanan/hal-yang-harus-ditolak; satu-satunya kandidat, "tidak ada validasi range", justru sengaja TIDAK ditolak — sudah tercakup S-04 sebagai Detail/quirk, bukan Negative) |

## Human QA Checklists

Digenerate di `10_qa/human_qa/` (lihat file terpisah) — 4 file per Level, siap dipakai ulang dev/QA tanpa AI.

## Loop-back

Tidak ada skenario yang gagal dari sisi analisis/kode (semua sudah terverifikasi Step 6/8/9) — yang tersisa murni verifikasi visual manual oleh dev (lihat catatan Mode Eksekusi di atas). Kalau dev menemukan kegagalan genuine saat menjalankan S-01..S-04 secara manual, balik ke Step 9 (bukan diteruskan ke Step 11 dengan "known issue").

## Verdict

- [ ] ✅ Lulus — **MENUNGGU dev menjalankan S-01..S-04 secara manual** (server live tersedia, lihat akses di atas) dan melaporkan hasilnya — AI tidak bisa mengklaim lulus sepihak untuk verifikasi visual yang genuinely butuh mata manusia/browser automation yang gagal.
- [ ] ❌ Ada kegagalan: ...
