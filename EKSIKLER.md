# EKSIKLER VE GERI DONULECEKLER
**Son guncelleme:** 23 Nisan 2026

---

## COZULMUS ✅

### 1. NocoDB Sektor Listesi → ✅ COZULDU
NocoDB arayuzunden 15 sektor eklendi. Code node'da fallback ile dogru sektor kaydediliyor.

### 3. Test Verileri → ✅ COZULDU
Test kayitlari temizlendi.

### 5. Lead Skorlama → ✅ COZULDU
Skor hesaplaniyor, NocoDB'ye yaziliyor, mailde gorunuyor.

### 9. Lead Skoru NocoDB'ye Yazilmiyor → ✅ COZULDU
Workflow yeniden duzenlendi: Webhook → Code (skor hesapla) → Create a row (skorla kaydet). Artik NocoDB `lead_skoru` kolonu dolu.

### 2. Sektor Expression Whitespace → ✅ COZULDU
Code node icinde validSectors listesi ile cozuldu. Gelen sektor valid degilse otomatik "Diger" yaziliyor.

---

## AKTIF EKSIKLER

### 4. Duplicate Kayit Kontrolu Yok
**Sorun:** Ayni lead 2 kez gelirse 2 satir olusuyor.
**Denenen:** n8n'de Get Many + IF ile kontrol denendi, bos sonuc IF'i tetiklemedi.
**Kalici cozum:** NocoDB'de email bazli unique constraint veya workflow'da farkli kontrol yontemi.

### 10. Lead Skoru ile Otomatik Asama Belirleme
**Sorun:** Skor hesaplaniyor ama asama hala webhook'tan geldigi gibi kaydediliyor.
**Hedef:** Skor bazli otomatik asama atama:
- 76-100 puan → Cok Sicak → Seyma HEMEN arasin
- 51-75 puan → Sicak → Seyma bugun arasin
- 26-50 puan → Ilik → Takip Agent kovalasin
- 0-25 puan → Soguk → Beklesin
**Durum:** Skor artik NocoDB'de. Sirada IF node'u skor bazli calisacak sekilde guncellenecek.

### 11. Slowdays Privacy Policy Sayfasi Yok
**Sorun:** Meta Lead Ads formu gizlilik politikasi URL'si istiyor. Su an `slowdaysai.com` ana sayfasi kullaniliyor ama bu profesyonel degil, KVKK/GDPR uyumsuz.
**Yapilmali:**
- `slowdaysai.com/privacy` sayfasi olusturulmali
- KVKK (Turk yasasi) + GDPR (AB yasasi) uyumlu gizlilik metni hazirlanmali
- Meta Lead Ads formunda URL guncellenecek
**Onerilen araclar:**
- termly.io (10 dk ucretsiz generator)
- privacypolicygenerator.info
- KVKK icin ozel madde: "Verileriniz 6698 sayili KVKK uyarinca islenmektedir"

### 12. Marka Ismi Temizligi (MindID → Slowdays)
**Sorun:** Eski dokumanlar ve workflow'larda hala "MindID" geciyor.
**Yapilmali:**
- Workflow isimleri: "MindID Gunluk Rapor" → "Slowdays Gunluk Rapor" vb.
- Gmail mail baslik/icerik: "Mindid" → "Slowdays"
- NocoDB veri girislerinde MindID referanslari
- Dokumanlar (AGENT-MIMARISI-MASTER.md, HEDEF-KITLE.md vb.)
- Hedef URL: `mindid.shop` → `slowdaysai.com`

---

## DIGER EKSIKLER

### 6. Webhook URL Production
Test: `webhook-test/lead-toplama` | Production: `webhook/lead-toplama`
Clay, Meta form gibi kaynaklar production URL kullanmali.

### 7. Sektor Standartlastirma
Clay "Hospitality" diyor, NocoDB "Otelcilik" bekliyor. Ceviri/mapping katmani lazim.

### 8. Tarih Alanlari
NocoDB `CreatedAt` otomatik doluyor (dogrulandi). Haftalik rapor icin kullaniliyor.

### 13. Email Self-Send Spam Filtresi
**Sorun:** Seyma kendi kendine mail gonderiyor (seymaakrs@gmail.com → seymaakrs@gmail.com), Gmail spam'e dusuruyor.
**Gecici cozum:** Spam'den "Spam degil" olarak isaretle.
**Kalici cozum:** Farkli bir mail adresinden gonder (orn: `bildirim@slowdaysai.com`).

---

## YAPILACAKLAR LISTESI

- [x] NocoDB sektor listesini genislet
- [x] Test verilerini temizle
- [x] Lead skorlama formulu kur
- [x] Sektor expression whitespace duzelt
- [x] Lead skoru NocoDB'ye yazdir
- [x] Haftalik rapor workflow
- [ ] Duplicate kontrolu ekle
- [ ] Lead skoru ile otomatik asama belirleme
- [ ] Slowdays privacy policy sayfasi olustur
- [ ] MindID → Slowdays marka temizligi
- [ ] DNS + SSL (nocodb.slowdaysai.com)
- [ ] Kullanici rolleri (Seyma, Beyza, Burak)
- [ ] Clay → Webhook tam otomasyonu
- [ ] Meta Ads form → Webhook entegrasyonu (form hazir, webhook baglanmali)
- [ ] Claude API entegrasyonu (kisisellesirilmis mesaj)
- [ ] WhatsApp bildirim (Seyma icin anlik)
- [ ] Domain isinmasi baslat (email outreach icin)
- [ ] Sektor standartlastirma (Clay → NocoDB mapping)
- [ ] Bildirim mail adresini degistir (spam onleme)
