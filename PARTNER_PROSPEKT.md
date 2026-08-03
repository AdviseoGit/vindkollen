# Prospektlista — köpare att ringa

**Det här är inte partnerregistret.** Ingen rad här får läggas in via `/api/partners`
förrän motparten sagt ja och det finns ett avtal. Registret styr vem som får ta emot
en markägares namn, telefon och fastighetsbeteckning — och besökaren har samtyckt till
"utvalda samarbetspartner", inte till en lista vi hittat på nätet.

Listan är sammanställd 2026-08-03 ur sökresultat. **Inga mejladresser finns med med
flit:** sidorna gick inte att öppna härifrån (403), och en gissad adress skulle betyda
att ett lead skickas till fel mottagare. Hämta kontaktvägen från bolagets egen sida när
du ringer.

---

## Projektörer med egen markägaringång

De här har redan en process för markägare som hör av sig — det är den varmaste dörren,
för de behöver inte övertygas om att markägarleads är värda något.

| Bolag | Markägarsida | Noterat |
|---|---|---|
| OX2 | [information-till-markagare](https://www.ox2.com/sv/sverige/verksamhet/landbaserad-vindkraft/information-till-markagare/) | Enhetligt produktionsbaserat arrendeavtal till alla markägare, även där verken inte står. Förvärvat projekt i SE3. |
| Eolus Vind | [eolus.com/vad-vi-gor/markagare](https://www.eolus.com/vad-vi-gor/markagare/) | Projekterar och bygger, säljer vidare färdiga anläggningar. Ersättning som andel av produktionen. |
| Rabbalshede Kraft | [Hej markägare!](https://www.rabbalshedekraft.se/sv/kontakt/hej-markagare) | Tar emot mark för både vind och sol. Bohuslänskt ursprung → sannolikt SE3-tyngdpunkt. |
| SR Energy | [om-bolaget/markagare](https://srenergy.se/om-bolaget/markagare/) | Uppger att de löpande söker nya platser för vindkraft. |
| Vasa Vind | [vasavind.se/markagare](https://www.vasavind.se/markagare/) | Har markägarportal med BankID där arrendeutbetalningar redovisas — mogen markägarrelation. |
| Euro Wind Energy | [eurowindenergy.com/se/markagare](https://eurowindenergy.com/se/markagare) | Egen markägarsida. |
| Vindin | [om-vindin/arrenden](https://www.vindin.se/om-vindin/arrenden/) | Sida specifikt om arrenden. |

## Projektörer utan tydlig markägaringång

Större volym, men kallare samtal — här får du förklara vad ett kvalificerat markägarlead är.

| Bolag | Ingång | Noterat |
|---|---|---|
| Vattenfall | [projekt.vattenfall.se/vindprojekt](https://projekt.vattenfall.se/vindprojekt/) | Tung närvaro i norr: Norrbäck (Lycksele), Storlandet (Gällivare/Boden), planer på 373 verk i Norrbotten. **Mest relevant för SE1/SE2.** |
| Svevind | — | Söker "vindfyndigheter" i norra Sverige, bolaget bakom Markbygden. **SE1.** |
| wpd Sweden | [wpd.se](https://www.wpd.se/) | Etablerad projektutvecklare, medlem i Svensk Vindenergi. |
| Arise | — | En av de fyra stora projektutvecklarna, hela värdekedjan. |
| RES Renewable Norden | — | Brittiskägd, ett tiotal vind- och vätgasprojekt i Sverige. |

Fler namn finns i [Svensk Vindenergis medlemsförteckning](https://svenskvindenergi.org/om-oss/medlemsforetag)
— den är den bästa källan när du vill bredda listan.

## Juridik och rådgivning

Den här silon är den som saknar mottagare mest akut: sajten har redan skarpa leads som
kryssat i att de vill ha juridisk hjälp.

| Aktör | Ingång | Varför |
|---|---|---|
| Ludvig & Co | [arrende- och nyttjanderätt](https://ludvig.se/tjanster/juristbyra/arrende-och-nyttjanderatt/), [mark- och miljörätt](https://ludvig.se/tjanster/juristbyra/mark-och-miljoratt/) | Uttalat vindkraft, arrende och lantbruksfastigheter. Företräder markägare i arrendefrågor. Rikstäckande kontorsnät → kan täcka flera län. |
| Hushållningssällskapet | [arrende- och nyttjanderätter](https://hushallningssallskapet.se/tjanster/juridik/arrende-och-nyttjanderatter/), [mark- och miljöjuridik](https://hushallningssallskapet.se/tjanster/juridik/mark-och-miljojuridik/) | Jurister med erfarenhet av arrendelagstiftning *och* ekonomisk värdering. Regionala sällskap → naturlig länsindelning i registret. |
| Svefa | [juridisk rådgivning](https://www.svefa.se/tjanster/juridisk-radgivning) | Fastighetsrådgivare, arbetar med markintrång och förhandling mot enskilda fastighetsägare — passar även närboendesilon (värdeminskning, inlösen). |
| LRF | [Vindavtalet](https://www.lrf.se/medlemsformaner/vindavtalet/) | LRF:s guide/avtalsmall vid vindkraftsetablering. Inte en köpare av leads, men rätt part att känna till — och en trovärdighetskälla att luta sig mot. |

---

## Så använder du listan

**Ring inte alla.** Två till tre räcker för att komma igång, och de ska väljas efter var
du faktiskt har leads. Första skarpa leadet är Norrbotten, alltså:

1. **En projektör för SE1/SE2.** Vattenfall och Svevind är tyngst i norr; Vasa Vind och
   OX2 är enklare att komma in hos eftersom de redan har markägarprocess.
2. **En jurist.** Ludvig & Co eller Hushållningssällskapet — båda arbetar redan med
   arrende åt markägare, så erbjudandet är begripligt på tio sekunder.
3. **En projektör för SE3/SE4** när det kommer leads därifrån. Inte innan.

**Vad du säljer.** De kommer fråga om volym, och där har du inget svar än. Sälj i stället
kvalitet och exklusivitet: *"Markägare i Piteå, 300 hektar, har fyllt i formulär hos oss,
lämnat telefonnummer och samtyckt till att bli kontaktad. Vill ni ha den — och vill ni ha
förtur på Norrbotten?"* Ett bra lead säljer de tjugo nästa. Regionsexklusivitet är dessutom
ett skäl för dem att teckna tidigt.

**När någon säger ja** — då, och först då, in i registret:

```bash
curl -X POST https://vindkoll.se/api/partners \
  -H "X-API-KEY: $INTERNAL_API_KEY" -H 'Content-Type: application/json' \
  -d '{"name":"...","kind":"projektor","email":"<från deras egen sida>",
       "contact_name":"...","elareas":"SE1,SE2","min_score":50,
       "monthly_cap":10,"exclusive":false,"auto_send":false}'
```

Lämna `auto_send` på `false` tills avtalet säger vad de får göra med uppgifterna.
`exclusive: true` bara om de faktiskt betalat för ensamrätt i regionen — den flaggan
stänger ute alla andra köpare i samma silo och område.

## Att kontrollera i samtalet

Regional täckning i tabellerna ovan är delvis en gissning utifrån var bolagen har projekt.
Fråga rakt ut vilka län de vill ha leads från — det är den uppgiften som ska in i
`counties`/`elareas`, och den avgör om matchningen fungerar.
