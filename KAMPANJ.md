## AKTIV KAMPANJ
Hypotes: Vindkoll rankar redan topp-5 på sina kärnfrågor men får nästan inga klick.
Om vi skriver om SERP-utdraget (titel, meta, schema, ingress) till ett DIREKTSVAR MED
SIFFRA på varje query där sidan står på position <6, tar vi hem klick som redan är
vunna i ranking — utan att bygga en enda ny sida.

Bevis som startade kampanjen (fönster 2026-08-16..08-29):
| query | sida | pos | visn | klick | CTR |
|---|---|---|---|---|---|
| ersättning vindkraftverk markägare | /ersattning-for-vindkraft | 3.0 | 40 | 1 | 2.5 % |
| vindkraftverk ersättning till markägare | /ersattning-for-vindkraft | 5.4 | 15 | 0 | 0 % |
| arrendeavtal vindkraft | /markagare | 3.3 | 13 | 1 | 7.7 % |
| arrende vind | /markagare | 3.6 | 13 | 0 | 0 % |
| arrendeavtal vind | /markagare | 3.1 | 8 | 0 | 0 % |
| vindkollen (varumärke!) | – | 2.7 | 15 | 0 | 0 % |
Summa: 104 visningar på position 2.7–5.4 gav 2 klick = 1.9 % CTR.
Normal CTR på position 3–5 är 6–10 %. Det ligger 5–8 klick per 14-dagarsfönster
på bordet utan att någon ranking behöver flyttas.

Målsiffra: CTR i position<6-klustret 1.9 % -> >6 % (klick 2 -> >6 per 14 dagar).
Löptid: pass 3 av 4 (startad 2026-09-01)
Kill-kriterium: Om CTR i klustret står stilla eller sjunker efter två pass med
omskrivet SERP-utdrag, är diagnosen fel — då är det inte utdraget som håller
tillbaka klicken utan SERP:en själv (AI Overview / featured snippet äter klicket),
och kampanjen läggs ner till förmån för GEO-spåret.

### Avläsning pass 2 (fönster 2026-08-23..09-05 mot 2026-08-09..08-22)
| query | före | efter |
|---|---|---|
| arrendeavtal vindkraft | 5 visn / 0 klick / pos 3.8 | 19 visn / **2 klick** / pos 1.9 |
| ersättning vindkraftverk markägare | 49 / 1 / 5.6 | 37 / **2** / 2.2 |
| vindkollen | 15 / 0 / 2.9 | 10 / **2** / 2.6 |
| vindkraftverk ersättning till markägare | 14 / 0 / 7.7 | 16 / 0 / 4.4 |
| arrende vind | 6 / 0 / 5.3 | 15 / 0 / 2.0 |
| arrendeavtal vind | 4 / 0 / 5.8 | 14 / 0 / 2.7 |

**Klustret: CTR 1.1 % → 5.3 % (klick 1 → 6, visningar 93 → 114).**
Målsiffran är >6 % och den är inom räckhåll. Kill-kriteriet — CTR står stilla
eller sjunker — slog INTE till. Kampanjen lever.

Två saker att notera i avläsningen. Positionen förbättrades kraftigt på varje
omskriven query (3.8→1.9, 5.6→2.2, 5.3→2.0, 5.8→2.7); omskrivningen tog alltså
inte bara klick, den flyttade ranking. Och de tre queries som fortfarande har
0 klick står nu 2.0–4.4 med 45 visningar mellan sig — det är där de återstående
klicken ligger.

### Avläsning pass 3 (fönster 2026-09-06..09-19 mot 2026-08-23..09-05)
| query | före | efter |
|---|---|---|
| arrendeavtal vindkraft | 19 visn / 2 klick / pos 1.9 | 14 / 0 / 2.0 |
| ersättning vindkraftverk markägare | 40 / 2 / 6.8 | 41 / **4** / 1.8 |
| vindkollen | 10 / 2 / 2.6 | 10 / 2 / 3.6 |
| vindkraftverk ersättning till markägare | 16 / 0 / 4.4 | 14 / 0 / 4.0 |
| arrende vind | 15 / 0 / 2.0 | 16 / 0 / **1.3** |
| arrendeavtal vind | 14 / 0 / 2.7 | 14 / 0 / 2.1 |

