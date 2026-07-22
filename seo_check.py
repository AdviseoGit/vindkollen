import requests

urls = [
    "https://vindkoll.se/jamforelse-ersattning-vs-arrende",
    "https://vindkoll.se/kalkylator",
    "https://vindkoll.se/arrendekalkylator",
    "https://vindkoll.se/arrende-vindkraft-vs-solpark"
]

for url in urls:
    try:
        response = requests.get(url)
        content = response.text
        has_lead = "lead" in content.lower()
        print(f"{url} - 200 OK: {response.status_code == 200} - Has Lead: {has_lead}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
