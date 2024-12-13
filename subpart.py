import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

def getmoneycontrolnews(sharename):
    if not sharename:
        return []  # Return an empty list if sharename is empty
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    encoded_share = urllib.parse.quote(sharename)
    url = f"https://www.google.com/search?q={encoded_share}%20share%20news"
    print(sharename)
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    soupp = soup.prettify()
    links = soup.find_all("a")
    mlink = ""
    
    for link in links:
        href = link.get("href")
        if href and "moneycontrol" in href:
            mlink = href
            break
    
    links = []
    mrequest = requests.get(mlink, headers=headers)
    msoup = BeautifulSoup(mrequest.text, 'html.parser')
    mlinks = msoup.find_all("a")
    
    for link in mlinks:
        href = link.get("href")
        if href and "news/business" in href:
            # Ensure sharename is not empty and properly split
            if sharename.split():
                if sharename.split()[0].lower() in href.lower():
                    absolute_url = urllib.parse.urljoin(mlink, href)  # Convert to absolute URL if it's relative
                    links.append(absolute_url)

    allheadingsh1 = []
    allheadingsh2 = []
    para = []

    links = list(set(links))
    print(str(len(links)) + " links found")
    max_links = links[:5]
    linklist={}

    for link in max_links:
        time.sleep(2)
        prequest = requests.get(link, headers=headers)
        psoup = BeautifulSoup(prequest.text, 'html.parser')
        hs1=psoup.find("h1")
        linklist[hs1.text]=link

        headingsh1 = psoup.find_all("h1")
        for h1 in headingsh1:
            allheadingsh1.append(h1.text)
        
        headingsh2 = psoup.find_all("h2")
        for h2 in headingsh2:
            allheadingsh2.append(h2.text)
        
        para1 = psoup.find_all("p")
        for p in para1:
            para.append(p.text)

    sorted_paragraphs = sorted(para, key=lambda para: count_occurrences(para, sharename), reverse=True)
    return linklist,sorted_paragraphs[:5]

def count_occurrences(paragraph, target):
    return paragraph.lower().count(target.lower())

