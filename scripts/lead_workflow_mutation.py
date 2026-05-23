#!/usr/bin/env python3
"""Idempotent Lead Toplama workflow mutation.

Re-shapes a Lead Toplama Agent workflow dict to add:

1. external_event_id propagation in Calculate Lead Score jsCode (Zernio
   message.id / platformMessageId; non-Zernio falls back to raw.external_event_id
   or '').
2. external_event_id field mapping in Create Lead in NocoDB.
3. onError=continueErrorOutput on Create Lead in NocoDB so NocoDB unique-index
   violations (duplicate external_event_id) AND missing-SingleSelect-option 422s
   route to a dedicated alert instead of failing the workflow silently.
4. New Gmail node "Send Lead Error Alert" wired to Create Lead's error output.

Re-running on an already-mutated workflow is a no-op.

Two consumers:
- CLI: `python3 scripts/lead_workflow_mutation.py` mutates the repo JSON file.
- Import: `n8n_apply_lead_toplama_fix.py` calls `mutate(wf)` on the live
  workflow dict before PUTing it back to n8n.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WF_PATH = Path(__file__).resolve().parent.parent / "n8n" / "workflows" / "lead-toplama-agent.json"

NEW_JSCODE = """// Zernio webhook (message.received) -> Lead mapping.
// Backwards compatible: generic webhook (LinkedIn/Manuel/etc) bypasses the
// detection branch. Detection key: Zernio always sends an 'event' field plus
// nested 'message.sender'.
const raw = $input.first().json.body || $input.first().json;
const isZernio = !!(raw && raw.event && raw.message && raw.message.sender);

let item;
let externalEventId = '';
if (isZernio) {
  const m = raw.message || {};
  const sender = m.sender || {};
  const conv = raw.conversation || {};
  const platform = (m.platform || (raw.account && raw.account.platform) || '').toLowerCase();

  // Phone in E.164 if Zernio gives it; otherwise reconstruct from sender.id (digits-only fallback for WA).
  let telefon = sender.phoneNumber || '';
  if (!telefon && /^\\d{8,}$/.test(sender.id || '')) telefon = '+' + sender.id;

  // Map Zernio platform -> NocoDB Leadler.kaynak SingleSelect option.
  // 'WhatsApp' option must exist in NocoDB (Adim 3 prerequisite).
  const kaynakMap = { whatsapp: 'WhatsApp', instagram: 'IG DM', facebook: 'IG DM' };
  const kaynak = kaynakMap[platform] || 'Manuel';

  // Slowdays cold outreach is otelci-bazli; default sektor speeds scoring.
  const sektorDefault = platform === 'whatsapp' ? 'Otelcilik' : '';

  // Idempotency key — Zernio always sends message.id (server UUID).
  // platformMessageId (e.g. wamid.xxx) is the WhatsApp Cloud API id, used as a
  // secondary fallback. raw.id is the envelope-level event id.
  externalEventId = m.id || m.platformMessageId || raw.id || '';

  item = {
    ad_soyad: sender.name || conv.participantName || '',
    email: '',
    telefon,
    sirket_adi: sender.name || conv.participantName || '',
    sektor: sektorDefault,
    konum: '',
    kaynak,
    // Inbound message = lead replied = sicak (eski monitor mantigi).
    asama: m.direction === 'incoming' ? 'Sicak' : 'Yeni',
    notlar: m.text || '',
    ihtiyac_notu: m.text ? ('Zernio ' + platform + ': ' + String(m.text).slice(0, 200)) : ''
  };
} else {
  item = raw;
  // Non-Zernio (LinkedIn/Manuel) callers may supply their own idempotency key.
  externalEventId = raw.external_event_id || raw.event_id || '';
}

let skor = 0;
const hedefSektorler = ['Otelcilik', 'Yeme-Icme', 'Turizm', 'Spa-Wellness'];
if (hedefSektorler.includes(item.sektor)) skor += 20;
else if (item.sektor && item.sektor !== 'Diger') skor += 10;

const hedefKonumlar = ['Bodrum', 'Marmaris', 'Fethiye', 'Datca', 'Gocek'];
if (hedefKonumlar.some(k => (item.konum || '').includes(k))) skor += 15;
else if ((item.konum || '').includes('Mugla')) skor += 10;

if (item.kaynak === 'Meta Ads') skor += 25;
else if (item.kaynak === 'WhatsApp') skor += 20;
else if (item.kaynak === 'Clay' || item.kaynak === 'LinkedIn') skor += 15;
else if (item.kaynak === 'IG DM') skor += 10;
else if (item.kaynak === 'Manuel') skor += 5;

