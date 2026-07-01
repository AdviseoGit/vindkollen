import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

import_statement = "from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse"
new_import_statement = import_statement + "\nfrom .mailer import send_email, notify_owner"
content = content.replace(import_statement, new_import_statement)
if "from .mailer import send_email, notify_owner" not in content:
    content = content.replace("from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse", "from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse\nfrom mailer import send_email, notify_owner")


mailer_func = """
def deliver_report(email: str, name: str, est: int):
    subject = "Din marknadsrapport för vindkraftsersättning"
    html = f\"\"\"
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
        <h2>Hej {name or ''},</h2>
        <p>Här är din personliga uträkning från Vindkollen.</p>
        <p>Enligt kalkylen är din estimerade årliga ersättning: <b>{est} kr/år</b>.</p>
        <p>Vi arbetar just nu med att ta fram en mer detaljerad rapport. Vi hör av oss om vi behöver kompletterande information om din fastighet.</p>
        <p>Vänliga hälsningar,<br>Teamet på Vindkollen</p>
    </body>
    </html>
    \"\"\"
    send_email(email, subject, html)
    
    notify_html = f"<p>Ny kalkylator-lead: {email} (Est: {est} kr/år)</p>"
    notify_owner("Ny lead - Vindkollen", notify_html)
"""

if "def deliver_report" not in content:
    target = "@app.post(\"/api/lead/report\")"
    content = content.replace(target, mailer_func + "\n" + target)

new_post = """
        await session.execute(stmt)
        await session.commit()
    
    background.add_task(deliver_report, email, lead.name, lead.estimated_compensation_sek)
"""

if "background.add_task(deliver_report" not in content:
    content = content.replace("""        await session.execute(stmt)
        await session.commit()""", new_post)

with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
    f.write(content)
