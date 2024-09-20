import pandas as pd
import datetime
import pytz
import math

# Convert sting to float
def convert_to_float(s):
    if s.endswith('K') or s.endswith("%"):
        return float(s[:-1])  # 去除末尾的K并将其转换为整数
    else:
        return float(s)
    
# Given the date and the diction, return a diction that contains the data released at that date
def find_current_date_data(df_dic: dict, current_time:datetime.datetime):
    #print(current_time)
    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    day = current_time.day
    month = month_list[current_time.month-1]
    year = current_time.year
    newest_data = {}
    today_has_a_data_release = False
    for i in df_dic.keys():
        if not df_dic[i].empty:
        #print(i, df_dic[i].tail(2))
            latest_data =  df_dic[i].iloc[-1]['Release_Date']
            segments = latest_data.split(" ")
            if day == int(segments[1]) and month == segments[0] and year == int(segments[2]):
                newest_data[i] = df_dic[i].tail(1).iloc[0].tolist()
                today_has_a_data_release = True
    if not today_has_a_data_release:
        return {}
    else:
        #print(newest_data)
        return newest_data

# Given a tag and the diction, find the most recent data within that tag
def find_the_data_with_tags(df_dic:dict, tag:str):
    """
    find the latest data with the tag
    """
    try:
        target_df = df_dic[tag].dropna()
        data = target_df.tail(1).iloc[0].tolist()
        return data
    except: # Data is absent
        return []

# Given a diction of dataframe and a list of tags, return the tag that is the most fresh /  Empty if tags do not exist
def get_the_most_fresh_tag(df_dic:dict, tags:list) -> list:
    #print(df_dic['Core Inflation Rate YoY'])
    #print(df_dic['Core PCE Price Index MoM'])
    latest_tag = ""
    day, month, year = 0, 0, 0
    month_to_int = {'January': 1,'February': 2,'March': 3,'April': 4,'May': 5,'June': 6,'July': 7,'August': 8,'September': 9,'October': 10,'November': 11,'December': 12}
    for i in tags:
        #print(i)
        data = find_the_data_with_tags(df_dic, i)
        date_segments =  data[-1].split(" ")
        if int(date_segments[-1]) > year:
            latest_tag = i
            day = int(date_segments[1])
            month = month_to_int[date_segments[0]]
            year = int(date_segments[-1])
        elif month_to_int[date_segments[0]] > month and int(date_segments[-1]) == year:
            latest_tag = i
            day = int(date_segments[1])
            month = month_to_int[date_segments[0]]
            year = int(date_segments[-1])
        elif month_to_int[date_segments[0]] == month and int(date_segments[-1]) == year and int(date_segments[1]) > day:
            latest_tag = i
            day = int(date_segments[1])
            month = month_to_int[date_segments[0]]
            year = int(date_segments[-1])
    return latest_tag

def get_econ_data_for_a_given_month(df_dic:pd.DataFrame, month: int, year: int) -> dict:
    result = {}
    for i in df_dic.keys():
        df =  df_dic[i].dropna()
        keyword =  str(year) +"/" + str(month)
        if keyword in df['Date'].values:
            result[i] = df[df['Date'] == keyword]
    return result

# Get the data in the previous terms.
def get_econ_data_for_a_given_period(df_dic:pd.DataFrame, current_time:datetime.datetime, period:int) -> list:
    """
    @period: must be larger than 0
    """
    result = []
    period_month = current_time.month - period
    year = current_time.year
    if period_month <= 0:
        period_month += 12
        year -=  1
    counter = 0
    while counter < period:
        #print(get_econ_data_for_a_given_month(df_dic, period_month, year))
        result.append(get_econ_data_for_a_given_month(df_dic, period_month, year))
        counter += 1
        period_month += 1
        if period_month > 12:
            period_month -= 12
            year += 1        
    #prev_month_data = get_econ_data_for_a_given_month(df_dic, period_month, year)
    return result


