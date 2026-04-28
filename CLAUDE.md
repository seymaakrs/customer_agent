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

## Hazir Olan Altyapi

- [x] NocoDB kurulu (kullanici tarafindan)
- [x] Facebook Lead Ads form aktif: "Slowdays Dijital Paketler" (Slowdays Bodrum sayfasi)
- [x] n8n Facebook Lead Ads trigger hazir, sayfa+form dropdown'da goruluyor
- [x] AGENT-MIMARISI-MASTER.md: 6 agent + 8 workflow + NocoDB tablo sablonlari

## Bilinen Riskler / Acik Sorular

1. **Facebook credential riski:** n8n credential'i Selahattin user token'inda. Selahattin sayfa admin'liginden cikarilirsa workflow sessizce kirilir. Yedek credential onerildi ama kullanici "su an problem degil" dedi.
2. **mind-agent entegrasyonu:** 6 agent'in mind-agent SDK'ya nasil eklenecegi henuz tasarlanmadi (instruction dosyasi + tool seti + registry kaydi gerekli).
3. **NocoDB → mind-agent baglantisi:** mind-agent suanda Firebase kullaniyor. NocoDB icin yeni bir client (`src/infra/nocodb_client.py`) gerekecek.

## Repo Haritasi

```
customer_agent/      Bu repo - sadece dokumantasyon ve mimari
mind-agent/          Python OpenAI Agents SDK orchestrator (kod buraya eklenecek)
mind-id/             Next.js admin paneli (UI ve n8n proxy)
```

## Calisma Stili

1. Yeni session basinda: BU DOSYAYI ve `SESSION_NOTES.md`'yi oku.
2. Onemli karar verildiginde: BURAYA yaz.
3. Session sonunda: `SESSION_NOTES.md`'ye o session'da yapilanlari ekle.
4. Belirsiz bir sey varsa: VARSAYIM YAPMA, kullaniciya sor.
5. Kullanici yeni mezun bir yazilim muhendisi gibi davranir — kavramlari acikla, surece dahil et.
