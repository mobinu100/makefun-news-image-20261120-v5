#!/usr/bin/env python3
"""news-image-20261120 V5 — 'THE WORLD IN ONE DAY'.
Draws the 20 November 2026 front page: giant date masthead, stats strip,
region counts, 3 large visual stories, 10 numbered stories, 17 MORE items,
DATE CHECK box, footer. All facts verified by the author from live reporting.
Deterministic: same bytes every run (fixed layout, no randomness, no time)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 236, 215)
INK = (20, 20, 20)
RED = (160, 28, 28)
GREY = (90, 84, 70)
RULE = (20, 20, 20)

FD = "/usr/share/fonts/truetype"
F_SERIF_B = f"{FD}/dejavu/DejaVuSerif-Bold.ttf"
F_SANS_B = f"{FD}/noto/NotoSans-Bold.ttf"
F_SANS = f"{FD}/noto/NotoSans-Regular.ttf"
F_COND_B = f"{FD}/noto/NotoSans-CondensedBold.ttf"
F_COND = f"{FD}/noto/NotoSans-Condensed.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(draw, text, f):
    return draw.textlength(text, font=f)


def wrap(draw, text, f, maxw):
    """Greedy wrap into lines that fit maxw; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(draw, t, f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


BANNED = ["first-ever", "largest ever", "smashes", "Bigger than Yalta",
          "historic", "record", "groundbreaking", "unprecedented"]

# --- content (every fact verified from live reporting, 21 Nov 2026) ---
MASTHEAD_KICKER = "THE WORLD IN ONE DAY \u00b7 30 STORIES"
MASTHEAD_DATE = "FRIDAY 20 NOVEMBER 2026"

STATS = [
    ("372,000", "EVACUATED"),
    ("950", "DOW POINTS LOST"),
    ("24.6M", "GTA VI COPIES"),
    ("100,000", "YOUTH PLACES"),
    ("9,341", "SHELTERS READY"),
]

REGION_BAR = "ASIA 9 \u00b7 EUROPE 6 \u00b7 AMERICAS 7 \u00b7 AFRICA 1 \u00b7 OCEANIA 2 \u00b7 GLOBAL 5"

# large stories: (num, kicker, headline, deck, scene)
LARGE = [
    (1, "KYIV \u00b7 20 NOV \u00b7 WAR",
     "MISSILES HIT KYIV BRIDGES",
     "8 killed, bridges shut. (Reuters)", "kyiv"),
    (2, "POLAND \u00b7 20 NOV \u00b7 DEFENCE",
     "RUSSIAN MISSILES LAND IN POLAND",
     "No one hurt, NATO alerted. (Reuters)", "poland"),
    (3, "ODISHA \u00b7 20 NOV \u00b7 WEATHER",
     "CYCLONE AKVAN HITS ODISHA",
     "372,000 evacuated to shelters. (IMD)", "cyclone"),
]

# numbered stories 4-13: (num, headline, kicker+deck line)
NUMBERED = [
    (4, "NASDAQ PLUNGES 5.3%",
     "NEW YORK \u00b7 20 NOV \u2014 Erases 2026 gains. (AP)"),
    (5, "UK AND EU SEAL RESET DEAL",
     "BRUSSELS \u00b7 20 NOV \u2014 100,000 places. (Reuters)"),
    (6, "ANTHROPIC SLIDES DAY TWO",
     "WALL ST \u00b7 20 NOV \u2014 Shares fall 8.5%. (Nasdaq)"),
    (7, "DOW DROPS 950 POINTS",
     "NEW YORK \u00b7 20 NOV \u2014 S&P falls 3.7%. (AP)"),
    (8, "TAIWAN SHARES CRASH 6.2%",
     "TAIPEI \u00b7 20 NOV \u2014 Chip rout spreads. (Reuters)"),
    (9, "NIKKEI FALLS 5.1%",
     "TOKYO \u00b7 20 NOV \u2014 Asia rout spreads. (Reuters)"),
    (10, "BITCOIN SINKS BELOW $59K",
     "GLOBAL \u00b7 20 NOV \u2014 7th weekly loss. (CoinDesk)"),
    (11, "COP31 TALKS RUN OVERTIME",
     "ANTALYA \u00b7 20 NOV \u2014 Fossil fuels out. (Reuters)"),
    (12, "KENYA STARTS OIL DRILLING",
     "TURKANA \u00b7 20 NOV \u2014 Rigs start. (Capital FM)"),
    (13, "ITALY STRIKES OVER WAGES",
     "ROME \u00b7 20 NOV \u2014 100 cities protest. (Reuters)"),
]

MORE_HEADER = "ALSO ON FRIDAY 20 NOVEMBER \u2014 17 MORE STORIES"
MORE = [
    "Nvidia falls 14% (WSJ)",
    "AMD falls 13% (Barron's)",
    "GTA 75% PS5 (SensorTower)",
    "GTA 120m hours (Game8)",
    "Seoul impeach (JoongAng)",
    "Phillips 118 (Reuters)",
    "Nicholls 175* (Reuters)",
    "JP CPI 2.3% (Stats Bureau)",
    "423 rescue teams (IMD)",
    "NATO jets up (BBC)",
    "SoftBank -14.5% (CNBC)",
    "Samsung falls 7% (Reuters)",
    "COP31 $120bn cut (Reuters)",
    "2 killed in Haiti (AJ)",
    "Kospi falls 5.2% (Reuters)",
    "11 regions lose power (AP)",
    "Micron -14% (Barron's)",
]

DATE_CHECK = [
    "DATE CHECK \u2014 LEFT OUT:",
    "Summit + ICJ (19 Nov). Anthropic $83 / $111.50 (19 Nov).",
    "\u2018Dems take Congress\u2019 (3 Nov). Voyager 1 (18 Nov).",
    "Hayabusa2 off (17 Nov). Voyager 2 in 2035 (not yet).",
]

FOOTER = [
    "Every story here happened, or was first reported, on Friday, 20 November 2026.",
    "Sources named beside each story.",
]


def check_content():
    """Zero banned hype words in story text; decks <=5 words; counts match."""
    texts = [MASTHEAD_KICKER, MASTHEAD_DATE, REGION_BAR,
             MORE_HEADER] + [s for pair in STATS for s in pair]
    for _, k, h, d, _ in LARGE:
        texts += [k, h, d]
    for _, h, k in NUMBERED:
        texts += [h, k]
    texts += MORE + DATE_CHECK + FOOTER
    for t in texts:
        low = t.lower()
        for b in BANNED:
            assert b not in low, f"banned word {b!r} in {t!r}"
    for _, _, h, d, _ in LARGE:
        deck = d.split("(")[0].strip()
        assert len(deck.split()) <= 5, f"deck too long: {d!r}"
    for _, _, k in NUMBERED:
        deck = k.split("\u2014", 1)[1].split("(")[0].strip()
        assert len(deck.split()) <= 5, f"deck too long: {k!r}"
    assert len(LARGE) + len(NUMBERED) + len(MORE) == 30, "story count"
    assert "30 STORIES" in MASTHEAD_KICKER
    assert "17 MORE STORIES" in MORE_HEADER
    return texts


def draw_scene(draw, kind, x, y, w, h):
    """Simple flat drawn scene for a large story."""
    if kind == "summit":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 32, 64))
        for i, bx in enumerate(range(x + 6, x + w - 18, 30)):
            bh = 12 + (i * 7) % 14
            draw.rectangle([bx, y + h - bh, bx + 20, y + h], fill=(12, 16, 34))
            draw.rectangle([bx + 3, y + h - bh + 3, bx + 7, y + h - bh + 7],
                           fill=(255, 214, 90))
        fx = x + w // 2 - 60
        for j, cols in enumerate([[(180, 30, 30), (255, 255, 255), (30, 60, 160)],
                                  [(200, 20, 20), (255, 220, 0)],
                                  [(255, 255, 255), (30, 60, 160), (200, 20, 20)]]):
            px = fx + j * 42
            draw.rectangle([px, y + 3, px + 2, y + 15], fill=(200, 200, 200))
            for k, c in enumerate(cols):
                draw.rectangle([px + 2, y + 3 + k * 4, px + 24, y + 7 + k * 4], fill=c)
        draw.ellipse([x + 30, y + h - 12, x + w - 30, y + h - 4], fill=(120, 72, 32))
        for j, skin in enumerate([(232, 190, 150), (240, 205, 160), (225, 185, 145)]):
            cx = x + w // 2 - 56 + j * 56
            draw.ellipse([cx - 9, y + h - 30, cx + 9, y + h - 14], fill=skin)
            draw.rectangle([cx - 12, y + h - 16, cx + 12, y + h - 11],
                           fill=[(30, 60, 140), (160, 30, 30), (40, 40, 40)][j])
    elif kind == "kyiv":
        draw.rectangle([x, y, x + w, y + h], fill=(22, 26, 44))
        # distant skyline silhouettes with a few lit windows
        for bx, bh in [(x + 14, 8), (x + 60, 11), (x + 118, 7), (x + 176, 10),
                       (x + 232, 8), (x + 284, 11)]:
            draw.rectangle([bx, y + 2, bx + 24, y + 2 + bh], fill=(14, 17, 30))
            draw.rectangle([bx + 5, y + 5, bx + 8, y + 8], fill=(255, 214, 90))
        # river (Dnipro) along the bottom
        draw.rectangle([x, y + h - 9, x + w, y + h], fill=(46, 78, 118))
        # bridge deck across the river, three arches dipping into the water
        draw.rectangle([x, y + h - 15, x + w, y + h - 13], fill=(150, 150, 160))
        for cx in (x + 55, x + w // 2, x + w - 55):
            draw.arc([cx - 13, y + h - 28, cx + 13, y + h], start=0, end=180,
                     fill=(150, 150, 160), width=2)
        # two explosion bursts on the deck
        for ex, ey in [(x + 55, y + h - 20), (x + w - 55, y + h - 20)]:
            draw.ellipse([ex - 6, ey - 5, ex + 6, ey + 5], fill=(255, 140, 40))
            draw.ellipse([ex - 3, ey - 2, ex + 3, ey + 2], fill=(255, 210, 90))
            draw.ellipse([ex - 9, ey - 10, ex - 1, ey - 4], fill=(120, 120, 130))
    elif kind == "poland":
        draw.rectangle([x, y, x + w, y + h], fill=(28, 28, 44))
        for j, (x0, y0) in enumerate([(x + 16, y + 5), (x + 110, y + 3), (x + 200, y + 7)]):
            draw.line([(x0, y0), (x0 + 44, y0 + 18)], fill=(255, 190, 60), width=3)
            draw.ellipse([x0 + 41, y0 + 15, x0 + 49, y0 + 23], fill=(255, 120, 40))
        for j in range(3):
            jx = x + 36 + j * 92
            draw.polygon([(jx, y + h - 16), (jx + 22, y + h - 11), (jx, y + h - 6)],
                         fill=(180, 180, 190))
        draw.rectangle([x, y + h - 5, x + w, y + h], fill=(40, 90, 50))
    else:  # cyclone
        draw.rectangle([x, y, x + w, y + h], fill=(58, 96, 120))
        cx, cy = x + w // 2, y + h // 2 + 2
        for r in (7, 13):
            draw.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=20 + r * 6,
                     fill=(255, 255, 255), width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
        for i in range(9):
            rx = x + 10 + i * 34
            draw.line([(rx, y + 3), (rx - 3, y + 10)], fill=(200, 220, 240), width=2)
        draw.rectangle([x, y + h - 6, x + w, y + h], fill=(30, 70, 60))
        for j in range(4):
            hx = x + 26 + j * 72
            draw.polygon([(hx, y + h - 14), (hx + 10, y + h - 21), (hx + 20, y + h - 14)],
                         fill=(200, 60, 40))
            draw.rectangle([hx + 2, y + h - 14, hx + 18, y + h - 6],
                           fill=(240, 220, 180))


def main():
    check_content()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 22
    CW = W - 2 * MX
    y = 12

    # ---- masthead: kicker (with story count) + giant date ----
    f_kick = font(F_COND_B, 28)
    f_date = font(F_SERIF_B, 44)
    assert tw(d, MASTHEAD_KICKER, f_kick) <= CW, "kicker too wide"
    d.text(((W - tw(d, MASTHEAD_KICKER, f_kick)) / 2, y), MASTHEAD_KICKER,
           font=f_kick, fill=RED)
    y += 29
    assert tw(d, MASTHEAD_DATE, f_date) <= CW, "date too wide"
    d.text(((W - tw(d, MASTHEAD_DATE, f_date)) / 2, y), MASTHEAD_DATE,
           font=f_date, fill=INK)
    y += 49
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=3)
    y += 5

    # ---- stats strip: 5 cells, number over label ----
    f_num = font(F_SERIF_B, 30)
    f_lab = font(F_COND, 26)
    cell = CW // 5
    y0 = y
    for i, (num, lab) in enumerate(STATS):
        cx = MX + i * cell + cell // 2
        assert tw(d, lab, f_lab) <= cell - 6, f"stat label too wide: {lab}"
        assert tw(d, num, f_num) <= cell - 6, f"stat number too wide: {num}"
        d.text((cx - tw(d, num, f_num) / 2, y), num, font=f_num, fill=INK)
        d.text((cx - tw(d, lab, f_lab) / 2, y + 32), lab, font=f_lab, fill=GREY)
        if i:
            d.line([(MX + i * cell, y + 2), (MX + i * cell, y + 56)], fill=GREY, width=1)
    y = y0 + 60
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=2)
    y += 5

    # ---- region bar ----
    f_reg = font(F_COND_B, 26)
    assert tw(d, REGION_BAR, f_reg) <= CW, "region bar too wide"
    d.text(((W - tw(d, REGION_BAR, f_reg)) / 2, y), REGION_BAR,
           font=f_reg, fill=RED)
    y += 28
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=2)
    y += 5

    # ---- 3 large stories ----
    f_lkick = font(F_COND, 26)
    f_lhead = font(F_SANS_B, 28)
    f_ldeck = font(F_SANS, 26)
    colw = (CW - 2 * 12) // 3
    SCENE_H = 30
    large_top = y
    row_h = 0
    for i, (num, kick, head, deck, scene) in enumerate(LARGE):
        x = MX + i * (colw + 12)
        assert tw(d, kick, f_lkick) <= colw, f"kicker too wide: {kick}"
        draw_scene(d, scene, x, y, colw, SCENE_H)
        yy = y + SCENE_H + 4
        d.text((x, yy), kick, font=f_lkick, fill=RED)
        yy += 28
        hl = wrap(d, head, f_lhead, colw)
        assert len(hl) <= 2, f"headline wraps to {len(hl)}: {head}"
        for ln in hl:
            d.text((x, yy), ln, font=f_lhead, fill=INK)
            yy += 29
        dl = wrap(d, deck, f_ldeck, colw)
        assert len(dl) <= 2, f"deck wraps to {len(dl)}: {deck}"
        for ln in dl:
            d.text((x, yy), ln, font=f_ldeck, fill=INK)
            yy += 26
        d.ellipse([x + 4, y + 3, x + 28, y + 27], fill=RED)
        f_badge = font(F_SANS_B, 24)
        d.text((x + 4 + (24 - tw(d, str(num), f_badge)) / 2, y + 3),
               str(num), font=f_badge, fill=(255, 255, 255))
        row_h = max(row_h, yy - y)
    y = large_top + row_h + 4
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=2)
    y += 5

    # ---- 10 numbered stories: 2 cols x 5 rows ----
    f_nhead = font(F_SANS_B, 26)
    f_nline = font(F_COND, 26)
    ncolw = (CW - 12) // 2
    for r in range(5):
        for c in range(2):
            num, head, line = NUMBERED[r * 2 + c]
            x = MX + c * (ncolw + 12)
            assert tw(d, f"{num}  {head}", f_nhead) <= ncolw - 34, \
                f"head too wide: {head}"
            assert len(wrap(d, line, f_nline, ncolw)) == 1, \
                f"line wraps: {line!r}"
            d.ellipse([x, y, x + 28, y + 28], fill=RED)
            f_badge = font(F_SANS_B, 26 if num < 10 else 20)
            ns = str(num)
            d.text((x + (28 - tw(d, ns, f_badge)) / 2, y + (0 if num < 10 else 3)),
                   ns, font=f_badge, fill=(255, 255, 255))
            d.text((x + 34, y), head, font=f_nhead, fill=INK)
            d.text((x, y + 28), line, font=f_nline, fill=GREY)
        y += 56
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=2)
    y += 5

    # ---- MORE list: 3 cols x 6 rows ----
    f_more_h = font(F_SANS_B, 28)
    f_more = font(F_COND, 26)
    assert tw(d, MORE_HEADER, f_more_h) <= CW, "more header too wide"
    d.text((MX, y), MORE_HEADER, font=f_more_h, fill=INK)
    y += 26
    mcolw = (CW - 2 * 12) // 3
    for i, item in enumerate(MORE):
        col, row = divmod(i, 6)
        x = MX + col * (mcolw + 12)
        yy = y + row * 25
        text = f"{14 + i}  {item}"
        assert tw(d, text, f_more) <= mcolw, f"more item too wide: {text!r}"
        d.text((x, yy), text, font=f_more, fill=INK)
    y += 6 * 25 + 4
    d.line([(MX, y), (W - MX, y)], fill=RULE, width=2)
    y += 5

    # ---- DATE CHECK box ----
    f_dc = font(F_COND, 26)
    f_dc_b = font(F_COND_B, 26)
    box_h = 4 * 26 + 10
    d.rectangle([MX, y, W - MX, y + box_h], outline=RED, width=2)
    yy = y + 3
    for j, line in enumerate(DATE_CHECK):
        f = f_dc_b if j == 0 else f_dc
        assert tw(d, line, f) <= CW - 16, f"date check too wide: {line!r}"
        d.text((MX + 8, yy), line, font=f, fill=INK)
        yy += 26
    y += box_h + 5

    # ---- footer ----
    f_foot = font(F_COND, 26)
    for line in FOOTER:
        assert tw(d, line, f_foot) <= CW, f"footer too wide: {line!r}"
        d.text(((W - tw(d, line, f_foot)) / 2, y), line, font=f_foot, fill=GREY)
        y += 25

    assert y <= 1016, f"layout overflow: bottom {y}"
    img.save("entry.png")
    print(f"saved entry.png {os.path.getsize('entry.png')} bytes, bottom={y}")


if __name__ == "__main__":
    main()
