import datetime

log_entry = f"{datetime.date.today().strftime('%Y-%m-%d')} | DATA/ANALYTICS | Implementerade GA4 Key Events (calculator_complete, cta_click, scroll_depth) | Data Capture & Conversion Tracking | nästa: Deploya till produktion\n"

with open("/data/workspace/projects/vindkollen/PROGRESS_LOG.md", "r") as f:
    lines = f.readlines()

lines.insert(0, log_entry)

with open("/data/workspace/projects/vindkollen/PROGRESS_LOG.md", "w") as f:
    f.writelines(lines)
print("Updated PROGRESS_LOG.md")
