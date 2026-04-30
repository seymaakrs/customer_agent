# NocoDB Schema V2 — Customer Agent Sistemi

> **AMAC:** Customer Agent (Sales) sistemi icin NocoDB tablolarini son haline getirmek.
> **KURAL:** Tum degisiklikler **ADDITIVE**. Mevcut veri/kolon silinmez/degistirilmez.
> **UYGULAMA:** Bu doc'u onayladiktan sonra Seyma NocoDB UI'dan elle uygulayacak.
> **VERSIYON:** v2.0 (Session 6, 2026-04-30)

---

## 1. Mevcut Tablolar (Session 2'den)

| Tablo | Amac | Durum |
|---|---|---|
| `leads` | Lead bilgileri | ✅ Aktif |
| `lead_messages` | Lead ile yazismalar | ✅ Aktif |
| `seyma_notifications` | Seyma'ya bildirimler | ✅ Aktif |

---

## 2. `leads` Tablosuna Eklenecek Kolonlar (ADDITIVE)

> **Onemli:** Mevcut kolonlar AYNEN KALIYOR. Sadece sonuna ekleniyor.

### Mevcut kolonlar (Session 2'den) — DEGISMIYOR, dogrulama icin listeleniyor

Yeni alanlari eklemeden once asagidaki kolonlarin tabloda var oldugunu
dogrulayin (yoksa ekleyin — istemci kodu bu isimlere harfiyen baglı):

| Kolon | Tip | Aciklama |
|---|---|---|
| `name` | SingleLineText | Lead adi |
| `email` | Email | Lead e-posta |
| `phone` | PhoneNumber / SingleLineText | Telefon (uluslararası format) |
| `company` | SingleLineText | İşletme adı |
| `sector` | SingleLineText / SingleSelect | Sektör (otel, restoran, cafe, ...) |
| `location` | SingleLineText | Şehir / bölge ("Bodrum", "Muğla") |
| `notes` | LongText | Serbest not |

### Yeni kolonlar (V2'de eklenecek)

