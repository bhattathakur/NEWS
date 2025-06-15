import streamlit as st
from datetime import datetime
import pytz


#page configuration
st.set_page_config(layout='wide')

eastern=pytz.timezone('US/EASTERN')

#st.write("will be completed later")
st.write(f"current datetime: {datetime.now(eastern).strftime('%H:%M, %Y-%m-%d')}")

st.markdown("""
# 📈 Welcome to the Market News & Ticker Insights App

This app helps you stay informed with real-time stock market and financial news. It offers intelligent tools for filtering, analyzing, and interacting with news headlines — powered by AI and the Finnhub API.

---

## 🔍 Key Features

- 📡 **Real-Time News Feed**  
  Pulls the latest financial news using the **Finnhub API**.

- 🗂️ **Dual News Modes**  
  - **Market News** – General stock market news  
  - **Ticker News** – Company-specific headlines (e.g., AAPL, TSLA)

- 📅 **Custom Date & Source Filters**  
  Easily filter news by:
  - Date range
  - Preferred news source

- 🧠 **Sentiment Analysis with Transformers**  
  Uses a transformer-based language model to classify headlines as:
  - Positive
  - Neutral
  - Negative

- 📊 **Ticker-Specific Sentiment Analysis**  
  View sentiment breakdowns specifically for the selected ticker.

- 🔊 **Text-to-Speech and Save to File**  
  - Read the news aloud using text-to-speech (Read Aloud) 
  - Save selected articles to a `.txt` file for future reference

---

## ✨ How to Use

1. Use the sidebar to choose **Market News** or **Ticker News**.
2. Filter by **date** or **news source**.
3. Toggle **sentiment analysis** to classify headlines.
4. Optionally, use **text-to-speech** (Read Aloud) to listen, or save articles for later.

---

## ⚠️ Disclaimer

This application is intended for informational and educational purposes only.  
It does **not** constitute financial advice or investment recommendations.  
Please consult a licensed financial advisor before making any investment decisions.

The app relies on third-party data sources (e.g., Finnhub), and while care has been taken to ensure accuracy, we do not guarantee the completeness or correctness of the data.

Use at your own risk.

---
""")
st.sidebar.write("\n\n\n")
st.sidebar.write("⚠️Disclaimer: Only Intended for Research and Education")
