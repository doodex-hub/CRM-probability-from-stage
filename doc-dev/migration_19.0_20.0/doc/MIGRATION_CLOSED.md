# Migration Closed — crm_probability_from_stage

> Titik-nol untuk deteksi hotfix (lihat `migration-tool/templates/HOTFIX_REVIEW.md`). Ditulis SEKALI,
> di akhir `11_uat/11_UAT_CHECKLIST.md` — jangan ditulis ulang/diedit setelahnya (kalau branch target
> dilanjutkan untuk migrasi versi berikutnya, ini bukti historis kapan siklus migrasi INI ditutup).

**Migration closed at commit:** `b2aa141129dcca876fdfc6c77ec63644962a4799`
**Branch:** `migration/20.0`
**Tanggal:** 2026-09-24
**Migrasi:** 19.0 → 20.0

**Dasar penutupan: WAIVER dev, bukan UAT sign-off penuh.** Ditulis atas instruksi eksplisit dev
(kuncoro@doodex.net, chat CLI 2026-09-24: "tulis MIGRATION_CLOSED.md juga"), setelah Step 11 ditutup
via waiver ("lanjut step 11 pakai waiver seperti 18→19"). Baris sign-off PM/FA/User di
`11_UAT_CHECKLIST.md` tetap kosong — belum ada business user yang menjalankan UAT sendiri. Kalau UAT
asli dilakukan nanti dan menghasilkan perbaikan kode, perbaikan itu masuk jalur Hotfix Review (commit
setelah SHA di atas), bukan dengan mengubah file ini.

**Catatan untuk Hotfix Review:** commit yang menambahkan file ini (langsung setelah SHA di atas) hanya
menyentuh dokumen (`doc-dev/`, `CLAUDE.md`) — bukan hotfix, abaikan saat scan.
