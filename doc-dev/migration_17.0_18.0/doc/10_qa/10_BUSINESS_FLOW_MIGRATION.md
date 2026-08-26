# Business Flow — Migrasi crm_probability_from_stage

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24 (draft awal), diselesaikan 2026-08-26

---

## Catatan Mode Eksekusi — Perjalanan sampai ke Mode D (Tour)

**Percobaan 1 — Claude Browser (in-app pane):** GAGAL total baca DOM webclient (`get_page_text`/`read_page` kosong, `screenshot` "Browser pane is not displayed"), walau network trace membuktikan server render sukses (`200 OK` semua asset). Identik dengan 3 data poin sebelumnya (`library_loan`, `purchase_product_optional`, project resmi modul ini sendiri) — **data poin ke-4**, dicatat di `migration-records/`.

**Percobaan 2 — Claude in Chrome (real browser extension):** Sebagian berhasil (login sukses, screenshot render sempurna, Settings page + search filter menunjukkan setting kita persis di tempat yang benar — bukti visual AC-01-04 tercapai) — TAPI klik interaktif (checkbox, tombol "New", kartu kanban) berhenti ter-registrasi setelah 1-2 interaksi, reproducible lintas tab baru & berbagai teknik (ref-click, koordinat presisi, keyboard, klik ke label). Root cause diduga relay/extension, bukan Odoo (network selalu normal). **Ditemukan juga bug infra nyata** di sela-sela percobaan ini: volume filestore Docker tidak di-mount (`docker-compose.yml`), menyebabkan 500 error pada asset — sudah diperbaiki.

**Percobaan 3 — Mode D, Tour test Odoo native (BERHASIL PENUH):** Dev mengarahkan untuk cek lesson `doc-dev-backfill` soal ini — solusinya adalah Tour test resmi Odoo (`HttpCase.start_tour()`, Chrome DevTools Protocol dikontrol LANGSUNG oleh Odoo test framework, bukan lewat extension eksternal). Diinstansiasi dari `migration-tool/templates/test/tour_example.js.template` + `Dockerfile.template` (resep `google-chrome-stable`). **Hasil: 2 Tour, 15 langkah total, 100% sukses di percobaan pertama** setelah image di-build — lihat `09_DEV_TESTING.md` "Mode D — Tour Test" untuk detail lengkap (log Chrome pid, step-by-step, assertion). Checkbox yang GAGAL diklik lewat Claude in Chrome, berhasil sempurna lewat Tour.

**Kesimpulan dicatat ke knowledge base (CAND-08):** untuk verifikasi UI Odoo yang genuinely butuh klik browser sungguhan, **Tour test (Mode D) jauh lebih reliable** daripada AI-interactive browser automation (Claude Browser maupun Claude in Chrome) — bukan cuma soal Odoo SPA berat, tapi soal jalur kontrol (test framework native vs extension relay). Rekomendasi untuk project migrasi berikutnya: pertimbangkan Mode D sebagai default untuk verifikasi visual, bukan cuma fallback kalau AI-interaktif gagal.

Server live (`http://localhost:8278`, admin/admin) TETAP disiapkan untuk dev — lihat `human_qa/` kalau sewaktu-waktu ingin re-verifikasi manual tanpa AI/Tour.

## Level skenario

### S-01: Toggle "Probability from stage" muncul & berfungsi
**Level:** Smoke
**Mode eksekusi:** ✅ **AI+tool otomatis (Tour)** — `test_crm_probability_settings_tour`
**Steps (dieksekusi Tour, 4 langkah):** filter search "Probability" → klik checkbox → Save → tunggu save selesai.
**Expected:** Setting tersimpan tanpa error. Posisi tepat boleh berbeda dari 17.0 (DIFF-04, kosmetik).
**Actual:** Tour "tour succeeded" (4/4 langkah), assert server-side `ir.config_parameter` = `'True'` — lihat log lengkap `09_DEV_TESTING.md`.
**Status:** [x] Pass

### S-02: Field probability tampil di form stage sesuai toggle
**Level:** Main Flow
**Mode eksekusi:** ✅ **Unit test** (`test_show_probability_computed`) + Code Review (Step 8, xpath `invisible="not show_probability"` dikonfirmasi byte-identical terhadap native-target)
**Expected:** Field terlihat/tersembunyi sesuai `show_probability`.
**Actual:** `show_probability` computed benar sesuai toggle (unit test), dan G1 install sukses membuktikan XML view valid (tidak ada ParseError pada xpath `is_won position=before`). Tidak dijalankan sebagai Tour terpisah — cakupan risikonya sudah rendah (murni satu expression `invisible=`, sudah diverifikasi 3 lapis: kode, unit test, install test).
**Status:** [x] Pass

### S-03: Probability opportunity ikut stage & revenue_probability terhitung
**Level:** Main Flow
**Mode eksekusi:** ✅ **AI+tool otomatis (Tour)** — `test_crm_probability_pipeline_tour`
**Steps (dieksekusi Tour, 11 langkah):** buka app CRM → quick-create opportunity (Expected Revenue 1000) → drag-and-drop ke stage "QA Tour High" (probability=88) → switch list view → assert baris berisi "880".
**Expected:** Probability ikut stage otomatis (AC-02-01); kolom Probability Revenue tampil & terhitung benar (AC-03-01/03).
**Actual:** Tour "tour succeeded" (11/11 langkah) — assertion `880` (= 1000 × 88%) match persis di baris list view, dikonfirmasi lewat klik/drag browser sungguhan (Chrome headless asli).
**Status:** [x] Pass

### S-04: Stage probability tanpa validasi range (quirk dipertahankan)
**Level:** Detail
**Mode eksekusi:** ✅ **Unit test** (`test_stage_probability_no_range_validation`)
**Expected:** Nilai -10 dan 150 tersimpan tanpa error validasi (BSL-014, bug pre-existing dipertahankan).
**Actual:** Unit test membuat stage dengan `probability=-50` dan `probability=150`, keduanya tersimpan tanpa exception.
**Status:** [x] Pass

### Multi-dialog check (WAJIB, `USAGE_GUIDE.md` "Dua Checklist Universal")
- [x] **N/A — dikonfirmasi tidak ada kasus multi-dialog.** Modul ini tidak punya wizard/dialog apapun (tidak ada `TransientModel` baru, tidak ada `target: new` action) — semua interaksi adalah edit field biasa di form/settings.

## Ringkasan per Level

| Level | Skenario | Jumlah | Status |
|---|---|---|---|
| Smoke | S-01 | 1 | ✅ Pass (Tour) |
| Main Flow | S-02, S-03 | 2 | ✅ Pass (Unit + Tour) |
| Detail | S-04 | 1 | ✅ Pass (Unit) |
| Negative | — | 0 | N/A — tidak ada guard/keamanan yang relevan (lihat S-04) |

## Human QA Checklists

Digenerate di `10_qa/human_qa/` (lihat file terpisah) — 4 file per Level, siap dipakai ulang dev/QA tanpa AI kapan saja (server live tetap tersedia untuk itu).

## Loop-back

Tidak ada skenario yang gagal — semua 4 skenario (S-01..S-04) pass lewat kombinasi unit test dan Tour test browser asli, tidak ada yang perlu balik ke Step 9.

## Verdict

- [x] ✅ **Lulus** — 4/4 skenario pass, dikonfirmasi lewat Tour test browser asli (Chrome headless, bukan simulasi/asumsi) untuk S-01 dan S-03, unit test untuk S-02/S-04. AI tidak mengklaim lulus dari analisis kode semata — ada bukti eksekusi browser sungguhan untuk skenario yang genuinely butuh itu.
