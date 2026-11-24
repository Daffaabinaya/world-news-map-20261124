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
    "politics": ((59, 130, 246), "Politics"),
    "economy": ((250, 204, 21), "Business, tech & science"),
    "disaster": ((251, 146, 60), "Disaster"),
    "travel": ((20, 184, 166), "Health"),
}

# (number, category, lon, lat, map label, label side, place tag, headline, detail)
# Version 2: every story was published on 24 November 2026.
STORIES = [
    (1, "conflict", 56.4, 26.6, "HORMUZ", "b", "STRAIT OF HORMUZ · IRAN",
     "Iran shuts Hormuz further", "4 tankers hit by mines; Qatar seeks to revive talks"),
    (2, "economy", -121.96, 37.37, "SANTA CLARA", "r", "SANTA CLARA · USA",
     "Jensen Huang back as Nvidia CEO", "Trump says he spoke to the board; AI-bubble fears linger"),
    (3, "conflict", 34.45, 31.5, "GAZA", "l", "GAZA",
     "Israeli strike kills Hamas security chief", "7 killed in Gaza as doctors warn of meningitis"),
    (4, "conflict", 35.14, 47.84, "ZAPORIZHZHIA", "r", "ZAPORIZHZHIA · UKRAINE",
     "Russian strike kills 2, wounds dozens", "Zelensky urges four-way talks with Russia, US, Europe"),
    (5, "politics", 44.0, 36.2, "KURDISTAN", "r", "KURDISTAN · IRAQ",
     "Baghdad orders takeover of Kurdish oilfields", "Iraq moves on oil in Kurdish-controlled areas"),
    (6, "politics", -77.04, 38.9, "WASHINGTON", "r", "WASHINGTON · USA",
     "Trump urges faster federal executions", "Blasts Newsom for commuting 548 death sentences"),
    (7, "economy", 100.3, 40.96, "JIUQUAN", "r", "JIUQUAN · CHINA",
     "China to fly its first foreign astronaut", "Pakistan's Zeeshan Ali heads for Tiangong station"),
    (8, "politics", 90.4, 23.8, "DHAKA", "l", "DHAKA · BANGLADESH",
     "Sheikh Hasina to end exile on Dec 16", "Ousted ex-PM plans return to Bangladesh"),
    (9, "disaster", 106.0, 16.0, "VIETNAM", "r", "VIETNAM",
     "Restaurant blast kills at least 6", "Deadly explosion tears through a restaurant"),
    (10, "conflict", -99.13, 19.43, "MEXICO", "l", "MEXICO",
     "Mexico to try 'El Chapo Isidro'", "Defies US extradition bid; US drone aided capture"),
    (11, "politics", 149.13, -35.28, "CANBERRA", "l", "CANBERRA · AUSTRALIA",
     "Australia warns tech giants of huge fines", "Multibillion-dollar penalties over online harm"),
    (12, "travel", -82.37, 23.11, "HAVANA", "r", "HAVANA · CUBA",
     "WHO chief visits crisis-hit Cuba", "Health system crumbles amid fuel shortages"),
]

# Map window (equirectangular)
MAP_TOP, MAP_BOTTOM = 152, 514
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
        col = CAT[cat][0]
        r = 26 * S
        gd.ellipse([x - r, y - r, x + r, y + r], fill=col + (110,))
    glow = glow.filter(ImageFilter.GaussianBlur(9 * S))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img)
    f_num = font("seguibl.ttf", 16)
    f_lab = font("segoeuib.ttf", 11.5)
    for n, cat, lon, lat, label, side, *_ in STORIES:
        x, y = proj(lon, lat)
        col = CAT[cat][0]
        r = 14 * S
        d.ellipse([x - r - 2 * S, y - r - 2 * S, x + r + 2 * S, y + r + 2 * S], fill=WHITE)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        txt_col = (20, 20, 20) if cat == "economy" else WHITE
        d.text((x, y + S), str(n), font=f_num, fill=txt_col, anchor="mm")
        tw = d.textlength(label, font=f_lab)
        off = 20 * S
        if side == "r":
            pos, anchor = (x + off, y), "lm"
        elif side == "l":
            pos, anchor = (x - off, y), "rm"
        else:
            pos, anchor = (x, y + off + 2 * S), "mt"
        bx0 = pos[0] - (tw if anchor == "rm" else tw / 2 if anchor == "mt" else 0) - 5 * S
        by0 = pos[1] - (8 * S if anchor != "mt" else 2 * S)
        d.rounded_rectangle([bx0, by0, bx0 + tw + 10 * S, by0 + 17 * S], radius=4 * S,
                            fill=(9, 17, 33))
        d.text((bx0 + 5 * S, by0 + 8.5 * S), label, font=f_lab, fill=WHITE, anchor="lm")


