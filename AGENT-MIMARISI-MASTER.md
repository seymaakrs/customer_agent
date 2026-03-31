# MINDID AGENT MIMARISI — ULTRA STRATEJIK ZINCIR SISTEMI
**Tarih:** 31 Mart 2026 (Guncellendi)
**HEDEF:** 1-30 NISAN 2026 → 240.000 TL / 4 HAFTA — HER AGENT BU HEDEFE HIZMET EDER
**GUNLUK LEAD HEDEFI:** MINIMUM 300 LEAD / GUN (tum kanallardan toplam)
**KURAL:** Her agent tek basina calisir ama hepsi tek bir noktada bulusur: NOCODB CRM → SEYMA → PARA

---

## BUYUK RESIM

```
╔══════════════════════════════════════════════════════════════════╗
║           HEDEF: 240.000 TL / 30 GUN (1-30 NISAN 2026)         ║
║           HAFTALIK: 60.000 TL | GUNLUK LEAD: MIN 300           ║
╚══════════════════════════════════════════════════════════════════╝
                              ↑
                    SEYMA (KAPANIS + ONAY)
                              ↑
                 ┌────────────┴────────────┐
                 │     NOCODB CRM        │
                 │  (TEK BULUSMA NOKTASI)  │
                 └────────────┬────────────┘
                              ↑
        ┌─────────┬─────────┬─┴──────┬──────────┬──────────┐
        ↑         ↑         ↑        ↑          ↑          ↑
   ╔════════╗ ╔════════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗
   ║LINKEDIN║ ║  META  ║ ║ CLAY  ║ ║DM BOT ║ ║TAKIP  ║ ║ITIRAZ ║
   ║ AGENT  ║ ║ AGENT  ║ ║ AGENT ║ ║ AGENT ║ ║ AGENT ║ ║ AGENT ║
   ╚════════╝ ╚════════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝
    7/24       7/24       7/24      7/24       7/24       7/24
    AVCI       AVCI       AVCI      AVCI       KOVALAYICI SAVUNMA
```

---

## ZINCIR AKISI (LEAD → PARA)

```
ADIM 1: AV (Lead Bulma — 6 Agent Paralel)
  LinkedIn Agent → lead bul + mesaj at
  Meta Ads Agent → reklam → form doldurt
  Clay Agent → yerel isletme tara → mesaj at
  DM Bot Agent → IG/TikTok yeni takipci → otomatik mesaj
  ↓
  TUM LEADLER → NOCODB CRM'e duser (otomatik)
  ↓

ADIM 2: ISINMA (Lead Takip — 2 Agent)
  Takip Agent → yanit vermeyenlere 48s/96s/7g otomatik takip
  Itiraz Agent → "pahali", "dusunecegim" diyenlere otomatik karsilama
  ↓
  ILIK/SICAK LEAD → Seyma'ya bildirim
  ↓

ADIM 3: KAPANIS (Seyma)
  Seyma → Discovery call → Teklif → Sozlesme → PARA
  ↓

ADIM 4: SONRASI
  Upsell Agent → 30 gunde otomatik upgrade teklifi
  Referans Agent → "arkadasini getir %10 indirim"
  ↓
  TEKRAR ADIM 1'e donus (dongu)
```

---

## AGENT 1: LINKEDIN AVCI AGENT (7/24)

**Departman:** 02-SATIS
**Gorev dosyasi:** `02-SATIS-MUSTERI-ILISKILERI/AGENT-LINKEDIN.md`
**Amac:** Yuksek gelir potansiyelli musteri bul, mesaj at, CRM'e kaydet
**Calısma:** 7 gun, 24 saat, durmadan

