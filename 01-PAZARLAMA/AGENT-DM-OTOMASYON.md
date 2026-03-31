# AGENT 4: DM BOT AGENT (7/24)

**Departman:** 01-PAZARLAMA
**Platform:** n8n custom build
**Amac:** IG + TikTok'ta otomatik mesajlasma, lead toplama

---

## GOREV ZINCIRI

### 1. YENI TAKIPCI → HOSGELDIN (aninda)

> "Merhaba! Vibe ID'ye hosgeldiniz.
> AI ile dijital pazarlama hizmetleri sunuyoruz.
> Isletmeniz icin ucretsiz icerik analizi ister misiniz?
> → 'EVET' yazin!"

### 2. "EVET" YAZANA → BILGI TOPLA

> "Harika! Birlikte bakalim:
> 1. Isletme adiniz?
> 2. Instagram hesabiniz? (@link)
> 3. En cok hangi konuda desteGe ihtiyaciniz var?"

### 3. BILGI GELINCE → CRM'E YAZ
NocoDB `LEADLER` tablosuna kaydet:
- `ad_soyad`, `sirket_adi`, `instagram`, `ihtiyac_notu`
- `kaynak` = "IG DM" veya "TikTok DM"
- `asama` = "Ilik" (aktif ilgi gosterdi)
- Lead skoru hesapla
- Seyma'ya bildirim

### 4. STORY YANITI → OTOMATIK CEVAP

> "Tesekkurler! Sizi tanimak isteriz. Isletmeniz hakkinda bilgi verir misiniz?"

---

## PERFORMANS HEDEFI

| Metrik | Gunluk | Haftalik |
|--------|--------|----------|
| Hosgeldin mesaji | 10+ | 70+ |
| "EVET" yaniti | 3+ | 21+ |
| CRM'e lead kaydi | 3+ | 21+ |

---

## BAGIMLILIKLAR
- n8n Workflow #4: IG DM → NocoDB
- Instagram API / TikTok API
- NocoDB CRM (LEADLER tablosu)
