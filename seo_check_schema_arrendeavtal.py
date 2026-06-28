import re
files = [
    '/data/workspace/projects/vindkollen/static/kalkylator.html',
    '/data/workspace/projects/vindkollen/static/kommun-dashboard.html',
    '/data/workspace/projects/vindkollen/static/ersattning-for-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/skatt-vindkraftersattning.html',
    '/data/workspace/projects/vindkollen/static/nackdelar-med-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/arrendekalkylator.html',
    '/data/workspace/projects/vindkollen/static/index.html',
    '/data/workspace/projects/vindkollen/static/original-data-rapport-arrende-2026.html',
    '/data/workspace/projects/vindkollen/static/om-sajten.html',
    '/data/workspace/projects/vindkollen/static/kommunersattning-vindkraft-2026.html',
    '/data/workspace/projects/vindkollen/static/ersattningsnivaer-region-for-region.html',
    '/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html'
]
for f in files:
    with open(f, 'r') as file:
        content = file.read()
    if 'h1' not in content.lower():
        print(f"Missing H1 in {f}")