| Kolon | Tip | Default | Aciklama |
|---|---|---|---|
| `lead_score` | Number (Int) | `0` | 0-10 arasi skor (Zernio agent spec'i: web yok+IG zayif=10, biri zayif=7, herseyi var=5) |
| `lead_status` | SingleSelect | `cold` | Degerler: `cold`, `warm`, `hot`, `closed`, `lost` |
| `source` | SingleSelect | `manual` | Degerler: `meta`, `clay`, `linkedin`, `ig_dm`, `manual`, `referral` |
| `consent_status` | Checkbox | `false` | KVKK/GDPR onay durumu (CAIDO icin zorunlu) |
| `consent_source` | SingleLineText | (bos) | Onay kaynagi: "form_v1", "linkedin_message", "voice_call", vs. |
| `consent_recorded_at` | DateTime | (bos) | Onayin alindigi an |
| `first_contact_at` | DateTime | (bos) | Ilk temas zamani |
| `first_response_time_min` | Number (Int) | (bos) | Lead'in ilk yaniti kac dakika sonra geldi (RevOps: < 5 dk hedef) |
| `last_action_at` | DateTime | (bos) | Son etkilesim zamani |
| `cac_attributed_try` | Decimal | (bos) | Bu lead'in maliyeti TL (kanal bazli attribution) |
| `expected_revenue_try` | Decimal | (bos) | Beklenen gelir TL (CGO pipeline icin) |
| `zernio_thread_id` | SingleLineText | (bos) | Zernio Inbox thread referansi |
| `zernio_account_id` | SingleLineText | (bos) | Zernio'da hangi sosyal hesap (IG/FB/LinkedIn) |
| `assigned_to` | SingleLineText | (bos) | Hangi agent ilgileniyor (`meta_agent`, `clay_agent`, ...) |
| `tags` | MultiSelect | (bos) | Serbest etiketler: `bodrum`, `otel`, `restoran`, `vip`, ... |

### Skor Kurallari (Zernio Spec'inden)

```
lead_score:
  10 → web sitesi yok + Instagram zayif (en cok ihtiyac)
   8 → web sitesi var + Instagram cok zayif (orta-yuksek)
   7 → sadece biri zayif
   5 → her sey var ama iyilestirilebilir
   3 → her sey iyi durumda (kritik degil)
   0 → tanimlanmamis (default)

lead_status gecisleri:
  cold (yeni lead) → warm (yanit verdi) → hot (skor 8+, Seyma alarm)
                                         → closed (kapanis) | lost (vazgecti)
```

---

## 3. `lead_messages` Tablosuna Eklenecek Kolonlar (ADDITIVE)

### Mevcut kolonlar (Session 2'den) — dogrulama icin

| Kolon | Tip | Aciklama |
|---|---|---|
| `body` | LongText | Mesaj metni (Türkçe) |
| `lead_id` | LinkRecord(`leads`) | Hangi lead ile ilgili |
| `created_at` | DateTime | Mesajin olusturulma zamani |

### Yeni kolonlar (V2'de eklenecek)

| Kolon | Tip | Default | Aciklama |
|---|---|---|---|
| `direction` | SingleSelect | `outbound` | `inbound` (lead'den geldi) / `outbound` (biz yolladik) |
| `channel` | SingleSelect | (bos) | `meta_dm`, `instagram_dm`, `linkedin_dm`, `email`, `whatsapp`, `phone`, `internal_note` |
| `agent_name` | SingleLineText | (bos) | Hangi agent gonderdi (`clay_agent`, `linkedin_agent`, ...) |
| `zernio_message_id` | SingleLineText | (bos) | Zernio mesaj ID (idempotency icin) |
| `is_auto_generated` | Checkbox | `false` | LLM uretti mi yoksa insan yazdi mi |
| `cbo_compliant` | Checkbox | `true` | CBO standardina uygun mu (yasakli ifade kontrolu gecti mi) |

---

## 4. YENI Tablo: `campaigns`

> Meta + LinkedIn + Google + TikTok reklam kampanyalarini takip eder.

| Kolon | Tip | Aciklama |
|---|---|---|
| `id` | AutoNumber | Birincil anahtar |
| `external_campaign_id` | SingleLineText | Zernio Ads veya direkt Meta/LinkedIn ID |
| `platform` | SingleSelect | `meta`, `linkedin`, `google`, `tiktok`, `pinterest`, `x` |
| `name` | SingleLineText | Kampanya adi |
| `objective` | SingleSelect | `lead_generation`, `traffic`, `engagement`, `conversions` |
| `status` | SingleSelect | `active`, `paused`, `archived` |
| `budget_daily_try` | Decimal | Gunluk butce TL |
| `started_at` | DateTime | Baslangic |
| `paused_at` | DateTime | Duraklama (otonom karar logu icin) |
| `pause_reason` | SingleLineText | "CTR<%1", "CPL>50", manual, vs. |
| `total_spend_try` | Decimal | Toplam harcama (anlik metrikten degil, snapshot) |
| `target_audience` | LongText | JSON: hedef kitle parametreleri |
| `created_by_agent` | SingleLineText | Hangi agent kurdu (genelde `meta_agent`) |

---

## 5. YENI Tablo: `daily_metrics`

> Gunluk kanal bazli metrikler. Daily Reporter (23:00) bu tabloyu yazar.

| Kolon | Tip | Aciklama |
|---|---|---|
| `id` | AutoNumber | |
| `date` | Date | Hangi gun |
| `channel` | SingleSelect | `meta`, `clay`, `linkedin`, `ig_dm`, `total` |
| `impressions` | Number | Gosterim |
| `clicks` | Number | Tiklanma |
| `leads_count` | Number | Yeni lead sayisi |
| `hot_leads_count` | Number | Skor 8+ lead sayisi |
| `conversions_count` | Number | Kapanis sayisi |
| `spend_try` | Decimal | Harcama TL |
| `revenue_try` | Decimal | Gelir TL |
| `cac_try` | Decimal | Customer Acquisition Cost (`spend / conversions`) |
| `cpl_try` | Decimal | Cost Per Lead (`spend / leads_count`) |
| `ctr_pct` | Decimal | Click-Through Rate (%) |
| `pipeline_value_try` | Decimal | Acik pipeline degeri |
| `notes` | LongText | Otonom karar notlari, anomali tespitleri |

**Unique constraint:** `(date, channel)` — ayni gun ayni kanal icin tek satir.

---

## 6. YENI Tablo: `decisions_log`

> Otonom kararlar (CTR<%1 → durdur, score 8+ → Seyma'ya bildir, vs.) buraya log'lanir. CAIDO denetim icin kritik.

| Kolon | Tip | Aciklama |
|---|---|---|
| `id` | AutoNumber | |
| `timestamp` | DateTime | Karar zamani |
| `agent_name` | SingleLineText | Karari veren agent |
| `decision_type` | SingleSelect | `pause_campaign`, `notify_seyma`, `escalate_human`, `auto_reply`, `score_lead`, `assign_lead` |
| `target_entity` | SingleLineText | Etkilenen entity ("lead#123", "campaign#456") |
| `reason` | LongText | Neden bu karar verildi (insan okur) |
| `data_snapshot` | LongText | JSON: karari tetikleyen veri |
| `human_required` | Checkbox | Insan onayi gerekiyor mu (CGO/Seyma) |
| `human_acknowledged_at` | DateTime | Insan ne zaman gordu/onayladi |
| `outcome` | SingleSelect | `applied`, `pending_approval`, `reverted`, `failed` |

---

## 7. YENI Tablo: `objections_log`

> Itiraz Agent'in karsilastigi itirazlar + verdigi yanitlar. Ogrenme amacli.

| Kolon | Tip | Aciklama |
|---|---|---|
| `id` | AutoNumber | |
| `lead_id` | LinkRecord(`leads`) | Hangi lead |
| `objection_text` | LongText | Lead'in soyledigi |
| `objection_category` | SingleSelect | `price`, `timing`, `competitor`, `trust`, `feature`, `other` |
| `response_template_used` | SingleLineText | Hangi sablon kullanildi |
| `response_text` | LongText | Verilen yanit |
| `outcome` | SingleSelect | `converted`, `still_objecting`, `lost`, `pending` |
| `created_at` | DateTime | |

---

## 8. YENI Tablo: `agent_health`

> Her agent'in son calisma durumu — mind-id dashboard'da gosterilir.

| Kolon | Tip | Aciklama |
|---|---|---|
| `agent_name` | PrimaryKey/SingleLineText | `meta_agent`, `clay_agent`, vs. |
| `last_run_at` | DateTime | Son calisma |
| `last_success_at` | DateTime | Son basarili calisma |
| `last_error_at` | DateTime | Son hata |
| `last_error_message` | LongText | Son hata mesaji |
| `total_runs_today` | Number | Bugun kac kez calisti |
| `total_leads_processed_today` | Number | Bugun kac lead isledi |
| `status` | SingleSelect | `healthy`, `degraded`, `down`, `paused` |

---

## 9. NocoDB Iliskiler (Linked Records)

```
leads ←→ lead_messages    (1-to-many)
leads ←→ objections_log   (1-to-many)
leads ←→ seyma_notifications  (1-to-many)
campaigns ←→ leads        (1-to-many, source=meta/linkedin)
```

NocoDB'de "LinkToAnotherRecord" tipiyle baglanir.

---

## 10. Uygulama Sirasi (Sen NocoDB UI'da)

> Soldan saga sirayla yap, her adimdan sonra "Save" bas.

1. ✅ `leads` tablosuna 15 yeni kolon ekle (Sectiyon 2)
2. ✅ `lead_messages` tablosuna 6 yeni kolon ekle (Sectiyon 3)
3. ✅ `campaigns` tablosunu olustur (Sectiyon 4)
4. ✅ `daily_metrics` tablosunu olustur (Sectiyon 5)
5. ✅ `decisions_log` tablosunu olustur (Sectiyon 6)
6. ✅ `objections_log` tablosunu olustur (Sectiyon 7)
7. ✅ `agent_health` tablosunu olustur (Sectiyon 8)
8. ✅ Linked Records'lari kur (Sectiyon 9)
9. ✅ Tum yeni table_id'lerini bana ver (env var icin):
   ```
   NOCODB_CAMPAIGNS_TABLE_ID=xxxxx
   NOCODB_DAILY_METRICS_TABLE_ID=xxxxx
   NOCODB_DECISIONS_LOG_TABLE_ID=xxxxx
   NOCODB_OBJECTIONS_LOG_TABLE_ID=xxxxx
   NOCODB_AGENT_HEALTH_TABLE_ID=xxxxx
   ```

---

## 11. Geri Alma (Rollback)

Tum degisiklikler additive oldugu icin **mevcut veriyi etkilemez**. Eger bir yanlis olursa:
- Yeni eklenen kolonlari NocoDB UI'dan **silebilirsin** (mevcut data kaybolmaz)
- Yeni tablolari (campaigns, daily_metrics, vb.) **silebilirsin**
- Hicbir mevcut tablo/veri silinmiyor

---

## 12. Mind-agent Tarafinda Karsilik

Bu schema'ya gore `src/infra/nocodb_client.py` ve `src/tools/sales/nocodb_tools.py` Pydantic modellerini uretecek (Faz 1c). Schema'nin **TEK KAYNAGI bu doc.** Kod buradaki kolon isimlerine harfiyen uyacak.

---

## ONAY

- [ ] Bu schema OK, NocoDB'ye uygulayacagim
- [ ] Belirli kolonlari degistir (asagida yaz)
- [ ] Bekle, tekrar konusalim
