import urllib.request
import json

req = urllib.request.Request("https://vindkoll.se/api/stats/leads", headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(r.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