if (item.asama === 'Sicak') skor += 30;
else if (item.asama === 'Ilik') skor += 20;
else if (item.asama === 'Yeni') skor += 5;

const validSectors = ['Otelcilik','Yeme-Icme','Perakende','Turizm','E-ticaret','Tekne-Yat','Emlak','Spa-Wellness','Doktor-Uzman','Koc-Egitmen','Kurumsal-Kamu','Butik-Moda','Kafe','Restoran','Diger'];
const sektorClean = validSectors.includes(item.sektor) ? item.sektor : 'Diger';

return [{json: {
  ad_soyad: item.ad_soyad || '',
  email: item.email || '',
  telefon: item.telefon || '',
  sirket_adi: item.sirket_adi || '',
  sektor: sektorClean,
  konum: item.konum || '',
  kaynak: item.kaynak || 'Manuel',
  asama: item.asama || 'Yeni',
  lead_skoru: skor,
  notlar: item.notlar || '',
  ihtiyac_notu: item.ihtiyac_notu || '',
  external_event_id: externalEventId
}}];
"""

IDEMPOTENCY_CHECK_JSCODE = """// Workflow-level idempotency guard.
// Looks up Leadler for an existing row with the same external_event_id;
// if found, returns [] so downstream nodes (Create Lead) are not triggered.
// If external_event_id is empty (legacy non-Zernio webhooks), passes through.
// Belt-and-suspenders: DB-side unique constraint should also be added later,
// but NocoDB 0.301.x SingleLineText un=true does not always materialize the
// physical index. This guard is the portable safety net.
const item = $input.first().json;
const eid = item.external_event_id || '';
if (!eid) {
  return [{ json: item }];
}

const cred = await this.getCredentials('nocoDbApiToken');
const host = (cred.host || '').replace(/\\/$/, '');
const url = `${host}/api/v2/tables/m5lcgc5ifeqh38h/records`
  + `?where=${encodeURIComponent('(external_event_id,eq,' + eid + ')')}`
  + `&limit=1`;

let exists = false;
try {
  const res = await this.helpers.httpRequest({
    method: 'GET',
    url,
    headers: { 'xc-token': cred.apiToken, 'Accept': 'application/json' },
    json: true,
  });
  exists = ((res && res.list) || []).length > 0;
} catch (err) {
  // On lookup failure, fail OPEN (allow the write) so a transient NocoDB
  // outage does not block fresh leads. Duplicates remain extremely unlikely
  // in this window (Zernio retry interval > seconds).
  console.log('Idempotency lookup failed; proceeding with insert:', err && err.message);
  return [{ json: item }];
}

