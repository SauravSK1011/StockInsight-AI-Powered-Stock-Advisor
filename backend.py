import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
from dotenv import load_dotenv
load_dotenv()

# Function to fetch Moneycontrol News
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

# Function to fetch News
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

# Langchain OpenAI setup
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a financial advisor specializing in stock market analysis.
    The user will provide a stock name and possibly some news links about that stock.

    If news links are provided, analyze them to determine if it's a good time to buy or sell the stock.
    If no news links are provided or they're not accessible, use your general knowledge about the stock market and the specific company to provide advice.

    Respond in about 50 words with a clear recommendation to either BUY or SELL {share} stock.
    Do not recommend to HOLD - you must choose either BUY or SELL based on the available information.

    Provide a brief explanation for your recommendation.
    """),
    ("user", "Stock: {share}\nNews links: {news_context}")
])

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

    # Combine and deduplicate news links
    all_news_links = list(set(linklist + linklist2))

    if all_news_links:
        # Create a container for news cards
        news_container = st.container()
        with news_container:
            # Create a 2-column layout for cards
            cols = st.columns(2)

            # Loop through the links and display them in cards
            for i, link in enumerate(all_news_links):
                try:
                    col = cols[i % 2]  # Alternate columns
                    with col:
                        # Extract a readable title from the URL
                        try:
                            # Try to get the last part of the URL path and format it
                            path_parts = link.rstrip('/').split('/')
                            # Find the last non-empty part
                            title_part = next((part for part in reversed(path_parts) if part), '')
                            # Clean it up
                            news_title = title_part.replace('-', ' ').replace('_', ' ').title()

                            # If the title is too short or empty, use a domain-based title
                            if len(news_title) < 5:
                                domain = link.split('//')[1].split('/')[0]
                                news_title = f"{input_text.title()} News from {domain}"
                        except:
                            # Fallback title if parsing fails
                            domain = link.split('//')[1].split('/')[0] if '//' in link else 'News Source'
                            news_title = f"{input_text.title()} News from {domain}"

                        # Display the news in a card-like format
                        st.markdown(f"""
                        <div style="background-color:#f1f1f1;padding:10px;border-radius:8px;margin-bottom:10px;">
                            <h5><a href="{link}" target="_blank" style="color:#1a73e8;text-decoration:none;">{news_title}</a></h5>
                            <p><a href="{link}" target="_blank" style="color:#1a73e8;text-decoration:none;">Read More</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    print(f"Error displaying news card: {e}")
    else:
        st.info("No specific news articles found for this stock. Try a different stock symbol or company name.")

    # Display AI predictions
    st.subheader("Predictions from StockInsight AI")
    prediction = chain.invoke({'share': input_text, 'news_context': news_combined})
    st.write(prediction)
else:
    st.write("Please enter a stock name to get predictions.")
