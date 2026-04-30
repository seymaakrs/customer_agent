# Lansman Checklist — Customer Agent (Sales) Sistemi

> **AMAÇ:** İlk gösterimde sıfır hata. Her madde doğrulanmadan production'a çıkma.
> **Tarih:** 2026-04-30 (Session 6 sonu)
> **Branch:** `claude/fix-api-error-gIkw4` (3 repoda da)
> **PR'lar:** customer_agent#7, mind-agent#6, mind-id#4 (hepsi DRAFT)

---

## 🟢 Kod Kalite Kontrolü (Tamamlandı)

| Kontrol | Sonuç | Detay |
|---|---|---|
| mind-agent test suite | ✅ 341/341 | tüm testler geçti, regression yok |
| Sales test suite | ✅ 196/196 | NocoDB+Zernio+Clay+webhooks+contract |
| Schema contract | ✅ 18/18 | Pydantic ↔ NocoDB doc birebir |
| Ruff lint (sales kodu) | ✅ Clean | 2 unused import düzeltildi |
| TypeScript (sales kodu) | ✅ Clean | adminDb null guard eklendi |
| Public symbol import | ✅ 50+ ok | tüm export'lar erişilebilir |
| Orchestrator OFF/ON | ✅ +5 tool | sales_agents_enabled doğru gate |
| Zernio API URL doğrulama | ✅ Documented | `/v1/inbox/conversations/{id}/messages` |
| Türkçe-aware lowercase | ✅ Test'li | "KAÇIRMA" düzgün yakalanıyor |
| HMAC webhook verify | ✅ 9 test | Zernio + Meta imza kontrolü |

---

## 🚀 Aktivasyon Sırası (Production'a Geçiş)

### 1. NocoDB Schema Migration

**Önce dogrulama:** `customer_agent/docs/NOCODB-SCHEMA-V2.md` Bölüm 2'deki **Mevcut kolonlar** listesinin (name, email, phone, company, sector, location, notes) `leads` tablosunda var olduğunu doğrula. Eksikse önce onları ekle.

**Sonra V2 değişiklikleri:**

- [ ] `leads` tablosuna 15 yeni kolon (Bölüm 2)
- [ ] `lead_messages` tablosuna 6 yeni kolon (Bölüm 3)
- [ ] `campaigns` tablosu oluştur (Bölüm 4)
- [ ] `daily_metrics` tablosu (Bölüm 5)
- [ ] `decisions_log` tablosu (Bölüm 6)
- [ ] `objections_log` tablosu (Bölüm 7)
- [ ] `agent_health` tablosu (Bölüm 8)
- [ ] Linked Records bağla (Bölüm 9)
- [ ] **Tüm yeni table_id'leri NocoDB UI'dan kopyala** (Tablo → ⋮ → "Copy table ID")

### 2. mind-agent Production Env

`mind-agent/.env.sales.example`'i kopyala:

```bash
# Production sunucusunda:
cd /opt/mind-agent
cp .env.sales.example .env.sales
# Sonra .env.sales'i düzenle, gerçek değerleri yaz
# Ana .env'in sonuna ekle:
cat .env.sales >> .env
```

**Doldurulacak kritik değerler:**

