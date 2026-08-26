# Main Flow Test — crm_probability_from_stage

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-02, S-03 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Settings → CRM: aktifkan "Probability from stage"
2. Settings → CRM → Stages: buka satu stage, isi field "Probability" = 42, Save
   -> Field "Probability" harus terlihat tepat sebelum field "Won"
3. Uncheck "Probability from stage" di Settings, buka stage yang sama lagi
   -> Field "Probability" harus TIDAK terlihat lagi
4. CRM → Pipeline: buat opportunity baru, Expected Revenue = 1000, Stage = stage dengan probability rendah (mis. 20)
   -> Field Probability opportunity = 20
5. Pindahkan opportunity itu ke stage dengan probability lebih tinggi (mis. 60)
   -> Field Probability opportunity ikut berubah jadi 60
6. Buka list view Pipeline (tampilan tabel)
   -> Kolom "Probability Revenue" muncul setelah kolom "Expected Revenue"
   -> Nilainya = Expected Revenue x Probability% (mis. 1000 x 60% = 600)
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
