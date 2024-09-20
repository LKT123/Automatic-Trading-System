"""
Logic control for operations based on analysis result

- Update 2024/04/28: From now on, this file will be used to preprocess the data from the terminal.py and pass it to the analysis only. It will no longer be used as a decision forming program.
"""
import pandas as pd
from .Analysis.basic_function import *
from .strategy import *
import pytz
import datetime
from .runtime_log import Runtime_log

"""
Given the amount available, generate contract and order for the return function
@param data_bundle
@return 'L', 'S', 'E'
"""
def decision(runtime_log:Runtime_log):
    if runtime_log.status == "Aborted":
        print("Program Aborted")
        return 'E'
    elif runtime_log.status == 'Force Long':
        print("Force Long")
        return 'L'
    elif runtime_log.status == 'Force Short':
        print("Force Short")
        return 'S'
    elif runtime_log.status == 'Force Cash':
        print("Force Cash")
        return 'E'
    runtime_flash_map, runtime_macro_data, runtime_fomc_decision = runtime_log.runtime_flash, runtime_log.macro_data, runtime_log.fed_opinion
    
    #print("####################################################################################", runtime_log.fed_opinion)
    #print("####################################################################################", runtime_fomc_decision)

    """convert all the data list into dataframe"""
    #df_30min_data = pd.DataFrame(runtime_flash_map[0], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
    df_1day_data = pd.DataFrame(runtime_flash_map[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
    #df_1week_data = pd.DataFrame(runtime_flash_map[2], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])

    """Calculate kdj value, store the result as '%K', '%D', '%J' """
    #kdj(df_30min_data)
    #kdj(df_1week_data)
    #kdj(df_1day_data)

    """Calculate the RSI related value, store the result as 'RSI', 'StochRSI_K', 'StochRSI_D' """
    #Stoch_RSI(df_30min_data)
    #Stoch_RSI(df_1week_data)
    #Stoch_RSI(df_1day_data)

    """Calculate the MACD value, store the result as 'MACD_leading', 'MACD_lagging', 'MACD_diff' """

    #macd(df_1day_data)
    #macd(df_1week_data)
    #macd(df_30min_data)


    """Calculate the moving average"""
    simple_moving_avevrage(df_1day_data, [4, 20, 120, 850])

    #for i in runtime_macro_data.keys():
    #    runtime_macro_data[i].to_csv('test/data/'+i+".csv", index=False)
    #df_1day_data.to_csv('test/data/qqq.csv', index=False)


    """
    *************************************************************************
    Subject to future changes (Depends on the development progress on models)
    *************************************************************************
    """
    print(df_1day_data.tail(2))

    """Spill the test data"""
    #df_1day_data.to_csv('testdata_qqq_1day_full_scale_extended_ta.csv', index=False)
    #df_1day_data.print("sss")

    current_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute
    index = 0
    use_today_for_decision_making = False
    if (current_hour == 15 and 51<= current_minute <= 59) or (current_hour == 16 and current_minute == 0): #Use today's kdy
        index = len(df_1day_data) - 1
        use_today_for_decision_making = True
    else: # Use the previous day's kdj 
        index = len(df_1day_data) - 2
        df_1day_data = df_1day_data.drop(df_1day_data.index[-1])
    
    #print('Success*******************************************************')
    result = ma850_ma120_ma4_macro_supertrend(df_1day_data, runtime_macro_data, runtime_log.program_setting["macro_indicators"], runtime_log.program_setting["macro_indicators_negative_list"], runtime_fomc_decision)
    print(f"Timestamp: {current_hour}:{current_minute} EST   result: {result}")
    return result




# Test Section

#if __name__  == '__main__':
#    from data_capture.main import macro_data_capture
#    df = pd.read_csv('Analysis/dataset/qqq_adjusted_23Y_1day.csv')
#    simple_moving_avevrage(df, [4, 20, 120, 850])
#    runtime_macro_data = macro_data_capture()
#    result = ma850_ma120_ma4_macro_supertrend(df, runtime_macro_data)
#    print(result)


