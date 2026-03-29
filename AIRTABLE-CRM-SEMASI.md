# AIRTABLE CRM SEMASI — MINDID AGENT SISTEMI

**Tarih:** 29 Mart 2026
**Amac:** Tum 6 agentin tek bulusma noktasi. Her lead, her etkilesim, her asama burada izlenir.

---

## TABLO 1: LEADLER (Ana Tablo)

> Her lead = 1 satir. Tum agentlar bu tabloya yazar.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `lead_id` | Auto Number | Benzersiz lead numarasi | 1001 |
| `ad_soyad` | Single Line Text | Kisinin tam adi | Ahmet Yilmaz |
| `email` | Email | E-posta adresi | ahmet@otel.com |
| `telefon` | Phone Number | Telefon numarasi | +90 532 XXX XX XX |
| `sirket_adi` | Single Line Text | Isletme / sirket adi | Bodrum Beach Hotel |
| `pozisyon` | Single Line Text | Unvan | Genel Mudur |
| `sektor` | Single Select | Faaliyet alani | Otelcilik / Yeme-Icme / Perakende / Turizm / E-ticaret / Diger |
| `konum` | Single Line Text | Sehir / ilce | Bodrum |
| `web_sitesi` | URL | Isletme web sitesi | https://bodrumbeach.com |
| `instagram` | Single Line Text | IG hesabi | @bodrumbeachhotel |
| `linkedin_url` | URL | LinkedIn profil linki | https://linkedin.com/in/ahmetyilmaz |
| `google_puani` | Number (1 decimal) | Google Maps puani | 4.3 |
| `kaynak` | Single Select | Lead nereden geldi | LinkedIn / Meta Ads / Clay / IG DM / TikTok DM / Referans / Manuel |
| `asama` | Single Select | Satis asamasi (pipeline) | Yeni / Soguk / Ilik / Sicak / Teklif / Sozlesme / Kazanildi / Kayip / Arsiv |
| `lead_skoru` | Number | 0-100 arasi oncelik puani | 75 |
| `ihtiyac_notu` | Long Text | Tespit edilen ihtiyac | Web sitesi yok, SM zayif |
| `atanan_kisi` | Single Line Text | Sorumlu (Seyma veya agent) | Seyma |
| `olusturma_tarihi` | Created Time | Kayit tarihi | 2026-03-29 14:30 |
| `son_guncelleme` | Last Modified Time | Son degisiklik | 2026-03-30 09:15 |
| `notlar` | Long Text | Genel notlar | Discovery call 1 Nisan'da |

### Lead Skoru Hesaplama Kriterleri:

| Kriter | Puan |
|--------|------|
| Sektor eslesmesi (Otelcilik, Turizm, Yeme-Icme) | +20 |
| Pozisyon (CEO/GM/Sahip) | +15 |
| Pozisyon (Pazarlama Muduru) | +10 |
| Web sitesi yok veya cok zayif | +15 |
| Instagram aktif ama profesyonel degil | +10 |
| Google puani < 4.0 | +10 |
| Konum: Bodrum/Mugla | +10 |
| Mesaja yanit verdi | +20 |
| Form doldurdu (Meta Ads) | +25 |
| 2+ itiraz karsilandi, hala konusuyor | +15 |

**Skor Araliklari:**
- 0-25: Soguk
- 26-50: Ilik
- 51-75: Sicak
- 76-100: Cok Sicak (Seyma oncelikli arasin)

---

## TABLO 2: ETKILESIMLER (Interaction Log)

