from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()



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

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
## Langmith tracking
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

prompt=ChatPromptTemplate.from_messages(
    [
        ("system","User will give latest news share now answer in 50 words that should its time to buy {share} or sell {share} dont answer hold"),
        ("user","Share news :{news_context}")
    ]
)

## streamlit framework

st.title('StockInsight – AI-Powered Stock Advisor')
input_text=st.text_input("Search the Share u want")

# openAI LLm 
llm=ChatOpenAI(model="gpt-3.5-turbo")
output_parser=StrOutputParser()
chain=prompt|llm|output_parser
linklist, news=getnews (input_text)
linklist2,news2=getmoneycontrolnews(input_text)
if isinstance(news, list) and isinstance(news2, list):
    news_combined = news + news2
    print("news_combined")
else:
    news_combined = news
if input_text:
    st.write("Latest News Of Shares:-")
    for title, url in linklist.items():
        st.markdown(f"[{title}]({url})")
    for title, url in linklist2.items():
        st.markdown(f"[{title}]({url})")
    st.write("Priduction of StockInsight AI from Latest News")
    st.write(chain.invoke({'share':input_text,'news_context':news_combined}))
else :
    st.write("Please try again after some time")
    
    
    
    

