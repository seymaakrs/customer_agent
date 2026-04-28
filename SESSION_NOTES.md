# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

---

## Session 2 — 2026-04-28 (devam ediyor)

### Yapilanlar
- `AGENT-MIMARISI-MASTER.md` Airtable -> NocoDB gecisi yapildi
- Meta Agent bolumune Facebook hesap degisimi notu eklendi (Slwodayss yeni hesap)
- NocoDB tablo sablonlari eklendi: `leads`, `lead_messages`, `seyma_notifications`
- n8n workflow tablosuna durum kolonu eklendi
- PR #1 acildi (draft): https://github.com/seymaakrs/customer_agent/pull/1
- `CLAUDE.md` ve `SESSION_NOTES.md` olusturuldu (kalici hafiza altyapisi)

### Konusulan / Ogrenilen
- Kullanici NocoDB'yi kurdu, kullanima hazir
- Facebook hesap degisimi yapildi ama n8n hala calisiyor (Selahattin'in user token'i sayfa admin yetkisini koruyor)
- Kullanici acil olarak Facebook credential yenilemesi istemiyor — ilerlemek istiyor
- **Yeni hedef:** 6 agent'i mind-agent SDK sistemine entegre etmek

### Bekleyen Aksiyonlar (oncelik sirasi)
1. **mind-agent entegrasyon plani:** 6 agent (LinkedIn, Meta, Clay, IG DM, Takip, Itiraz) mind-agent SDK'da nasil yapilanacak?
   - Her agent icin: `src/agents/instructions/` altinda instruction dosyasi
   - Her agent icin: `src/tools/` altinda tool seti
   - `src/agents/registry.py`'de kayit
   - Orchestrator'a yeni keyword'ler
2. **NocoDB client:** `src/infra/nocodb_client.py` (REST API wrapper)
3. **Yeni tools:** `nocodb_tools.py` (create_lead, update_lead, get_leads, log_message)
4. **Webhook entegrasyon:** n8n -> mind-agent /task endpoint baglantisi
5. **Mind-id UI:** Yeni agent'lari tetikleyen panel

### Sonraki Session Icin Notlar
- Once "Meta Agent" tek basina end-to-end calistirilmali (en hazir olani)
- Diger agent'lar bunu sablon alarak eklenir
- LinkedIn agent icin Apollo/PhantomBuster gibi 3rd party gerekli mi sorulmali

---

## Session 1 — 2026-03-29

### Yapilanlar
- `AGENT-MIMARISI-MASTER.md` olusturuldu (6 agent + zincir + n8n workflow listesi)
- Master mimari karari: Tum lead'ler tek CRM'de bulusur, Seyma sadece kapanis yapar
