
"""
*************************************************************************
This file is used to store the first generation model that fails to work.
*************************************************************************
"""

import pandas as pd


"""
*************************************************************************
                    Basic Technical Analysis Models
*************************************************************************
"""

"""Model 1: Naive Stochastic Ocillartor"""
def naive_stochastic_ocillator_diff(df:pd.DataFrame, index: int):
    diff = df.at[index, "%K"] - df.at[index-1, "%D"]
    print(f"diff: {diff}")
    if diff > 0:
        return 'L'
    elif diff < 0:
        return 'S'
    else:
        return 'U'


"""Model 2: Stochastic Ocillator with RSI threshold"""
# Use the RSI difference as an addiiton evaluation condition to rule the short-term fluctuation of kdj
def stochastic_ocillator_rsi_diff(df:pd.DataFrame, index:int):

    if df.at[index, "%K"] - df.at[index, "%D"] >= 0 :
        if df.at[index-1, "%K"] - df.at[index-1, "%D"] >= 0:
            return 'L'
        else:
            rsi_diff = df.at[index, 'RSI'] - df.at[index-1, 'RSI']
            if rsi_diff < 0:
                return 'S'
            else:
                return 'L'
    else:
        if df.at[index-1, "%K"] - df.at[index-1, "%D"] <= 0:
            return 'S' 
        else:
            rsi_diff = df.at[index, 'RSI'] - df.at[index-1, 'RSI']
            if rsi_diff > 0:
                return 'L'
            else:
                return 'S'
            
"""Model 3: stochastic rsi"""
def stochastic_rsi_diff(df:pd.DataFrame, index:int):
    diff = df.at[index, "StochRSI_K"] - df.at[index, "StochRSI_D"]
    if diff > 0:
        return 'L'
    elif diff < 0:
        return 'S'
    else:
        return 'U'

"""Model 4: Decision Tree"""
"""
Decision Table:

Over Bought & Over Sold
(RSI > 72) => -
(RSI < 32) => +
    RSI         KDJ         StochRSI        Result
     -           +              +            Long
     -           +              -            Short
     -           -              +            Short
     -           -              -            Short
     +           +              +            Long
     +           +              -            Long
     +           -              +            Long
     +           -              -            Short

Normal Sotuation:

Subtable
R(+)/R(-): Relative strength

    RSI_diff(3 day lagging)         MACD_diff        MA_cross (1, 2)        R(+)/R(-)
            +                           +                   +                    +
            +                           +                   -                    +
            +                           -                   +                    +
            +                           -                   -                    -
            -                           +                   +                    +
            -                           +                   -                    -
            -                           -                   +                    -
            -                           -                   -                    -
    
Main Decision Table:
    R(+)/R(-)      KDJ         StochRSI        Result
        -           +              +            Long
        -           +              -            Short
        -           -              +            Short
        -           -              -            Short
        +           +              +            Long
        +           +              -            Long
        +           -              +            Long
        +           -              -            Short

"""
def decision_tree(df: pd.DataFrame, index: int):
    # Same day indicator
    kdj_diff = df.at[index, "%K"] - df.at[index, "%D"]
    stochrsi_diff = df.at[index, "StochRSI_K"] - df.at[index, "StochRSI_D"]

    r_list = [df.at[index, "MACD_diff"],df.at[index, "Close"] - df.at[index, "MA2"],df.at[index, "RSI"] - df.at[index-1, "RSI"]]

    if df.at[index, "RSI"] > 80:
        if kdj_diff > 0:
            if stochrsi_diff >= 0: 
                """
                RSI         KDJ         StochRSI        Result
                 -           +              +            Long
                """
                return 'L'
            else:
                """
                RSI         KDJ         StochRSI        Result
                 -           +              -            Short
                """
                return 'S'
        else:
            if stochrsi_diff >= 0: # 2
                """
                RSI         KDJ         StochRSI        Result
                 -           -              +            Short
                """
                return 'S'
            else:
                """
                RSI         KDJ         StochRSI        Result
                 -           -              -            Short
                """
                return 'S'
    elif df.at[index, "RSI"] < 20:   # Overall sold
        if kdj_diff >= 0: # 1
            if stochrsi_diff > 0: # 2
                """
                RSI         KDJ         StochRSI        Result
                 +           +              +            Long
                """
                return 'L'
            else:
                """
                RSI         KDJ         StochRSI        Result
                 +           +              -            Long
                """
                return 'L'
        else:
            if stochrsi_diff > 0: # 2
                """
                RSI         KDJ         StochRSI        Result
                 +           -              +            Long
                """
                return 'L'
            else:
                """
                RSI         KDJ         StochRSI        Result
                 +           -              +            Short
                """
                return 'S'
    else: #  Nomral situation
        """Calculate the R(+)/R(-) and convert the result to an integer"""
        relative_strength = 0
        for i in r_list:
            if i > 0:
                relative_strength += 1
            elif i < 0:
                relative_strength -= 1

        """Handle the edge case (Having same StochRSI_K and StochRSI_D or %K and %D)"""
        if stochrsi_diff == 0 and df.at[index, "StochRSI_K"] != 0 and (df.at[index, "StochRSI_K"] == 100 or df.at[index-1, "StochRSI_K"] - df.at[index-1, "StochRSI_D"] < 0): # treat it as it's larger than zero
            stochrsi_diff = 1
        
        if kdj_diff == 0 and df.at[index-1, "StochRSI_K"] - df.at[index-1, "StochRSI_D"] < 0:
            kdj_diff = 1

        if kdj_diff > 0: # 1
            if stochrsi_diff > 0: # 2
                if relative_strength >= 0:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        +           +              +            Long
                    """
                    return 'L'
                else:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        -           +              +            Long
                    """
                    return 'L'
            else:
                if relative_strength >= 0:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        +           +              -            Long
                    """
                    return 'L'
                else:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        -           +              -            Short
                    """
                    return 'S'      
        else:

            if stochrsi_diff > 0: # 2
                if relative_strength >= 0:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        +           -              +            Long
                    """
                    return 'L'
                else:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        -           -              +            Long
                    """
                    return 'S'
            else:
                if relative_strength >= 0:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        +           -              -            Short
                    """
                    return 'S'
                else:
                    """
                    R(+)/R(-)      KDJ         StochRSI        Result
                        +           -              -            Short
                    """
                    return 'S'

"""Model 5: Decision Tree based on Time series data"""
def time_series_decision_tree(df: pd.DataFrame, index: int):
    return 0