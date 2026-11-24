#!/usr/bin/env python3
"""news-image-20261124 v1 — sums up Tuesday 24 November 2026 world news
in one 1024x1024 image. Pure PIL rendering, stdlib otherwise.
No network, no wall clock, no randomness: deterministic output.
Writes /output/entry.png when run.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"
CUTOFF = "02:30 UTC, Tuesday 24 November 2026"

INK = (26, 26, 26)
PAPER = (250, 246, 238)
NAVY = (20, 33, 61)
RED = (193, 18, 31)
GREY = (107, 107, 107)
LINE = (216, 210, 196)
BLUE = (31, 78, 121)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
MAPLAND = (196, 196, 170)
MAPSEA = (222, 235, 240)


def load_font(bold, size):
    paths = []
    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


F = {
    "mast": load_font(True, 44),
    "mastkick": load_font(True, 13),
    "subdeck": load_font(False, 15),
    "num": load_font(True, 28),
    "numlab": load_font(True, 10),
    "seclab": load_font(True, 11),
    "tl_date": load_font(True, 11),
    "tl": load_font(False, 11),
    "leadkick": load_font(True, 11),
    "leadhead": load_font(True, 20),
    "leaddeck": load_font(False, 13),
    "leaddate": load_font(False, 10),
    "gridhead": load_font(True, 13),
    "gridbody": load_font(False, 11),
    "gridnum": load_font(True, 11),
    "also": load_font(False, 11),
    "alsob": load_font(True, 11),
    "maplab": load_font(True, 10),
    "mapname": load_font(False, 9),
    "datecheck": load_font(True, 12),
    "datecheck2": load_font(False, 11),
}


def fit_font(draw, bold, text, max_w, start_size):
    """Largest size <= start_size whose text fits max_w (deterministic)."""
    for size in range(start_size, 7, -1):
        f = load_font(bold, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return load_font(bold, 7)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, font, fill, max_w, lh, max_lines=None):
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def hline(draw, x0, x1, y, fill=LINE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- data
NUMBERS = [
    ("+31%", "NVIDIA SHARES, MONDAY"),
    ("$2TN", "ANTHROPIC DEBUT VALUE"),
    ("24", "DEAD, JAVA FACTORY FIRE"),
    ("12,000", "MANCHESTER EVACUATION"),
    ("$44BN", "CROWDSTRIKE DEAL"),
    ("10,000", "ROHINGYA KILLED: ICJ"),
]

TIMELINE = [
    ("19 NOV", "ICJ: Myanmar guilty of genocide; Anthropic debuts near $2tn"),
    ("19 NOV", "Trump, Xi and Putin meet in Shenzhen at APEC"),
    ("22 NOV", "COP31 collapses in Antalya: no deal agreed"),
    ("23 NOV", "Nvidia reinstates Huang; shares jump 31%"),
    ("23 NOV", "Russian ship Sparta II ablaze off Finland"),
    ("24 NOV", "Java factory fire kills 24; dozens missing"),
    ("24 NOV", "12,000 evacuated from Manchester concert"),
]

LEADS = [
    ("CLIMATE — ANTALYA, TÜRKIYE",
     "COP31 COLLAPSES WITH NO DEAL",
     "194 nations reject the \u201cAntalya Pact\u201d after record overtime "
     "\u2014 its text never mentions fossil fuels. The EU calls it a step "
     "backwards; the UN chief says the world must do much more.",
     "SUN 22 NOV"),
    ("MARKETS — NEW YORK",
     "HUANG IS BACK AT NVIDIA",
     "The board reinstates Jensen Huang as chief executive days after his "
     "exit. Shares soar 31% on Monday, lifting the Nasdaq 6.5% and the "
     "S&P 500 4.7%.",
     "MON 23 NOV"),
    ("JUSTICE — THE HAGUE",
     "MYANMAR GUILTY OF GENOCIDE",
     "The world court rules 9\u20136 that Myanmar committed genocide against "
     "the Rohingya in 2017 — the first state ever found responsible. About "
     "10,000 were killed; reparations are ordered.",
     "THU 19 NOV"),
]

GRID = [
    ("4", "ANTHROPIC'S $2TN DEBUT",
     "Shares open at $111.50, up 34% on the $83 IPO price, in the biggest stock-market debut ever."),
    ("5", "SHIP ABLAZE OFF FINLAND",
     "Russian cargo vessel Sparta II catches fire in the Gulf of Finland after a drone attack."),
    ("6", "KYIV REGION UNDER FIRE",
     "Russian drones and missiles hit homes in Dymer; residents are missing after the strikes."),
    ("7", "24 DEAD IN JAVA FACTORY FIRE",
     "A candy-factory blaze in Banten kills at least 24; more than 30 are missing as rescuers dig on."),
    ("8", "12,000 FLEE MANCHESTER GIG",
     "A concert is evacuated after an unknown substance is released into the air."),
    ("9", "TRUMP, XI AND PUTIN'S 'PEACE PACT'",
     "The three leaders issue a joint declaration at APEC in Shenzhen on nuclear risk."),
    ("10", "CROWDSTRIKE BUYS ZSCALER",
     "$44bn cyber deal, the day's biggest, as online threats mount."),
    ("11", "A PACIFIC ISLAND EMPTIED",
     "Every resident of Kanton Island, Kiribati, is moved out with a day's notice."),
    ("12", "HOUTHI STRIKE HITS RIYADH",
     "Saudi Arabia says an attack damaged floors of a tower in the capital's financial district."),
    ("13", "STANDOFF AT HORMUZ",
     "Iran claims a US MQ-9 drone downed; its minister floats a 48-hour plan as talks stall."),
]

ALSO = [
    ("LISBON", "Thousands march on living costs."),
    ("INDIA-NEPAL", "Modi, Shah open cross-border train."),
    ("CRICKET", "Pant hits 128; India-NZ Test drawn."),
    ("TENNIS", "Alcaraz beats Zverev for ATP Finals."),
    ("FORMULA 1", "Verstappen wins Las Vegas GP."),
    ("CHESS", "Gukesh defends title in Geneva today."),
    ("INDIA-CHINA", "Generals meet in Arunachal Pradesh."),
    ("INDIA", "Modi opens AI centre at IIT Patna."),
    ("INDIA", "Oil and gas import bill up ~60%."),
    ("SPICEJET", "Pilots plead over pay, grounded jets."),
    ("FERRARI", "Two new 296 racers shown in Spain."),
    ("US BANKING", "JPMorgan glitch disrupts payments."),
    ("IRAN", "Singer gets 74 lashes, no hijab."),
    ("POLAND", "Three Russian missiles crossed airspace."),
    ("US SENATE", "Bill speeds up energy projects."),
    ("INDIA", "Cyclone Akvan hits Odisha coast."),
    ("GAZA", "Strike on Gaza City kills at least 3."),
    ("SUDAN", "UN condemns Khartoum airstrikes."),
    ("MEDITERRANEAN", "Two Russian diplomats expelled."),
    ("WORD OF 2026", "Cambridge picks 'human'."),
    ("VATICAN", "Pope Leo XIV ends S. America tour."),
    ("FIFA", "Three challenge Infantino."),
    ("TEXAS", "Execution lasts over an hour."),
]

# Simplified continent outlines, (lon, lat). Schematic, hand-drawn.
NORTH_AMERICA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
                 (-105, 70), (-95, 69), (-90, 73), (-85, 70), (-82, 66),
                 (-78, 62), (-72, 62), (-65, 60), (-60, 55), (-55, 47),
                 (-60, 44), (-65, 44), (-70, 42), (-74, 39), (-76, 35),
                 (-80, 32), (-81, 26), (-84, 30), (-89, 29), (-91, 21),
                 (-95, 19), (-97, 16), (-93, 15), (-88, 14), (-83, 9),
                 (-79, 8), (-82, 9), (-87, 13), (-92, 15), (-97, 16),
                 (-104, 20), (-108, 23), (-112, 28), (-117, 33), (-122, 37),
                 (-124, 42), (-124, 48), (-128, 52), (-134, 58), (-145, 60),
                 (-152, 58), (-158, 56), (-164, 60), (-168, 66)]
SOUTH_AMERICA = [(-79, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
                 (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
                 (-74, -52), (-70, -55), (-66, -55), (-65, -47), (-62, -41),
                 (-58, -35), (-52, -33), (-48, -28), (-41, -23), (-39, -17),
                 (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
                 (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
                 (-77, 8), (-79, 8)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 4), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 6),
          (14, 8), (18, 10), (22, 12), (25, 15), (30, 18), (33, 20),
          (35, 23), (37, 27), (39, 30), (34, 31), (32, 31), (30, 32),
          (25, 32), (20, 32), (15, 32), (11, 34), (10, 35), (5, 37),
          (0, 36), (-6, 35)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-5, 49),
           (0, 51), (5, 53), (8, 57), (10, 59), (5, 60), (5, 62),
           (10, 64), (14, 67), (20, 70), (28, 71), (35, 68), (40, 66),
           (45, 68), (55, 69), (65, 69), (75, 72), (85, 74), (95, 76),
           (105, 77), (115, 73), (125, 72), (135, 72), (145, 72), (155, 70),
           (162, 66), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52),
           (155, 48), (150, 45), (142, 42), (140, 38), (135, 35), (130, 33),
           (127, 35), (122, 38), (120, 32), (118, 25), (110, 20), (108, 12),
           (105, 9), (103, 7), (100, 8), (98, 12), (94, 16), (92, 21),
           (90, 22), (88, 22), (85, 19), (82, 16), (80, 13), (77, 8),
           (75, 12), (72, 20), (68, 23), (66, 25), (62, 25), (58, 26),
           (56, 27), (54, 27), (52, 28), (50, 29), (48, 30), (48, 29),
           (44, 29), (42, 27), (39, 24), (38, 22), (35, 20), (34, 18),
           (35, 16), (39, 15), (43, 12), (45, 12), (48, 14), (52, 16),
           (55, 17), (58, 20), (60, 22), (62, 24), (60, 25), (57, 25),
           (54, 26), (51, 26), (50, 29), (48, 30), (44, 30), (40, 31),
           (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (22, 37),
           (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40),
           (-2, 37), (-6, 36), (-9, 37), (-10, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (136, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (151, -24),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
             (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50)]
JAPAN = [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
         (141, 41), (139, 37), (136, 34), (132, 33)]
INDONESIA = [(95, 5), (98, 3), (102, 0), (106, -6), (110, -7), (114, -8),
             (118, -9), (122, -10), (120, -10), (115, -8), (110, -7),
             (105, -5), (100, 0), (97, 4)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (174, -41), (172, -43), (168, -46)]

# (name, lat, lon, label offset dx, dy or None for dot only)
PINS = [
    ("Antalya", 36.9, 30.7, (5, -5)),
    ("Kyiv", 50.45, 30.52, (5, -5)),
    ("Finland", 59.8, 24.5, None),
    ("Java", -6.2, 106.2, (5, -5)),
    ("Manchester", 53.48, -2.24, (-64, -5)),
    ("Tehran", 35.7, 51.4, None),
    ("Riyadh", 24.7, 46.7, (5, -5)),
    ("Geneva", 46.2, 6.1, (5, 6)),
    ("Shenzhen", 22.5, 114.1, (-60, -5)),
    ("The Hague", 52.07, 4.3, None),
    ("Lisbon", 38.7, -9.1, None),
    ("Kanton I.", 2.77, -171.7, None),
    ("Wellington", -41.3, 174.8, None),
    ("New York", 40.7, -74.0, None),
]


def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=MAPSEA)
    lon0, lon1, lat0, lat1 = -180.0, 190.0, 75.0, -55.0

    def proj(lon, lat):
        px = x0 + (lon - lon0) / (lon1 - lon0) * w
        py = y0 + (lat0 - lat) / (lat0 - lat1) * h
        return (px, py)

    for poly in (NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EURASIA,
                 AUSTRALIA, UK, JAPAN, INDONESIA, NEW_ZEALAND):
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=MAPLAND)
    for name, lat, lon, off in PINS:
        px, py = proj(lon, lat)
        r = 3
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=WHITE, width=1)
        if off is not None:
            draw.text((px + off[0], py + off[1]), name,
                      font=F["mapname"], fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 16
    x1 = W - mx

    # ---- masthead
    d.rectangle([0, 0, W, 76], fill=NAVY)
    d.text((mx, 10), "THE WORLD IN ONE IMAGE  —  TUESDAY",
           font=F["mastkick"], fill=GOLD)
    d.text((mx, 28), "24 NOVEMBER 2026", font=F["mast"], fill=WHITE)
    d.text((x1 - d.textlength("WORLD NEWS", font=F["mastkick"]),
            14), "WORLD NEWS", font=F["mastkick"], fill=WHITE)

    # ---- red sub-deck
    d.rectangle([0, 76, W, 104], fill=RED)
    d.text((mx, 83),
           "Climate talks collapse, a chip king returns, and a court makes history.",
           font=F["subdeck"], fill=WHITE)

    # ---- 6 key numbers
    y = 112
    bw = (x1 - mx - 5 * 8) // 6
    for i, (num, lab) in enumerate(NUMBERS):
        bx = mx + i * (bw + 8)
        d.rectangle([bx, y, bx + bw, y + 58], fill=WHITE, outline=LINE)
        d.rectangle([bx, y, bx + bw, y + 4], fill=RED)
        d.text((bx + 8, y + 10), num, font=F["num"], fill=NAVY)
        lab_f = fit_font(d, True, lab, bw - 16, 10)
        d.text((bx + 8, y + 42), lab, font=lab_f, fill=GREY)

    # ---- timeline
    y = 184
    d.text((mx, y), "THE DAY SO FAR — UTC TIMELINE", font=F["seclab"],
           fill=RED)
    y += 18
    hline(d, mx, x1, y + 8, fill=LINE, width=2)
    tw = (x1 - mx - 6 * 8) // 7
    for i, (dt, txt) in enumerate(TIMELINE):
        tx = mx + i * (tw + 8)
        d.ellipse([tx + 2, y + 4, tx + 10, y + 12], fill=RED)
        d.text((tx, y + 16), dt, font=F["tl_date"], fill=NAVY)
        text_block(d, tx, y + 30, txt, F["tl"], INK, tw, 13, max_lines=4)

    # ---- leads
    y = 282
    d.text((mx, y), "TOP STORIES", font=F["seclab"], fill=RED)
    y += 18
    lw = (x1 - mx - 2 * 12) // 3
    for i, (kick, head, deck, dt) in enumerate(LEADS):
        lx = mx + i * (lw + 12)
        if i:
            d.line([(lx - 7, y), (lx - 7, y + 158)], fill=LINE, width=1)
        d.text((lx, y), kick, font=F["leadkick"], fill=RED)
        yy = text_block(d, lx, y + 18, head, F["leadhead"], INK, lw, 24,
                        max_lines=2)
        text_block(d, lx, yy + 4, deck, F["leaddeck"], INK, lw, 16,
                   max_lines=4)
        d.text((lx, y + 142), dt, font=F["leaddate"], fill=GREY)

    # ---- grid stories 4-13
    y = 478
    d.text((mx, y), "MORE TOP STORIES", font=F["seclab"], fill=RED)
    y += 18
    gw = (x1 - mx - 4 * 8) // 5
    gh = 96
    for i, (num, head, body) in enumerate(GRID):
        r, c = divmod(i, 5)
        gx = mx + c * (gw + 8)
        gy = y + r * (gh + 8)
        d.rectangle([gx, gy, gx + gw, gy + gh], fill=WHITE, outline=LINE)
        d.text((gx + 8, gy + 7), num, font=F["gridnum"], fill=RED)
        yy = text_block(d, gx + 8, gy + 22, head, F["gridhead"], INK,
                        gw - 16, 15, max_lines=2)
        text_block(d, gx + 8, yy + 2, body, F["gridbody"], INK, gw - 16,
                   13, max_lines=3)

    # ---- ALSO IN + map
    y = 700
    d.text((mx, y), "ALSO IN — 23 MORE STORIES", font=F["seclab"],
           fill=RED)
    d.text((656, y), "WHERE IT HAPPENED", font=F["seclab"], fill=RED)
    y += 18
    col_w = 306
    for j, (tag, txt) in enumerate(ALSO):
        col = j // 12
        row = j % 12
        ax = mx + col * (col_w + 12)
        ay = y + row * 22
        d.text((ax, ay), tag + " — ", font=F["alsob"], fill=NAVY)
        twd = d.textlength(tag + " — ", font=F["alsob"])
        text_block(d, ax + twd, ay, txt, F["also"], INK,
                   col_w - twd, 14, max_lines=1)
    draw_map(d, 656, y, 352, 254)
    d.rectangle([656, y, 1008, y + 254], outline=LINE)

    # ---- DATE CHECK
    d.rectangle([0, 972, W, H], fill=NAVY)
    d.text((mx, 980), "DATE CHECK", font=F["datecheck"], fill=GOLD)
    d.text((mx + 108, 980),
           "Coverage to " + CUTOFF + ".",
           font=F["datecheck"], fill=WHITE)
    d.text((mx, 998),
           "Every story above was reported by then; nothing after that time is included.",
           font=F["datecheck2"], fill=(200, 205, 215))

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG")


if __name__ == "__main__":
    main()
