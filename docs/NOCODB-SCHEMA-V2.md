# NocoDB Schema V2 — CRM Source of Truth

**Status:** Draft (2026-04-30)
**Owner:** customer_agent (mimari) · mind-agent (yazıcı) · n8n (yazıcı)
**Sürüm:** v2.0

NocoDB, satış / CRM verisi için **tek source of truth**'tur. Bu dokümandaki şema, hem n8n workflow'larının hem de mind-agent'ın `nocodb_client` modülünün uyması zorunlu olan sözleşmedir. Şema değişikliği yapılırsa **bu dosya + contract test + n8n workflow JSON** birlikte güncellenmelidir.

---

## Tablo 1: `leads`

Satış pipeline'ının ana tablosu. Tüm kaynaklardan gelen lead'ler buraya yazılır.

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `id` | AutoNumber (PK) | ✅ | ✅ | NocoDB tarafından üretilir |
| `external_id` | Text | ✅ | ✅ | Kaynak sistemdeki kayıt ID'si (idempotency için) |
| `leadgen_id` | Text | ❌ | ✅ | Meta Lead Ads özel — `leadgen_id` payload alanı |
| `source` | Text (enum) | ✅ | ❌ | `meta_lead_ads`, `instagram_dm`, `webhook_generic`, `manual`, `csv_import` |
| `source_workflow_id` | Text | ✅ | ❌ | n8n workflow ID — hangi workflow yazdı (audit) |
| `name` | Text | ✅ | ❌ | Lead adı |
| `company` | Text | ❌ | ❌ | Şirket adı |
| `email` | Email | ❌ | ❌ | İletişim e-posta |
| `phone` | PhoneNumber | ❌ | ❌ | E.164 formatında |
| `lead_score` | Number (0-100) | ❌ | ❌ | Map Fields and Score node tarafından doldurulur |
| `stage` | Text (enum) | ✅ | ❌ | `new`, `contacted`, `qualified`, `proposal`, `won`, `lost` (default: `new`) |
| `temperature` | Text (enum) | ❌ | ❌ | `cold`, `warm`, `hot` (lead_score'dan türetilebilir) |
| `notes` | LongText | ❌ | ❌ | Serbest not |
| `assigned_to` | Text | ❌ | ❌ | Atanan satışçı (örn. "seyma") |
| `created_at` | DateTime | ✅ | ❌ | UTC ISO8601, yazım anında |
| `updated_at` | DateTime | ✅ | ❌ | UTC ISO8601, her UPDATE'te |

**Constraints:**
- `UNIQUE(external_id)` — temel idempotency
- `UNIQUE(leadgen_id) WHERE leadgen_id IS NOT NULL` — Meta retry koruması
- `INDEX(source, created_at)` — raporlama için
- `INDEX(stage)` — pipeline view için

**Upsert kuralı:** Yazıcılar (n8n + mind-agent) **INSERT yerine upsert** yapmalı:
1. `GET /records?where=(external_id,eq,{X})` — lookup
2. Varsa: `PATCH` ile güncelle, `updated_at = now()`
3. Yoksa: `POST` ile insert, `created_at = updated_at = now()`

---

## Tablo 2: `lead_messages`

Bir lead ile yapılan tüm yazışmalar (DM, e-posta, WhatsApp, takip mesajı vb.).

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `id` | AutoNumber (PK) | ✅ | ✅ | |
| `lead_id` | Number (FK→leads.id) | ✅ | ❌ | NocoDB Link to `leads` |
| `external_message_id` | Text | ❌ | ✅ | Kaynak platform mesaj ID'si (idempotency) |
| `direction` | Text (enum) | ✅ | ❌ | `inbound`, `outbound` |
| `channel` | Text (enum) | ✅ | ❌ | `instagram_dm`, `whatsapp`, `email`, `sms`, `manual` |
| `body` | LongText | ✅ | ❌ | Mesaj içeriği |
| `source_workflow_id` | Text | ✅ | ❌ | Yazan workflow (örn. `takip_agent`, `itiraz_agent`) |
| `meta` | JSON | ❌ | ❌ | Platform-spesifik metadata |
| `created_at` | DateTime | ✅ | ❌ | UTC ISO8601 |

**Constraints:**
- `UNIQUE(external_message_id) WHERE external_message_id IS NOT NULL`
- `INDEX(lead_id, created_at DESC)` — lead timeline view

---

## Tablo 3: `seyma_notifications`

mind-id `/satis` sekmesinin bildirim kuyruğu. "Kaç sıcak lead var?" gibi sorulara cevap üreten kayıtlar.

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `id` | AutoNumber (PK) | ✅ | ✅ | |
| `lead_id` | Number (FK→leads.id) | ❌ | ❌ | İlgili lead (varsa) |
| `kind` | Text (enum) | ✅ | ❌ | `hot_lead`, `objection_detected`, `followup_due`, `upsell_opportunity` |
| `title` | Text | ✅ | ❌ | Kısa başlık |
| `body` | LongText | ❌ | ❌ | Detay |
| `source_workflow_id` | Text | ✅ | ❌ | Üreten n8n workflow |
| `is_read` | Checkbox | ✅ | ❌ | Default: false |
| `priority` | Text (enum) | ✅ | ❌ | `low`, `medium`, `high` |
| `created_at` | DateTime | ✅ | ❌ | |
| `read_at` | DateTime | ❌ | ❌ | UI'da okunduğunda |

---

## n8n Workflow → Tablo Yazma Matrisi

| Workflow ID | Workflow Adı | leads | lead_messages | seyma_notifications |
|---|---|---|---|---|
| `xblguxS49CJ4r4OF` | Meta Lead Ads Agent | upsert | — | hot_lead (score≥80 ise) |
| `l31p16NRZeyk4eEm` | Lead Toplama Agent | upsert | — | hot_lead |
| `nWNMQYHJzsMvMUGP` | Takip Agent | — | insert (outbound) | followup_due |
| `9nTdKNPLCjo8DKfE` | İtiraz Agent | — | insert (inbound) | objection_detected |
| `kVXXr4e6O5F3lGiD` | Upsell Agent | update (stage) | insert (outbound) | upsell_opportunity |

---

## Migration Adımları (NocoDB UI)

1. NocoDB → Project → "Sales CRM" base'ini aç.
2. Yukarıdaki üç tabloyu **bu sıraya göre** oluştur (FK bağımlılığı): `leads` → `lead_messages` → `seyma_notifications`.
3. Her unique kolon için NocoDB UI'dan **Field Properties → Unique** işaretle.
4. `lead_messages.lead_id` ve `seyma_notifications.lead_id` için **Link to Another Record → leads** seç.
5. Test: `POST` ile aynı `external_id` ile iki kez yaz — ikincisi 4xx dönmeli.
6. `mind-agent/tests/test_nocodb_schema_contract.py` çalıştır → tüm kolonlar yeşil olmalı.
7. n8n'de her workflow için "Save to NocoDB" node'unu aç → field mapping'in bu dokümanla aynı olduğunu görsel doğrula.

---

## Şema Değişikliği Süreci

1. Bu dosyayı PR'da güncelle.
2. `tests/test_nocodb_schema_contract.py` içindeki beklenen kolon listesini güncelle.
3. NocoDB UI'da migration'ı uygula.
4. Etkilenen n8n workflow JSON'larını export edip `n8n/workflows/*.json` altında güncelle.
5. PR review'da: NocoDB ekran görüntüsü + contract test geçtiğinin kanıtı zorunlu.

**Asla yapma:** NocoDB UI'da kolon adını değiştirip kodu/testi güncellememek. Sessiz bozulma sebebi #1.
