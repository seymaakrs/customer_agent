# YAPILACAKLAR — ONCELIK SIRASI

## KATEGORI 1: HEMEN YAPILMALI (Bu Hafta)

### P1. Meta Ads Form → Webhook Baglantisi
- **Neden oncelikli:** Gunluk 150 lead buradan gelecek (en buyuk hacim)
- **Gereksinimler:** Meta Business Manager hesabi, aktif reklam kampanyasi
- **Yapilacak:** Meta lead form → n8n webhook (lead-toplama) bagla
- **Sonuc:** Form dolduran kisi otomatik CRM'e duser + Sicaksa Seyma'ya mail

### P2. NocoDB Sektor Listesini Genislet
- **Neden oncelikli:** Workflow'da "Diger" sabit yazili, yeni sektorler taninamıyor
- **Yapilacak:** NocoDB arayuzunden sektor kolonuna yeni secenekler ekle
- **Secenekler:** Tekne-Yat, Emlak, Spa-Wellness, Doktor-Uzman, Koc-Egitmen, Kurumsal-Kamu, Butik-Moda, Kafe, Restoran
- **Sonuc:** Her sektor dogru kayit edilir

### P3. Duplicate Kayit Kontrolu
- **Neden oncelikli:** Ayni lead 2 kez gelirse 2 satir olusuyor
- **Yapilacak:** Lead Toplama workflow'una "once kontrol et, varsa guncelle" mantigi ekle
- **Sonuc:** Temiz veri, duplike yok

### P4. Test Verilerini Temizle
- **Neden oncelikli:** NocoDB'de 17+ test kaydi var, gercek verilerle karisir
- **Yapilacak:** Test Lead, Ahmet Yilmaz (duplike), Test Sicak gibi kayitlari sil
- **Sonuc:** Temiz CRM

---

## KATEGORI 2: BU HAFTA ICINDE

### P5. Itiraz Agent Workflow
- **Neden oncelikli:** Lead gelince "pahali" diyene otomatik cevap
- **Gereksinimler:** Claude API veya GPT API key
- **Yapilacak:** n8n workflow: mesaj geldi → anahtar kelime tara → AI ile cevap yaz → gonder
- **Sonuc:** Itirazlar otomatik karsilanir

### P6. Gunluk Rapor Workflow
- **Neden oncelikli:** Her gun 23:00'te Seyma'ya ozet gitsin
- **Yapilacak:** Schedule Trigger (23:00) → NocoDB'den istatistik cek → Email gonder
- **Icerik:** Bugunku yeni lead, mesaj, yanit, sicak lead, kapanis sayilari
- **Sonuc:** Gunluk performans takibi

### P7. Clay → Webhook Tam Otomasyon
- **Neden oncelikli:** Clay'dan lead'ler otomatik aksin
- **Secenekler:**
  - A: Claude MCP uzerinden (sen tetiklersin)
  - B: Haftalik CSV export + n8n import workflow
  - C: Clay upgrade ($149/ay) → tam otomatik
- **Onerilen:** B ile basla, ciro artinca C'ye gec

### P8. DNS + SSL (nocodb.mindid.shop)
- **Neden:** Profesyonel gorunum, guvenli erisim
- **Yapilacak:** DNS A kaydi + Certbot SSL + Nginx HTTPS
- **Sonuc:** http://34.26.138.196 yerine https://nocodb.mindid.shop

### P9. Kullanici Rolleri
- **Yapilacak:** NocoDB'ye Seyma (Owner), Beyza (Owner), Burak (Editor) ekle
- **Sonuc:** Ekip CRM'e erisir

---

## KATEGORI 3: GELECEK HAFTA

### P10. DM Bot Agent (Instagram/TikTok)
- **Gereksinimler:** ManyChat hesabi veya Instagram API
- **Yapilacak:** Yeni takipci → otomatik hosgeldin mesaji → bilgi topla → webhook → CRM
- **Sonuc:** IG/TikTok'tan gunluk 40 lead

