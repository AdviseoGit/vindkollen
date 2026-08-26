# Mission — site-driver för vindkoll.se

Ett pass per vecka. Allt skrivs på svenska.

## Målet — tre delar som alla väger

1. **#1 på Google** i nischen: vindkraftsersättning, arrende, intäktsdelning till markägare och närboende.
2. **#1 i GEO** — den källa ChatGPT, Perplexity, AI Overviews och Copilot faktiskt citerar. En växande del av nischen når aldrig en blå länk; osynlighet i AI-svaret är osynlighet.
3. **#1 på leadflow** — heta leads, inte trafik för trafikens skull.

Ett drag som flyttar två av tre slår ett som flyttar ett.

## Setup

Två repon behövs: **vindkollen** (sajten) och **AgentSim** (skripten och credentials).

**Kör du lokalt på Sims maskin** ligger de på kända platser i WSL, och alla `python3`-
och `git`-kommandon måste gå genom WSL — Windows-sidan saknar python:

```bash
VK=~/site-fixes/vindkollen
AS=~/AdviseoGit/AgentSim
```

Notera att AgentSim-checkouten står på grenen `fix-switch-model`. **`scoreboard.py`
finns bara där, inte på `main`** — byt inte gren utan att kontrollera att skriptet
följer med.

**Kör du i en molnsandbox** är repona utcheckade under `/home/user`. Hitta dem:

```bash
VK=$(find / -maxdepth 6 -type d -name vindkollen 2>/dev/null | head -1)
AS=$(find / -maxdepth 6 -type d -name AgentSim 2>/dev/null | head -1)
pip install pyyaml requests 2>/dev/null || pip3 install pyyaml requests
```

Saknas `scoreboard.py` i `$AS/skills/site-updater/scripts/` — avbryt passet och
rapportera det. Gissa aldrig fram en mätning.

I båda fallen:

```bash
export OPENCLAW_WORKSPACE_DIR=$AS
```

## Steg 1 — mät först, alltid

```bash
python3 $AS/skills/site-updater/scripts/scoreboard.py \
  --project $VK --site sc-domain:vindkoll.se --ga4 539992197 \
  --leads-url https://vindkoll.se/api/stats/leads --window 14
```

Skriptet skriver `SCOREBOARD.md` + `metrics.jsonl` i `$VK` och **räknar ut triggrarna själv**. Läs hela utskriften.

**Triggrarna binder.** Finns en KRITISK trigger avgör den vad passet handlar om. Du väljer inte kategori på känsla.

**Men verifiera att triggern är sann innan du agerar.** Triggrar mäter URL:er, inte avsikt. En sida som tappat visningar kan vara medvetet 301:ad till en ny URL — det är ett flytt, inte en regression, och att "laga" det förstör riktigt arbete. Kolla alltid först:

```bash
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' -A 'Mozilla/5.0' <url>
```

Är triggern ett artefakt: skriv det i rapporten och gå vidare till nästa trigger. Det är ett fullgott passresultat.

## Steg 2 — välj ETT drag

Använd tabellen **"sidor rankade på möjlighet"** (visningar × missad CTR mot position 3) för att välja sida. Inte GEO-poäng — den rankar sitemap-ordning och är okorrelerad med trafik.

Menyn är bred. Allt detta är tillåtna drag:

- fördjupa eller bygga om en sida som redan har visningar
- bygga intilliggande intent (en fråga folk ställer men ingen äger)
- konvertering: formulärplacering, friktion, vad som lovas
- distribution utanför Google
- partnerskap och försäljning
- produktändringar (kalkylatorn är största konverteringsytan)
- ompositionering
- **radera innehåll** som drar ner helheten

Hygien (QA, trasiga länkar, schema) får bara ta passet om det är en **regression** — annars är det sysselsättning.

`KAMPANJ.md` håller **en satsning över flera pass**, med ett dödskriterium. Finns en pågående kampanj: driv den vidare om inte en KRITISK trigger säger annat. Det är det som gör stora drag möjliga när ett pass är kort.

## Steg 3 — leadkedjan, varje pass

Skicka en **riktig testinskickning**, märkt `QA-TEST <datum>`, och bekräfta tre saker:

1. endpointen svarar 2xx
2. leadet är **lagrat** (fråga `/api/stats/leads` före och efter — siffran ska öka)
3. **mailet kom fram** — kolla via Gmail-connectorn att välkomstmailet landat

