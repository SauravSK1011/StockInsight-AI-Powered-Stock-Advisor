import requests
from bs4 import BeautifulSoup
import urllib.parse

def getnews(sharename):
    if not sharename:
        return []  # Return an empty list if sharename is empty

    try:
        # Try to get news from Yahoo Finance
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        encoded_share = urllib.parse.quote(sharename)

        # Try Yahoo Finance
        yahoo_url = f"https://finance.yahoo.com/quote/{encoded_share}/news"

        # Fallback to a general search if Yahoo doesn't work
        fallback_url = f"https://www.google.com/search?q={encoded_share}+stock+news&tbm=nws"

        # Try Yahoo first
        request = requests.get(yahoo_url, headers=headers)

        # If that fails, use the fallback
        if request.status_code != 200:
            request = requests.get(fallback_url, headers=headers)

        soup = BeautifulSoup(request.text, 'html.parser')
        links = []

        # Look for news links in various formats
        # Try to find all anchor tags
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            # Check if it's a news link and contains our stock name
            if href and ('news' in href or 'article' in href):
                # Extract the text associated with this link
                link_text = a_tag.text.strip()
                if link_text and sharename.lower() in link_text.lower():
                    # Make sure it's a full URL
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif not href.startswith('http'):
                        # If it's from Yahoo
                        if 'yahoo' in request.url:
                            href = 'https://finance.yahoo.com' + href
                        else:
                            continue  # Skip relative links we can't resolve

                    # Clean up Google redirect URLs
                    if 'google.com' in href and '/url?q=' in href:
                        href = href.split('/url?q=')[1].split('&')[0]

                    links.append(href)

        # If we didn't find any links, add some default financial news sites
        if not links:
            links = [
                f"https://finance.yahoo.com/quote/{encoded_share}/news",
                f"https://www.reuters.com/search/news?blob={encoded_share}",
                f"https://www.bloomberg.com/search?query={encoded_share}"
            ]

        return list(set(links))
    except Exception as e:
        print(f"Error fetching news: {e}")
        # Return some default financial news sites
        return [
            "https://finance.yahoo.com/news/",
            "https://www.reuters.com/business/",
            "https://www.bloomberg.com/markets"
        ]