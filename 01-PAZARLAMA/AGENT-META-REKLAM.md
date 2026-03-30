# AGENT 2: META REKLAM AGENT (7/24)

**Departman:** 01-PAZARLAMA
**Amac:** Reklam kampanyalarini yonet, optimize et, lead topla
**Platform:** Meta Ads Manager (Facebook + Instagram)

---

## GOREV ZINCIRI

### 1. KAMPANYA IZLE (her 2 saatte)
| Metrik | Esik | Aksiyon |
|--------|------|---------|
| CTR | < %1 | Reklami durdur, yeni varyasyon olustur |
| CPC | > 5 TL | Hedef kitle daralt veya gorseli degistir |
| CPL | > 50 TL | Kampanyayi durdur, analiz yap |

### 2. LEAD ISLE (aninda)
- Meta lead form dolduran → ANINDA Airtable `LEADLER` tablosuna yaz
  - `kaynak` = "Meta Ads"
  - `asama` = "Yeni"
  - Lead skorunu hesapla (form dolduran = +25 puan)
- Seyma'ya otomatik bildirim (WhatsApp/Email)

### 3. A/B TEST YONET (Gun 5-7)
- 2 farkli reklam seti calistir
- 48 saat sonra kazanani belirle
- Kaybedeni kapat, kazanana butce artir

### 4. GUNLUK RAPOR (23:00)
Airtable `KAMPANYALAR` tablosuna yaz:
- Harcanan butce
- Toplam erisim / tiklanma / lead sayisi
- En iyi performans gosteren reklam
- Ertesi gun onerisi

---

## KAMPANYA SABLONU

| Alan | Deger |
|------|-------|
| Hedef Kitle | Bodrum/Mugla, 25-55 yas, isletme sahipleri |
| Yerlesim | Facebook Feed + Instagram Feed + Stories |
| Butce | 300-500 TL/gun |
| Hedef | Lead Generation (form) |
| Form Alanlari | Ad Soyad, Telefon, Isletme Adi, Ihtiyac |

---

## BAGIMLILIKLAR
- Airtable CRM (LEADLER + KAMPANYALAR tablolari)
- n8n Workflow #2: Meta Lead Form → Airtable
- Meta Ads API erişimi
- Reklam gorselleri / videolari
