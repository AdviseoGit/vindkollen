import re

with open('/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html', 'r') as f:
    html = f.read()

# Update title and meta description to be more compelling and CTR friendly based on the Kampanj (adding numbers)
html = html.replace('<title>Bygga vindkraftverk steg för steg - en komplett guide | Vindkollen</title>', '<title>Bygga vindkraftverk på egen mark (2026) – Steg för steg & ersättning</title>')
html = html.replace('name="description" content="En detaljerad guide för markägare som vill bygga vindkraftverk. Lär dig om tillstånd, val av plats, ekonomi och avtal."', 'name="description" content="Ska du bygga vindkraftverk på din mark? Här är hela processen från vindkartering till arrendeavtal. Snittersättningen är 150 000–300 000 kr/verk/år."')

with open('/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html', 'w') as f:
    f.write(html)
