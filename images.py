"""Rasm (kartochka) va animatsiya (GIF) yasash. Faqat Pillow kerak, pulsiz."""
import base64
import io
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from logo_data import LOGO_B64

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "DejaVuSans-Bold.ttf")
INK = (16, 35, 58); SUN = (255, 201, 60); WHITE = (255, 255, 255); GRAY = (238, 242, 247)
STYLE = {"edu": ((30, 140, 200), "TA\u02bcLIM"), "tip": ((30, 150, 95), "MASLAHAT"),
         "promo": ((214, 96, 24), "XIZMAT"), "news": ((66, 84, 214), "YANGILIK"),
         "quiz": ((118, 84, 222), "VIKTORINA"), "demo": ((30, 140, 200), "NAMUNA")}


def F(size):
    return ImageFont.truetype(FONT, size)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def gradient(w, h, c1, c2):
    mask = Image.linear_gradient("L").resize((w, h))
    return Image.composite(Image.new("RGB", (w, h), c2), Image.new("RGB", (w, h), c1), mask)


def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if font.getlength(t) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def fit(text, maxw, maxh, hi=104, lo=44):
    for size in range(hi, lo - 1, -4):
        f = F(size)
        lines = wrap(text, f, maxw)
        if len(lines) * size * 1.18 <= maxh and all(f.getlength(l) <= maxw for l in lines):
            return f, lines, size
    f = F(lo)
    return f, wrap(text, f, maxw)[:6], lo


def logo_circle(size):
    return Image.open(io.BytesIO(base64.b64decode(LOGO_B64))).convert("RGBA").resize((size, size), Image.LANCZOS)


def make_card(kind, headline, handle="@sahifabot_bot"):
    """1080x1080 JPEG kartochka. Qaytaradi: bytes."""
    acc, label = STYLE.get(kind, STYLE["edu"])
    W = H = 1080
    base = gradient(W, H, (10, 20, 36), mix((10, 20, 36), acc, .45)).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(glow)
    d.ellipse((600, -200, 1200, 400), fill=acc + (130,)); d.ellipse((-250, 650, 450, 1350), fill=acc + (90,))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(base)
    d.ellipse((760, 90, 1000, 330), outline=WHITE + (45,), width=14)
    chip_w = int(F(36).getlength(label)) + 64
    d.rounded_rectangle((80, 100, 80 + chip_w, 172), 36, fill=SUN)
    d.text((80 + 32, 112), label, font=F(36), fill=INK)
    f, lines, size = fit(headline.strip(), 880, 540)
    y = 260 + (540 - int(len(lines) * size * 1.18)) // 2
    for l in lines:
        d.text((80, y), l, font=f, fill=WHITE)
        y += int(size * 1.18)
    d.rounded_rectangle((80, y + 18, 80 + 130, y + 30), 6, fill=SUN)
    base.alpha_composite(logo_circle(104), (80, 890))
    d.text((208, 896), "sahifabot", font=F(46), fill=WHITE)
    d.text((208, 952), handle, font=F(30), fill=(190, 210, 230))
    buf = io.BytesIO()
    base.convert("RGB").save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()


def _bubble(text, me, acc, font):
    lines = wrap(text, font, 470)
    tw = int(max(font.getlength(l) for l in lines)); lh = int(font.size * 1.25)
    w, h = tw + 52, lh * len(lines) + 34
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=(acc if me else GRAY) + (255,))
    for i, l in enumerate(lines):
        d.text((26, 17 + i * lh), l, font=font, fill=WHITE if me else INK)
    return im


def make_dialog_gif(title, msgs, cta="Sizga ham shunday bot kerakmi?", acc=(30, 140, 200), handle="@sahifabot_bot"):
    """720x720 animatsiyali GIF: bot va mijoz yozishmasi. msgs: [("me"|"bot", matn), ...]. Qaytaradi: bytes."""
    S = 720
    font = F(28)
    base = gradient(S, S, mix((255, 255, 255), acc, .10), (246, 249, 252)).convert("RGBA")
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, S, 104), fill=acc + (255,))
    base.alpha_composite(logo_circle(64), (28, 20))
    d.text((108, 18), title, font=F(34), fill=WHITE)
    d.text((108, 62), "namuna \u00b7 online", font=F(22), fill=(225, 240, 250))
    bubbles = [_bubble(t, side == "me", acc, font) for side, t in msgs]
    ys, y = [], 128
    for b in bubbles:
        ys.append(y); y += b.height + 18

    def xpos(i, b):
        return S - 36 - b.width if msgs[i][0] == "me" else 36

    def compose(shown, pop=None, typing=None, ribbon=0.0, dots=0):
        fr = base.copy()
        for i in range(shown):
            fr.alpha_composite(bubbles[i], (xpos(i, bubbles[i]), ys[i]))
        if pop:
            i, k = pop
            b = bubbles[i].copy(); b.putalpha(b.getchannel("A").point(lambda v: int(v * (.35 + .65 * k))))
            fr.alpha_composite(b, (xpos(i, b), ys[i] + int(20 * (1 - k))))
        if typing is not None:
            tb = Image.new("RGBA", (120, 56), (0, 0, 0, 0)); td = ImageDraw.Draw(tb)
            td.rounded_rectangle((0, 0, 119, 55), 28, fill=GRAY + (255,))
            for q in range(3):
                on = (dots % 3) == q
                td.ellipse((26 + q * 28, 20 - (5 if on else 0), 44 + q * 28, 38 - (5 if on else 0)), fill=(110, 125, 145, 255))
            fr.alpha_composite(tb, (36, ys[typing]))
        if ribbon > 0:
            ry = S - int(92 * ribbon)
            rd = ImageDraw.Draw(fr)
            rd.rectangle((0, ry, S, S), fill=INK + (255,))
            rd.text((36, ry + 14), cta, font=F(28), fill=WHITE)
            rd.text((36, ry + 52), handle, font=F(24), fill=SUN)
        return fr.convert("RGB")

    frames, durs = [], []
    def add(fr, ms=84):
        frames.append(fr.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)); durs.append(ms)
    for i, (side, _) in enumerate(msgs):
        if side == "bot":
            for k in range(8):
                add(compose(i, typing=i, dots=k))
        else:
            for _ in range(4):
                add(compose(i))
        for k in (.25, .6, .85, 1.0):
            add(compose(i, pop=(i, k)))
        for _ in range(6):
            add(compose(i + 1))
    for k in (.3, .6, .85, 1.0):
        add(compose(len(msgs), ribbon=k))
    add(compose(len(msgs), ribbon=1.0), 2600)
    buf = io.BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=False)
    return buf.getvalue()
