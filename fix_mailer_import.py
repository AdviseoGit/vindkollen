import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

# Add from mailer import send_email, notify_owner near the top
import_str = "from fastapi.staticfiles import StaticFiles"
new_import_str = import_str + "\nfrom mailer import send_email, notify_owner"
if "from mailer import send_email, notify_owner" not in content:
    content = content.replace(import_str, new_import_str)

with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
    f.write(content)
