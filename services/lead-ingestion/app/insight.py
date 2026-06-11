"""AI satis notu. OpenAI varsa LLM, yoksa/deterministik sablon. Asla ingestion'i bloklamaz."""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("lead-ingestion.insight")


def _template_note(lead: dict) -> str:
    parca = []
    if lead.get("sektor") and lead["sektor"] != "Diger":
        parca.append(f"{lead['sektor']} sektorunden")
    if lead.get("konum"):
        parca.append(f"{lead['konum']} konumundan")
    kim = " ".join(parca) or "yeni"
    butce = f", belirtilen butce {lead['butce']} TL" if lead.get("butce") else ""
    return (
        f"{lead['ad_soyad']} {kim} bir lead ({lead['source']} kanali, skor "
        f"{lead['lead_skoru']}/100, segment {lead['segment']}){butce}. "
        f"Onerilen takip tarihi: {lead['takip_tarihi']}."
    )


async def generate_sales_note(lead: dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _template_note(lead)
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = (
            "Asagidaki lead icin Turkce, 2-3 cumlelik somut bir satis notu yaz. "
            "Sektor, konum ve butceyi dikkate al; satis ekibine yaklasim onerisi ver.\n"
            f"Ad: {lead['ad_soyad']}\nSirket: {lead.get('sirket_adi') or '-'}\n"
            f"Sektor: {lead['sektor']}\nKonum: {lead.get('konum') or '-'}\n"
            f"Butce: {lead.get('butce') or '-'}\nKaynak: {lead['source']}\n"
            f"Skor: {lead['lead_skoru']}/100 ({lead['segment']})\n"
            f"Mesaj: {lead.get('mesaj') or '-'}"
        )
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            timeout=15,
        )
        note = (resp.choices[0].message.content or "").strip()
        return note or _template_note(lead)
    except Exception as exc:  # AI hatasi ingestion'i durdurmaz
        logger.warning("AI satis notu uretilemedi, sablona dusuldu: %s", exc)
        return _template_note(lead)
