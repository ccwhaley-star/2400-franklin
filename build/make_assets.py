# logo.svg (lockup as paths), favicon.svg, favicon.ico, apple-touch-icon.png, og.jpg
import pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = pathlib.Path(r"C:\Github_folder\2400-franklin")
VF = P / "build" / "Montserrat-VF.ttf"
INK, BG, RED, CREAM = "#1E1D1E", "#151415", "#B3262E", "#F6F3EC"

def static(wght):
    return instantiateVariableFont(TTFont(VF), {"wght": wght}, inplace=False)

def text_path(font, text, size, tracking_em=0.0):
    """SVG path data for `text` at `size` px (y down), plus advance width."""
    glyphs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
    scale = size / upm; x = 0; d = []
    for ch in text:
        g = cmap[ord(ch)]; pen = SVGPathPen(glyphs); glyphs[g].draw(pen)
        path = pen.getCommands()
        if path:
            d.append(f'<path transform="translate({x:.2f} 0) scale({scale:.5f} {-scale:.5f})" d="{path}"/>')
        x += glyphs[g].width * scale + tracking_em * size
    return "\n".join(d), x

def lockup_svg(fill, with_url=False):
    """The sign lockup. '2400' 100px; FRANKLIN/FLEX SPACES to its right; optional URL third line."""
    f700, f500, f600 = static(700), static(500), static(600)
    num, numw = text_path(f700, "2400", 100, -0.04)
    numw += 0.04 * 100  # last tracking step is not drawn
    fr, frw = text_path(f500, "FRANKLIN", 33, 0.24)
    fs, fsw = text_path(f600, "FLEX SPACE", 15, 0.24)
    url, urlw = text_path(f500, "2400franklin.com", 15, 0.06)
    cap = 100 * 0.70  # Montserrat cap height ~0.70em
    bar_x = numw + 18; right_x = bar_x + 20
    h = cap + 8
    parts = [f'<g fill="{fill}">', f'<g transform="translate(0 {cap:.2f})">{num}</g>',
             f'<rect x="{bar_x:.2f}" y="2" width="2" height="{cap-4:.2f}" opacity=".5"/>',
             f'<g transform="translate({right_x:.2f} {33*0.70:.2f})">{fr}</g>',
             f'<g transform="translate({right_x:.2f} {33*0.70 + 15 + 12:.2f})">{fs}</g>']
    if with_url:
        parts.append(f'<g transform="translate({right_x:.2f} {33*0.70 + 15 + 12 + 15 + 10:.2f})">{url}</g>')
    parts.append("</g>")
    w = max(right_x + frw, right_x + (urlw if with_url else 0)) + 4
    return w, h, "\n".join(parts)

for name, fill, with_url in [("logo.svg", INK, False), ("logo-with-url.svg", INK, True), ("logo-light.svg", CREAM, False)]:
    w, h, body = lockup_svg(fill, with_url)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="2400 Franklin Flex Space">\n'
           f'<title>2400 Franklin Flex Space</title>\n{body}\n</svg>\n')
    (P / name).write_text(svg, encoding="utf-8"); print(name, f"{w:.0f}x{h:.0f}")

# favicon.svg: "2400" mark on Caviar with a red rule
f700 = static(700)
num, numw = text_path(f700, "2400", 21, -0.05)
numw += 0.05 * 21
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="{BG}"/>'
       f'<rect x="8" y="50" width="48" height="4" fill="#C9A86A"/>'
       f'<g fill="#EEE9E0" transform="translate({(64-numw)/2:.2f} 42)">{num}</g></svg>\n')
(P / "favicon.svg").write_text(fav, encoding="utf-8"); print("favicon.svg")

# raster icons via PIL (variable font, weight set by axis)
def pil_font(size, wght):
    f = ImageFont.truetype(str(VF), size); f.set_variation_by_axes([wght]); return f
