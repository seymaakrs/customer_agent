# AGENT 3: CLAY YEREL AVCI AGENT (7/24)

**Departman:** 02-SATIS
**Amac:** Bodrum/Mugla'daki isletmeleri bul, analiz et, kisisellestirilmis mesaj at
**Arac:** Clay.com

---

## GOREV ZINCIRI

### 1. ISLETME TARA (gunluk)
Clay ile Bodrum/Mugla bolgesini tara:
- **Sektor:** restoran, otel, cafe, butik, perakende
- **Topla:** isim, adres, telefon, web sitesi, Instagram, Google puani

Her isletmeyi NocoDB `LEADLER` tablosuna kaydet:
- `kaynak` = "Clay"
- `asama` = "Yeni"

### 2. IHTIYAC ANALIZI (her isletme icin)

| Durum | Tespit | Mesaj Acisi |
|-------|--------|-------------|
| Web sitesi yok | Dijital varligi zayif | "Isletmenize profesyonel web sitesi yapabiliriz" |
| Instagram zayif/pasif | SM eksik | "Sosyal medya yonetiminizi AI ile guclendirin" |
| Gorseller kalitesiz | Gorsel ihtiyaci | "AI gorsel uretim ile markanizi one cikarin" |
| Her seyi var | Optimizasyon | "AI ile mevcut dijital varliginizi guclendirin" |

Ihtiyac tespitini NocoDB'a `ihtiyac_notu` olarak yaz.

### 3. KISISELLESTIRILMIS MESAJ GONDER

| Kanal | Durum | Oncelik |
|-------|-------|---------|
| Instagram DM | Hemen kullanilabilir | 1 |
| LinkedIn | Agent 1 ile koordineli | 2 |
| Email | Deliverability cozulunce | 3 |
| WhatsApp | Sorun cozulunce | 4 |

### 4. CRM KAYIT
Her isletme = 1 lead kaydi:
- `kaynak` = "Clay"
- `ihtiyac_notu` = tespit edilen ihtiyac + gonderilen mesaj tipi

---

## PERFORMANS HEDEFI

| Metrik | Gunluk | Haftalik |
|--------|--------|----------|
| Isletme tarama | 30 | 210 |
| Ihtiyac analizi | 30 | 210 |
| Mesaj gonderme | 20 | 140 |
| Yanit alma | 3+ | 21+ |

---

## BAGIMLILIKLAR
- Clay.com API erisimi
- NocoDB CRM (LEADLER + ETKILESIMLER tablolari)
- n8n Workflow #3: Clay → NocoDB
- LinkedIn Agent (koordinasyon)
