# Findings — crm_probability_from_stage (migrasi 17.0 → 18.0)

**Modul:** crm_probability_from_stage
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | `security/ir.model.access.csv` rusak/tidak terpakai | 1 | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED — dipertahankan apa adanya, disetujui dev 2026-08-24 |
| MF-02 | Interaksi related-field `probability` vs override PLS (`_compute_probabilities`) | 1 | `[DIWARISI-SOURCE]` | Sedang | ✅ CONFIRMED — didokumentasikan BSL-006/007, jadi basis test plan Step 5 |
| MF-03 | `_compute_is_automated_probability` tidak depends ke `ir.config_parameter` toggle | 1 | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED — konsekuensi mekanisme `@api.depends`, dipertahankan (BSL-005) |
| MF-04 | BSL-001 salah — storage `ir.config_parameter` diasumsikan simetris string, ternyata asimetris | 9 | `[GAP-MIGRASI]` (koreksi dokumentasi, bukan bug modul) | Rendah | ✅ RESOLVED — ditemukan dari test gagal (run #1), `01b_BASELINE_SPEC.md` BSL-001 dikoreksi, test diperbaiki (run #2 pass) |

---

## Detail

### MF-01 — `security/ir.model.access.csv` rusak/tidak terpakai
**Ditemukan di:** Step 1 (2026-08-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** BSL-016 (`01b_BASELINE_SPEC.md`)
**Lokasi:** `security/ir.model.access.csv:2`
**Deskripsi:** Baris merujuk `model_id:id` = `model_crm_stage_probability_crm_stage_probability`, model yang tidak eksis di modul ini sama sekali. File di-comment-out di `__manifest__.py` §`data`, jadi efeknya nol saat install (kalau tidak di-comment, install akan gagal total).
**Dampak:** Tidak ada risiko runtime (file tidak dimuat). Kalau suatu saat baris comment dihapus tanpa sadar (mis. saat migrasi manifest), install akan langsung gagal — worth diperhatikan di Step 8 (Code Review), pastikan baris comment tetap ada.
**Rekomendasi:** Pertahankan apa adanya (comment-out + isi rusak) — larangan mutlak "jangan perbaiki bug source" (`CLAUDE.md`).
**Keputusan pemilik modul:** Disetujui dev saat sign-off Step 1 (2026-08-24) — dipertahankan, tidak diperbaiki/dihapus.

---

### MF-02 — Interaksi related-field `probability` vs override PLS (`_compute_probabilities`)
**Ditemukan di:** Step 1 (2026-08-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** BSL-006, BSL-007 (`01b_BASELINE_SPEC.md`)
**Lokasi:** `models/crm_lead.py` (field `probability`, method `_compute_probabilities`)
**Deskripsi:** `probability` adalah `related='stage_id.probability', store=True, readonly=False` — SELALU ikut `stage_id.probability` lewat mekanisme related-field standar ORM setiap kali `stage_id` berubah, TERLEPAS dari toggle `crm.manual.compute.probability`. Toggle itu HANYA mempengaruhi `is_automated_probability` (via `_compute_is_automated_probability`), yang baru berefek balik ke `probability` lewat jalur `_compute_probabilities` (dipanggil PLS, cron/trigger tertentu) — BUKAN via toggle secara langsung.
**Dampak:** Bukan bug — ini business rule inti modul, tapi non-obvious dan mudah salah tebak jadi "toggle ON = probability selalu ikut stage" secara sederhana. Acceptance criteria (Step 5) dan test plan (Step 9/10) WAJIB menguji kedua jalur ini secara terpisah (perubahan `stage_id` langsung vs trigger PLS re-compute), bukan cuma satu skenario.
**Rekomendasi:** Tidak ada perubahan kode — murni dokumentasi behavior untuk basis testing yang akurat.
**Keputusan pemilik modul:** Dikonfirmasi sebagai bagian sign-off Step 1 (2026-08-24) — behavior ini benar dan harus dipertahankan identik di 18.0.

---

### MF-03 — `_compute_is_automated_probability` tidak re-trigger otomatis saat toggle setting berubah
**Ditemukan di:** Step 1 (2026-08-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** BSL-005 (`01b_BASELINE_SPEC.md`)
**Lokasi:** `models/crm_lead.py` — `@api.depends('probability', 'automated_probability')` di `_compute_is_automated_probability`
**Deskripsi:** Decorator `@api.depends` tidak (dan tidak bisa) menyertakan `ir.config_parameter` sebagai dependency. Akibatnya, mengubah toggle setting TIDAK langsung memicu re-compute `is_automated_probability` untuk lead-lead yang sudah ada — baru ter-update saat `probability`/`automated_probability` berubah lagi lewat jalur lain.
**Dampak:** Quirk/bug ringan yang sudah ada di source 17.0 — admin yang mengubah toggle mungkin tidak langsung melihat efeknya di lead existing sampai ada trigger lain. Bukan risiko data-loss/crash.
**Rekomendasi:** Pertahankan apa adanya (larangan "perbaiki bug source").
**Keputusan pemilik modul:** Disetujui dev saat sign-off Step 1 (2026-08-24) — dipertahankan.

---

### MF-04 — BSL-001 salah: storage `ir.config_parameter` diasumsikan simetris string, ternyata asimetris
**Ditemukan di:** Step 9 (2026-08-24)
**Tag:** `[GAP-MIGRASI]` (koreksi dokumentasi baseline spec, bukan bug modul — modul-nya sendiri benar, cuma klaim `01b_BASELINE_SPEC.md` yang salah)
**Ref:** BSL-001 (`01b_BASELINE_SPEC.md`), CAND-07 (`migration-tool/migration-records/crm_probability_from_stage_17_18/SUMMARY.md`)
**Lokasi:** Test `test_toggle_saves_config_parameter` (run #1) gagal: `AssertionError: False != 'False'`
**Deskripsi:** Baseline spec awal mengklaim toggle tersimpan sebagai string `'True'`/`'False'` simetris. Ternyata `ir.config_parameter.set_param(key, False)` MENGHAPUS key (perilaku core Odoo untuk value falsy apapun), jadi `get_param(key, False)` mengembalikan default Python `False`, bukan string.
**Dampak:** Tidak ada dampak ke modul (behavior modul sendiri tetap benar, sudah pakai `get_param(key, False)` dengan default yang tepat) — cuma dokumentasi baseline spec yang perlu dikoreksi supaya tidak menyesatkan test/keputusan berikutnya.
**Rekomendasi:** Tidak ada tindakan kode. Baseline spec sudah dikoreksi langsung.
**Keputusan pemilik modul:** Tidak perlu keputusan — koreksi murni faktual, sudah diterapkan.
