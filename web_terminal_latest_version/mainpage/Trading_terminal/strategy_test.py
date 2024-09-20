#from charset_normalizer import detect
import matplotlib
matplotlib.use('agg')
import pandas as pd
import numpy as np
from .strategy import *
import datetime
import os
import pytz
from dateutil.relativedelta import relativedelta
from itertools import combinations
import matplotlib.pyplot as plt
from matplotlib import gridspec


class status:
    def __init__(self, current_date, fund_available):
        self.last_operation_date = current_date
        self.current_date = current_date
        self.last_operation = None
        self.holding_price = None
        self.fund_available = fund_available
        self.have_stock = False
        self.action_time = None
        self.concurrent_profit_tracker = 100
        self.current_price = None
        self.strategy = None
        self.profit_array = []
        self.decision_array = []
        self.max_loss = 0

    def print_variables(self):
        print("last_operation_date:", self.last_operation_date)
        print("current_date:", self.current_date)
        print("last_operation:", self.last_operation)
        #print("holding_price:", self.holding_price)
        #print("fund_available:", self.fund_available)
        print("have_stock:", self.have_stock)
        print("action_time:", self.action_time)
        print("concurrent_profit_tracker:", self.concurrent_profit_tracker)
        print("current_price:", self.current_price)
        #print("strategy:", self.strategy)
        
        #print(self.concurrent_profit_tracker)
        print('------------------------------------------------#####------------------------------------------------')

# build the macro_data_tree
def load_macro_data(path:str, filenames):
    result = {}
    for i in filenames:
        if i != 'qqq.csv':
            df = pd.read_csv(path +  '/' + i)
            tag = i.split('.')
            result[tag[0]] =  df
    return result

def load_index_price(path:str):
    return pd.read_csv(path + '/qqq.csv')

def parse_macro_data(date:datetime.datetime, df_dict: dict):
    result = {}
    for i in df_dict.keys():
        df = df_dict[i]
        index = 0
        for k in range(0, len(df)):
            time =  datetime.datetime.strptime(df.loc[k, 'Release_Date'], '%B %d %Y')
            #if date == time:
            #    index = k
                #print(date, i, index, 'date == time Triggered')
            #    break
            #if i == 'Core Inflation Rate YoY':
            #    print(date, time)
            if date < time:
                index = k -1
                #print(date, i, index, 'date < time Triggered')
                break
            if k == len(df)-1:
                index = k + 1
        result[i] = df.loc[0: index].copy()
    #print("Inside", result['Core Inflation Rate YoY'])
    return result

def parse_index_price(index, df: pd.DataFrame, length = 1000):
    start_index = max(0, index - length + 1)
    return df.iloc[start_index: index], df.iloc[start_index: index+1],

