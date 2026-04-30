# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

---

# Session Notes - Customer Agent

> En yeni session en ustte. Her session sonunda buraya yazilan notlar kalici hafiza olarak kullanilir.

---

## Session 5 — 2026-04-30 (Zernio kesfi + revize plan, Meta park edildi)

### TL;DR (yeni session bunu oku, kullaniciya anlatmasin)

Kullanici yeni session acti cunku oncekinde API error aldi. CLAUDE.md ve SESSION_NOTES.md okundu, devam edildi. Bugun:
1. Meta Lead Ads webhook kapsamli debug edildi -> kanitlandi ki **App Development modunda oldugu icin** webhook teslim olmuyor
2. Stratejik karar: **Meta agent PARK** (App Review icin demo+privacy hazirlamak su an verimsiz; Seyma haftalik manuel CSV import)
3. Kullanici Seyma'nin Claude Console'da kurdugu **Zernio agent spec'ini** paylasti -> `ZERNIO-AGENT-SPEC.md` olarak kaydedildi
4. Kullanici "Zernio'da 3 paket aldigimizi" gosterdi (Analitik, Gelen Kutusu, Reklamlar -- her biri $10/mo)
5. Zernio arastirildi -> **15 platform tek API**, n8n native node var, IG/LinkedIn/FB DM webhook destegi, Meta+LinkedIn+TikTok ads API
6. Plan revize edildi: Apollo + IG Graph API + LinkedIn API ayri ayri kurmak yerine **Zernio tek noktadan**
7. **3 soru kullanicidan bekliyor** (asagida)

### Bu Session'da Tamamlanan Diagnostik (Meta Lead Ads)

