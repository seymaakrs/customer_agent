#!/usr/bin/env python3
"""Apply Lead Toplama mutations to the live n8n workflow.

Pulls live workflow l31p16NRZeyk4eEm, runs the same `mutate()` used on the
repo JSON (see lead_workflow_mutation.py), and PUTs it back. A timestamped
backup of the pre-mutation live JSON is written to /tmp first.

Changes applied (idempotent):
1. Calculate Lead Score jsCode -> Zernio-aware mapper that emits
   external_event_id.
2. Create Lead in NocoDB -> field mappings notlar, ihtiyac_notu,
   external_event_id; onError=continueErrorOutput.
3. + Send Lead Error Alert Gmail node, wired to Create Lead's error branch.

Usage:
    export N8N_API_TOKEN='n8n_api_xxxxx'
    python3 scripts/n8n_apply_lead_toplama_fix.py            # apply
    python3 scripts/n8n_apply_lead_toplama_fix.py --dry-run  # preview only

Prerequisite (one-time, per docs/LEAD-IDEMPOTENCY-MIGRATION.md):
- NocoDB Leadler must have a `external_event_id` text column with a unique
  index, plus the SingleSelect option `WhatsApp` on the `kaynak` column.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lead_workflow_mutation import mutate  # noqa: E402

BASE = "https://mindidai.app.n8n.cloud/api/v1"
WORKFLOW_ID = "l31p16NRZeyk4eEm"

# n8n public PUT only accepts these top-level keys, and `settings` only
# allows a whitelist of properties (binaryMode/availableInMCP rejected).
ALLOWED_SETTINGS = {
    "saveExecutionProgress",
    "saveManualExecutions",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "executionTimeout",
    "errorWorkflow",
    "timezone",
    "executionOrder",
}


def http(method: str, path: str, token: str, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "X-N8N-API-KEY": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"n8n API {method} {path} failed: {e.code} {e.read().decode()[:400]}")


def main() -> None:
    token = os.environ.get("N8N_API_TOKEN")
    if not token:
        sys.exit(
            "N8N_API_TOKEN not set. Get one from "
            "https://mindidai.app.n8n.cloud > Settings > n8n API > Create API key."
        )
    dry = "--dry-run" in sys.argv

    print(f"[1/3] GET /workflows/{WORKFLOW_ID}")
    wf = http("GET", f"/workflows/{WORKFLOW_ID}", token)
    print(f"      name={wf['name']!r} active={wf.get('active')} nodes={len(wf['nodes'])}")

    backup = Path(f"/tmp/lead-toplama.backup.{int(time.time())}.json")
    backup.write_text(json.dumps(wf, indent=2, ensure_ascii=False))
    print(f"      backup -> {backup}")

    print("[2/3] Applying mutations")
    changes = mutate(wf)
    if not changes:
        print("      Live workflow already up to date — nothing to PUT.")
        return
    for c in changes:
        print(f"      - {c}")

    settings = {k: v for k, v in (wf.get("settings") or {}).items() if k in ALLOWED_SETTINGS}
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": settings,
    }
    if "staticData" in wf and wf["staticData"] is not None:
        payload["staticData"] = wf["staticData"]

    if dry:
        print(f"[3/3] --dry-run: would PUT {len(json.dumps(payload))} bytes — skipping")
        return

    print(f"[3/3] PUT /workflows/{WORKFLOW_ID}")
    res = http("PUT", f"/workflows/{WORKFLOW_ID}", token, body=payload)
    print(f"      OK. versionId={res.get('versionId')} updatedAt={res.get('updatedAt')}")
    print()
    print("Smoke test next:")
    print("  python3 scripts/smoke_zernio_lead.py  # idempotency assertion included")


if __name__ == "__main__":
    main()
