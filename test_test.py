import urllib.request
with urllib.request.urlopen("https://vindkoll.se/kalkylator") as response:
   html = response.read().decode('utf-8')
if "Beräkna din ersättning" in html:
    print("Found 'Beräkna din ersättning'")
if "Få en kostnadsfri rapport" in html:
    print("Found 'Få en kostnadsfri rapport'")
