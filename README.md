# 2400franklin.com

One-page leasing site for **2400 Franklin Flex Spaces**, 2400 Franklin Rd, Lawrence, KS 66046
(a Flint Hills Capital property; sister of Free State Storage). Static HTML, no build step,
hosted on Netlify.

| | |
|---|---|
| Netlify site | `2400-franklin` (id `0175550f-254b-42df-ae4b-75dea2f64c8c`), https://2400-franklin.netlify.app |
| Production domain | https://2400franklin.com (www and 2400franklinrd.com redirect to it, see `netlify.toml`) |
| Inquiries | Netlify Forms, form name `inquiry`, delivered to leasing@2400franklin.com |
| Design | Option D of the mockups in `../2400-franklin-mockups/` (dark "Shop Floor" + floor plan + site map) |

## Update availability, pricing or the existing-businesses row

Everything that changes lives in **`data/bays.json`**. Edit it, then from this folder:

```bash
python build.py
```

That rewrites the marked blocks in `index.html` (headline, the A–H drawing, the bay rows, the
note, the terms table, the existing-businesses row). Commit `index.html` and deploy.

- A row's `status` is `available`, `soon` or `leased`; `pill` is the text shown (e.g. "Spring 2027").
- `bays` lists which letters a row covers so the drawing colors them the same way.
- To show a tenant logo, drop a grayscale-friendly PNG/WebP in `images/tenants/` and set the row's
  `logo` to its path (`/images/tenants/kutz.png`); set it to `null` to show the text mark instead.
- FAQ and all other copy are edited directly in `index.html`. Keep the FAQ answers and the
  `FAQPage` JSON-LD in the `<head>` in sync.

## Deploy

```bash
netlify deploy --prod --no-build --dir=C:/Github_folder/2400-franklin --site 0175550f-254b-42df-ae4b-75dea2f64c8c
```

Always pass `--site` and `--dir` explicitly. Netlify does not build anything; it publishes the folder.

## Point the domain (GoDaddy → Netlify)

1. Register **2400franklin.com** and **2400franklinrd.com** (neither was registered as of 2026-10-18).
2. Netlify → this site → **Domain management** → add `2400franklin.com`, `www.2400franklin.com`,
   `2400franklinrd.com` and `www.2400franklinrd.com`. Set `2400franklin.com` as the primary domain.
3. At GoDaddy, for **each** of the two domains, set DNS to:

   | Type | Name | Value |
   |---|---|---|
   | A | `@` | `75.2.60.5` |
   | CNAME | `www` | `2400-franklin.netlify.app` |

   Delete GoDaddy's default parked A record and any "Forwarding" on the domain first.
   (Alternative: move nameservers to Netlify DNS, `dns1.p0X.nsone.net` etc., shown in Netlify when
   you add the domain. Either works; the A/CNAME route keeps the domain fully at GoDaddy.)
4. Netlify issues the Let's Encrypt certificate itself once DNS resolves (usually under an hour).
   HTTPS and the www → apex and 2400franklinrd → 2400franklin redirects are already in `netlify.toml`.

## Form delivery

- `index.html` posts to Netlify Forms (`data-netlify="true"`, honeypot `bot-field`). Form
  detection is turned on for the site. The hidden `subject` field becomes the email subject:
  `2400 Franklin inquiry: {Business or Name} — {Space needed}`.
- Notification: Netlify → Forms → **Form notifications** → email to `leasing@2400franklin.com`.
  Until that mailbox exists, submissions still sit in the Netlify Forms dashboard.
- Spam: honeypot + Netlify's filtering. No CAPTCHA unless spam becomes a problem.

## What is in the folder

```
index.html         the page (inline CSS/JS; blocks between <!-- data:… --> are generated)
data/bays.json     availability, terms, existing businesses
build.py           renders data/bays.json into index.html
images/            renderings as WebP + JPG at 900 and 1600 wide, og.jpg (1200×630), tenants/
fonts/             Montserrat variable woff2 (latin), self-hosted
logo.svg           sign lockup as vector paths (also logo-light.svg, logo-with-url.svg for the sign vendor)
favicon.svg / favicon.ico / apple-touch-icon.png
netlify.toml       redirects (www, 2400franklinrd.com) and cache/security headers
robots.txt, sitemap.xml, llms.txt
build/shot.py      headless-Chrome screenshot helper used for QA
```

All three building images are AI renderings of planned improvements and are captioned "(rendering)".
The frontage rendering has its tenant-sign panels blanked; regenerate it before using it anywhere else.

## Launch checklist (owner)

- [ ] Register 2400franklin.com and 2400franklinrd.com; point DNS as above.
- [ ] Create the **leasing@2400franklin.com** mailbox, then add the Netlify form notification.
- [ ] Decide whether rent stays visible (currently "From $950/mo").
- [ ] Phone line and tour hours: none yet. When they exist, add `telephone` and `openingHours` to the
      LocalBusiness JSON-LD, a tap-to-call button, and hours in the Inquire section.
- [ ] Kutz Family Hair Care logo → `images/tenants/kutz.png`, then set `logo` in `data/bays.json`.
      Confirm all three businesses are OK being shown.
- [ ] Regenerate `frontage.jpg` with clean sign panels (not currently on the page).
- [ ] Sign vendor: `logo-with-url.svg` has the URL as the third line of the lockup. Swap in the sign's
      exact font if it is not Montserrat.
- [ ] Google Business Profile for 2400 Franklin (separate phone line from Free State Storage); link
      the site; keep name/address identical to the footer and JSON-LD.
- [ ] Keep "Newly renovated" until renovations are visibly done; switch to "Renovations underway" if
      launching earlier.
- [ ] Cookieless analytics if wanted (Plausible or Cloudflare Web Analytics); none installed.

## QA notes (2026-10-18)

Lighthouse mobile on the Netlify preview: Performance 100, Accessibility 100, Best Practices 100,
SEO 100. First load 181 KB. Checked at 360 px (no sideways scroll, 44 px tap targets, sticky
"Ask about a bay" bar hides over the form) and 1440 px, in the dark design and the light variant.
