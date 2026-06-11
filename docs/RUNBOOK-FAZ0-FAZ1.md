# RUNBOOK — Faz 0 + Faz 1 (Lead Ingestion altyapısı)

> Plan: `docs/PLAN-LEAD-INGESTION-2026-06-11.md`. Bu runbook VM üzerinde
> yapılacak adımları sırasıyla anlatır. Her adımın rollback'i en altta.

## Faz 0 — Yedek + SSL'li NocoDB

### 0.1 Mevcut NocoDB verisini yedekle (ROLLBACK kuralı — ZORUNLU İLK ADIM)

VM'de (SSH):

```bash
# NocoDB hangi storage'ı kullanıyor bak (sqlite mi pg mi)
docker ps
docker inspect <nocodb_container> | grep -i -A2 volume

# SQLite ise: volume'u tarihli arşivle
docker run --rm --volumes-from <nocodb_container> -v $(pwd):/backup alpine \
  tar czf /backup/nocodb-data-$(date +%F).tar.gz /usr/app/data

# PG ise:
docker exec <pg_container> pg_dump -U <user> <db> > nocodb-dump-$(date +%F).sql
```

Yedeği VM dışına da kopyala (`gcloud storage cp` veya `scp`).

### 0.2 DNS

`db.mindidai.com.tr` → VM IP A kaydı **zaten açık** (kontrol: `dig db.mindidai.com.tr`).

### 0.3 Traefik'li NocoDB kur (mindid-nocodb şablonu)

```bash
git clone https://github.com/<org>/mindid-nocodb
cd mindid-nocodb/docker-compose/3_traefik
# .env / docker-compose.yml içinde:
#   NC_DOMAIN=db.mindidai.com.tr
#   PG kullanıcı/şifre (güçlü, sadece VM'de)
docker compose up -d
```

Bu şablon Traefik (otomatik Let's Encrypt SSL) + PostgreSQL + Watchtower getirir.
**Eski `http://34.26.138.196` instance'ı KAPATMA** — paralel dursun (rollback yolu).

Doğrulama: `https://db.mindidai.com.tr` açılıyor, sertifika geçerli.

## Faz 1 — PostgreSQL şema + NocoDB penceresi

### 1.1 Lead veritabanı ve kullanıcı

Traefik compose'unun getirdiği PG container'ında:

```bash
docker exec -it <pg_container> psql -U postgres
```

```sql
CREATE DATABASE leads;
CREATE USER lead_user WITH PASSWORD '<guclu-sifre>';
GRANT ALL PRIVILEGES ON DATABASE leads TO lead_user;
\c leads
GRANT ALL ON SCHEMA public TO lead_user;
```

Cloud Run'ın bağlanabilmesi için: PG portunu doğrudan internete AÇMA —
ya GCP firewall'da sadece Cloud Run egress IP'lerine 5432 aç, ya da
Cloud SQL Auth benzeri tünel/VPC connector kullan.

### 1.2 Şemayı uygula

Repo'dan VM'e kopyala ve çalıştır:

```bash
scp services/lead-ingestion/db/schema.sql <vm>:
psql "postgresql://lead_user:<sifre>@localhost:5432/leads" -f schema.sql
```

Doğrulama:

```sql
\d leads          -- UNIQUE (external_id) görünmeli
\di               -- leads_leadgen_id_key (partial unique) görünmeli
```

### 1.3 NocoDB'yi PG üstüne "pencere" olarak bağla

1. `https://db.mindidai.com.tr` → giriş yap
2. Sol alt **Base** oluştur → **Connect External Data** → PostgreSQL
3. Host: PG container adı (aynı compose network'ünde) veya `localhost`,
   DB: `leads`, kullanıcı: `lead_user`
4. `leads` ve `etkilesimler` tabloları görünür — NocoDB artık verinin sahibi
   değil, sadece görüntüleme/düzenleme penceresi.

### 1.4 Lead Ingestion API'yi deploy et

`services/lead-ingestion/README.md` içindeki `gcloud run deploy` komutu.
Smoke test: `GET /healthz` 200, ardından README'deki curl ile test lead;
NocoDB penceresinde satırın göründüğünü ve aynı `external_id` ile ikinci
istekte `deduped: true` döndüğünü doğrula.

## Rollback

| Adım | Geri dönüş |
|---|---|
| Faz 0 NocoDB | Eski `http://34.26.138.196` instance kapatılmadı — DNS/kullanım eskiye döner. Veri 0.1 yedeğinden geri yüklenir. |
| Faz 1 şema | `DROP TABLE etkilesimler; DROP TABLE leads;` (boş başladığı için kayıpsız). NocoDB external source bağlantısı UI'dan kaldırılır. |
| Ingestion API | Cloud Run servisi silinir/trafiği kesilir; kaynaklar eski n8n webhook yoluna devam eder (Faz 3 başlayana dek zaten çift yazım yok). |

## Notlar

- Tüm şifre/secret'lar Secret Manager veya VM `.env` — repoya YAZILMAZ.
- n8n workflow'larına bu fazlarda DOKUNULMAZ (Faz 3'te, çift yazımla).
