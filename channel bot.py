"""
sahifabot kanalini mustaqil yurituvchi bot.

Ikki rejim:
  - API kalitsiz (tekin): tayyor kontent bazasi (content_bank.py) aylanma tartibda joylanadi.
  - ANTHROPIC_API_KEY bilan: yangilikni topib, Claude orqali oʻzbekcha yozadi (pullik).
Har postga rasm (kartochka) yoki animatsiya (GIF) avtomatik yasaladi.

MODE=review -> post avval adminga tasdiqqa keladi (tavsiya etiladi)
MODE=auto   -> toʻgʻridan-toʻgʻri kanalga chiqadi
"""
import asyncio
import html
import json
import logging
import os
import random
import re
import sqlite3
import time
import datetime as dt
from zoneinfo import ZoneInfo

import feedparser
import httpx
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import (BufferedInputFile, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, LinkPreviewOptions, Message)
from dotenv import load_dotenv

import content_bank as bank
from content import (EDU_PROMPT, FEEDS, KEYWORDS, NEWS_PROMPT, PROMO_PROMPT, PROMO_TYPES,
                     QUIZ_PROMPT, SYSTEM, TIP_PROMPT, TOPICS)
from helpers import (clip_text, extract_json, make_slots, pick_kind, sanitize_html, strip_tags)
from images import make_card, make_dialog_gif

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL = os.getenv("CHANNEL_ID", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
MODE = os.getenv("MODE", "review").lower()
PER_DAY = int(os.getenv("POSTS_PER_DAY", "12"))
TZNAME = os.getenv("TIMEZONE", "Asia/Tashkent")
START = os.getenv("WINDOW_START", "08:00")
END = os.getenv("WINDOW_END", "22:30")
BOT_USERNAME = os.getenv("BOT_USERNAME", "sahifabot_bot").lstrip("@")
INSTAGRAM = os.getenv("INSTAGRAM_HANDLE", "sahifabot").lstrip("@")
DB_PATH = os.getenv("DB_PATH", "kanal.db")
MODEL = os.getenv("LLM_MODEL", "claude-haiku-5-5")
USE_AI = bool(os.getenv("ANTHROPIC_API_KEY"))
ENABLE_NEWS = USE_AI or os.getenv("ENABLE_NEWS", "0") == "1"   # tarjimasiz yangilik: sarlavha + havola
TZ = ZoneInfo(TZNAME)
VIDEO_DIR = os.getenv("VIDEO_DIR", "videos")

ai = None
if USE_AI:
    from anthropic import AsyncAnthropic
    ai = AsyncAnthropic()

log = logging.getLogger("kanal")
router = Router()

# ------------------------------------------------------------------ BAZA
db = sqlite3.connect(DB_PATH)
db.executescript("""
CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, topic TEXT, url TEXT,
    text TEXT, poll TEXT, media_type TEXT, media BLOB, status TEXT DEFAULT 'draft', day TEXT,
    created INTEGER, posted INTEGER);
CREATE TABLE IF NOT EXISTS slots(day TEXT, idx INTEGER, ts INTEGER, done INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0, PRIMARY KEY(day, idx));
CREATE TABLE IF NOT EXISTS seen(url TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS topics_used(topic TEXT PRIMARY KEY, used INTEGER);
CREATE TABLE IF NOT EXISTS bank_used(k TEXT PRIMARY KEY, used INTEGER);
CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT);
""")
db.commit()

def kv_get(k, default=""):
    r = db.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
    return r[0] if r else default

def kv_set(k, v):
    db.execute("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))
    db.commit()

def today() -> dt.date:
    return dt.datetime.now(TZ).date()

def ensure_slots(day: dt.date):
    d = day.isoformat()
    if db.execute("SELECT 1 FROM slots WHERE day=? LIMIT 1", (d,)).fetchone():
        return
    for i, t in enumerate(make_slots(day, PER_DAY, START, END, TZNAME, seed=d)):
        db.execute("INSERT INTO slots(day,idx,ts) VALUES(?,?,?)", (d, i, int(t.timestamp())))
    db.commit()

# ------------------------------------------------------------------ CLAUDE (ixtiyoriy)
async def llm(user: str, max_tokens: int = 900) -> str:
    last_err = None
    for attempt in range(3):
        try:
            r = await ai.messages.create(model=MODEL, max_tokens=max_tokens, system=SYSTEM,
                                         messages=[{"role": "user", "content": user}])
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
        except Exception as e:
            last_err = e
            await asyncio.sleep(2 + attempt * 3)
    raise RuntimeError(f"LLM xatosi: {last_err}")

# ------------------------------------------------------------------ YANGILIKLAR
NEWS: list[dict] = []

async def fetch_news() -> list[dict]:
    items = []
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "sahifabot-kanal/1.0"}) as c:
        for url in FEEDS:
            try:
                r = await c.get(url)
                feed = await asyncio.to_thread(feedparser.parse, r.content)
            except Exception as e:
                log.warning("RSS xato %s: %s", url, e)
                continue
            for e in feed.entries[:20]:
                link, title = e.get("link"), (e.get("title") or "").strip()
                if not link or not title or db.execute("SELECT 1 FROM seen WHERE url=?", (link,)).fetchone():
                    continue
                summary = re.sub(r"<[^>]+>", " ", e.get("summary", ""))
                summary = re.sub(r"\s+", " ", html.unescape(summary)).strip()[:700]
                if any(k in f"{title} {summary}".lower() for k in KEYWORDS):
                    items.append({"title": title, "summary": summary, "link": link})
    random.shuffle(items)
    return items

