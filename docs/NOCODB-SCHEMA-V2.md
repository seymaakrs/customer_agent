# NocoDB Schema V2 — CRM Source of Truth

**Status:** Live (2026-05-01)
**Owner:** Beyza (n8n workflow'lar) · mind-agent (sales agent)
**Sürüm:** v2.1 — gerçek production şemasıyla hizalandı

NocoDB, satış / CRM verisi için **tek source of truth**'tur. Bu doküman, hem Beyza'nın n8n workflow'larının hem de mind-agent `nocodb_client` modülünün uyduğu **canlı şemadır**. Şema değişikliği yapılırsa **bu dosya + mind-agent kodu + n8n workflow JSON** birlikte güncellenmeli.

> **🔑 Kritik:** Bu canlı şema Beyza tarafından önceden kuruldu. mind-agent buna **adapt oldu** (paralel tablo değil). Tek SoT prensibi.

---

## NocoDB Project / Base

```
Workspace: wgh5kblj (Default Workspace)
Base:      ps9dj2fqrh823av (Getting Started)
URL:       http://34.26.138.196
```

## Tablolar Genel Bakış

| Tablo | ID | Kim Yazıyor | Kim Okuyor | Rol |
|---|---|---|---|---|
| `Leadler` | `m5lcgc5ifeqh38h` | n8n + mind-agent | mind-id | Lead ana tablo |
| `Etkilesimler` | `mx3kbw2vhwimxjf` | n8n + mind-agent | mind-id | Mesajlar + bildirimler |
| `Itirazlar` | `mky0j8v1ldynbfu` | n8n (İtiraz Agent) | mind-id | Lead'in dile getirdiği itirazlar |
| `Takip_Kuyrugu` | `mue67gno1fw8z2k` | n8n (Takip Agent) | mind-id | Zamanlanmış takip mesajları |
| `Kampanyalar` | `m9pryed2gfz7c2o` | n8n (Meta Lead Ads) | mind-id | Reklam metrikleri (CTR/CPC/CPL) |
| `Pipeline` | `mnf5nyu2mx5xtej` | n8n + manuel | mind-id | Sales pipeline aşamaları |
| `Gunluk_Raporlar` | `m21n8qqlklxorwj` | n8n cron | dashboard | Günlük özet |
| `Features` | `miigpyoleyby4ex` | manuel | dashboard | Özellik listesi |

---

## Tablo 1: `Leadler` — Lead Ana Tablo

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `Id` | AutoNumber (PK) | ✅ | ✅ | NocoDB tarafından üretilir |
| `external_id` | SingleLineText | ⭕ | ✅ | Idempotency anahtarı (mind-agent) |
| `leadgen_id` | SingleLineText | ❌ | ✅ | Meta Lead Ads payload alanı |
| `source_workflow_id` | SingleLineText | ⭕ | ❌ | n8n workflow ID — yazan workflow (audit) |
| `ad_soyad` | SingleLineText | ✅ | ❌ | Lead adı soyadı |
| `email` | Email | ❌ | ❌ | İletişim e-posta |
| `telefon` | PhoneNumber | ❌ | ❌ | Telefon |
| `sirket_adi` | SingleLineText | ❌ | ❌ | Şirket |
| `pozisyon` | SingleLineText | ❌ | ❌ | Lead'in şirketteki pozisyonu |
| `sektor` | SingleSelect | ❌ | ❌ | `Otelcilik`, `Yeme-Icme`, `Perakende`, `Turizm`, `E-ticaret`, `Tekne-Yat`, `Emlak`, `Spa-Wellness`, `Doktor-Uzman`, `Koc-Egitmen`, `Kurumsal-Kamu`, `Butik-Moda`, `Kafe`, `Restoran`, `Diger` |
| `konum` | SingleLineText | ❌ | ❌ | Şehir / ilçe |
| `web_sitesi` | URL | ❌ | ❌ | |
| `instagram` | SingleLineText | ❌ | ❌ | @handle |
| `linkedin_url` | URL | ❌ | ❌ | |
| `google_puani` | Number | ❌ | ❌ | Google işletme yıldız puanı |
| `kaynak` | SingleSelect | ✅ | ❌ | `LinkedIn`, `Meta Ads`, `Clay`, `IG DM`, `TikTok DM`, `Referans`, `Manuel` (Beyza'nın canlı option listesi — `Meta` değil `Meta Ads`!) |
| `asama` | SingleSelect | ✅ | ❌ | `Yeni`, `Soguk`, `Ilik`, `Sicak`, `Teklif`, `Sozlesme`, `Kazanildi`, `Kayip`, `Arsiv` |
| `lead_skoru` | Number | ⭕ | ❌ | 0-100 |
| `ihtiyac_notu` | LongText | ❌ | ❌ | Lead ne istiyor |
| `atanan_kisi` | SingleLineText | ❌ | ❌ | Hangi satışçı (örn. "seyma") |
| `notlar` | LongText | ❌ | ❌ | Serbest not |
| `CreatedAt` / `UpdatedAt` | system | ✅ | - | NocoDB otomatik |

**⭕ Zorunlu (mind-agent için):** `external_id`, `source_workflow_id`, `lead_skoru`. n8n workflow'lar bunları opsiyonel kullanıyor (eski kayıtlar boş olabilir, sorun değil).

**Constraints:**
- `UNIQUE(external_id)` — idempotency (mind-agent webhook retry koruması)
- `UNIQUE(leadgen_id) WHERE NOT NULL` — Meta retry koruması
- INDEX yok (NocoDB UI yapmıyor; ihtiyaç olunca SQLite-level eklenecek)

**Upsert kuralı (mind-agent):** `external_id` ile lookup-then-INSERT/PATCH. n8n workflow'lar hâlâ doğrudan INSERT yapıyor (idempotency yok), Beyza'nın ileride upsert paternine geçirmesi öneriliyor.

---

## Tablo 2: `Etkilesimler` — Mesajlar + Bildirimler

| Kolon | Tip | Zorunlu | Unique | Açıklama |
|---|---|---|---|---|
| `Id` | AutoNumber (PK) | ✅ | ✅ | |
| `external_message_id` | SingleLineText | ❌ | ✅ | Platform mesaj ID (örn. WhatsApp `wamid.HBgM...`), idempotency |
| `lead_adi` | SingleLineText | ✅ | ❌ | Leadler.ad_soyad ile string match (FK yok!) |
| `tarih` | DateTime | ✅ | ❌ | UTC ISO8601 |
| `kanal` | SingleSelect | ✅ | ❌ | `LinkedIn`, `Email`, `WhatsApp`, `IG DM`, `TikTok DM`, `Telefon`, `Meta Form`, `Yuz Yuze` (Beyza'nın canlı option listesi) |
| `yon` | SingleSelect | ✅ | ❌ | `Giden`, `Gelen` (BÜYÜK harf!) |
| `tur` | SingleSelect | ❌ | ❌ | `Baglanti Istegi`, `Ilk Mesaj`, `Takip Mesaji`, `Itiraz Karsilama`, `Discovery Call`, `Teklif`, `Yanit` |
| `sonuc` | SingleSelect | ❌ | ❌ | `Yanit Bekleniyor`, `Olumlu Yanit`, `Olumsuz Yanit`, `Itiraz`, `Soru Sordu`, `Gorusme Planlandi` |
| `agent` | SingleSelect | ❌ | ❌ | `LinkedIn Agent`, `Meta Agent`, `Clay Agent`, `DM Bot`, `Takip Agent`, `Itiraz Agent`, `Seyma` |
| `mesaj_icerigi` | LongText | ✅ | ❌ | İçerik |
| `sonuc` | SingleSelect | ❌ | ❌ | `cevapsiz`, `cevap_alindi`, `randevu`, `ilgisiz` |
| `agent` | SingleSelect | ❌ | ❌ | `meta`, `takip`, `itiraz`, `upsell`, `referans`, `manuel` |
| `otomatik_mi` | Checkbox | ✅ | ❌ | true: bot, false: manuel |
| `notlar` | LongText | ❌ | ❌ | |
| `CreatedAt` | system | ✅ | - | |

**⚠️ Zayıflık:** `lead_adi` string match — aynı isimde iki lead varsa karışır. NocoDB'de Link to Records eklenirse FK olur, ileride iyileştirme önerisi.

**Constraints:**
- `UNIQUE(external_message_id) WHERE NOT NULL` — WhatsApp/Meta retry koruması

---

## Tablo 3: `Itirazlar` — İtiraz Tespit + Cevap

(Beyza'nın "İtiraz Agent" workflow'u yazıyor, kolon detayı n8n workflow JSON'undan görünür)

## Tablo 4: `Takip_Kuyrugu` — Zamanlanmış Takip

(Beyza'nın "Takip Agent" workflow'u yazıyor, kolon detayı workflow JSON'unda)

## Tablo 5: `Kampanyalar` — Reklam Metrikleri

| Kolon | Tip | Açıklama |
|---|---|---|
| `Id` | AutoNumber | PK |
| `kampanya_adi` | SingleLineText | |
| `platform` | SingleSelect | |
| `baslangic_tarihi` / `bitis_tarihi` | Date | |
| `gunluk_butce` / `toplam_harcama` | Number | TL |
| `erisim` / `tiklanma` / `ctr` / `cpc` / `lead_sayisi` / `cpl` | Number | metrikler |
| `durum` | SingleSelect | aktif / pasif / tamam |
| `en_iyi_reklam` | SingleLineText | |
| `notlar` | LongText | |

mind-agent şu an Kampanyalar'a yazmıyor; ileride Meta Ads Manager API entegrasyonu için kullanılacak.

## Tablo 6: `Pipeline`, 7: `Gunluk_Raporlar`, 8: `Features`

Bu üç tablo bu doküman kapsamı dışında — Beyza'nın workflow'ları yazıyor, mind-agent şimdilik dokunmuyor.

---

## n8n Workflow → Tablo Yazma Matrisi

| Workflow | Leadler | Etkilesimler | Itirazlar | Takip_Kuyrugu | Kampanyalar |
|---|---|---|---|---|---|
| Meta Lead Ads Agent (xblguxS49CJ4r4OF) | INSERT | — | — | — | UPDATE (metric) |
| Lead Toplama Agent (l31p16NRZeyk4eEm) | INSERT | INSERT (ilk mesaj) | — | — | — |
| Takip Agent (nWNMQYHJzsMvMUGP) | UPDATE (asama) | INSERT (giden) | — | INSERT/UPDATE | — |
| İtiraz Agent (9nTdKNPLCjo8DKfE) | UPDATE | INSERT (gelen) | INSERT | — | — |
| Upsell Agent (kVXXr4e6O5F3lGiD) | UPDATE | INSERT | — | — | — |
| Referans Agent (28hnN6OrH5TF9NX2) | INSERT | INSERT | — | — | — |

mind-agent (sales agent) Leadler + Etkilesimler'e yazıyor, diğer tablolara şimdilik dokunmuyor.

---

## Şema Değişikliği Süreci

1. Bu dosyayı PR'da güncelle
2. mind-agent `tests/test_nocodb_schema_contract.py` beklenen kolon listesini güncelle
3. NocoDB UI'da kolon ekle/düzenle (additive tercih edilir, mevcut workflow'ları bozmamak için)
4. n8n etkilenen workflow'ları aç → mapping'i kontrol et → değiştirip JSON'unu repo'ya export et (`customer_agent/n8n/workflows/`)
5. mind-agent `nocodb_tools.py` field adlarını güncelle, testleri koş, image rebuild + deploy
6. PR review'da: NocoDB UI ekran görüntüsü + contract test geçtiğinin kanıtı

**Asla yapma:** Burak/Beyza'nın production tablo adını değiştirip workflow'ları sessizce kırmak.

---

## Bilinen Sınırlamalar

1. **NocoDB UI `unique` flag DB-level constraint oluşturmuyor** — idempotency yine kod tarafında (`upsert_record` lookup). Bu live test ile kanıtlandı (2026-05-01 idem_007 testi).
2. **Etkilesimler.lead_adi string match** — FK değil. Aynı isim çakışması nadir ama risk var; ileride Link to Records ile değiştirilmeli.
3. **n8n workflow'ları upsert paterni kullanmıyor** — sadece INSERT yapıyor. Webhook retry'lerinde duplicate riski var. Beyza'nın "Save to NocoDB" node'una pre-lookup eklenmesi öneriliyor (ayrı iş).
4. **NOCODB_BASE_URL plain HTTP** (port 80). Cloud Run → VM trafiği GCP iç ağında, şimdilik kabul edilebilir.

---

## İlgili Dokümanlar

- `ADR-001-database-boundaries.md` — NocoDB CRM vs Firestore medya sınırı
- `INTEGRATION-AUDIT-2026-04-30.md` — orijinal audit (eski şema varsayımıyla)
- `DEVIR-2026-05-01.md` — bu session'ın kronolojisi
- `n8n/workflows/` — 7 workflow JSON export (cold backup)
