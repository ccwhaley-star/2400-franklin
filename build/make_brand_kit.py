# brand/: PNG logo + favicon files for uploading to other services (Cubby portal, Google, etc.).
# Same lockup geometry as og.jpg: FRANKLIN cap top = 2400 cap top, FLEX SPACE baseline = 2400 baseline,
# FLEX SPACE spaced to FRANKLIN's width. Run: python -I build/make_brand_kit.py
import pathlib
from PIL import Image, ImageDraw, ImageFont

P = pathlib.Path(r"C:\Github_folder\2400-franklin")
VF = P / "build" / "Montserrat-VF.ttf"
OUT = P / "brand"; OUT.mkdir(exist_ok=True)
INK, BG, CREAM, BRASS = "#1E1D1E", "#151415", "#EEE9E0", "#C9A86A"

def font(size, wght):
    f = ImageFont.truetype(str(VF), size); f.set_variation_by_axes([wght]); return f

def lockup(num_px, fill, divider, pad, bg=None):
    """Transparent (or bg) image of the lockup with `pad` px around the ink."""
    scratch = ImageDraw.Draw(Image.new("L", (1, 1)))
    num_f, fr_f = font(num_px, 700), font(round(num_px * 0.385), 500)
    def sw(text, f, tr): return sum(scratch.textlength(c, font=f) for c in text) + tr * (len(text) - 1)
    nb = scratch.textbbox((0, 0), "2400", font=num_f); cap_h = nb[3] - nb[1]; nw = nb[2] - nb[0]
    fr_track = num_px * 0.091
    fr_w = sw("FRANKLIN", fr_f, fr_track)
    fs_f = font(10, 600)
    for s in range(10, num_px):                         # largest FLEX SPACE that still fits FRANKLIN's width
        f_try = font(s, 600)
        if sw("FLEX SPACE", f_try, 0.3 * s) > fr_w: break
        fs_f = f_try
    fs_track = (fr_w - sw("FLEX SPACE", fs_f, 0)) / 9
    gap = round(num_px * 0.21)
    W = pad * 2 + nw + gap + 2 + round(num_px * 0.23) + round(fr_w)
    H = pad * 2 + cap_h
    im = Image.new("RGBA", (W, H), bg or (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, top = pad, pad
    d.text((x0 - nb[0], top - nb[1]), "2400", font=num_f, fill=fill)
    bar_x = x0 + nw + gap
    d.rectangle([bar_x, top, bar_x + max(2, num_px // 50), top + cap_h], fill=divider)
    rx = bar_x + round(num_px * 0.23)
    def spaced(x, y_top, text, f, tr):
        off = d.textbbox((0, 0), "H", font=f)[1]
        for c in text:
            d.text((x, y_top - off), c, font=f, fill=fill); x += d.textlength(c, font=f) + tr
    spaced(rx, top, "FRANKLIN", fr_f, fr_track)
    fs_box = d.textbbox((0, 0), "H", font=fs_f)
    spaced(rx + 1, top + cap_h - (fs_box[3] - fs_box[1]), "FLEX SPACE", fs_f, fs_track)
    return im

def icon(px):
    im = Image.new("RGB", (px, px), BG); d = ImageDraw.Draw(im)
    f = font(int(px * 0.33), 700); t = "2400"
    bb = d.textbbox((0, 0), t, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((px - tw) / 2 - bb[0], px * 0.56 - th / 2 - bb[1]), t, font=f, fill=CREAM)
    d.rectangle([px * 0.125, px * 0.80, px * 0.875, px * 0.85], fill=BRASS)
    return im

files = {
    "logo-dark.png":  lockup(240, INK, "#9A968F", 24),            # for white/light backgrounds (Cubby portal)
    "logo-light.png": lockup(240, CREAM, "#8A8782", 24),          # for dark backgrounds
    "logo-on-dark.png": lockup(240, CREAM, "#8A8782", 96, BG),    # solid dark tile, for places that want a filled image
}
for name, im in files.items():
    im.save(OUT / name, optimize=True); print(name, im.size)
for px in (512, 192, 32):
    icon(px).save(OUT / f"favicon-{px}.png", optimize=True); print(f"favicon-{px}.png")
icon(64).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]); print("favicon.ico")
