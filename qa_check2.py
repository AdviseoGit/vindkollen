import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    resp = urllib.request.urlopen('https://vindkoll.se/markagare', context=ctx)
    print("Code:", resp.getcode())
except Exception as e:
    print("Error:", e)
