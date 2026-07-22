import re

content = ""
with open("/data/workspace/projects/vindkollen/static/jamforelse-ersattning-vs-arrende.html", "r", encoding="utf-8") as f:
    content = f.read()

# Enhance title and meta description
content = content.replace("<title>Jämför Vindkraftsersättning: Närboende vs Markarrende | Vindkollen</title>", "<title>Jämför Vindkraftsersättning: Närboende vs Markarrende (Verktyg 2026)</title>")
content = content.replace("<meta name=\"description\" content=\"Närboende-ersättning eller markarrende? Jämför intäkterna mellan den statliga trappstegsmodellen (närboende) och kommersiella arrendeavtal (markägare) med vå...\">", "<meta name=\"description\" content=\"Närboende-ersättning eller markarrende? Jämför intäkterna mellan den statliga trappstegsmodellen för närboende och kommersiella arrendeavtal för vindkraft. Prova verktyget.\">")

# Add missing schema logic for tool comparison if not present
if "FAQPage" not in content:
    faq_schema = """
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [{
        "@type": "Question",
        "name": "Vad är skillnaden mellan arrende och närboendeersättning?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Arrende är ersättning till markägaren för upplåtelse av mark för vindkraft. Närboendeersättning är en skattefri intäktsdelning (enligt lagförslag 2026) till boende i närområdet oavsett om de äger marken eller inte."
        }
      }, {
        "@type": "Question",
        "name": "Är närboendeersättningen skattefri?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Ja, enligt regeringens trappstegsmodell (prop 2025/26) blir intäktsdelningen skattefri för närboende."
        }
      }]
    }
    </script>
"""
    content = content.replace("</head>", faq_schema + "</head>")

with open("/data/workspace/projects/vindkollen/static/jamforelse-ersattning-vs-arrende.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated jamforelse-ersattning-vs-arrende.html")
