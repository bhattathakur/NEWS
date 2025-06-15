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
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from collections import Counter
from transformers import pipeline

    # Cancel any ongoing speech when the app loads

st.set_page_config(
    page_title="Stock News Sentiment App",
    page_icon="📰",
    layout="wide",         # 👈 This makes it full-width
    initial_sidebar_state="auto"
)
components.html(
        """
        <script>
        window.speechSynthesis.cancel();
        </script>
        """,
        height=0
)

tab_names=["TICKER NEWS","SENTIMENT STATISTICS"]

tab1,tab2=st.tabs(tab_names)


#tabs

with tab1:
    


    finnhub_api_key=st.secrets['finnhub']['apikey']#os.getenv("FINNHUB_API_KEY") #api key for finnhub


    #eastern time zone
    eastern=pytz.timezone('US/EASTERN')
    #st.write(f"current datetime: {datetime.now(eastern)}")
    st.write(f"current datetime: {datetime.now(eastern).strftime('%H:%M, %Y-%m-%d')}")

    finnhub_client=finnhub.Client(api_key=finnhub_api_key)

    #enter the ticker name
    ticker_box=st.sidebar.text_input("Enter a ticker name")
    ticker_box=ticker_box.upper()

    st.sidebar.write(f"You have entered: {ticker_box}")

    if not ticker_box:st.stop()

    #top news 
    try:
        today=datetime.now(eastern).strftime('%Y-%m-%d')
        yesterday=datetime.now(eastern)-timedelta(days=2)
        yesterday=yesterday.strftime('%Y-%m-%d')
        headline_news=finnhub_client.company_news(ticker_box,_from=yesterday,to=today)  #general news
    except:
        #st.write("Error in the API data extraction !!! \n Try Again !!!")
        st.write(f'{ticker_box} NEWS not found ..only NorthAmerican company Newas are supported ... check and try again !!!')
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
    sentiment=st.sidebar.checkbox("Select for Sentiment Analyis with transformers")
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

    # Download button for .txt file

    if debug:st.dataframe(temp_df2)
    read_aloud=st.sidebar.checkbox("🔊Read Aloud")
    st.sidebar.download_button(
        label="📄 Download News as Plain Text",
        data=plain_text,
        file_name=f"{ticker_box}_news_{date_radio}_{source_radio}_highlights.txt",
        mime="text/plain"
    )


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
    st.sidebar.write("\n\n\n")
    st.sidebar.write("⚠️Disclaimer: Only Intended for Research and Education")
    
    #tab2
    with tab2:
        debug=False
        if not sentiment:
            st.warning("Sentiment Needs to be selected !!!")
            st.stop()
        temp_df2.insert(1,"ticker",ticker_box)
        st.header(f"Ticker: {ticker_box} | Date: {date_radio} | Source: {source_radio}")
        if 'sentiment_result' in temp_df2.columns:temp_df2.drop('sentiment_result',axis=1,inplace=True)
        if 'summary' in temp_df2.columns:temp_df2.drop('summary',axis=1,inplace=True)
        if 'url' in temp_df2.columns:temp_df2.drop('url',axis=1,inplace=True)
        if 'category' in temp_df2.columns:temp_df2.drop('category',axis=1,inplace=True)


        #for plots
        counts=Counter(temp_df2['sentiment'])
        if debug:st.write(counts)


         #Fixed order
        #ordered_labels = ['positive', 'neutral', 'negative']
        ordered_labels = ['positive','negative']
        ordered_labels=[i.upper() for i in ordered_labels]
        ordered_counts = [counts.get(label, 0) for label in ordered_labels]

        if debug:st.write(ordered_counts)
        colors = ['green','red']
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.pie(ordered_counts, labels=ordered_labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"{ticker_box} Sentiment Distribution")

        # Equal aspect ratio ensures the pie is drawn as a circle
        ax.axis('equal')
        st.pyplot(fig)
        st.markdown("# Related Table")
        st.dataframe(temp_df2)


        st.sidebar.write("\n\n\n")
        st.sidebar.write("⚠️Disclaimer: Only Intended for Research and Education")

