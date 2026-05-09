#!/usr/bin/env python3
"""Apply Adim 3 fix to the live 'Lead Toplama Agent' n8n workflow.

What this script does:

1. GETs the live workflow l31p16NRZeyk4eEm from n8n Cloud.
2. Replaces the 'Calculate Lead Score' node's jsCode with the Zernio-aware
   payload mapper from `n8n/workflows/lead-toplama-agent.json`.
3. Adds `notlar` and `ihtiyac_notu` fieldUi entries to 'Create Lead in NocoDB'
   so the WhatsApp message text persists into Leadler.
4. PUTs the modified workflow back. Stores a backup of the live JSON to
   /tmp/lead-toplama.backup.<timestamp>.json before mutating.

Usage (Cloud Shell or local):

    export N8N_API_TOKEN='n8n_api_xxxxx'   # https://mindidai.app.n8n.cloud > Settings > n8n API
    python3 scripts/n8n_apply_lead_toplama_fix.py            # apply
    python3 scripts/n8n_apply_lead_toplama_fix.py --dry-run  # preview only

Prerequisite: NocoDB Leadler.kaynak SingleSelect must already include the
'WhatsApp' option, otherwise NocoDB will reject the inbound row with a 422.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://mindidai.app.n8n.cloud/api/v1"
WORKFLOW_ID = "l31p16NRZeyk4eEm"
NODE_CODE = "Calculate Lead Score"
NODE_NOCO = "Create Lead in NocoDB"

REPO_WORKFLOW = (
    Path(__file__).resolve().parent.parent
    / "n8n"
    / "workflows"
    / "lead-toplama-agent.json"
)

EXTRA_FIELDS = [
    {"fieldName": "notlar", "fieldValue": "={{ $json.notlar }}"},
    {"fieldName": "ihtiyac_notu", "fieldValue": "={{ $json.ihtiyac_notu }}"},
]


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


def find_node(nodes: list, name: str) -> dict:
    for n in nodes:
        if n.get("name") == name:
            return n
    sys.exit(f"Node not found: {name}")


def load_repo_jscode() -> str:
    wf = json.loads(REPO_WORKFLOW.read_text())
    return find_node(wf["nodes"], NODE_CODE)["parameters"]["jsCode"]


def main() -> None:
    token = os.environ.get("N8N_API_TOKEN")
    if not token:
        sys.exit(
            "N8N_API_TOKEN not set. Get one from "
            "https://mindidai.app.n8n.cloud > Settings > n8n API > Create API key."
        )
    dry = "--dry-run" in sys.argv

    print(f"[1/4] Loading new jsCode from {REPO_WORKFLOW.name}")
    new_jscode = load_repo_jscode()
    print(f"      {len(new_jscode)} chars, {new_jscode.count(chr(10))} lines")

    print(f"[2/4] GET /workflows/{WORKFLOW_ID}")
    wf = http("GET", f"/workflows/{WORKFLOW_ID}", token)
    print(f"      name={wf['name']!r} active={wf.get('active')} nodes={len(wf['nodes'])}")

    backup = Path(f"/tmp/lead-toplama.backup.{int(time.time())}.json")
    backup.write_text(json.dumps(wf, indent=2, ensure_ascii=False))
    print(f"      backup -> {backup}")

    code_node = find_node(wf["nodes"], NODE_CODE)
    if code_node["parameters"].get("jsCode") == new_jscode:
        print(f"[3/4] {NODE_CODE} already up to date — nothing to do")
    else:
        code_node["parameters"]["jsCode"] = new_jscode
        print(f"[3/4] Replaced jsCode in {NODE_CODE!r}")

    noco_node = find_node(wf["nodes"], NODE_NOCO)
    fields = noco_node["parameters"]["fieldsUi"]["fieldValues"]
    existing = {f["fieldName"] for f in fields}
    added = []
    for f in EXTRA_FIELDS:
        if f["fieldName"] not in existing:
            fields.append(f)
            added.append(f["fieldName"])
    if added:
        print(f"      Added field mapping(s): {', '.join(added)}")
    else:
        print("      All field mappings already present")

    # n8n public PUT only accepts these top-level keys.
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
    }
    if "staticData" in wf and wf["staticData"] is not None:
        payload["staticData"] = wf["staticData"]

    if dry:
        print(f"[4/4] --dry-run: would PUT {len(json.dumps(payload))} bytes — skipping")
        return

    print(f"[4/4] PUT /workflows/{WORKFLOW_ID}")
    res = http("PUT", f"/workflows/{WORKFLOW_ID}", token, body=payload)
    print(f"      OK. versionId={res.get('versionId')} updatedAt={res.get('updatedAt')}")
    print()
    print("Done. Smoke test:")
    print("  Send a WhatsApp message from your test phone (+905439335595) to")
    print("  Slowdays Bodrum, then check NocoDB Leadler — new row should have")
    print("  kaynak=WhatsApp, telefon=+90..., notlar=<message text>, asama=Sicak.")


if __name__ == "__main__":
    main()
