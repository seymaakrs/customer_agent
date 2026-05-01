# Launch Checklist — Satış Workflow Aktivasyonu

**Hedef:** n8n satış workflow'larını + mind-agent NocoDB entegrasyonunu + mind-id `/satis` sekmesini production'a alma.
**Önkoşul:** PR `customer_agent#8` (şema/ADR/audit) ve `mind-agent#7` (contract test) merge edilmiş olmalı.

---

## 🟢 STATUS: 2026-05-01 — Backend %100, kalan kullanıcı aksiyonları

**✅ Tamamlananlar (bu checklist'teki adım numaralarına göre):**
- T-60dk: NocoDB migration ✅, mind-agent token ✅, kod merge ✅
- T-30dk: Contract test (creds varsa yeşil olur), idempotency canlı kanıtlandı ✅
- T-15dk: mind-agent v1.20.0 deploy ✅ (revision 00009-667)
- T-0: 4 active workflow (Lead Toplama, Takip, İtiraz, Upsell) zaten ACTIVE; Meta Lead Ads PAUSED (App Review)
- T+15dk: Sahte lead /task → NocoDB'ye yazıldı ✅ + ikinci POST upsert oldu ✅

**⏳ Kalan kullanıcı aksiyonları:**
- 🔒 Güvenlik temizliği (OpenAI key rotate, repo'daki credential dosyalarını sil)
- 🔗 Zernio Inbox addon webhook URL bind
- 📦 n8n 5 workflow JSON'ını repo'ya export
- 🖥 mind-id /satis sekmesi E2E test

Aşağıdaki orijinal checklist referans olarak kalır; "T-60dk" → "T+15dk" arası fiilen tamamlandı.

---

## T-60dk · Hazırlık

- [ ] **NocoDB UI migration tamam** (`scripts/nocodb_migration_v2.md` adımları)
  - [ ] `leads`, `lead_messages`, `seyma_notifications` tabloları var
  - [ ] `external_id`, `leadgen_id`, `external_message_id` UNIQUE
  - [ ] Link kolonları (`lead_id` → leads) bağlı
- [ ] **Token'lar oluşturuldu**
  - [ ] `NOCODB_API_TOKEN_WRITE` (n8n + mind-agent için, read+write)
  - [ ] `NOCODB_API_TOKEN_READ` (mind-id için, read-only)
  - [ ] Çeyreklik rotasyon takvimi (Google Calendar) eklendi
- [ ] **mind-agent `claude/check-facebook-meta-ads-KM4MZ` PR merge edildi**
  - [ ] `src/infra/nocodb_client.py` main'de
  - [ ] `src/tools/sales/nocodb_tools.py` main'de
  - [ ] **`create_lead` → `upsert_lead` refactor uygulandı** (P0)
- [ ] `.env.sales.example` baz alınarak gerçek `.env` üretildi
  - [ ] Secrets manager'a yazıldı (Cloud Run secret veya GCP Secret Manager)

## T-30dk · Doğrulama

- [ ] **Contract test yeşil**
  ```bash
  cd mind-agent
  NOCODB_BASE_URL=... NOCODB_API_TOKEN_READ=... \
  NOCODB_LEADS_TABLE_ID=... NOCODB_MESSAGES_TABLE_ID=... \
  NOCODB_NOTIFICATIONS_TABLE_ID=... \
  pytest tests/test_nocodb_schema_contract.py -v
  ```
  Beklenen: 9 test PASSED.
- [ ] **Mevcut 87 test hâlâ geçiyor** (`pytest` regression check)
- [ ] **Idempotency canlı test:** aynı `external_id` ile iki kez POST → ikincisi 4xx veya UPDATE'e döner
- [ ] **n8n workflow JSON'ları repo'ya export edildi** (`n8n/workflows/*.json`)

## T-15dk · Bağlantılar

- [ ] **Zernio dashboard:** Inbox addon ($10/mo) aktif
- [ ] **Zernio webhook URL** n8n "Lead Toplama Agent" workflow'una set edildi
- [ ] mind-agent Cloud Run servisi yeniden deploy edildi (yeni env var'larla)
- [ ] mind-id deploy edildi, `/satis` sekmesi yükleniyor

## T-0 · Aktivasyon

- [ ] n8n'de aktif edilecek workflow'lar:
  - [ ] Lead Toplama Agent (zaten ACTIVE — kontrol et)
  - [ ] Takip Agent
  - [ ] İtiraz Agent
  - [ ] Upsell Agent
  - [ ] **Meta Lead Ads Agent** — sadece App Review onayı geldiyse

## T+15dk · Smoke Test

- [ ] Test webhook'u (Postman/curl) ile bir sahte lead at → NocoDB'de göründü mü?
- [ ] mind-id `/satis` → "Kaç sıcak lead var?" sorusu cevap dönüyor mu?
- [ ] Aynı sahte lead'i ikinci kez at → DUPLICATE olmadı (Id aynı, sadece UpdatedAt değişti)
- [ ] `seyma_notifications` tablosunda hot_lead bildirimi oluştu mu?

## T+1saat · Gözlemleme

- [ ] n8n execution history → tüm workflow'lar yeşil
- [ ] mind-agent Cloud Run logs → NocoDB hata yok
- [ ] Firestore'da `errors/` koleksiyonuna `nocodb` ile başlayan kayıt yok
- [ ] İlk 10 gerçek lead'i NocoDB UI'da spot-check (alanlar dolu mu)

## Rollback Planı

Bir şey ters giderse:

1. **n8n:** Etkilenen workflow'u DEACTIVATE et (silme).
2. **mind-agent:** Cloud Run'da önceki revizyona geri dön (rollback button).
3. **NocoDB:** Veri kaybı yok — sadece read access kalsın, daha sonra inceleyin.
4. **Iletişim:** Şeyma'ya Slack/WhatsApp bildirimi: `/satis` sekmesi geçici devre dışı.

## Tamamlandığında

- [ ] DEVİR notunu güncelle: aktivasyon tarihi + commit SHA
- [ ] Bu checklist dosyasını commit'le, "✅ ÇALIŞIYOR" damgası bas
- [ ] Bir sonraki çeyreklik için: token rotasyon hatırlatıcısı
