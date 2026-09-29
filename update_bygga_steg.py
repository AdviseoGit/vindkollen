import re

with open('/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html', 'r') as f:
    html = f.read()

new_content = """<h2>Hur fungerar ekonomi, ersättning och finansiering?</h2>
            <p>Ett vindkraftverk är en stor investering. Du behöver en detaljerad kalkyl som tar hänsyn till alla kostnader: inköp och installation av verket (kan ofta ligga på 40-60 miljoner kr per modernt stort verk), anslutning till elnätet, underhåll och försäkringar. På intäktssidan finns försäljning av el (PPAs) och eventuella ursprungsgarantier.</p>
            <p>Om du istället arrenderar ut din mark till en projektör (vilket är det vanligaste för markägare) står projektören för hela investeringskostnaden. Din intäkt kommer i form av arrende, ofta som en procent av bruttointäkten från elförsäljningen (vanligen 2-5 %). I snitt innebär det en årlig ersättning på <strong class="text-white">150 000 till 300 000 kronor per vindkraftverk</strong>. Läs mer i vår <a href="/ersattning-for-vindkraft" class="text-blue-400 hover:underline">fullständiga guide om ersättning för vindkraft</a> eller använd <a href="/arrendekalkylator" class="text-blue-400 hover:underline">vår arrendekalkylator</a> för att räkna på dina specifika förutsättningar.</p>
"""

html = re.sub(r'<h2>Hur fungerar ekonomi och finansiering\?</h2>\s*<p>Ett vindkraftverk är en stor investering[^<]*</p>', new_content, html)

with open('/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html', 'w') as f:
    f.write(html)
