# RUNBOOK — Faz 0 + Faz 1 (Lead Ingestion altyapısı)

> Plan: `docs/PLAN-LEAD-INGESTION-2026-06-11.md`.
> **Karar güncellemesi (2026-06-11):** Ana veri motoru **Neon PostgreSQL**
> (yönetilen, SSL'li, internetten erişilir — agent/n8n/NocoDB uyumu için).
> Şema %100 standart PostgreSQL: ileride AWS RDS'e taşınabilir. pgvector
> Neon'da hazır (AI memory/semantic search ihtiyacı doğunca açılır).
> VM artık veri katmanı DEĞİL; sadece NocoDB panelini barındırır.

## Faz 0 — Yedek + SSL'li NocoDB paneli

### 0.1 Mevcut NocoDB verisini yedekle (ROLLBACK kuralı — ZORUNLU İLK ADIM)

VM'de (SSH):

```bash
docker ps
docker inspect <nocodb_container> | grep -i -A2 volume

# SQLite ise:
docker run --rm --volumes-from <nocodb_container> -v $(pwd):/backup alpine \
  tar czf /backup/nocodb-data-$(date +%F).tar.gz /usr/app/data

# PG ise:
docker exec <pg_container> pg_dump -U <user> <db> > nocodb-dump-$(date +%F).sql
```

Yedeği VM dışına da kopyala (`gcloud storage cp` veya `scp`).

### 0.2 DNS

`db.mindidai.com.tr` → VM IP A kaydı **zaten açık** (doğrulandı: 34.26.138.196'ya çözülüyor).

### 0.3 Traefik'li NocoDB kur (mindid-nocodb şablonu)

```bash
git clone https://github.com/<org>/mindid-nocodb
cd mindid-nocodb/docker-compose/3_traefik
# .env: NC_DOMAIN=db.mindidai.com.tr + güçlü PG şifresi (NocoDB'nin KENDİ meta DB'si için)
docker compose up -d
```

**Eski `http://34.26.138.196` instance'ı KAPATMA** — paralel dursun (rollback yolu).
Doğrulama: `https://db.mindidai.com.tr` açılıyor, sertifika geçerli.

## Faz 1 — Neon PostgreSQL + şema + NocoDB penceresi

### 1.1 Neon projesi aç (Şeyma — 5 dk)

1. https://console.neon.tech → **New Project** — ad: `mindid-leads`, bölge: AWS eu-central-1 (Frankfurt)
2. Database adı: `leads`
3. **Connection string**'i kopyala (`postgresql://...neon.tech/leads?sslmode=require`)
4. Bu string = `DATABASE_URL`. Repoya YAZMA; Cloud Run/Secret Manager'a girilecek.

### 1.2 Şemayı uygula

Neon internetten erişilir olduğu için herhangi bir makineden (Claude session'ı dahil):

```bash
psql "$DATABASE_URL" -f services/lead-ingestion/db/schema.sql
```

Doğrulama:

```sql
\d leads          -- UNIQUE (external_id) görünmeli
\di               -- leads_leadgen_id_key (partial unique) görünmeli
```

### 1.3 NocoDB'yi Neon üstüne "pencere" olarak bağla

1. `https://db.mindidai.com.tr` → giriş
2. **Create Base → Connect External Data → PostgreSQL**
3. Host: `<proje>.neon.tech`, DB: `leads`, SSL: **require**
4. `leads` ve `etkilesimler` tabloları arayüzde görünür — NocoDB verinin
   sahibi değil, sadece görüntüleme/düzenleme penceresi.

### 1.4 Lead Ingestion API'yi deploy et

`services/lead-ingestion/README.md` içindeki `gcloud run deploy` komutu;
`DATABASE_URL` = Neon string. Cloud Run → Neon arası SSL'li, ekstra
firewall/tünel GEREKMEZ (Neon'un avantajı).

Smoke test: `GET /healthz` 200 → README'deki curl ile test lead →
NocoDB penceresinde satır görünür → aynı `external_id` ile ikinci istek
`deduped: true` döner.

## Rollback

| Adım | Geri dönüş |
|---|---|
| Faz 0 NocoDB paneli | Eski `http://34.26.138.196` instance kapatılmadı — eskiye dönülür. Veri 0.1 yedeğinden geri yüklenir. |
| Faz 1 Neon | Proje silinir ya da `DROP TABLE etkilesimler, leads;` (boş başladığı için kayıpsız). NocoDB external source UI'dan kaldırılır. |
| Ingestion API | Cloud Run servisi durdurulur; kaynaklar eski n8n yoluna devam eder (çift yazım sayesinde kayıpsız). |
| Neon → RDS taşıma (ileride) | `pg_dump | pg_restore` — şema standart PG, kod tarafında sadece `DATABASE_URL` değişir. |

## Notlar

- Tüm secret'lar Secret Manager / Neon console — repoya YAZILMAZ.
- n8n workflow'larına bu fazlarda DOKUNULMAZ (Faz 3'te, çift yazımla).
- pgvector: ihtiyaç doğduğunda `schema.sql` sonundaki yorumlu satırlar açılır.