Tum altyapi DOGRU kuruldu, sorun App publish durumu:
- ✅ Workflow `xblguxS49CJ4r4OF` 5 node, hepsi yesil tikli, Published
- ✅ FB Lead Ads credential connected (Client ID 1582227782846873)
- ✅ App Secret yenilendi: `af4cb94b90e4789ef6bdeafd826b06db` (n8n credential'a paste edildi)
- ✅ OAuth reconnect yapildi
- ✅ Page-App subscription Graph API ile dogrulandi:
  - `GET /me/accounts` -> Page ID: `948197981703583` (Slowdays Bodrum)
  - `GET /948197981703583/subscribed_apps` -> Slowdays Lead Integration listede, leadgen subscribed
- ✅ FB App webhook config: callback URL = `https://mindidai.app.n8n.cloud/webhook/2a3403b2-f405-4ef5-b640-317747ecb6fd/webhook`, leadgen subscribed
- ❌ App "Unpublished" (Development mode) -> production data teslim edilmiyor
- 🔍 Iki FB App tespit edildi: Slowdays Lead Integration (kullanilan) ve "n8n" (1865681887495088, bos kabuk -- yoksay)
- 🔍 App contact email Selahattin'in (selehattinkoc@gmail.com) -- temizlik amacli sonra guncellenebilir, kritik degil

### Zernio Bulgusu (KRITIK)

**Zernio = 15 platform icin tek API** (Instagram, TikTok, X, Facebook, LinkedIn, YouTube, WhatsApp, Threads, Pinterest, Reddit, Bluesky, Telegram, Google Business, Snapchat, Discord)

**Kullanicinin paketleri:**
| Paket | Fiyat | Durum |
|---|---|---|
| Analitik | $10/mo | ✅ 7 gun deneme aktif |
| Gelen Kutusu (Inbox) | $10/mo | ⏸️ Eklenmemis (eklenecek) |
| Reklamlar (Ads) | $10/mo | ⏸️ Eklenmemis (Faz D'de eklenir) |

**Plana etkisi:**
- IG DM Agent: Apollo + IG Graph API yerine Zernio Inbox webhook (App Review YOK)
- LinkedIn Agent: LinkedIn cookie cekme/Phantombuster yerine Zernio LinkedIn DM API
- Daily Reporter: Meta + IG + LinkedIn Insights ayri ayri yerine Zernio Analytics tek API
- Meta Lead Ads (PARK): Zernio'nun kendi Meta App'i Lead Ads cekiyorsa App Review beklemeden cozulebilir -- TEST EDILMEDI henuz, kullanici onayi bekleniyor

**Maliyet:** Aylik ~$60 (Apollo + Phantombuster) -> $30 (Zernio 3 add-on) = yari fiyat
**Sure:** 3 hafta -> 2 hafta (entegrasyonlar tek API uzerinden)

### Revize Edilmis Plan (Kullanici Onayi Bekleyen)

```
Faz A — Clay Agent (yerel arama Bodrum/Mugla)              4-5 gun
Faz B — Zernio entegrasyonu (n8n native node + Inbox)       2-3 gun
Faz C — IG DM + LinkedIn Agent (Zernio Inbox webhook)       3-4 gun
Faz D — Daily Reporter + Reklamlar API otonom karar         2 gun
Faz E — mind-agent + mind-id Sales Dashboard                5-7 gun
```

**Faz E hedefi:** Seyma "kac sicak lead var?" diye sorar -> mind-agent NocoDB'den ceker -> dogal dilde cevap (mind-id dashboard'da chat arayuzu)

### Kullanicidan Bekleyen 3 Soru (Session 6'da Sor)

1. **Zernio "Gelen Kutusu" paketini ekleyelim mi?** ($10/mo, Faz B/C icin zorunlu)
2. **Meta Lead Ads'i Zernio ile test edelim mi?** (yarim saat, App Review beklemesini iptal edebilir)
3. **Faz sirasi:** Once Clay (A) mi, once Zernio entegrasyonu (B) mu? **Onerim B** -- Zernio kurulur kurulmaz 3 kanaldan lead gelir.

### Korunacak (DOKUNMA, KURAL)

- Meta Lead Ads workflow (xblguxS49CJ4r4OF) PAUSED, silmeyin -- App Review onayinda direkt aktive edilecek
- mind-agent main -- DOKUNULMUYOR
- Mevcut 5 calisan agent: Lead Toplama, Takip, Itiraz, Upsell, Referans, Mail Otomasyonu

### Eklenen Master Doc

`customer_agent/ZERNIO-AGENT-SPEC.md` -- Seyma'nin Claude Console'da kurdugu agent mimarisi:
- C-Suite roller: CGO, CAIDO, CBO
- Otonom karar kurallari (CTR<%1 -> durdur, CPL>50 -> dondur, lead score 8+ -> Seyma'ya 2 dk icinde bildir)
- Gunluk rapor formati (23:00 cron)
- Itiraz sablonlari (pahali/dusunecegim/baska teklif)
- Yasakli ifadeler (CBO standardi: spam YOK, baski taktigi YOK)

### Kullanici Durumu (Onemli Not)

- Saatlerce Meta debug yapildi, kullanici cok yoruldu/bunaldi -- Session 6'da OZEN GOSTER
- Hizli sonuc istiyor, hata istemiyor, plan netligi istiyor
- Anydesk'ten Seyma'nin hesabindan calisiyordu -> kendi PC'sine gecmek istedi (henuz yapilmadi, FB davet adimi anlatildi ama yapilmadi)

### Bir Sonraki Session — Net Akis

1. **Selam ver, "kaldigimiz yer" diye sor** (kullanici tekrar anlatmasin diye bu dosyayi oku)
2. **3 soruyu hatirla**, kullaniciya sun
3. Cevaplara gore Faz A veya Faz B baslat
4. **mind-agent main'e DOKUNMA**
5. Her buyuk adimda ONAY al
6. Session sonunda bu dosyayi tekrar guncelle

---

## Session 4 — 2026-04-29 (Meta Lead Ads webhook debug — App Review'da takildi)

### Kullanici Durumu
- Kullanici cok bunalmis, saatlerdir ayni sorunda kalmis (Meta Agent calismiyor)
- Anydesk uzerinden Seyma'nin hesabindan calisiyordu, ardindan kendi PC'sinde devam etti

### Meta Lead Ads Workflow Detayli Inceleme (n8n: xblguxS49CJ4r4OF)

**Tum altyapi DOGRU kuruldu, sorun App publish durumu:**

| Komponent | Durum | Detay |
|---|---|---|
| Workflow yapisi | ✅ | 5 node: FB Lead Ads → Map Fields → NocoDB → Is Hot → Alert Seyma |
| Workflow durumu | ✅ Published | n8n'de aktif, dinliyor |
| FB Lead Ads credential | ✅ Account connected | Client ID: 1582227782846873 (Slowdays Lead Integration) |
| Page secimi | ✅ | Slowdays Bodrum (ID: 948197981703583) |
| Form secimi | ✅ | Slowdays Dijital Paketler |
| App Secret n8n credential | ✅ Guncellendi | af4cb94b90e4789ef6bdeafd826b06db (Session 4'te elle paste edildi) |
| FB App webhook config | ✅ | Callback URL: n8n production URL, leadgen subscribed |
| Page-App subscription | ✅ DOGRULANDI | Graph API ile kontrol: leadgen subscribed |
| NocoDB credential | ✅ Yesil tikli | n8n'de calisir durumda |
| Gmail credential | ✅ Yesil tikli | Alert Seyma node'u calisir |

**n8n Production Webhook URL:**
`https://mindidai.app.n8n.cloud/webhook/2a3403b2-f405-4ef5-b640-317747ecb6fd/webhook`

### KOK SORUN: FB App Development Modunda

**Slowdays Lead Integration (App ID: 1582227782846873) "Unpublished/Development" modunda.**

FB Webhooks sayfasinda kirmizi uyari:
> "Apps will only be able to receive test webhooks sent from the dashboard while the app is unpublished. No production data, including from app admins, developers or testers, will be delivered unless the app has been published."

- Lead Ads Testing Tool'dan gonderilen test lead -> sonsuz "Pending" -> n8n'e ulasmiyor
- FB Webhooks sayfasindaki "Test" butonu -> n8n executions bos
- Webhook altyapisi tam, sadece App Live mode'a alinmamis

### Yapilan Tum Diagnostik Adimlar

1. ✅ Lead Ads Testing Tool'da Page Diagnostics yesil (Lead Permission, Lead Access Manager, Page Admin)
2. ✅ Page Lead Access ayarlarinda "Slowdays Lead Integration" CRM listede gorundu
3. ✅ Webhook config'de Page > leadgen subscribed (Callback URL n8n)
4. ✅ Verify and save butonu gri (zaten dogrulanmis)
5. ✅ App Secret yenilendi, n8n credential update edildi, OAuth reconnect yapildi
6. ✅ Workflow unpublish/republish yapildi
7. ✅ Graph API ile Page subscription dogrulandi: `948197981703583/subscribed_apps` -> Slowdays Lead Integration listede, leadgen var
8. ❌ Tum dogru yapilandirmaya ragmen webhook gelmiyor — App publish gerekli

### Diger Bulgular

- **2 FB App var:** "Slowdays Lead Integration" (kullanilan, 1582227782846873) ve "n8n" (1865681887495088 — bos kabuk, hicbir sey yapilandirilmamis)
- **App contact email hala selehattinkoc@gmail.com** — Selahattin ait, bizim sorunumuz icin etkisiz ama temizlik amacli sonra guncellenebilir
- **Permissions durumu:** ads_management, ads_read, business_management, leads_retrieval hepsi "Ready for testing" — yani dev mode'da admin kullanabilir AMA Live icin App Review gerekli
- **Yayin sayfasi 2 eksik gosteriyor:**
  1. Privacy Policy URL (bos)
  2. Capture & manage ad leads with Marketing API use case (App Review gerekli olabilir)

### Bir Sonraki Session — Net Plan (GUNCELLENDI 2026-04-29 sonu)

**Stratejik karar (kullanici):** Meta agent'i park et, eksik 3 agent'i kur (Clay, LinkedIn, IG DM).

Sebep: Meta App Review icin demo video + privacy policy hazirligi su an verimsiz. Seyma haftalik manuel CSV import yapacak. Lead hacmi 50/hafta'yi gectiginde App Review'a basvurulacak (3-4 hafta sonra).

**Yeni Yol Haritasi:**

```
Hafta 1 (su an)   -> Clay Agent (yerel arama + cold mail) ⭐ EN COK BIRAK GETIRIR
Hafta 2           -> LinkedIn Agent (Apollo + LinkedIn outreach)
Hafta 3           -> IG DM Agent (Instagram Direct Message bot)
Hafta 4           -> Meta App Review basvurusu (lead hacmi oturduktan sonra)
2 ay              -> Mind-agent gecisi (n8n -> Python SDK)
```

**Korunacak (DOKUNMA):**
- Meta Lead Ads workflow (xblguxS49CJ4r4OF) - paused, silmeyin
- mind-agent main - dokunulmuyor (kural)
- Mevcut 5 calisan agent (Lead Toplama, Takip, Itiraz, Upsell, Referans, Mail Otomasyonu)

### Onemli Karar — Workflow YENIDEN KURMA

**Kullanici sordu:** "Bu workflow'u silip bastan temiz mi kursak?"

**Cevap:** HAYIR. Sebepleri:
- Mevcut workflow yapisi tam dogru (5 node, hepsi yesil tikli)
- Sorun workflow'da degil, FB App publish durumunda
- Yeniden kurmak ayni sorunu cozmez (App Review yine gerekli)
- Ek olarak: NocoDB field mapping, Gmail template gibi detaylar yeniden ayarlanmasi gerekir

**Mevcut workflow'u koru.** Tek ihtiyac App Review.

### Kullaniciya Notlar

- Saatlerdir ayni sorunda kalindi, kullanici cok yoruldu
- App Review beklenmesi gerekecek bu gece bitirme imkani yok
- Yarin Privacy Policy + App Review basvurusu birlikte 1 saatte halledilebilir
- mind-agent'a ASLA dokunulmadi (kuralina uyuldu)
- Bu session'da hicbir kod degisikligi yapilmadi, sadece config ve diagnostics

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
