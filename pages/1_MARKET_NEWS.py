import os 
import sys
import types
os.environ["STREAMLIT_WATCHER_TYPE"] = "watchdog"
# Prevent streamlit from scanning torch.classes
import torch
torch.classes.__path__ = types.SimpleNamespace(_path=[])  # Safe dummy path object
import pandas as pd
import pytz
from datetime import datetime,time,timedelta
import finnhub #news api
import streamlit as st
import streamlit.components.v1 as components
from transformers import pipeline
#from gtts import gTTS
#import tempfile

st.set_page_config(
    page_title="Stock News Sentiment App",
    page_icon="📰",
    layout="wide",         # 👈 This makes it full-width
    initial_sidebar_state="auto"
)

# Cancel any ongoing speech when the app loads
components.html(
    """
    <script>
    window.speechSynthesis.cancel();
    </script>
    """,
    height=0
)


finnhub_api_key=os.getenv("FINNHUB_API_KEY") #api key for finnhub


#eastern time zone
eastern=pytz.timezone('US/EASTERN')
st.write(f"current datetime: {datetime.now(eastern)}")


finnhub_client=finnhub.Client(api_key=finnhub_api_key)

#top news 
try:
  headline_news=finnhub_client.general_news('general',min_id=0)  #general news
except:
   st.write("Error in the API data extraction !!! \n Try Again !!!")
   st.stop()


#create a function to create a dataframe from the news
def get_news_df(api_news):
  temp_df=pd.DataFrame(api_news)

  #change unix datatime to est
  temp_df['estdatetime']=pd.to_datetime(temp_df['datetime'],unit='s',utc=True)\
  .dt.tz_convert('US/Eastern')\
  .dt.strftime("%H:%M:%S %Y-%m-%d")
  #get date and time
  temp_df['date']=temp_df['estdatetime'].apply(lambda x:x.split(' ')[1])
  #temp_df['hour']=temp_df['estdatetime'].dt.hour

  return temp_df

selected_columns=['category','estdatetime','date','headline','source','summary','url']
news_df=get_news_df(headline_news)[selected_columns]
#if empty stop
if news_df.empty:
   st.write(f'Empty DataFrame...Exiting !!!')
   st.stop()
debug=False

if debug:st.dataframe(news_df)

#unique dates and sources
unique_date=news_df['date'].unique().tolist()
unique_source=news_df['source'].unique().tolist()

if debug:st.write(f"  unique_dates: {unique_date}")
if debug:st.write(f"unique_sources: {unique_source}")

#sidebar
with st.sidebar:
  date_radio=st.radio('choose a date',['all']+unique_date)
with st.sidebar:
  source_radio=st.radio('choose a source',['all']+unique_source)

if debug:st.write(f"selected_date: {date_radio}\nsource_radio: {source_radio}")

temp_df1=news_df.query("date==@date_radio") if date_radio in unique_date else news_df
#temp_df2=news_df.query("source==@source_radio") if source_radio in unique_source else news_df
temp_df2=temp_df1.query("source==@source_radio") if source_radio in unique_source else temp_df1

temp_df2=temp_df2.reset_index(drop=True)

#read aloud part ... for this dataframe needs to be non-empty
if temp_df2.empty:st.stop()
#want sentiment analysis
sentiment=st.sidebar.checkbox("Want Centiment Analyis with transformers?")
#Load sentiment pipeline once (might take a few seconds)
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
#sentiment analysis
if sentiment:
   sentiment_model=load_model()
   temp_df2['sentiment_result']=temp_df2['headline'].apply(lambda x: sentiment_model(x)[0])
   temp_df2['sentiment']=temp_df2['sentiment_result'].apply(lambda x:x.get('label'))
   temp_df2['score']=temp_df2['sentiment_result'].apply(lambda x:x.get('score'))
# else:
#    temp_df2['sentiment']='N/A'
#    temp_df2['score']='N/A'

#st.write(f"temp_df1: {temp_df1}")
if debug:st.dataframe(temp_df2)
#create a query based on the choosen options
# query_statement=f"""

