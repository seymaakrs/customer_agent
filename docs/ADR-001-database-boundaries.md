# ADR-001: Veritabanı Sınırları — NocoDB vs Firestore

**Tarih:** 2026-04-30
**Durum:** Kabul edildi
**Karar verenler:** Mimari (customer_agent)

---

## Bağlam

Sistemde iki veritabanı eş zamanlı kullanılıyor:

- **Firestore** (Firebase) — `mind-agent` zaten kullanıyor: medya, Instagram istatistikleri, dry_run logları, video/görsel pipeline çıktıları.
- **NocoDB** — n8n workflow'ları yazıyor; CRM/satış için planlanan source of truth.

n8n ile inşa edilen satış workflow'ları mind-agent'a entegre edilirken, **aynı domain verisinin iki yere yazılması (dual-write) riski** ortaya çıktı. Bu, veri drift'i, çift kayıt, atomicity kaybı ve KVKK ihlal noktası riski yaratır.

## Karar

Veritabanı sınırını **domain'e göre** kesin olarak ayırıyoruz:

### NocoDB — CRM / Sales (single source of truth)
- `leads`
- `lead_messages`
- `seyma_notifications`
- Gelecekte eklenecek: `deals`, `companies`, `tasks`, `pipeline_events`

**Kural:** Lead, müşteri yazışması, satış pipeline aşaması, satışçı bildirimi → **yalnızca NocoDB**. Hiçbir kod yolu bu verileri Firestore'a yazmaz.

### Firestore — Marketing / Media / Analytics (operational)
- `businesses/{bid}/media`
- `instagram_stats/`
- `media/`
- `dry_run_logs/`
- `errors/`
- `threads/` (OpenAI thread state)

**Kural:** Üretilmiş içerik (görsel/video), Instagram metrikleri, hata logları, agent thread state → **yalnızca Firestore**.

### Yasak: Dual-write
Aynı domain entity'sinin (örn. bir lead) hem NocoDB'ye hem Firestore'a yazılması **yasaktır**. Cross-domain ilişki gerekirse:
- NocoDB'deki `leads.id`'ye Firestore'da yalnızca **referans** (string `lead_id`) tutulabilir, kayıt değil.
- Tersi de geçerli: medya asset'inin `id`'si NocoDB'de string referans olarak tutulabilir.

## Sonuçlar

### Olumlu
- Tek silme noktası → KVKK "right to be forgotten" tek query.
- Tek backup hedefi domain başına.
- Şema değişikliği etkisi sınırlı.
- Trace edilebilirlik: bir lead'in tüm yaşamı NocoDB audit'inden okunabilir.

### Olumsuz / Maliyet
- Cross-domain join'ler uygulama katmanında yapılır (NocoDB API + Firestore call).
- Geliştiriciler hangi DB'ye yazacaklarına dikkat etmeli — bu ADR ve `NOCODB-SCHEMA-V2.md` referans olarak kullanılmalı.

## Yaptırım

1. **Code review:** Yeni bir `firestore_client.collection("leads")` veya `nocodb_client.table("media")` çağrısı görülürse PR reddedilir.
2. **Contract test:** `tests/test_nocodb_schema_contract.py` — NocoDB'nin beklenen tablolarını ve kolonlarını doğrular. CI'da koşar.
3. **Lint kuralı (ileride):** Kod tabanında belirli koleksiyon adlarının yanlış client'ta kullanımını tespit eden basit grep kontrolü CI step'i olarak eklenebilir.

## Idempotency Politikası

Her NocoDB write'ı **upsert** olmalı:
- `external_id` (zorunlu, unique) ile lookup
- Meta Lead Ads için ek olarak `leadgen_id` unique
- Mesajlar için `external_message_id` unique (varsa)

Detay: `NOCODB-SCHEMA-V2.md`.

## Token / Yetki Politikası

- `NOCODB_API_TOKEN_WRITE` — n8n workflow'ları ve mind-agent için (read+write).
- `NOCODB_API_TOKEN_READ` — mind-id `/satis` UI ve raporlama için (read-only).
- Token rotasyonu: çeyreklik (her 3 ayda bir).

## İlgili Dokümanlar
- `NOCODB-SCHEMA-V2.md` — Tablo ve kolon tanımları.
- `INTEGRATION-AUDIT-2026-04-30.md` — Mevcut durumda tespit edilen sorunlar ve düzeltme listesi.
