---
name: restaurant-research
description: "Find restaurants matching dish + setting criteria (view, rooftop, ambience) and verify menus/prices from primary sources: official menu PDFs, Wayback archives, hotel sites. Produces verdict-first reports with honest caveats."
version: 1.0.0
metadata:
  hermes:
    tags: [restaurants, food, menus, research, verification, travel, dining]
    related_skills: [google-workspace, grounded-citations]
---

# Restaurant & Menu Research

Use when the user asks to find restaurants by dish + setting (e.g. "views that serve beef pepper steak"), verify what's actually on a menu, check prices, or produce a dining report.

## Core principle
Blogs, TripAdvisor blurbs, and search snippets describe menus loosely — they are NOT proof a dish exists today. Verify dish, price, and view claims against PRIMARY sources: the restaurant's own menu (PDF or page), official site "Basic Information", or a Wayback snapshot. When you cannot verify, say so explicitly and give the phone number to confirm.

## Workflow

1. **Discover candidates** — web_search combos: `<dish> <city>`, `best restaurants with a view <city>`, `<city> steakhouse`, plus local food guides (yamu.lk for Colombo). For Colombo buffets specifically, the two highest-yield roundups are **Pulse.lk** (`pulse.lk/everythingelse/colombo-buffet-roundup-<year>/`, annual snapshots) and **Happening Colombo** (`happeningcolombo.com/offer-by-type/lunch`, rolling current listings) — both curl-friendly. Collect venue names + official sites.
2. **Fetch menus from official sites**:
   - `curl -sL -A "Mozilla/5.0 ... Chrome/120..." <page> -o page.html` — hotel sites often 200 but JS-rendered, or 403/503 to curl (Galle Face 403, Mount Lavinia 503 → use `browser_navigate` instead).
   - If the HTML has no menu text, hunt for menu **PDF links**: `grep -oE 'href="[^"]*\.pdf[^"]*"' page.html`
   - Menu PDFs commonly live on CDN/upload domains separate from the main site: `sitecore-cd.<brand>.com`, `<hotel>.eme-devops.com`, `wp-content/uploads/` — grep everything.
   - In the browser (JS pages), extract links via console: `Array.from(document.querySelectorAll('a')).filter(a => /menu/i.test(a.textContent)).map(a => ({text: a.textContent.trim(), href: a.href}))`
3. **Extract PDF text** — `pdftotext`/pymupdf are often absent; pypdf in the Hermes venv works:
   - One-time: `~/.hermes/hermes-agent/venv/bin/pip install pypdf`
   - Then: `PdfReader(url_path)` → `'\n'.join(p.extract_text() or '' for p in r.pages)` → grep lines for dish keywords (pepper, steak, etc.).
   - Image-only menus extract ~0 chars — do NOT guess the dish; report "menu is image-only, could not verify".
4. **Dead or bot-blocked sites → Wayback Machine**:
   - Find archived menu PDFs: `curl "https://web.archive.org/cdx/search/cdx?url=<domain>*&filter=statuscode:200&filter=mimetype:application/pdf&collapse=urlkey&limit=40"`
   - Fetch original bytes: `https://web.archive.org/web/<timestamp>id_/<original_url>` (the `id_` suffix matters — without it you get the HTML wrapper).
5. **Verify the SETTING/VIEW claim explicitly** — this is where search results lie. Check the official page's location info (floor/level, rooftop, oceanfront vs interior room). Example: "Capital Bar & Grill" sounded like a high-floor viewpoint but its own page said **Level 2**. Oceanfront hotel ≠ window table. Rooftop ≠ serves dinner (some rooftops are cocktails/tapas only).
6. **Write the report** — verdict-first (top pick + why), then per venue: exact dish + price + view description + contact/booking + honest caveats (menu date, unverified status). Include an "excluded" list with reasons (no view, tapas-only, site down).
7. **Email deliverable** — use the google-workspace skill flow: `setup.py --check`, `google_api.py gmail send --to <addr> --subject ... --body "$(cat body.html)" --html`, then **verify** with `gmail search "subject:(...) newer_than:1d"`. Run with the Hermes venv python (`~/.hermes/hermes-agent/venv/bin/python`), never system python (PEP 668).

## Pitfalls
- Hotel sites are the worst to scrape: JS menus, bot protection, PDF-only menus. Budget for browser + PDF hunting; don't conclude "not on the menu" from an empty HTML page.
- Prices: always note the menu date and that ~10% service charge + taxes apply (Sri Lanka) — menus change, reconfirm at booking.
- Buffet/price sources disagree by design: annual roundups (Pulse) lag, rolling listings (Happening) drift, official sites are current, and **hotel Facebook/Instagram posts are often the MOST current price source** (official pages sometimes omit buffet prices entirely). Quote each price WITH its verification date and flag conflicts instead of picking one (real case: Graze Kitchen lunch LKR 6,888 Apr 2025 vs 8,888 in 2026 listings; Quizine 5,800 vs 6,900). Check hotel social + promo aggregators (mypromo.lk, americanexpress.lk offers) for recurring 20–25% bank-card buffet discounts before quoting full price.
- "Pepper steak" is ambiguous: Sri Lankan local style (beef in peppery gravy, mid-range spots) vs Western steak au poivre / pepper-crust + peppercorn-cream sauce (fine dining). State which interpretation you used.
- A search snippet that claims a view/dish may be stale or wrong — the restaurant's own current PDF beats any third-party description.

## References
- `references/colombo-steak-venues.md` — verified Colombo (Sri Lanka) steak-with-view venues: dishes, prices, contacts, menu PDF URLs, verification dates (Aug 2026).
- `references/colombo-lunch-buffets.md` — verified Colombo hotel lunch-buffet venues (4–5★): prices, hours, phones, specials, source-conflict notes, verification dates (Sep 2026).
