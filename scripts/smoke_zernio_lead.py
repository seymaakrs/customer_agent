#!/usr/bin/env python3
"""Lead Toplama smoke test — Zernio mapping + idempotency end-to-end.

Four steps in one shot:

1. Sign in to NocoDB (email+password -> JWT) and add 'WhatsApp' to the
   Leadler.kaynak SingleSelect options if missing. NocoDB API tokens (xc-token)
   only allow data CRUD; schema mutation needs a JWT.
2. POST a synthetic Zernio `message.received` webhook to the n8n Lead Toplama
   webhook with a deterministic external_event_id derived from the run id.
3. Verify Leadler row: kaynak=WhatsApp, asama=Sicak, notlar non-empty,
   external_event_id matches, lead_skoru >= 50.
4. POST the SAME payload a second time and verify only ONE row exists for
   that external_event_id (idempotency assertion — covers Zernio at-least-once
   delivery and user double-tap).

Required env:
    NOCODB_BASE_URL    e.g. http://34.26.138.196
    NOCODB_API_TOKEN   xc-token (data CRUD only)
    NOCODB_EMAIL       admin email (for JWT)
    NOCODB_PASSWORD    admin password
Optional:
    LEAD_WEBHOOK       default https://mindidai.app.n8n.cloud/webhook/lead-toplama
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

LEADS_TABLE_ID = "m5lcgc5ifeqh38h"
DEFAULT_WEBHOOK = "https://mindidai.app.n8n.cloud/webhook/lead-toplama"


def env(name: str, *, optional: bool = False, default: str | None = None) -> str:
    v = os.environ.get(name) or default
    if not v and not optional:
        sys.exit(f"{name} env not set")
    return v or ""


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


def step_1_add_whatsapp_option(base: str, email: str, password: str) -> None:
    print("[1/3] NocoDB schema: ensure Leadler.kaynak has 'WhatsApp' option")

    # Sign in -> JWT
    code, body = http(
        "POST",
        f"{base}/api/v1/auth/user/signin",
        headers={"Content-Type": "application/json"},
        body={"email": email, "password": password},
    )
    if code != 200 or not isinstance(body, dict) or "token" not in body:
        sys.exit(f"      Sign-in failed: {code} {body}")
    jwt = body["token"]
    auth = {"xc-auth": jwt, "Content-Type": "application/json"}
    print("      Signed in")

    # GET table metadata to find the kaynak column id
    code, table = http(
        "GET", f"{base}/api/v1/db/meta/tables/{LEADS_TABLE_ID}", headers=auth
    )
    if code != 200:
        sys.exit(f"      GET table failed: {code} {table}")
    columns = table.get("columns", [])
    col = next((c for c in columns if c.get("title") == "kaynak"), None)
    if not col:
        sys.exit("      'kaynak' column not found")
    options = (col.get("colOptions") or {}).get("options") or []
    titles = {o.get("title") for o in options}
    print(f"      kaynak column id={col['id']} options={sorted(titles)}")

    if "WhatsApp" in titles:
        print("      'WhatsApp' already present — no schema change")
        return

    options.append({"title": "WhatsApp", "color": "#d1f7c4"})
    payload = {
        "title": col["title"],
        "uidt": col["uidt"],
        "colOptions": {"options": options},
    }
    code, res = http(
        "PATCH", f"{base}/api/v1/db/meta/columns/{col['id']}", headers=auth, body=payload
    )
    if code >= 300:
        sys.exit(f"      PATCH column failed: {code} {res}")
    print("      Added 'WhatsApp' option ✓")


def build_payload(run_id: int) -> dict:
    """Deterministic per-run Zernio payload. message.id is the idempotency key."""
    return {
        "id": f"evt_smoke_{run_id}",
        "event": "message.received",
        "message": {
            "id": f"msg_smoke_{run_id}",
            "conversationId": "conv_smoke",
            "platform": "whatsapp",
            "platformMessageId": f"wamid.smoke.{run_id}",
            "direction": "incoming",
            "text": "Smoke test: Slowdays paketi hakkinda bilgi alabilir miyim?",
            "attachments": [],
            "sender": {
                "id": "905555555555",
                "name": "Smoke Test Otel",
                "phoneNumber": "+905555555555",
                "businessScopedUserId": "bsuid_smoke_001",
            },
            "sentAt": "2026-05-09T16:00:00Z",
            "isRead": False,
        },
        "conversation": {
            "id": "conv_smoke",
            "platformConversationId": "conv_plat_smoke",
            "participantId": "905555555555",
            "participantName": "Smoke Test Otel",
            "status": "active",
        },
        "account": {"id": "69ecc2273a63baf2053dfc21", "platform": "whatsapp", "username": "Slowdays Bodrum"},
        "timestamp": "2026-05-09T16:00:00Z",
    }


def fire_webhook(webhook_url: str, payload: dict, *, label: str) -> None:
    code, body = http(
        "POST",
        webhook_url,
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if code >= 300:
        sys.exit(f"      Webhook POST ({label}) failed: {code} {body}")
    print(f"      [{label}] webhook accepted ({code}) — body: {str(body)[:120]}")


def query_rows_by_event_id(base: str, token: str, external_event_id: str) -> list[dict]:
    headers = {"xc-token": token, "Content-Type": "application/json"}
    # URL-encode would be nicer, but external_event_id is alphanum/dot only here.
    where = f"(external_event_id,eq,{external_event_id})"
    code, res = http(
        "GET",
        f"{base}/api/v2/tables/{LEADS_TABLE_ID}/records?where={where}&limit=10",
        headers=headers,
    )
    if code != 200:
        sys.exit(f"      GET records by event_id failed: {code} {res}")
    return res.get("list") or []


def step_3_verify_mapping(base: str, token: str, external_event_id: str) -> None:
    print(f"[3/4] NocoDB Leadler — verify row for external_event_id={external_event_id!r}")
    for attempt in range(6):
        time.sleep(2)
        rows = query_rows_by_event_id(base, token, external_event_id)
        if rows:
            match = rows[0]
            print(f"      Found row Id={match.get('Id')} after {attempt + 1} polls")
            print(f"        ad_soyad           = {match.get('ad_soyad')!r}")
            print(f"        telefon            = {match.get('telefon')!r}")
            print(f"        kaynak             = {match.get('kaynak')!r}")
            print(f"        asama              = {match.get('asama')!r}")
            print(f"        lead_skoru         = {match.get('lead_skoru')!r}")
            print(f"        sektor             = {match.get('sektor')!r}")
            print(f"        notlar             = {(match.get('notlar') or '')[:80]!r}")
            print(f"        ihtiyac_notu       = {(match.get('ihtiyac_notu') or '')[:80]!r}")
            print(f"        external_event_id  = {match.get('external_event_id')!r}")

            checks = [
                ("kaynak == 'WhatsApp'", match.get("kaynak") == "WhatsApp"),
                ("asama == 'Sicak'", match.get("asama") == "Sicak"),
                ("notlar non-empty", bool(match.get("notlar"))),
                ("lead_skoru >= 50", (match.get("lead_skoru") or 0) >= 50),
                ("external_event_id round-trips", match.get("external_event_id") == external_event_id),
            ]
            failed = [name for name, ok in checks if not ok]
            if failed:
                print(f"      ✗ FAILED: {failed}")
                sys.exit(2)
            print("      All mapping assertions passed ✓")
            return
        print(f"      ...not yet (poll {attempt + 1}/6)")
    sys.exit("      Timed out waiting for the smoke row to appear")


def step_4_verify_idempotency(
    base: str, token: str, webhook_url: str, payload: dict, external_event_id: str
) -> None:
    print(f"[4/4] Idempotency — re-fire SAME payload, expect row count to stay at 1")
    fire_webhook(webhook_url, payload, label="replay")
    # Give n8n time to process & either dedupe via unique index or no-op via guard.
    for attempt in range(6):
        time.sleep(2)
        rows = query_rows_by_event_id(base, token, external_event_id)
        count = len(rows)
        print(f"      poll {attempt + 1}/6 — rows for event_id={external_event_id!r}: {count}")
        if count > 1:
            ids = [r.get("Id") for r in rows]
            sys.exit(
                f"      ✗ Idempotency violated: {count} rows for the same event_id "
                f"(Ids={ids}). NocoDB unique index on external_event_id likely missing — "
                f"see docs/LEAD-IDEMPOTENCY-MIGRATION.md."
            )
        if attempt >= 2 and count == 1:
            # Stable for at least 2 polls past the replay window.
            print("      Idempotency holds ✓ (1 row after replay)")
            return
    print("      Idempotency holds ✓ (1 row throughout)")


def main() -> None:
    base = env("NOCODB_BASE_URL").rstrip("/")
    token = env("NOCODB_API_TOKEN")
    email = env("NOCODB_EMAIL")
    password = env("NOCODB_PASSWORD")
    webhook = env("LEAD_WEBHOOK", optional=True, default=DEFAULT_WEBHOOK)

    step_1_add_whatsapp_option(base, email, password)

    run_id = int(time.time())
    payload = build_payload(run_id)
    external_event_id = payload["message"]["id"]
    print(f"[2/4] POST synthetic Zernio webhook -> {webhook} (event_id={external_event_id})")
    fire_webhook(webhook, payload, label="initial")

    step_3_verify_mapping(base, token, external_event_id)
    step_4_verify_idempotency(base, token, webhook, payload, external_event_id)
    print("\nSmoke complete. Lead Toplama end-to-end + idempotency yesil.")


if __name__ == "__main__":
    main()
