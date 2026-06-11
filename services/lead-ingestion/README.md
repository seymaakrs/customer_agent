# Lead Ingestion API

Tüm lead kaynaklarının (Site, Meta Ads, WhatsApp, IG DM, LinkedIn, Clay, Manuel)
tek noktadan girdiği servis. Akış:

```
POST /leads/ingest (X-Ingest-Secret)
  → normalize (Türkçe şema, E.164 telefon, sektör enum)
  → dedup (PG UNIQUE external_id / leadgen_id, upsert)
  → lead skoru (0-100) + segment (Sicak/Ilik/Soguk/Nurture)
  → asama + pipeline aşaması + takip tarihi
  → AI satış notu (OpenAI; yoksa şablon)
  → PostgreSQL upsert
  → Sicak/Ilik + yeni lead ise Gmail API → hello@slowdaysai.com
```

Detaylı plan: `docs/PLAN-LEAD-INGESTION-2026-06-11.md` (repo kökünde).

## Ortam değişkenleri

Bkz. `.env.example`. Zorunlu: `INGEST_SHARED_SECRET`, `DATABASE_URL`.
Opsiyonel: `OPENAI_API_KEY`/`OPENAI_MODEL` (AI not), `GMAIL_SA_JSON` **veya**
`GMAIL_REFRESH_TOKEN`+`GMAIL_CLIENT_ID`+`GMAIL_CLIENT_SECRET` (bildirim),
`MAIL_FROM`/`MAIL_TO`.

AI veya mail tarafı hata verirse lead kaydı YİNE de yapılır (fail-open bildirim).

## Lokal çalıştırma

```bash
cd services/lead-ingestion
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
psql "$DATABASE_URL" -f db/schema.sql
cp .env.example .env   # değerleri doldur
uvicorn app.main:app --reload --port 8080
```

Test isteği:

```bash
curl -X POST localhost:8080/leads/ingest \
  -H "Content-Type: application/json" \
  -H "X-Ingest-Secret: $INGEST_SHARED_SECRET" \
  -d '{"source":"Site","external_id":"site-123","ad_soyad":"Test Kisi","sektor":"Otelcilik","konum":"Bodrum","butce":"15000"}'
```

## Testler

```bash
pip install pytest
PYTHONPATH=. pytest tests/
```

## Cloud Run deploy

```bash
gcloud run deploy lead-ingestion \
  --source services/lead-ingestion \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_MODEL=gpt-4o-mini,MAIL_FROM=hello@slowdaysai.com,MAIL_TO=hello@slowdaysai.com \
  --set-secrets INGEST_SHARED_SECRET=ingest-shared-secret:latest,DATABASE_URL=lead-db-url:latest,OPENAI_API_KEY=openai-api-key:latest,GMAIL_SA_JSON=gmail-sa-json:latest
```

Secret'lar Secret Manager'da tutulur, asla repoya yazılmaz.
