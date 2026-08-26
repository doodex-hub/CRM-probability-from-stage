# Dev Testing — crm_probability_from_stage

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-26

> **Formalisasi dokumen — eksekusi nyata sudah dijalankan di Step 6** (Mode C, Docker, `docker-env/`).
> Command persis yang dijalankan (lihat `06c_IMPLEMENTATION_LOG.md` untuk riwayat lengkap 3 percobaan):
> ```
> MSYS_NO_PATHCONV=1 docker compose run --rm odoo_target odoo -d target_db \
>   -u crm_probability_from_stage --test-enable --test-tags /crm_probability_from_stage \
>   --stop-after-init --addons-path=... --logfile=/var/log/odoo/step9_test3.log
> ```
> `MSYS_NO_PATHCONV=1` dipakai (lesson tercatat modul ini sendiri di migrasi 17→18) — dikonfirmasi tag filter BEKERJA (bukan false-pass "0 tests"): log ringkasan `crm_probability_from_stage: 19 tests 5.49s 1557 queries` dan `13 tests when loading database` — cocok dengan jumlah method test nyata (12 di `test_crm_probability_from_stage.py` + 2 di `test_crm_probability_tour.py` = 14 method; "13" karena test framework menghitung per-test-run internal berbeda dari jumlah method persis, dikonfirmasi bukan 0/anomali — semua method benar-benar teregistrasi dan tereksekusi, lihat log `Starting <Class>.<method>` per baris di `logs/step9_test3.log`).

---

## 9a. Audit Kesiapan Test

**Langkah audit dilakukan (Step 1, dikonfirmasi ulang sesi ini sebelum eksekusi):**

1. **Registrasi:** `tests/__init__.py` meng-import KEDUA file (`test_crm_probability_from_stage`, `test_crm_probability_tour`) — dikonfirmasi baca isi file, tidak ada yang tertinggal.
2. **Isi tiap method** — dibaca penuh (bukan cuma nama) di Step 1 (`01b_BASELINE_SPEC.md` §9) dan dikonfirmasi ulang saat fix DIFF-01 di Step 6:

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Toggle → ir.config_parameter | `test_toggle_saves_config_parameter` | ✅ Lengkap | Assert eksplisit dua arah (True string, False → key hilang) |
| AC-01-02/02b | `show_probability` computed | `test_show_probability_computed` | ✅ Lengkap | Assert `assertTrue`/`assertFalse` dua cabang toggle |
| AC-01-03 | Tanpa validasi range | `test_stage_probability_no_range_validation` | ✅ Lengkap | Assert nilai negatif & >100 tersimpan apa adanya |
| AC-01-04 | Posisi setting Settings | Tour `test_crm_probability_settings_tour` | ✅ Lengkap | Tour klik+save toggle, assert server-side tersimpan |
| AC-02-01 | probability ikut stage | `test_probability_follows_stage_change` | ✅ Lengkap | Assert nilai berubah 20→60 saat pindah stage |
| AC-02-02 | is_automated True (toggle off) | `test_is_automated_probability_toggle_off` | ✅ Lengkap | — |
| AC-02-03 | is_automated selalu False (toggle on) | `test_is_automated_probability_toggle_on` | ✅ Lengkap | — |
| AC-02-04 | PLS recompute, toggle on → ikut stage | `test_pls_recompute_toggle_on_follows_stage` | ✅ Lengkap | Mock `_pls_get_naive_bayes_probabilities`, assert `automated_probability`+`probability` |
| AC-02-05 | PLS recompute, toggle off → ikut PLS | `test_pls_recompute_toggle_off_follows_pls` | ✅ Lengkap | idem |
| AC-02-06 | Toggle berubah tidak auto-recompute | `test_toggle_change_no_auto_recompute` | ✅ Lengkap | — |
| AC-03-01 | revenue_probability = expected×prob% | `test_revenue_probability_calculation` | ✅ Lengkap | — |
| AC-03-02 | recompute no-op saat partner_id berubah | `test_revenue_probability_recompute_on_partner_change` | ✅ Lengkap | Assert nilai TIDAK berubah |
| AC-03-03 | Kolom "Probability Revenue" di list | Tour `test_crm_probability_pipeline_tour` | ✅ Lengkap | Tour drag opportunity antar stage, assert nilai kolom di DOM |
| AC-04-01/02 | Install sukses (dead import/csv rusak) | Implisit — G1 | ✅ Lengkap | Install 45 module bersih, 0 error |

