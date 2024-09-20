import pandas as pd
import datetime
import pytz

def long_term_trend_1(dataframe: pd.DataFrame, use_today_for_decision_making = False):
    """
    Use 120 MA - 5 MA cross and 850 MA for decision making

    Args:
        dataframe: pd.DataFrame that contains Open, Close, High, Low, Volume, and Time

    Returns:
        Decision: 'Long', 'Short', 'Long No Change', 'Short No Change'
        
    TODO:
        Add branch for Long no cross and short no cross
    """
    recent_low = dataframe.iloc[-1]['Low']
    recent_MA850 = dataframe.iloc[-1]['MA850']
    if recent_low <=  recent_MA850 * 1.01:
        return 'Long', datetime.datetime.strptime(str(dataframe.iloc[-1]["Time"]), "%Y%m%d")
    pre_MA120 = dataframe.iloc[-2]["MA120"]
    pre_MA4 = dataframe.iloc[-2]["MA4"]
    post_MA120 = dataframe.iloc[-1]["MA120"]
    post_MA4 = dataframe.iloc[-1]["MA4"]
    if pre_MA120 >= pre_MA4 and post_MA120 <= post_MA4:
        return 'Long', datetime.datetime.strptime(str(dataframe.iloc[-1]["Time"]), "%Y%m%d")
    elif pre_MA120 <= pre_MA4 and post_MA120 >= post_MA4:
        return 'Short', datetime.datetime.strptime(str(dataframe.iloc[-1]["Time"]), "%Y%m%d")
    else:
        if post_MA120 > post_MA4:
            date = None
            for i in range(len(dataframe) - 1, -1, -1):
                loop_MA120 = dataframe.at[i, "MA120"]
                loop_MA4 = dataframe.at[i, "MA4"]
                if loop_MA120 <= loop_MA4:
                    date = datetime.datetime.strptime(str(dataframe.at[i+1, "Time"]), "%Y%m%d")
                    return "Short", date
            
            return "Short", datetime.datetime.strptime(str(dataframe.at[0, "Time"]), "%Y%m%d")
        else:
            date = None
            for i in range(len(dataframe) - 1, -1, -1):
                loop_MA120 = dataframe.at[i, "MA120"]
                loop_MA4 = dataframe.at[i, "MA4"]
                if loop_MA120 >= loop_MA4:
                    date = datetime.datetime.strptime(str(dataframe.at[i+1, "Time"]), "%Y%m%d")
                    return "Long", date
            return "Long", datetime.datetime.strptime(str(dataframe.at[i+1, "Time"]), "%Y%m%d")


def long_term_trend_2(dataframe: pd.DataFrame):
    return 0