### P11. LinkedIn Agent (Alternatif Yol)
- **Gercek:** LinkedIn API mesaj gondermeye izin vermiyor
- **Alternatif:** Clay/Phantombuster ile lead listesi cek → email outreach
- **Yapilacak:** Clay'dan lead bul → email yaz (AI ile) → gonder → CRM takip
- **Sonuc:** LinkedIn kaynakli gunluk 30 lead (email uzerinden)

### P12. Email Outreach Sistemi
- **Gereksinimler:** mindid.shop domain isinmasi (SPF/DKIM/DMARC)
- **Yapilacak:** n8n workflow: CRM'den lead cek → Claude API kisisellestirmis email yaz → Gmail/SMTP ile gonder
- **Dikkat:** Gunluk 10 ile basla, yavas artir (ban onleme)
- **Sonuc:** Otomatik kisisellestirmis email outreach

### P13. WhatsApp Bildirim
- **Gereksinimler:** WhatsApp Business API
- **Yapilacak:** Sicak lead gelince email yerine (veya yaninda) WhatsApp bildirimi
- **Sonuc:** Seyma aninda gorur, mail kutusuna bakmak zorunda kalmaz

### P14. Lead Skorlama Sistemi
- **Yapilacak:** n8n'de Code node ile skor hesapla
- **Kriterler:** Sektor eslesmesi (+20), Pozisyon CEO/GM (+15), Konum Bodrum (+10), Form doldurdu (+25), Mesaja yanit verdi (+20)
- **Sonuc:** Her lead 0-100 puan, Seyma oncelikli olanlara odaklanir

---

## KATEGORI 4: 2-3 HAFTA ICINDE

### P15. Meta Ads Agent (Kampanya Yonetimi)
- **Yapilacak:** n8n workflow: Meta API'den kampanya verilerini cek → CTR/CPC/CPL kontrol → otomatik durdur/basla
- **Sonuc:** Reklam optimizasyonu yari-otomatik

### P16. A/B Test Yonetimi
- **Yapilacak:** Meta'da 2 farkli reklam → 48 saat sonra otomatik karsilastir → kazanani sec
- **Sonuc:** Reklam performansi surekli iyilesir

### P17. Upsell Agent
- **Yapilacak:** Mevcut musterilere 30 gun sonra otomatik upgrade teklifi
- **Sonuc:** Mevcut musterilerden ek gelir

### P18. Referans Agent
- **Yapilacak:** "Arkadasini getir %10 indirim" otomatik takibi
- **Sonuc:** Organik buyume

### P19. Haftalik Performans Raporu
- **Yapilacak:** Her Cuma otomatik haftalik ozet
- **Icerik:** Haftalik lead, kapanis, ciro, en iyi kanal, sapma analizi
- **Sonuc:** Stratejik karar alma

### P20. NocoDB Marka Ozellestirmesi
- **Yapilacak:** Logo, renk, baslik degistirme (Docker rebuild)
- **Sonuc:** "NocoDB" yerine "MindID LAB" gorunumu

---

## ZAMAN CIZELGESI

```
HAFTA 1 (Su an):  P1-P4  → Temel eksikleri kapat
HAFTA 2:          P5-P9  → Itiraz, rapor, Clay, DNS, roller
HAFTA 3:          P10-P14 → DM Bot, LinkedIn, Email, WhatsApp, Skorlama
HAFTA 4:          P15-P20 → Meta optimizasyon, Upsell, Referans, Branding
```

## BASARI OLCUTU

Her hafta sonu kontrol:
- Gunluk 300 lead hedefine ne kadar yakiniz?
- Kac sicak lead Seyma'ya ulasti?
- Kac teklif gonderildi?
- Kac kapanis yapildi?
- Haftalik 60K TL hedefine ne kadar yakiniz?