def simulation(begin_date, end_date, fed_decision_list, step_result = True, dict_macro = None, df_index_price = None, economic_indicator_set = [], folder_path = 'test/data'):
    # Load data
    if dict_macro is None or df_index_price is None:
        dict_macro =  load_macro_data(folder_path, os.listdir(folder_path))
        df_index_price = load_index_price(folder_path)
        for tag in dict_macro:
            dict_macro[tag] = dict_macro[tag].astype(str)
    else:
        simple_moving_avevrage(df_index_price, [4, 20, 120, 850])
    # Data preprocessing
    begin_index = -1
    end_index = -1
    
    #print("date", type(begin_date), begin_date)
    #print("date", type(end_date), end_date)
    
    for i in range(0, len(df_index_price)):
        date = datetime.datetime.strptime(str(df_index_price.loc[i, 'Time']), '%Y%m%d').date()
        #print("date", type(date), date)
        if date == begin_date:
            begin_index = i
        if date == end_date:
            end_index = i
            break
    ########################################################################################
    account_status = status(begin_date, 1000)
    test = 6
    
    fed_decision_morning = None
    fed_decision_evening = None
    counter = 0
    # print(df_index_price.tail(2))
    # print(begin_index)
    # print(end_index)
    
    
    for i in range(begin_index, end_index+1):
        
        
        
        # Data Processing
        current_date = datetime.datetime.strptime(str(int(df_index_price.loc[i, 'Time'])), '%Y%m%d')
        #print(fed_decision_list)
        if len(fed_decision_list) == 0:
            fed_decision_morning, fed_decision_evening = None, None
        else:
            while datetime.datetime.strptime(fed_decision_list[counter][1], "%B %d %Y") <= current_date:
                counter += 1
                if counter >= len(fed_decision_list):
                    break
            counter -= 1
            if counter < 0:
                counter = 0
                fed_decision_morning = None
                fed_decision_evening = None
            elif datetime.datetime.strptime(fed_decision_list[counter][1], "%B %d %Y") == current_date:
                fed_decision_evening = fed_decision_list[counter]
            else:
                fed_decision_morning = fed_decision_list[counter]
                fed_decision_evening = fed_decision_list[counter]
        
        
        
        
        simulated_price_df_moring,  simulated_price_df_moring_afternoon = parse_index_price(i, df_index_price)
        simulated_macro_dict = parse_macro_data(current_date, dict_macro)

        simulated_price_df_moring.reset_index(drop=True, inplace=True)
        simulated_price_df_moring.loc[:, 'Time'] = simulated_price_df_moring['Time'].astype(int).astype(str)
        simulated_price_df_moring_afternoon.reset_index(drop=True, inplace=True)
        simulated_price_df_moring_afternoon.loc[:, 'Time'] = simulated_price_df_moring_afternoon['Time'].astype(int).astype(str)
        
        # Strategy Selection
        strategy_morning = 'N'
        strategy_evening = 'N'
        #fed_decision_morning, fed_decision_evening = None, None
        strategy_morning  = ma850_ma120_ma4_macro_supertrend(simulated_price_df_moring, simulated_macro_dict, 
                                                             economic_indicator_set[0], economic_indicator_set[1], fed_decision_morning, current_date)
        strategy_evening  = ma850_ma120_ma4_macro_supertrend(simulated_price_df_moring_afternoon, simulated_macro_dict, 
                                                             economic_indicator_set[0], economic_indicator_set[1], fed_decision_evening, current_date)
                    #strategy_morning  = ma850_ma120_ma4_macro_supertrend(simulated_price_df_moring, simulated_macro_dict, element_list[k][0], element_list[k][1], None, current_date)

        
        # Simulation
        account_status.current_date = current_date
        
        if strategy_morning == 'L':
            """        
            self.last_operation_date = current_date
            self.last_operation = None
            self.holding_price = None
            self.cumulative_profits = 0
            self.fund_available = fund_available
            """
            if account_status.have_stock == False:
                account_status.holding_price = df_index_price.loc[i, 'Open']
                account_status.last_operation = 'L'
                account_status.last_operation_date = current_date
                account_status.have_stock = True
                account_status.action_time = 'Morning'
                account_status.current_price = df_index_price.loc[i, 'Open']
                if step_result:
                    account_status.print_variables()      
            else:
                if account_status.last_operation == 'S':
                    old_price = account_status.holding_price
                    new_price = df_index_price.loc[i, 'Open']
                    profit_rate = (old_price - new_price)/old_price + 1
                    account_status.fund_available = account_status.fund_available * profit_rate
                    
                    account_status.last_operation_date = current_date
                    account_status.last_operation = 'L'
                    account_status.holding_price = df_index_price.loc[i, 'Open']
                    account_status.action_time = 'Morning'
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (1+(account_status.current_price - new_price)/account_status.current_price)
                    account_status.current_price = new_price
                    if step_result:
                        account_status.print_variables()
                else:
                    new_price = df_index_price.loc[i, 'Open']
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (new_price/account_status.current_price)
                    account_status.current_price = new_price    
        else:
            if account_status.have_stock == False:
                account_status.holding_price = df_index_price.loc[i, 'Open']
                account_status.last_operation = 'S'
                account_status.last_operation_date = current_date
                account_status.have_stock = True
                account_status.action_time = 'Morning'
                account_status.current_price = df_index_price.loc[i, 'Open']
                if step_result:
                    account_status.print_variables()    
            else:
                if account_status.last_operation == 'L':
                    old_price = account_status.holding_price
                    new_price = df_index_price.loc[i, 'Open']
                    profit_rate = (new_price - old_price)/old_price + 1
                    #print('Profit Rate: ', profit_rate)
                    account_status.fund_available = account_status.fund_available * profit_rate
                    
                    account_status.last_operation_date = current_date
                    account_status.last_operation = 'S'
                    account_status.holding_price = df_index_price.loc[i, 'Open']
                    account_status.action_time = 'Morning'
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (new_price/account_status.current_price)
                    account_status.current_price = new_price
                    if step_result:
                        account_status.print_variables()    
                else:
                    new_price = df_index_price.loc[i, 'Open']
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (1+(account_status.current_price- new_price)/account_status.current_price)
                    account_status.current_price = new_price
                    
        if strategy_evening == 'L':
            """        
            self.last_operation_date = current_date
            self.last_operation = None
            self.holding_price = None
            self.cumulative_profits = 0
            self.fund_available = fund_available
            """
            if account_status.have_stock == False:
                account_status.holding_price = df_index_price.loc[i, 'Close']
                account_status.last_operation = 'L'
                account_status.last_operation_date = current_date
                account_status.have_stock = True
                account_status.action_time = 'Afternoon'
                new_price = df_index_price.loc[i, 'Open']
                if step_result:
                    account_status.print_variables()    
                account_status.profit_array.append(account_status.concurrent_profit_tracker)
                account_status.decision_array.append(1)
            else:
                if account_status.last_operation == 'S':
                    old_price = account_status.holding_price
                    new_price = df_index_price.loc[i, 'Close']
                    profit_rate = (old_price - new_price)/old_price + 1
                    account_status.fund_available = account_status.fund_available * profit_rate
                    
                    account_status.last_operation_date = current_date
                    account_status.last_operation = 'L'
                    account_status.holding_price = df_index_price.loc[i, 'Close']
                    account_status.action_time = 'Afternoon'
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (1+(account_status.current_price - new_price)/account_status.current_price)
                    account_status.current_price = new_price
                    account_status.profit_array.append(account_status.concurrent_profit_tracker)
                    account_status.decision_array.append(1)
                    if step_result:
                        account_status.print_variables()   
                else:
                    new_price = df_index_price.loc[i, 'Open']
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (new_price/account_status.current_price)
                    account_status.current_price = new_price
                    account_status.decision_array.append(1)
                    account_status.profit_array.append(account_status.concurrent_profit_tracker)
        else:
            if account_status.have_stock == False:
                account_status.holding_price = df_index_price.loc[i, 'Close']
                account_status.last_operation = 'S'
                account_status.last_operation_date = current_date
                account_status.have_stock = True
                account_status.action_time = 'Afternoon'
                account_status.current_price = df_index_price.loc[i, 'Open']
                account_status.profit_array.append(account_status.concurrent_profit_tracker)
                account_status.decision_array.append(-1)
                if step_result:
                    account_status.print_variables()    
            else:
                if account_status.last_operation == 'L':
                    old_price = account_status.holding_price
                    new_price = df_index_price.loc[i, 'Close']
                    profit_rate = (new_price - old_price)/old_price + 1
                    account_status.fund_available = account_status.fund_available * profit_rate
                    
                    account_status.last_operation_date = current_date
                    account_status.last_operation = 'S'
                    account_status.holding_price = df_index_price.loc[i, 'Close']
                    account_status.action_time = 'Afternoon'
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (new_price/account_status.current_price)
                    account_status.current_price = new_price
                    account_status.profit_array.append(account_status.concurrent_profit_tracker)
                    account_status.decision_array.append(-1)
                    if step_result:
                        account_status.print_variables() 
                        
                else:
                    new_price = df_index_price.loc[i, 'Open']
                    account_status.decision_array.append(-1)
                    account_status.concurrent_profit_tracker = account_status.concurrent_profit_tracker * (1+(account_status.current_price-new_price)/account_status.current_price)
                    account_status.current_price = new_price
                    account_status.profit_array.append(account_status.concurrent_profit_tracker)
        # test -= 1
        # if test <= 0:
        #     break
        
    selected_value = df_index_price.loc[begin_index:end_index, 'Close'] / df_index_price.loc[begin_index, 'Close'] * 100
    baseline_result =  selected_value.tolist()
    return account_status, baseline_result

