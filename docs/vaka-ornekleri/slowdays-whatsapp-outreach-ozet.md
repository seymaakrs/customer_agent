# Slowdays Otel WhatsApp Cold Outreach — Vaka Özeti

> Kaynak repo `slowdays-reklam-agent-handoff` kaldırılmadan önce süzülen vaka özeti. Tarih: 2026-06-07.
>
> Bu doküman, daha önce gerçekten çalıştırılmış bir B2B WhatsApp outreach kampanyasının
> operasyon desenini ve öğrenilen dersleri içerir. Ham kod ve credential bilerek dışarıda
> bırakılmıştır — amaç tekrar edilebilir "operasyon reçetesi" + hata listesidir.

---

## 1. Kampanyanın Amacı

- **Marka:** Slowdays AI (Bodrum merkezli AI destekli reklam/yazılım ajansı).
- **Hedef:** Bodrum / Marmaris / Fethiye / Göcek bölgesindeki küçük-orta otel sahiplerine
  dijital hizmet paketi satmak (B2B).
- **Satış açısı:** "Büyük zincirler kapalı/sınırlı; küçük otelin yılı bu sezon. Dijitalde görün,
  sezonu kazan." Zamanlama: Mayıs 2026, sezon açılışı + bayram öncesi.
- **Ölçek:** Google Places'ten toplanan ve skorlanmış **331 otel** master listesi.
- **Kanal:** Onaylı WhatsApp template ile toplu cold outreach (asıl aktif kanal). Meta Ads
  (Awareness + Conversion) ayrıca planlanmış ama görsel/pixel beklediği için duraklatılmış.

---

## 2. Nasıl Çalıştı (Mimari / Akış)

İki ayrı arka plan süreci paralel koştu:

### 2.1 Gönderim Worker (outreach)
1. Master CSV listesinden otelleri okur.
2. Gönderim log'undan daha önce `SENT` olanları çıkarır (resume / kaldığı yerden devam).
3. Her oteli **tek tek** onaylı WhatsApp template'i ile gönderir (`{{1}}` = otel adı).
4. Her gönderimi önce log'a yazar, sonra ekrana basar (print çökse bile log korunur).
5. Günlük limit dolunca veya mesai bitince durur; ertesi gün restart ile devam eder.

### 2.2 Lead Monitor + Auto-Reply
1. Her 60 saniyede CRM'deki kişileri tarar.
2. Bizim gönderdiğimiz listeden olup yanıt veren + daha önce yakalanmamış kişiyi tespit eder.
3. CRM'de `hot_lead` ve `yaniti_var` etiketi ekler.
4. 30-60 sn insan-benzeri gecikmeden sonra **3 yanıt varyantından rastgele birini** otomatik
   gönderir (şablon-spam görünmesin diye), `oto_yanit_gonderildi` etiketler.
5. Yanıtı `inbound_log`'a yazar; aynı kişiye tekrar yanıt vermemek için dedupe yapar.
6. Müşteri otomatik 2. mesaja tekrar cevap verirse → **insan devralır** (kapanışı Şeyma yapar).

### Mesaj sıralaması (cold lead sequence)
+1 saat / +24 saat / +3 gün / +7 gün takip ritmi tasarlandı.

---

## 3. Kullanılan Parametreler (reçete)

| Parametre | Değer | Neden |
|---|---|---|
| Mesai saatleri | 09:00 – 21:00 | Doğal/insan saatleri; gece gönderim yok |
| Mesajlar arası gecikme | 25–90 sn random | İnsan davranışı taklidi, anti-spam |
| Batch | 20 mesajda bir 4–7 dk mola | Ritmi insancıllaştır, throttle |
| Günlük limit | 240 / 24h | WhatsApp TIER_250'ye 10 buffer'lı |
| Retry | başarısızda 2 kez, 30 sn arayla | Geçici API/ağ hatalarını yut |
| Resume | log'daki `SENT` kayıtları atla | Restart'ta tekrar göndermeyi önle |
| Monitor polling | 60 sn | Yanıtları yakalama sıklığı |
| Auto-reply gecikme | 30–60 sn random | Botvari anında cevap görünmesin |
| Auto-reply varyant | 3 farklı metin, rastgele | Şablon spam algısını azalt |
| Temiz çıkış | Ctrl+C → mevcut mesaj bitince dur | Veri/log bütünlüğü |

