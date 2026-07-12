#!/bin/bash
find /data/workspace/projects/vindkollen/static -name "*.html" -exec sed -i 's/\/arrendeavtal-vindkraft\.html/\/arrendeavtal-vindkraft/g' {} +
