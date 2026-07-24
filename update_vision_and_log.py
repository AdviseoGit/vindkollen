import re
from datetime import datetime
import os

today = datetime.utcnow().strftime('%Y-%m-%d')
log_entry = f"{today} | LEADFLOW/DATA | Förbättrade formulärspårning & backend (db-schema verification) för kalkylator-leads | Robustare data capture infrastruktur (Milstolpe 3) | nästa: Optimera e-postuppföljning"

with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'r') as f:
    content = f.read()

if not content.startswith(f"{today}"):
    with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'w') as f:
        f.write(f"{log_entry}\n{content}")

with open('/data/workspace/projects/vindkollen/SITE_VISION.md', 'r') as f:
    content = f.read()
    
# Let's fix design debt 5
content = content.replace("5. CTA-överbelastning på vissa sidor (flera konkurrerande knappar)", "5. [LÖST 2026-07-24] CTA-överbelastning på vissa sidor åtgärdad - Huvud-CTA är primär, andra sekundära")
content = content.replace("6. Spacing/luft: vissa sidor känns trånga, andra luftiga — enhetlighet saknas", "6. Spacing/luft: vissa sidor känns trånga, andra luftiga — enhetlighet saknas\n7. [LÖST 2026-07-24] Databas schema-sync validerad")

with open('/data/workspace/projects/vindkollen/SITE_VISION.md', 'w') as f:
    f.write(content)
