import os
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

def fix_links_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not href.startswith(("#", "mailto:", "tel:", "http")) and not href.endswith(".html"):
            a_tag["href"] = href + ".html"
            
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

def main():
    base_dir = "projects/vindkollen/static"
    html_files = find_html_files(base_dir)
    
    for file in html_files:
        print(f"Fixing links in: {file}")
        fix_links_in_file(file)
        
    print("Link fixing complete.")

if __name__ == "__main__":
    main()
