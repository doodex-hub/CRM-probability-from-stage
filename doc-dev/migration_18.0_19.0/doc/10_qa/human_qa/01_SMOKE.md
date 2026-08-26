# Smoke Test — crm_probability_from_stage

**Level:** Smoke — kalau ini gagal: STOP, jangan lanjut deploy/testing lain.
**Estimasi waktu:** ~2 menit.
**Sumber:** S-01 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Login sebagai admin (atau user dengan akses CRM).
2. Buka app CRM dari menu utama Odoo.
3. Verifikasi: pipeline kanban terbuka tanpa error, stage-stage tampil normal.
```

## Hasil eksekusi

*(isi tiap kali dipakai — jangan overwrite riwayat lama, tambah baris baru)*

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Docker `odoo:19.0` (`docker-env`) | AI (via Tour test `crm_probability_pipeline_tour`, headless Chrome nyata) | ✅ Pass | Bagian awal tour — `showAppsMenuItem()` + klik app CRM sukses |
