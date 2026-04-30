# NocoDB Migration V2 — Adım Adım UI Kılavuzu

**Hedef:** `docs/NOCODB-SCHEMA-V2.md`'deki üç tabloyu NocoDB instance'ında oluşturmak.
**Süre:** ~20-30 dakika.
**Tehlike:** Mevcut tablolar varsa (eski şema), önce backup al — `Project → ⋯ → Export to JSON`.

---

## Ön kontrol

```bash
# NocoDB erişimi var mı?
curl -H "xc-token: $NOCODB_API_TOKEN_WRITE" \
  "$NOCODB_BASE_URL/api/v2/meta/bases" | jq .
```
JSON liste dönmeli. Hata varsa token / base URL kontrol et.

---

## Adım 1 — Base oluştur (yoksa)

NocoDB UI → `+ New Project` → "Sales CRM" adıyla bir base aç. Mevcutsa atla.

## Adım 2 — `leads` tablosu

`+ New Table` → name: `leads` → `Create`.

Her satır için: **Add Field** → tip seç → `Field name` gir → varsa **Field Properties** açıp Unique işaretle.

| Field name | Type | Unique | Default | Notlar |
|---|---|---|---|---|
| external_id | SingleLineText | ✅ | — | n8n'in idempotency key'i |
| leadgen_id | SingleLineText | ✅ | — | Meta retry koruması |
| kaynak | SingleSelect | ❌ | — | options: Meta, LinkedIn, Clay, IG DM, Referans |
| source_workflow_id | SingleLineText | ❌ | — | Hangi n8n workflow yazdı |
| isim | SingleLineText | ❌ | — | |
| sirket | SingleLineText | ❌ | — | |
| email | Email | ❌ | — | |
| telefon | PhoneNumber | ❌ | — | |
| sektor | SingleLineText | ❌ | — | |
| skor | Number | ❌ | 50 | 0-100 |
| asama | SingleSelect | ❌ | Yeni | options: Yeni, Soguk, Ilik, Sicak, Teklif, Kazanildi, Kayip |
| not | LongText | ❌ | — | |
| son_iletisim | DateTime | ❌ | — | |
| takip_sayisi | Number | ❌ | 0 | |
| seyma_bildirildi | Checkbox | ❌ | false | |

> `Id`, `CreatedAt`, `UpdatedAt` NocoDB tarafından otomatik üretilir, eklemenize gerek yok.

## Adım 3 — `lead_messages` tablosu

| Field name | Type | Unique | Notlar |
|---|---|---|---|
| lead_id | LinkToAnotherRecord → leads (Has Many) | ❌ | mesaj → lead bağlantısı |
| external_message_id | SingleLineText | ✅ | platform mesaj ID |
| yon | SingleSelect | ❌ | options: gelen, giden |
| kanal | SingleSelect | ❌ | options: instagram_dm, whatsapp, email, sms, manual |
| icerik | LongText | ❌ | |
| source_workflow_id | SingleLineText | ❌ | |
| meta | JSON | ❌ | platform metadata |

## Adım 4 — `seyma_notifications` tablosu

| Field name | Type | Unique | Default | Notlar |
|---|---|---|---|---|
| lead_id | LinkToAnotherRecord → leads | ❌ | — | nullable |
| tur | SingleSelect | ❌ | — | options: hot_lead, objection_detected, followup_due, upsell_opportunity |
| baslik | SingleLineText | ❌ | — | |
| icerik | LongText | ❌ | — | |
| source_workflow_id | SingleLineText | ❌ | — | |
| okundu | Checkbox | ❌ | false | |
| oncelik | SingleSelect | ❌ | orta | options: dusuk, orta, yuksek |
| okundu_at | DateTime | ❌ | — | |

---

## Adım 5 — Doğrulama

```bash
# Table ID'lerini al, .env.sales'e yaz
curl -H "xc-token: $NOCODB_API_TOKEN_WRITE" \
  "$NOCODB_BASE_URL/api/v2/meta/bases/{BASE_ID}/tables" | jq '.list[] | {id, title}'
```

Sonra contract test:
```bash
cd mind-agent
pytest tests/test_nocodb_schema_contract.py -v
```

Beklenen: 9 test PASSED. Kırmızı varsa hata mesajı hangi kolonun eksik/fazla olduğunu söyleyecek — geri dön ve düzelt.

## Adım 6 — Idempotency canlı test

```bash
# Aynı external_id ile iki kez POST
curl -X POST -H "xc-token: $NOCODB_API_TOKEN_WRITE" \
  -H "Content-Type: application/json" \
  -d '{"external_id":"test_dup_001","kaynak":"Meta","source_workflow_id":"manual_test","isim":"Test"}' \
  "$NOCODB_BASE_URL/api/v2/tables/$NOCODB_LEADS_TABLE_ID/records"

# İkincisi 4xx dönmeli (UNIQUE ihlali)
curl -X POST ... # aynı body
```

İkincisi 200 dönüyorsa UNIQUE constraint'i unutmuşsunuz — Adım 2'ye dön.

## Adım 7 — Temizlik

Test kayıtlarını sil:
```bash
curl -X DELETE -H "xc-token: $NOCODB_API_TOKEN_WRITE" \
  -H "Content-Type: application/json" \
  -d '[{"Id": <test_id>}]' \
  "$NOCODB_BASE_URL/api/v2/tables/$NOCODB_LEADS_TABLE_ID/records"
```

Migration tamam.
