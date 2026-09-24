# Business Flow — Migrasi crm_probability_from_stage

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md` §Step 10, `09_devtest/09_DEV_TESTING.md`
**Tanggal:** 2026-09-24

> Port kode saja (Step 7 N/A) → dijalankan di **install bersih**, bukan jalur upgrade data produksi.
>
> **Environment:** Odoo 20.0 FINAL dari source `odoo20` (Docker, `docker-env/`), DB baru `qa_db` tanpa demo data (`--without-demo`), `--http-interface=0.0.0.0`, port host 8179, user `admin`. Server dicek dulu dari host (`curl` → HTTP 200) sebelum dipakai browser tool.
> **Mode eksekusi:** AI-interaktif — **Playwright MCP** (headless, default CLI sesuai template). Nilai tersimpan diverifikasi langsung ke Postgres (`psql` di container `db_target`), bukan cuma dari DOM. Screenshot: `screenshots/`.
> **Slot Step 10:** dimulai atas aba-aba dev ("lanjut step 10", 2026-09-24).
>
> **Kenapa Step 10 perlu di luar tour Step 9:** kontrol negatif Step 6 membuktikan tour kanban/list/settings **tidak** memicu compute `show_probability`/`is_automated_probability` (kode 19.0 apa adanya tetap lolos tour). Maka skenario di bawah sengaja membuka **form stage** dan **form opportunity** di kedua posisi toggle.

---

## Skenario

- [x] Skenario dari AC risiko tinggi — AC-01-02/02b, AC-01-05, AC-02-03 (DIFF-01/02) → S-01, S-03, S-06.
- [x] **Cross-Version Compare:** N/A — dikonfirmasi tidak masuk kriteria (satu addon, tanpa dependency Enterprise, 5 `MF-NNN` < 10, dev tidak meminta).
- [x] Spot-check integritas data pasca migrasi: N/A (Step 7 N/A, port kode saja).
- [x] Multi-dialog dari satu aksi: N/A — dikonfirmasi tidak ada (modul tidak membuka dialog/wizard; wizard "Update Probabilities" milik core, satu dialog).

### S-01: Toggle OFF (default instalasi) — form stage & form opportunity tetap bisa dibuka
**Level:** Smoke
**Precondition:** DB baru, modul baru di-install, toggle belum pernah disentuh (param tidak ada).
**Mode eksekusi:** AI-interaktif (Playwright MCP)
**Steps:** 1) CRM → Configuration → Stages → buka "Qualified". 2) CRM → Pipeline → New (form penuh) → isi "QA S01 Opportunity", Expected Revenue 1000 → Save.
**Expected:** Form stage terbuka tanpa error, field "Probability" TIDAK tampil (BSL-002/009). Form opportunity terbuka & tersimpan tanpa error (compute `is_automated_probability` jalan, BSL-004); Probability = probability stage "New" (0).
**Actual:** Form stage: label terlihat hanya "Is Won Stage?", "Rotting in", "Fold by Default"; `div[name=probability]` tidak dirender; tanpa dialog error (`S01_stage_form_toggle_off.png`). Form opportunity: terbuka & tersimpan (record id 1), Probability 0.00 %, Expected Revenue $1,000.00, 0 error console, 0 error dialog (`S01_lead_form_toggle_off.png`).
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-02: Aktifkan "Probability from stage" di Settings → CRM
**Level:** Main Flow
**Precondition:** S-01.
**Mode eksekusi:** AI-interaktif
**Steps:** Settings → CRM → centang "Probability from stage" → Save → reload.
**Expected:** Setting ada di block kedua app CRM dengan help text modul (BSL-012; tetangga baru 20.0 "Multi Teams"/"Membership / Partnership", DIFF-08); tersimpan ON (BSL-001).
**Actual:** Block ke-2 app CRM, help "Make lead probability computation manually base probability from the stage.", tetangga Multi Teams + Membership / Partnership (`S02_settings_before.png`, `S02_settings_toggle_on.png`). Setelah Save checkbox tetap tercentang; DB: `crm.manual.compute.probability = 'True'`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-03: Toggle ON — field Probability tampil di form stage dan bisa diisi
**Level:** Main Flow
**Precondition:** S-02 (toggle ON).
**Mode eksekusi:** AI-interaktif
**Steps:** Buka stage "Qualified" → isi Probability 75 → Save.
**Expected:** Field "Probability" + suffix " %" terlihat (BSL-002/010), posisi 20.0: grup pertama tepat sebelum "Is Won Stage?" (DIFF-05); nilai tersimpan tanpa validasi error (BSL-003).
**Actual:** Grup kiri: Probability → Is Won Stage? → Rotting in; grup kanan: Fold by Default. Tampil "75.00 %" setelah save, rata dengan field lain, tidak ada tumpang tindih (`S03_stage_form_toggle_on.png`). Stage Proposition juga diisi 40 (dipakai S-05).
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-04: Opportunity pindah stage → probability ikut stage, kolom Probability Revenue
**Level:** Main Flow
**Precondition:** S-03 (Qualified = 75%), opportunity "QA S01 Opportunity" Expected Revenue 1000 di stage New.
**Mode eksekusi:** AI-interaktif
**Steps:** 1) Buka opportunity → klik "Qualified" di statusbar → keluar dari form (auto-save). 2) Pipeline → tampilan list.
**Expected:** Probability = 75 (BSL-007), Probability Revenue = 750 (BSL-008); kolom "Probability Revenue" tepat setelah "Expected Revenue", monetary, ada total footer (BSL-011).
**Actual:** Form menampilkan 75.00 (`S04_lead_form_qualified_75.png`). DB: stage Qualified, `probability=75`, `revenue_probability=750`. List: kolom urut "Expected Revenue", "Probability Revenue"; baris $1,000.00 / $750.00; footer $1,000.00 / $750.00 (`S04_list_probability_revenue.png`).
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]
**Catatan:** klik statusbar di 20.0 tidak langsung menulis ke DB — tersimpan saat meninggalkan form (auto-save native). Query DB pertama (sebelum keluar form) masih menunjukkan New/0; query kedua setelah keluar: Qualified/75. Perilaku native, bukan modul.

### S-05: Dengan riwayat PLS (1 won, 1 lost), toggle ON — pindah stage tetap mengikuti probability stage
**Level:** Detail
**Precondition:** toggle ON; dibuat via JSON-RPC 1 opportunity won + 1 lost (DB QA lokal) supaya PLS punya statistik.
**Mode eksekusi:** AI-interaktif (+ JSON-RPC untuk data riwayat)
**Steps:** 1) Settings → "Update Probabilities" → Update. 2) Buka "QA S01 Opportunity" (Qualified) → klik "Proposition" (40%) → Save.
**Expected:** Tanpa error. Setelah pindah stage dengan toggle ON: `probability` = probability stage (40), bukan angka PLS (BSL-006); `revenue_probability` = 400.
**Actual:** Langkah 1: tanpa error; DB `automated_probability` 0 → **91.67**, `probability` tetap 75. Langkah 2: DB `probability=40`, `automated_probability=91.67`, `revenue_probability=400`, form tanpa error.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]
**Catatan penting (batas bukti):** langkah 1 menjalankan jalur batch **core** (`_cron_update_automated_probabilities`, UPDATE SQL yang cuma menyelaraskan `probability` kalau sebelumnya sama dengan `automated_probability`) — modul tidak meng-override jalur ini, jadi hasilnya adalah perilaku core yang identik 19.0↔20.0, bukan bukti override modul. Langkah 2 melewati override `_compute_probabilities` (ORM, depends `stage_id`) dan hasil `probability=40` konsisten dengan BSL-006 — tapi hasil yang sama juga diberikan related-field `stage_id.probability` (BSL-007), dan `automated_probability` kebetulan sama (91.67) sebelum/sesudah, jadi skenario live ini tidak bisa membedakan kedua mekanisme. Pembuktian cabang BSL-006 tetap di unit test Step 9 (`test_pls_recompute_toggle_on_follows_stage` / `_off_follows_pls`, dengan mock PLS).

### S-06: Matikan toggle lewat UI — field Probability HARUS hilang lagi (regresi DIFF-02)
**Level:** Negative
**Precondition:** toggle ON (S-02).
**Mode eksekusi:** AI-interaktif
**Steps:** 1) Settings → CRM → hapus centang "Probability from stage" → Save. 2) Buka stage "Qualified". 3) Buka "QA S01 Opportunity".
**Expected:** DB menyimpan `'False'` (storage baru 20.0, DIFF-02). Field Probability TIDAK boleh tampil di form stage (BSL-002/009) — kalau tampil, berarti nilai `'False'` terbaca sebagai string truthy (regresi yang dicegah `get_bool`). Form opportunity tetap terbuka tanpa error.
**Actual:** DB: `crm.manual.compute.probability = 'False'` (record tidak dihapus — beda dari 19.0, sesuai analisis). Form stage: label hanya "Is Won Stage?", "Rotting in", "Fold by Default"; `div[name=probability]` tidak dirender; tanpa error (`S06_stage_form_after_toggle_off.png`). Form opportunity: terbuka, Probability 40.00 (stage Proposition), 0 error console.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

---

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03, S-04 | 3 |
| Detail | S-05 | 1 |
| Negative | S-06 | 1 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 6 | S-01 … S-06 |
| `[HASIL-BACA]` | 0 | — |
| `[HASIL-BACA-MURNI]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Temuan & Catatan Eksekusi

