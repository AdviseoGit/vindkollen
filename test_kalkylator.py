import requests

url = "https://vindkoll.se/api/lead/report"
data = {
    "email": "test_kalkylator_lead@example.com",
    "name": "Test Kalkylator",
    "municipality": "Testkommun",
    "property_address": "Testgatan 1",
    "elarea": "SE3",
    "distance_m": 500,
    "turbine_height_m": 250,
    "turbine_count": 5,
    "estimated_compensation_sek": 50000,
    "promille": 1.5,
    "source": "kalkylator_test_script"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
