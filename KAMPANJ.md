## AKTIV KAMPANJ
Hypotes: Om vi fixar de falska siffrorna i leads-mätningen (både på startsidan och i API:et) så kan vi bygga förtroende, börja mäta de faktiska leads-konverteringarna ärligt, och därefter optimera lead-flödet metodiskt.
Målsiffra: Leads-mätning: 0 (falsk + mätfel) -> 1 (ärlig, tillförlitlig, 100% spårbar DB-count)
Löptid: pass 1 av 2
Kill-kriterium: Om vi inte kan få upp tillförlitlig leads-data på nästa pass avbryter vi fokus på lead-trackingen tillfälligt och lutar oss på traffic/sitemap-förbättringar tills en större mätarkitektur finns på plats.
Steg:
[ ] Steg 1: Ta bort den påhittade baslinjen i `main.py` (i `GET /api/stats/leads` och eventuell hårdkodning på startsidan/index.html) samt verifiera att faktiska db-leads mäts och renderas korrekt. Bygga ett riktigt mätsystem för leads.

## AVSLUTADE
_Inga kampanjer avslutade än._