import os
import re

def analyze_seo(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    
    issues = []
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check title length
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title_len = len(title_match.group(1).strip())
                if title_len > 60:
                    issues.append(f"{filepath}: Title too long ({title_len} chars)")
                if title_len < 10:
                    issues.append(f"{filepath}: Title too short ({title_len} chars)")
            else:
                issues.append(f"{filepath}: Missing <title> tag")
                
            # Check meta description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', content, re.IGNORECASE)
            if desc_match:
                desc_len = len(desc_match.group(1).strip())
                if desc_len > 160:
                    issues.append(f"{filepath}: Meta description too long ({desc_len} chars)")
                if desc_len < 50:
                    issues.append(f"{filepath}: Meta description too short ({desc_len} chars)")
            else:
                issues.append(f"{filepath}: Missing meta description")
                
            # H1 check
            h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
            if len(h1_matches) == 0:
                issues.append(f"{filepath}: Missing H1 tag")
            elif len(h1_matches) > 1:
                issues.append(f"{filepath}: Multiple H1 tags ({len(h1_matches)})")
                
    return issues

print("Running SEO audit on Vindkollen static files...")
issues = analyze_seo("/data/workspace/projects/vindkollen/static")
for issue in issues:
    print(issue)
print(f"Total issues found: {len(issues)}")
