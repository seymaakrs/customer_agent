# PLAN — Tek NocoDB + Lead Ingestion API (2026-06-11)

> Durum: **ONAYLANDI** (Şeyma, 2026-06-11). Uygulama henüz başlamadı.
> Karar 1: Lead Ingestion API **mind-agent / Cloud Run** içinde yaşayacak.
> Karar 2: Bildirim maili **Gmail API → hello@slowdaysai.com** (Google Workspace hesabı mevcut).

## Neden bu plan?

Bugünkü durum (audit 2026-06-11):

| Ada | NocoDB | Yazan | Mail |
|---|---|---|---|
| CRM (customer_agent + n8n + mind-agent) | Self-hosted, GCP VM `http://34.26.138.196` (düz HTTP), base `ps9dj2fqrh823av`, Leadler `m5lcgc5ifeqh38h` | 7 n8n workflow + mind-agent | Gmail → seymaakrs@gmail.com |
| Web sitesi (slowdaysai-web) | NocoDB **Cloud** (app.nocodb.com), tablo `mtecjyy2j88c6lq`, İngilizce alanlar | `lib/leads.ts` via `/api/contact` | Resend → hello@slowdaysai.com |
| mindid-nocodb repo | NocoDB kaynak kodu (motor) — veri yok | — | — |

Sorunlar: site lead'leri CRM'e düşmüyor; iki mail kanalı/iki format; VM düz HTTP;
idempotency DB seviyesinde garantili değil (NocoDB UI unique flag ≠ gerçek constraint);
skor/dedup mantığı n8n workflow'larına dağılmış.

## Hedef mimari

```
 Website Form ──────────┐
 Meta Lead Form ────────┤   n8n / Zernio webhook'ları
 WhatsApp (Zernio) ─────┤   sadece "postacı"
 Instagram DM (Zernio) ─┘
            │ HTTPS POST + shared secret
            ▼
 LEAD INGESTION API  (mind-agent, Cloud Run, /leads/ingest)
   1. normalize (tek Türkçe şema)
   2. dedup (external_id / leadgen_id)
   3. lead skoru + Sicak/Ilik/Soguk
   4. pipeline aşaması + takip tarihi
   5. AI satış notu (OpenAI Agents SDK)
            ▼
 Neon PostgreSQL (yonetilen)  — gerçek UNIQUE index'ler, SQL, yedeklenebilir
            ▼  (external data source)
 NocoDB → https://db.mindidai.com.tr  — sadece görüntüleme/düzenleme penceresi
            ▼  Sicak/Ilik ise
 Gmail API → hello@slowdaysai.com  (tek mail kanalı, tek format)
```

Kritik kavram: NocoDB verinin sahibi olmaktan çıkar, PostgreSQL üstünde **pencere** olur.

## Fazlar (her biri tek başına bitirilebilir + geri dönülebilir)

### Faz 0 — Yedek + alan adı (yarım gün)
- [ ] VM'deki mevcut NocoDB verisinin tam dump'ı (ROLLBACK kuralı)
- [ ] `db.mindidai.com.tr` DNS → VM IP
- [ ] `mindid-nocodb/docker-compose/3_traefik` ile SSL'li NocoDB (Traefik + PG + Watchtower)
- Çıktı: HTTPS'li NocoDB, veri kaybı riski sıfır

### Faz 1 — PostgreSQL şema (1 gün)
- [ ] **Neon PostgreSQL** projesinde `leads`, `etkilesimler` (karar 2026-06-11: VM değil; standart PG, RDS-taşınabilir, pgvector-hazır)
- [ ] `external_id`, `leadgen_id`, `external_message_id` → **gerçek UNIQUE index**
- [ ] NocoDB'ye external source olarak bağla
- Çıktı: boş ama sağlam veri katmanı

### Faz 2 — Lead Ingestion API (2-3 gün, mind-agent repo'da)
- [ ] mind-agent'a `POST /leads/ingest` (shared-secret header)
- [ ] normalize → dedup → skor (mevcut n8n skor kuralları taşınır) → aşama → takip tarihi → AI satış notu → PG insert
- [ ] Sicak/Ilik → Gmail API ile hello@slowdaysai.com'a tek formatta mail
- Çıktı: tek beyin, tek mail kanalı

### Faz 3 — Kaynak geçişleri (kaynak başına ~1 saat, çift yazımla)
Sıra: ① slowdaysai-web `lib/leads.ts` → ② Zernio webhook → ③ Meta Lead Ads (n8n node sadece API'ye POST) → ④ LinkedIn/Clay.
Her kaynakta 1-2 hafta çift yazım (eski + yeni yol), doğrulanınca eski kapanır.

### Faz 4 — Temizlik
- [ ] Eski NocoDB Leadler/Etkilesimler verisini PG'ye taşı
- [ ] NocoDB Cloud yazımını kapat; Resend'i kapat veya yedek bildirim olarak bırak
- [ ] n8n'deki skor/dedup code node'ları emekli (workflow'lar arşivlenir, silinmez)

## Roller (repo bazında)
- `mindid-nocodb` → sadece deploy şablonu (Faz 0); custom kod eklenmez
- `customer_agent` → dokümantasyon + devir notları (bu dosya)
- mind-agent → Ingestion API kodu (Faz 2) — bu session'ın repo kapsamında DEĞİL, ayrı oturum gerekir
- `slowdaysai-web` → Faz 3-① köprü değişikliği

## Rollback
- Faz 0: eski `http://34.26.138.196` instance kapatılmaz, paralel durur
- Faz 3: çift yazım sayesinde her kaynak tek env değişikliğiyle eski yola döner
- Tüm n8n workflow değişiklikleri öncesi `n8n/backups/<ad>.<tarih>.pre-<degisiklik>.json`
