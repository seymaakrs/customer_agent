# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

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
