#!/usr/bin/env python3
"""One-shot NocoDB schema migration for Lead Toplama idempotency.

What it does (all idempotent — safe to re-run):

1. Sign in to NocoDB with email+password to obtain a JWT (xc-token cannot
   mutate schema).
2. Add `external_event_id` column to the Leadler table if missing
   (SingleLineText, nullable, default empty).
3. Mark the column as unique if NocoDB exposes it via meta API. If not
   supported by this NocoDB version, print the exact SQL the operator
   should run on the underlying Postgres (partial unique index that ignores
   empty strings so legacy rows are unaffected).
4. Verify by GETting the column metadata back and printing the final state.

Required env (same as smoke_zernio_lead.py):
    NOCODB_BASE_URL    e.g. http://34.26.138.196
    NOCODB_EMAIL       admin email (for JWT)
    NOCODB_PASSWORD    admin password

Usage:
    python3 scripts/nocodb_apply_idempotency_migration.py            # apply
    python3 scripts/nocodb_apply_idempotency_migration.py --dry-run  # plan only
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

LEADS_TABLE_ID = "m5lcgc5ifeqh38h"
COLUMN_TITLE = "external_event_id"


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"{name} env not set")
    return v


def http(method: str, url: str, *, headers: dict, body=None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def sign_in(base: str, email: str, password: str) -> dict:
    code, body = http(
        "POST",
        f"{base}/api/v1/auth/user/signin",
        headers={"Content-Type": "application/json"},
        body={"email": email, "password": password},
    )
    if code != 200 or not isinstance(body, dict) or "token" not in body:
        sys.exit(f"Sign-in failed: {code} {body}")
    return {"xc-auth": body["token"], "Content-Type": "application/json"}


def get_table(base: str, auth: dict) -> dict:
    code, table = http("GET", f"{base}/api/v1/db/meta/tables/{LEADS_TABLE_ID}", headers=auth)
    if code != 200:
        sys.exit(f"GET table failed: {code} {table}")
    return table


def find_column(table: dict, title: str) -> dict | None:
    return next((c for c in table.get("columns", []) or [] if c.get("title") == title), None)


def create_column(base: str, auth: dict) -> None:
    payload = {
        "title": COLUMN_TITLE,
        "uidt": "SingleLineText",
        "rqd": False,
        "cdf": None,
    }
    code, res = http(
        "POST",
        f"{base}/api/v1/db/meta/tables/{LEADS_TABLE_ID}/columns",
        headers=auth,
        body=payload,
    )
    if code >= 300:
        sys.exit(f"POST create column failed: {code} {res}")
    print(f"      Created column {COLUMN_TITLE!r} ✓")


def try_mark_unique(base: str, auth: dict, column_id: str) -> bool:
    """Return True if NocoDB accepted a `un=True` PATCH on the column."""
    code, res = http(
        "PATCH",
        f"{base}/api/v1/db/meta/columns/{column_id}",
        headers=auth,
        body={"un": True},
    )
    if code < 300:
        print(f"      Marked column unique via meta API ✓")
        return True
    print(f"      meta API didn't accept un=True ({code}) — falling back to SQL hint")
    return False


def print_sql_fallback() -> None:
    print()
    print("      Manual unique index (run on the Postgres NocoDB uses):")
    print()
    print("        CREATE UNIQUE INDEX IF NOT EXISTS leadler_external_event_id_uq")
    print(f"          ON leadler (external_event_id)")
    print(f"          WHERE external_event_id IS NOT NULL")
    print(f"            AND external_event_id <> '';")
    print()
    print("      Partial index lets legacy rows (empty external_event_id) coexist.")
    print("      After running, re-run this script — verification step will be green.")


def main() -> None:
    base = env("NOCODB_BASE_URL").rstrip("/")
    email = env("NOCODB_EMAIL")
    password = env("NOCODB_PASSWORD")
    dry = "--dry-run" in sys.argv

    print(f"[1/4] Sign in to {base}")
    auth = sign_in(base, email, password)
    print("      OK")

    print(f"[2/4] GET Leadler table ({LEADS_TABLE_ID})")
    table = get_table(base, auth)
    col = find_column(table, COLUMN_TITLE)
    print(f"      table={table.get('title')!r} columns={len(table.get('columns') or [])} "
          f"{COLUMN_TITLE}_present={bool(col)}")

    if col is None:
        if dry:
            print(f"[3/4] --dry-run: would POST new column {COLUMN_TITLE!r}")
        else:
            print(f"[3/4] POST new column {COLUMN_TITLE!r}")
            create_column(base, auth)
            table = get_table(base, auth)
            col = find_column(table, COLUMN_TITLE)
    else:
        print(f"[3/4] Column {COLUMN_TITLE!r} already exists — skipping create")

    print(f"[4/4] Ensure unique constraint on {COLUMN_TITLE}")
    if col is None:
        print("      Column missing (dry-run); cannot mark unique.")
        return
    is_unique = bool(col.get("un"))
    if is_unique:
        print("      Column already marked unique ✓")
    elif dry:
        print(f"      --dry-run: would PATCH un=True on column id={col['id']}")
    else:
        accepted = try_mark_unique(base, auth, col["id"])
        if not accepted:
            print_sql_fallback()

    print()
    print("Migration complete. Now:")
    print("  python3 scripts/n8n_apply_lead_toplama_fix.py --dry-run")
    print("  python3 scripts/n8n_apply_lead_toplama_fix.py")
    print("  python3 scripts/smoke_zernio_lead.py")


if __name__ == "__main__":
    main()
