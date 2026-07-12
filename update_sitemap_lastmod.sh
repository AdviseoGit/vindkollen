#!/bin/bash
sed -i -E "s|<lastmod>[0-9]{4}-[0-9]{2}-[0-9]{2}</lastmod>|<lastmod>$(date +%Y-%m-%d)</lastmod>|g" /data/workspace/projects/vindkollen/sitemap.xml
