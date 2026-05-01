#!/usr/bin/env bash
# NocoDB Schema V2 — Otomatik migration script
#
# Kullanim:
#   export NOCODB_BASE_URL="http://34.26.138.196"
#   export NOCODB_API_TOKEN="..."         # claude-setup token'i
#   export NOCODB_BASE_ID=""              # bos birak; script listeleyecek
#   bash scripts/nocodb_migrate.sh
#
# Calistiktan sonra ciktidan NOCODB_*_TABLE_ID degerlerini alip
# .env.sales'e yapistir.

set -euo pipefail

: "${NOCODB_BASE_URL:?NOCODB_BASE_URL set edilmedi}"
: "${NOCODB_API_TOKEN:?NOCODB_API_TOKEN set edilmedi}"

API="${NOCODB_BASE_URL%/}"
H_TOK=(-H "xc-token: ${NOCODB_API_TOKEN}")
H_JSON=(-H "Content-Type: application/json")

log() { echo -e "\033[1;34m[migrate]\033[0m $*"; }
ok()  { echo -e "\033[1;32m[ ok  ]\033[0m $*"; }
err() { echo -e "\033[1;31m[fail]\033[0m $*" >&2; }

need() { command -v "$1" >/dev/null || { err "Eksik komut: $1"; exit 1; }; }
need curl; need jq

# ----------------------------------------------------------------------
# 1) Base kesfi
# ----------------------------------------------------------------------
log "Bases listeleniyor..."
BASES_JSON="$(curl -fsS "${H_TOK[@]}" "$API/api/v2/meta/bases" || true)"
if ! echo "$BASES_JSON" | jq . >/dev/null 2>&1; then
  log "v2/meta/bases bos veya yok, v1 deneniyor..."
  BASES_JSON="$(curl -fsS "${H_TOK[@]}" "$API/api/v1/db/meta/projects")"
fi
echo "$BASES_JSON" | jq '.list[] | {id, title}' || echo "$BASES_JSON"

if [ -z "${NOCODB_BASE_ID:-}" ]; then
  err "NOCODB_BASE_ID set edilmedi. Yukaridaki listeden birinin id'sini export edip tekrar calistir."
  err "ornek: export NOCODB_BASE_ID='p_xxx' && bash $0"
  exit 1
fi
ok "Base secildi: $NOCODB_BASE_ID"

# ----------------------------------------------------------------------
# 2) Mevcut tablolar — backup
# ----------------------------------------------------------------------
log "Mevcut tablolari listele..."
TABLES_JSON="$(curl -fsS "${H_TOK[@]}" "$API/api/v2/meta/bases/$NOCODB_BASE_ID/tables")"
echo "$TABLES_JSON" | jq '.list[] | {id, title}'

mkdir -p .nocodb_backup
TS="$(date +%Y%m%d_%H%M%S)"
for tbl in leads lead_messages seyma_notifications; do
  EXISTING_ID="$(echo "$TABLES_JSON" | jq -r --arg t "$tbl" '.list[] | select(.title==$t) | .id' || true)"
  if [ -n "$EXISTING_ID" ]; then
    log "Eski $tbl tablosu var ($EXISTING_ID) — JSON dump aliniyor..."
    curl -fsS "${H_TOK[@]}" "$API/api/v2/tables/$EXISTING_ID/records?limit=10000" \
      > ".nocodb_backup/${tbl}_${TS}.json"
    ok "Backup: .nocodb_backup/${tbl}_${TS}.json"
  fi
done

# ----------------------------------------------------------------------
# 3) Helper: tablo olustur
# ----------------------------------------------------------------------
create_table() {
  local title="$1"
  local fields_json="$2"
  log "Tablo olusturuluyor: $title"
  local payload
  payload="$(jq -n --arg t "$title" --argjson cols "$fields_json" '{title:$t, columns:$cols}')"
  RES="$(curl -fsS "${H_TOK[@]}" "${H_JSON[@]}" -X POST \
    "$API/api/v2/meta/bases/$NOCODB_BASE_ID/tables" \
    -d "$payload")"
  echo "$RES" | jq '{id, title}'
  echo "$RES" | jq -r '.id'
}

