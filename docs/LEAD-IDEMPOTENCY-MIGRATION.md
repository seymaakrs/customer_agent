# Lead Toplama Idempotency Migration

> Bir kerelik NocoDB schema migrasyonu. **Live workflow yeni JSON'a güncellenmeden
> ÖNCE** uygulanmalı; aksi takdirde Create Lead in NocoDB node, var olmayan
> `external_event_id` kolonuna yazmaya çalışacak ve her satır error branch'e
> düşecek.

## Neden?

`scripts/n8n_apply_lead_toplama_fix.py` artık workflow'a iki katmanlı koruma
ekliyor:

1. **`external_event_id` field** — Zernio `message.id` (veya `platformMessageId`)
   her lead satırına yazılır. Aynı webhook iki kez gelirse aynı değer üretilir.
2. **NocoDB unique index** — bu kolonda unique constraint olduğunda duplicate
   insert NocoDB tarafından reject edilir; `onError=continueErrorOutput`
   sayesinde silent fail yerine `Send Lead Error Alert` Gmail node'una düşer.

Belt-and-suspenders: workflow-side mapper + database-side constraint.

## Migration adımları

### 1. Leadler tablosuna `external_event_id` kolonu ekle

NocoDB UI'da Leadler tablosunu aç → **+ Add Column**:

- **Title:** `external_event_id`
- **Type:** SingleLineText (LongText değil — index için)
- **Required:** false (legacy satırlar boş kalacak)
- **Default value:** boş

Veya API ile (admin JWT gerekir, xc-token yetmez):

```bash
curl -X POST "$NOCODB_BASE_URL/api/v1/db/meta/tables/m5lcgc5ifeqh38h/columns" \
  -H "xc-auth: $NOCODB_JWT" \
  -H "Content-Type: application/json" \
  -d '{"title":"external_event_id","uidt":"SingleLineText","rqd":false}'
```

### 2. Bu kolona unique index ekle

NocoDB UI: kolon başlığı → **⋯** → **Edit Column** → **Unique** toggle on.

NocoDB v0.250+ unique constraint'i UI'dan destekler. Daha eski versiyon
kullanıyorsan: doğrudan Postgres'e `CREATE UNIQUE INDEX leadler_event_id_uq
ON leadler(external_event_id) WHERE external_event_id <> '';` (partial index;
boş string'lere unique uygulanmaz, legacy satırlar etkilenmez).

### 3. Workflow'u güncelle

```bash
export N8N_API_TOKEN='n8n_api_xxxxx'
python3 scripts/n8n_apply_lead_toplama_fix.py --dry-run
python3 scripts/n8n_apply_lead_toplama_fix.py
```

### 4. Doğrula

```bash
export NOCODB_BASE_URL=... NOCODB_API_TOKEN=... NOCODB_EMAIL=... NOCODB_PASSWORD=...
python3 scripts/smoke_zernio_lead.py
```

Smoke artık 4 adım: schema → fire → verify mapping → **replay & verify
count==1**. Replay sonrası 1'den fazla satır görürse exit code 2 ile fail eder
ve doğrudan bu doc'a yönlendirir.

## Rollback

1. Workflow'u önceki versiyona döndür: `gcloud` benzeri bir komut yok; n8n
   public API'sinin version history endpoint'i ile yapılır. Pratikte:
   `/tmp/lead-toplama.backup.<timestamp>.json` PUT et.
2. NocoDB unique constraint kaldır (kolonu silmek yerine sadece unique flag'i
   kapat — legacy satırlar bozulmasın).

## Beklenen davranışlar

| Senaryo | Sonuç |
|---|---|
| Yeni Zernio mesajı | Leadler'a 1 yeni satır + (sıcaksa) Hot Lead Alert |
| Aynı Zernio mesajı 2. kez | Create Lead → 422 unique violation → error branch → Send Lead Error Alert ("Idempotency koruyucu calisti, aksiyon yok") |
| WhatsApp option NocoDB'de eksik | Create Lead → 422 SingleSelect → error branch → Send Lead Error Alert ("Schema option eksik") |
| Legacy non-Zernio webhook (LinkedIn/Manuel) | `raw.external_event_id` opsiyonel — yoksa boş string yazılır, unique partial index bunu yakalamaz, eski davranış korunur |
