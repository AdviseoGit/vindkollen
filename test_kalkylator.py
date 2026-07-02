import requests

data = {
    "email": "test@example.com",
    "name": "Test User",
    "municipality": "Stockholm",
    "source": "newsletter"
}
try:
    res = requests.post("https://vindkoll.se/api/lead", json=data)
    print(res.status_code, res.text)
except Exception as e:
    print(e)