async def next_news():
    if not NEWS:
        NEWS.extend(await fetch_news())
    if not NEWS:
        return None
    item = NEWS.pop()
    db.execute("INSERT OR IGNORE INTO seen(url) VALUES(?)", (item["link"],))
    db.commit()
    return item

def pick_topic() -> str:
    now = int(time.time())
    used = {t: u for t, u in db.execute("SELECT topic, used FROM topics_used")}
    fresh = [t for t in TOPICS if now - used.get(t, 0) > 30 * 86400]
    topic = random.choice(fresh or TOPICS)
    db.execute("INSERT INTO topics_used(topic,used) VALUES(?,?) ON CONFLICT(topic) DO UPDATE SET used=excluded.used", (topic, now))
    db.commit()
    return topic

# ------------------------------------------------------------------ POST YARATISH
async def finish(kind, topic, text, head=None, url=None, poll=None, gif=None) -> dict:
    mtype = media = None
    if gif:
        mtype, media = "gif", await asyncio.to_thread(make_dialog_gif, gif[0], gif[1], "Sizga ham shunday bot kerakmi?",
                                                      (30, 140, 200), "@" + BOT_USERNAME)
    elif kind != "quiz":
        mtype, media = "photo", await asyncio.to_thread(make_card, kind, head or topic, "@" + BOT_USERNAME)
    return dict(kind=kind, topic=topic, url=url, text=text, poll=poll, media_type=mtype, media=media)

def video_files() -> list:
    if not os.path.isdir(VIDEO_DIR):
        return []
    return sorted(f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(".mp4"))

def make_video_post() -> dict:
    from helpers import pick_least_used
    files = video_files()
    used = dict(db.execute("SELECT k, used FROM bank_used").fetchall())
    keys = [f"video:{f}" for f in files]
    i = pick_least_used(keys, used, random)
    db.execute("INSERT INTO bank_used(k,used) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET used=excluded.used", (keys[i], int(time.time() * 1000)))
    db.commit()
    with open(os.path.join(VIDEO_DIR, files[i]), "rb") as fh:
        data = fh.read()
    text = random.choice(bank.VIDEO_CAPTIONS) + f"\n\n👉 @{BOT_USERNAME}\n📷 Instagram: @{INSTAGRAM}"
    return dict(kind="video", topic=files[i], url=None, text=text, poll=None, media_type="video", media=data)

def from_bank(kind: str) -> dict:
    used = dict(db.execute("SELECT k, used FROM bank_used").fetchall())
    key, post = bank.build(kind, random, used, BOT_USERNAME, INSTAGRAM)
    db.execute("INSERT INTO bank_used(k,used) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET used=excluded.used", (key, int(time.time() * 1000)))
    db.commit()
    return post

