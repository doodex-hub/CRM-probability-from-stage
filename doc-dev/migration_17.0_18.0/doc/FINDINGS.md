# Findings — crm_probability_from_stage (migrasi 17.0 → 18.0)

**Modul:** crm_probability_from_stage
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-10-05 (review pasca-rilis)

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | `security/ir.model.access.csv` rusak/tidak terpakai | 1 | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED — dipertahankan apa adanya, disetujui dev 2026-08-24 |
| MF-02 | Interaksi related-field `probability` vs override PLS (`_compute_probabilities`) | 1 | `[DIWARISI-SOURCE]` | Sedang | ✅ CONFIRMED — didokumentasikan BSL-006/007, jadi basis test plan Step 5 |
| MF-03 | `_compute_is_automated_probability` tidak depends ke `ir.config_parameter` toggle | 1 | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED — konsekuensi mekanisme `@api.depends`, dipertahankan (BSL-005) |
| MF-04 | BSL-001 salah — storage `ir.config_parameter` diasumsikan simetris string, ternyata asimetris | 9 | `[GAP-MIGRASI]` (koreksi dokumentasi, bukan bug modul) | Rendah | ✅ RESOLVED — ditemukan dari test gagal (run #1), `01b_BASELINE_SPEC.md` BSL-001 dikoreksi, test diperbaiki (run #2 pass) |
| MF-05 | `probability` (related, `readonly=False`) menulis tembus ke `crm.stage` | Review pasca-rilis | `[DIWARISI-SOURCE]` | Tinggi | ✅ RESOLVED 2026-10-05 — hotfix 18.0.1.0.1 (membalik keputusan MF-02 17.0→18.0) |

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
**Update 2026-10-05:** koreksi — penilaian "bukan bug" di atas keliru. Related field dengan `readonly=False` menulis tembus ke `crm.stage` (Mark as Lost menjadikan stage 0% untuk semua lead; edit manual mengubah seluruh stage; salesperson biasa kena AccessError). Dibuktikan di Docker dan diperbaiki, lihat MF-05. Keputusan "dipertahankan identik" dibalik oleh pemilik modul pada 2026-10-05.

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

---

### MF-05 — `probability` (related, `readonly=False`) menulis tembus ke `crm.stage`
**Ditemukan di:** review pasca-rilis (bukan migrasi), 2026-10-05
**Tag:** `[DIWARISI-SOURCE]` — ada sejak 17.0, terbawa ke 18.0/19.0/20.0
**Ref:** MF-02 (17.0 → 18.0, "Interaksi related-field `probability`", sebelumnya dicatat "bukan bug"); `odoo20/odoo/orm/fields.py:799` (`_inverse_related`); core `crm.lead.action_set_lost` / `action_set_won`
**Lokasi:** `crm_probability_from_stage/models/crm_lead.py` — definisi field `probability`
**Prioritas:** Tinggi (data forecast salah; Mark as Lost tidak bisa dipakai salesperson biasa)
**Status:** ✅ RESOLVED — hotfix `18.0.1.0.1` dirilis 2026-10-05

**Deskripsi:** `probability` didefinisikan `related='stage_id.probability', readonly=False, store=True`. Field related yang tidak readonly punya inverse yang menulis nilainya ke record tujuan (`crm.stage`) dengan hak user yang sedang login, sehingga *setiap* tulis ke `probability` di lead diteruskan ke stage dan mengubah semua lead di stage itu. Core menulis `probability` pada Mark as Lost (0) dan Mark as Won (100), jadi bug muncul pada alur normal, bukan hanya edit manual.

**Bukti (Docker, skrip RPC yang sama sebelum dan sesudah; toggle ON, stage Qualified = 30%):**

| Skenario | Sebelum | Sesudah |
|---|---|---|
| Admin: Mark as Lost 1 lead | stage Qualified → 0%, semua lead di stage 0% | stage tetap 30%, hanya lead itu 0% (arsip) |
| Admin: edit 1 lead jadi 77% | stage → 77%, semua lead 77% | hanya lead itu 77% |
| Salesperson (`group_sale_salesman_all_leads`): edit atau Mark as Lost | AccessError "not allowed to modify CRM Stage" | berhasil, stage tidak berubah |
| Toggle OFF: `action_set_automated_probability` | nilai PLS 1 lead ditulis ke stage, semua lead ikut | hanya lead itu |
| Mark as Won saat stage Won = 0% | (lihat catatan) | lead 100%, stage tetap 0% |
| Pindah stage, ubah probability stage, `revenue_probability` (regresi) | normal | normal |

Hasil "sebelum" identik di 18.0, 19.0 dan 20.0 (beda hanya teks pesan error).

**Catatan efek samping lama:** Mark as Won sebelumnya hanya "bekerja" karena tulis-tembus menjadikan stage Won = 100. Tanpa itu (stage Won 0%) core menolak dengan "A lead in a Won stage cannot be lost". Karena itu perbaikan menambah aturan "stage won = 100".

**Opsi yang dipertimbangkan:** A) field computed tersimpan yang tetap bisa diedit (dipilih); B) `readonly=True` — satu atribut tapi lead tidak bisa diedit dan Mark as Won error kecuali stage Won diisi 100 manual; C) biarkan.
**Keputusan pemilik modul:** opsi A untuk 18.0/19.0/20.0 (kuncoro@doodex.net, 2026-10-05, via chat). **Membalik keputusan MF-02 (17.0 → 18.0)** yang mempertahankan perilaku related apa adanya. 16.0 dan 17.0 punya kode sama dan sengaja tidak diubah.

**Perubahan kode (hotfix, hanya di `staging/18.0` dan `18.0`):** `probability` menjadi `compute='_compute_probability_from_stage'` (`readonly=False, store=True`, depends `stage_id.probability`, `stage_id.is_won`); helper `_get_stage_probability()` (stage won → 100, selain itu `stage_id.probability`) dipakai juga di cabang else `_compute_probabilities`. Kolom DB sama, tanpa migrasi data. Versi manifest `18.0.1.0.1`.
**Perilaku yang berubah (disengaja):** edit manual probability di lead hanya berlaku untuk lead itu, dan kembali ke nilai stage bila stage lead atau probability stage berubah. Lead lost yang diarsipkan juga kembali ke nilai stage bila stage-nya berubah (sama seperti sebelum perbaikan, tidak diubah).

**Pengujian:** upgrade modul di DB berisi data lama; skenario tabel di atas; skenario tambahan (Mark as Won dengan stage Won 0%, drag ke dan dari stage Won, `revenue_probability`); suite test migrasi dijalankan dari `migration/18.0` dengan `crm_lead.py` baru: 13/13 PASS. Tidak ada warning "both compute and related".
**Belum teruji:** tampilan form lead lewat browser (UI); hanya RPC dan tour bawaan.
**Catatan audit operasional:** instalasi yang sudah berjalan bisa memiliki `crm.stage.probability` yang melenceng akibat bug lama (mis. stage jadi 0 setelah satu lead di-lost). Kode baru tidak memperbaikinya; cek dan koreksi nilai stage secara manual setelah upgrade.
**PERHATIAN untuk branch ini:** kode di `migration/18.0` sengaja TIDAK diubah (masih related, identik source). Bila `staging/18.0` dibangun ulang dari branch ini, port dulu perubahan `models/crm_lead.py` dan versi `18.0.1.0.1`, kalau tidak bug kembali.
**Rilis:** staging `8be15b7→c16dab2`, `18.0` `d223362→a32bf40` (merge commit (history rilis punya merge sendiri)); diff staging = rilis kosong.
