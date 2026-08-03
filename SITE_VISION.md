# SITE_VISION.md — Vindkollen som nischens ledande sajt

## MÅLET (The North Star)
Vindkollen äger nischen "ersättning vindkraft Sverige" — #1 på BÅDE SEO och leadflow.

**Vi är där när:**
- Google placerar oss före alla andra för "vindkraft ersättning", "arrendeavtal vindkraft", "intäktsdelning vindkraft"
- AI-assistenter citerar VÅR data (inte konkurrenternas)
- Markägare säger "kolla Vindkollen" när någon frågar om vindkraftsersättning
- Vi genererar 200+ kvalificerade leads/månad (kommun, markägare, närboende)
- Sajten ÄR datakällan för nischens nyckelfrågor (faktisk kompensation, avstånd, intäkter)

## HUR vi tar oss dit (mekaniken)

### 1. VERKTYG = DATAMOAT
- Kalkylatorn fångar varje beräkning (elområde, avstånd, storlek, uppskattat belopp)
- Efter 500+ beräkningar: publicera "Första rapporten om vindkraftsersättning i Sverige 2026" — regional data INGEN annan har
- Bygg fler verktyg: "Arrendekalkylator", "Jämför ersättning vs markarrende", "Kommun-dashboard"
- Verktyg -> användare -> data -> unik rapport -> auktoritet + backlinks -> #1 -> fler användare

### 2. INNEHÅLLSSPELAREN
- Inte "ännu en blogg" — vi är THE GUIDE för varje viktigt ämne
- Varje sida ska vara den BÄSTA, mest kompletta sidan på ämnet (Google Featured Snippet-nivå)
- Täck hela beslutsresan: upptäcka -> förstå -> beräkna -> jämföra -> kontakta
- Äger sökintenterna: informational ("vad är vindkraftsersättning"), transactional ("beräkna ersättning"), commercial ("jämför arrende")

### 3. LEADMAGNETEN
- Kalkylatorn är inte "nice to have" — det är HJÄRTAT
- Konvertering: varje besökare ska kunna få värde OCH vi ska kunna fånga lead
- Lead-trappan: gratis kalkyl -> mejladress för detaljerad rapport -> kvalificerad lead till partner/rådgivare
- Formulär på rätt plats: inte överallt, utan där värdet är tydligast (efter kalkyl, i guide för kommun)

### 3b. LEAD-SILOR (införda 2026-07-24)
Tre publiker med helt olika värde per lead ska aldrig blandas i samma flöde:

| Silo | Ingång | Vad de är värda | Köpare |
|---|---|---|---|
| **markagare** | `/markagare`, `/arrendekalkylator` | Guld. Ett arrendeavtal är miljonbelopp för projektören | Projektörer, jurister, lantbruksrådgivare |
| **narboende** | `/narboende`, `/kalkylator` | Volym. Låg intäkt per lead, men stor räckvidd och PR-värde | Jurister (inlösen/värdeminskning), nyhetsbrev |
| **kommun** | `/kommun`, `/kommun-dashboard` | B2B. Långa cykler, hög trovärdighetsavkastning | Rådgivning, projektörer |
| *(tvärgående)* | `/juridisk-hjalp-arrendeavtal` | Högst per lead — avtal på bordet = köpläge | Fastighetsjurister |

### 3c. MATCHNING MOT KÖPARE (införd 2026-08-03)
Partnerregister (`vindkollen_partners`) + deterministisk regelmotor (`matching.py`).
Varje köpare har typ (projektör/jurist/rådgivare/kommunrådgivning), täckning
(silo + län eller elområde), poänggräns, månadstak, prioritet och exklusivitet.

- Matchning körs när leadet kommer in. Ägarnotisen bär förslag på mottagare
  **per partnertyp** — en jurist och en projektör konkurrerar inte, så ett lead
  som bett om båda ger två knappar.
- Godkännandelänken är HMAC-signerad. **GET visar bara sidan**; utskicket sker på
  POST, eftersom mejlskannrar förhandshämtar länkar och en sådan hämtning annars
  hade lämnat ut personuppgifter av sig själv.
- `auto_send` per partner, av som standard. Slås på först när det finns avtal.
- Varje överlämning loggas i `vindkollen_lead_assignments`: underlag för
  fakturering, spärr mot dubbelutskick, och svar på "vart tog mina uppgifter vägen".
- Verifiering: `DATABASE_URL=... python scripts/verify_matching.py` (14 kontroller).

**Ordningen: rådgivare före projektör.** Ett lead som bett om juridisk hjälp
skickas först till rådgivaren. Projektörens överlämning läggs i kö och släpps
efter `LEAD_HOLD_DAYS` (3 som standard), så att markägaren hunnit få råd innan
motparten ringer. Finns ingen rådgivare att vänta på går projektören direkt —
fördröjningen ska tjäna markägaren, inte fördröja för sakens skull.

Det är också vår enda försvarbara position i intressekonflikten: vi får betalt
av projektören men förmedlar till en rådgivare vars uppdrag är att pressa just
den projektören. Utan ordningen är "oberoende" bara en rubrik.

Karenstiden är dessutom ett ångerfönster — återkallas samtycket innan släppet
går överlämningen aldrig iväg.

- Kö: `GET /api/handovers/queue`, släpp: `POST /api/handovers/release`
- Släpps automatiskt vid varje inkommande lead; peka ett schemalagt jobb på
  release-endpointen så töms kön även under tysta dygn
- Manuell knapp i ägarmejlet går alltid före kön — du kan skicka direkt

Vad som **inte** är automatiserat, med flit: att teckna upp partners (det är
engångsarbete som skapar utbudssidan) och själva utskicket utan `auto_send`.

