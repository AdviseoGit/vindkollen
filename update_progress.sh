#!/bin/bash
cat << 'LOG' > /tmp/new_log
2026-07-12 | SEO/TEKNIK | Åtgärdade brutna .html-länkar för arrendeavtal, fixade sitemap för 4 oindexerade URL:er | URL:er kan nu crawlas & indexeras | nästa: Optimera landningssidor för lead-capture
LOG
cat /data/workspace/projects/vindkollen/PROGRESS_LOG.md >> /tmp/new_log
mv /tmp/new_log /data/workspace/projects/vindkollen/PROGRESS_LOG.md