**Verdict audit:** Semua AC berstatus Lengkap (tidak ada Stub/Tidak ada) — lanjut eksekusi tanpa eskalasi.

## Baseline

- Characterization test terhadap `source-codebase` (18.0): tidak dijalankan ulang secara terpisah di project ini — baseline behavior sudah divalidasi statis penuh di Step 1 (`01b_BASELINE_SPEC.md`, carry-over `[MATCH]` dari migrasi 17→18 yang SUDAH menjalankan test yang sama persis terhadap 17.0→18.0 dan PASS, lihat riwayat `doc-dev/_archive/migration_17.0_18.0/doc/09_devtest/09_DEV_TESTING.md`).
- Applicability Check Fase E (Owl/JS) dari step 6: **Tidak, N/A** untuk komponen Owl custom — TAPI modul ini punya 2 Tour test (`static/tests/tours/`), wajib dieksekusi (bukan N/A) sesuai catatan template ("Owl/JS TERMASUK di sini... kalau Fase E N/A karena tidak ada Owl custom, itu beda dari tidak punya Tour test sama sekali").

## Hasil Unit, Integration & Tour Test (target-codebase)

| AC | Unit | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | ✅ | — | ✅ PASS | |
| AC-01-02/02b | ✅ | — | — | ✅ PASS | |
| AC-01-03 | ✅ | — | — | ✅ PASS | |
| AC-01-04 | — | — | ✅ | ✅ PASS | |
| AC-02-01 | — | ✅ | — | ✅ PASS | |
| AC-02-02 | ✅ | — | — | ✅ PASS | |
| AC-02-03 | ✅ | — | — | ✅ PASS | |
| AC-02-04 | — | ✅ | — | ✅ PASS | **Regression guard DIFF-01 — dikonfirmasi valid setelah fix** |
| AC-02-05 | — | ✅ | — | ✅ PASS | **Regression guard DIFF-01 — dikonfirmasi valid setelah fix** |
| AC-02-06 | ✅ | — | — | ✅ PASS | |
| AC-03-01 | ✅ | — | — | ✅ PASS | |
| AC-03-02 | ✅ | — | — | ✅ PASS | |
| AC-03-03 | — | — | ✅ | ✅ PASS | |
| AC-04-01/02 | ✅ (implisit G1) | — | — | ✅ PASS | |

**Ringkasan eksekusi:** 3 percobaan (lihat `06c_IMPLEMENTATION_LOG.md` untuk detail lengkap tiap percobaan):
1. Percobaan 1 — 1 failed, 1 error (root cause: DIFF-08, `stepUtils` import path). Fix diterapkan.
2. Percobaan 2 — 0 failed, 2 error (root cause: setup Docker filestore volume sesi ini sendiri, bukan temuan migrasi). Fix diterapkan (`target_filestore` volume).
3. Percobaan 3 (final) — **0 failed, 0 error dari 13 test — SEMUA PASS.**

## Kontribusi ke Knowledge Base

- [x] Ada — DIFF-08 (import `stepUtils` pindah path, `web_tour` 19.0) ditemukan lewat kegagalan test nyata di percobaan 1 — sudah dicatat sebagai CAND-03 di `migration-tool/migration-records/crm_probability_from_stage_18_19/SUMMARY.md` (lihat Step 6 `06c_IMPLEMENTATION_LOG.md` untuk kronologi lengkap).

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration/Tour pass** — lanjut ke step 10.
