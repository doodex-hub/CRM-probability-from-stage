# Findings — crm_probability_from_stage (migrasi 19.0 → 20.0)

> Dokumen konsolidasi tunggal untuk gap/bug/ambiguitas yang butuh keputusan manusia (template
> `migration-tool/templates/FINDINGS.md`). ID `MF-NNN` tidak pernah dipakai ulang. Step 4 dan Step 8
> wajib membaca file ini sebagai bagian gate.

**Modul:** crm_probability_from_stage
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-24

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | Aset App Store di branch rilis `19.0` tidak ada di `migration/19.0` | 1 | `[PERLU-KEPUTUSAN]` | Rendah | 🟡 OPEN — default AI: tidak di-port di migrasi ini |
| MF-02 | Baseline visual 19.0 belum pernah diverifikasi mata manusia (gate 11 18→19 via waiver) | 1 | `[DIWARISI-SOURCE]` | Sedang | 🟡 OPEN — diteruskan ke Step 10 |

---

## Detail

### MF-01 — Aset App Store di branch rilis `19.0` tidak ada di `migration/19.0`
**Ditemukan di:** Step 1 (2026-09-24), dicatat awal saat conditioning.
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `01a_MIGRATION_INTAKE.md` Ringkasan poin 3.
**Lokasi:** `git diff --stat migration/19.0 origin/19.0 -- crm_probability_from_stage` (47 file).
**Deskripsi:** Branch rilis `19.0` (merge `staging/19.0`, HEAD `b0bca89`) berisi commit pasca-migrasi: `banner.gif` (45 MB) menggantikan `banner.png`, `icon.png` baru, `index.html` ditulis ulang (+1531 baris), folder `static/description/assets/{gifs,icons,screenshots}/`, manifest `images` → `banner.gif`+`icon.png`, dan commit "cleaning" yang **menghapus** `tests/`, `LICENSE`, `step_*.png(.bak)`, `doodex_odoo.png`.
**Dampak:** Tidak ada dampak fungsional (semua di `static/description/` + manifest `images`). Kalau di-port ke `migration/20.0`, penghapusan `tests/` justru menghilangkan dasar Step 9.
**Rekomendasi (dipakai sebagai default):** jangan di-port di branch migrasi. Saat branch rilis `20.0` dibuat dari `migration/20.0`, ulangi packaging store yang sama (aset + cleaning) seperti di 19.0.
**Keputusan pemilik modul:** *(kosong)*

### MF-02 — Baseline visual 19.0 belum pernah diverifikasi mata manusia
**Ditemukan di:** Step 1 (2026-09-24)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-010`, `BSL-012`; `doc-dev/migration_18.0_19.0/doc/11_uat/11_UAT_CHECKLIST.md` (waiver 2026-08-26); DIFF-04 18→19.
**Deskripsi:** Gate 11 migrasi 18→19 ditutup lewat waiver eksplisit dev, bukan UAT business user. Posisi field "Probability" di form stage (pindah ke grup kedua di 19.0) dan baris setting di Settings → CRM hanya pernah dibuktikan lewat Tour/unit test, tidak pernah dilihat manusia.
**Dampak:** Kalau ada regresi visual yang sudah terjadi di 19.0, 20.0 akan mewarisinya tanpa terdeteksi. Di 20.0 form stage berubah lagi (DIFF-05) — lihat `02_DIFF_ANALYSIS.md`.
**Rekomendasi:** Step 10 wajib memasukkan verifikasi visual live form stage + Settings (screenshot) — bukan `[HASIL-BACA-MURNI]`.
**Keputusan pemilik modul:** *(kosong)*

---

## Cara Pakai

Lihat `migration-tool/templates/FINDINGS.md` §Cara Pakai. Update status (bukan hapus) saat resolved.
