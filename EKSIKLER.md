# EKSIKLER VE GERI DONULECEKLER

## Acil Cozulmesi Gereken Sorunlar

### 1. NocoDB Sektor Listesi Tam Degil
**Sorun:** Sektor alaninda sadece 6 secenek var: Otelcilik, Yeme-Icme, Perakende, Turizm, E-ticaret, Diger

**Eksik sektorler (hedef kitlemize gore):**
- Tekne-Yat
- Emlak
- Spa-Wellness
- Doktor-Uzman
- Koc-Egitmen
- Kurumsal-Kamu
- Butik-Moda
- Kafe
- Restoran

**Gecici cozum:** Lead Toplama Agent workflow'unda sektor field'i sabit "Diger" olarak yazildi.

**Kalici cozum:** NocoDB arayuzunden sektor kolonunun secenek listesini el ile genisletip, workflow'daki expression'i tekrar dinamik yapmak.

### 2. Sektor Expression Whitespace Sorunu
n8n expression'inda kosul sonrasinda "Diger" yazildiginda n8n cikti olarak `"Diger "` (sondaki bosluk) uretiyordu. Bu muhtemelen n8n'in expression parser hatasi. Sektor listesi genisletilince tekrar denenmeli.

### 3. Test Verileri NocoDB'de Fazla
Leadler tablosunda 11 test kaydi var. Production'a gecmeden once bunlar temizlenmeli.

### 4. Duplicate Kayit Kontrolu Yok
Webhook'a ayni lead 2 kere gelirse 2 satir olusuyor. NocoDB'de email bazli unique kontrol eklenmeli veya workflow'a "önce kontrol et, varsa guncelle" mantigi eklenmeli.

### 5. Lead Skorlama Yok
Simdilik sadece `asama` alanina bakiyoruz (Sicak/Ilik). Gercek lead skorlama (sektor, pozisyon, konum, butce bazli puanlama) yok.

---

## Sonraki Workflow'larda Lazim Olacaklar

### 6. Webhook URL Production Guncel
Test ederken `webhook-test/lead-toplama` kullandik. Production'da `webhook/lead-toplama` olacak. Clay, Meta form gibi kaynaklarin bu production URL'e veri gondermesi gerekiyor.

### 7. Sektor Standartlastirma
Clay'dan gelen veri "Hospitality" diyebilir, NocoDB "Otelcilik" bekliyor. Ceviri/mapping katmani lazim.

### 8. Tarih Alanlari Bos
NocoDB'de olusturma tarihi, guncelleme tarihi gibi alanlar otomatik doluyor mu kontrol edilmeli.

---

## Gelecek Hafta Yapilacaklar

- [ ] NocoDB sektor listesini genislet (manuel)
- [ ] Duplicate kontrolu ekle
- [ ] Lead skorlama formulu kur
- [ ] Test verilerini temizle
- [ ] DNS + SSL (nocodb.mindid.shop)
- [ ] Kullanici rolleri (Seyma, Beyza, Burak)
- [ ] Clay → Webhook otomasyonu
- [ ] Meta Ads form → Webhook entegrasyonu
- [ ] Claude API entegrasyonu (kisisellesirilmis mesaj)
- [ ] WhatsApp bildirim (Seyma icin anlik)
- [ ] Domain isinmasi baslat (email outreach icin)
