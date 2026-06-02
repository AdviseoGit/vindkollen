import markdown2
import os

def convert_md_to_html(md_path, html_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = markdown2.markdown(md_content)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Converted {md_path} to {html_path}")

def main():
    md_file = "projects/vindkollen/content/blog/fordelar-och-nackdelar-med-vindkraft.md"
    html_file = "projects/vindkollen/content/blog/fordelar-och-nackdelar-med-vindkraft.html"
    convert_md_to_html(md_file, html_file)

if __name__ == "__main__":
    main()
