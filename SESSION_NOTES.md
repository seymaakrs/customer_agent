# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

---

## Session 3 — 2026-04-28 (n8n node parametreleri detayli)

### Calisilan workflow'lar - Detaylar

PowerShell ile tum node parametreleri cekildi. Detaylar CLAUDE.md'deki
"n8n Workflow Node Parametreleri" bolumune islendi.

**Onemli kesifler:**
1. Meta Lead Ads ve Lead Toplama AYNI NocoDB tablosuna yaziyor (m5lcgc5ifeqh38h)
2. Iki workflow'da da skorlama mantigi paralel ama farkli formuller var
3. Tum sicak/ilik leadler seymaakrs@gmail.com'a HTML mail ile gidiyor
4. Mail Otomasyon (Claude Trigger) ayri webhook (LLM tetikleyici)
5. Master mimari'deki "her agent ayri n8n workflow" yerine yapilan: "1 ozel Meta trigger + 1 generic webhook (Lead Toplama)"
   - LinkedIn/Clay/IG DM Lead Toplama webhook'una post etmeli
   - Meta direkt FB trigger ile geliyor

### Meta Lead Ads Aktif Etme Plani

1. ✅ Yapi dogru, sadece pasif
2. 🚧 Kullanici **Facebook credential reconnect** yapiyor (Selahattin -> Seyma)
   - Ya mevcut credential'i (eu0Cazh3zO0houcS) override ediyor
   - Ya da yeni credential olusturuyor (oneri: temiz olur)
3. ⏳ Reconnect bitince ben PowerShell aktive komutu verecegim:
   ```powershell
   Invoke-RestMethod -Uri "https://mindidai.app.n8n.cloud/api/v1/workflows/xblguxS49CJ4r4OF/activate" -Method POST -Headers $headers
   ```
4. ⏳ Test lead: https://developers.facebook.com/tools/lead-ads-testing/

### Calisma Modu (Kalici Hatirlatma)

- **Sandbox <-> n8n erisim YOK** (Anthropic egress kisitlamasi)
- **Token sahip:** Kullanici, paylasildi ama sandbox'tan 403 doner
- **Yontem:** Claude komut/JSON yazar -> Kullanici PowerShell'de calistirir -> Cikti yapistirilir
- **PowerShell template:** Her komutun basina:
  ```powershell
  $TOKEN = '<token>'
  $headers = @{ 'X-N8N-API-KEY' = $TOKEN }
  ```

---

## Session 3 — 2026-04-28 (n8n envanter cikartildi)

### n8n API ile Workflow Listesi Cekildi

Kullanici PowerShell ile n8n REST API'ye baglandi (sandbox -> n8n bloklu, kullanici aracilik etti).
Tam liste CLAUDE.md'deki "n8n Workflow Envanteri" bolumunde.

**Aktif olan sales/CRM agent'lari:** Lead Toplama, Takip, Itiraz, Upsell, Referans, Musteri Mail Otomasyonu
**Pasif:** Meta Lead Ads Agent (yapisi dogru, sadece activate edilmemis), Facebook Lead Ads Performance Tracker
**Yok:** LinkedIn outreach, Clay yerel arama, IG DM bot

### Meta Lead Ads Agent - Detayli Yapi (5 node)

```
Facebook Lead Ads -> Map Fields and Score -> Save to NocoDB -> Is Hot Lead (IF) -> Alert Seyma (Gmail)
```

Yapi dogru, sadece pasif. Aktive etmeden once node parametrelerini (credential, page/form id, field mapping)
detayli incelemek lazim.

### Onaylanmis Calisma Modu

Sandbox <-> n8n erisimi olmadigi icin: **Ben komut/JSON yaziyorum, kullanici PowerShell'de calistirip
ciktiyi yapistiriyor.** Bu yontemle workflow'lari ben kuracagim/duzenleyecegim, kullanici sadece
"Enter" tusuna basacak.

---

## Session 3 — 2026-04-28 (kullanici brief)

### Kullanicidan Gelen Guncel Durum Bilgisi

**Hazir / Aktif:**
- ✅ NocoDB **aktif**, tablolar olustu, n8n yaziyor
- ✅ **Cogu agent kuruldu** ve NocoDB'ye lead yaziyor (n8n workflow olarak)
- ✅ **Seyma'ya mail bildirim aktif** — n8n'den mail gidiyor
- ✅ **Production sunucu: Google Cloud VM** — n8n bu VM'de calisiyor
- ✅ SSH ile test verisi gonderiliyor (test akisi calisiyor)
- ✅ **Facebook hesap gecisi tamam:** Selahattin -> Seyma. Kullanicinin tum yetkileri var, kimseden onay almasi gerekmiyor

**Mevcut Tikanma:**
- 🚧 **Meta Ads agent workflow'u** — n8n'de bu agent'ta kalindi. FB hesap geçişi ile ilgili duraksama vardi, simdi devam etmek istiyor