async def make_post(kind: str) -> dict:
    if kind == "news" and not ENABLE_NEWS:
        kind = "edu"
    if kind == "video" and not video_files():
        kind = "demo"
    if kind == "video":
        return make_video_post()
    if kind == "demo":
        p = from_bank("demo")
        return await finish("demo", p["head"], p["text"], gif=p["dialog"])
    if kind == "news":
        for _ in range(6):
            item = await next_news()
            if not item:
                break
            link = f'<a href="{html.escape(item["link"], quote=True)}">Batafsil oʻqish</a>'
            if USE_AI:
                txt = await llm(NEWS_PROMPT.format(title=item["title"], summary=item["summary"] or "—"))
                if txt.upper().startswith("SKIP") or len(txt) < 80:
                    continue
                body = sanitize_html(clip_text(txt, 3300)) + f"\n\n🔗 {link}"
            else:
                body = f"📰 <b>{html.escape(item['title'])}</b>\n\n🌐 Dunyo texnologiya yangiliklaridan\n🔗 {link}\n\n#yangiliklar #texnologiya"
            return await finish("news", item["title"][:100], body, head=item["title"], url=item["link"])
        kind = "edu"
    if kind in ("edu", "tip"):
        if USE_AI:
            try:
                topic = pick_topic()
                txt = await llm((EDU_PROMPT if kind == "edu" else TIP_PROMPT).format(topic=topic))
                return await finish(kind, topic, sanitize_html(clip_text(txt, 3500)), head=topic)
            except Exception:
                log.exception("AI ishlamadi, baza ishlatiladi")
        p = from_bank(kind)
        return await finish(kind, p["head"], p["text"], head=p["head"])
    if kind == "promo":
        if USE_AI:
            try:
                ptype = random.choice(PROMO_TYPES)
                txt = sanitize_html(clip_text(await llm(PROMO_PROMPT.format(kind=ptype)), 3300))
                txt += f"\n\n👉 Buyurtma: @{BOT_USERNAME}\n📷 Instagram: @{INSTAGRAM}"
                return await finish("promo", ptype, txt, head=ptype.capitalize())
            except Exception:
                log.exception("AI ishlamadi, baza ishlatiladi")
        p = from_bank("promo")
        return await finish("promo", p["head"], p["text"], head=p["head"])
    # quiz
    if USE_AI:
        try:
            topic = random.choice(TOPICS)
            data = extract_json(await llm(QUIZ_PROMPT.format(topic=topic), 600))
            opts = [str(o)[:95] for o in data["options"]][:4]
            correct = int(data["correct"])
            if len(opts) >= 2 and 0 <= correct < len(opts):
                poll = {"question": str(data["question"])[:290], "options": opts, "correct": correct,
                        "explanation": str(data.get("explanation", ""))[:190]}
                return await finish("quiz", topic, poll["question"], poll=json.dumps(poll, ensure_ascii=False))
        except Exception:
            log.exception("AI viktorina ishlamadi, baza ishlatiladi")
    p = from_bank("quiz")
    return await finish("quiz", p["head"], p["text"], poll=json.dumps(p["poll"], ensure_ascii=False))

def save_post(p: dict) -> int:
    cur = db.execute("INSERT INTO posts(kind,topic,url,text,poll,media_type,media,day,created) VALUES(?,?,?,?,?,?,?,?,?)",
                     (p["kind"], p["topic"], p["url"], p["text"], p["poll"], p["media_type"], p["media"],
                      today().isoformat(), int(time.time())))
    db.commit()
    return cur.lastrowid

def load_post(pid: int) -> dict:
    r = db.execute("SELECT kind,text,poll,media_type,media FROM posts WHERE id=?", (pid,)).fetchone()
    return dict(kind=r[0], text=r[1], poll=r[2], media_type=r[3], media=r[4])

# ------------------------------------------------------------------ YUBORISH
async def _send(fn, **kw):
    try:
        return await fn(**kw)
    except TelegramBadRequest:   # HTML xato boʻlsa, oddiy matn bilan qayta urinamiz
        kw = dict(kw)
        for k in ("caption", "text"):
            if k in kw:
                kw[k] = strip_tags(kw[k])
        kw["parse_mode"] = None
        return await fn(**kw)

async def deliver(bot: Bot, chat_id, p: dict, markup=None, prefix=""):
    text = prefix + p["text"]
    preview = LinkPreviewOptions(is_disabled=(p["kind"] != "news"))
    media, mtype = p.get("media"), p.get("media_type")

    async def send_media(caption=None, kb=None):
        if mtype == "video":
            return await _send(bot.send_video, chat_id=chat_id, video=BufferedInputFile(media, "video.mp4"),
                               caption=caption, reply_markup=kb, supports_streaming=True)
        if mtype == "gif":
            return await _send(bot.send_animation, chat_id=chat_id, animation=BufferedInputFile(media, "demo.gif"),
                               caption=caption, reply_markup=kb)
        return await _send(bot.send_photo, chat_id=chat_id, photo=BufferedInputFile(media, "post.jpg"),
                           caption=caption, reply_markup=kb)

    if media and len(strip_tags(text)) <= 1000:
        await send_media(text, markup)
    else:
        if media:
            await send_media()
        await _send(bot.send_message, chat_id=chat_id, text=text, reply_markup=markup, link_preview_options=preview)

