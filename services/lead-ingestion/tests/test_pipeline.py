from datetime import date

from app.pipeline import (
    asama_for_segment,
    enrich_lead,
    normalize_lead,
    normalize_sektor,
    normalize_telefon,
    score_lead,
    segment_for_score,
    takip_tarihi_for_segment,
)

TODAY = date(2026, 6, 11)


def base_payload(**over):
    p = {"source": "Meta Ads", "external_id": "ext-1", "ad_soyad": "Ali Veli"}
    p.update(over)
    return p


# --- normalize ---

def test_telefon_e164():
    assert normalize_telefon("0541 931 55 50") == "+905419315550"
    assert normalize_telefon("05419315550") == "+905419315550"
    assert normalize_telefon("905419315550") == "+905419315550"
    assert normalize_telefon("+90 541 931 55 50") == "+905419315550"
    assert normalize_telefon("5419315550") == "+905419315550"
    assert normalize_telefon(None) is None
    assert normalize_telefon("") is None


def test_sektor_enum_mapping():
    assert normalize_sektor("Otelcilik") == "Otelcilik"
    assert normalize_sektor("otel") == "Otelcilik"
    assert normalize_sektor("Restoran") == "Restoran"
    assert normalize_sektor("yeme içme") == "Yeme-Icme"
    assert normalize_sektor("bilinmeyen sey") == "Diger"
    assert normalize_sektor(None) == "Diger"


def test_normalize_lead_trims_and_lowercases():
    lead = normalize_lead(base_payload(email="  Ali@EXAMPLE.com ", konum=" Bodrum ", butce="15.000 TL"))
    assert lead["email"] == "ali@example.com"
    assert lead["konum"] == "Bodrum"
    assert lead["butce"] == 15000
    assert lead["sektor"] == "Diger"


# --- scoring ---

def test_score_meta_hot():
    lead = normalize_lead(base_payload(sektor="Otelcilik", konum="Bodrum", butce=30000))
    # 25 + 20 + 15 + 15 = 75
    assert score_lead(lead) == 75


def test_score_site_base():
    lead = normalize_lead(base_payload(source="Site"))
    assert score_lead(lead) == 20


def test_score_other_sources():
    for src, expected in [("Clay", 15), ("LinkedIn", 15), ("IG DM", 10), ("WhatsApp", 10), ("Manuel", 5)]:
        assert score_lead(normalize_lead(base_payload(source=src))) == expected


def test_score_non_target_sektor_and_mugla():
    lead = normalize_lead(base_payload(source="Manuel", sektor="Emlak", konum="Milas, Mugla"))
    # 5 + 10 + 10 = 25
    assert score_lead(lead) == 25


def test_score_butce_5000():
    lead = normalize_lead(base_payload(source="Manuel", butce="5000"))
    assert score_lead(lead) == 10


def test_score_clamped_0_100():
    lead = normalize_lead(base_payload(sektor="Otelcilik", konum="Bodrum", butce=30000))
    assert 0 <= score_lead(lead) <= 100


# --- segment / asama / takip ---

def test_segments():
    assert segment_for_score(60) == "Sicak"
    assert segment_for_score(59) == "Ilik"
    assert segment_for_score(40) == "Ilik"
    assert segment_for_score(39) == "Soguk"
    assert segment_for_score(20) == "Soguk"
    assert segment_for_score(19) == "Nurture"


def test_asama_mapping():
    assert asama_for_segment("Sicak") == "Sicak"
    assert asama_for_segment("Ilik") == "Ilik"
    assert asama_for_segment("Soguk") == "Yeni"
    assert asama_for_segment("Nurture") == "Yeni"


def test_takip_tarihi():
    assert takip_tarihi_for_segment("Sicak", TODAY) == date(2026, 6, 12)
    assert takip_tarihi_for_segment("Ilik", TODAY) == date(2026, 6, 14)
    assert takip_tarihi_for_segment("Soguk", TODAY) == date(2026, 6, 18)
    assert takip_tarihi_for_segment("Nurture", TODAY) == date(2026, 6, 25)


def test_enrich_lead_end_to_end():
    lead = enrich_lead(
        normalize_lead(base_payload(sektor="Turizm", konum="Fethiye", butce=15000)), TODAY
    )
    assert lead["lead_skoru"] == 75
    assert lead["segment"] == "Sicak"
    assert lead["asama"] == "Sicak"
    assert lead["pipeline_asamasi"] == "takip"
    assert lead["takip_tarihi"] == date(2026, 6, 12)