def icon(px):
    im = Image.new("RGB", (px, px), BG); d = ImageDraw.Draw(im)
    f = pil_font(int(px * 0.33), 700); t = "2400"
    bb = d.textbbox((0, 0), t, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((px - tw) / 2 - bb[0], px * 0.56 - th / 2 - bb[1]), t, font=f, fill="#EEE9E0")
    d.rectangle([px * 0.125, px * 0.80, px * 0.875, px * 0.85], fill="#C9A86A")
    return im
icon(180).save(P / "apple-touch-icon.png", optimize=True)
icon(64).save(P / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("apple-touch-icon.png, favicon.ico")

# og.jpg 1200x630: hero rendering, dark gradient-free band at the bottom with the lockup in cream
hero = Image.open(P / "images" / "door-open-v2-1600.webp").convert("RGB")
W, H = 1200, 630
ratio = max(W / hero.width, H / hero.height)
hero = hero.resize((round(hero.width * ratio), round(hero.height * ratio)), Image.LANCZOS)
hero = hero.crop(((hero.width - W) // 2, (hero.height - H) // 2 - 20, (hero.width - W) // 2 + W, (hero.height - H) // 2 - 20 + H))
band_h = 210
band = Image.new("RGB", (W, band_h), BG)
og = hero.copy(); og.paste(band, (0, H - band_h))
d = ImageDraw.Draw(og)
d.rectangle([0, H - band_h, W, H - band_h + 4], fill="#C9A86A")
num_f = pil_font(104, 700); fr_f = pil_font(40, 500); fs_f = pil_font(21, 600); tag_f = pil_font(22, 500)
def spaced_width(text, font, tracking):
    return sum(d.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)
def spaced(x, y_top, text, font, fill, tracking):
    # draw so the glyphs' cap tops sit exactly at y_top
    off = d.textbbox((0, 0), "H", font=font)[1]
    for ch in text:
        d.text((x, y_top - off), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + tracking
x0 = 64
nb = d.textbbox((0, 0), "2400", font=num_f)              # numerals' own ink box
cap_h = nb[3] - nb[1]
top = H - band_h + 34                                     # cap top of 2400
d.text((x0 - nb[0], top - nb[1]), "2400", font=num_f, fill="#EEE9E0")
nw = nb[2] - nb[0]
bar_x = x0 + nw + 22
d.rectangle([bar_x, top, bar_x + 2, top + cap_h], fill="#8A8782")   # divider = exactly the numerals' cap height
rx = bar_x + 24
fr_box = d.textbbox((0, 0), "H", font=fr_f); fr_cap = fr_box[3] - fr_box[1]
fs_box = d.textbbox((0, 0), "H", font=fs_f); fs_cap = fs_box[3] - fs_box[1]
spaced(rx, top, "FRANKLIN", fr_f, "#EEE9E0", 9.5)                    # FRANKLIN cap top = 2400 cap top
fr_w = spaced_width("FRANKLIN", fr_f, 9.5)
for size in range(18, 34):                                   # largest size whose ~0.3em tracking still fits FRANKLIN's width
    f_try = pil_font(size, 500)
    if spaced_width("FLEX SPACE", f_try, 0.3 * size) > fr_w: break
    fs_f = f_try
fs_box = d.textbbox((0, 0), "H", font=fs_f); fs_cap = fs_box[3] - fs_box[1]
fs_track = (fr_w - spaced_width("FLEX SPACE", fs_f, 0)) / (len("FLEX SPACE") - 1)
spaced(rx + 1, top + cap_h - fs_cap, "FLEX SPACE", fs_f, "#EEE9E0", fs_track)  # FLEX SPACE baseline = 2400 baseline
tag = "Flex bays for lease · Lawrence, Kansas · 2400franklin.com"
tw = d.textlength(tag, font=tag_f)
d.text((x0, H - 50), tag, font=tag_f, fill="#A39D94")
og.save(P / "images" / "og.jpg", "JPEG", quality=82, optimize=True, progressive=True)
print("og.jpg", og.size)