> Her mesaj, her arama, her temas = 1 satir. Lead ile linked.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `etkilesim_id` | Auto Number | Benzersiz kayit no | 5001 |
| `lead` | Link to Leadler | Hangi lead ile | Ahmet Yilmaz |
| `tarih` | Date + Time | Ne zaman | 2026-03-29 14:30 |
| `kanal` | Single Select | Hangi kanal uzerinden | LinkedIn / Email / WhatsApp / IG DM / TikTok DM / Telefon / Meta Form / Yuz Yuze |
| `yon` | Single Select | Gelen mi giden mi | Giden / Gelen |
| `tur` | Single Select | Ne tipi etkilesim | Baglanti Istegi / Ilk Mesaj / Takip Mesaji / Itiraz Karsilama / Discovery Call / Teklif / Yanit |
| `mesaj_icerigi` | Long Text | Gonderilen/alinan mesaj | "Merhaba Ahmet, isletmeniz icin..." |
| `sonuc` | Single Select | Ne oldu | Yanit Bekleniyor / Olumlu Yanit / Olumsuz Yanit / Itiraz / Soru Sordu / Gorusme Planlandi |
| `agent` | Single Select | Hangi agent yapti | LinkedIn Agent / Meta Agent / Clay Agent / DM Bot / Takip Agent / Itiraz Agent / Seyma |
| `otomatik_mi` | Checkbox | Agent otomatik mi gonderdi | true |
| `notlar` | Long Text | Ek aciklama | "Pahali dedi, itiraz scripti #3 uygulandi" |

---

## TABLO 3: ITIRAZLAR

> Her itiraz ayrı kaydedilir. Itiraz Agent bu tabloyu okur/yazar.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `itiraz_id` | Auto Number | Benzersiz kayit no | 3001 |
| `lead` | Link to Leadler | Hangi lead | Ahmet Yilmaz |
| `tarih` | Date + Time | Ne zaman geldi | 2026-03-29 |
| `itiraz_turu` | Single Select | Kategori | Fiyat / Erteleme / Rekabet / Olcek / Teknoloji / Kanit / Diger |
| `itiraz_metni` | Long Text | Musterinin dedigi | "Butcemize uygun degil" |
| `karsilama_scripti` | Single Line Text | Hangi script kullanildi | Script #3 - Fiyat/Deger |
| `karsilama_metni` | Long Text | Gonderilen cevap | "Anlasilabilir. 2.999 TL deneme..." |
| `sonuc` | Single Select | Karsilama sonrasi | Ikna Oldu / Devam Ediyor / Kayip / Eskalasyon (Seyma) |
| `eskalasyon` | Checkbox | Seyma'ya mi yonlendirildi | false |

---

## TABLO 4: TAKIP KUYRUĞU

> Takip Agent bu tabloyu surekli tarar. Otomatik takip zamanlayicisi.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `takip_id` | Auto Number | Benzersiz kayit no | 4001 |
| `lead` | Link to Leadler | Hangi lead | Ahmet Yilmaz |
| `son_iletisim_tarihi` | Date | En son ne zaman mesaj gitti | 2026-03-27 |
| `takip_sayisi` | Number | Kac kez takip yapildi | 2 |
| `sonraki_takip_tarihi` | Date | Ne zaman takip yapilacak | 2026-03-29 |
| `takip_asamasi` | Single Select | Hangi adimda | 48s Takip / 96s Takip / 7g Son Mesaj / Arsiv / Telefon Listesi |
| `denenen_kanallar` | Multiple Select | Hangi kanallar denendi | LinkedIn, Email, IG DM |
| `sonraki_kanal` | Single Select | Siradaki denenecek kanal | WhatsApp |
| `durum` | Single Select | Aktif mi | Aktif / Tamamlandi / Arsivlendi |

### Takip Zamanlama Kurallari:

```
Takip 1 → Son iletisimden 48 saat sonra → Farkli kanal
Takip 2 → Son iletisimden 96 saat sonra → Deneme paketi vurgula
Takip 3 → Son iletisimden 7 gun sonra → "Son firsat" mesaji
Takip 4 → 14 gun sonra → Soguk Arsiv'e al, 60 gun sonra tekrar aktif et
```

---

## TABLO 5: KAMPANYALAR (Meta Ads)

