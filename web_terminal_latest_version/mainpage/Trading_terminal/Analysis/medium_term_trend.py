import pandas as pd
import numpy as np
import pandas_ta as ta


def supertrend(df: pd.DataFrame):
    periods  = 10
    multiplier = 3.0

    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=periods, multiplier=3)
    dataframe = pd.concat([df, sti], axis=1)
    dataframe = dataframe.rename(columns={'SUPERTd_10_3.0': 'supertrend_Trend', 'SUPERT_10_3.0':'supertrend_Bound'})
    dataframe = dataframe.drop(['SUPERTl_10_3.0', 'SUPERTs_10_3.0'], axis=1)
    return dataframe