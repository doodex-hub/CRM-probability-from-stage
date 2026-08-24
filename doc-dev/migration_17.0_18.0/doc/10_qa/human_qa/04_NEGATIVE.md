# Negative Test — crm_probability_from_stage

**Level:** Negative — guard/keamanan, hal yang HARUS ditolak/tidak boleh muncul.

**N/A — modul ini tidak punya skenario ber-Level Negative di `../10_BUSINESS_FLOW_MIGRATION.md`.**
Modul tidak menambah guard/keamanan/permission apapun di luar yang sudah standar Odoo (`base.group_user`
via ACL default `crm`) — satu-satunya kandidat "hal yang harus ditolak" (validasi range probability)
justru sebaliknya: SENGAJA tidak ditolak (lihat `03_DETAIL.md`), jadi tidak masuk kategori ini.
