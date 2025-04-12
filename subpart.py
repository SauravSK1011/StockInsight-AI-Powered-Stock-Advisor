import requests
from bs4 import BeautifulSoup
import urllib.parse

def getmoneycontrolnews(sharename):
    if not sharename:
        return []  # Return an empty list if sharename is empty

    # Use a direct approach to get news from Moneycontrol
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        # Try to directly access Moneycontrol search
        encoded_share = urllib.parse.quote(sharename)
        url = f"https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={encoded_share}"

        # If that doesn't work, try a more general approach
        fallback_url = f"https://www.moneycontrol.com/news/business/stocks/"

        # Try the direct URL first
        request = requests.get(url, headers=headers)

        # If that fails, use the fallback
        if request.status_code != 200:
            request = requests.get(fallback_url, headers=headers)

        soup = BeautifulSoup(request.text, 'html.parser')
        links = []

        # Look for news articles
        articles = soup.find_all(['h2', 'h3'])

        for article in articles:
            # Try to find links within these headings
            link_tag = article.find('a')
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                # Check if the article is related to our stock
                if sharename.lower() in article.text.lower():
                    if not href.startswith('http'):
                        href = 'https://www.moneycontrol.com' + href
                    links.append(href)

        # If we didn't find any specific articles, add the main page as a fallback
        if not links:
            links.append(f"https://www.moneycontrol.com/news/business/stocks/")

        return list(set(links))
    except Exception as e:
        print(f"Error fetching moneycontrol news: {e}")
        # Return a fallback link if everything fails
        return ["https://www.moneycontrol.com/news/business/stocks/"]