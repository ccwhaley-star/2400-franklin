"""Pull bay availability from Cubby into data/bays.json, then rebuild index.html.

Usage, from the site folder:   CUBBY_STOREFRONT_KEY=... python build/cubby_sync.py
Run hourly by .github/workflows/cubby-sync.yml, which commits any change (Netlify then deploys).

Cubby lists each space as a "pricing group". A bay follows Cubby when it is matched to one:
  - by an explicit "cubby": "pg_..." field on the bay in bays.json, or
  - by name: "Suite H" -> bay H, "Suite F-G" / "Bays F–G" -> bays F and G.
What Cubby can change (and nothing else; names, blurbs and sizes stay as written):
  - occupied: true  -> the bay is shown as Leased
  - occupied: false -> an Open/Leased bay is shown as Open. A "soon" bay stays soon
    (opening dates are not in Cubby), so listing F–G in Cubby early does not show it as open.
Bays Cubby does not list are left exactly as bays.json has them. If Cubby cannot be
reached or answers oddly, nothing is changed (fail closed).
When any status changes, the phone bar line ("Bay H · open now") is rewritten to match.
"""
import json, os, re, subprocess, sys, pathlib, urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "bays.json"
SLUG = "2400-franklin"
URL = f"https://api.cubbystorage.com/sf/facilities/{SLUG}"
ORDER = "ABCDEFGH"
MONTHS = {m: i for i, m in enumerate("january february march april may june july august "
                                      "september october november december".split(), 1)}
SEASONS = {"spring": 3, "summer": 6, "fall": 9, "autumn": 9, "winter": 12}


def fetch(key):
    req = urllib.request.Request(URL, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def groups_of(fac):
    seen = {}
    for c in fac.get("collections") or []:
        for g in c.get("pricingGroups") or []:
            if isinstance(g, dict) and g.get("extId") and isinstance(g.get("occupied"), bool):
                seen[g["extId"]] = g
    return list(seen.values())


def letters_for(name):
    m = re.search(r"\b(?:suite|bays?)\s+([A-H])(?:\s*[-–]\s*([A-H]))?\b", name or "", re.I)
    if not m:
        return []
    a, b = m.group(1).upper(), (m.group(2) or m.group(1)).upper()
    return [ORDER[i] for i in range(ORDER.index(a), ORDER.index(b) + 1)]


def when_key(when):
    s = (when or "").lower()
    y = re.search(r"(20\d\d)", s)
    mo = next((v for k, v in {**MONTHS, **SEASONS}.items() if k in s), 6)
    return (int(y.group(1)) if y else 9999, mo)


def sticky(bays):
    """Phone bar line from the statuses: what is open now, and the next opening."""
    def label(letter):
        b = bays[letter]
        return f"Bays {b['unit']}" if b.get("unit") else f"Bay {letter}"
    open_now, soon = [], []
    for k in ORDER:
        b = bays[k]
        lab = label(k)
        if b["status"] == "available" and lab not in open_now:
            open_now.append(lab)
        if b["status"] == "soon" and lab not in [s[0] for s in soon]:
            soon.append((lab, b))
    if open_now:
        title = (" and ".join(open_now)) + " · open now"
    else:
        title = "Ask about the next bay"
    note = ""
    if soon:
        lab, b = min(soon, key=lambda s: when_key(s[1].get("when")))
        when = (b.get("when") or "").split("·")[0].strip()
        size = f" ({b['sf']})" if b.get("sf") else ""
        note = f"{lab.replace('Bays ', '')}{size} opens {when}" if b.get("unit") else f"{lab}{size} opens {when}"
    return {"title": title, "note": note}


def main():
    key = os.environ.get("CUBBY_STOREFRONT_KEY")
    if not key:
        print("CUBBY_STOREFRONT_KEY is not set; skipping (add it as a repo secret to turn the sync on)")
        return
    try:
        fac = fetch(key)
    except Exception as e:
        print(f"Cubby not reachable ({e}); bays.json left as is")
        return
    groups = groups_of(fac)
    if not groups:
        print("Cubby returned no pricing groups; bays.json left as is")
        return

    data = json.loads(DATA.read_text(encoding="utf-8"))
    bays = data["bays"]
    by_ext = {b.get("cubby"): k for k, b in bays.items() if b.get("cubby")}
    changed = []
    for g in groups:
        letters = [by_ext[g["extId"]]] if g["extId"] in by_ext else letters_for(g.get("name"))
        letters = [l for l in letters if l in bays]
        if not letters:
            print(f"  Cubby group not matched to a bay: {g.get('name')!r} ({g['extId']})")
            continue
        for l in letters:
            b = bays[l]
            if g["occupied"]:
                new = "leased"
            elif b["status"] == "soon":
                new = "soon"
            else:
                new = "available"
            if new == b["status"]:
                continue
            old = b["status"]
            b["status"] = new
            if new == "leased":
                b["tag"], b["when"] = "Leased", "Leased" + (f" · {b['sf']}" if b.get("sf") else "")
            else:
                b["tag"], b["when"] = "Open", "Available now"
            changed.append(f"{l}: {old} -> {new} ({g.get('name')})")

    if not changed:
        print(f"No change ({len(groups)} Cubby group(s) checked)")
        return
    data["sticky_bar"] = sticky(bays)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Changed:\n  " + "\n  ".join(changed))
    print(f"Phone bar: {data['sticky_bar']['title']} / {data['sticky_bar']['note']}")
    subprocess.run([sys.executable, str(HERE / "build.py")], check=True, cwd=HERE)


if __name__ == "__main__":
    main()
