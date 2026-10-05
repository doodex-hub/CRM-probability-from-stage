# Findings — crm_probability_from_stage (migrasi 18.0 → 19.0)

> Dibuat 2026-10-05 saat review pasca-rilis. Migrasi 18.0 → 19.0 sendiri tidak pernah membuat FINDINGS.md
> (catatan lama tersebar di BASELINE/DIFF/UAT dan migration-records). ID `MF-NNN` tidak pernah dipakai ulang.

**Modul:** crm_probability_from_stage
**Terakhir update:** 2026-10-05

---

## Ringkasan

| ID | Judul | Ditemukan di | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | `probability` (related, `readonly=False`) menulis tembus ke `crm.stage` | Review pasca-rilis | `[DIWARISI-SOURCE]` | Tinggi | ✅ RESOLVED 2026-10-05 — hotfix 19.0.1.0.1 |

---

## Detail

### MF-01 — `probability` (related, `readonly=False`) menulis tembus ke `crm.stage`
**Ditemukan di:** review pasca-rilis (bukan migrasi), 2026-10-05
**Tag:** `[DIWARISI-SOURCE]` — ada sejak 17.0, terbawa ke 18.0/19.0/20.0
**Ref:** MF-02 (17.0 → 18.0, "Interaksi related-field `probability`", sebelumnya dicatat "bukan bug"); `odoo20/odoo/orm/fields.py:799` (`_inverse_related`); core `crm.lead.action_set_lost` / `action_set_won`
**Lokasi:** `crm_probability_from_stage/models/crm_lead.py` — definisi field `probability`
**Prioritas:** Tinggi (data forecast salah; Mark as Lost tidak bisa dipakai salesperson biasa)
**Status:** ✅ RESOLVED — hotfix `19.0.1.0.1` dirilis 2026-10-05

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

**Perubahan kode (hotfix, hanya di `staging/19.0` dan `19.0`):** `probability` menjadi `compute='_compute_probability_from_stage'` (`readonly=False, store=True`, depends `stage_id.probability`, `stage_id.is_won`); helper `_get_stage_probability()` (stage won → 100, selain itu `stage_id.probability`) dipakai juga di cabang else `_compute_probabilities`. Kolom DB sama, tanpa migrasi data. Versi manifest `19.0.1.0.1`.
**Perilaku yang berubah (disengaja):** edit manual probability di lead hanya berlaku untuk lead itu, dan kembali ke nilai stage bila stage lead atau probability stage berubah. Lead lost yang diarsipkan juga kembali ke nilai stage bila stage-nya berubah (sama seperti sebelum perbaikan, tidak diubah).

**Pengujian:** upgrade modul di DB berisi data lama; skenario tabel di atas; skenario tambahan (Mark as Won dengan stage Won 0%, drag ke dan dari stage Won, `revenue_probability`); suite test migrasi dijalankan dari `migration/19.0` dengan `crm_lead.py` baru: 13/13 PASS. Tidak ada warning "both compute and related".
**Belum teruji:** tampilan form lead lewat browser (UI); hanya RPC dan tour bawaan.
**Catatan audit operasional:** instalasi yang sudah berjalan bisa memiliki `crm.stage.probability` yang melenceng akibat bug lama (mis. stage jadi 0 setelah satu lead di-lost). Kode baru tidak memperbaikinya; cek dan koreksi nilai stage secara manual setelah upgrade.
**PERHATIAN untuk branch ini:** kode di `migration/19.0` sengaja TIDAK diubah (masih related, identik source). Bila `staging/19.0` dibangun ulang dari branch ini, port dulu perubahan `models/crm_lead.py` dan versi `19.0.1.0.1`, kalau tidak bug kembali.
**Rilis:** staging `73d1f21→8210643`, `19.0` `b0bca89→52f8eb6` (merge commit); diff staging = rilis kosong.
