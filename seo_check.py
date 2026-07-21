import urllib.request
import json
import re

urls = [
    "https://vindkoll.se/",
    "https://vindkoll.se/kalkylator",
    "https://vindkoll.se/arrendeavtal-vindkraft",
    "https://vindkoll.se/ersattning-for-vindkraft"
]

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        title = re.search(r'<title>(.*?)</title>', html)
        h1 = re.search(r'<h1.*?>(.*?)</h1>', html, re.DOTALL)
        meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
        print(f"URL: {url}")
        print(f"Title: {title.group(1) if title else 'None'}")
        print(f"H1: {h1.group(1).strip() if h1 else 'None'}")
        print(f"Meta Desc: {meta_desc.group(1) if meta_desc else 'None'}")
        print("---")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
