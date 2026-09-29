import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d")
log_entry = f"{now} | INNEHÅLL | Optimerade och fördjupade bygga-vindkraftverk-steg-for-steg | CTR kluster < 6 | nästa: avläs SCOREBOARD för effekten av CTR i klustret"

with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'r') as f:
    content = f.read()

with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'w') as f:
    f.write(log_entry + "\n" + content)
