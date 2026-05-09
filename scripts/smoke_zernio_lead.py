#!/usr/bin/env python3
"""Adim 3 smoke test — Zernio payload mapping fix end-to-end.

Three steps in one shot:

1. Sign in to NocoDB (email+password -> JWT) and add 'WhatsApp' to the
   Leadler.kaynak SingleSelect options if missing. NocoDB API tokens (xc-token)
   only allow data CRUD; schema mutation needs a JWT.
2. POST a synthetic Zernio `message.received` webhook to the n8n Lead Toplama
   webhook (https://mindidai.app.n8n.cloud/webhook/lead-toplama). This drives
   the freshly-deployed Calculate Lead Score code node end-to-end.
3. Read the latest Leadler row via xc-token and assert the mapping landed:
   kaynak == 'WhatsApp', telefon, notlar non-empty, asama == 'Sicak'.

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


def step_2_fire_webhook(webhook_url: str) -> str:
    print(f"[2/3] POST synthetic Zernio webhook -> {webhook_url}")
    payload = {
        "id": f"evt_smoke_{int(time.time())}",
        "event": "message.received",
        "message": {
            "id": f"msg_smoke_{int(time.time())}",
            "conversationId": "conv_smoke",
            "platform": "whatsapp",
            "platformMessageId": "wamid.smoke",
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
    code, body = http(
        "POST",
        webhook_url,
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if code >= 300:
        sys.exit(f"      Webhook POST failed: {code} {body}")
    print(f"      Webhook accepted ({code}) — body: {str(body)[:120]}")
    return payload["message"]["sender"]["phoneNumber"]


def step_3_verify(base: str, token: str, expected_phone: str) -> None:
    print("[3/3] NocoDB Leadler — verify last row matches mapping")
    headers = {"xc-token": token, "Content-Type": "application/json"}
    # Wait briefly for n8n to write
    for attempt in range(6):
        time.sleep(2)
        code, res = http(
            "GET",
            f"{base}/api/v2/tables/{LEADS_TABLE_ID}/records?sort=-CreatedAt&limit=3",
            headers=headers,
        )
        if code != 200:
            sys.exit(f"      GET records failed: {code} {res}")
        rows = res.get("list") or []
        # Find a row whose phone matches our smoke phone
        match = next((r for r in rows if (r.get("telefon") or "").replace(" ", "") == expected_phone), None)
        if match:
            print(f"      Found row Id={match.get('Id')} after {attempt + 1} polls")
            print(f"        ad_soyad     = {match.get('ad_soyad')!r}")
            print(f"        telefon      = {match.get('telefon')!r}")
            print(f"        kaynak       = {match.get('kaynak')!r}")
            print(f"        asama        = {match.get('asama')!r}")
            print(f"        lead_skoru   = {match.get('lead_skoru')!r}")
            print(f"        sektor       = {match.get('sektor')!r}")
            print(f"        notlar       = {(match.get('notlar') or '')[:80]!r}")
            print(f"        ihtiyac_notu = {(match.get('ihtiyac_notu') or '')[:80]!r}")

            checks = [
                ("kaynak == 'WhatsApp'", match.get("kaynak") == "WhatsApp"),
                ("asama == 'Sicak'", match.get("asama") == "Sicak"),
                ("notlar non-empty", bool(match.get("notlar"))),
                ("lead_skoru >= 50", (match.get("lead_skoru") or 0) >= 50),
            ]
            failed = [name for name, ok in checks if not ok]
            if failed:
                print(f"      ✗ FAILED: {failed}")
                sys.exit(2)
            print("      All assertions passed ✓")
            return
        print(f"      ...not yet (poll {attempt + 1}/6, latest phones: "
              f"{[r.get('telefon') for r in rows]})")
    sys.exit("      Timed out waiting for the smoke row to appear")


def main() -> None:
    base = env("NOCODB_BASE_URL").rstrip("/")
    token = env("NOCODB_API_TOKEN")
    email = env("NOCODB_EMAIL")
    password = env("NOCODB_PASSWORD")
    webhook = env("LEAD_WEBHOOK", optional=True, default=DEFAULT_WEBHOOK)

    step_1_add_whatsapp_option(base, email, password)
    phone = step_2_fire_webhook(webhook)
    step_3_verify(base, token, phone)
    print("\nSmoke complete. Adim 3 end-to-end yesil.")


if __name__ == "__main__":
    main()