if (exists) {
  // Drop the item silently — duplicate.
  return [];
}
return [{ json: item }];
"""


def make_idempotency_node(cred_id: str, cred_name: str) -> dict:
    return {
        "id": "a1b2c3d4-e5f6-4789-89ab-cdef01234567",
        "name": "Check Idempotency",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [40, 0],
        "parameters": {
            "jsCode": IDEMPOTENCY_CHECK_JSCODE,
        },
        "credentials": {
            "nocoDbApiToken": {"id": cred_id, "name": cred_name},
        },
    }


ERROR_ALERT_NODE = {
    "id": "f8a3c2e1-1d4b-4c7a-9f2e-ab12cd34ef56",
    "name": "Send Lead Error Alert",
    "type": "n8n-nodes-base.gmail",
    "typeVersion": 2.2,
    "position": [320, 160],
    "parameters": {
        "resource": "message",
        "operation": "send",
        "sendTo": "seymaakrs@gmail.com",
        "subject": "=[Lead Toplama] NocoDB yazma hatasi (event_id={{ $json.external_event_id }})",
        "emailType": "html",
        "message": (
            "=<h3>NocoDB Create Lead hata verdi</h3>"
            "<p>Bu mesaj iki sebepten gelir: (a) duplicate external_event_id "
            "(idempotency koruyucu calisti, beklenen davranis) veya "
            "(b) SingleSelect option NocoDB sema'sinda eksik (orn. WhatsApp).</p>"
            "<p><b>external_event_id:</b> {{ $json.external_event_id }}</p>"
            "<p><b>kaynak:</b> {{ $json.kaynak }}</p>"
            "<p><b>telefon:</b> {{ $json.telefon }}</p>"
            "<p><b>asama:</b> {{ $json.asama }}</p>"
            "<p><b>n8n error:</b> {{ $json.error || $json.message || 'unknown' }}</p>"
            "<hr><p>Idempotency (a) ise <b>aksiyon yok</b>. Schema (b) ise NocoDB "
            "Leadler.kaynak option listesine eksik degeri ekleyin.</p>"
        ),
        "options": {},
    },
    "credentials": {
        "gmailOAuth2": {
            "id": "REDACTED",
            "name": "Gmail account",
        }
    },
}


def find_node(nodes, name):
    for n in nodes:
        if n.get("name") == name:
            return n
    raise SystemExit(f"Node not found: {name}")


def ensure_field(fields_list, field_name, field_value):
    for f in fields_list:
        if f.get("fieldName") == field_name:
            f["fieldValue"] = field_value
            return False
    fields_list.append({"fieldName": field_name, "fieldValue": field_value})
    return True


def mutate(wf):
    changed = []
    code_node = find_node(wf["nodes"], "Calculate Lead Score")
    if code_node["parameters"].get("jsCode") != NEW_JSCODE:
        code_node["parameters"]["jsCode"] = NEW_JSCODE
        changed.append("Calculate Lead Score jsCode")

    create_node = find_node(wf["nodes"], "Create Lead in NocoDB")
    fields = create_node["parameters"]["fieldsUi"]["fieldValues"]
    if ensure_field(fields, "external_event_id", "={{ $json.external_event_id }}"):
        changed.append("Create Lead fieldsUi += external_event_id")

    # onError so the error branch runs instead of failing silently.
    if create_node.get("onError") != "continueErrorOutput":
        create_node["onError"] = "continueErrorOutput"
        # Remove deprecated continueOnFail if present
        create_node.pop("continueOnFail", None)
        changed.append("Create Lead onError=continueErrorOutput")

    # Add error alert node if missing
    if not any(n.get("name") == "Send Lead Error Alert" for n in wf["nodes"]):
        wf["nodes"].append(json.loads(json.dumps(ERROR_ALERT_NODE)))
        changed.append("+ Send Lead Error Alert node")

    # Wire Create Lead error output -> Send Lead Error Alert.
    # n8n connection schema: connections["Create Lead in NocoDB"]["main"] is a
    # list-of-list. main[0] = success branch, main[1] = error branch (when
    # onError=continueErrorOutput).
    conns = wf["connections"].setdefault("Create Lead in NocoDB", {}).setdefault("main", [])
    while len(conns) < 2:
        conns.append([])
    error_targets = [c.get("node") for c in conns[1]]
    if "Send Lead Error Alert" not in error_targets:
        conns[1].append({"node": "Send Lead Error Alert", "type": "main", "index": 0})
        changed.append("connection: Create Lead [error] -> Send Lead Error Alert")

    # Workflow-level Code-node guard was tried (commit 6bdc711) but n8n Cloud
    # Code v2 sandbox blocks `this.getCredentials` for nocoDbApiToken — the
    # node throws at runtime. Idempotency is enforced at the DB layer instead
    # (Postgres partial unique index — see docs/LEAD-IDEMPOTENCY-MIGRATION.md
    # SQL fallback). Duplicates surface as Create Lead 422 -> existing
    # onError=continueErrorOutput -> Send Lead Error Alert.
    #
    # If a previous run inserted the Check Idempotency node, remove it and
    # restore direct Calculate Lead Score -> Create Lead in NocoDB wiring.
    if any(n.get("name") == "Check Idempotency" for n in wf["nodes"]):
        wf["nodes"] = [n for n in wf["nodes"] if n.get("name") != "Check Idempotency"]
        wf["connections"].pop("Check Idempotency", None)
        changed.append("- Check Idempotency Code node (removed; DB-level guard)")

    calc_conns = wf["connections"].setdefault("Calculate Lead Score", {}).setdefault("main", [[]])
    while len(calc_conns) < 1:
        calc_conns.append([])
    calc_targets = [c.get("node") for c in calc_conns[0]]
    if "Create Lead in NocoDB" not in calc_targets:
        # Strip any stale Check Idempotency reference.
        calc_conns[0] = [c for c in calc_conns[0] if c.get("node") != "Check Idempotency"]
        calc_conns[0].append({"node": "Create Lead in NocoDB", "type": "main", "index": 0})
        changed.append("connection: Calculate Lead Score -> Create Lead in NocoDB (restored)")
    elif "Check Idempotency" in calc_targets:
        calc_conns[0] = [c for c in calc_conns[0] if c.get("node") != "Check Idempotency"]
        changed.append("connection: stripped stale Check Idempotency edge")

    return changed


def main():
    wf = json.loads(WF_PATH.read_text())
    changed = mutate(wf)
    if not changed:
        print("No changes — workflow already up to date.")
        return
    WF_PATH.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
    print(f"Mutated {WF_PATH.relative_to(WF_PATH.parent.parent.parent)}:")
    for c in changed:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
