import os 
import pandas as pd
import pytz
from datetime import datetime,time,timedelta
import finnhub #news api
import streamlit as st

st.set_page_config(
    page_title="Stock News Sentiment App",
    page_icon="📰",
    layout="wide",         # 👈 This makes it full-width
    initial_sidebar_state="auto"
)


finnhub_api_key=os.getenv("FINNHUB_API_KEY") #api key for finnhub


#eastern time zone
eastern=pytz.timezone('US/EASTERN')


finnhub_client=finnhub.Client(api_key=finnhub_api_key)

#top news 
headline_news=finnhub_client.general_news('general',min_id=0)  #general news





debug=True
if debug:
    print(headline_news[:3])

#function to parse the json from top_news or ticker news
def parse_news(top_news):
  temp_text=""
  for i,news in enumerate(top_news):
    unix_datetime=top_news[i].get('datetime')
    estdatetime=datetime.fromtimestamp(unix_datetime,tz=eastern).strftime('%H:%M:%S, %Y-%m-%d')
    headline=top_news[i].get('headline')
    source=top_news[i].get('source')
    url=top_news[i].get('url')
    news_text=f"""
  datetime : {estdatetime}
  headline : {headline}
  source   : {source}
  url      : {url}
    """
    temp_text+=news_text
    #print(f"datetime:{estdatetime}\nheadline:{headline}\nsource:{source}\nurl: {url}")
  #print(temp_text)
  return temp_text

if debug:
   print(parse_news(headline_news))


#


#streamlit program
st.title("📰 Stock News Sentiment App")
st.header("LAST 50 NEWS")

#sidebar
st.sidebar.title(
   'test'
)

st.text(parse_news(headline_news))




