# Migration Acceptance Criteria — crm_probability_from_stage

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan — **bukan** `03_spec/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-26

> Carry-over dari `doc-dev/_archive/migration_17.0_18.0/doc/05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
> — ID `AC-NN-NN` dipertahankan SAMA PERSIS (bukan dinomori ulang), karena `01b_BASELINE_SPEC.md`
> project ini adalah carry-over `[MATCH]` dari baseline yang sama (semua 16 klaim BSL identik, lihat
> `01_intake/01b_BASELINE_SPEC.md` §Ringkasan). ID ini juga sudah tertanam sebagai referensi langsung
> di `tests/test_crm_probability_from_stage.py` (komentar `# AC-NN-NN` per method) — mempertahankan ID
> yang sama menjaga traceability test tetap valid tanpa perlu rename.

---

## AC-01 — Toggle Setting & Konfigurasi Probability per Stage

**AC-01-01** (verifies `BSL-001`)
Given admin membuka Settings → CRM
When admin mencentang/uncheck field "Probability from stage" (`crm_manual_compute_probability`)
Then nilai tersimpan sebagai `ir.config_parameter` key `crm.manual.compute.probability`, global (bukan per-company) — ON tersimpan string `'True'`, OFF menghapus key sepenuhnya (`get_param(key, False)` lalu return Python `False`)

**AC-01-02** (verifies `BSL-002`, `BSL-009`, `BSL-010`)
Given toggle "Probability from stage" AKTIF
When admin membuka form stage CRM manapun (Settings → CRM → Stages)
Then field "Probability" (widget float, suffix "%") TERLIHAT — **posisi tampil PERSIS di form (grup mana)** boleh berbeda dari 18.0 (lihat DIFF-04, kosmetik: field `is_won` pindah ke grup kedua form di 19.0), tapi field tetap ADA dan tetap langsung sebelum `is_won`

**AC-01-02b** (verifies `BSL-002`, `BSL-009`, `BSL-010`)
Given toggle "Probability from stage" NONAKTIF
When admin membuka form stage CRM manapun
Then field "Probability" TIDAK TERLIHAT di form stage

**AC-01-03** (verifies `BSL-003`, `BSL-014`)
Given form stage dengan field "Probability" terlihat (AC-01-02)
When admin mengisi field probability dengan angka apapun (termasuk negatif atau >100 — TIDAK ADA validasi range, bug yang dipertahankan)
Then nilai tersimpan apa adanya tanpa error validasi

**AC-01-04** (verifies `BSL-012`)
Given toggle "Probability from stage" ada di Settings → CRM
When admin membuka halaman Settings → CRM
Then setting tersebut muncul sebagai satu baris `<setting>` tambahan di block kedua (bersama "Assign salespersons into multiple Sales Teams") — **posisi tampil PERSIS** boleh berbeda dari 18.0 (lihat DIFF-06 — block kedua di 19.0 juga berisi setting baru `module_partnership`, kosmetik, bukan kegagalan AC)

---

## AC-02 — Interaksi `probability` (related-field) vs PLS

**AC-02-01** (verifies `BSL-007`)
Given sebuah opportunity (`crm.lead`) dengan `stage_id` = Stage A (probability stage = 20)
When `stage_id` opportunity itu diubah ke Stage B (probability stage = 60), TERLEPAS dari toggle setting
Then field `probability` opportunity itu otomatis berubah jadi 60 (ikut `stage_id.probability`, lewat mekanisme related-field standar — bukan lewat toggle)

**AC-02-02** (verifies `BSL-004`)
Given toggle "Probability from stage" NONAKTIF, sebuah opportunity dengan `probability` == `automated_probability` (persis sama, presisi 2 desimal)
When `is_automated_probability` di-compute ulang
Then hasilnya `True` (behavior default Odoo, tidak berubah)

**AC-02-03** (verifies `BSL-004`)
Given toggle "Probability from stage" AKTIF, opportunity APAPUN (terlepas nilai `probability`/`automated_probability`)
When `is_automated_probability` di-compute ulang
Then hasilnya SELALU `False`