### Gorev Zinciri:
```
1. ARAMA (her 4 saatte 1 tur)
   → LinkedIn'de filtrele:
     Konum: Bodrum/Mugla/Turkiye
     Pozisyon: Isletme Sahibi, CEO, GM, Pazarlama Muduru
     Sektor: Otelcilik, Yeme-Icme, Perakende, Turizm, E-ticaret
   → Gunluk 20 yeni profil bul
   → Her profili NocoDB'a kaydet (isim, sirket, pozisyon, sektor, LinkedIn URL)

2. BAGLANTI ISTEGI (bulunca hemen)
   → Kisisellestirilmis not ile baglanti iste:
   "Merhaba [Isim], [Sehir]'deki [Isletme]'yi takip ediyorum.
   AI destekli dijital pazarlama ile deger katabileceGimize inaniyoruz.
   Baglanmak isterseniz sevinirim. — Seyma, Vibe ID"

3. MESAJ DIZISI (baglanti kabul edince)
   Mesaj 1 (hemen):
   "Tesekkurler! [Isletme] icin ucretsiz dijital analiz hazirlamak
   isteriz. Ilginizi ceker mi?"

   Mesaj 2 (+48 saat yanit yoksa):
   "Merhaba [Isim], Bodrum'daki isletmeler icin AI ile
   urettigimiz ornekleri gormek ister misiniz? [portfolyo linki]"

   Mesaj 3 (+5 gun yanit yoksa):
   "Son bir not: Deneme paketimiz 2.999 TL, risk sifir.
   Merak ederseniz buradayim. mindid.shop"

4. YANITLARI ISLE
   → Olumlu yanit → NocoDB'da "Ilik" yap → Seyma'ya ANINDA bildirim
   → Soru sordu → Cevapla (itiraz rehberine bak) → NocoDB guncelle
   → Olumsuz → NocoDB'da "Kayip" yap → 30 gun sonra tekrar dene

5. CRM KAYIT (her islemde)
   → NocoDB'a yaz: isim, sirket, asama, mesaj durumu, tarih, not
```

