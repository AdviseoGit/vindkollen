
import requests
from bs4 import BeautifulSoup
import json

def get_wind_power_trends():
    """
    Scrapes relevant websites for the latest news and developments in wind power.
    """
    urls = {
        "Svensk Vindenergi": "https://svenskvindenergi.org/nyheter",
        "Energimyndigheten": "https://www.energimyndigheten.se/nyhetsarkiv/",
        "Ny Teknik": "https://www.nyteknik.se/topic/vindkraft",
    }

    trends = {}

    for source, url in urls.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, "html.parser")

            if source == "Svensk Vindenergi":
                headlines = soup.find_all("h3", class_="c-news-list__heading", limit=5)
                trends[source] = [headline.text.strip() for headline in headlines]
            elif source == "Energimyndigheten":
                headlines = soup.find_all("h2", class_="font-weight-bold", limit=5)
                trends[source] = [headline.text.strip() for headline in headlines]
            elif source == "Ny Teknik":
                headlines = soup.find_all("h3", class_="article-list-item__heading", limit=5)
                trends[source] = [headline.text.strip() for headline in headlines]

        except requests.exceptions.RequestException as e:
            trends[source] = f"Error fetching content: {e}"
        except Exception as e:
            trends[source] = f"An unexpected error occurred: {e}"

    return trends

if __name__ == "__main__":
    trends = get_wind_power_trends()
    with open("projects/vindkollen/trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False, indent=4)

    print("Wind power trends have been saved to projects/vindkollen/trends.json")
