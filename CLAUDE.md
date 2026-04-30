# Customer Agent - Claude Session Hafizasi

> **HER YENI SESSION BASLANGICINDA OKU.** Bu dosya ve `SESSION_NOTES.md` projenin kalici hafizasidir.

## Proje Ozeti

**Hedef:** 7 gunde 116.000 TL gelir
**Mimari:** 6 agent paralel calisir (LinkedIn, Meta, Clay, IG DM, Takip, Itiraz) → NocoDB CRM → Seyma kapanis yapar
**Detay:** `AGENT-MIMARISI-MASTER.md`

## Detay/Master Dokümanlar

- `AGENT-MIMARISI-MASTER.md` → 6 agent + 8 workflow + NocoDB tablo şablonları (mimari)
- `ZERNIO-AGENT-SPEC.md` → **Şeyma'nın Claude Console'da kurduğu agent spec'i** (rol matrisi, otonom karar kuralları, raporlama formatı, itiraz şablonları). **Tüm yeni agent'lar bu spec'e göre kurulacak.**
- `SESSION_NOTES.md` → Session bazlı kalıcı notlar

## Karar Verilmis Olan Seyler (DEGISMEZ)

| Konu | Karar |
|------|-------|
| CRM | **NocoDB** (Airtable degil, gecis yapildi) |
| Orchestrator | `mind-agent` (OpenAI Agents SDK, Python) — yeni 6 agent oraya entegre edilecek |
| Admin Panel | `mind-id` (Next.js) — agent'lari tetikleyen UI |
| Workflow Engine | n8n (mindidai.app.n8n.cloud) — webhook'lar buradan akar |
| Hedef bolge | Bodrum / Mugla |
| Hedef sektor | Otelcilik, Restoran, Cafe, Perakende, Turizm, E-ticaret |
| Agent yapilanmasi | Yeni alt-modul: `mind-agent/src/agents/sales/` |
| Orkestrasyon modeli | **Hibrit:** Sablon/cron akislar n8n'de, LLM analiz/personalizasyon mind-agent'ta |
| Ilk entegre edilecek agent | **Meta Reklam Agent** (Lead Form trigger zaten hazir) |

## Hazir Olan Altyapi (Session 3 — 2026-04-28 sonrasi GUNCEL)

