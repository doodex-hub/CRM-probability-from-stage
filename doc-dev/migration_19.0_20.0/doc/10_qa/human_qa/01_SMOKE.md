# Smoke Test — crm_probability_from_stage

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain, balik ke step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Smoke` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-01).

```
1. Login sebagai admin.
2. Pastikan Settings → CRM → "Probability from stage" TIDAK dicentang.
3. Buka CRM → Configuration → Stages → klik stage mana saja (mis. "Qualified").
   Harus: form terbuka tanpa pesan error, dan TIDAK ada field "Probability".
4. Buka CRM → Pipeline → klik "New" → isi nama opportunity + Expected Revenue 1000 → Save.
   Harus: tersimpan tanpa pesan error. Field "Probability" di form = probability stage-nya.
5. Buka lagi opportunity tadi dari Pipeline.
   Harus: terbuka tanpa pesan error.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker Odoo 20.0 source, `qa_db` | AI (Playwright MCP) | Pass | S-01 |