def basic_economic_data_digest(df_dic: dict, current_time, tags: list, neg_long=["Core Inflation Rate YoY", "Inflation Rate YoY", "Core PCE Price Index MoM", "Unemployment Rate"]) -> list:
    """
    Takes a series of tags as input, return the most recent data and its evaluation

    @param df_dic   : The diction of dataframe that stores all the economic data
    @param tags     : The list of tags that will be considered (From most important to the least important)
    @param neg_long : Determine the evaluation. Every tag in this list will be analyzed in the opposite way. i.e. Higher diff means Long rather than Short
    @return         : list of evaluation result ['Suggested Action', tag, diff, 'data status', date(optional)]
    """
    # check if there's new data on nonfarm and inflation:
    dict_today =  find_current_date_data(df_dic, current_time)
    for i in tags:
        if i == "Core Inflation Rate YoY" or i == "Core Inflation Rate MoM":
            if "Core Inflation Rate YoY" in dict_today.keys(): # Inflation Day
                cpi_mom = dict_today['Core Inflation Rate MoM']
                cpi_yoy = dict_today['Core Inflation Rate YoY']
                mom_consensus_current_diff = convert_to_float(cpi_mom[3]) - convert_to_float(cpi_mom[1]) 
                yoy_consensus_current_diff = convert_to_float(cpi_yoy[3]) - convert_to_float(cpi_yoy[1])
                if mom_consensus_current_diff < 0 and yoy_consensus_current_diff < 0:
                    if i in neg_long:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                elif mom_consensus_current_diff > 0 and yoy_consensus_current_diff > 0:
                    if i in neg_long:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                elif mom_consensus_current_diff > 0 and yoy_consensus_current_diff == 0:
                    if i in neg_long:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                elif mom_consensus_current_diff == 0 and yoy_consensus_current_diff > 0:
                    if i in neg_long:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                elif mom_consensus_current_diff < 0 and yoy_consensus_current_diff == 0:
                    if i in neg_long:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                elif mom_consensus_current_diff == 0 and yoy_consensus_current_diff < 0:
                    if i in neg_long:
                        return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                    else:
                        return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff, 'Fresh', cpi_yoy[5]]
                else:
                    full_scale_cpi = dict_today['Inflation Rate YoY']
                    full_scale_cpi_consensus_current_diff = convert_to_float(full_scale_cpi[3]) - convert_to_float(full_scale_cpi[1])
                    return ['Long', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff, 'Fresh', full_scale_cpi[5]]
                    
        elif i in dict_today.keys():
            i_data = dict_today[i]
            i_consensus_current_diff = convert_to_float(i_data[3]) - convert_to_float(i_data[1])
            if i in neg_long:
                if i_consensus_current_diff >= 0:
                    return ['Long', i, i_consensus_current_diff, 'Fresh', i_data[5]]
                else:
                    return ['Short', i, i_consensus_current_diff, 'Fresh', i_data[5]]
            else:
                if i_consensus_current_diff >= 0:
                    return ['Short', i, i_consensus_current_diff, 'Fresh', i_data[5]]
                else:
                    return ['Long', i, i_consensus_current_diff, 'Fresh', i_data[5]]
    #print('-----------------------$$$$$$$$$$$$$$$$$$$----------------------')
    most_fresh_tag = get_the_most_fresh_tag(df_dic, tags)
    #print(current_time, most_fresh_tag, tags)
    #print('-----------------------$$$$$$$$$$$$$$$$$$$----------------------')
    if most_fresh_tag == 'Core Inflation Rate MoM' or most_fresh_tag == "Core Inflation Rate YoY":
        cpi_mom_old = find_the_data_with_tags(df_dic, 'Core Inflation Rate MoM')
        cpi_yoy_old = find_the_data_with_tags(df_dic, 'Core Inflation Rate YoY')
        mom_consensus_current_diff_old = convert_to_float(cpi_mom_old[3]) - convert_to_float(cpi_mom_old[1])
        yoy_consensus_current_diff_old = convert_to_float(cpi_yoy_old[3]) - convert_to_float(cpi_yoy_old[1])
        if mom_consensus_current_diff_old < 0 and yoy_consensus_current_diff_old < 0:
            if most_fresh_tag in neg_long:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
        elif mom_consensus_current_diff_old > 0 and yoy_consensus_current_diff_old > 0:
            if most_fresh_tag in neg_long:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]] 
        elif mom_consensus_current_diff_old > 0 and yoy_consensus_current_diff_old == 0:
            if most_fresh_tag in neg_long:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]       
        elif mom_consensus_current_diff_old == 0 and yoy_consensus_current_diff_old > 0:
            if most_fresh_tag in neg_long:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]] 
        elif mom_consensus_current_diff_old < 0 and yoy_consensus_current_diff_old == 0:
            if most_fresh_tag in neg_long:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]] 
        elif mom_consensus_current_diff_old == 0 and yoy_consensus_current_diff_old < 0:
            if most_fresh_tag in neg_long:
                return ['Short', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]]
            else:
                return ['Long', 'Core Inflation Rate YoY', yoy_consensus_current_diff_old, 'Old', cpi_yoy_old[5]] 
        else:

            full_scale_cpi_old = find_the_data_with_tags(df_dic, 'Inflation Rate YoY')
            full_scale_cpi_consensus_current_diff_old = convert_to_float(full_scale_cpi_old[3]) - convert_to_float(full_scale_cpi_old[1])
            return ['Long', 'Inflation Rate YoY', full_scale_cpi_consensus_current_diff_old, 'Old', full_scale_cpi_old[5]]
    elif most_fresh_tag in neg_long:
        neg_long_old = find_the_data_with_tags(df_dic, most_fresh_tag)
        neg_long_consensus_current_diff_old = convert_to_float(neg_long_old[3]) - convert_to_float(neg_long_old[1])
        #print(most_fresh_tag, neg_long_old, neg_long_consensus_current_diff_old)
        if neg_long_consensus_current_diff_old >= 0:
            return ['Long', most_fresh_tag, neg_long_consensus_current_diff_old, 'Old', neg_long_old[5]]
        else:
            return ['Short', most_fresh_tag, neg_long_consensus_current_diff_old, 'Old', neg_long_old[5]]
    else:
        normal_long_old = find_the_data_with_tags(df_dic, most_fresh_tag)
        normal_long_consensus_current_diff_old =  convert_to_float(normal_long_old[3]) - convert_to_float(normal_long_old[1])
        if normal_long_consensus_current_diff_old >= 0:
            return ['Short', most_fresh_tag, normal_long_consensus_current_diff_old, 'Old', normal_long_old[5]]
        else:
            return ['Long', most_fresh_tag, normal_long_consensus_current_diff_old, 'Old', normal_long_old[5]]   

def automatic_adaptive_economic_data_digest():
    return True

def macro_digest_main(df_dic: dict, current_time:datetime.datetime, economic_indicators, macro_indicators_negative_list):
    return basic_economic_data_digest(df_dic, current_time, economic_indicators, macro_indicators_negative_list)




#if __name__ == '__main__':
#    import sys
#    sys.path.append('C:/Users/Hengz/Desktop/File/Program/Python/Trading_terminal')
#    from data_capture.main import *
#    df_dic = macro_data_capture()
#    #print(df_dic.keys())
#    print(df_dic)
#    #print(basic_economic_data_digest(df_dic, ['Core Inflation Rate YoY', 'Core PCE Price Index MoM']))
