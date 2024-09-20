from threading import Lock
from time import sleep
import datetime
import pytz 
from .Trading_terminal.terminal import *
import pandas as pd


class BackendManager:
    _lock = Lock()
    
    """
    Cache Key Form: All parameter added together, separated by " ", based on their order in the function
    Cache Value Form: Time Stamp + result
    """
    _cache = {}
    
    
    
    def auto_update(self):
        """
        Description: Update the information everyday after the normal trading session. It will execute the task at 16:00:30 regardless of the weekdays or weekends
        """
        # Request the data
        if not self._cache:
            """
            Task Block
            """
            with data_request_lock:
                runtime_log.time_interval = 1
                program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                sleep(2)
                cached_dataframe = pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
            price_list = cached_dataframe['Close'].tolist()
            prediction_result, place_holder = runtime_log.timesfm_forecast_model.make_a_forecast("day", cached_dataframe['Close'].tolist())
            self._cache['home.html timesfm'] = [price_list[len(price_list)-60:], prediction_result]
        while True:
            # Load the time
            last_recorded_trading_date = datetime.datetime.strptime(str(cached_dataframe.loc[len(cached_dataframe), 'Time']), '%Y%m%d').date()
            current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
            
            # Run the update and sleep to the next day
            if current_time.hours >= 16 and current_time.date() == last_recorded_trading_date:
                """
                Task Block
                """
                with data_request_lock:
                    runtime_log.time_interval = 1
                    program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                    sleep(2)
                    cached_dataframe = pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
                price_list = cached_dataframe['Close'].tolist()
                prediction_result, place_holder = runtime_log.timesfm_forecast_model.make_a_forecast("day", price_list)
                self._cache['home.html timesfm'] = [price_list[len(price_list)-60:], prediction_result]
                # 24 hour
                """
                Sleep Block
                """
                basic_sleep_time = 86400
                diff_hour_in_sec = (current_time.hour - 16) * 3600
                diff_min_in_sec = current_time.minute  * 60
                diff_sec =  current_time.second - 30
                total_sleep_time = basic_sleep_time - diff_hour_in_sec - diff_min_in_sec - diff_sec
                sleep(total_sleep_time)
            # During the trading session, sleep to the end
            elif current_time.hours < 16 and current_time.date() == last_recorded_trading_date:
                sleep(   (16-current_time.hour)*3600 - current_time.minute*60 + 30)
                
            # Before the trading session, sleep for an hour (No need to caliberate the time)
            elif current_time.hours < 16 and current_time.date() > last_recorded_trading_date:
                sleep(3600)
            # The information is not up to date, update the information and hand the control to the previous one
            else:
                with data_request_lock:
                    runtime_log.time_interval = 1
                    program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                    sleep(2)
                    cached_dataframe = pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
                price_list = cached_dataframe['Close'].tolist()
                prediction_result, place_holder = runtime_log.timesfm_forecast_model.make_a_forecast("day", price_list)
                self._cache['home.html timesfm'] = [price_list[len(price_list)-60:], prediction_result]

        
        
        
    
    def backward_test(self, start_date, end_date, stock_code, setting_and_indicators):
        try:
            # start_date = datetime.datetime.strptime(start_date, r'%Y-%m-%d')
            # end_date = datetime.datetime.strptime(end_date, r'%Y-%m-%d')
            setting_list = ["Model A", "Enable Fed Decision"]
            
            # Request for the data
            with data_request_lock:
                runtime_log.time_interval = 7
                runtime_log.runtime_flash[7] = []
                program.reqHistoricalData(1, build_contract([stock_code, 'STK', 'SMART', 'USD']), '', '10 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                sleep(2)
                price_data = pd.DataFrame(runtime_log.runtime_flash[7], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time'])
                
            # sort based on the indicators and settings
            fed_decision_list = []
            temp_indicator_list, temp_setting_list = [], []
            for i in setting_and_indicators:
                if i not in setting_list:
                    temp_indicator_list.append(i)
                else:
                    temp_setting_list.append(i)
            
            negative_list = []
            economic_indicators = []
            for i in temp_indicator_list:
                if i[0:3] == "Neg":
                    negative_list.append(i[10:])
                else:
                    economic_indicators.append(i)
                    
            
            setting_list = temp_setting_list
                
                
            # Load the setting
            if "Enable Fed Decision" in setting_list:    
                fed_decision_list = runtime_log.program_setting['historical_fed_opinion']
            else:
                fed_decision_list = []
                
                
            # Run the backward test
            result =  night_sky(start_date, 
                                end_date, 
                                fed_decision_list, 
                                False, 
                                runtime_log.macro_data, 
                                price_data, 
                                [economic_indicators, 
                                 negative_list]
                                )
            
            return [result[0].profit_array, result[1], result[2], result[3], result[4]]
        except error as e :
            print("The Error is:\n", e)
            return []