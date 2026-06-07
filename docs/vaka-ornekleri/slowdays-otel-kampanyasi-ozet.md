# Vaka Çalışması: Slowdays AI — Otel Cold Outreach (B2B)

> Bodrum bölgesi küçük/orta otel sahiplerine dijital hizmet satışı kampanyası.
> Mayıs 2026. Bu doküman **case study** olarak tutulur: planın nasıl kurulduğu,
> B2B davranışı ve istatistiksel sonuçlar. Operasyonel detay, script ve sırlar
> alınmadı (artık kullanılmıyor). Amaç: gelecek prospecting kampanyaları için ders.

---

## 1. Konumlandırma (neden işe yaradı)

- **Hedef:** Bodrum / Marmaris / Fethiye / Göcek'te **küçük-orta otel sahipleri** (B2B).
- **Strateji açısı:** *"Büyük zincirler kapalı/sınırlı — küçük otelin yılı bu sezon.
  Dijitalde görün, sezonu kazan."*
- **Mevsimsel aciliyet:** yaz sezonu açılışı + bayram öncesi gönderim.
- **Ders:** yerel + mevsimsel + "rakibin zayıf, sıra sende" çerçevesi soğuk mesajda
  açılma oranını artırır. Jenerik "dijital pazarlama yapalım" değil, sektöre özel acı.

---

## 2. Plan: 3 Paralel Kanal

| Kanal | Rol | Bütçe |
|---|---|---|
| WhatsApp toplu cold outreach | Birebir, en yüksek dönüşüm | template bazlı, 331 otel |
| Meta Ads — Awareness (Reels) | Marka bilinirliği | ~200 TL/gün |
| Meta Ads — Conversion (Lead Form / CTW) | Lead toplama | ~400 TL/gün (240 Lead Form + 160 CTW hibrit) |

**Ders (B2B + Meta):** Meta'da "otel sahibi" doğrudan hedeflenemez →
**lokasyon + interest + iş ünvanı** kombinasyonu kurulur. Pixel/thank-you sayfası
hazır değilse **Lead Form** on-platform çalışır, pixel gerektirmez (hızlı başlangıç).

---

## 3. Satış Hunisi (5 adım) + Takip Cadence'i

1. Karşılama + niyet (otel tipi, lokasyon).
2. Mevcut durum (reklam/sosyal medya aktif mi).
3. Acı noktası (doluluk / Booking komisyonu / direct booking).
4. Çözüm (3 paket: Başlangıç / Sezon / Premium).
5. Randevu / demo kapama.

**Cold lead takip:** `+1 saat → +24 saat → +3 gün → +7 gün`.

---

## 4. İstatistiksel Sonuçlar (handoff anı, 2026-05-09 ~16:50)

| Metrik | Değer |
|---|---|
| Master listedeki otel | **331** |
| O gün gönderilen (yarım gün) | ~42 |
| Yanıt veren | 2 (İde Beach Home, Bono Residence) |
| Anlık yanıt oranı | ~%4.8 (42 gönderim / 2 yanıt) |

**Yorum:** İlk yarım günde ~%5 yanıt oranı, soğuk WhatsApp B2B için makul bir başlangıç
sinyali. Asıl ölçüm 24 saat sonrası reply rate + varyant performansı ile yapılmalı.
Küçük örneklemde tek bir yanıt oranı %2-3 oynatır; karar için minimum 1 günlük veri şart.

---

## 5. Davranışsal Öğrenimler (tekrar kullanılabilir)

1. **Throttle = hayatta kalma:** mesaj arası 25-90 sn random, her 20 batch'te 4-7 dk mola,
   sadece 09:00-21:00, günlük ~240 limit. Toplu WhatsApp'ta asıl risk teknik değil
   **Quality rating düşüşü** (RED olursa hat yanar) — onaylı template + throttle pazarlıksız.
2. **İdempotent gönderim:** gönderim log'undan resume → restart'ta duplicate yok
   (mind-agent `upsert_lead` external_id felsefesiyle aynı).
3. **İnsan devralma sınırı:** müşteri otomatik 2. mesaja **3. mesajla** cevap verirse bot
   susar, insan devralır. → Qualifier **mail kapısı**nın davranışsal atası.
4. **ICP doğrulaması:** kampanya hedefi (Bodrum otelcilik) `mind-agent/src/tools/sales/icp.py`
   içindeki hedef sektör/konum listesiyle birebir örtüşür — ICP seçimimiz sahada denenmiş.

---

## 6. Meta Otel Interest ID'leri (referans)

| Interest ID | Ad | ~Erişim |
|---|---|---|
| `6003147405549` | Boutique hotel | ~18M |
| `6003572379887` | Oteller / konaklama | ~603M |
| `6777460559594` | Seyahat Acenteleri ve Rezervasyon | ~850k |
| `6003359052437` | Hospitality management studies | ~10M |
| `6003240159610` | İkram sektörü | ~41M |
| `6002884511422` | Küçük işletme | ~177M |

Coğrafi: Bodrum/Marmaris/Fethiye/Göcek 25 km · Yaş 28-58 · Dil TR.
