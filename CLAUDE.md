# Customer Agent - Claude Session Hafizasi

> **HER YENI SESSION BASLANGICINDA OKU.** Bu dosya ve `SESSION_NOTES.md` projenin kalici hafizasidir.

## Proje Ozeti

**Hedef:** 7 gunde 116.000 TL gelir
**Mimari:** 6 agent paralel calisir (LinkedIn, Meta, Clay, IG DM, Takip, Itiraz) → NocoDB CRM → Seyma kapanis yapar
**Detay:** `AGENT-MIMARISI-MASTER.md`

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

## Mevcut Durak Noktasi
**Meta Ads Agent workflow'unda kalindi** (n8n'de). Devam etmek icin kullanici hazir.

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
