import requests

url = "https://vindkoll.se/arrendera-ut-mark-for-vindkraftverk"
r = requests.get(url)
print("Status:", r.status_code)
if r.status_code == 200:
    print("Content length:", len(r.text))
    print("Title:", [line for line in r.text.split('\n') if '<title>' in line.lower()])
else:
    print(r.text[:200])
