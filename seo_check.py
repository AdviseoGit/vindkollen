import glob
from bs4 import BeautifulSoup

def check_seo():
    for f in glob.glob('/data/workspace/projects/vindkollen/static/**/*.html', recursive=True):
        with open(f, 'r') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.title.string if soup.title else None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            h1 = soup.h1.text if soup.h1 else None
            schema = soup.find('script', type='application/ld+json')
            print(f"{f}: Title: {bool(title)}, Desc: {bool(meta_desc)}, H1: {bool(h1)}, Schema: {bool(schema)}")

if __name__ == '__main__':
    check_seo()
