"""Lead pipeline saf fonksiyonlari: normalize, skor, segment, takip tarihi.

Skor kurallari CLAUDE.md / n8n workflow'larindan birebir tasindi.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

SEKTOR_ENUM = [
    "Otelcilik", "Yeme-Icme", "Perakende", "Turizm", "E-ticaret",
    "Tekne-Yat", "Emlak", "Spa-Wellness", "Doktor-Uzman", "Koc-Egitmen",
    "Kurumsal-Kamu", "Butik-Moda", "Kafe", "Restoran", "Diger",
]

# Serbest metin -> enum eslesmesi (lowercase, ascii'lestirilmis anahtarlar)
_SEKTOR_ALIASES = {
    "otel": "Otelcilik", "otelcilik": "Otelcilik", "hotel": "Otelcilik",
    "yeme-icme": "Yeme-Icme", "yeme icme": "Yeme-Icme", "food": "Yeme-Icme",
    "perakende": "Perakende", "retail": "Perakende",
    "turizm": "Turizm", "tourism": "Turizm",
    "e-ticaret": "E-ticaret", "eticaret": "E-ticaret", "e ticaret": "E-ticaret",
    "ecommerce": "E-ticaret",
    "tekne": "Tekne-Yat", "yat": "Tekne-Yat", "tekne-yat": "Tekne-Yat",
    "emlak": "Emlak", "gayrimenkul": "Emlak",
    "spa": "Spa-Wellness", "wellness": "Spa-Wellness", "spa-wellness": "Spa-Wellness",
    "doktor": "Doktor-Uzman", "uzman": "Doktor-Uzman", "doktor-uzman": "Doktor-Uzman",
    "koc": "Koc-Egitmen", "egitmen": "Koc-Egitmen", "koc-egitmen": "Koc-Egitmen",
    "kurumsal": "Kurumsal-Kamu", "kamu": "Kurumsal-Kamu", "kurumsal-kamu": "Kurumsal-Kamu",
    "butik": "Butik-Moda", "moda": "Butik-Moda", "butik-moda": "Butik-Moda",
    "kafe": "Kafe", "cafe": "Kafe",
    "restoran": "Restoran", "restaurant": "Restoran",
    "diger": "Diger",
}

_TR_MAP = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")

SOURCE_BASE_SCORE = {
    "Meta Ads": 25,
    "Site": 20,
    "Clay": 15,
    "LinkedIn": 15,
    "IG DM": 10,
    "WhatsApp": 10,
    "Manuel": 5,
}

TARGET_SEKTORLER = {"Otelcilik", "Yeme-Icme", "Turizm", "Spa-Wellness"}
TARGET_KONUMLAR = {"bodrum", "marmaris", "fethiye", "datca", "gocek"}

SEGMENT_TAKIP_GUN = {"Sicak": 1, "Ilik": 3, "Soguk": 7, "Nurture": 14}
SEGMENT_ASAMA = {"Sicak": "Sicak", "Ilik": "Ilik", "Soguk": "Yeni", "Nurture": "Yeni"}
SEGMENT_PIPELINE = {"Sicak": "takip", "Ilik": "takip", "Soguk": "takip", "Nurture": "takip"}


def _ascii_lower(s: str) -> str:
    return s.translate(_TR_MAP).strip().lower()


def normalize_telefon(telefon: str | None) -> str | None:
    """Turkiye telefonunu E.164'e cevirir (+90...)."""
    if not telefon:
        return None
    digits = re.sub(r"\D", "", telefon)
    if not digits:
        return None
    if digits.startswith("0090"):
        digits = digits[4:]
    elif digits.startswith("90") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return "+90" + digits
    # TR kalibina uymuyorsa oldugu gibi + ile sakla
    return "+" + digits


def normalize_sektor(sektor: str | None) -> str:
    if not sektor:
        return "Diger"
    s = sektor.strip()
    if s in SEKTOR_ENUM:
        return s
    key = _ascii_lower(s)
    if key in _SEKTOR_ALIASES:
        return _SEKTOR_ALIASES[key]
    for alias, enum_val in _SEKTOR_ALIASES.items():
        if alias in key:
            return enum_val
    return "Diger"


def normalize_butce(butce) -> int | None:
    if butce is None or butce == "":
        return None
    digits = re.sub(r"\D", "", str(butce))
    return int(digits) if digits else None


def normalize_lead(data: dict) -> dict:
    """Ham payload -> tek Turkce sema."""
    def clean(v):
        return v.strip() if isinstance(v, str) and v.strip() else None

    email = clean(data.get("email"))
    return {
        "source": clean(data.get("source")) or "Manuel",
        "external_id": data["external_id"].strip(),
        "leadgen_id": clean(data.get("leadgen_id")),
        "ad_soyad": data["ad_soyad"].strip(),
        "email": email.lower() if email else None,
        "telefon": normalize_telefon(clean(data.get("telefon"))),
        "sirket_adi": clean(data.get("sirket_adi")),
        "sektor": normalize_sektor(clean(data.get("sektor"))),
        "konum": clean(data.get("konum")),
        "butce": normalize_butce(data.get("butce")),
        "mesaj": clean(data.get("mesaj")),
        "raw": data.get("raw") or {},
    }


def score_lead(lead: dict) -> int:
    skor = SOURCE_BASE_SCORE.get(lead["source"], 5)

    sektor = lead.get("sektor") or "Diger"
    if sektor in TARGET_SEKTORLER:
        skor += 20
    elif sektor != "Diger":
        skor += 10

    konum = _ascii_lower(lead.get("konum") or "")
    if any(k in konum for k in TARGET_KONUMLAR):
        skor += 15
    elif "mugla" in konum:
        skor += 10

    butce = lead.get("butce")
    if butce in (15000, 30000):
        skor += 15
    elif butce == 5000:
        skor += 5

    return max(0, min(100, skor))


def segment_for_score(skor: int) -> str:
    if skor >= 60:
        return "Sicak"
    if skor >= 40:
        return "Ilik"
    if skor >= 20:
        return "Soguk"
    return "Nurture"


def asama_for_segment(segment: str) -> str:
    return SEGMENT_ASAMA[segment]


def takip_tarihi_for_segment(segment: str, today: date | None = None) -> date:
    today = today or date.today()
    return today + timedelta(days=SEGMENT_TAKIP_GUN[segment])


def enrich_lead(lead: dict, today: date | None = None) -> dict:
    """Normalize edilmis lead'e skor/segment/asama/takip alanlarini ekler."""
    skor = score_lead(lead)
    segment = segment_for_score(skor)
    return {
        **lead,
        "lead_skoru": skor,
        "segment": segment,
        "asama": asama_for_segment(segment),
        "pipeline_asamasi": SEGMENT_PIPELINE[segment],
        "takip_tarihi": takip_tarihi_for_segment(segment, today),
    }
