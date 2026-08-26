# Human QA Checklists — crm_probability_from_stage

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia, langkah bernomor siap-jalan.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari (termasuk S-02, satu-satunya yang belum tervalidasi visual sesi ini) | QA rutin, atau setelah deploy fitur baru |
| `03_DETAIL.md` | Varian/edge-case | N/A — modul ini tidak punya skenario Detail |
| `04_NEGATIVE.md` | Guard/keamanan | N/A — modul ini tidak punya skenario Negative aktif (dikonfirmasi tidak ada multi-dialog) |

**Kombinasi disarankan:** deploy kecil → `01_SMOKE.md` saja; deploy rutin → `01_SMOKE.md` + `02_MAIN_FLOW.md`; rilis besar/sebelum UAT → keempat file (walau `03`/`04` isinya N/A untuk modul ini, tetap dicek supaya tidak ada yang diam-diam terlewat).
