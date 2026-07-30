with open("/data/workspace/projects/vindkollen/PROGRESS_LOG.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_line = "2026-07-30 | SEO | Fördjupade oindexerade sidor med unikt Vindkollen-data | Höjer unikt värde för indexering på 4 URL:er | nästa: Optimera kalkylatorns leadflow\n"
lines.insert(0, new_line)

with open("/data/workspace/projects/vindkollen/PROGRESS_LOG.md", "w", encoding="utf-8") as f:
    f.writelines(lines)
