# Vindkollen Project Status — 2026-05-22

## Cycle Summary: Lead Capture & Conversion System v1

This cycle audited the live site, fixed critical broken links and a silent
backend failure, and shipped the first version of an end-to-end lead capture
funnel anchored on the ersättningskalkylator.

### Critical bugs fixed
- **`/api/lead` was a no-op** (body literally `pass`). Every email submitted
  through the hero/footer forms was silently discarded — returned `null` with
  HTTP 200. Now persists to Postgres with idempotent upsert on email.
- **Sitemap.xml not served** — no FastAPI route existed. Added route +
  corrected domain (`vindkollen.se` → `vindkoll.se`).
- **Broken nav links** — homepage and kalkylator linked to
  `/ersattning-for-vindkraft.html` and `/kalkylator.html` which 404'd. Added
  clean URL routes (`/kalkylator`, `/ersattning-for-vindkraft`,
  `/guider/nackdelar-med-vindkraft`) plus `.html` aliases for back-compat.
- **`#about` anchor** referenced from hero nav had no matching section. Nav
  rewritten with stable destinations only.
- **Schema.jsonld orphaned** — JSON-LD existed in the repo but was never
  embedded in HTML. Now inlined in every page (Organization, WebSite,
  WebPage, Article, FAQPage, HowTo).

### High-impact improvement: enriched lead funnel on the kalkylator
1. The kalkylator now uses the **official trappstegsmodell** (2,5 / 2,0 / 1,5
   / 1,0 / 0,5 promille per band of verkshöjder) from prop. 2025/26:239 —
   replacing the previous linear approximation. More accurate, more
   defensible, and a thought-leadership signal.
2. After the result is computed, a **"Personlig marknadsrapport"** card
   appears asking for name, e-post, kommun and (optional) fastighetsadress.
3. Submissions hit the new `POST /api/lead/report` endpoint, which persists
   the contact **plus the full calc context** (elområde, distance, height,
   turbine count, estimated kr/year, promille tier) into
   `vindkollen_leads` — giving sales a rich pre-qualified record.
4. A public `GET /api/stats/leads` endpoint powers a social-proof counter
   on the homepage hero ("Över 1 200 markägare & närboende har beräknat …").

### Content / thought leadership
- **New page**: `/guider/nackdelar-med-vindkraft` — the existing markdown
  draft is now a styled HTML page targeting the top rising Swedish keyword
  in trends.txt (+194 400 %). Includes FAQPage schema.
- **Rewritten markägarguide**: `/ersattning-for-vindkraft` was a light-theme
  page with a fake "Annonsplats" placeholder and zero lead capture. Now
  matches the dark design system, has Article + FAQPage schema, and a
  proper "Markägarens checklista" lead magnet at the bottom.

### Hygiene
- Sitemap rewritten with `vindkoll.se`, weekly/monthly changefreq, and the
  new pages.
- `robots.txt` (both root and static copies) updated to the absolute sitemap
  URL.
- `generate_sitemap.py` rewritten to reflect the production layout — earlier
  version pointed at `projects/vindkollen/...` paths that don't exist in
  this repo.

## Next cycle
1. Configure the email automation that turns captured leads into actual
   delivered PDF reports (currently we collect, but the email pipeline
   isn't wired).
2. Add a GA4 (or Plausible) tracking snippet and connect it to AgentSim
   for next cycle's traffic analysis.
3. Publish the second high-value markdown that's still unused:
   `vindkraftsersattning_guide.md`, as a `/guider/vindkraftsersattning-2026`
   pillar page.
4. A/B test hero CTA: "Beräkna din ersättning" vs. "Få en kostnadsfri
   rapport".