def draw_header(img):
    d = ImageDraw.Draw(img)
    d.rectangle([28 * S, 26 * S, 36 * S, 136 * S], fill=ACCENT)
    d.text((52 * S, 24 * S), "THE WORLD IN ONE IMAGE", font=font("segoeuib.ttf", 19),
           fill=ACCENT)
    d.text((50 * S, 44 * S), "TUESDAY 24 NOVEMBER 2026", font=font("seguibl.ttf", 60),
           fill=WHITE)
    d.text((52 * S, 118 * S),
           "12 stories that defined the day \u2014 from mined tankers in Hormuz to Nvidia's boardroom",
           font=font("segoeui.ttf", 20), fill=MUTED)


def draw_list(img):
    d = ImageDraw.Draw(img)
    cols = [(26, STORIES[:6]), (528, STORIES[6:])]
    top, row_h, col_w = 528, 74, 474
    f_tag = font("segoeuib.ttf", 12.5)
    f_num = font("seguibl.ttf", 19)
    for x0, items in cols:
        for i, (n, cat, *_rest) in enumerate(items):
            tag, head, sub = _rest[-3:]
            col = CAT[cat][0]
            y0 = top + i * row_h
            cx, cy = (x0 + 19) * S, (y0 + 28) * S
            r = 18 * S
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
            d.text((cx, cy + S), str(n), font=f_num,
                   fill=(20, 20, 20) if cat == "economy" else WHITE, anchor="mm")
            tx = (x0 + 50) * S
            d.text((tx, y0 * S), tag, font=f_tag, fill=col)
            d.text((tx, (y0 + 16) * S), head, font=fit(d, head, "segoeuib.ttf", 23, col_w - 56),
                   fill=WHITE)
            d.text((tx, (y0 + 46) * S), sub, font=fit(d, sub, "segoeui.ttf", 17, col_w - 56),
                   fill=MUTED)


def draw_footer(img):
    d = ImageDraw.Draw(img)
    d.line([26 * S, 974 * S, (W - 26) * S, 974 * S], fill=GRID, width=2 * S)
    f_leg = font("segoeui.ttf", 14)
    x, y = 26, 979
    for key in ["conflict", "politics", "economy", "disaster", "travel"]:
        col, name = CAT[key]
        d.ellipse([x * S, (y + 4) * S, (x + 11) * S, (y + 15) * S], fill=col)
        d.text(((x + 16) * S, y * S), name, font=f_leg, fill=WHITE)
        x += 30 + d.textlength(name, font=f_leg) / S
    d.text((26 * S, 1000 * S),
           "Stories published on 24 Nov 2026  ·  Sources: Al Jazeera, Euronews, France 24",
           font=font("segoeui.ttf", 14), fill=MUTED)
    d.text(((W - 26) * S, 990 * S), "Tue 24.11.2026", font=font("segoeuib.ttf", 17),
           fill=WHITE, anchor="rm")


def main():
    img = Image.new("RGB", (W * S, H * S), BG)
    draw_map(img)
    draw_markers(img)
    draw_header(img)
    draw_list(img)
    draw_footer(img)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, "PNG", optimize=True)
    print("wrote", os.path.normpath(OUT), os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
