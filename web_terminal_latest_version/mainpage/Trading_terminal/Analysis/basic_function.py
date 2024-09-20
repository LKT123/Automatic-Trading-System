
# Package required
import pandas as pd
import numpy as np

"""
Technical indicator calculation
For return format, see the documentations in logic.py
"""

"""
stochastic RSI
"""
def Stoch_RSI(dataframe, lengthRSI=14, lengthStoch=14, smoothK=3, smoothD=3):
    # Calculate RSI
    rsi(dataframe, lengthRSI)

    # Calculate Stochastic RSI (StochRSI_K)
    dataframe['min_rsi'] = dataframe['RSI'].rolling(window=lengthStoch).min()
    dataframe['max_rsi'] = dataframe['RSI'].rolling(window=lengthStoch).max()
    dataframe['rsv_rsi'] = (dataframe['RSI'] - dataframe['min_rsi']) / (dataframe['max_rsi'] - dataframe['min_rsi']) * 100

    # Smooth StochRSI_K to get StochRSI_D
    dataframe["StochRSI_K"] = dataframe['rsv_rsi'].rolling(window=smoothK).mean()
    dataframe['StochRSI_D'] = dataframe["StochRSI_K"].rolling(window=smoothD).mean()

    dataframe['StochRSI_J'] = (3 * dataframe['StochRSI_K']) - (2 * dataframe['StochRSI_D'])

    dataframe.drop(['min_rsi', 'max_rsi', 'rsv_rsi'], axis=1, inplace=True)
    #dataframe.drop(['L9', 'H9', 'rsv'], axis=1, inplace=True)


"""
skdj calculation
"""
def kdj(data, k_period=9, k_smooth=3, d_smooth=3):
    # Calculate %K
    data['L9'] = data['Low'].rolling(window=k_period).min()
    data['H9'] = data['High'].rolling(window=k_period).max()
    data['rsv'] = ((data['Close'] - data['L9']) / (data['H9'] - data['L9'])) * 100

    # Calculate %D
    data['%K'] = data['rsv'].rolling(window=k_smooth).mean()
    data['%D'] = data['%K'].rolling(window=d_smooth).mean()

    # Calculate %J
    data['%J'] = (3 * data['%K']) - (2 * data['%D'])

    data.drop(['L9', 'H9', 'rsv'], axis=1, inplace=True)


"""
Moving Average
"""
def simple_moving_avevrage(df: pd.DataFrame, ma_list=[10, 20, 30, 60, 120]):
    for i in ma_list:
        df["MA"+str(i)] = df['Close'].rolling(i).mean()


"""
MACD calculation
"""
def macd(dataframe: pd.DataFrame, short_period=12, long_period=26, signal_period=9):
    # Calculate the short-term EMA
    short_ema = dataframe['Close'].ewm(span=short_period, adjust=False).mean()
    
    # Calculate the long-term EMA
    long_ema = dataframe['Close'].ewm(span=long_period, adjust=False).mean()
    
    # Calculate the MACD line
    macd_line = short_ema - long_ema
    
    # Calculate the signal line (a 9-day EMA of the MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate the MACD histogram
    macd_histogram = macd_line - signal_line
    
    # Add the MACD values as new columns to the original DataFrame
    dataframe['MACD_leading'] = macd_line
    dataframe['MACD_Lagging'] = signal_line
    dataframe['MACD_diff'] = macd_histogram

"""
percent change
"""
def calculate_percent_changes(df):
    # Calculate the trading session percent change
    df['%Trading_Session_Change'] = ((df['Close'] - df['Open']) / df['Close']) * 100
    
    # Calculate the overnight percent change
    df['%Overnight_Change'] = ((df['Open'] - df['Close'].shift(1)) / df['Close']) * 100

    df['%Overall_Change'] = ((df['Close'] - df['Close'].shift(1)) / df['Close']) * 100


"""
RSI calculation
"""
def rsi(df, periods = 14):
    """
    Returns a pd.Series with the relative strength index.
    """
    close_delta = df['Close'].diff()
    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
    ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
    df['RSI'] = 100 - (100/(1 + ma_up / ma_down))
