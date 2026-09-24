# Detail Test — crm_probability_from_stage

**Level:** Detail — varian/edge-case, fitur sekunder.
**Estimasi waktu:** ~5 menit (butuh minimal 1 opportunity Won dan 1 Lost di database).
**Sumber:** skenario ber-`Level: Detail` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-05).

## Probability tetap ikut stage walau Predictive Lead Scoring punya data

```
1. Pastikan "Probability from stage" dicentang, dan stage "Proposition" diisi Probability 40.
2. Pastikan ada minimal satu opportunity yang sudah "Won" dan satu yang "Lost".
3. Settings → CRM → "Update Probabilities" → Update.
   Harus: selesai tanpa pesan error.
4. Buka opportunity (Expected Revenue 1000) → klik "Proposition" di bar stage → Save.
   Harus: Probability = 40.00 (angka dari stage, BUKAN angka prediksi PLS),
          dan di list view Probability Revenue = $ 400.00.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker Odoo 20.0 source, `qa_db` | AI (Playwright MCP) | Pass | S-05 (riwayat won/lost dibuat via JSON-RPC) |