# """
plain_text="" #save in the file
# Display each row as an HTML paragraph
sentiment_color={'POSITIVE':'green','NEGATIVE':'red','NEUTRAL':'gray'}
for _, row in temp_df2.iterrows():
    st.markdown(
        f"""
        <p style="font-size:16px;">
        <b>{row['estdatetime']}</b><br>
        <span style="color:magenta; font-size:28px;"><i>{row['headline']}</i></span><br>
        Sentiment: <span style="color:{sentiment_color.get(row.get('sentiment','N/A'),'black')};">{row.get('sentiment','N/A')}</span> <br>
        Source   : {row['source']}<br>
        <a href="{row['url']}" target="_blank">Read more</a>
        </p>
        <hr>
        """,
        unsafe_allow_html=True
    )
   # Build plain text version
    plain_text += f"{row['estdatetime']}\n"
    plain_text += f"{row['headline']}\n"
    plain_text += f"Sentiment:{row.get('sentiment','N/A')}\n"
    plain_text += f"Score    :{row.get('score',0):0.3f}\n"
    plain_text += f"Source   :{row['source']}\n"
    plain_text += f"Link     :{row['url']}\n"
    plain_text += "-" * 40 + "\n"

# #want sentiment analysis
# sentiment=st.sidebar.checkbox("Want Centiment Analyis with transformers?")
# #Load sentiment pipeline once (might take a few seconds)
# @st.cache_resource
# def load_model():
#     return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
# #sentiment analysis
# if sentiment:
#    sentiment_model=load_model()
#    temp_df2['sentiment_result']=temp_df2['headline'].apply(lambda x: sentiment_model(x)[0])
#    temp_df2['sentiment']=temp_df2['sentiment_result'].apply(lambda x:x.get('label'))
#    temp_df2['score']=temp_df2['sentiment_result'].apply(lambda x:x.get('score'))

# Download button for .txt file

if debug:st.dataframe(temp_df2)
st.sidebar.download_button(
    label="📄 Download News as Plain Text",
    data=plain_text,
    file_name=f"news_{date_radio}_{source_radio}_highlights.txt",
    mime="text/plain"
)

read_aloud=st.sidebar.checkbox("🔊Read Aloud")

reading_text="\n".join(temp_df2['headline'].tolist())
if debug:st.write(reading_text)

if read_aloud:
  st.sidebar.write("Reading Alound ... ")
   # Inject JavaScript to speak text immediately
  safe_text = reading_text.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
  js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{safe_text}");
    window.speechSynthesis.speak(msg);
    </script>
  """
  components.html(js_code, height=0)


  #  #changing text to speech
  #  tts=gTTS(text=reading_text,lang='en')

  #  with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
  #    tts.save(tmp.name)
  #    st.audio(tmp.name, format="audio/mp3")



# if debug:
#     print(headline_news[:3])

# #function to parse the json from top_news or ticker news
# def parse_news(top_news):
#   temp_text=""
#   for i,news in enumerate(top_news):
#     unix_datetime=top_news[i].get('datetime')
#     estdatetime=datetime.fromtimestamp(unix_datetime,tz=eastern).strftime('%H:%M:%S, %Y-%m-%d')
#     headline=top_news[i].get('headline')
#     source=top_news[i].get('source')
#     url=top_news[i].get('url')
#     news_text=f"""
#   datetime : {estdatetime}
#   headline : {headline}
#   source   : {source}
#   url      : {url}
#     """
#     temp_text+=news_text
#     #print(f"datetime:{estdatetime}\nheadline:{headline}\nsource:{source}\nurl: {url}")
#   #print(temp_text)
#   return temp_text

# if debug:
#    print(parse_news(headline_news))


# #


# #streamlit program
# st.title("📰 Stock News Sentiment App")
# st.header("LAST 50 NEWS")

# #sidebar
# st.sidebar.title(
#    'test'
# )

# st.text(parse_news(headline_news))




