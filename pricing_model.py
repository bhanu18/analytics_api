import pandas as pd
import yfinance as yf
import numpy as np

# Parameters
ticker = 'aapl'  # Replace with your desired stock ticker 
lookback_months = 3
buy_threshold = 0.15  # 15% price increase to trigger buy
sell_threshold = -0.15  # 15% price decrease to trigger sell

# Fetch historical data 
data = yf.download(ticker, period='1y')  # Download one year of data

# Calculate percentage change over the lookback period
data['pct_change'] = data['Adj Close'].pct_change(periods=lookback_months * 21)  # Assuming roughly 21 trading days per month

# Latest price change
current_change = data['pct_change'].iloc[-1]

# Decision logic
if current_change > buy_threshold:
    print(f'BUY signal for {ticker}')
elif current_change < sell_threshold:
    print(f'SELL signal for {ticker}')
else:
    print(f'No strong signal for {ticker}')