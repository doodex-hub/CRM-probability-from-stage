# Detail Test — crm_probability_from_stage

**Level:** Detail — edge-case/quirk yang sengaja dipertahankan dari versi asal (17.0).
**Estimasi waktu:** ~2 menit.
**Sumber:** S-04 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Dengan toggle "Probability from stage" aktif, buka form sebuah stage
2. Isi field "Probability" = -10, Save -> harus TERSIMPAN tanpa error
3. Isi field "Probability" = 150, Save -> harus TERSIMPAN tanpa error
```

**Catatan:** ini BUKAN bug yang perlu dilaporkan — modul ini secara sengaja tidak memvalidasi
range 0-100 (perilaku yang sudah ada di versi 17.0, dipertahankan apa adanya di migrasi 18.0).

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
