"""Gmail API bildirim maili (Sicak/Ilik). Hata loglanir, istegi asla dusurmez."""
from __future__ import annotations

import base64
import html
import json
import logging
import os
from email.mime.text import MIMEText

logger = logging.getLogger("lead-ingestion.notify")

DEFAULT_MAIL_TO = "hello@slowdaysai.com"
GMAIL_SCOPE = ["https://www.googleapis.com/auth/gmail.send"]


def _credentials():
    sa_json = os.getenv("GMAIL_SA_JSON")
    if sa_json:
        from google.oauth2 import service_account

        info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=GMAIL_SCOPE)
        # Workspace'te SA, gonderen kullanici adina delege edilir
        return creds.with_subject(os.getenv("MAIL_FROM", DEFAULT_MAIL_TO))
    refresh = os.getenv("GMAIL_REFRESH_TOKEN")
    if refresh:
        from google.oauth2.credentials import Credentials

        return Credentials(
            token=None,
            refresh_token=refresh,
            client_id=os.environ["GMAIL_CLIENT_ID"],
            client_secret=os.environ["GMAIL_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=GMAIL_SCOPE,
        )
    return None


def build_mail(lead: dict, ai_not: str) -> tuple[str, str]:
    """Doner: (subject, html_body). Tek standart format."""
    sirket = lead.get("sirket_adi") or "-"
    subject = f"[Lead] {lead['segment'].upper()}: {lead['ad_soyad']} – {sirket} (Skor {lead['lead_skoru']}/100)"
    rows = [
        ("Ad Soyad", lead["ad_soyad"]),
        ("Sirket", sirket),
        ("E-posta", lead.get("email") or "-"),
        ("Telefon", lead.get("telefon") or "-"),
        ("Sektor", lead["sektor"]),
        ("Konum", lead.get("konum") or "-"),
        ("Butce", f"{lead['butce']} TL" if lead.get("butce") else "-"),
        ("Kaynak", lead["source"]),
        ("Skor", f"{lead['lead_skoru']}/100"),
        ("Segment", lead["segment"]),
        ("Asama", lead["asama"]),
        ("Takip Tarihi", str(lead["takip_tarihi"])),
        ("Mesaj", lead.get("mesaj") or "-"),
    ]
    tr = "".join(
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold'>{html.escape(k)}</td>"
        f"<td style='padding:4px 0'>{html.escape(str(v))}</td></tr>"
        for k, v in rows
    )
    body = (
        "<div style='font-family:Arial,sans-serif;font-size:14px'>"
        f"<h2 style='color:#0c1339'>Yeni {html.escape(lead['segment'])} Lead</h2>"
        f"<table>{tr}</table>"
        f"<h3>AI Satis Notu</h3><p>{html.escape(ai_not)}</p></div>"
    )
    return subject, body


def send_lead_mail(lead: dict, ai_not: str) -> bool:
    try:
        creds = _credentials()
        if creds is None:
            logger.warning("Gmail credential yok (GMAIL_SA_JSON / GMAIL_REFRESH_TOKEN) — mail atlandi")
            return False
        from googleapiclient.discovery import build

        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        subject, body = build_mail(lead, ai_not)
        msg = MIMEText(body, "html", "utf-8")
        msg["to"] = os.getenv("MAIL_TO", DEFAULT_MAIL_TO)
        msg["from"] = os.getenv("MAIL_FROM", DEFAULT_MAIL_TO)
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception as exc:
        logger.error("Lead bildirimi gonderilemedi: %s", exc)
        return False
