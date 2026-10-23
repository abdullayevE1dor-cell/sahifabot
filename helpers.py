"""Kutubxonasiz yordamchi funksiyalar: jadval, tur tanlash, matn tozalash."""
import datetime as dt
import json
import random
import re
from zoneinfo import ZoneInfo

WEIGHTS = {"news": 20, "edu": 25, "tip": 18, "promo": 9, "quiz": 10, "demo": 12, "video": 8}


def make_slots(day: dt.date, n: int, start="08:00", end="22:30", tz="Asia/Tashkent", seed=None):
    """Kun ichida n ta vaqtni teng taqsimlab, biroz tasodifiy siljitib beradi."""
    z = ZoneInfo(tz)
    s = dt.datetime.combine(day, dt.time.fromisoformat(start), z)
    e = dt.datetime.combine(day, dt.time.fromisoformat(end), z)
    step = (e - s).total_seconds() / n
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        center = s.timestamp() + step * i + step / 2
        out.append(dt.datetime.fromtimestamp(center + rnd.uniform(-.3, .3) * step, z))
    return out


def pick_kind(rnd: random.Random, counts: dict, last: list, per_day: int = 12, allowed=None):
    """Post turini tanlaydi: reklama va viktorina haddan oshmasin, bir tur ketma-ket takrorlanmasin."""
    w = dict(WEIGHTS)
    cap = max(2, per_day // 6)
    for k in ("promo", "quiz", "demo", "video"):
        if counts.get(k, 0) >= cap:
            w[k] = 0
    if allowed is not None:
        for k in list(w):
            if k not in allowed:
                w[k] = 0
    if len(last) >= 2 and last[0] == last[1] and last[0] in w:
        w[last[0]] = 0
    kinds = [k for k, v in w.items() if v > 0]
    return rnd.choices(kinds, [w[k] for k in kinds])[0]


_ALLOWED = r"(?:b|i|u|s|code|pre|a)"
_BAD_TAG = re.compile(r"</?(?!" + _ALLOWED + r"\b)[a-zA-Z][^>]*>")
_ANY_TAG = re.compile(r"<[^>]+>")


def sanitize_html(text: str) -> str:
    """Telegram qo'llamaydigan HTML teglarni olib tashlaydi."""
    text = text.replace("```", "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = _BAD_TAG.sub("", text)
    return text.strip()


def strip_tags(text: str) -> str:
    return _ANY_TAG.sub("", text)


def clip_text(text: str, limit: int = 3500) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def extract_json(text: str):
    """Model javobidan birinchi JSON obyektini ajratib oladi."""
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def pick_least_used(keys: list, used: dict, rnd: random.Random):
    """Eng uzoq vaqt ishlatilmagan (yoki umuman ishlatilmagan) elementning tartib raqamini tanlaydi."""
    oldest = min(used.get(k, 0) for k in keys)
    cands = [i for i, k in enumerate(keys) if used.get(k, 0) == oldest]
    return rnd.choice(cands)
