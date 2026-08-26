# Main Flow Test — crm_probability_from_stage

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-02, S-03, S-04 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
Bagian 1 — Toggle & visibility field stage (S-02, BELUM diverifikasi visual — prioritaskan ini):
1. Settings -> CRM -> aktifkan "Probability from stage" -> Save.
2. Settings -> CRM -> Stages -> buka salah satu stage.
3. Cari field "Probability" (angka + suffix "%") -- di 19.0 field ini ada di grup KEDUA
   form (sebelahan dengan "Days to rot"), BUKAN grup pertama seperti sebelumnya -- pastikan
   tetap kelihatan, jangan bingung kalau posisinya beda dari yang diingat.
4. Isi angka apa saja di field Probability, Save -- harus tersimpan tanpa error validasi
   (termasuk kalau isi negatif atau di atas 100, itu memang perilaku lama yang dipertahankan).
5. Matikan toggle "Probability from stage" -> Save.
6. Buka lagi stage yang sama -- field "Probability" harus TIDAK terlihat lagi.

Bagian 2 — Pipeline & Probability Revenue (S-03, sudah PASS via automated tour, opsional re-cek manual):
7. Buka app CRM -> buat opportunity baru lewat quick-create di kanban (isi nama + expected revenue).
8. Drag opportunity itu ke stage manapun yang punya angka Probability tertentu.
9. Switch ke list view -- cari kolom "Probability Revenue" tepat setelah "Expected Revenue".
10. Verifikasi angkanya = Expected Revenue x Probability stage / 100.

Bagian 3 — Settings toggle (S-04, sudah PASS via automated tour, opsional re-cek manual):
11. Settings -> CRM -> ketik "Probability" di kolom pencarian settings.
12. Klik toggle "Probability from stage" -> Save -> pastikan tersimpan (halaman tidak error,
    toggle tetap dalam posisi yang baru diklik setelah reload).
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker `odoo:19.0` (`docker-env`) | AI (via Tour test, Bagian 2 & 3 saja) | ✅ Pass (Bagian 2 & 3) | Bagian 1 (S-02) BELUM dieksekusi visual — tool Browser pane AI tidak bisa compositing di sesi ini, didelegasikan ke dev |