- **MF-02 (baseline visual):** form stage (toggle ON/OFF) dan baris Settings sekarang terverifikasi live dengan screenshot — tata letak rapi. Posisi Probability di grup pertama (DIFF-05) terkonfirmasi. Ini verifikasi AI-interaktif; lihat mata manusia tetap di Step 11 (UAT) → MF-02 diperbarui.
- **Server log:** satu-satunya ERROR selama sesi berasal dari 2 panggilan JSON-RPC yang saya kirim dengan format argumen salah (08:57:34, `ValueError: not enough values to unpack`) — bukan dari modul atau alur UI. Tidak ada ERROR/Traceback dari alur UI; console browser 0 error.
- **Kegagalan tool:** klik pertama baris stage gagal karena selector ambigu (strict mode, 4 sel) — diulang dengan selector berbeda, berhasil. Satu klik login timeout 5 dtk menunggu navigasi (build asset pertama) — navigasi tetap selesai. Tidak ada STOP-rule yang terpicu.

## Human QA Checklists

Digenerate di `human_qa/` (5 file dari `templates/human_qa/`).

## Loop-back

Tidak ada skenario Fail — tidak ada loop-back ke Step 9.

## Verdict

- [x] ✅ Lulus — semua 6 skenario `[DIKONFIRMASI]` (0 `[HASIL-BACA-MURNI]`) — lanjut ke step 11
- [ ] ⚠️ Lulus Bersyarat
- [ ] ❌ Ada kegagalan
