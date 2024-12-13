import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

def getnews( sharename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    encoded_share = urllib.parse.quote(sharename)
    url = f"https://www.google.com/search?q={encoded_share}%20news"
    print(sharename)
    request= requests.get(url,headers=headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    soupp=soup.prettify()
    news=soup.find_all("div",class_="m7jPZ")
    links=[]
    for n in news:
     if sharename in n.text.lower():
        link=n.find("a",class_="WlydOe")
        links.append(link.get("href"))
    allheadingsh1=[]
    allheadingsh2=[]
    para=[]

    links=list(set(links))
    print(str(len(links))+" links found")
    max_links = links[:5]
    linklist={}
    for link in max_links:
        time.sleep(2)
        prequest= requests.get(link,headers=headers)
        psoup = BeautifulSoup(prequest.text, 'html.parser')
        hs1=psoup.find("h1")
        linklist[hs1.text]=link
        headingsh1=psoup.find_all("h1")
        for h1 in headingsh1:
            allheadingsh1.append(h1.text)
        headingsh2=psoup.find_all("h2")
        for h2 in headingsh2:
            allheadingsh2.append(h1.text)
        para1=psoup.find_all("p")
        for p in para1:
            para.append(p.text)
    sorted_paragraphs = sorted(para, key=lambda para: count_occurrences(para, sharename), reverse=True)
    return linklist, sorted_paragraphs[:10]


def count_occurrences(paragraph, target):
    return paragraph.lower().count(target.lower())
