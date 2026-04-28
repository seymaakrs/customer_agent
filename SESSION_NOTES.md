# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

---

## Session 2 — 2026-04-28 (devam ediyor)

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
- Tests: `tests/test_nocodb_client.py`, `tests/test_meta_agent.py`

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
