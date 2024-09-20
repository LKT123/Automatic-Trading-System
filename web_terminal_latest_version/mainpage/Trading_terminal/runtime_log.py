"""
Runtime_setting
keep a record of all runtime values
"""

import pandas as pd
import json
from .Analysis.timesfm_model.GOOGLE_TIMESFM_MODEL.timesfm_forecast import timesfm_model
import os

class Runtime_log:
    def __init__(self) -> None:
        #AI_model
        self.timesfm_forecast_model = None
        
        # Account setting
        self.account_setting = {}
        
        self.status = "Activated"

        # Store the data in each round of price requests
        self.runtime_flash = {0: [], 1:[], 2:[], 3:[], 4:[]}
        
        # Used for place order
        self.nextorderId = 0

        # To increase the speed of if condition, time_interval is represented as integer
        # time_interval = 0 : 30 mins
        # time_interval = 1 : 60 mins
        # time_interval = 2 : 120 mins
        # time_interval = 3 : 1 day
        # time_interval = 4 : 1 week
        # time_interval = 10: Ask price
        self.time_interval = -1 

        # Program setting
        self.program_setting = {}

        # Current Portfolio
        self.portfolio = {}

        # Current position: 'L', 'S', 'E'
        self.current_position = 'U'

        # Amount of stocks
        self.current_amount = -1

        # Used for purchasing stocks
        self.target_amount = -1

        # Total profit during runtime
        self.total_profit = 0

        # Profit in one round of buying and selling
        self.profit = 0
        
        self.macro_data = {}
        
        self.fed_opinion = []
        self.fed_speech = {}
        
    """Only called at the begining of the execution to load all the value properly"""
    def instant_update(self):
        print(self.portfolio)
        print(self.portfolio['portfolio'])
        if self.portfolio['portfolio'] == "empty":
            self.current_position = 'C'
            self.current_amount = 0
        elif self.portfolio['portfolio'] == self.program_setting["long_stock/etf"]:
            self.current_position = 'L'
            self.current_amount = int(self.portfolio['position'])
        elif self.portfolio['portfolio'] == self.program_setting["short_stock/etf"]:
            self.current_position = 'S'
            self.current_amount = int(self.portfolio['position'])
        else:
            self.current_position = 'C' # For Test
            self.current_amount = 0
        
        print("Current amount: " + str(self.current_amount) + " Currrent position: "+str(self.current_position))


    """May be removed in future versions"""
    def record_transaction_result(self):
        return 0
    
    """May be removed in future versions"""
    def log_runtime_date(self):
        print(self.account_setting)
        self.operation_record.to_csv('weekly report.csv')
        
    
    def save_log(self):
        self.program_setting['fed_opinion'] = self.fed_opinion[0]
        self.program_setting['fed_opinion_date'] = self.fed_opinion[1]
        self.program_setting['FED_Speech'] = self.fed_speech
        with open('setting.json', 'w') as fp:
            json.dump(self.program_setting, fp, indent=4)
    
    def load_log(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, 'setting.json')
        with open(file_path) as f_in:
            self.program_setting = json.load(f_in)
        self.fed_opinion = [self.program_setting['fed_opinion'], self.program_setting['fed_opinion_date']]
        self.fed_speech = self.program_setting['FED_Speech']
        
        
        if self.program_setting["Enable_timesfm"]:
            self.timesfm_forecast_model = timesfm_model(True)
        
        
    