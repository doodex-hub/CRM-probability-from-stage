#!/usr/bin/env bash
# ==========================================================================
# run-test.sh — wrapper WAJIB untuk SEMUA eksekusi test G2/Step 9 lewat Docker
# ==========================================================================
# Instansiasi dari migration-tool/templates/run-test.sh.template (2026-09-24, migrasi 19.0->20.0).
#
# KENAPA FILE INI ADA (jangan hapus catatan ini):
# Argumen `--test-tags /crm_probability_from_stage` (diawali garis miring) rawan di-mangle
# MSYS/Git Bash di Windows jadi path Windows SEBELUM sampai ke `docker compose`/`odoo-bin`
# -> tag filter kosong -> "0 failed, 0 error(s) of 0 tests" dengan exit code 0 = false-pass.
# Wrapper ini memaksa MSYS_NO_PATHCONV=1 dan gagal (exit non-nol) kalau 0 test ter-start.
#
# Adaptasi project ini (dibanding template):
#  1. Image menjalankan Odoo 20.0 dari source (`ENTRYPOINT python3 /opt/odoo/odoo-bin`), jadi
#     command TIDAK diawali `odoo`, dan `--addons-path` wajib eksplisit.
#  2. DB SELALU di-wipe dulu (`docker compose down -v`) — gotcha G1 19->20: `-i` di atas DB yang
#     sudah pernah install modul yang sama diam-diam skip install+test.
#  3. `--without-demo` tanpa `=all` — di 20.0 `=all` memicu warning "invalid boolean value"
#     (demo memang sudah off secara default sejak 19.0).
#  4. Hitungan "Starting" dibatasi ke baris test method (`Starting <Class>.test_*`), karena log
#     20.0 juga berisi "Starting post tests"/"Starting enrich of company" yang bukan test.
#  5. Exit non-nol juga kalau ringkasan Odoo melaporkan failed/error > 0.
#
# USAGE (dari folder docker-env/):
#   ./run-test.sh <service> <db_name> <module_name> [extra_tags]
#   ./run-test.sh odoo_target target_db crm_probability_from_stage
# ==========================================================================
set -euo pipefail

SERVICE="${1:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
DB_NAME="${2:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
MODULE_NAME="${3:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
EXTRA_TAGS="${4:-}"

TAGS="/${MODULE_NAME}${EXTRA_TAGS}"
mkdir -p logs
LOGFILE="logs/run-test_$(date +%Y%m%d_%H%M%S).log"

echo "=== run-test.sh: MSYS_NO_PATHCONV=1 dipaksa otomatis ==="
echo "=== service=${SERVICE} db=${DB_NAME} module=${MODULE_NAME} tags=${TAGS} ==="
echo "=== log lengkap: docker-env/${LOGFILE} ==="

docker compose down -v >/dev/null 2>&1 || true
docker compose up -d db_target >/dev/null 2>&1
sleep 5

MSYS_NO_PATHCONV=1 docker compose run --rm "${SERVICE}" \
  -d "${DB_NAME}" -i "${MODULE_NAME}" --without-demo \
  --addons-path=/opt/odoo/addons,/opt/odoo/odoo/addons,/mnt/extra-addons \
  --test-enable --test-tags "${TAGS}" --stop-after-init > "${LOGFILE}" 2>&1 || true

echo ""
echo "=== Sanity check otomatis ==="
STARTED_COUNT=$(grep -cE "Starting [A-Za-z0-9_]+\.test_" "${LOGFILE}" || true)
SUMMARY_LINE=$(grep -E "[0-9]+ failed, [0-9]+ error\(s\) of [0-9]+ tests" "${LOGFILE}" | tail -1 || true)
echo "Baris 'Starting <Class>.test_*' ditemukan: ${STARTED_COUNT}"
echo "Ringkasan Odoo: ${SUMMARY_LINE:-'(tidak ditemukan di log)'}"
grep -E "(ERROR|FAIL): " "${LOGFILE}" || true

if [ "${STARTED_COUNT}" -eq 0 ]; then
  echo "GAGAL — 0 test ter-start (pola false-pass). Buka ${LOGFILE}."
  exit 2
fi
if ! echo "${SUMMARY_LINE}" | grep -qE "^.* 0 failed, 0 error\(s\) of"; then
  echo "GAGAL — ada test failed/error (atau ringkasan tidak ditemukan)."
  exit 1
fi
echo "OK — ${STARTED_COUNT} test method ter-eksekusi, 0 failed, 0 error."