### Performans Hedefi:
| Metrik | Gunluk | Haftalik |
|--------|--------|----------|
| Yeni profil bulma | 20 | 140 |
| Baglanti istegi | 20 | 140 |
| Mesaj gonderme | 30 | 210 |
| Yanit alma | 5+ | 35+ |
| Sicak lead (Seyma'ya) | 2+ | 14+ |

---

## AGENT 2: META REKLAM AGENT (7/24)

**Departman:** 01-PAZARLAMA
**Gorev dosyasi:** `01-PAZARLAMA/reklam-kampanyalari/AGENT-META-REKLAM.md`
**Amac:** Reklam kampanyalarini yonet, optimize et, lead topla

### Gorev Zinciri:
```
1. KAMPANYA IZLE (her 2 saatte)
   → CTR, CPC, CPL kontrol et
   → CTR < %1 → reklami durdur, yeni varyasyon olustur
   → CPC > 5 TL → hedef kitle daralt veya gorseli degistir
   → CPL > 50 TL → kampanyayi durdur, analiz yap

2. LEAD ISLE (aninda)
   → Meta lead form dolduran → ANINDA NocoDB'a yaz
   → Otomatik bildirim Seyma'ya (WhatsApp/Email)
   → Lead skoru hesapla ve ata

3. A/B TEST YONET (Gun 5-7)
   → 2 farkli reklam seti calistir
   → 48 saat sonra kazanani belirle
   → Kaybedeni kapat, kazanana butce artir

4. GUNLUK RAPOR (23:00)
   → Harcanan butce
   → Toplam erisim / tiklanma / lead sayisi
   → En iyi performans gosteren reklam
   → Ertesi gun onerisi
   → NocoDB'a rapor kaydi
```

---

## AGENT 3: CLAY YEREL AVCI AGENT (7/24)

**Departman:** 02-SATIS
**Gorev dosyasi:** `02-SATIS-MUSTERI-ILISKILERI/AGENT-CLAY-OUTREACH.md`
**Amac:** Bodrum/Mugla'daki isletmeleri bul, analiz et, kisisellestirilmis mesaj at

### Gorev Zinciri:
```
1. ISLETME TARA (gunluk)
   → Clay ile Bodrum/Mugla bolgesini tara
   → Sektor: restoran, otel, cafe, butik, perakende
   → Topla: isim, adres, telefon, web sitesi, Instagram, Google puani

2. IHTIYAC ANALIZI (her isletme icin)
   → Web sitesi var mi? Yoksa → "Web sitesi yapabiliriz" mesaji
   → Instagram aktif mi? Zayifsa → "SM yonetimi" mesaji
   → Gorseller kaliteli mi? Degilse → "AI gorsel" mesaji
   → Her seyi varsa → "AI ile guclendirin" mesaji

3. KISISELLESTIRILMIS MESAJ GONDER
   → Email (deliverability cozulunce)
   → WhatsApp (sorun cozulunce)
   → Instagram DM (hemen)
   → LinkedIn (agent 1 ile koordineli)

4. NOCODB'A KAYDET
   → Her isletme = 1 lead kaydi
   → Kaynak: Clay
   → Ihtiyac notu: ne mesaj gonderildi
```

---

## AGENT 4: DM BOT AGENT (7/24)

**Departman:** 01-PAZARLAMA
**Gorev dosyasi:** `01-PAZARLAMA/AGENT-DM-OTOMASYON.md`
**Platform:** n8n custom build
**Amac:** IG + TikTok'ta otomatik mesajlasma, lead toplama

### Gorev Zinciri:
```
1. YENI TAKIPCI → HOSGELDIN (aninda)
   "Merhaba! Vibe ID'ye hosgeldiniz.
   AI ile dijital pazarlama hizmetleri sunuyoruz.
   Isletmeniz icin ucretsiz icerik analizi ister misiniz?
   → 'EVET' yazin!"

2. "EVET" YAZANA → BILGI TOPLA
   "Harika! Birlikte bakalim:
   1. Isletme adiniz?
   2. Instagram hesabiniz? (@link)
   3. En cok hangi konuda desteGe ihtiyaciniz var?"

3. BILGI GELINCE → CRM'E YAZ
   → NocoDB'a kaydet: isim, isletme, ihtiyac, kaynak: IG DM
   → Lead skoru ata
   → "Ilik" olarak isaretle
   → Seyma'ya bildirim

4. STORY YANITI → OTOMATIK CEVAP
   → "Tesekkurler! Sizi tanımak isteriz. Isletmeniz hakkinda
   bilgi verir misiniz?"
```

---

## AGENT 5: TAKIP KOVALAYICI AGENT (7/24)

**Departman:** 02-SATIS
**Gorev dosyasi:** `02-SATIS-MUSTERI-ILISKILERI/AGENT-TAKIP.md`
**Amac:** Yanit vermeyen leadleri kovala, birini bile kacirma

### Gorev Zinciri:
```
1. NOCODB'I TARA (her 6 saatte)
   → "Soguk" veya "Ilik" asamadaki leadleri kontrol et
   → Son iletisimden bu yana gecen sure hesapla

2. TAKIP KURALLARI:
   48 saat yanit yok → 2. mesaj gonder (farkli aci)
   96 saat yanit yok → 3. mesaj gonder (deneme paketi vurgula)
   7 gun yanit yok → Son mesaj ("Son firsat, kapimiz acik")
   14 gun yanit yok → "Soguk arsiv"e al, 60 gun sonra tekrar

3. KANAL SECIMI:
   → Ilk mesaj hangi kanaldan gittiyse, takip FARKLI kanaldan
   → Ornek: Email gitti, yanit yok → LinkedIn DM gonder
   → LinkedIn gitti, yanit yok → Instagram DM dene
   → Hicbiri olmadi → Telefon listesine ekle (Seyma arar)

4. NOCODB GUNCELLE (her islemde)
   → Son iletisim tarihi
   → Kac takip yapildi
   → Hangi kanallar denendi
```

---

## AGENT 6: ITIRAZ SAVUNMA AGENT (7/24)

**Departman:** 02-SATIS
**Gorev dosyasi:** `02-SATIS-MUSTERI-ILISKILERI/AGENT-ITIRAZ.md`
**Amac:** "Pahali", "dusunecegim" diyenlere aninda profesyonel cevap
**Referans:** `ITIRAZ-KARSILAMA.md` (12 itiraz + script)

### Gorev Zinciri:
```
1. ITIRAZ TESPIT (aninda)
   → Gelen mesajlarda anahtar kelime tara:
     "pahali" / "ucuz" / "butce" → Fiyat itirazi
     "dusunecegim" / "sonra" → Erteleme itirazi
     "baska teklif" / "rakip" → Rekabet itirazi
     "kucuguz" / "bize gore degil" → Olcek itirazi
     "yapay zeka" / "guvenilir mi" → Teknoloji itirazi
     "referans" / "ornek" → Kanit itirazi

2. OTOMATIK KARSILAMA
   → ITIRAZ-KARSILAMA.md'den uygun scripti sec
   → Kisisellesir: [isletme adi], [sektor], [konum] ekle
   → Mesaji gonder (ayni kanal uzerinden)

3. ESKALASYON (gerekirse)
   → 2 itiraz karsilamadan sonra hala olumsuz →
     Seyma'ya bildir: "Bu lead 2 kez itiraz etti, kisisel mudahale gerekli"
   → NocoDB'a not: itiraz turu + karsilama + sonuc

4. OGRENIM
   → Her itiraz + karsilama + sonucu kaydet
   → Haftalik rapor: En cok gelen itiraz hangisi? Hangi karsilama ise yaradi?
   → ITIRAZ-KARSILAMA.md'yi guncelleme onerisi sun
```

---

## ZINCIR ENTEGRASYON HARITASI

```
LINKEDIN AGENT ──┐
META AGENT ──────┤
CLAY AGENT ──────┼──→ NOCODB CRM ──→ TAKIP AGENT ──→ SEYMA
DM BOT AGENT ────┤         ↑                ↓
                 │    ITIRAZ AGENT ←── Musteri itirazi
                 │         ↓
                 │    NOCODB GUNCELLE
                 │         ↓
                 └──→ 116.000 TL
```

**Veri akisi:**
1. 6 agent paralel lead bulur → NocoDB'a yazar
2. Takip agent yanit vermeyenleri kovalar
3. Itiraz agent olumsuz yanitlari karsilar
4. Sicak lead → Seyma bildirim → Discovery call → Teklif → PARA
5. Her islem NocoDB'da izlenir → Gunluk rapor → Optimizasyon

---

## n8n WORKFLOW LISTESI (Kurulmasi Gereken)

| # | Workflow | Tetikleyici | Cikti |
|---|----------|-------------|-------|
| 1 | LinkedIn → NocoDB | Yeni lead bulundu | CRM kayit |
| 2 | Meta Lead Form → NocoDB | Form doldu | CRM kayit + Seyma bildirim |
| 3 | Clay → NocoDB | Isletme tarandi | CRM kayit |
| 4 | IG DM → NocoDB | "EVET" yazildi | CRM kayit |
| 5 | NocoDB → Takip mesaji | 48 saat gecti | Otomatik mesaj |
| 6 | NocoDB → Itiraz karsilama | Itiraz keylord tespit | Otomatik cevap |
| 7 | NocoDB → Seyma bildirim | Lead "Sicak" oldu | WhatsApp/Email bildirim |
| 8 | Gunluk rapor | Her gun 23:00 | Ozet rapor Seyma'ya |

---

## 30 GUNLUK AGENT PERFORMANS HEDEFI (1-30 NISAN 2026)

### HAFTALIK KIRILIM

| Hafta | Tarih | Gunluk Lead | Haftalik Lead | Sicak Lead | Teklif | Kapanis | Ciro |
|-------|-------|-------------|---------------|------------|--------|---------|------|
| 1 | 1-7 Nisan | 300 | 2.100 | 50 | 10 | 2 | 60.000 TL |
| 2 | 8-14 Nisan | 300 | 2.100 | 60 | 12 | 2 | 60.000 TL |
| 3 | 15-21 Nisan | 300 | 2.100 | 70 | 15 | 2 | 60.000 TL |
| 4 | 22-30 Nisan | 300 | 2.700 | 80 | 18 | 2+ | 60.000 TL |
| **TOPLAM** | **30 gun** | **300/gun** | **9.000** | **260** | **55** | **8+** | **240.000 TL** |

### GUNLUK LEAD DAGILIMI (MIN 300 / GUN)

| Kaynak | Gunluk Lead | Aciklama |
|--------|-------------|----------|
| Meta Ads | 150 | Reklam kampanyalari (form + landing page) |
| LinkedIn Agent | 30 | Profil bulma + baglanti + mesaj |
| Clay Agent | 50 | Yerel isletme tarama + outreach |
| DM Bot (IG/TikTok) | 40 | Otomatik mesajlasma |
| Organik + Referans | 30 | Web sitesi, SEO, agizdan agiza |
| **TOPLAM** | **300** | **Minimum hedef, ustu bonus** |

### KAPANIS HESABI
**8 kapanis x ortalama 30.000 TL = 240.000 TL**

Paket dagilimi tahmini:
- 2x Premium (29.000 TL) = 58.000 TL
- 3x Growth (14.900 TL) = 44.700 TL
- 2x Starter (7.500 TL) = 15.000 TL
- 5x Deneme (2.999 TL) = 14.995 TL
- Upsell/Ekstra = ~107.305 TL
- **TOPLAM: ~240.000 TL**

---

## ASLA UNUTMA

1. **HER AGENT TEK BIR HEDEFE HIZMET EDER: 240.000 TL / NISAN**
2. **GUNLUK 300 LEAD. BU SAYI ASAGI DUSMEZ.**
3. **HER LEAD DEGER. TEK BIR LEAD BILE KACIRMAK YOK.**
4. **TAKIP AGENT DURMAZ. YANIT GELENE KADAR KOVALAR.**
5. **ITIRAZ = FIRSAT. HER ITIRAZ BIR SATIS FIRSATIDIR.**
6. **NOCODB CRM = TEK GERCEK. ORADA OLMAYAN LEAD YOK DEMEKTIR.**
7. **SEYMA SADECE KAPANIS YAPAR. GERISI AGENTLARIN ISI.**
8. **HAFTALIK 60K HEDEF. HER CUMA KONTROL, SAPMA VARSA MUDAHALE.**