# Kolon JSON sablonlari (uidt = NocoDB Field tipi)
LEADS_COLS='[
  {"title":"external_id","uidt":"SingleLineText"},
  {"title":"leadgen_id","uidt":"SingleLineText"},
  {"title":"kaynak","uidt":"SingleSelect","colOptions":{"options":[{"title":"Meta"},{"title":"LinkedIn"},{"title":"Clay"},{"title":"IG DM"},{"title":"Referans"}]}},
  {"title":"source_workflow_id","uidt":"SingleLineText"},
  {"title":"isim","uidt":"SingleLineText"},
  {"title":"sirket","uidt":"SingleLineText"},
  {"title":"email","uidt":"Email"},
  {"title":"telefon","uidt":"PhoneNumber"},
  {"title":"sektor","uidt":"SingleLineText"},
  {"title":"skor","uidt":"Number"},
  {"title":"asama","uidt":"SingleSelect","colOptions":{"options":[{"title":"Yeni"},{"title":"Soguk"},{"title":"Ilik"},{"title":"Sicak"},{"title":"Teklif"},{"title":"Kazanildi"},{"title":"Kayip"}]}},
  {"title":"not","uidt":"LongText"},
  {"title":"son_iletisim","uidt":"DateTime"},
  {"title":"takip_sayisi","uidt":"Number"},
  {"title":"seyma_bildirildi","uidt":"Checkbox"}
]'

MESSAGES_COLS='[
  {"title":"external_message_id","uidt":"SingleLineText"},
  {"title":"yon","uidt":"SingleSelect","colOptions":{"options":[{"title":"gelen"},{"title":"giden"}]}},
  {"title":"kanal","uidt":"SingleSelect","colOptions":{"options":[{"title":"instagram_dm"},{"title":"whatsapp"},{"title":"email"},{"title":"sms"},{"title":"manual"}]}},
  {"title":"icerik","uidt":"LongText"},
  {"title":"source_workflow_id","uidt":"SingleLineText"},
  {"title":"meta","uidt":"JSON"}
]'

NOTIFS_COLS='[
  {"title":"tur","uidt":"SingleSelect","colOptions":{"options":[{"title":"hot_lead"},{"title":"objection_detected"},{"title":"followup_due"},{"title":"upsell_opportunity"}]}},
  {"title":"baslik","uidt":"SingleLineText"},
  {"title":"icerik","uidt":"LongText"},
  {"title":"source_workflow_id","uidt":"SingleLineText"},
  {"title":"okundu","uidt":"Checkbox"},
  {"title":"oncelik","uidt":"SingleSelect","colOptions":{"options":[{"title":"dusuk"},{"title":"orta"},{"title":"yuksek"}]}},
  {"title":"okundu_at","uidt":"DateTime"}
]'

# ----------------------------------------------------------------------
# 4) Tablolari olustur (varsa atla)
# ----------------------------------------------------------------------
get_table_id() {
  local title="$1"
  curl -fsS "${H_TOK[@]}" "$API/api/v2/meta/bases/$NOCODB_BASE_ID/tables" \
    | jq -r --arg t "$title" '.list[] | select(.title==$t) | .id'
}

LEADS_ID="$(get_table_id leads)"
[ -z "$LEADS_ID" ] && LEADS_ID="$(create_table "leads" "$LEADS_COLS" | tail -1)"
ok "leads: $LEADS_ID"

MSGS_ID="$(get_table_id lead_messages)"
[ -z "$MSGS_ID" ] && MSGS_ID="$(create_table "lead_messages" "$MESSAGES_COLS" | tail -1)"
ok "lead_messages: $MSGS_ID"

NOTIFS_ID="$(get_table_id seyma_notifications)"
[ -z "$NOTIFS_ID" ] && NOTIFS_ID="$(create_table "seyma_notifications" "$NOTIFS_COLS" | tail -1)"
ok "seyma_notifications: $NOTIFS_ID"