- [x] NocoDB **AKTIF**, tablolar olusturuldu, n8n yaziyor
- [x] **Cogu agent kuruldu** — n8n workflow'lari NocoDB'ye lead yaziyor (detay session notes'ta)
- [x] **Seyma'ya mail bildirim aktif** — n8n'den mail gidiyor
- [x] **Production sunucu: Google Cloud VM** — n8n burada calisiyor, SSH ile test verisi yolluyoruz
- [x] Facebook Lead Ads form aktif: "Slowdays Dijital Paketler" (Slowdays Bodrum sayfasi)
- [x] **Facebook hesap gecisi:** Selahattin -> Seyma. Tum yetkiler kullanicida (Seyma), kimseden onay gerekmiyor.
- [x] AGENT-MIMARISI-MASTER.md: 6 agent + 8 workflow + NocoDB tablo sablonlari (PR #1 draft'da Airtable->NocoDB guncellemesi bekliyor)

## Hizli Erisim Bilgileri

### n8n
- **URL:** https://mindidai.app.n8n.cloud/  (n8n Cloud)
- **Webhook base:** https://mindidai.app.n8n.cloud/webhook
- **API base:** https://mindidai.app.n8n.cloud/api/v1
- **API auth header:** `X-N8N-API-KEY: <token>`

### n8n API Token Nasil Alinir (kullaniciya rehber)
1. https://mindidai.app.n8n.cloud/ -> giris yap
2. Sol alt: kullanici avatari (initials) -> **Settings**
3. Sol menude **n8n API** sekmesi
4. **Create an API key** butonu
5. Label: ornek "claude-code"
6. Expiration: 7 gun veya 30 gun (gecici icin)
7. **Save** -> Token bir kez gosterilir, HEMEN KOPYALA (formati: `n8n_api_xxxxx...`)
8. Bu token .env'de tutulur, ASLA commit edilmez. Kullanim bitince Settings'ten sil.

### Production sunucu
- Google Cloud VM (detayli adres kullanicida)
- SSH erisimi var (kullanicida)
- VM'de calisanlar: NocoDB (ve muhtemelen mind-agent docker)

### NocoDB
- Tablolar aktif: `leads`, `lead_messages`, `seyma_notifications` (semasi master doc'ta)
- API token + URL kullanicida

## Mevcut Durak Noktasi (Session 6 sonu — 2026-04-30)

**KIRMIZI BOLGE IMPLEMENTASYON TAMAMLANDI + LANSMAN HARDENING.**

3 PR draft'ta, kullanici merge bekliyor:
- `seymaakrs/customer_agent#7` (docs)
- `seymaakrs/mind-agent#6` (kod, 385/385 test)
- `seymaakrs/mind-id#4` (UI, sales tab)

**Bugun tamamlanan ek isler (lansman hardening):**
- Zernio API URL'leri docs.zernio.com'a gore duzeltildi (`/v1/inbox/conversations/{id}/messages`)
- Schema contract test (18) — Pydantic ↔ NocoDB doc birebir hizali
- 22 production edge case test
- adminDb null guard (mind-id)
- Ruff temiz, TS sales kodu temiz
- `.env.sales.example` (17 env)
- `LAUNCH-CHECKLIST.md` (T-30dk demo kontrol listesi)
- `DEVIR-2026-04-30.md` (gun sonu devir cikti)

**Tum doku ve devir bilgileri:** `docs/DEVIR-2026-04-30.md`

**Yeni session basinda oku:**
1. `CLAUDE.md` (bu dosya)
2. `docs/DEVIR-2026-04-30.md` — bugun ne yapildi, ne bekliyor
3. `docs/LAUNCH-CHECKLIST.md` — aktivasyon rehberi (kullanici aktivasyona basliyorsa)

**KORU:** Meta Lead Ads workflow PAUSED, mind-agent main DOKUNULMADI

## Buyuk Hedef Sirasi
1. **Once mimariyi tamamla** — n8n'deki tum agent workflow'lari calisir hale getir (mevcut hedef)
2. **Sonra mind-agent'a tasi** — n8n'deki sistemi mind-agent SDK icine al (gelecek hedef)

## Bilinen Riskler / Acik Sorular

1. **Facebook hesap gecisi:** Selahattin -> Seyma'ya gecildi. Yetkiler tamam, kimseden onay alinmasi gerekmiyor. Eski credential durumu kullanici tarafindan halledilecek.
2. **n8n -> mind-agent gecisi:** Henuz baslamadi. Once mimari tamamlanacak, sonra tasinacak.
3. **mind-agent kod degisiklikleri (PR #5 draft):** Henuz kararsiz — kullanici onay gerektigini belirtti, geri donulebilir kalmali.

## Repo Haritasi

```
customer_agent/      Bu repo - sadece dokumantasyon ve mimari
mind-agent/          Python OpenAI Agents SDK orchestrator (kod buraya eklenecek)
mind-id/             Next.js admin paneli (UI ve n8n proxy)
```

## Calisma Stili (KESIN KURALLAR)

1. **Yeni session basinda:** BU DOSYAYI ve `SESSION_NOTES.md`'yi oku.
2. **ONAY ALMADAN KOD DEGISTIRME.** Once plan sun, sor, sonra yap. Mind-agent bozulmamali, hep geri donulebilir olmali.
3. **Onemli karar verildiginde:** BURAYA yaz.
4. **Session sonunda:** `SESSION_NOTES.md`'ye o session'da yapilanlari ekle.
5. **Belirsiz bir sey varsa:** VARSAYIM YAPMA, kullaniciya sor.
6. **Kullaniciya soracagin sey hakkinda:** Sadece projeye ait bilgi sor. Yetki, hesap, sifre vb. icin sorma — kullanicinin tum yetkileri var.
7. Kullanici yeni mezun bir yazilim muhendisi gibi davranir — kavramlari acikla, surece dahil et.

## n8n Workflow Envanteri (Session 3 — 2026-04-28)

> Tam liste API'den cekildi. Ana hatlariyla.

### Sales/CRM Akisinda Olanlar (master mimari ile eslesme)

| Master Agent | n8n Workflow Adi | ID | Aktif | Not |
|---|---|---|---|---|
| LinkedIn Agent | (Yok — `Lead Toplama Agent` generic webhook olabilir) | l31p16NRZeyk4eEm | ✅ | Webhook trigger |
| **Meta Reklam** | **Meta Lead Ads Agent** | xblguxS49CJ4r4OF | ❌ | **Burada tikandik** |
| Clay Agent | Yok | — | — | Henuz kurulmadi |
| IG DM Agent | Yok (instagram_* var ama content uretimi icin) | — | — | Henuz kurulmadi |
| Takip Agent | Takip Agent | nWNMQYHJzsMvMUGP | ✅ | Calisiyor |
| Itiraz Agent | Itiraz Agent | 9nTdKNPLCjo8DKfE | ✅ | Calisiyor |
| Upsell (ekstra) | Upsell Agent | kVXXr4e6O5F3lGiD | ✅ | |
| Referans (ekstra) | Referans Agent | 28hnN6OrH5TF9NX2 | ✅ | |

### Diger Onemliler

| Workflow | ID | Aktif | Rol |
|---|---|---|---|
| Musteri Mail Otomasyonu (Claude Trigger) | faolAyTcoUJIBcal | ✅ | Webhook -> Splitout -> Personalize -> Gmail |
| Facebook Lead Ads Performance Tracker | 47pTxyFQPaQxEWxU | ❌ | CTR/CPC izleme (henuz aktif degil) |
| Gunluk Rapor | z80cGhIcVrKSnIAy | ✅ | |
| Haftalik Rapor | 71xugM3hTqDZiIUx | ✅ | |
| Airtable CRM Setup | zI7CyXdyHmxX9mF0 | ❌ | Eski Airtable kalintisi, silinebilir |
| NocoDB Test | rNpzfRmdNLnOwXBR | ❌ | Test, silinebilir |

### Meta Lead Ads Agent (xblguxS49CJ4r4OF) — DURAK NOKTASI

**Yapi (5 node, hepsi enabled, ama workflow disable):**
1. `Facebook Lead Ads` — n8n-nodes-base.facebookLeadAdsTrigger
2. `Map Fields and Score` — code (lead skor hesabi)
3. `Save to NocoDB` — n8n-nodes-base.nocoDb
4. `Is Hot Lead` — IF
5. `Alert Seyma` — Gmail (sicaksa Seyma'ya bildirim)

**Bu yapi tam istenildigi gibi.** Pasif olmasinin muhtemel sebepleri:
- Facebook Lead Ads credential eski Selahattin hesabinda, yeni hesap (Seyma) icin guncellenmedi
- Form/page secimi degisti (Slowdays Bodrum -> Slowdays Dijital Paketler)
- Bilerek pasif birakildi, simdi aktive edilebilir

**Yeni session'da bu sirayla ilerle:**
1. PowerShell ile node parametrelerini detayli cek (credential id, page id, form id, NocoDB field mapping, Gmail to-address)
2. FB credential'i yeni hesapla yenile (gerekirse)
3. Workflow'u activate et (PATCH /workflows/{id} ile active=true)
4. Test lead at, NocoDB'ye dustugunu ve Seyma'ya mail gittigini dogrula

### Lead Toplama Agent (l31p16NRZeyk4eEm) — Generic Webhook

5 node: Webhook -> Calculate Lead Score -> Create Lead in NocoDB -> Is Hot or Warm -> Send Hot Lead Alert (Gmail)
- Bu generic — herhangi bir kaynaktan webhook alir, lead'i NocoDB'ye yazar.
- LinkedIn agent ayri kurulmadiysa burasi LinkedIn icin de kullaniliyor olabilir.
- Master mimaride kaynak field'i set edilmeli (Meta/LinkedIn/Clay/IG DM)

### Musteri Mail Otomasyonu (faolAyTcoUJIBcal)

4 node: Webhook -> Alicilari Ayir (splitout) -> Kisisellestir (code) -> Gmail
- "Claude Trigger" adinda — yani LLM'den gelen mesaj ile tetikleniyor
- Birden fazla aliciya kisisellestirilmis mail atiyor

## Bilinen Eksiklikler

- LinkedIn outreach workflow yok (master mimaride var)
- Clay yerel arama workflow yok
- IG DM bot workflow yok
- Meta Lead Ads Agent pasif
