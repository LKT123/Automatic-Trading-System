from .Analysis.long_term_trend import *
from .Analysis.short_term_trend import *
from .Analysis.medium_term_trend import *
from .Analysis.basic_function import *
from .Analysis.macrodigest_lite.macrodigest_main import *
import pandas as pd
from datetime import datetime
import pytz

"""
Make decision based on various trend
@Return L(Long) S(Short) N(No action) E(Clear all positons)
"""
def ma850_ma120_ma4_macro_supertrend(df: pd.DataFrame, macro_dic: dict, economic_indicators, macro_indicators_negative_list, runtime_fomc_decision:list = None, current_time = datetime.now(pytz.timezone('US/Eastern')), disable_MA_techniqual_analysis = True):    
    result = 'N'
    techniqual_result, techniqual_result_date = long_term_trend_1(df) #--> 'Long', 'Short', 'datetime.datetime'
    macroeconomic_result = macro_digest_main(macro_dic, current_time, economic_indicators, macro_indicators_negative_list) #--> ['Long'/'Short', tag, Diff, 'Fresh'/'Old, Date]
    df_supertrend = supertrend(df) #--> df['supertrend_Trend'] & df['supertrend_Bound']
    latest_date = None
    
    if macroeconomic_result[3] == "Fresh":
        result = macroeconomic_result[0][0]
        latest_date = datetime.strptime(str(df.iloc[-1]['Time']), r'%Y%m%d')
    elif df_supertrend.iloc[-1]['supertrend_Trend'] == df_supertrend.iloc[-2]['supertrend_Trend']:
        # Get the start point of the current trend
        start_point = 0
        for i in range(0, len(df_supertrend)):
            if df_supertrend.iloc[-1-i]['supertrend_Trend'] != df_supertrend.iloc[-1]['supertrend_Trend']:
                start_point = -i
                break
        # Check if the macro data falls within the trend
        trend_date = datetime.strptime(str(df.iloc[-i]['Time']), r'%Y%m%d')
        #print(trend_date)
        data_release_date = datetime.strptime(macroeconomic_result[4], r'%B %d %Y')
        if runtime_fomc_decision !=  None:
            fomc_data_release_date =  datetime.strptime(runtime_fomc_decision[1], r'%B %d %Y')
            if fomc_data_release_date >= data_release_date:
                if runtime_fomc_decision[0][0] == "L":
                    macroeconomic_result[0] = 'Long'
                    data_release_date = fomc_data_release_date
                else:
                    macroeconomic_result[0] = 'Short'
                    data_release_date = fomc_data_release_date
        if trend_date <= data_release_date:
            latest_date = data_release_date
            if macroeconomic_result[0] == 'Long':
                result = 'L'
            else:
                result = 'S'
        else:
            latest_date = trend_date
            if df_supertrend.iloc[-1]['supertrend_Trend'] == 1:
                result = 'L'
            else:
                result = 'S'
    else:
        latest_date = datetime.strptime(str(df.iloc[-1]['Time']), r'%Y%m%d')
        if df_supertrend.iloc[-1]['supertrend_Trend'] == 1 and df_supertrend.iloc[-2]['supertrend_Trend'] == -1:
            result = 'L'
        else:
            result = 'S'
    if latest_date < techniqual_result_date and not disable_MA_techniqual_analysis:
        result = techniqual_result[0]
    
    return result

# On Fly test functions