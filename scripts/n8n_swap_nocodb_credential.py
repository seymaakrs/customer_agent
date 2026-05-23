#!/usr/bin/env python3
"""Swap the NocoDB host used by Lead Toplama's Create Lead node.

The legacy NocoDB credential (LC3XeYkArk2TDsVH, host=34.26.138.196) returns
308 Permanent Redirect after DNS migration to db.mindidai.com.tr — n8n native
NocoDB nodes do not follow redirects, so writes silently fail.

Fix: POST a new credential pointing at the new host, then PUT the workflow
with the Create Lead in NocoDB node re-bound to the new credential id.
Idempotent — re-running finds the existing credential by name and re-uses it.

Required env:
    N8N_API_TOKEN      n8n Cloud API key
    NOCODB_API_TOKEN   xc-token from NocoDB UI (reused inside the credential)

Optional:
    NOCODB_NEW_HOST    default https://db.mindidai.com.tr
    NEW_CRED_NAME      default 'NocoDB Token (db.mindidai.com.tr)'
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://mindidai.app.n8n.cloud/api/v1"
WORKFLOW_ID = "l31p16NRZeyk4eEm"
NODE = "Create Lead in NocoDB"
DEFAULT_HOST = "https://db.mindidai.com.tr"
DEFAULT_NAME = "NocoDB Token (db.mindidai.com.tr)"

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


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"{name} env not set")
    return v


def n8n(method: str, path: str, token: str, body=None):
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
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"n8n {method} {path} failed: {e.code} {e.read().decode()[:400]}")


def find_existing_credential(token: str, name: str) -> dict | None:
    # n8n public API has no list endpoint for credentials in all editions; the
    # safest path is to attempt a deterministic name match via the workflow's
    # node credential block after a CREATE+PUT cycle. As a best-effort, try the
    # /credentials list endpoint first; if it 404s, fall back to None.
    try:
        status, body = n8n("GET", "/credentials", token)
        if isinstance(body, dict):
            body = body.get("data") or body.get("credentials") or []
        if isinstance(body, list):
            for c in body:
                if c.get("name") == name and c.get("type") == "nocoDbApiToken":
                    return c
    except SystemExit:
        # /credentials list disabled — proceed to create.
        pass
    return None


def create_credential(token: str, name: str, host: str, api_token: str) -> str:
    payload = {
        "name": name,
        "type": "nocoDbApiToken",
        "data": {
            "host": host,
            "apiToken": api_token,
            "allowedHttpRequestDomains": "all",
        },
    }
    status, body = n8n("POST", "/credentials", token, body=payload)
    cred_id = body.get("id")
    if not cred_id:
        sys.exit(f"POST /credentials returned no id: {body}")
    print(f"      Created credential id={cred_id} name={name!r}")
    return cred_id


def swap_in_workflow(token: str, new_cred_id: str, new_cred_name: str) -> None:
    status, wf = n8n("GET", f"/workflows/{WORKFLOW_ID}", token)
    create_node = next((n for n in wf["nodes"] if n["name"] == NODE), None)
    if create_node is None:
        sys.exit(f"Node {NODE!r} not found")
    current = create_node.get("credentials", {}).get("nocoDbApiToken") or {}
    if current.get("id") == new_cred_id:
        print(f"      {NODE!r} already bound to {new_cred_id} — no change")
        return
    print(f"      Rebinding {NODE!r}: {current.get('id')!r} -> {new_cred_id!r}")
    create_node["credentials"]["nocoDbApiToken"] = {
        "id": new_cred_id,
        "name": new_cred_name,
    }

    settings = {k: v for k, v in (wf.get("settings") or {}).items() if k in ALLOWED_SETTINGS}
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": settings,
    }
    if wf.get("staticData") is not None:
        payload["staticData"] = wf["staticData"]
    status, res = n8n("PUT", f"/workflows/{WORKFLOW_ID}", token, body=payload)
    print(f"      Workflow PUT OK. versionId={res.get('versionId')}")


def main() -> None:
    n8n_token = env("N8N_API_TOKEN")
    noco_token = env("NOCODB_API_TOKEN")
    host = os.environ.get("NOCODB_NEW_HOST") or DEFAULT_HOST
    name = os.environ.get("NEW_CRED_NAME") or DEFAULT_NAME

    print(f"[1/3] Look up existing credential by name {name!r}")
    existing = find_existing_credential(n8n_token, name)
    if existing:
        cred_id = existing["id"]
        print(f"      Re-using existing credential id={cred_id}")
    else:
        print(f"[2/3] CREATE NocoDB credential host={host}")
        cred_id = create_credential(n8n_token, name, host, noco_token)

    print(f"[3/3] Swap {NODE!r} -> credential {cred_id}")
    swap_in_workflow(n8n_token, cred_id, name)
    print()
    print("Done. Re-run smoke:")
    print("  python3 scripts/smoke_zernio_lead.py")


if __name__ == "__main__":
    main()
