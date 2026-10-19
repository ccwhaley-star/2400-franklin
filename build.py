"""Render data/bays.json into index.html.

Usage, from this folder:   python build.py
Then commit index.html. Netlify serves the committed file; it does not run this.

The HTML between each pair of <!-- data:NAME --> ... <!-- /data:NAME --> markers is
replaced. Everything else in index.html is left alone.
"""
import json, re, sys, html, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data" / "bays.json").read_text(encoding="utf-8"))
page = (HERE / "index.html").read_text(encoding="utf-8")

e = html.escape
status_class = {"available": "open", "soon": "soon", "leased": ""}

# --- the A-H drawing: each bay takes the status of the row it belongs to
bay_status = {}
for row in data["rows"]:
    for b in row["bays"]:
        bay_status[b] = row["status"]
strip = "\n".join(
    f'          <div class="bay{(" " + status_class[bay_status.get(b, "leased")]).rstrip()}">{b}</div>'
    for b in "ABCDEFGH")

# --- the rows
rows = "\n".join(
    f'        <li class="{status_class[r["status"]]}"><span class="id">{e(r["label"])}</span>'
    f'<span class="who-txt">{e(r["description"])}</span><span class="pill">{e(r["pill"])}</span></li>'
    for r in data["rows"])
rows = rows.replace(' class=""', "")

# --- existing businesses
biz = []
for b in data["existing_businesses"]:
    if b.get("logo"):
        mark = f'<img src="{e(b["logo"])}" width="168" height="141" alt="{e(b["name"])} logo" loading="lazy">'
    else:
        mark = f'<span class="mark" aria-hidden="true">{e(b["mark"])}</span>'
    name = f'<a href="{e(b["url"])}" target="_blank" rel="noopener">{e(b["name"])}</a>' if b.get("url") else e(b["name"])
    biz.append(f'          <li>{mark}<div><b>{name}</b><span>{e(b["line"])}</span></div></li>')
biz = "\n".join(biz)

blocks = {
    "headline": f'      <h2>{e(data["headline"])}</h2>',
    "strip": strip,
    "rows": rows,
    "note": f'      <p class="note">{e(data["note"])}</p>',
    "businesses": biz,
}

missing = []
for name, body in blocks.items():
    pat = re.compile(rf"(<!-- data:{name} -->\n).*?(\n\s*<!-- /data:{name} -->)", re.S)
    if not pat.search(page):
        missing.append(name); continue
    page = pat.sub(lambda m: m.group(1) + body + m.group(2), page, count=1)

if missing:
    sys.exit(f"markers not found in index.html: {', '.join(missing)}")

(HERE / "index.html").write_text(page, encoding="utf-8")
open_now = [r["label"] for r in data["rows"] if r["status"] == "available"]
print(f"index.html updated: {len(data['rows'])} rows, open now: {', '.join(open_now) or 'none'}")
