from pytrends.request import TrendReq
import pandas as pd

def get_related_queries():
    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list = ["vindkraft"]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 1-m', geo='SE', gprop='')

    related_queries = pytrends.related_queries()
    
    top_queries = related_queries['vindkraft']['top']
    rising_queries = related_queries['vindkraft']['rising']

    with open("projects/vindkollen/trends.txt", "w", encoding="utf-8") as f:
        f.write("Top queries related to 'vindkraft':\n")
        if top_queries is not None:
            f.write(top_queries.to_string(index=False))
        else:
            f.write("No top queries found.\n")
            
        f.write("\n\nRising queries related to 'vindkraft':\n")
        if rising_queries is not None:
            f.write(rising_queries.to_string(index=False))
        else:
            f.write("No rising queries found.\n")

if __name__ == "__main__":
    get_related_queries()
