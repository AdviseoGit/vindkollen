import requests

url = "https://vindkoll.se/guider"
response = requests.get(url, allow_redirects=False)
print(f"Status Code: {response.status_code}")
print(f"Location Header: {response.headers.get('Location')}")
