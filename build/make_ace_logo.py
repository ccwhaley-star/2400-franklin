# images/tenants/ace-bail-bonds.png/.webp: Ace Bail Bonds sign lettering redrawn sharp (owner's photo of the
# sign was 136x27). Tall condensed "ACE" + bold "BAIL BONDS", no "Inc." (owner, 2026-11-22).
# Run: python -I build/make_ace_logo.py
import pathlib
from PIL import Image, ImageDraw, ImageFont
P = pathlib.Path(__file__).resolve().parent.parent
INK = (11, 15, 28, 255)
F = pathlib.Path(r"C:\Windows\Fonts")
cap = 120                                              # cap height of BAIL BONDS, px
bold = ImageFont.truetype(str(F / "arialbd.ttf"), round(cap / 0.716))
narrow = ImageFont.truetype(str(F / "ARIALNB.TTF"), round(cap / 0.716))

def word(text, font, track):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = sum(d.textlength(c, font=font) for c in text) + track * (len(text) - 1)
    top = d.textbbox((0, 0), "H", font=font)[1]
    im = Image.new("RGBA", (round(w) + 20, cap + 4), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); x = 0
    for c in text:
        dd.text((x, -top), c, font=font, fill=INK); x += d.textlength(c, font=font) + track
    return im.crop(im.getbbox())

ace = word("ACE", narrow, -cap * 0.06)
ace = ace.resize((round(ace.width * 1.0), round(cap * 1.42)), Image.LANCZOS)   # sign's ACE stands taller
bb = word("BAIL BONDS", bold, cap * 0.03)
pad, gap = 12, round(cap * 0.4)
H = ace.height + pad * 2
W = pad * 2 + ace.width + gap + bb.width
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.alpha_composite(ace, (pad, pad))
base = pad + (ace.height + bb.height) // 2                 # BAIL BONDS centred on the tall ACE, as on the sign
out.alpha_composite(bb, (pad + ace.width + gap, base - bb.height))
out.save(P / "images/tenants/ace-bail-bonds.png", optimize=True)
small = out.resize((360, round(H * 360 / W)), Image.LANCZOS)                # ~2x its on-page size
small.save(P / "images/tenants/ace-bail-bonds.webp", quality=90, method=6)
print(out.size, small.size)
