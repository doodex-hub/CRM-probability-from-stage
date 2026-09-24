# Negative Test — crm_probability_from_stage

**Level:** Negative — hal yang HARUS tidak terjadi.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Negative` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-06).

## Mematikan toggle harus benar-benar mematikan fitur

> Kenapa penting: di Odoo 20.0 nilai "mati" disimpan sebagai teks `False`. Kalau modul salah membacanya,
> fitur tetap aktif walau checkbox sudah tidak dicentang.

```
1. Settings → CRM → hapus centang "Probability from stage" → Save → refresh.
   Harus: tetap tidak tercentang.
2. CRM → Configuration → Stages → buka "Qualified".
   Harus: field "Probability" TIDAK tampil. (Kalau tampil = BUG, stop dan laporkan.)
3. Buka salah satu opportunity.
   Harus: terbuka tanpa pesan error.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker Odoo 20.0 source, `qa_db` | AI (Playwright MCP) | Pass | S-06; DB tersimpan `'False'` |
