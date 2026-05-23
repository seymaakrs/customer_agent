#!/usr/bin/env bash
# One-shot: revert workflow-level guard, apply DB-level partial unique index,
# push the cleaned-up workflow live, run smoke. Exits non-zero on any failure.
#
# Required env:
#   NOCODB_BASE_URL, NOCODB_EMAIL, NOCODB_PASSWORD, NOCODB_API_TOKEN, N8N_API_TOKEN
#
# DB partial unique index needs Postgres access. Two paths:
#   A) PGCONN set (e.g. "postgresql://user:pass@host:5432/nocodb")  -> psql
#   B) NOCODB_DOCKER set to the Docker container name on the VM      -> docker exec
#
# If neither is set the script prints the SQL and the exact one-liner to run
# on the NocoDB VM, then stops at the workflow apply step. Re-run after the
# SQL is in place.

set -euo pipefail

cd "$(dirname "$0")/.."

step() { echo; echo "==[ $* ]=="; }

step "0. Pre-flight"
for v in NOCODB_BASE_URL N8N_API_TOKEN NOCODB_API_TOKEN NOCODB_EMAIL NOCODB_PASSWORD; do
  if [ -z "${!v:-}" ]; then echo "  $v=MISSING"; exit 1; fi
done
echo "  envs OK"

step "1. Apply DB-level partial unique index"
SQL="CREATE UNIQUE INDEX IF NOT EXISTS leadler_external_event_id_uq
  ON leadler (external_event_id)
  WHERE external_event_id IS NOT NULL AND external_event_id <> '';"

if [ -n "${PGCONN:-}" ]; then
  echo "  Path A: psql via PGCONN"
  echo "$SQL" | psql "$PGCONN" -v ON_ERROR_STOP=1
  echo "  ✓ index ensured"
elif [ -n "${NOCODB_DOCKER:-}" ]; then
  echo "  Path B: docker exec into $NOCODB_DOCKER"
  echo "$SQL" | docker exec -i "$NOCODB_DOCKER" psql -U "${PGUSER:-postgres}" -d "${PGDATABASE:-nocodb}" -v ON_ERROR_STOP=1
  echo "  ✓ index ensured"
elif [ -n "${GCE_INSTANCE:-}" ] && [ -n "${GCE_ZONE:-}" ]; then
  echo "  Path C: gcloud compute ssh into $GCE_INSTANCE ($GCE_ZONE)"
  REMOTE_CMD="docker exec -i \$(docker ps --format '{{.Names}}' | grep -i nocodb | head -1) psql -U ${PGUSER:-postgres} -d ${PGDATABASE:-nocodb} -v ON_ERROR_STOP=1"
  echo "$SQL" | gcloud compute ssh "$GCE_INSTANCE" --zone="$GCE_ZONE" --command="$REMOTE_CMD"
  echo "  ✓ index ensured"
else
  cat <<EOF
  Postgres erişimi tanımlı değil. İki yol:

  A) Direkt psql:
       export PGCONN='postgresql://USER:PASS@HOST:5432/DB'
       ./scripts/lead_finalize.sh

  B) NocoDB Docker container içinden:
       export NOCODB_DOCKER=<container name>      # docker ps | grep nocodb
       export PGUSER=postgres PGDATABASE=nocodb   # gerekirse override
       ./scripts/lead_finalize.sh

  C) Uzak GCE VM'ye SSH ile (en yaygın):
       gcloud compute instances list           # VM adını ve zone'u bul
       export GCE_INSTANCE=<vm-name>  GCE_ZONE=<zone>
       export PGUSER=postgres PGDATABASE=nocodb # gerekirse override
       ./scripts/lead_finalize.sh

  Veya tek seferlik manuel (VM SSH'inde):
       docker exec -i \$(docker ps --format '{{.Names}}' | grep -i nocodb | head -1) \\
         psql -U postgres -d nocodb -c "$SQL"

  SQL hazır oldu mu? Doğrulamak için:
       docker exec \$(docker ps --format '{{.Names}}' | grep -i nocodb | head -1) \\
         psql -U postgres -d nocodb -c "\d+ leadler" | grep external_event_id_uq

  Bittiğinde script'i yeniden çalıştır — idempotent, ileri adımları yapacak.
EOF
  echo
  echo "  SKIP (no PG access env). Continuing to workflow apply + smoke anyway"
  echo "  (DB index olmadan smoke step 4'te tekrar fail görmen beklenir)."
fi

step "2. Apply current mutation (reverts Code guard, restores direct wiring)"
python3 scripts/n8n_apply_lead_toplama_fix.py --dry-run
python3 scripts/n8n_apply_lead_toplama_fix.py

step "3. Clean any leftover dupes from earlier runs"
python3 - <<'PY'
import json, os, urllib.request, urllib.error
base = os.environ["NOCODB_BASE_URL"].rstrip("/")
token = os.environ["NOCODB_API_TOKEN"]
url = f"{base}/api/v2/tables/m5lcgc5ifeqh38h/records?where=(external_event_id,like,msg_smoke_%25)&limit=50"
req = urllib.request.Request(url, headers={"xc-token": token})
with urllib.request.urlopen(req) as r:
    rows = json.load(r).get("list", [])
print(f"  smoke rows found: {len(rows)} -> {[r['Id'] for r in rows]}")
if rows:
    data = json.dumps([{"Id": r["Id"]} for r in rows]).encode()
    req = urllib.request.Request(
        f"{base}/api/v2/tables/m5lcgc5ifeqh38h/records",
        data=data,
        method="DELETE",
        headers={"xc-token": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        print(f"  deleted ({r.status})")
PY

step "4. Smoke (4 steps)"
python3 scripts/smoke_zernio_lead.py

echo
echo "Done."
