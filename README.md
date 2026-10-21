# 2400franklin.com

One-page leasing site for **2400 Franklin Flex Space**, 2400 Franklin Rd, Lawrence, KS 66046
(a Flint Hills Capital property; sister of Free State Storage). Static HTML, no build step,
hosted on Netlify.

| | |
|---|---|
| Netlify site | `2400-franklin` (id `0175550f-254b-42df-ae4b-75dea2f64c8c`), https://2400-franklin.netlify.app, git-linked to github.com/ccwhaley-star/2400-franklin (push to `main` deploys) |
| Production domain | https://2400franklin.com (live with HTTPS since 2026-10-20; www redirects to it; 2400franklinrd.com will too once registered, see `netlify.toml`) |
| Inquiries | Netlify Forms, form name `inquiry`. Email notifications go to ccwhaley@gmail.com until the leasing@2400franklin.com mailbox exists (switch the hook in Netlify → Forms → Form notifications then). Phone (785) 727-2112 |
| Design | Option F ("Atelier") of the mockups in `../2400-franklin-mockups/`, live from 2026-10-20 |

## Update availability or the existing-businesses row

Everything that changes lives in **`data/bays.json`**. Edit it, then from this folder:

```bash
python build.py
```

That rewrites three marked blocks in `index.html`: the bay data the chooser reads (tiles, building
overlay, detail panel), the "Existing businesses" logo strip, and the phone sticky bar. Commit
`index.html` and push.

- Each bay has `status` (`available`, `soon`, `leased`), a short `tag` shown under the letter
  (`Open`, `Dec 2026`, `Leased`), a longer `when` for the detail panel, a `name`, a `blurb`, and
  `mezzanine`. Only bays with `mezzanine: true` show the mezzanine office and the flex-suite photo.
- `sticky_bar` is the line on the phone bar ("Bay H · open now / F and G open December 2026").
- Tenant logos go in `images/tenants/` and are listed under `existing_businesses` with a link.
- All other copy (headline, FAQ, neighborhood list) is edited directly in `index.html`. Keep the FAQ
  answers and the `FAQPage` JSON-LD in the `<head>` in sync.

## Deploy

```bash
netlify deploy --prod --no-build --dir=C:/Github_folder/2400-franklin --site 0175550f-254b-42df-ae4b-75dea2f64c8c
```

The site is git-linked: pushing to `main` deploys automatically. The CLI command above is the manual fallback; always pass `--site` and `--dir` explicitly. Netlify does not build anything; it publishes the folder.

## Point the domain (Cloudflare → Netlify)

2400franklin.com was registered at **Cloudflare** on 2026-10-18 (nameservers vin/wren.ns.cloudflare.com).
The Netlify site already has `2400franklin.com` as its primary domain and `www.2400franklin.com` as an alias.

1. Cloudflare → 2400franklin.com → **DNS → Records**, add (proxy status **DNS only**, grey cloud, on both):

   | Type | Name | Content | Proxy |
   |---|---|---|---|
   | A | `@` | `75.2.60.5` | DNS only |
   | CNAME | `www` | `2400-franklin.netlify.app` | DNS only |

   Keep the records **DNS only**. With the orange-cloud proxy on, Netlify cannot issue the
   certificate and visitors get Cloudflare/Netlify errors.
2. Cloudflare → **SSL/TLS** → set the mode to **Full** (harmless with DNS-only records, and avoids
   redirect loops if the proxy is ever switched on).
3. Netlify → Domain management → **Verify DNS configuration**, then **Provision certificate** if it has
   not done so on its own (usually within an hour of the records resolving). HTTPS, the www → apex
   redirect and the 2400franklinrd.com redirect are already in `netlify.toml`.
4. **2400franklinrd.com** (not registered yet): register it at Cloudflare too, add the same two records,
   and add `2400franklinrd.com` + `www.2400franklinrd.com` as domain aliases on the Netlify site.

Until step 1 is done, 2400franklin.com does not resolve at all; after it, a Netlify "Not found" page
means the domain is not attached to the site (it is), and a certificate warning means step 3 is pending.

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

- [x] Register 2400franklin.com (done 2026-10-18, Cloudflare). [x] DNS records added and HTTPS issued (2026-10-20). [ ] Register 2400franklinrd.com.
- [ ] Create the **leasing@2400franklin.com** mailbox, then add the Netlify form notification.
- [x] Rent and terms are off the site (owner, 2026-10-19). Pricing is quoted by email.
- [x] Phone line: (785) 727-2112 (on the page, footer and LocalBusiness JSON-LD, 2026-10-21). [ ] Tour hours: none yet. When they exist, add `telephone` and `openingHours` to the
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
