# Entegrasyon Denetimi — 2026-04-30

**Kapsam:** customer_agent · mind-agent · mind-id repo'larında NocoDB ↔ n8n ↔ Firestore entegrasyonu
**Hazırlayan:** claude/database-integrity-check-6PitF branch'i

---

## Yönetici Özeti

n8n ile inşa edilen satış workflow'larının mind-agent'a entegre edilmesi öncesi yapılan denetimde **3 P0 (kritik), 4 P1 (yüksek), 3 P2 (orta)** bulgu tespit edildi. Aktivasyondan önce P0'ların kapatılması zorunludur.

## Bulgular

### P0-1 · Firebase ↔ NocoDB dualism (mimari belirsizlik)
- **Kanıt:** `mind-agent/src/infra/firebase_client.py:56-60` Firestore client; `mind-agent/src/agents/marketing_agent.py:44-46` Instagram istatistikleri Firestore'da; `customer_agent/SESSION_NOTES.md:77-88` NocoDB client taslak ama main'de yok.
- **Risk:** Lead'lerin nereye yazılacağı kod review'da net değil → ileride Firestore'a kayar, drift başlar.
- **Çözüm:** `ADR-001-database-boundaries.md` ile sınır tanımlandı (bkz. bu PR). CRM verisi yalnızca NocoDB.

### P0-2 · NocoDB client `main`'de yok
- **Kanıt:** `claude/check-facebook-meta-ads-KM4MZ` branch'inde `src/infra/nocodb_client.py` var; `main`'e merge edilmemiş. `src/app/config.py` içinde `NOCODB_*` env değişkeni yok.
- **Risk:** Aktivasyon adımı 3'te merge edilmesi gereken PR. Ondan önce hiçbir mind-agent yolu NocoDB'ye yazamaz.
- **Çözüm:** PR #5 (veya muadili) merge edilmeli. Bu denetim PR'ı, sözleşmeyi (schema + contract test) hazırlıyor — kodun gelmesini bekliyor.

### P0-3 · Idempotency yok
- **Kanıt:** Hiçbir n8n workflow tanımı `leadgen_id` unique check yapmıyor; NocoDB tablolarında unique constraint dokümante edilmemiş.
- **Risk:** Meta webhook retry'lerinde aynı lead 2-3 kez NocoDB'ye düşer.
- **Çözüm:** `NOCODB-SCHEMA-V2.md` her tabloda `external_id` / `leadgen_id` / `external_message_id` unique constraint zorunlu kılıyor. Workflow'lar upsert paternine geçecek.

---

### P1-1 · n8n workflow JSON'ları version control'de değil
- **Kanıt:** Field mapping yalnızca n8n Cloud UI'da. Repo'da `n8n/workflows/` dizini yok.
- **Risk:** NocoDB kolon adı değişirse 5 workflow sessizce bozulur, diff göremezsiniz.
- **Çözüm:** Aktivasyon sonrası workflow JSON'larını export edip `n8n/workflows/` altında commit edin. Her change PR'ında diff görünür olur.

### P1-2 · `source_workflow_id` audit kolonu yok
- **Kanıt:** Hiçbir tabloda yazan workflow'u izleyen kolon yok.
- **Çözüm:** `NOCODB-SCHEMA-V2.md` her tabloya `source_workflow_id` zorunlu kıldı.

### P1-3 · Tek token, scope ayrımı yok
- **Kanıt:** `NOCODB_API_TOKEN` config'de tek değer (taslak branch).
- **Çözüm:** ADR-001 — `NOCODB_API_TOKEN_WRITE` + `NOCODB_API_TOKEN_READ` ayrımı. Çeyreklik rotasyon.

### P1-4 · Şema sözleşmesi (contract) test yok
- **Kanıt:** `tests/` altında 13 dosya, NocoDB ile ilgili 0 test.
- **Çözüm:** `mind-agent/tests/test_nocodb_schema_contract.py` eklendi (bu PR). NocoDB API'sinden meta çekip beklenen kolonlarla karşılaştırır.

---

### P2-1 · DEVİR notunda atıfta bulunulan dosyalar repo'da yok
- **Kanıt:** `DEVIR-2026-04-30.md`, `LAUNCH-CHECKLIST.md`, `.env.sales.example` hiçbir branch'te bulunamadı.
- **Çözüm:** Bu PR ile NOCODB-SCHEMA-V2.md + ADR-001 + audit raporu commit edildi. LAUNCH-CHECKLIST kullanıcı tarafından sağlanırsa eklenecek; yoksa minimal bir hali aşağıda taslak olarak bırakıldı.

### P2-2 · Meta Lead Ads workflow paused, App Review bekliyor
- **Kanıt:** DEVİR notu.
- **Çözüm (kullanıcı aksiyonu):** App Review onayı gelince aktive et; öncesinde NocoDB tablolarının migrate edildiğini ve contract test'in yeşil olduğunu doğrula.

### P2-3 · Inbox addon ($10/mo) ve Zernio webhook URL
- **Çözüm (kullanıcı aksiyonu):** DEVİR notundaki adım. Bu denetimin kapsamı dışında.

---

## Bu PR ile Eklenenler

| Dosya | Repo | Amaç |
|---|---|---|
| `docs/NOCODB-SCHEMA-V2.md` | customer_agent | Şema sözleşmesi |
| `docs/ADR-001-database-boundaries.md` | customer_agent | Mimari karar (Firebase vs NocoDB sınırı) |
| `docs/INTEGRATION-AUDIT-2026-04-30.md` | customer_agent | Bu rapor |
| `docs/ARCHITECTURE-DIAGRAM.md` | customer_agent | Mermaid mimari diyagram |
| `tests/test_nocodb_schema_contract.py` | mind-agent | Şema contract test |

## Sonraki Adımlar (sıralı)

1. **Bu PR'ı merge et** — şema + ADR + test main'de olsun.
2. **NocoDB UI'da migration** — `NOCODB-SCHEMA-V2.md`'deki tabloları oluştur, unique constraint'leri ekle.
3. **mind-agent NocoDB client PR'ını merge et** — `claude/check-facebook-meta-ads-KM4MZ`.
4. **Contract test çalıştır** — gerçek NocoDB'ye karşı; tüm yeşil olana kadar şema veya beklenti listesini düzelt.
5. **n8n workflow'larında upsert paternine geç** — her "Save to NocoDB" node'u öncesi GET-by-external_id.
6. **Workflow JSON'larını export edip repo'ya commit et** (`n8n/workflows/`).
7. **Token'ları ikiye böl** (READ / WRITE) ve rotasyon takvimini başlat.
8. **Aktivasyon:** Meta Lead Ads workflow → ACTIVE.

## Başarı Kriterleri

- [ ] `pytest tests/test_nocodb_schema_contract.py` yeşil
- [ ] Aynı `external_id` ile iki POST → ikincisi reddedilir veya UPDATE'e döner
- [ ] mind-id `/satis` "Kaç sıcak lead var?" sorusu NocoDB'den cevap döner
- [ ] Hiçbir kod yolu `firestore.collection("leads")` çağırmıyor
- [ ] 87 mevcut test hâlâ geçiyor (regression yok)
