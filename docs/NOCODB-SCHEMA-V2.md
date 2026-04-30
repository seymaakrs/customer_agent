# NocoDB Schema V2 — CRM Source of Truth

**Status:** Draft (2026-04-30)
**Owner:** customer_agent (mimari) · mind-agent (yazıcı) · n8n (yazıcı)
**Sürüm:** v2.0
**Dil notu:** Alan adları **Türkçe** — n8n workflow'ları ve mind-agent `nocodb_tools.py` zaten Türkçe alan adlarıyla yazıyor (gerçek sözleşme bu).

NocoDB, satış / CRM verisi için **tek source of truth**'tur. Bu doküman, hem n8n workflow'larının hem de mind-agent `nocodb_client` modülünün uyması zorunlu olan sözleşmedir. Şema değişikliği yapılırsa **bu dosya + contract test + n8n workflow JSON** birlikte güncellenmelidir.

---

## Tablo 1: `leads`

Satış pipeline'ının ana tablosu.

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `Id` | AutoNumber (PK) | ✅ | ✅ | NocoDB tarafından üretilir |
| `external_id` | Text | ✅ | ✅ | Kaynak sistemdeki kayıt ID'si (idempotency anahtarı) |
| `leadgen_id` | Text | ❌ | ✅ | Meta Lead Ads — `leadgen_id` payload alanı, retry koruması |
| `kaynak` | Text (enum) | ✅ | ❌ | `Meta`, `LinkedIn`, `Clay`, `IG DM`, `Referans` |
| `source_workflow_id` | Text | ✅ | ❌ | n8n workflow ID — hangi workflow yazdı (audit) |
| `isim` | Text | ✅ | ❌ | Lead adı |
| `sirket` | Text | ❌ | ❌ | Şirket adı |
| `email` | Email | ❌ | ❌ | İletişim e-posta |
| `telefon` | PhoneNumber | ❌ | ❌ | E.164 formatında |
| `sektor` | Text | ❌ | ❌ | Sektör |
| `skor` | Number (0-100) | ❌ | ❌ | Lead score |
| `asama` | Text (enum) | ✅ | ❌ | `Yeni`, `Soguk`, `Ilik`, `Sicak`, `Teklif`, `Kazanildi`, `Kayip` (default: `Yeni`) |
| `not` | LongText | ❌ | ❌ | Serbest not |
| `son_iletisim` | DateTime | ❌ | ❌ | Son temas zamanı |
| `takip_sayisi` | Number | ✅ | ❌ | Default: 0 |
| `seyma_bildirildi` | Checkbox | ✅ | ❌ | Default: false |
| `CreatedAt` | DateTime | ✅ | ❌ | NocoDB system kolonu (otomatik) |
| `UpdatedAt` | DateTime | ✅ | ❌ | NocoDB system kolonu (otomatik) |

**Constraints:**
- `UNIQUE(external_id)` — temel idempotency
- `UNIQUE(leadgen_id) WHERE leadgen_id IS NOT NULL` — Meta retry koruması
- `INDEX(kaynak, CreatedAt)` — raporlama için
- `INDEX(asama)` — pipeline view için

**Upsert kuralı:** Yazıcılar (n8n + mind-agent) **INSERT yerine upsert** yapmalı. `create_lead` yerine `upsert_lead`:
1. `GET /records?where=(external_id,eq,{X})` — lookup
2. Varsa: `PATCH` ile güncelle
3. Yoksa: `POST` ile insert

> ⚠️ Mevcut `mind-agent/src/tools/sales/nocodb_tools.py:create_lead` upsert yapmıyor. Aktivasyon öncesi `upsert_lead` ile değiştirilmeli (P0). Ek not: NocoDB'deki UNIQUE constraint'i, kod unutsa bile son savunma hattıdır.

---

## Tablo 2: `lead_messages`

