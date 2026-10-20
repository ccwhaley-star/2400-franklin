"""Render data/bays.json into index.html.

Usage, from this folder:   python build.py
Then commit index.html. Netlify serves the committed file; it does not run this.

The HTML between each pair of <!-- data:NAME --> ... <!-- /data:NAME --> markers is
replaced. Everything else in index.html is left alone.
  baydata     the JSON the bay chooser reads (tiles, building overlay, detail panel)
  businesses  the "Existing businesses" logo strip under the hero
  bar         the phone sticky bar text
"""
import json, re, sys, html, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data" / "bays.json").read_text(encoding="utf-8"))
page = (HERE / "index.html").read_text(encoding="utf-8")
e = html.escape

STATUS = {"available": "open", "soon": "soon", "leased": "leased"}
bays = {}
for letter, b in data["bays"].items():
    if b["status"] not in STATUS:
        sys.exit(f"bay {letter}: status must be available, soon or leased")
    bays[letter] = {"s": STATUS[b["status"]], "tag": b["tag"], "status": b["when"],
                    "name": b["name"], "mezz": bool(b["mezzanine"]), "p": b["blurb"]}
baydata = ('<script type="application/json" id="bay-data">'
           + json.dumps(bays, ensure_ascii=False).replace("</", "<\\/") + "</script>")

def logo_size(path):
    try:
        from PIL import Image
        with Image.open(HERE / path.lstrip("/")) as im:
            return im.size
    except Exception:
        return (400, 200)

biz = []
for b in data["existing_businesses"]:
    w, h = logo_size(b["logo"])
    img = f'<img src="{e(b["logo"])}" width="{w}" height="{h}" alt="{e(b["name"])}" loading="lazy">'
    if b.get("url"):
        img = f'<a href="{e(b["url"])}" target="_blank" rel="noopener">{img}</a>'
    biz.append(f"        <li>{img}</li>")

bar = data["sticky_bar"]
blocks = {
    "baydata": baydata,
    "businesses": "\n".join(biz),
    "bar": f'<div class="bay-line"><b>{e(bar["title"])}</b>{e(bar["note"])}</div>',
}

missing = []
for name, body in blocks.items():
    pat = re.compile(rf"(<!-- data:{name} -->\n?).*?(\n?\s*<!-- /data:{name} -->)", re.S)
    if not pat.search(page):
        missing.append(name); continue
    page = pat.sub(lambda m: m.group(1) + body + m.group(2), page, count=1)
if missing:
    sys.exit(f"markers not found in index.html: {', '.join(missing)}")

(HERE / "index.html").write_text(page, encoding="utf-8")
open_now = [k for k, b in data["bays"].items() if b["status"] == "available"]
print(f"index.html updated: {len(bays)} bays, open now: {', '.join(open_now) or 'none'}")