**CRM etiket taksonomisi** (yeniden kullanılabilir): segment (butik_otel/pansiyon/villa/zincir),
bölge (bodrum/marmaris/fethiye/göcek/dalaman), sıcaklık (hot/warm/cold/dead_lead),
aksiyon (demo_istedi/teklif_gonderildi/fiyat_sordu/...), bütçe katmanı, sezon, kaynak, kampanya,
otomasyon (oto_yanit_gonderildi/yaniti_var/manual_review).

---

## 4. Ne Öğrenildi

- **Resume + "önce log, sonra print" deseni çalıştı:** Arka plan süreci güvenle restart edilebildi,
  hiçbir otele iki kez mesaj gitmedi. CSV log'u sürecin kalıcı durumu (state) oldu.
- **İnsan-benzeri throttling işe yaradı:** Random gecikme + batch mola + mesai saatleri ile WhatsApp
  hesabının quality rating'i korundu (RED'e düşmeden gönderim sürdü).
- **Otomatik yanıtta varyasyon önemli:** Tek sabit metin yerine 3 varyantın rastgele seçilmesi
  şablon-spam algısını düşürdü; yanıt verene 30-60 sn sonra dönmek doğal hissettirdi.
- **Net insan-devralma sınırı:** "2. mesaja müşteri tekrar yazarsa insan devralır" kuralı,
  otomasyonun nerede biteceğini netleştirdi — kapanış her zaman insanda kaldı.
- **API keşif maliyeti:** Bazı endpoint'ler 404 verdi (deneme-yanılma ile doğru path bulundu);
  doğru çalışan endpoint listesi sonraki agent için zaman kazandırdı.

---

## 5. Tekrarlanırsa Dikkat Edilecekler

### 5.1 GÜVENLİK DERSİ (en kritik)
- **Anti-pattern:** API anahtarı (`ZERNIO_API_KEY`) hem worker hem monitor script'ine
  **hardcoded gömülüydü**. Bu anahtarın koda/repoya girmesi ciddi bir güvenlik açığıdır.
- **Doğrusu:** Anahtar yalnızca ortam değişkeninden (`os.environ` / `.env` + secret manager)
  okunmalı; repoya asla commit edilmemeli. Sızan anahtar derhal **rotate** edilmeli.
- Bu repoyu süzerken anahtar bilerek kopyalanmadı; eski repo kaldırıldığında anahtar da gitmeli,
  ayrıca güvenlik için rotate edilmesi önerilir.

### 5.2 Operasyonel
- **Tek log dosyasına bağımlılık:** Resume mantığı log CSV'sine güvenir. Log silinir/bozulursa
  tekrar gönderim olur. Log dosyasını silme/düzenleme; yedekle.
- **Limit/quality izleme:** İlk 24 saat sonra reply-rate, varyant performansı ve WhatsApp quality
  rating'i kontrol edilmeli (RED riski). TIER limiti aşılmamalı.
- **Windows'a özgü kod:** `stdout.reconfigure(encoding='utf-8')` gibi parçalar platform bağımlıydı;
  taşınırken sadeleştirilmeli.
- **MCP yerine direct curl gibi geçici çözümler:** O dönem MCP entegrasyonu 401 verdiği için doğrudan
  HTTP kullanıldı. Bu geçici bir workaround'tu; kalıcı sistemde düzgün entegrasyon tercih edilmeli.
- **KVKK/izin:** Cold B2B outreach'te izin/şikâyet riski var; opt-out yolu ve template onayı şart.

---

## 6. Bu Sistemin Mevcut Mimariye Bağlantısı

- WhatsApp hesabı (`WA_ACCOUNT_ID 69ecc2273a63baf2053dfc21`) mind-agent'taki Zernio entegrasyonuyla
  aynı hattır. Bu standalone script'lerin yaptığı iş, kalıcı sistemde `mind-agent` içindeki
  prospecting + outreach + auto-reply agent'larına taşınmalıdır (script → SDK geçişi).
- Lead yaşam döngüsü ve "qualified + uygun kaynak/aşama → bildirim" kuralı mind-agent'ta zaten
  tanımlı; bu kampanya o akışın elle yapılmış erken bir prototipidir.