Bir lead ile yapılan tüm yazışmalar.

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `Id` | AutoNumber (PK) | ✅ | ✅ | |
| `lead_id` | Link → leads | ✅ | ❌ | NocoDB Link to `leads` |
| `external_message_id` | Text | ❌ | ✅ | Kaynak platform mesaj ID'si (idempotency) |
| `yon` | Text (enum) | ✅ | ❌ | `gelen`, `giden` |
| `kanal` | Text (enum) | ✅ | ❌ | `instagram_dm`, `whatsapp`, `email`, `sms`, `manual` |
| `icerik` | LongText | ✅ | ❌ | Mesaj içeriği |
| `source_workflow_id` | Text | ✅ | ❌ | Yazan workflow (`takip_agent`, `itiraz_agent` vb.) |
| `meta` | JSON | ❌ | ❌ | Platform-spesifik metadata |
| `CreatedAt` | DateTime | ✅ | ❌ | |

**Constraints:**
- `UNIQUE(external_message_id) WHERE external_message_id IS NOT NULL`
- `INDEX(lead_id, CreatedAt DESC)` — lead timeline view

---

## Tablo 3: `seyma_notifications`

mind-id `/satis` sekmesinin bildirim kuyruğu.

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `Id` | AutoNumber (PK) | ✅ | ✅ | |
| `lead_id` | Link → leads | ❌ | ❌ | İlgili lead (varsa) |
| `tur` | Text (enum) | ✅ | ❌ | `hot_lead`, `objection_detected`, `followup_due`, `upsell_opportunity` |
| `baslik` | Text | ✅ | ❌ | Kısa başlık |
| `icerik` | LongText | ❌ | ❌ | Detay |
| `source_workflow_id` | Text | ✅ | ❌ | Üreten n8n workflow |
| `okundu` | Checkbox | ✅ | ❌ | Default: false |
| `oncelik` | Text (enum) | ✅ | ❌ | `dusuk`, `orta`, `yuksek` |
| `CreatedAt` | DateTime | ✅ | ❌ | |
| `okundu_at` | DateTime | ❌ | ❌ | UI'da okunduğunda |

---

## n8n Workflow → Tablo Yazma Matrisi

| Workflow ID | Workflow Adı | leads | lead_messages | seyma_notifications |
|---|---|---|---|---|
| `xblguxS49CJ4r4OF` | Meta Lead Ads Agent | upsert | — | hot_lead (skor≥80) |
| `l31p16NRZeyk4eEm` | Lead Toplama Agent | upsert | — | hot_lead |
| `nWNMQYHJzsMvMUGP` | Takip Agent | — | insert (giden) | followup_due |
| `9nTdKNPLCjo8DKfE` | İtiraz Agent | — | insert (gelen) | objection_detected |
| `kVXXr4e6O5F3lGiD` | Upsell Agent | update (asama) | insert (giden) | upsell_opportunity |

---

## Migration (NocoDB UI)

`scripts/nocodb_migration_v2.md` adım-adım kılavuz içerir. Özet:
1. NocoDB → Sales CRM base
2. Üç tabloyu oluştur (FK sırası: `leads` → `lead_messages` → `seyma_notifications`)
3. Her unique kolon için Field Properties → Unique
4. Link kolonlarını ayarla (`lead_id` → `leads`)
5. `pytest tests/test_nocodb_schema_contract.py` yeşil olmalı
6. n8n her workflow'da "Save to NocoDB" node'unu görsel doğrula

---

## Şema Değişikliği Süreci

1. Bu dosyayı PR'da güncelle
2. `tests/test_nocodb_schema_contract.py` beklenen kolon listesini güncelle
3. NocoDB UI'da migration uygula
4. `n8n/workflows/*.json` dosyalarını güncelle (export edip commit et)
5. PR review'da: NocoDB ekran görüntüsü + contract test geçtiğinin kanıtı zorunlu

**Asla yapma:** NocoDB UI'da kolon adını değiştirip kodu/testi güncellememek.
