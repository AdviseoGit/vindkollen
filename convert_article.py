import markdown2
import argparse

def convert_md_to_html(md_path, html_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = markdown2.markdown(md_content)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Converted {md_path} to {html_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML.')
    parser.add_argument('md_path', help='Path to the input Markdown file.')
    parser.add_argument('html_path', help='Path to the output HTML file.')
    args = parser.parse_args()
    
    convert_md_to_html(args.md_path, args.html_path)

if __name__ == "__main__":
    main()
