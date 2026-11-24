"""Draw entry.png: a world-map infographic of the news of Tuesday 24 November 2026.

Run once on a machine with Pillow and the Windows system fonts:
    python tools/make_image.py
It writes ../entry.png (1024x1024 PNG). main.py only copies that file.
Land outlines: Natural Earth 1:110m land (public domain), tools/data/ne_110m_land.geojson.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "entry.png")
FONTS = r"C:\Windows\Fonts"

S = 2                      # supersampling factor, downscaled at the end
W = H = 1024

# Colours
BG = (9, 17, 33)
OCEAN = (13, 27, 50)
LAND = (34, 58, 92)
COAST = (70, 104, 148)
GRID = (24, 42, 70)
WHITE = (245, 247, 250)
MUTED = (168, 182, 204)
ACCENT = (239, 68, 68)

CAT = {
    "conflict": ((239, 68, 68), "Conflict & security"),
    "politics": ((59, 130, 246), "Politics & justice"),
    "economy": ((250, 204, 21), "Business, tech & science"),
    "disaster": ((251, 146, 60), "Disasters"),
    "society": ((20, 184, 166), "Health, society & climate"),
    "sport": ((168, 85, 247), "Sport"),
}
DARK_TEXT = {"economy"}

# (number, category, lon, lat, place tag, headline, detail)
# Version 3: 24 stories, every one published on 24 November 2026.
STORIES = [
    (1, "conflict", 56.4, 26.6, "STRAIT OF HORMUZ · IRAN",
     "Iran shuts Hormuz 'day by day'", "IRGC says tankers hit mines; Qatar pushes talks"),
    (2, "economy", -121.96, 37.37, "SANTA CLARA · USA",
     "Jensen Huang back as Nvidia CEO", "Rally adds ~$950bn; Trump spoke to the board"),
    (3, "conflict", 20.07, 32.12, "BENGHAZI · LIBYA",
     "Ukraine hits Russian ships off Libya", "Kyiv vows more strikes; Tripoli denies any role"),
    (4, "conflict", 35.14, 47.84, "ZAPORIZHZHIA · UKRAINE",
     "Russian strike kills 2, wounds ~40", "Zelensky urges four-way talks with Russia, US, EU"),
    (5, "conflict", 34.45, 31.5, "GAZA",
     "Israel kills Hamas security chief", "Six others killed in strikes across the Strip"),
    (6, "society", 30.7, 36.9, "ANTALYA · TÜRKIYE",
     "COP31 collapses; EU wants reform", "Deal without fossil-fuel exit was rejected"),
    (7, "conflict", 37.6, 55.75, "MOSCOW · RUSSIA",
     "Leak: 490,000 Russian troops killed", "Rosstat data on war deaths up to August"),
    (8, "conflict", 46.7, 24.7, "RIYADH · SAUDI ARABIA",
     "Riyadh tower hit in 'terrorist attack'", "Saudi-led coalition condemns strike on finance hub"),
    (9, "politics", 44.0, 36.2, "KURDISTAN · IRAQ",
     "Baghdad orders Kurdish oilfield takeover", "Government moves on oil in Kurdish-held areas"),
    (10, "politics", 2.35, 48.86, "PARIS · FRANCE",
     "Officer who shot Nahel faces murder trial", "Charge upgraded; up to 30 years in prison"),
    (11, "sport", -17.45, 14.7, "DAKAR · SENEGAL",
     "Senegal handed back AFCON title", "Sport court overturns award to Morocco"),
    (12, "society", 13.15, 11.85, "BORNO · NIGERIA",
     "Borno school enrolment nearly doubles", "Classrooms fill again after years of conflict"),
    (13, "politics", 90.4, 23.8, "DHAKA · BANGLADESH",
     "Hasina to end exile on 16 December", "Ousted ex-PM plans return from India"),
    (14, "economy", 100.3, 40.96, "JIUQUAN · CHINA",
     "China to fly first foreign astronaut", "Pakistan's Zeeshan Ali heads for Tiangong"),
    (15, "disaster", 105.85, 21.03, "HANOI · VIETNAM",
     "Restaurant blast kills at least 6", "At least 10 hurt in Dong Da district"),
    (16, "disaster", 106.15, -6.12, "BANTEN · INDONESIA",
     "Factory fire death toll rises to 26", "Search goes on for trapped workers"),
    (17, "society", 101.7, 3.14, "KUALA LUMPUR · MALAYSIA",
     "Malaysia to send Rohingya back", "Thousands face return to Myanmar after ICJ ruling"),
    (18, "conflict", 128.9, 36.4, "SOUTH KOREA",
     "Russian jets trigger Korean alert", "Islanders told to shelter; jets stayed outside"),
    (19, "politics", 149.13, -35.28, "CANBERRA · AUSTRALIA",
     "Australia warns tech giants of huge fines", "Multibillion-dollar penalties over online harm"),
    (20, "politics", -77.04, 38.9, "WASHINGTON · USA",
     "Trump urges faster federal executions", "Blasts Newsom for commuting 548 death sentences"),
    (21, "society", -82.37, 23.11, "HAVANA · CUBA",
     "WHO chief visits crisis-hit Cuba", "Health system crumbles amid fuel shortages"),
    (22, "conflict", -99.13, 19.43, "MEXICO",
     "Mexico to try 'El Chapo Isidro'", "Defies US extradition bid; US drone aided capture"),
    (23, "conflict", -73.63, 4.14, "META · COLOMBIA",
     "Car bomb hits governor's office", "Ten years after the peace deal, conflict returns"),
    (24, "disaster", -90.3, -0.74, "GALÁPAGOS · ECUADOR",
     "Severe floods swamp the Galápagos", "Residents evacuated by boat amid El Niño fears"),
]

ALSO = ("UN chief wants an AI oversight deal within a year  ·  Most distant quasar ever found  ·  "
        "Indian teen Sooryavanshi hits 204 off 53 balls")

# Map window (equirectangular)
MAP_TOP, MAP_BOTTOM = 140, 492
LON0, LON1 = -131.0, 160.0
PX_PER_DEG = W / (LON1 - LON0)
LAT_TOP = 60.0


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size * S))


def proj(lon, lat):
    x = (lon - LON0) * PX_PER_DEG
    y = MAP_TOP + (LAT_TOP - lat) * PX_PER_DEG
    return x * S, y * S


def fit(draw, text, fname, size, max_w, min_size=11):
    while size > min_size:
        f = font(fname, size)
        if draw.textlength(text, font=f) <= max_w * S:
            return f
        size -= 0.5
    return font(fname, min_size)


def draw_map(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, MAP_TOP * S, W * S, MAP_BOTTOM * S], fill=OCEAN)
    for lon in range(-120, 151, 30):
        x, _ = proj(lon, 0)
        d.line([x, MAP_TOP * S, x, MAP_BOTTOM * S], fill=GRID, width=S)
    for lat in range(-30, 61, 15):
        _, y = proj(0, lat)
        if MAP_TOP * S <= y <= MAP_BOTTOM * S:
            d.line([0, y, W * S, y], fill=GRID, width=S)
    with open(os.path.join(HERE, "data", "ne_110m_land.geojson"), encoding="utf-8") as fh:
        geo = json.load(fh)
    land = Image.new("L", img.size, 0)
    ld = ImageDraw.Draw(land)
    rings = []
    for feat in geo["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for i, ring in enumerate(poly):
                pts = [proj(lon, lat) for lon, lat in ring]
                ld.polygon(pts, fill=0 if i else 255)
                rings.append(pts)
    clip = Image.new("L", img.size, 0)
    ImageDraw.Draw(clip).rectangle([0, MAP_TOP * S, W * S, MAP_BOTTOM * S], fill=255)
    mask = Image.composite(land, Image.new("L", img.size, 0), clip)
    img.paste(Image.new("RGB", img.size, LAND), (0, 0), mask)
    coast = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(coast)
    for pts in rings:
        cd.line(pts + [pts[0]], fill=COAST + (255,), width=S)
    coast.putalpha(Image.composite(coast.getchannel("A"), Image.new("L", img.size, 0), clip))
    img.paste(coast, (0, 0), coast)
    # fade map edges into the background
    d.rectangle([0, (MAP_TOP - 1) * S, W * S, MAP_TOP * S], fill=GRID)
    d.rectangle([0, MAP_BOTTOM * S, W * S, (MAP_BOTTOM + 1) * S], fill=GRID)


def draw_markers(img):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for n, cat, lon, lat, *_ in STORIES:
        x, y = proj(lon, lat)
        r = 18 * S
        gd.ellipse([x - r, y - r, x + r, y + r], fill=CAT[cat][0] + (120,))
    glow = glow.filter(ImageFilter.GaussianBlur(7 * S))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img)
    f_num = font("seguibl.ttf", 12.5)
    for n, cat, lon, lat, *_ in STORIES:
        x, y = proj(lon, lat)
        col = CAT[cat][0]
        r = 10.5 * S
        d.ellipse([x - r - 2 * S, y - r - 2 * S, x + r + 2 * S, y + r + 2 * S], fill=WHITE)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        d.text((x, y + S), str(n), font=f_num,
               fill=(20, 20, 20) if cat in DARK_TEXT else WHITE, anchor="mm")


def draw_header(img):
    d = ImageDraw.Draw(img)
    d.rectangle([24 * S, 22 * S, 31 * S, 124 * S], fill=ACCENT)
    d.text((44 * S, 18 * S), "THE WORLD IN ONE IMAGE", font=font("segoeuib.ttf", 18),
           fill=ACCENT)
    d.text((42 * S, 36 * S), "TUESDAY 24 NOVEMBER 2026", font=font("seguibl.ttf", 58),
           fill=WHITE)
    sub = ("24 stories \u00b7 23 countries \u00b7 6 continents \u2014 Nvidia's boss returns "
           "as Hormuz closes and COP31 collapses")
    d.text((44 * S, 104 * S), sub, font=fit(d, sub, "segoeui.ttf", 19, W - 70), fill=MUTED)


def draw_also(img):
    d = ImageDraw.Draw(img)
    y = 500
    f_pill = font("segoeuib.ttf", 12)
    label = "ALSO TODAY"
    tw = d.textlength(label, font=f_pill) / S
    d.rounded_rectangle([22 * S, y * S, (22 + tw + 16) * S, (y + 20) * S], radius=4 * S,
                        fill=ACCENT)
    d.text(((30) * S, (y + 10) * S), label, font=f_pill, fill=WHITE, anchor="lm")
    x = 22 + tw + 26
    d.text((x * S, (y + 10) * S), ALSO, font=fit(d, ALSO, "segoeui.ttf", 14, W - 22 - x, 9),
           fill=WHITE, anchor="lm")


def draw_list(img):
    d = ImageDraw.Draw(img)
    col_w = 330
    cols = [(18, STORIES[:8]), (18 + col_w + 6, STORIES[8:16]), (18 + 2 * (col_w + 6), STORIES[16:])]
    top, row_h = 530, 54
    f_tag = font("segoeuib.ttf", 10.5)
    f_num = font("seguibl.ttf", 15)
    for x0, items in cols:
        for i, (n, cat, _lon, _lat, tag, head, sub) in enumerate(items):
            col = CAT[cat][0]
            y0 = top + i * row_h
            cx, cy = (x0 + 14) * S, (y0 + 22) * S
            r = 13.5 * S
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
            d.text((cx, cy + S), str(n), font=f_num,
                   fill=(20, 20, 20) if cat in DARK_TEXT else WHITE, anchor="mm")
            tx = (x0 + 36) * S
            tmax = col_w - 40
            d.text((tx, y0 * S), tag, font=f_tag, fill=col)
            d.text((tx, (y0 + 12) * S), head, font=fit(d, head, "segoeuib.ttf", 17, tmax, 10),
                   fill=WHITE)
            d.text((tx, (y0 + 34) * S), sub, font=fit(d, sub, "segoeui.ttf", 13, tmax, 9),
                   fill=MUTED)


def draw_footer(img):
    d = ImageDraw.Draw(img)
    d.line([20 * S, 968 * S, (W - 20) * S, 968 * S], fill=GRID, width=2 * S)
    f_leg = font("segoeui.ttf", 13)
    x, y = 22, 973
    for key in CAT:
        col, name = CAT[key]
        d.ellipse([x * S, (y + 4) * S, (x + 10) * S, (y + 14) * S], fill=col)
        d.text(((x + 14) * S, y * S), name, font=f_leg, fill=WHITE)
        x += 26 + d.textlength(name, font=f_leg) / S
    d.text((22 * S, 995 * S),
           "All stories published on 24 Nov 2026  \u00b7  Sources: Al Jazeera, Euronews, France 24"
           "  \u00b7  Map: Natural Earth",
           font=font("segoeui.ttf", 13), fill=MUTED)
    d.text(((W - 22) * S, 1003 * S), "Tue 24.11.2026", font=font("segoeuib.ttf", 16),
           fill=WHITE, anchor="rm")


def main():
    img = Image.new("RGB", (W * S, H * S), BG)
    draw_map(img)
    draw_markers(img)
    draw_header(img)
    draw_also(img)
    draw_list(img)
    draw_footer(img)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, "PNG", optimize=True)
    print("wrote", os.path.normpath(OUT), os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
