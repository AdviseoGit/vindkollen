import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote("rätt till inlösen vindkraft")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8')
        with open('duck.html', 'w') as f:
            f.write(html)
        import re
        titles = re.findall(r'<a class="result__url" href="[^"]+">([^<]+)</a>', html)
        for t in titles[:5]:
            print(t.strip())
except Exception as e:
    print(f"Error: {e}")
