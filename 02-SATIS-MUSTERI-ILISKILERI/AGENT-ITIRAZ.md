# AGENT 6: ITIRAZ SAVUNMA AGENT (7/24)

**Departman:** 02-SATIS
**Amac:** "Pahali", "dusunecegim" diyenlere aninda profesyonel cevap
**Referans:** `ITIRAZ-KARSILAMA.md`

---

## GOREV ZINCIRI

### 1. ITIRAZ TESPIT (aninda)
Gelen mesajlarda anahtar kelime tara:

| Anahtar Kelimeler | Itiraz Turu |
|--------------------|-------------|
| "pahali", "ucuz", "butce", "para", "fiyat" | Fiyat |
| "dusunecegim", "sonra", "simdi degil" | Erteleme |
| "baska teklif", "rakip", "alternatif" | Rekabet |
| "kucuguz", "bize gore degil", "buyuk" | Olcek |
| "yapay zeka", "guvenilir mi", "bot mu" | Teknoloji |
| "referans", "ornek", "kimin icin yaptin" | Kanit |

### 2. OTOMATIK KARSILAMA
- `ITIRAZ-KARSILAMA.md`'den uygun scripti sec
- Kisisellesir: `[isletme_adi]`, `[sektor]`, `[konum]` ekle
- Mesaji ayni kanal uzerinden gonder

### 3. ESKALASYON (gerekirse)

```
1. itiraz → Otomatik karsilama
2. itiraz → Farkli script ile tekrar
3. itiraz veya hala olumsuz → Seyma'ya eskalasyon:
   "Bu lead 2 kez itiraz etti, kisisel mudahale gerekli"
```

Airtable'a not: itiraz turu + karsilama + sonuc

### 4. OGRENIM
- Her itiraz + karsilama + sonucu `ITIRAZLAR` tablosuna kaydet
- Haftalik rapor:
  - En cok gelen itiraz hangisi?
  - Hangi karsilama ise yaradi?
  - ITIRAZ-KARSILAMA.md guncelleme onerisi

---

## PERFORMANS HEDEFI

| Metrik | Gunluk | Haftalik |
|--------|--------|----------|
| Itiraz tespit | 5+ | 35+ |
| Basarili karsilama | 3+ | 21+ |
| Eskalasyon (Seyma) | 1-2 | 7-10 |

---

## BAGIMLILIKLAR
- ITIRAZ-KARSILAMA.md (script rehberi)
- Airtable CRM (LEADLER + ITIRAZLAR + ETKILESIMLER tablolari)
- n8n Workflow #6: Airtable → Itiraz karsilama
