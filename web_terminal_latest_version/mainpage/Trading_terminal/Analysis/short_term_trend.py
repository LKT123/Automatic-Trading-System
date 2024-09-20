import pandas as pd
import numpy as np
import math

def sqzmom_lb(df: pd.DataFrame):
    """
    Imported from Trading view
    Link: https://www.tradingview.com/chart/vgfKfdM9/?symbol=QQQ
    TODO: update and make it return a dataframe
    """
    # parameter setup
    length = 20
    mult = 2
    length_KC = 20
    mult_KC = 1.5

    # calculate BB
    m_avg = df['Close'].rolling(window=length).mean()
    m_std = df['Close'].rolling(window=length).std(ddof=0)
    df['upper_BB'] = m_avg + mult_KC * m_std                         # Need more detailed examination
    df['lower_BB'] = m_avg - mult_KC * m_std

    # calculate true range
    df['tr0'] = abs(df["High"] - df["Low"])
    df['tr1'] = abs(df["High"] - df["Close"].shift())
    df['tr2'] = abs(df["Low"] - df["Close"].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)

    # calculate KC
    range_ma = df['tr'].rolling(window=length_KC).mean()
    df['upper_KC'] = m_avg + range_ma * mult_KC
    df['lower_KC'] = m_avg - range_ma * mult_KC

    # calculate bar value
    highest = df['High'].rolling(window = length_KC).max()
    lowest = df['Low'].rolling(window = length_KC).min()
    m1 = (highest + lowest)/2
    df['value'] = (df['Close'] - (m1 + m_avg)/2)
    fit_y = np.array(range(0,length_KC))
    df['value'] = df['value'].rolling(window = length_KC).apply(lambda x: 
                            np.polyfit(fit_y, x, 1)[0] * (length_KC-1) + 
                            np.polyfit(fit_y, x, 1)[1], raw=True)

    # check for 'squeeze'
    df['squeeze_on'] = (df['lower_BB'] > df['lower_KC']) & (df['upper_BB'] < df['upper_KC'])
    df['squeeze_off'] = (df['lower_BB'] < df['lower_KC']) & (df['upper_BB'] > df['upper_KC'])
    df = df.drop(['upper_BB', 'lower_BB', 'tr0', 'tr1', 'tr2', 'tr', 'upper_KC', 'lower_KC', 'squeeze_off'], axis = 1)
    df = df.rename(columns={'squeeze_on': 'sqzmob_squeeze_on', 'sqzmob_value':'supertrend_Bound'})
    return df