> Meta Reklam Agent bu tabloyu yonetir. Kampanya performans takibi.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `kampanya_id` | Auto Number | Benzersiz kayit no | 2001 |
| `kampanya_adi` | Single Line Text | Meta'daki kampanya adi | Bodrum Otel Q2 2026 |
| `platform` | Single Select | Reklam platformu | Facebook / Instagram / Her Ikisi |
| `baslangic_tarihi` | Date | Ne zaman basladi | 2026-03-29 |
| `bitis_tarihi` | Date | Ne zaman bitiyor | 2026-04-05 |
| `gunluk_butce` | Currency (TRY) | Gunluk harcama limiti | 500 TL |
| `toplam_harcama` | Currency (TRY) | Simdiye kadar harcanan | 1.250 TL |
| `erisim` | Number | Toplam erisim | 12.500 |
| `tiklanma` | Number | Toplam tik | 340 |
| `ctr` | Percent | Tiklanma orani | %2.7 |
| `cpc` | Currency (TRY) | Tik basina maliyet | 3.68 TL |
| `lead_sayisi` | Number | Toplanan lead | 18 |
| `cpl` | Currency (TRY) | Lead basina maliyet | 69 TL |
| `durum` | Single Select | Kampanya durumu | Aktif / Durduruldu / A/B Test / Tamamlandi |
| `en_iyi_reklam` | Single Line Text | En iyi performans | Gorsel A - Video |
| `notlar` | Long Text | Optimizasyon notlari | "CTR dusuk, gorsel degistirildi" |

---

## TABLO 6: GUNLUK RAPORLAR

> Her gun 23:00'te otomatik olusur. Genel performans takibi.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `rapor_id` | Auto Number | Benzersiz kayit no | 6001 |
| `tarih` | Date | Hangi gunun raporu | 2026-03-29 |
| `yeni_lead_toplam` | Number | O gun eklenen lead | 35 |
| `yeni_lead_linkedin` | Number | LinkedIn'den gelen | 12 |
| `yeni_lead_meta` | Number | Meta Ads'den gelen | 8 |
| `yeni_lead_clay` | Number | Clay'den gelen | 10 |
| `yeni_lead_dm` | Number | DM Bot'tan gelen | 5 |
| `mesaj_gonderilen` | Number | Toplam gonderilen mesaj | 52 |
| `yanit_alinan` | Number | Toplam gelen yanit | 7 |
| `itiraz_gelen` | Number | Gelen itiraz sayisi | 3 |
| `itiraz_karsilanan` | Number | Basarili karsilama | 2 |
| `sicak_lead` | Number | Sicak'a yukselttilen | 4 |
| `discovery_call` | Number | Yapilan gorusme | 1 |
| `teklif_gonderilen` | Number | Gonderilen teklif | 1 |
| `kapanis` | Number | Kapanan satis | 0 |
| `gelir` | Currency (TRY) | O gunun geliri | 0 TL |
| `toplam_gelir` | Currency (TRY) | Kumulatif toplam gelir | 29.000 TL |
| `reklam_harcama` | Currency (TRY) | O gunun reklam gideri | 500 TL |
| `notlar` | Long Text | Gunun ozeti | "LinkedIn'den 2 sicak lead geldi" |

---

## TABLO 7: PIPELINE (Satis Hunisi)

> Seyma'nin gorecegi ana gorunum. Teklif → Sozlesme → Para akisi.

