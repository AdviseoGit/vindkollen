import os
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def find_html_files(directory):
    html_files = []
    for root, _, files in os.walk(directory):
        if "drafts" in root:
            continue
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files

def check_links(file_path, base_url):
    broken_links = []
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue

        url = urljoin(base_url, href)
        
        # Check if it's a local file
        parsed_url = urlparse(url)
        if parsed_url.scheme in ["", "file"]:
            local_path = os.path.join(os.path.dirname(file_path), href)
            if not os.path.exists(local_path):
                 broken_links.append((href, "Local file not found"))
            continue

        try:
            response = requests.get(url, timeout=5)
            if response.status_code >= 400:
                broken_links.append((url, response.status_code))
        except requests.RequestException as e:
            broken_links.append((url, str(e)))
            
    return broken_links

def main():
    base_dir = "projects/vindkollen/static"
    base_url = "https://vindkoll.se/"
    html_files = find_html_files(base_dir)
    
    report = ""
    
    for file in html_files:
        relative_path = os.path.relpath(file, base_dir)
        page_url = urljoin(base_url, relative_path)
        
        report += f"Checking links in: {file} (URL: {page_url})\n"
        broken = check_links(file, page_url)
        if broken:
            report += "  Broken links found:\n"
            for link, status in broken:
                report += f"    - {link} (Status: {status})\n"
        else:
            report += "  No broken links found.\n"
        report += "-"*20 + "\n"
        
    with open("projects/vindkollen/seo_analysis_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("Link checking complete. Report saved to projects/vindkollen/seo_analysis_report.txt")

if __name__ == "__main__":
    main()
