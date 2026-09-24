# Main Flow Test — crm_probability_from_stage

**Level:** Main Flow — flow bisnis inti yang paling sering dipakai user/admin sehari-hari.
**Estimasi waktu:** ~8 menit.
**Sumber:** skenario ber-`Level: Main Flow` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-02, S-03, S-04).

## Aktifkan "Probability from stage"

```
1. Settings → CRM.
2. Di blok kedua (bersama "Multi Teams" dan "Membership / Partnership") cari "Probability from stage"
   dengan keterangan "Make lead probability computation manually base probability from the stage."
3. Centang → Save → refresh halaman.
   Harus: tetap tercentang.
```

## Isi probability per stage

```
1. CRM → Configuration → Stages → buka "Qualified".
   Harus: ada field "Probability" dengan tanda "%" di kolom kiri, di atas "Is Won Stage?".
2. Isi 75 → Save.
   Harus: tersimpan tanpa error, tampil "75.00 %".
```

## Opportunity mengikuti probability stage

```
1. Buka opportunity dengan Expected Revenue 1000 yang masih di stage lain.
2. Klik "Qualified" di bar stage atas → Save.
   Harus: Probability berubah jadi 75.00.
3. Kembali ke Pipeline → ganti ke tampilan list.
   Harus: kolom "Probability Revenue" ada tepat setelah "Expected Revenue",
          baris opportunity tadi = $ 750.00, dan baris total di bawah ikut menjumlahkan.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker Odoo 20.0 source, `qa_db` | AI (Playwright MCP) | Pass | S-02, S-03, S-04 |
