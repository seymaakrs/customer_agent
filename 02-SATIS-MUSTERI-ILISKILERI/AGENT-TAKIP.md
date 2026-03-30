# AGENT 5: TAKIP KOVALAYICI AGENT (7/24)

**Departman:** 02-SATIS
**Amac:** Yanit vermeyen leadleri kovala, birini bile kacirma

---

## GOREV ZINCIRI

### 1. AIRTABLE'I TARA (her 6 saatte)
- `asama` = "Soguk" veya "Ilik" olan leadleri kontrol et
- Son iletisimden bu yana gecen sureyi hesapla
- `TAKIP KUYRUGU` tablosundan aktif takipleri oku

### 2. TAKIP KURALLARI

| Sure | Aksiyon | Mesaj Tonu |
|------|---------|------------|
| 48 saat yanit yok | 2. mesaj gonder | Farkli aci, deger onerisi |
| 96 saat yanit yok | 3. mesaj gonder | Deneme paketi vurgula |
| 7 gun yanit yok | Son mesaj | "Son firsat, kapimiz acik" |
| 14 gun yanit yok | Soguk arsive al | 60 gun sonra tekrar aktif et |

### 3. KANAL SECIMI
Ilk mesaj hangi kanaldan gittiyse, takip **FARKLI** kanaldan:

```
Email gitti, yanit yok     → LinkedIn DM gonder
LinkedIn gitti, yanit yok  → Instagram DM dene
Instagram gitti, yanit yok → Email dene
Hicbiri olmadi             → Telefon listesine ekle (Seyma arar)
```

### 4. CRM GUNCELLE (her islemde)
Airtable `TAKIP KUYRUGU` tablosunu guncelle:
- `son_iletisim_tarihi`
- `takip_sayisi` +1
- `denenen_kanallar` guncelle
- `sonraki_kanal` belirle
- `sonraki_takip_tarihi` hesapla

---

## PERFORMANS HEDEFI

| Metrik | Gunluk | Haftalik |
|--------|--------|----------|
| Takip mesaji gonderme | 15+ | 105+ |
| Yanit alma (takipten) | 3+ | 21+ |
| Sicak'a yukseltme | 1+ | 7+ |
| Seyma telefon listesi | 2+ | 14+ |

---

## BAGIMLILIKLAR
- Airtable CRM (LEADLER + TAKIP KUYRUGU + ETKILESIMLER tablolari)
- n8n Workflow #5: Airtable → Takip mesaji
- Tum kanallara erisim (Email, LinkedIn, IG, WhatsApp)