async def publish(bot: Bot, pid: int):
    p = load_post(pid)
    if p["poll"]:
        q = json.loads(p["poll"])
        await bot.send_poll(CHANNEL, question=q["question"], options=q["options"], type="quiz",
                            correct_option_id=q["correct"], explanation=q.get("explanation") or None)
    else:
        await deliver(bot, CHANNEL, p)
    db.execute("UPDATE posts SET status='posted', posted=?, media=NULL WHERE id=?", (int(time.time()), pid))
    db.commit()

def draft_kb(pid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Joylash", callback_data=f"ok:{pid}"),
        InlineKeyboardButton(text="♻️ Qayta", callback_data=f"re:{pid}"),
        InlineKeyboardButton(text="❌ Rad", callback_data=f"no:{pid}")]])

async def send_draft(bot: Bot, pid: int):
    p = load_post(pid)
    head = f"📝 <b>Qoralama #{pid}</b> ({p['kind']})\n\n"
    if p["poll"]:
        q = json.loads(p["poll"])
        opts = "\n".join(("✅ " if i == q["correct"] else "▫️ ") + html.escape(o) for i, o in enumerate(q["options"]))
        await _send(bot.send_message, chat_id=ADMIN_ID, text=f"{head}🧩 <b>Viktorina</b>\n{html.escape(q['question'])}\n\n{opts}",
                    reply_markup=draft_kb(pid))
    else:
        await deliver(bot, ADMIN_ID, p, markup=draft_kb(pid), prefix=head)

def allowed_kinds():
    ks = {"edu", "tip", "promo", "quiz", "demo"}
    if ENABLE_NEWS:
        ks.add("news")
    if video_files():
        ks.add("video")
    return ks

async def run_slot(bot: Bot, kind: str | None = None):
    d = today().isoformat()
    counts = dict(db.execute("SELECT kind, COUNT(*) FROM posts WHERE day=? GROUP BY kind", (d,)).fetchall())
    last = [r[0] for r in db.execute("SELECT kind FROM posts ORDER BY id DESC LIMIT 2")]
    kind = kind or pick_kind(random, counts, last, PER_DAY, allowed_kinds())
    pid = save_post(await make_post(kind))
    if MODE == "auto":
        await publish(bot, pid)
    else:
        await send_draft(bot, pid)

# ------------------------------------------------------------------ REJALASHTIRUVCHI
async def scheduler(bot: Bot):
    while True:
        try:
            if kv_get("paused") != "1":
                now = int(time.time())
                ensure_slots(today())
                row = db.execute("SELECT day,idx,ts,attempts FROM slots WHERE done=0 AND ts<=? ORDER BY ts LIMIT 1", (now,)).fetchone()
                if row:
                    day, idx, ts, attempts = row
                    if now - ts > 1800:   # juda kechikkan boʻlsa, ommaviy yuborib yubormaymiz
                        db.execute("UPDATE slots SET done=1 WHERE day=? AND idx=?", (day, idx))
                    else:
                        try:
                            await run_slot(bot)
                            db.execute("UPDATE slots SET done=1 WHERE day=? AND idx=?", (day, idx))
                        except Exception as e:
                            log.exception("Slot xatosi")
                            attempts += 1
                            db.execute("UPDATE slots SET attempts=?, done=? WHERE day=? AND idx=?",
                                       (attempts, 1 if attempts >= 3 else 0, day, idx))
                            if ADMIN_ID:
                                await bot.send_message(ADMIN_ID, f"⚠️ Post yaratishda xato ({attempts}/3): {str(e)[:300]}", parse_mode=None)
                    db.commit()
        except Exception:
            log.exception("Rejalashtiruvchi xatosi")
        await asyncio.sleep(30)

# ------------------------------------------------------------------ ADMIN
def is_admin(uid: int) -> bool:
    return bool(ADMIN_ID) and uid == ADMIN_ID

