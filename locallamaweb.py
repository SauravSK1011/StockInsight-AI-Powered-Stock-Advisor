from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from  langchain_community.llms import Ollama


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
        ("system","User will give prompt for creating website create a website and give code"),
        ("user","prompt :{news_context}")
    ]
)

## streamlit framework

st.title('StockInsight – AI-Powered Stock Advisor')
input_text=st.text_input("Search the Share u want")

# openAI LLm 
llm=Ollama(model="llama3.2")
output_parser=StrOutputParser()
chain=prompt|llm|output_parser
if input_text:
    # st.write(news)
    st.write(chain.invoke({'news_context':input_text}))
else :
    st.write("Please try again after some time")  
    