**AC-02-04** (verifies `BSL-006`) — **regression guard utama untuk DIFF-01**
Given toggle "Probability from stage" AKTIF (sehingga `is_automated_probability` = False, lihat AC-02-03), sebuah opportunity dengan `stage_id` yang punya `probability` stage = 60
When PLS re-compute jalan untuk opportunity itu (`_compute_probabilities` dipanggil — mis. lewat cron/action "Update Probabilities", atau via `crm.stage.write()` baru di 19.0 saat `is_won` berubah, lihat DIFF-03)
Then `automated_probability` diupdate ke hasil PLS (Naive Bayes), TAPI `probability` di-set ke `stage_id.probability` (60) — BUKAN ke `automated_probability` — karena `was_automated` False. **Kalau DIFF-01 belum di-fix di `crm_lead.py`, AC ini akan GAGAL (probability tidak pernah ter-update sama sekali) — ini adalah AC yang seharusnya menangkap regresi DIFF-01, bukan cuma test mock (lihat `05b_TEST_PLAN_MIGRATION.md` catatan Fase 9a).**

**AC-02-05** (verifies `BSL-006`) — **regression guard kedua untuk DIFF-01**
Given toggle "Probability from stage" NONAKTIF, sebuah opportunity yang SEBELUMNYA `is_automated_probability` = True (`was_automated` True saat compute jalan)
When PLS re-compute jalan untuk opportunity itu
Then `probability` di-set ke `automated_probability` hasil PLS (mengikuti behavior asli/default). Sama seperti AC-02-04 — gagal kalau DIFF-01 belum di-fix.

**AC-02-06** (verifies `BSL-005`)
Given sebuah opportunity dengan `is_automated_probability` sudah ter-compute (kapanpun sebelumnya)
When admin mengubah toggle setting (tanpa mengubah `probability`/`automated_probability` opportunity itu)
Then `is_automated_probability` opportunity itu **TIDAK otomatis ter-recompute** — tetap nilai lama sampai `probability`/`automated_probability` berubah lewat jalur lain (bukan bug baru, dipertahankan dari 18.0)

---

## AC-03 — `revenue_probability`

**AC-03-01** (verifies `BSL-008`)
Given sebuah opportunity dengan `expected_revenue` = 1000 dan `probability` = 25
When `revenue_probability` di-compute
Then hasilnya 250 (`= 1000 * 25 / 100`)

**AC-03-02** (verifies `BSL-008`, `BSL-015`)
Given sebuah opportunity dengan `revenue_probability` sudah ter-compute
When `partner_id` opportunity itu diubah (TANPA mengubah `stage_id`/`probability`/`expected_revenue`)
Then `revenue_probability` di-recompute ulang (karena ada di `@api.depends`) TAPI hasilnya TIDAK berubah nilainya — overhead recompute yang tidak perlu, dipertahankan dari 18.0, bukan bug yang mempengaruhi correctness

**AC-03-03** (verifies `BSL-011`)
Given list view Opportunities (Pipeline)
When user membuka list view tersebut
Then kolom "Probability Revenue" (`revenue_probability`) muncul tepat setelah kolom "Expected Revenue", widget monetary, ikut dihitung di baris total (`sum`)

---

## AC-04 — Quirk yang Wajib Dipertahankan (Regression Guard)

**AC-04-01** (verifies `BSL-013`)
Given `models/res_config_settings.py` di-load Odoo
When modul di-install/upgrade
Then tidak ada error — import `timedelta`/`relativedelta` yang tidak dipakai TETAP ADA (dead code, bukan pemicu error, larangan "refactor demi readability")

**AC-04-02** (verifies `BSL-016`)
Given `security/ir.model.access.csv` berisi baris yang merujuk model tidak eksis
When modul di-install
Then install BERHASIL TANPA error — karena baris `# 'security/ir.model.access.csv'` di `__manifest__.py` §`data` TETAP di-comment-out (regression guard: kalau baris comment ini ke-uncomment tanpa sengaja saat migrasi, install akan GAGAL — AC ini eksplisit menjaga supaya tidak terjadi)
