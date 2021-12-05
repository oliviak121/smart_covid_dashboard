from markupsafe import Markup
import requests
import json
from global_vars import *

with open('config.json') as file:
    config = json.load(file)


def news_API_request():
    search_news_list = []
    # so each term can be searched seperately and artilcles dont have to have every key term to be flagged
    search_terms = config["search_terms"]
    base_url = "https://newsapi.org/v2/everything?q="
    api_key = config["api_key"]
    q = ""
    for item in search_terms:
        q = item
        complete_url = base_url + q + api_key
        response = requests.get(complete_url)
        if response.status_code == 200:
            articles = response.json()["articles"]
            for article in articles:
                search_news_list = {
                    "title": article["title"],
                    "content": article["description"] + Markup(" <a href=" + article["url"] + ">" + "read more ..." + "<a>")}
                news_list.insert(0, search_news_list)  # appends to top of list
    return news_list