**Buyuk Hedef Sirasi:**
1. **Once:** n8n mimarisini tamamla — eksik agent'lari bitir, tum workflow'lari calisir hale getir
2. **Sonra:** n8n'deki sistemi mind-agent SDK icine al (kod tarafina)

### Kural — kullanici acik soyledi
- Mind-agent ASLA bozulmamali
- HER ZAMAN geri donulebilir olmali
- Onay almadan radikal degisiklik YASAK
- Her seyi sormaya gerek yok — sadece projeye ait belirsizlik varsa sor (yetki sorma, kullanicinin var)

### Bekleyen Aksiyonlar
1. **Meta Ads workflow tamamla** (n8n) — kullanici devam etmek istiyor, neyin eksik oldugu netlessin
2. Diger agent workflow'larin durumu — hangileri tamamlandi, hangileri yarim?
3. Mimari tamamlandiktan SONRA mind-agent gecisi planlanacak

---

## Session 2 — 2026-04-28

### Yapilanlar (customer_agent)
- `AGENT-MIMARISI-MASTER.md` Airtable -> NocoDB gecisi yapildi
- Meta Agent bolumune Facebook hesap degisimi notu eklendi (Slwodayss yeni hesap)
- NocoDB tablo sablonlari eklendi: `leads`, `lead_messages`, `seyma_notifications`
- n8n workflow tablosuna durum kolonu eklendi
- PR #1 acildi (draft): https://github.com/seymaakrs/customer_agent/pull/1
- `CLAUDE.md` ve `SESSION_NOTES.md` olusturuldu (kalici hafiza altyapisi)

### Yapilanlar (mind-agent) — Meta Agent entegrasyonu
- `src/infra/nocodb_client.py` — NocoDB v2 REST API wrapper (httpx, ServiceError)
- `src/infra/errors.py` — `_NOCODB_MAP` eklendi (HTTP 400/401/404/429/5xx -> ErrorCode)
- `src/app/config.py` — 5 yeni env: `NOCODB_BASE_URL`, `NOCODB_API_TOKEN`, `NOCODB_LEADS_TABLE_ID`, `NOCODB_MESSAGES_TABLE_ID`, `NOCODB_NOTIFICATIONS_TABLE_ID`
- `src/tools/sales/nocodb_tools.py` — 6 tool: create_lead, update_lead, get_lead, query_leads, log_lead_message, notify_seyma
- `src/agents/instructions/sales/meta.py` — Meta Agent instruction (lead skor formulu, asama haritasi, tool listesi)
- `src/agents/sales/meta_agent.py` — Agent factory
- `src/tools/agent_wrapper_tools.py` — `create_meta_agent_wrapper_tool` eklendi (orchestrator routing icin)
- `src/agents/orchestrator_agent.py` — Meta agent orchestrator tools listesinde
- `src/agents/registry.py` — `create_meta` + registry kaydi
- `src/agents/instructions/orchestrator.py` — meta_agent_tool routing keyword'leri eklendi
- Tests: `tests/test_nocodb_client.py`, `tests/test_meta_agent.py` — **13/13 PASSED**
- mind-agent PR #5 (draft): https://github.com/seymaakrs/mind-agent/pull/5

### KARAR (Session 2 sonu)

**Kullanici onay almadan yapilan radikal degisikliklere itiraz etti.** Mind-agent
icin kural: HER ZAMAN ONAY AL, ASLA radikal degisiklik yapma, geri donulebilir
olmali.

**Mevcut durum:**
- mind-agent main: DOKUNULMADI. Tum kod degisiklikleri PR #5 draft'inda branch'te bekliyor.
- customer_agent main: SADECE bu hafiza dosyalari (CLAUDE.md + SESSION_NOTES.md) merge edilecek.
- AGENT-MIMARISI-MASTER.md degisiklikleri (Airtable->NocoDB, FB hesap notu) PR #1 draft'inda branch'te bekliyor — kullanici karari icin.
- mind-id: HIC dokunulmadi.

**Branch:** `claude/check-facebook-meta-ads-KM4MZ` (her iki repoda)
- Istenirse merge edilir, istenirse silinir. Karar kullaniciya ait.

### Sonraki Session Icin Notlar
- BU DOSYAYI ve `CLAUDE.md`'yi OKU, baslamadan once kullanicinin sana onceki
  konusmalardan ne hatirlamani bekledigini gorursun.
- ONAY ALMADAN KOD DEGISTIRME. Once plan sun, sor, sonra yap.
- mind-agent main'i el degmedi. Eger kullanici "Meta agent'i tamamla"
  derse PR #5'i incele, branch'i kullan, main'e bos yere bir sey gondermeden once SOR.
- Eger kullanici master doc guncellemelerini de istiyorsa PR #1'i merge et.

---

## Session 1 — 2026-03-29

### Yapilanlar
- `AGENT-MIMARISI-MASTER.md` olusturuldu (6 agent + zincir + n8n workflow listesi)
- Master mimari karari: Tum lead'ler tek CRM'de bulusur, Seyma sadece kapanis yapar