**Städa bort testleadet efteråt.** Ostädade tester ligger kvar i databasen och blåser upp siffran som triggrarna räknar på — det finns redan minst tre sådana i `vindkollen_leads` (`kalkylator_test_script`, `post_fix_check`, `qa-test@example.com`).

Endpoints som finns: `/api/lead` (JSON), `/api/newsletter/subscribe` (formulär, 303 → rapportsidan), `/api/lead/report` (kalkylatortratten), `/api/lead/qualify`.

## Steg 4 — publicera och VERIFIERA LIVE

Commit och push till `main` i `$VK`. Railway autodeployar.

**Bekräfta att pushen faktiskt landade innan du går vidare.** En misslyckad push
är tyst farlig: Railway deployar ingenting, live-verifieringen kollar då en
oförändrad sajt, allt svarar 200, och passet rapporterar framgång fast ingenting
skeppades. Kontrollera mot fjärren, inte mot ditt eget commit-kommando:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main    # ska visa samma sha
```

Skiljer de sig — pushen gick inte igenom. Rapportera det som passets utfall och
verifiera ingenting live, för det du skulle verifiera finns inte där.

Autentiseringen sköts av `gh` (`credential.https://github.com.helper`), inte av
en token i remote-URL:en.

**Efter deploy är verifiering obligatorisk.** Vänta tills appen svarar, kolla sedan:

```bash
for p in / /kalkylator /markagare /original-data-rapport-arrende-2026; do
  printf '%s %s\n' "$(curl -sS -o /dev/null -w '%{http_code}' -A 'Mozilla/5.0' "https://vindkoll.se$p")" "$p"
done
curl -sS -A 'Mozilla/5.0' https://vindkoll.se/api/stats/leads
```

**Svarar något annat än 200 — rulla tillbaka omedelbart** med `git revert HEAD && git push`, vänta in deployen, verifiera att sajten är uppe igen, och rapportera det som passets utfall.

Det här steget finns av en anledning: 2026-08-26 fällde en enda rad hela sajten på 502. `Form(...)` i FastAPI kräver `python-multipart`, och FastAPI reser kravet när **rutten definieras**, inte när den anropas — så importen av `main.py` kraschade och allt gick ner, inte bara den nya rutten. Syntaxkontroll fångade det inte. Bara ett live-anrop gör det.

**Verifiera alltid live-sidan, aldrig commit-meddelandet.** Vindkoll har tidigare haft en commit som påstod att en påhittad statistiksiffra var borttagen från startsidan medan texten låg kvar.

## Steg 5 — rapportera

Skriv en kort rapport, i den här formen:

```
MÄTNING:   klick / visningar / CTR / position, delta mot förra passet
TRIGGER:   vilken som band — och om någon avfärdades som artefakt, varför
DRAGET:    vad du gjorde, på vilken sida, och vilket av de tre målen det flyttar
GEO:       poäng före→efter om du rörde GEO, annars "ej i fokus"
LEADS:     antal senaste 7d, källa, samt testet: 2xx / lagrad / mailad / uppstädad
UX-DATA:   signalen du agerade på, MED siffran
PUBLICERAT: commit-sha + resultatet av live-verifieringen
KAMPANJ:   pågående satsning, dess dödskriterium, och om den lever vidare
NÄSTA:     ett konkret nästa drag — och siffran som ska bevisa att det var rätt
```

Ett utfall som inte skrivs ner kan inte styra nästa beslut. `SCOREBOARD.md` och `metrics.jsonl` **ska committas varje pass** — de är passets enda minne.

## Bakgrund värd att känna till

- Leadsiffran är låg och verklig. Den var tidigare uppblåst med en påhittad baseline på 1247 medan sanningen var 15. Siffran ska aldrig snyggas till.
- **`metrics.jsonl` har ett brott 2026-08-26.** Rader före det datumet redovisar 15–17 leads; från och med då är siffran 9. Skillnaden är inte ett tapp — passet den kvällen raderade 8 kvarglömda `@example.com`-testleads som aldrig var riktiga leads. Läs alltså inte 17 → 9 som en regression, och fyra ingen `LEADS`-trigger på den övergången. Första äkta jämförelsen är 9 mot nästa mätning.
- `kalkylator_report` är största leadkällan.
- `/api/leads/export` kräver headern `X-API-KEY` (satt som `INTERNAL_API_KEY` på Railway-tjänsten).
- AgentSims cron för den här sajten är avstängd sedan 2026-08-26. Du är ensam skribent på repot.
