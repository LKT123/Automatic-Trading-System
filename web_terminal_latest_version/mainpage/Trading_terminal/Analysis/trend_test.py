# Standard test template
import pandas as pd
from short_term_trend import *
from long_term_trend import *
from medium_term_trend import *
from basic_function import *


def long_term_trend_1_test(df: pd.DataFrame):
    start_index = 200
    result_list = []
    for i in range(0, 200):
        result_list.append("N/A")
    for i in range(start_index, len(df)):
        data_section = df.iloc[i-2: i+1]
        result_list.append(long_term_trend_1(data_section, True))
    df['Result'] = result_list
    return df

def sqzmom_lb_test(df: pd.DataFrame, Full_scale = False):
    sqzmom_lb(df)

    return df

def supertrend_test(df: pd.DataFrame):
    return supertrend(df)

def long_term_trend_2_test(df: pd.DataFrame):
    return df



#----------------------------------------------------------------------------------------------

def main():
    setting()

def setting(Full_scale_output = False, use_price_only = True):
    df = pd.read_csv("dataset/qqq_adjusted_23Y_1day.csv")
    if use_price_only:
        df = df[['High', 'Low', 'Open', 'Close', 'Time']]
    simple_moving_avevrage(df, [4, 20, 120, 850])
    print(df.columns)
    #------------------------------------------------------------------------------------------
    #   Test Function
    df = sqzmom_lb(df)
    #------------------------------------------------------------------------------------------
    df = df.drop(['MA4', 'MA20', 'MA120', 'MA850'], axis=1)
    print(df.tail(100))
    if Full_scale_output:
        df.to_csv("trend_test.csv", index=False)
    else:
        df = df.tail(365)
        df.to_csv("trend_test.csv", index=False)



if __name__ == '__main__':
    main()


#----------------------------------------------------------------------------------------------