# ----------------------------------------------------------------------
# 5) UNIQUE constraint'leri ayarla
# ----------------------------------------------------------------------
set_unique() {
  local tbl_id="$1"
  local col_title="$2"
  log "UNIQUE: $col_title (tbl $tbl_id)"
  COL_ID="$(curl -fsS "${H_TOK[@]}" "$API/api/v2/meta/tables/$tbl_id" \
    | jq -r --arg t "$col_title" '.columns[] | select(.title==$t) | .id')"
  if [ -z "$COL_ID" ] || [ "$COL_ID" = "null" ]; then
    err "$col_title bulunamadi"; return 1
  fi
  curl -fsS "${H_TOK[@]}" "${H_JSON[@]}" -X PATCH \
    "$API/api/v2/meta/columns/$COL_ID" \
    -d '{"unique": true}' >/dev/null
  ok "UNIQUE set: $col_title"
}

set_unique "$LEADS_ID" "external_id" || true
set_unique "$LEADS_ID" "leadgen_id" || true
set_unique "$MSGS_ID"  "external_message_id" || true

# ----------------------------------------------------------------------
# 6) Idempotency canli test
# ----------------------------------------------------------------------
log "Idempotency canli test..."
TEST_BODY='{"external_id":"test_dup_001","kaynak":"Meta","source_workflow_id":"manual_test","isim":"DUPTEST","asama":"Yeni","skor":50,"takip_sayisi":0,"seyma_bildirildi":false}'

R1="$(curl -fsS -o /dev/null -w "%{http_code}" "${H_TOK[@]}" "${H_JSON[@]}" -X POST \
  "$API/api/v2/tables/$LEADS_ID/records" -d "$TEST_BODY" || true)"
log "Ilk POST: $R1"

R2="$(curl -fsS -o /dev/null -w "%{http_code}" "${H_TOK[@]}" "${H_JSON[@]}" -X POST \
  "$API/api/v2/tables/$LEADS_ID/records" -d "$TEST_BODY" || true)"
log "Tekrar POST: $R2 (4xx olmali, UNIQUE engellemeli)"

# Test kaydini sil
TEST_ID="$(curl -fsS "${H_TOK[@]}" \
  "$API/api/v2/tables/$LEADS_ID/records?where=(external_id,eq,test_dup_001)&limit=1" \
  | jq -r '.list[0].Id // empty')"
if [ -n "$TEST_ID" ]; then
  curl -fsS "${H_TOK[@]}" "${H_JSON[@]}" -X DELETE \
    "$API/api/v2/tables/$LEADS_ID/records" \
    -d "[{\"Id\": $TEST_ID}]" >/dev/null
  ok "Test kaydi silindi (Id=$TEST_ID)"
fi

if [ "$R1" = "200" ] && [[ "$R2" =~ ^4 ]]; then
  ok "IDEMPOTENCY GREEN ✓"
else
  err "IDEMPOTENCY KIRMIZI — R1=$R1 R2=$R2 (R2'nin 4xx olmasi beklenirdi)"
  err "leads tablosunda external_id UNIQUE mi? Ekran goruntusu at, beraber bakalim."
fi

# ----------------------------------------------------------------------
# 7) Cikti — .env.sales'e yapistirilacak
# ----------------------------------------------------------------------
echo ""
echo "==============================================================="
echo "  .env.sales'e yapistir:"
echo "==============================================================="
echo "NOCODB_BASE_URL=$API"
echo "NOCODB_LEADS_TABLE_ID=$LEADS_ID"
echo "NOCODB_MESSAGES_TABLE_ID=$MSGS_ID"
echo "NOCODB_NOTIFICATIONS_TABLE_ID=$NOTIFS_ID"
echo "==============================================================="
echo ""
ok "Migration tamam. Sonraki adim: tokenlar (mind-agent + read-only)."
