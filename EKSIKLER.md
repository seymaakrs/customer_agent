# EKSIKLER VE GERI DONULECEKLER
**Son guncelleme:** 12 Nisan 2026

---

## COZULMUS ✅

### 1. NocoDB Sektor Listesi → ✅ COZULDU
NocoDB arayuzunden 15 sektor eklendi. Workflow'da sektor field'i hala sabit "Diger" — expression whitespace sorunu cozulunce dinamik yapilacak.

### 3. Test Verileri → ✅ COZULDU
Test kayitlari temizlendi.

### 5. Lead Skorlama → ✅ KISMI COZUM
Skor hesaplanıyor ve mailde gorunuyor. Ama asagidaki 2 eksik var.

---

## AKTIF EKSIKLER

### 2. Sektor Expression Whitespace Sorunu
**Sorun:** n8n expression'inda "Diger" yazildiginda `"Diger "` (sondaki bosluk) uretiyor.
**Gecici cozum:** Sektor field'i sabit "Diger" olarak yazildi.
**Kalici cozum:** n8n'de trim() veya farkli expression yontemi denenmeli.

### 4. Duplicate Kayit Kontrolu Yok
**Sorun:** Ayni lead 2 kez gelirse 2 satir olusuyor.
**Denenen:** n8n'de Get Many + IF ile kontrol denendi, bos sonuc IF'i tetiklemedi.
**Kalici cozum:** NocoDB'de email bazli unique constraint veya workflow'da farkli kontrol yontemi.

### 9. Lead Skoru NocoDB'ye Yazilmiyor
**Sorun:** Code node'da skor hesaplaniyor, mailde gorunuyor ama NocoDB lead_skoru kolonu bos kaliyor.
**Denenen:** Code node icinde fetch() ile NocoDB API cagrisi denendi, n8n sandbox engelliyor.
**Kalici cozum:** Code node'dan sonra ayri bir NocoDB Update node eklenip, lead_skoru alani guncellenecek. Dikkat: baglantilari bozmadan eklenmeli.

### 10. Lead Skoru ile Otomatik Asama Belirleme
**Sorun:** Skor hesaplaniyor ama asama hala elle belirleniyor (webhook'tan gelen deger).
**Hedef:** Skor bazli otomatik asama atama:
- 76-100 puan → Cok Sicak → Seyma HEMEN arasin
- 51-75 puan → Sicak → Seyma bugun arasin
- 26-50 puan → Ilik → Takip Agent kovalasin
- 0-25 puan → Soguk → Beklesin
**Onkosul:** Once #9 cozulmeli (skor NocoDB'ye yazilmali). Sonra IF node'u skor bazli calisacak sekilde guncellenecek.

---

## DIGER EKSIKLER

### 6. Webhook URL Production
Test: `webhook-test/lead-toplama` | Production: `webhook/lead-toplama`
Clay, Meta form gibi kaynaklar production URL kullanmali.

### 7. Sektor Standartlastirma
Clay "Hospitality" diyor, NocoDB "Otelcilik" bekliyor. Ceviri/mapping katmani lazim.

### 8. Tarih Alanlari
NocoDB'de olusturma/guncelleme tarihi otomatik doluyor mu kontrol edilmeli.

---

## YAPILACAKLAR LISTESI

- [x] NocoDB sektor listesini genislet
- [x] Test verilerini temizle
- [x] Lead skorlama formulu kur (mailde calisiyor)
- [ ] Sektor expression whitespace duzelt
- [ ] Duplicate kontrolu ekle
- [ ] Lead skoru NocoDB'ye yazdir
- [ ] Lead skoru ile otomatik asama belirleme
- [ ] DNS + SSL (nocodb.mindid.shop)
- [ ] Kullanici rolleri (Seyma, Beyza, Burak)
- [ ] Clay → Webhook tam otomasyonu
- [ ] Meta Ads form → Webhook entegrasyonu
- [ ] Claude API entegrasyonu (kisisellesirilmis mesaj)
- [ ] WhatsApp bildirim (Seyma icin anlik)
- [ ] Domain isinmasi baslat (email outreach icin)
- [ ] Sektor standartlastirma (Clay → NocoDB mapping)
