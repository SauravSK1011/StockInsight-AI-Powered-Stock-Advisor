from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from subpart import getmoneycontrolnews

import streamlit as st
import os
from dotenv import load_dotenv
from subpart2 import getnews
load_dotenv()
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
news=getnews (input_text)
news.append(getmoneycontrolnews(input_text))
st.write(news)
if input_text:
    # st.write(news)
    st.write(chain.invoke({'share':input_text,'news_context':news}))
else :
    st.write("Please try again after some time")