def brute_force(begin_date, end_date, dict_macro, df_index_price, economic_indicators, fed_decision_list):
    simple_moving_avevrage(df_index_price, [4, 20, 120, 850])
    print(df_index_price)
    # Data preprocessing
    begin_index = -1
    end_index = -1
    for i in range(0, len(df_index_price)):
        date = datetime.datetime.strptime(str(df_index_price.loc[i, 'Time']), '%Y%m%d')
        if date == begin_date:
            begin_index = i
        if date == end_date:
            end_index = i
            break
    # print(begin_index, end_index)
    ########################################################################################
    element_list = []
    simulated_account_list = []
    for n in range(2, len(economic_indicators) + 1):  # n ranges from 1 to length of the list (inclusive)
        for perm in combinations(economic_indicators, n):
            element_list.append([perm, []])
            simulated_account_list.append(status(begin_date, 1000))
            for k in range(1, len(perm)):
               for negative_perm in combinations(perm, k):
                   element_list.append([perm, negative_perm])
                   simulated_account_list.append(status(begin_date, 1000))
            
    print(len(element_list))
    element_list, simulated_account_list = remove_duplicate(element_list, simulated_account_list)       
    #print(f"The number of strategies are: {len(element_list)}")  
    #account_status = status(begin_date, 1000)
    
    
    
    fed_decision_morning = None
    fed_decision_evening = None
    counter = 0
    for i in range(begin_index, end_index+1):
        
        # Data Processing
        current_date = datetime.datetime.strptime(str(int(df_index_price.loc[i, 'Time'])), '%Y%m%d')
        
        if len(fed_decision_list) == 0:
            fed_decision_morning, fed_decision_evening = None, None
        else:
            while datetime.datetime.strptime(fed_decision_list[counter][1], "%B %d %Y") <= current_date:
                counter += 1
                if counter >= len(fed_decision_list):
                    break
            counter -= 1
            if counter < 0:
                counter = 0
                fed_decision_morning = None
                fed_decision_evening = None
            elif datetime.datetime.strptime(fed_decision_list[counter][1], "%B %d %Y") == current_date:
                fed_decision_evening = fed_decision_list[counter]
            else:
                fed_decision_morning = fed_decision_list[counter]
                fed_decision_evening = fed_decision_list[counter]
                

        simulated_price_df_moring,  simulated_price_df_moring_afternoon = parse_index_price(i, df_index_price)
        simulated_macro_dict = parse_macro_data(current_date, dict_macro)

        simulated_price_df_moring.reset_index(drop=True, inplace=True)
        simulated_price_df_moring.loc[:, 'Time'] = simulated_price_df_moring['Time'].astype(int).astype(str)
        simulated_price_df_moring_afternoon.reset_index(drop=True, inplace=True)
        simulated_price_df_moring_afternoon.loc[:, 'Time'] = simulated_price_df_moring_afternoon['Time'].astype(int).astype(str)
        
        # Strategy Selection
        strategy_morning = 'N'
        strategy_evening = 'N'
        print(current_date.date())
        
        for k in range(0, len(element_list)):
            
            strategy_morning  = ma850_ma120_ma4_macro_supertrend(simulated_price_df_moring, simulated_macro_dict, element_list[k][0], element_list[k][1], fed_decision_morning, current_date)
            strategy_evening  = ma850_ma120_ma4_macro_supertrend(simulated_price_df_moring_afternoon, simulated_macro_dict, element_list[k][0], element_list[k][1], fed_decision_evening, current_date)

            
            # Simulation
            simulated_account_list[k].current_date = current_date
            
            if strategy_morning == 'L':
                """        
                self.last_operation_date = current_date
                self.last_operation = None
                self.holding_price = None
                self.cumulative_profits = 0
                self.fund_available = fund_available
                """
                if simulated_account_list[k].have_stock == False:
                    simulated_account_list[k].holding_price = df_index_price.loc[i, 'Open']
                    simulated_account_list[k].last_operation = 'L'
                    simulated_account_list[k].last_operation_date = current_date
                    simulated_account_list[k].have_stock = True
                    simulated_account_list[k].action_time = 'Morning'
                    simulated_account_list[k].current_price = df_index_price.loc[i, 'Open']
        
                else:
                    if simulated_account_list[k].last_operation == 'S':
                        old_price = simulated_account_list[k].holding_price
                        new_price = df_index_price.loc[i, 'Open']
                        profit_rate = (old_price - new_price)/old_price + 1
                        simulated_account_list[k].fund_available = simulated_account_list[k].fund_available * profit_rate
                        
                        simulated_account_list[k].last_operation_date = current_date
                        simulated_account_list[k].last_operation = 'L'
                        simulated_account_list[k].holding_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].action_time = 'Morning'
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (1+(simulated_account_list[k].current_price - new_price)/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price

                    else:
                        new_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (new_price/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price    
            else:
                if simulated_account_list[k].have_stock == False:
                    simulated_account_list[k].holding_price = df_index_price.loc[i, 'Open']
                    simulated_account_list[k].last_operation = 'S'
                    simulated_account_list[k].last_operation_date = current_date
                    simulated_account_list[k].have_stock = True
                    simulated_account_list[k].action_time = 'Morning'
                    simulated_account_list[k].current_price = df_index_price.loc[i, 'Open']
    
                else:
                    if simulated_account_list[k].last_operation == 'L':
                        old_price = simulated_account_list[k].holding_price
                        new_price = df_index_price.loc[i, 'Open']
                        profit_rate = (new_price - old_price)/old_price + 1
                        #print('Profit Rate: ', profit_rate)
                        simulated_account_list[k].fund_available = simulated_account_list[k].fund_available * profit_rate
                        
                        simulated_account_list[k].last_operation_date = current_date
                        simulated_account_list[k].last_operation = 'S'
                        simulated_account_list[k].holding_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].action_time = 'Morning'
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (new_price/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price
    
                    else:
                        new_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (1+(simulated_account_list[k].current_price- new_price)/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price
                        
            if strategy_evening == 'L':
                """        
                self.last_operation_date = current_date
                self.last_operation = None
                self.holding_price = None
                self.cumulative_profits = 0
                self.fund_available = fund_available
                """
                if simulated_account_list[k].have_stock == False:
                    simulated_account_list[k].holding_price = df_index_price.loc[i, 'Close']
                    simulated_account_list[k].last_operation = 'L'
                    simulated_account_list[k].last_operation_date = current_date
                    simulated_account_list[k].have_stock = True
                    simulated_account_list[k].action_time = 'Afternoon'
                    new_price = df_index_price.loc[i, 'Open']
                    simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                    simulated_account_list[k].decision_array.append(1)
    
                else:
                    if simulated_account_list[k].last_operation == 'S':
                        old_price = simulated_account_list[k].holding_price
                        new_price = df_index_price.loc[i, 'Close']
                        profit_rate = (old_price - new_price)/old_price + 1
                        simulated_account_list[k].fund_available = simulated_account_list[k].fund_available * profit_rate
                        
                        simulated_account_list[k].last_operation_date = current_date
                        simulated_account_list[k].last_operation = 'L'
                        simulated_account_list[k].holding_price = df_index_price.loc[i, 'Close']
                        simulated_account_list[k].action_time = 'Afternoon'
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (1+(simulated_account_list[k].current_price - new_price)/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price 
                        simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                        simulated_account_list[k].decision_array.append(0)
                    else:
                        new_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (new_price/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price  
                        simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                        simulated_account_list[k].decision_array.append(1)
            else:
                if simulated_account_list[k].have_stock == False:
                    simulated_account_list[k].holding_price = df_index_price.loc[i, 'Close']
                    simulated_account_list[k].last_operation = 'S'
                    simulated_account_list[k].last_operation_date = current_date
                    simulated_account_list[k].have_stock = True
                    simulated_account_list[k].action_time = 'Afternoon'
                    simulated_account_list[k].current_price = df_index_price.loc[i, 'Open']
                    simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                    simulated_account_list[k].decision_array.append(-1)
    
                else:
                    if simulated_account_list[k].last_operation == 'L':
                        old_price = simulated_account_list[k].holding_price
                        new_price = df_index_price.loc[i, 'Close']
                        profit_rate = (new_price - old_price)/old_price + 1
                        simulated_account_list[k].fund_available = simulated_account_list[k].fund_available * profit_rate
                        
                        simulated_account_list[k].last_operation_date = current_date
                        simulated_account_list[k].last_operation = 'S'
                        simulated_account_list[k].holding_price = df_index_price.loc[i, 'Close']
                        simulated_account_list[k].action_time = 'Afternoon'
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (new_price/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price 
                        simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                        simulated_account_list[k].decision_array.append(0)
                    else:
                        new_price = df_index_price.loc[i, 'Open']
                        simulated_account_list[k].concurrent_profit_tracker = simulated_account_list[k].concurrent_profit_tracker * (1+(simulated_account_list[k].current_price-new_price)/simulated_account_list[k].current_price)
                        simulated_account_list[k].current_price = new_price  
                        simulated_account_list[k].profit_array.append(simulated_account_list[k].concurrent_profit_tracker)
                        simulated_account_list[k].decision_array.append(-1)

    estimated_return = ((df_index_price.loc[end_index, 'Close'] - df_index_price.loc[begin_index, 'Close']) / df_index_price.loc[begin_index, 'Close'] + 1)*100
    selected_value = df_index_price.loc[begin_index:end_index, 'Close'] / df_index_price.loc[begin_index, 'Close'] * 100
    values_list = selected_value.tolist()
    result_element_list = []
    result_simulated_account_list = []
    for i in range(0,len(element_list)):
        if simulated_account_list[i].concurrent_profit_tracker >= estimated_return:
            result_element_list.append(element_list[i])
            result_simulated_account_list.append(simulated_account_list[i])
    
    return result_element_list, result_simulated_account_list, values_list

def get_max_loss(profit_array):
    local_max = profit_array[0]
    local_min = profit_array[0]
    local_max_x = 0
    local_min_x = 0
    
    
    current_max_x = 0
    current_min_x = 0
    current_max_loss = (1 - local_min/local_max) * 100
    for i in range(1, len(profit_array)):
        if profit_array[i] >= local_max:
            local_max = profit_array[i]
            local_min = profit_array[i]
            local_max_x, local_min_x = i, i
        elif profit_array[i] <= local_min:
            local_min = profit_array[i]
            local_min_x = i
            
            
        if current_max_loss < (1 - local_min/local_max) * 100:
            current_max_loss = (1 - local_min/local_max) * 100
            current_max_x, current_min_x = local_max_x, local_min_x
            
    return [current_max_loss, current_max_x, current_min_x]

def build_result(result_list, result_account, baseline_result, n=10):
    for i in range(0, len(result_list)):
        result_account[i].strategy = result_list[i]
        result_account[i].max_loss = get_max_loss(result_account[i].profit_array)
    sorted_result_account_by_profit = sorted(result_account, key=lambda x: x.concurrent_profit_tracker, reverse=True)
    sorted_result_account_by_max_loss = sorted(result_account, key=lambda x: x.max_loss[0], reverse=False)
    
    re_list_by_profit = []
    if n > len(sorted_result_account_by_profit):
        n = len(sorted_result_account_by_profit)
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    for i in range(0, n):
          # 2 Rows, 1 Column
        #gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])  # Adjust height ratios to change relative sizes

        # Plotting the first array
        #axs[0].plot(sorted_result_account_by_profit[i].profit_array)
        axs[0].plot(sorted_result_account_by_profit[i].profit_array, label='Profit', color='blue')
        axs[0].plot(baseline_result, label='Baseline', linestyle='--', color='red')
        
        x_values = list(range(sorted_result_account_by_profit[i].max_loss[1], sorted_result_account_by_profit[i].max_loss[2]+1))
        y_values = sorted_result_account_by_profit[i].profit_array[sorted_result_account_by_profit[i].max_loss[1]:sorted_result_account_by_profit[i].max_loss[2]+1]
        axs[0].plot(x_values, y_values, label='Max Loss', color='green')  
        
        axs[0].set_title('Profit tracker')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Value')

        # Plotting the second array
        axs[1].plot(sorted_result_account_by_profit[i].decision_array)
        axs[1].set_title('Operation tracker')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Action')

        # Automatically adjust subplot params to give specified padding
        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig(f'temp/by_profit_{i}.png')
        axs[0].cla()
        axs[1].cla()
        re_list_by_profit.append([sorted_result_account_by_profit[i].strategy, sorted_result_account_by_profit[i].concurrent_profit_tracker, sorted_result_account_by_profit[i].max_loss[0], f'temp/by_profit_{i}.png']) 
    re_list_by_max_loss = []
    if n > len(sorted_result_account_by_max_loss):
        n = len(sorted_result_account_by_max_loss)
    for i in range(0, n):        
        
        # Plotting the first array
        axs[0].plot(sorted_result_account_by_max_loss[i].profit_array, label='Profit', color='blue')
        axs[0].plot(baseline_result, label='Baseline', linestyle='--', color='red')
        
        x_values = list(range(sorted_result_account_by_max_loss[i].max_loss[1], sorted_result_account_by_max_loss[i].max_loss[2]+1))
        y_values = sorted_result_account_by_max_loss[i].profit_array[sorted_result_account_by_max_loss[i].max_loss[1]:sorted_result_account_by_max_loss[i].max_loss[2]+1]
        axs[0].plot(x_values, y_values, label='Max Loss', color='green')  
        
        
        axs[0].set_title('Profit tracker')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Value')

        # Plotting the second array
        axs[1].plot(sorted_result_account_by_max_loss[i].decision_array)
        axs[1].set_title('Operation tracker')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Action')

        # Automatically adjust subplot params to give specified padding
        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig(f'temp/by_max_loss_{i}.png')
        axs[0].cla()
        axs[1].cla()
        re_list_by_max_loss.append([sorted_result_account_by_max_loss[i].strategy, sorted_result_account_by_max_loss[i].concurrent_profit_tracker, sorted_result_account_by_max_loss[i].max_loss[0], f'temp/by_max_loss_{i}.png'])
        
    plt.close('all')
    return [re_list_by_profit, re_list_by_max_loss]


def remove_duplicate(result, account):
    detect_diction = {}
    processed_result = []
    processed_account = []
    for i in range(0, len(result)):
        indicator_string = " ".join(result[i][0])
        negative_string = " ".join(result[i][1])
        combined_key = indicator_string + negative_string
        if not combined_key in detect_diction:
            processed_result.append(result[i])
            processed_account.append(account[i])
            detect_diction[combined_key] = True
    return processed_result, processed_account



def sky_cloud(stock_price:pd.DataFrame, duration, max_amount, macro_diction, economic_indicator:dict, fed_decision_list, date = None, days_ahead = None):
    begin_date, end_date = None, None
    if date == None:
        if days_ahead == None:
            last_time_str = str(stock_price.iloc[-1]['Time'])
            end_date = datetime.datetime.strptime(last_time_str, '%Y%m%d')
            begin_date = end_date - relativedelta(days=duration)
        else:
            last_time_str = str(stock_price.iloc[-1]['Time'])
            end_date = datetime.datetime.strptime(last_time_str, '%Y%m%d')
            begin_date = end_date - relativedelta(days=days_ahead)
    else:
        begin_date = datetime.datetime.strptime(date[0], r'%B-%d-%Y')
        end_date = datetime.datetime.strptime(date[1], r'%B-%d-%Y')

    result_infl, account_infl, baseline_result = brute_force(begin_date, end_date, macro_diction, stock_price, economic_indicator['Inflation']+economic_indicator['Growth'], fed_decision_list)
    
    #result_growth, account_growth = brute_force(begin_date, end_date, macro_diction, stock_price, economic_indicator['Growth'])
    result_cleaned, account_cleaned = result_infl, account_infl
    result =  build_result(result_cleaned, account_cleaned, baseline_result, max_amount)
    return result

def night_sky(begin_date, end_date, fed_decision_list, step_result, dict_macro, df_index_price, economic_indicator_set):
    account_result, baseline_result =  simulation(begin_date, end_date, fed_decision_list, step_result, dict_macro, df_index_price, economic_indicator_set)
    account_result.max_loss =  get_max_loss(account_result.profit_array)
    #fig, axs = plt.subplots(2, 1)  # 2 Rows, 1 Column
    account_result.strategy = economic_indicator_set    
    return [account_result, baseline_result, account_result.concurrent_profit_tracker, account_result.max_loss, account_result.decision_array]
    
    
    

# #Load data
# print(datetime.datetime.now())
# folder_path = 'test/data'
# filenames = os.listdir(folder_path)
# begin_date = "January 10 2024"
# end_date = "May 1 2024"
# dict_macro =  load_macro_data(folder_path, filenames)
# df_index_price = load_index_price(folder_path)
# for tag in dict_macro:
#     dict_macro[tag] = dict_macro[tag].astype(str)
# # Data preprocessing
# begin_date = datetime.datetime.strptime(begin_date, '%B %d %Y')
# end_date  =  datetime.datetime.strptime(end_date, '%B %d %Y')
# decision_list = [
#         [
#             "L",
#             "January 03 2024"
#         ],
#         [
#             "L",
#             "January 31 2024"
#         ],
#         [
#             "L",
#             "March 07 2024"
#         ],
#         [
#             "S",
#             "March 29 2024"
#         ],
#         [
#             "L",
#             "April 03 2024"
#         ],
#         [
#             "L",
#             "April 10 2024"
#         ],
#         [
#             "S",
#             "April 16 2024"
#         ],
#         [
#             "L",
#             "May 01 2024"
#         ],
#         [
#             "L",
#             "May 14 2024"
#         ],
#         [
#             "S",
#             "May 22 2024"
#         ]
#     ]


# re = simulation(begin_date, end_date, decision_list, economic_indicator_set=[[ "Core PCE Price Index MoM", "Retail Sales MoM", "Durable Goods Orders MoM"], 
#                                                             [ "Core PCE Price Index MoM", "Retail Sales MoM", "Durable Goods Orders MoM"]])

# import matplotlib.pyplot as plt
# import numpy as np

# # 假设这是你的数据列表
# data = re.profit_array

# # 创建一个索引列表，对应每个数据点
# indices = range(len(data))

# # 绘制折线图
# plt.figure(figsize=(10, 5))  # 设置图形大小
# plt.plot(indices, data, marker='o')  # 绘制线条和点
# plt.xlabel('Index')  # 设置横坐标标签
# plt.ylabel('Value')  # 设置纵坐标标签

# for value, color in zip([1, 0, -1], ['green', 'gray', 'red']):
#     mask = re.decision_array == value
#     #plt.scatter(indices[mask], re.decision_array[mask], color=color, label=f'Value {value}')

# plt.title('Line Plot of Python List')  # 设置图形标题
# plt.grid(True)  # 显示网格
# plt.show()


#result_list, result_account = brute_force(begin_date, end_date, dict_macro, df_index_price, ["Core PCE Price Index MoM", "Core Inflation Rate MoM", "PPI MoM"]) #2024-03-12 March 12 2024
#result_list += result_list
#print(datetime.datetime.now())
#for i in range(0, len(result_list)):
#    if result_account[i].concurrent_profit_tracker > 100:
#        print(result_list[i])
#        result_account[i].print_variables()