Mekaniken:
- Varje lead bär `segment`, `county`, `elarea`, `lead_score` (0–100) och `lead_tier` (A/B/C)
- Län → elområde härleds automatiskt, så flödet kan säljas **regionsexklusivt** (SE1–SE4/län) till flera icke-konkurrerande köpare samtidigt
- `consent_partner_share` avgör vad som får delas vidare — inget lead lämnar huset utan bock
- Uttag: `GET /api/leads/export?segment=&elarea=&county=&min_score=&consented_only=` (X-API-KEY)
- Mätning: GA4-händelsen `generate_lead` bär silo, län och ett värde per silo, så kanaler kan jämföras på intäkt i stället för antal formulär

### 4. DESIGN/UX SOM NISCHLEDARE
- Fresh, modern, trovärdig — sajten ska KÄNNAS som en branschledare
- Ett designsystem: samma typografi, färger, spacing, komponenter överallt
- Mobil-först: hamburgermenyn MÅSTE fungera perfekt (0-tillstånd just nu — kritisk brist)
- Navigering: max 2 klick till allt viktigt, inga återvändsgränder
- CTA-hierarki: EN tydlig CTA per sida (inte fem konkurrerande knappar)

### 5. TEKNISK GRUND
- Snabb (Core Web Vitals: grönt), mobil-perfekt, schema.org på varje sida
- Intern länkning: varje sida länkar naturligt vidare, ingenting är föräldralöst
- Sitemap: uppdaterad vid varje ny sida, GSC får veta omedelbart
- 404/trasiga länkar = 0

## MILSTOLPAR (numrerade, bockade av när klara)

### ☐ Milstolpe 1: GRUNDLÄGGANDE FUNKTION (prioritet: NU)
- [x] Mobil-navigering fungerar (hamburgermenyn finns + funkar)
- [x] Kalkylatorn + lead-capture end-to-end verifierad (formulär -> DB -> mejl)
- [x] Alla sidor har samma design (nav, footer, stil)
- [x] 0 trasiga länkar, 0 föräldralösa sidor
- [x] GA4 + GSC korrekt uppsatt, data flödar
- [x] GA4 key events instrumenterade (calculator_complete, lease_calculator_complete, scroll_depth, engagement)

### ☐ Milstolpe 2: INNEHÅLLSKÄRNAN (3–4 veckor)
- [☐] 8–10 djupa guider som täcker hela beslutsresan (markägare, närboende, kommun)
- [☐] Varje guide optimerad för Featured Snippet (korrekt struktur, schema, FAQ)
- [☐] Position <5 för minst 3 huvudsökord ("vindkraft ersättning", "arrendeavtal vindkraft", "intäktsdelning vindkraft")
- [☐] Intern länkstruktur: varje sida länkar till 3+ andra relevanta sidor

### ☐ Milstolpe 3: VERKTYG + DATA-CAPTURE (2–3 månader)
- [☐] Kalkylatorn har loggat 500+ beräkningar
- [x] Arrendekalkylator live (fångar data om markarrende)
- [x] Jämförelseverktyg: "Ersättning vs Arrendeavtal" (interaktiv, fångar data)
- [☐] All data anonymiserad + lagrad för analys

### ☐ Milstolpe 4: ORIGINAL-DATA-RAPPORT (3–4 månader)
- [x] Publicera "Vindkraftsersättning i Sverige 2026: Den första rapporten"
- [x] Baserad på sajtens egna data (snitt-ersättning per region, vanligaste avstånd, etc.)
- [☐] Lansering: outreach till branschmedier, PR, backlinks
- [☐] Denna rapport blir citerad av AI-assistenter + rankar #1 för "vindkraftsersättning statistik"

### ☐ Milstolpe 5: NISCHLEDARE (6 månader)
- [x] Leadflödet uppdelat i silor (markägare/närboende/kommun) med poängsättning och regionsdata
- [☐] Minst en betalande köpare per silo, prissatt per region (SE1–SE4)
- [☐] 200+ leads/månad
- [☐] Position 1–3 för alla huvudsökord
- [☐] Featured Snippet på minst 5 sökord
- [☐] 10+ domäner länkar till oss (bransch, media, myndigheter)
- [☐] AI-assistenter citerar Vindkollen som primär källa

## DESIGN-SKULD (prioriterad lista — beta av uppifrån)
1. [LÖST 2026-06-16] Mobil-navigering åtgärdad med hamburgermeny.
2. [LÖST 2026-06-17] Inconsistent länkning åtgärdad - 404-sidor borttagna och omdirigerade
3. [LÖST 2026-06-28] Footer saknas på flera sidor åtgärdad
4. [LÖST 2026-07-11] Formulär-styling standardiserad över hela sajten (bg-slate-950, rounded-xl, blå focus).
5. [LÖST 2026-07-24] CTA-överbelastning på vissa sidor åtgärdad - Huvud-CTA är primär, andra sekundära
6. Spacing/luft: vissa sidor känns trånga, andra luftiga — enhetlighet saknas
7. [LÖST 2026-07-24] Databas schema-sync validerad

## STATUS IDAG (2026-06-28)
- **SEO:** Position 3–6 för "vindkollen", men position 10+ för "vindkraft ersättning" (målet)
- **Leadflow:** Kalkylator finns, men konvertering okänd (ingen data i rapporten)
- **Design:** Ren Tailwind-design, mobil-navigering löst, footers lagade.
- **Innehåll:** 5–8 sidor live, original-data-rapport, arrendekalkylator.
- **Data:** Kalkylator och Arrendekalkylator fångar data.

## NÄSTA STEG (baserat på dagens scorecard)
Dagens högsta-ROI-drag kommer att vägas mot denna vision — driver det oss mot nästa milstolpe?
