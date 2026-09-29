import re

with open('/data/workspace/projects/vindkollen/KAMPANJ.md', 'r') as f:
    content = f.read()

# Add Step 5 for the winning trigger
step_5 = """
[ ] Steg 5 (pass 4, 2026-09-29): SCOREBOARD visade en VINNARE trigger för 
    /guider/bygga-vindkraftverk-steg-for-steg (klick 0->2, position 41->16). 
    Vi häller på mer bränsle här. Eftersom /markagare är en stark ingång länkar 
    vi /markagare till den här guiden, och fördjupar guiden med mer konkret 
    ersättningsdata, så att de som söker "bygga vindkraftverk" leds in i vår 
    konverteringstratt. Detta adresserar CTR i position < 6 indirekt genom att 
    driva interntrafik och bygga ut intent för sökord som relaterar till 
    "vindkraftverk ersättning till markägare" i samma veva.
"""

content = content.replace("Bevis att det var rätt: GA4 generate_lead på /arrendekalkylator 0 → ≥2\n    på 28 dagar, och rader med source='arrendekalkylator' i vindkollen_leads.", "Bevis att det var rätt: GA4 generate_lead på /arrendekalkylator 0 → ≥2\n    på 28 dagar, och rader med source='arrendekalkylator' i vindkollen_leads.\n" + step_5)

with open('/data/workspace/projects/vindkollen/KAMPANJ.md', 'w') as f:
    f.write(content)
