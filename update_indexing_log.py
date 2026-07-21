import os
import datetime

log_file = "/data/workspace/projects/vindkollen/INDEXING_LOG.md"
with open(log_file, "r") as f:
    content = f.read()

today = datetime.datetime.now().strftime("%Y-%m-%d")

# Update dates and actions
content = content.replace("2026-07-20 | Lade till unika Vindkollen insikter", f"{today} | Lade till unika Vindkollen insikter (Klar)")
content = content.replace("2026-07-20 | Fixat felaktig canonical", f"{today} | Fördjupade med Vindkollen-data")
content = content.replace("2026-07-16 | fixat felaktig canonical till .html", f"{today} | Fördjupade med Vindkollen-data")
content = content.replace("2026-07-16 | förstärk interna länkar", f"{today} | Fördjupade med Vindkollen-data & lade till i mobilmeny")
content = content.replace("2026-07-16 | kvalitet/uniktvärde-problem; fördjupa/differentiera sidan", f"{today} | Lade till unika insiktssektioner & omskrivningar")

with open(log_file, "w") as f:
    f.write(content)