@router.message(Command("start"))
async def start(m: Message):
    if is_admin(m.from_user.id):
        await m.answer("Kanal boti ishlayapti.\n/status — bugungi holat\n/plan — bugungi jadval\n"
                       "/now [edu|tip|promo|quiz|demo|video|news] — hozir bitta post\n/pause, /resume — toʻxtatish va davom ettirish")

@router.message(Command("status"))
async def status(m: Message):
    if not is_admin(m.from_user.id):
        return
    d = today().isoformat()
    done = db.execute("SELECT COUNT(*) FROM slots WHERE day=? AND done=1", (d,)).fetchone()[0]
    total = db.execute("SELECT COUNT(*) FROM slots WHERE day=?", (d,)).fetchone()[0]
    posted = db.execute("SELECT COUNT(*) FROM posts WHERE day=? AND status='posted'", (d,)).fetchone()[0]
    wait = db.execute("SELECT COUNT(*) FROM posts WHERE status='draft'").fetchone()[0]
    await m.answer(f"📊 Bugun: {done}/{total} vaqt ishlatildi, kanalga chiqdi: {posted}\nTasdiq kutayotgan qoralamalar: {wait}\n"
                   f"Rejim: {MODE}, kontent: {'AI' if USE_AI else 'tayyor baza'}, "
                   f"{'⏸ toʻxtatilgan' if kv_get('paused') == '1' else '▶️ ishlayapti'}")

@router.message(Command("plan"))
async def plan(m: Message):
    if not is_admin(m.from_user.id):
        return
    rows = db.execute("SELECT ts, done FROM slots WHERE day=? ORDER BY ts", (today().isoformat(),)).fetchall()
    await m.answer("\n".join(f"{'✅' if d else '⏳'} {dt.datetime.fromtimestamp(t, TZ):%H:%M}" for t, d in rows) or "Jadval yoʻq")

@router.message(Command("pause"))
async def pause(m: Message):
    if is_admin(m.from_user.id):
        kv_set("paused", "1"); await m.answer("⏸ Toʻxtatildi")

@router.message(Command("resume"))
async def resume(m: Message):
    if is_admin(m.from_user.id):
        kv_set("paused", "0"); await m.answer("▶️ Davom etmoqda")

@router.message(Command("now"))
async def now_cmd(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id):
        return
    kind = (command.args or "").strip().lower() or None
    if kind not in (None, "news", "edu", "tip", "promo", "quiz", "demo", "video"):
        await m.answer("Tur: edu, tip, promo, quiz, demo, video yoki news")
        return
    await m.answer("Tayyorlanmoqda...")
    try:
        await run_slot(bot, kind)
    except Exception as e:
        await m.answer(f"Xato: {e}", parse_mode=None)

@router.callback_query(F.data.regexp(r"^(ok|re|no):\d+$"))
async def draft_action(c: CallbackQuery, bot: Bot):
    if not is_admin(c.from_user.id):
        await c.answer()
        return
    act, pid = c.data.split(":"); pid = int(pid)
    row = db.execute("SELECT status, kind FROM posts WHERE id=?", (pid,)).fetchone()
    if not row or row[0] != "draft":
        await c.answer("Bu qoralama allaqachon hal qilingan", show_alert=True)
        return
    if act == "ok":
        await publish(bot, pid)
        await c.message.edit_reply_markup(reply_markup=None)
        await c.answer("✅ Kanalga joylandi")
        return
    db.execute("UPDATE posts SET status='rejected', media=NULL WHERE id=?", (pid,)); db.commit()
    await c.message.edit_reply_markup(reply_markup=None)
    if act == "no":
        await c.answer("Rad etildi")
    else:
        await c.answer("Qayta tayyorlanmoqda...")
        await send_draft(bot, save_post(await make_post(row[1])))

async def main():
    if not (TOKEN and CHANNEL):
        raise SystemExit("BOT_TOKEN va CHANNEL_ID kerak. .env faylini tekshiring.")
    if MODE != "auto" and not ADMIN_ID:
        raise SystemExit("review rejimi uchun ADMIN_ID kerak (yoki MODE=auto qoʻying).")
    logging.basicConfig(level=logging.INFO)
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"🚀 Kanal boti ishga tushdi. Rejim: {MODE}, kontent: {'AI' if USE_AI else 'tayyor baza'}, "
                                         f"kuniga {PER_DAY} ta post.")
    asyncio.create_task(scheduler(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
