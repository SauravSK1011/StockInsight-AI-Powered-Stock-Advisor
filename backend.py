import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import os
from dotenv import load_dotenv
load_dotenv()

# Function to fetch Moneycontrol News
def getmoneycontrolnews(sharename):
    if not sharename:
        return []  # Return an empty list if sharename is empty
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    encoded_share = urllib.parse.quote(sharename)
    url = f"https://www.google.com/search?q={encoded_share}%20share%20news"
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "moneycontrol" in href:
            mlink = href
            break
    mrequest = requests.get(mlink, headers=headers)
    msoup = BeautifulSoup(mrequest.text, 'html.parser')
    for link in msoup.find_all("a"):
        href = link.get("href")
        if href and "news/business" in href:
            if sharename.split() and sharename.split()[0].lower() in href.lower():
                absolute_url = urllib.parse.urljoin(mlink, href)
                links.append(absolute_url)
    return list(set(links))

# Function to fetch News
def getnews(sharename):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    encoded_share = urllib.parse.quote(sharename)
    url = f"https://www.google.com/search?q={encoded_share}%20news"
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    news = soup.find_all("div", class_="m7jPZ")
    links = [n.find("a", class_="WlydOe").get("href") for n in news if sharename.lower() in n.text.lower()]
    return list(set(links))

# Langchain OpenAI setup
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

prompt = ChatPromptTemplate.from_messages(
    [("system", "User will give latest news share now answer in 50 words that should its time to buy {share} or sell {share} dont answer hold"),
     ("user", "Share news :{news_context}")]
)

# Streamlit UI
st.set_page_config(page_title="StockInsight AI Advisor", layout="wide")
st.title('StockInsight – AI-Powered Stock Advisor')
st.markdown("""
Welcome to StockInsight, your go-to platform for AI-powered stock predictions based on the latest news. Enter the stock name to get news and AI predictions.
""")

# Input for stock share name
input_text = st.text_input("Search the Share you want", "")

# OpenAI LLM setup
llm = ChatOpenAI(model="gpt-3.5-turbo")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    # Get news from multiple sources
    linklist = getnews(input_text)
    linklist2 = getmoneycontrolnews(input_text)
    news_combined = linklist + linklist2

    # Display the latest news in cards
    st.subheader("Latest News of the Share")
    
    # Create a container for news cards
    news_container = st.container()
    with news_container:
        # Create a 2-column layout for cards
        cols = st.columns(2)

        # Loop through the links and display them in cards
        for i, link in enumerate(linklist + linklist2):
            col = cols[i % 2]  # Alternate columns
            with col:
                # Fetch the title of the news article
                news_title = link.split("/")[-1].replace("-", " ").title()
                # Display the news in a card-like format
                st.markdown(f"""
                <div style="background-color:#f1f1f1;padding:10px;border-radius:8px;margin-bottom:10px;">
                    <h5><a href="{link}" target="_blank" style="color:#1a73e8;text-decoration:none;">{news_title}</a></h5>
                    <p><a href="{link}" target="_blank" style="color:#1a73e8;text-decoration:none;">Read More</a></p>
                </div>
                """, unsafe_allow_html=True)

    # Display AI predictions
    st.subheader("Predictions from StockInsight AI")
    prediction = chain.invoke({'share': input_text, 'news_context': news_combined})
    st.write(prediction)
else:
    st.write("Please enter a stock name to get predictions.")