| Alan Adi | Tip | Aciklama | Ornek |
|----------|-----|----------|-------|
| `firsat_id` | Auto Number | Benzersiz kayit no | 7001 |
| `lead` | Link to Leadler | Hangi lead | Ahmet Yilmaz |
| `firsat_adi` | Single Line Text | Firsat basligi | Bodrum Beach Hotel - Web + SM |
| `paket` | Single Select | Teklif edilen paket | Deneme (2.999) / Starter (7.500) / Growth (14.900) / Premium (29.000) / Enterprise (Ozel) |
| `tutar` | Currency (TRY) | Teklif tutari | 29.000 TL |
| `asama` | Single Select | Pipeline asamasi | Discovery Call / Teklif Hazirlik / Teklif Gonderildi / Muzakere / Sozlesme / Kazanildi / Kayip |
| `discovery_tarihi` | Date | Gorusme tarihi | 2026-04-01 |
| `teklif_tarihi` | Date | Teklif gonderim tarihi | 2026-04-02 |
| `beklenen_kapanis` | Date | Tahmini kapanis | 2026-04-05 |
| `kapanis_tarihi` | Date | Gercek kapanis tarihi | — |
| `kayip_nedeni` | Single Select | Neden kaybedildi | — / Fiyat / Rakip / Zamanlama / Ihtiyac Yok / Iletisim Kesildi |
| `notlar` | Long Text | Gorusme notlari | "2 paket arasi kararsiz" |

---

## GORUNUM (VIEW) ONERILERI

### Leadler Tablosu Gorunumleri:
| Gorunum | Filtre | Kullanan |
|---------|--------|----------|
| **Tum Leadler** | Filtre yok | Genel bakis |
| **Bugunun Leadleri** | `olusturma_tarihi = bugun` | Gunluk kontrol |
| **Sicak Leadler** | `asama = Sicak` veya `lead_skoru >= 51` | Seyma (oncelikli) |
| **Takip Bekleyenler** | `asama = Soguk VEYA Ilik` + `son iletisim > 48 saat` | Takip Agent |
| **Itiraz Edenler** | Son etkilesim sonucu = Itiraz | Itiraz Agent |
| **Kaynak Bazli** | `kaynak` grupla | Performans analizi |
| **Kanban Board** | `asama` bazli sutunlar | Pipeline gorunumu |

### Pipeline Tablosu Gorunumleri:
| Gorunum | Filtre | Kullanan |
|---------|--------|----------|
| **Aktif Pipeline** | `asama != Kazanildi/Kayip` | Seyma |
| **Bu Hafta Kapanis** | `beklenen_kapanis = bu hafta` | Seyma (oncelikli) |
| **Kazanilan** | `asama = Kazanildi` | Gelir takibi |

---

## TABLO ILISKILERI (LINKED RECORDS)

```
LEADLER (1) ←→ (N) ETKILESIMLER
LEADLER (1) ←→ (N) ITIRAZLAR
LEADLER (1) ←→ (N) TAKIP KUYRUGU
LEADLER (1) ←→ (N) PIPELINE
KAMPANYALAR (1) ←→ (N) LEADLER (kaynak = Meta Ads olan)
GUNLUK RAPORLAR — bagimsiz (rollup/formula ile hesaplanir)
```

---

## OTOMASYON TETIKLEYICILERI (Airtable Automations)

| # | Tetikleyici | Aksiyon |
|---|-------------|---------|
| 1 | Lead skoru >= 51 olunca | `asama` → "Sicak" yap + Seyma'ya bildirim |
| 2 | Yeni lead eklenince | Lead skorunu hesapla + Takip kuyruGuna ekle |
| 3 | `asama` = "Kazanildi" olunca | Pipeline'da kapanis tarihini yaz + gelir guncelle |
| 4 | 48 saat yanit yok | Takip Agent'a tetikle (n8n webhook) |
| 5 | Itiraz tespit edilince | Itiraz Agent'a tetikle (n8n webhook) |
| 6 | Her gun 23:00 | Gunluk rapor satirini otomatik olustur |

---

## SONRAKI ADIMLAR

- [ ] Airtable'da tablolari olustur
- [ ] Field tiplerini ve Single Select opsiyonlarini gir
- [ ] View'lari kur (Kanban, filtrelenmis listeler)
- [ ] Otomasyon tetikleyicilerini aktif et
- [ ] n8n webhook URL'lerini Airtable otomasyonlarina bagla
- [ ] Test: 5 ornek lead gir, tum akisi kontrol et
