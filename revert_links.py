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

def revert_links_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    made_changes = False
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.endswith(".html"):
            new_href = href[:-5]
            a_tag["href"] = new_href
            made_changes = True

    if made_changes:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        return True
    return False

def main():
    base_dir = "projects/vindkollen/static"
    html_files = find_html_files(base_dir)
    
    print("Starting link reversion process...")
    for file in html_files:
        if revert_links_in_file(file):
            print(f"  Reverted links in: {file}")
    print("Link reversion complete.")

if __name__ == "__main__":
    main()