- [ ] `SALES_AGENTS_ENABLED=true`
- [ ] `SALES_SEYMA_EMAIL=seymaakrs@gmail.com`
- [ ] `NOCODB_BASE_URL` (https olmalı)
- [ ] `NOCODB_API_TOKEN` (xc-token)
- [ ] 8 NocoDB table id (yukarıda kopyaladığın)
- [ ] `ZERNIO_API_KEY` (Zernio dashboard → Settings → API Keys)
- [ ] `ZERNIO_INBOX_ENABLED=true` (sadece Inbox addon $10/mo aktive ettikten sonra!)
- [ ] `ZERNIO_WEBHOOK_SECRET` (Zernio dashboard → Webhooks → Add → secret göster)
- [ ] `META_VERIFY_TOKEN` (rastgele string, FB'ye de aynısını yazacaksın)
- [ ] `META_WEBHOOK_SECRET` (FB App Settings → Basic → "Show app secret")

### 3. PR Merge Sırası

**KRİTİK:** Sırayı bozma. mind-agent önce, sonra mind-id.

- [ ] `customer_agent#7` merge → docs (sıfır risk)
- [ ] **`mind-agent#6` merge** → backend kod (175 test yeşil, default OFF flag)
- [ ] `mind-id#4` merge → frontend tab (mind-agent merged'i bekleyecek)

### 4. Deploy

- [ ] mind-agent docker image build + push:
  ```bash
  cd mind-agent
  git pull origin main
  docker build -t agents-sdk-api:v1.19.0 .
  docker tag agents-sdk-api:v1.19.0 us-central1-docker.pkg.dev/instagram-post-bot-471518/agents-sdk/agents-sdk-api:v1.19.0
  docker push us-central1-docker.pkg.dev/instagram-post-bot-471518/agents-sdk/agents-sdk-api:v1.19.0
  ```
- [ ] Cloud Run / VM'de yeni image'i deploy et
- [ ] `.env` güncel mi kontrol et
- [ ] Container yeniden başlat
- [ ] Health check: `curl https://<mind-agent>/healthz` → 200 OK
- [ ] Sales endpoint var mı: `curl -X POST https://<mind-agent>/sales/webhook/zernio` → 401 dönmeli (signature olmadan), 404 değil (route bağlı)

### 5. mind-id Deploy

mind-id Netlify'da otomatik deploy oluyor (PR merge sonrası).

- [ ] Netlify deploy yeşil (PR check'leri)
- [ ] Production URL'de Sales tab görünür mü
- [ ] `/api/sales/query` POST → 401 (auth header olmadan), 404 değil

### 6. Zernio Dashboard Webhook Bağla

- [ ] Zernio dashboard → Settings → Webhooks → "Add endpoint"
- [ ] URL: `https://<mind-agent>/sales/webhook/zernio`
- [ ] Secret: `.env`'deki `ZERNIO_WEBHOOK_SECRET` ile **aynı** olmalı
- [ ] Events: `message.received`, `comment.received` seç
- [ ] "Save" → Zernio test webhook gönderir → mind-agent log'unda "Zernio webhook accepted" satırı görmeli

### 7. End-to-End Test

- [ ] mind-id `/satis` tab aç
- [ ] **"Kaç sıcak lead var?"** hızlı butonuna bas
- [ ] **Beklenen yanıt (5-15 sn içinde):**
  - "Şu an 0 sıcak lead var (skor 8+)" (yeni kurulum, lead yok)
  - veya "Şu an X sıcak lead var..."
- [ ] **NocoDB'de hata logu yok** (ayrı sekmede leads tablosuna bak)
- [ ] **Zernio'da test mesajı:** Slowdays IG hesabına test DM at → 30 sn içinde mind-id'de yeni lead görünmeli

---

## 🛡️ Lansman Sırası Hata Yönetimi

### Test Sırası "Hata: ..." görürsen

| Hata | Sebep | Düzeltme |
|---|---|---|
| `NocoDB is not configured` | env eksik | `.env` kontrol, container restart |
| `error_code: AUTH_ERROR` | NOCODB_API_TOKEN yanlış | Token yenile NocoDB UI'dan |
| `error_code: NOT_FOUND` | TABLE_ID yanlış | Doğru tabloya tıklayıp Id kopyala |
| `Zernio inbox addon not enabled` | ZERNIO_INBOX_ENABLED=false veya addon kapalı | Zernio dashboard'da addon aktive, env'i true yap |
| `error_code: INSUFFICIENT_BALANCE` | Zernio addon $10/mo aktif değil | Zernio dashboard → Add-ons → Inbox → Activate |
| `Failed to reach mind-agent` | mind-agent down veya endpoint yanlış | Health check, Firestore `settings/app_settings.agentEndpoint` |
| `Invalid signature` (webhook) | ZERNIO_WEBHOOK_SECRET uyuşmazlık | Zernio dashboard'taki ile env'deki aynı mı |
| `Invalid OAuth 2.0 Access Token` | Firebase ID token expire | Tarayıcı yenile, tekrar giriş |

### Acil Durum: Rollback

**3 dakikalık rollback yolu:**

1. mind-agent: `SALES_AGENTS_ENABLED=false` env'e yaz, container restart → tüm sales rotaları kapanır, eski davranış geri gelir.
2. mind-id: Sales tab görünür kalır ama backend cevap vermez. Kullanıcıya "Sales şu an bakımda" diye gösterir. **Kritik değil.**

**Tam rollback (kod):**

```bash
git revert <commit-of-pr-mind-agent-6>  # main'de tek revert commit
git push origin main
# Cloud Run yeniden deploy
```

Veritabanı migration'ı **additive** olduğu için geri alma gerekmez — eski kod yeni alanları görmez (zaten kullanmıyor).

---

## 📊 Lansman Sonrası Monitoring (İlk 24 Saat)

- [ ] **Saat 0:** İlk test query başarılı
- [ ] **Saat 1:** İlk gerçek IG DM (Şeyma'dan / arkadaştan) → ig_dm_agent çalıştı mı
- [ ] **Saat 4:** Zernio webhook delivery log temiz (Zernio dashboard → Webhooks → Recent Activity)
- [ ] **Saat 12:** mind-agent container memory < 500MB (lekaj yok)
- [ ] **Saat 24:** İlk Türkçe NL query: "Bugün kaç DM geldi?" → query_agent doğru cevap

---

## ✅ Demo Akışı (İlk Sunum)

1. **mind-id açık, login yapılı, Sales tab seçili.**
2. "Kaç sıcak lead var?" → cevap (rakam + yorum)
3. "Bu hafta pipeline?" → cevap
4. "Hangi kanal en iyi?" → cevap
5. **CANLI demo:** Slowdays IG hesabına telefondan test DM at → 30 sn sonra `/satis` sayfasında **"Yeni lead: ..."** satırı belirsin (refresh ile).
6. NocoDB'yi de aç, leads tablosunda yeni satır gözüksün.
7. "Bu lead için Şeyma'ya bildirim gönderildi mi?" → query_agent → seyma_notifications tablosundaki kayıtla teyit.

---

## 📝 Demo Sırası Söylenecekler

> "Slowdays Bodrum'a Instagram'dan gelen her DM, Zernio üzerinden mind-agent'a düşüyor.
> Mind-agent bunu okuyup CBO standartında otomatik yanıtlıyor — hiçbir baskı dili kullanmadan,
> Şeyma'nın markası bozulmuyor.
>
> Sıcak lead'i (skor 8+) **anında Şeyma'ya mail atıyor.**
>
> Şeyma da bu sayfadan **doğal dilde sorgu yapıyor** — 'kaç sıcak lead?', 'hangi kanal en iyi?',
> 'bugün ne kararlar alındı?'. Her şey NocoDB'de loglanıyor, hiçbir veri kaybolmuyor."

---

## 🚨 Demo Öncesi Son Kontrol (T-30 dk)

- [ ] mind-id production URL açık, Sales tab görünüyor
- [ ] Login bilgileri test edildi
- [ ] Test cep telefonundan Slowdays IG'ye 1 DM at, 30 sn içinde `/satis` sayfasında lead göründü mü
- [ ] NocoDB'de o test lead'i `source=ig_dm` ile kaydedilmiş
- [ ] Şeyma'nın gmail'ine test bildirim maili düşmüş (skor 8+ ise)
- [ ] Tarayıcıda console'da kırmızı hata yok

**Bu kontrol listesi geçilirse demo gönül rahatlığıyla yapılabilir.** 🌱