**Klustret: CTR 5.3 % → 5.5 % (klick 6 → 6, visningar 114 → 109).** Stilla, strax
under målet >6 %. Kill-kriteriet ("står stilla eller sjunker efter två pass") är
inte formellt utlöst — pass 2 var en uppgång — men pass 3 är det första stilla
passet, och mönstret i de tre nollklick-queries är talande: "arrende vind" står
på position **1.3** med 0 klick av 31 visningar på 28 dagar. Position 1 med 0 %
CTR finns inte i en vanlig SERP — det är AI Overview-citeringen som räknas som
visning på position 1. Utdraget kan inte skrivas om till att slå ett svar som
Google redan visar ovanför. Ett pass kvar: står klustret stilla igen läggs
kampanjen ner enligt kill-kriteriet, till förmån för GEO-spåret.

Sajten i helhet: klick 31 → 69, position 21.4 → 13.4. Det är inte kampanjen som
driver det — det är breda anonymiserade queries (bara 10 av 69 klick syns på
query-nivå).

Steg:
[x] Steg 1 (pass 1, 2026-09-01): /markagare. Titel/meta/og skrevs om från
    "Vindkraft på min mark – arrende, ersättning och avtal 2026" (ingen siffra,
    matchade inte frasen folk söker på) till
    "Arrendeavtal vindkraft 2026 – 150 000–300 000 kr per verk och år".
    Metan leder nu med direktsvaret i stället för en motfråga.
[x] Steg 2 (pass 2, 2026-09-08): Utfallet på /ersattning-for-vindkraft är
    mätt. "ersättning vindkraftverk markägare" gick 1 klick/49 visn/pos 5.6 ->
    2 klick/37 visn/pos 2.2. CTR 2.0 % -> 5.4 %. Omskrivningen håller.
[x] Steg 3 (pass 2, 2026-09-08): "vindkollen" löste sig utan drag — 0 klick
    av 15 visningar blev 2 klick av 10 (20 % CTR, pos 2.6). Fortfarande under
    30–60 %, men på 10 visningar är skillnaden mellan 20 % och 40 % ett enda
    klick. För litet underlag för att vara värt ett pass. Avförd.
[~] Steg 4 (pass 3, 2026-09-22) — OMVÄRDERAT. Solcells-underlaget kollapsade:
    "sol"-queries gick 60 visningar (pass 2) → 8 (pass 3), enda kvarvarande är
    "ersättning solceller mark" 8 visn / pos 69.6. Google slutade visa oss för
    frasen när vi inte fick klick på position 48–89. En ny sida för 8 synliga
    visningar är inte ett pass värt. Parkerad, inte avförd — kollas vid nästa
    scoreboard; återuppstår underlaget (>30 visn/14d) är sidan draget.
    Passet gick i stället till det GA4 visade när kalkylatorerna granskades:
    /arrendekalkylator hade 46 slutförda beräkningar på 90 dagar och 0 leads
    (/kalkylator: 48 → leads finns; /markagare: 55 formvisningar → 2). Lead-
    sektionen låg under hela resultatgridden utan pekare och utan scroll, och
    löftet ("vi mejlar genomgången") hölls inte av välkomstmailet. Fixat:
    CTA i resultatrutan, scroll till resultatet, löfte = checklistan på
    /juridisk-hjalp-arrendeavtal som nu ligger först i markägarmailet, och
    /ersattning-for-vindkraft (459 visn, sajtens största) skickar markägare
    till /arrendekalkylator i stället för närboende-kalkylatorn.
    Bevis att det var rätt: GA4 generate_lead på /arrendekalkylator 0 → ≥2
    på 28 dagar, och rader med source='arrendekalkylator' i vindkollen_leads.

## AVSLUTADE
2026-09-01 | Om vi fördjupar /markagare genom intern länkning och riktade sökbehov
driver vi fler klick och bättre placering | klick 6 -> >12, placering 19.8 -> <15 |
**Målsiffran nåddes inte.** Utfall över 4 pass: visningar 59 -> 210 (+256 %),
klick 5 -> 4, position 18.8 -> 21.5. Kill-kriteriet (visningar/klick minskar) slog
aldrig till på visningar — de tredubblades — men klicken följde aldrig med.
Positionsförsämringen är inte ett tapp: sidan drog in 45 nya visningar på
solcells-queries den rankar 50–81 på, och de drar ner det visningsviktade snittet.
På de queries sidan faktiskt äger står den 3.1–3.6. Kampanjen misslyckades med sitt
mål men lyckades med något mer användbart: den bevisade att flaskhalsen är CTR,
inte ranking. Den nya kampanjen ovan angriper exakt det.
2026-08-11 | Om vi optimerar våra starkaste innehållssidor för AI-citerbarhet (GEO)... | GEO > 85/100 | Sidor optimerade, men gav ingen märkbar klickökning ännu. Kampanj avslutad.
