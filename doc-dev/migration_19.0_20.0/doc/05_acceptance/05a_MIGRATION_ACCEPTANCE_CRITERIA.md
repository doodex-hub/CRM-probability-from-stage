# Migration Acceptance Criteria — crm_probability_from_stage

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 19.0 (`migration/19.0`) — **bukan** `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-24

> ID AC dipertahankan dari migrasi 18→19 (dirujuk langsung oleh komentar test). Satu AC baru: **AC-01-05** (jalur Settings sungguhan, regression guard DIFF-02). Semua "Then" = identik 19.0.

---

## AC-01 — Toggle Setting & Konfigurasi Probability per Stage

**AC-01-01** (verifies `BSL-001`)
Given admin di Settings → CRM
When toggle "Probability from stage" di-set ON lalu OFF
Then nilai terbaca balik ON lalu OFF (lewat API baca bertipe yang dipakai modul). *Catatan 20.0:* representasi mentah OFF berubah dari "key dihapus" (19.0) jadi `'False'` (20.0) — perubahan native `base`, bukan modul; yang diverifikasi adalah nilai logis.

**AC-01-02** (verifies `BSL-002`, `BSL-009`, `BSL-010`)
Given toggle ON
When form `crm.stage` dibuka
Then `show_probability` True → label + field Probability + " %" terlihat.

**AC-01-02b** (verifies `BSL-002`, `BSL-009`, `BSL-010`)
Given toggle OFF
When form `crm.stage` dibuka
Then `show_probability` False → field Probability tersembunyi. **(Risiko tinggi DIFF-02.)**

**AC-01-03** (verifies `BSL-003`, `BSL-014`)
Given admin membuat stage
When probability diisi −50 atau 150
Then tersimpan apa adanya, tanpa error validasi.

**AC-01-04** (verifies `BSL-012`)
Given admin membuka Settings → CRM
When halaman dirender
Then baris setting "Probability from stage" dengan help text modul ada di block kedua app CRM, bisa dicentang dan disimpan.

**AC-01-05** (verifies `BSL-001`, `BSL-004`, `BSL-009`) — **BARU, regression guard DIFF-02**
Given toggle di-set ON lalu OFF **lewat `res.config.settings` (`execute()`), bukan API param langsung**
When `show_probability` dan `is_automated_probability` dihitung ulang
Then setelah ON: `show_probability` True, `is_automated_probability` False; setelah OFF: `show_probability` False, `is_automated_probability` = `float_compare(probability, automated_probability, 2) == 0`.

---

## AC-02 — Interaksi `probability` (related-field) vs PLS

**AC-02-01** (verifies `BSL-007`)
Given opportunity di stage A (probability 20), toggle apapun
When dipindah ke stage B (probability 60)
Then `probability` = 60.

**AC-02-02** (verifies `BSL-004`)
Given toggle OFF, `probability == automated_probability`
When `is_automated_probability` dihitung
Then True.

**AC-02-03** (verifies `BSL-004`) — **risiko tinggi DIFF-01**
Given toggle ON
When `is_automated_probability` dihitung
Then False apapun nilai probability/automated_probability (dan tidak ada exception).

**AC-02-04** (verifies `BSL-006`)
Given toggle ON (is_automated_probability False), PLS mengembalikan 99 untuk lead
When `_compute_probabilities` jalan
Then `automated_probability` = 99, `probability` = probability stage.

**AC-02-05** (verifies `BSL-006`)
Given toggle OFF, lead aktif & automated
When PLS mengembalikan 42
Then `automated_probability` = 42, `probability` = 42.

**AC-02-06** (verifies `BSL-005`)
Given lead existing dengan `is_automated_probability` True (toggle OFF)
When toggle diubah ON tanpa write ke lead
Then `is_automated_probability` tidak ter-recompute (tetap True).

---

## AC-03 — `revenue_probability`

**AC-03-01** (verifies `BSL-008`)
Given lead expected_revenue 1000 di stage probability 20
Then `revenue_probability` = 200.

**AC-03-02** (verifies `BSL-008`, `BSL-015`)
Given lead dengan revenue_probability X
When `partner_id` diubah dan compute jalan
Then nilai tetap X.

**AC-03-03** (verifies `BSL-011`)
Given list view Opportunities
Then kolom "Probability Revenue" tampil setelah Expected Revenue, monetary, dengan total di footer; lead 1000 di stage probability 88 menampilkan 880.

---

## AC-04 — Quirk yang Wajib Dipertahankan

**AC-04-01** (verifies `BSL-013`) — dead import `timedelta`/`relativedelta` di `res_config_settings.py` masih ada (review kode).
**AC-04-02** (verifies `BSL-016`) — `security/ir.model.access.csv` masih ter-comment di manifest, isi tidak diubah; modul install sukses (review kode + G1).
