"""
Terminal.py

By: Hengzhou Li
Email: hengzhouli0@gmail.com
---------------------------------------------------------------------------------------------------------------------------------------------------
- Basic structure for acquiring data and perform trading, 
- The program will ask price and put all data bundles in a list
- Trading will be based on the result returned by the function `decision`, it can return `E`(cash out), 'L'(long the market), 'S'(short the market)
- To use the trading program, call `python3 terminal.py` in the terminal or the powershell
- This part may be changed, but the basic structure should not be modified
- You must subscribe to IBKR streaming to make this work
- Do not distribute this program (including other files without the author's consensus)
---------------------------------------------------------------------------------------------------------------------------------------------------

"""
# Package requirement:
# Standard lib
import json
import typing # For typehinting 
import functools

# Packages for time/threads
#import time
#from datetime import timedelta
import datetime
from os import error
from typing_extensions import runtime
import pytz
from time import sleep
import threading
import pandas_market_calendars as mcal


# Customized Packages
from .order import *
from .logic import *
from .runtime_log import Runtime_log
from .data_capture.main import macro_data_capture
from .strategy_test import night_sky, sky_cloud



# IBKR API Associated
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.account_summary_tags import AccountSummaryTags




# Discord Bot API Associated
import discord
from discord.ext import commands
import sys
"""
Wrapper and Client for communication with TWS
"""
class IBapi(EWrapper, EClient):
    """
    Event evoking functions (Called automatically)
    """
    def __init__(self):
        EClient.__init__(self, self)

    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=''):
        if errorCode == 504:
            print("Received 504 error. Reconnecting...")
            # Perform cleanup or any necessary actions before reconnecting
            self.disconnect()
            # Sleep for a short duration before attempting to reconnect
            while True:
                sleep(20)
                try:
                    self.connect("127.0.0.1", 7496, 0)  # Reconnect
                    print("Connection back online")
                    break
                except:
                    print("Reconnection failed, retry in 20 sec")
                    pass
        else:
            # Handle other error codes or continue normal execution
            print(f"{errorCode} {errorString}")
            pass
    
    
    
    
    
    # Next valid ID
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        runtime_log.nextorderId = orderId + 1
        print('The next valid order id is: ', runtime_log.nextorderId)

    # Event: Acquire data
    def historicalData(self, reqId, bar):
        if runtime_log.time_interval == 10: # collect price for placing order
            print('The current ask price is: ', bar.close)
            print("Target amount of purchase: " + str(int((float(runtime_log.account_setting['NetLiquidation'])-200)/bar.close)))
            runtime_log.target_amount = int((float(runtime_log.account_setting['NetLiquidation'])-200)/(bar.close+0.018))
        else: # collect data for analysis
            runtime_log.runtime_flash[runtime_log.time_interval].append([bar.open, bar.close, bar.high, bar.low, bar.volume, bar.date]) # collect data for analysis

    # Event Acquire account info
    def accountSummary(self, reqId, account, tag, value, currency):
        runtime_log.account_setting[tag] = value
    
    # Update portfolio
    def position(self, account, contract, position, avgCost):
        if int(position) != 0:
            runtime_log.portfolio["portfolio"] = contract.symbol
            runtime_log.portfolio["position"] = position
            runtime_log.portfolio["avgCost"] = avgCost
            runtime_log.portfolio["contract"] = contract
            runtime_log.portfolio["account"] = account

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2:
            print('The current ask price is: ', price)
            print("Target amount of purchase: " + str(int((float(runtime_log.account_setting['NetLiquidation'])-200)/price)))
            #self.op_amount = int((float(self.account_summary['NetLiquidation'])-200)/price)
            runtime_log.target_amount = int((float(runtime_log.account_setting['NetLiquidation'])-200)/price)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
    
    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)  



"""
Thread/Associated function
"""

"""
Start the API
"""
def run_loop_api():
    program.run()
            
              

def run_bot():
    bot.run(runtime_log.program_setting['discord_bot_token'])


"""
Send requests for data
"""
def price_request():
    while True:
        # Set up requests
        current_time = datetime.datetime.now(est)
        opening_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        closing_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
        if current_time.weekday() < 5 and not nyse.valid_days(start_date=current_time.date(), end_date=current_time.date()).empty and opening_time <= current_time <= closing_time:
            try:
                #clear the flash memory
                for i in range(0, 3):
                    runtime_log.runtime_flash[i] = []
                #runtime_log.time_interval = 2
                #program.reqHistoricalData(1, baseline_contract, '', '15 Y', '1 week', 'TRADES', 1, 2, False, [])
                #sleep(2)
                #print("Success")
                with data_request_lock:
                    runtime_log.time_interval = 1
                    program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                    sleep(5)
                #print("Success")
                #runtime_log.time_interval = 2
                #program.reqHistoricalData(1, baseline_contract, '', '240 D', '2 hours', 'TRADES', 1, 2, False, [])
                #sleep(2)

                #runtime_log.time_interval = 1
                #program.reqHistoricalData(1, baseline_contract, '', '120 D', '1 hour', 'TRADES', 1, 2, False, [])
                #sleep(3)
                with data_request_lock:
                    runtime_log.time_interval = 0
                    program.reqHistoricalData(1, baseline_contract, '', '60 D', '30 mins', 'TRADES', 1, 2, False, [])
                    sleep(2)
                #print("Success")
                """
                Call the response function here (may want to use a multithreading call here)
                """
                response()
                #print("Success")
                print("----------------*************----------------")
            except Exception as e:
                print("Unable to interact with the TWS. May due to the internet fluctation\nEnter sleep mode to wait for the reconnection")
                sleep(13)
                print("----------------*************----------------")
                print(e)
            if current_time.hour == 15 and  50 <current_time.minute <= 58:
                sleep((59 - current_time.minute)*60 - current_time.second + 26)
            else:
                sleep(287)
        else:
            if  current_time.weekday() < 5 and not nyse.valid_days(start_date=current_time.date(), end_date=current_time.date()).empty and 8 < current_time.hour < 10:
                print("Not in a normal trade session, sleep for 10 minutes")
                print("----------------*************----------------")
                sleep(600)
            else:
                sleep(3600 - current_time.minute* 60 - current_time.second )


def macro_data_request():
    global runtime_log
    while True:
        current_time = datetime.datetime.now(est)
        first_release_begin = current_time.replace(hour=8, minute=33, second=0, microsecond=0)
        first_release_end = current_time.replace(hour=8, minute=36, second=0, microsecond=0)
        second_release_begin = current_time.replace(hour=10, minute=3, second=0, microsecond=0)
        second_release_end = current_time.replace(hour=10, minute=6, second=0, microsecond=0)
        #print(second_release_begin, second_release_end, current_time)
        if current_time.weekday() < 5 and first_release_begin <= current_time <= first_release_end:
            runtime_log.macro_data, place_holder = macro_data_capture('Data')
            print("Macroeconomic data updated at", current_time)
            sleep(600)
        elif current_time.weekday() < 5 and second_release_begin < current_time < second_release_end:
            runtime_log.macro_data, place_holder = macro_data_capture('Data')
            print("Macroeconomic data updated at", current_time)
            sleep(600)
        else:
            if current_time.hour < 7 or current_time.hour > 11:
                sleep(600)
            else:
                sleep(60)
            

"""
Make responses to the analysis result
"""
def response():
    global runtime_log, reponse_lock
    with reponse_lock:
        result = decision(runtime_log)       # Call Analysis function
        # Opperation based on result
        #print("result: "+ str(result))
        #runtime_log.current_position = "C"
        #result = 'S'
        if result == 'L':
            if runtime_log.current_position == 'L':
                sleep(7)
            else:
                if runtime_log.current_position == 'C':
                    """Hold cash"""
                    # Acquire the account information\
                    program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                    sleep(2)
                    with data_request_lock:
                        runtime_log.time_interval = 10
                        program.reqHistoricalData(1, long_contract, '', '1 D', '1 day', 'BID', 1, 2, False, [])
                        sleep(1)
                    # Buy
                    order_long = build_order('L', runtime_log.target_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, long_contract, order_long)
                    runtime_log.current_amount = runtime_log.target_amount
                    sleep(4)
                
                else:   
                    """Hold short position"""
                    # Sell
                    order_short = build_order('S', runtime_log.current_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, short_contract, order_short)
                    sleep(2)

                    runtime_log.profit = float(runtime_log.account_setting['NetLiquidation'])

                    program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                    sleep(2)
    
                    runtime_log.profit = float(runtime_log.account_setting['NetLiquidation']) - runtime_log.profit
                    runtime_log.total_profit += runtime_log.profit
                    print("Profit in this round of holding: " + str(runtime_log.profit)+"\nTotal profit: ", runtime_log.total_profit)

                    with data_request_lock:
                        runtime_log.time_interval = 10
                        program.reqHistoricalData(1, long_contract, '', '1 D', '1 day', 'BID', 1, 2, False, [])
                        sleep(1)

                    # Buy
                    order_long = build_order('L', runtime_log.target_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, long_contract, order_long)
                    runtime_log.current_amount = runtime_log.target_amount

                    sleep(2)
        elif result == 'S':
            if runtime_log.current_position == 'S':
                sleep(7)
            else:
                if runtime_log.current_position == 'C':
                    """Hold cash"""
                    # Acquire account information
                    program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                    sleep(2)
                    with data_request_lock:
                        runtime_log.time_interval = 10
                        program.reqHistoricalData(1, short_contract, '', '1 D', '1 day', 'BID', 1, 2, False, [])
                        sleep(1)
                    
                    order_short = build_order('L', runtime_log.target_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, short_contract, order_short)
                    runtime_log.current_amount = runtime_log.target_amount
                    sleep(4)
                else:
                    """Hold long positon"""
                    # Reverse
                    order_short = build_order('S', runtime_log.current_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, long_contract, order_short)
                    sleep(2)

                    runtime_log.profit = float(runtime_log.account_setting['NetLiquidation'])

                    program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                    sleep(2)

                    runtime_log.profit = float(runtime_log.account_setting['NetLiquidation']) - runtime_log.profit
                    runtime_log.total_profit += runtime_log.profit
                    print("Profit in this round of holding: " + str(runtime_log.profit)+"\nTotal profit: ", runtime_log.total_profit)

                    with data_request_lock:
                        runtime_log.time_interval = 10
                        program.reqHistoricalData(1, short_contract, '', '1 D', '1 day', 'BID', 1, 2, False, [])

                        sleep(1)
                    # Sell
                    order_short = build_order('L', runtime_log.target_amount)
                    runtime_log.nextorderId += 1
                    program.placeOrder(runtime_log.nextorderId, short_contract, order_short)
                    runtime_log.current_amount = runtime_log.target_amount
                    sleep(2)
        elif result == 'E': # exit all positions
            result = 'C'
            if runtime_log.current_position == 'L':
                order_short = build_order('S', runtime_log.current_amount)
                runtime_log.nextorderId += 1
                program.placeOrder(runtime_log.nextorderId, long_contract, order_short)

                runtime_log.profit = float(runtime_log.account_setting['NetLiquidation'])
                program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                sleep(2)
                runtime_log.profit = float(runtime_log.account_setting['NetLiquidation']) - runtime_log.profit
                runtime_log.total_profit += runtime_log.profit
                print("Profit in this round of holding: " + str(runtime_log.profit)+"\nTotal profit: ", runtime_log.total_profit)

                runtime_log.current_amount = 0
            elif runtime_log.current_position == 'S':
                order_short = build_order('S', runtime_log.current_amount)
                runtime_log.nextorderId += 1
                program.placeOrder(runtime_log.nextorderId, short_contract, order_short)

                runtime_log.profit = float(runtime_log.account_setting['NetLiquidation'])
                program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                sleep(2)
                runtime_log.profit = float(runtime_log.account_setting['NetLiquidation']) - runtime_log.profit
                runtime_log.total_profit += runtime_log.profit
                print("Profit in this round of holding: " + str(runtime_log.profit)+"\nTotal profit: ", runtime_log.total_profit)
            runtime_log.current_amount = 0
            sleep(5)
        else:
            sleep(7)
        runtime_log.current_position = result
    #print("response finished")




"""
Global variable
"""
# API & Contract set up
global runtime_log, data_request_lock, reponse_lock, baseline_contract, long_contract, short_contract




reponse_lock = threading.Lock()
data_request_lock =  threading.Lock()




program = IBapi()
runtime_log = Runtime_log()
runtime_log.load_log()
baseline_contract = build_contract([runtime_log.program_setting["baseline_stock/etf"], 'STK', 'SMART', 'USD'])
long_contract = build_contract([runtime_log.program_setting['long_stock/etf'], 'STK', 'SMART', 'USD'])
short_contract = build_contract([runtime_log.program_setting['short_stock/etf'], 'STK', 'SMART', 'USD'])
# Historical Analysis data



historical_data = {}
FINANCIALJUICE_CHANNEL_ID = 1240949550794014792
FED_SPEECH_CHANNEL_ID = 1242348959029268520

# Date & time set up
est = pytz.timezone('US/Eastern')
nyse = mcal.get_calendar('XNYS')

# Discord Bot Set up
intents = discord.Intents.default()
intents.messages = True  # To receive message events
intents.message_content = True  # To read message content
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def sky_cloud_analysis(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)

@bot.event         # Update the program setting based on discord instruction
async def on_message(message):
    global runtime_log
    if message.author == bot.user:
        return
    if message.channel.id == FINANCIALJUICE_CHANNEL_ID:
        target_channel = bot.get_channel(FED_SPEECH_CHANNEL_ID)
        if target_channel:
            if "FED'S" in message.content:
                await target_channel.send(message.content.capitalize())
        
    print(message.channel)
    if bot.user in message.mentions:
        if str(message.author.id) in runtime_log.program_setting['accepted_users'] or str(message.author.id) in runtime_log.program_setting['accepted_guest']:
            #print(message.content)
            instruction = message.content
            instruction = instruction.strip(' ')
            raw_message_segment = instruction.split(' ')
            message_segment = []
            for i in raw_message_segment:
                if '<@' not in i:
                    message_segment.append(i)
            if len(message_segment) == 0:
                return
            # FOMC Decision Appending
            #print(message_segment)
            if (message_segment[0] == 'FOMC_Decision' or message_segment[0] == 'FD') and len(message_segment) > 1 and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                if len(message_segment) == 2:
                    date = datetime.datetime.now(est).strftime("%B %d %Y")
                    decision = message_segment[1]
                    runtime_log.fed_opinion = [decision, date]
                    runtime_log.program_setting['historical_fed_opinion'].append([decision, date])
                    if len(runtime_log.program_setting['historical_fed_opinion']) > 100:
                        new_list = []
                        for i in range(1, len(runtime_log.program_setting['historical_fed_opinion'])):
                            new_list.append(runtime_log.program_setting['historical_fed_opinion'][i])
                        runtime_log.program_setting['historical_fed_opinion'] = new_list
                    runtime_log.save_log()
                    #print("####################################################################################", runtime_log.fed_opinion)
                    await message.channel.send('FOMC DECISION UPDATED: '+runtime_log.fed_opinion[0]+" "+runtime_log.fed_opinion[1])
                else:
                    decision = message_segment[1]
                    runtime_log.fed_opinion = [decision, message_segment[2]+" "+message_segment[3]+" "+message_segment[4]]
                    runtime_log.program_setting['historical_fed_opinion'].append(runtime_log.fed_opinion)
                    if len(runtime_log.program_setting['historical_fed_opinion']) > 50:
                        new_list = []
                        for i in range(1, len(runtime_log.program_setting['historical_fed_opinion'])):
                            new_list.append(runtime_log.program_setting['historical_fed_opinion'][i])
                        runtime_log.program_setting['historical_fed_opinion'] = new_list
                    runtime_log.save_log()
                    await message.channel.send('FOMC DECISION UPDATED: '+decision+" "+message_segment[2]+" "+message_segment[3]+" "+message_segment[4])
            elif message_segment[0] == 'Current_Decision' or message_segment[0] == 'CD':
                await message.channel.send(f'1. Current Decision: {runtime_log.current_position}\n2. Current FOMC Decision: {runtime_log.fed_opinion[0]}')
            elif message_segment[0] == 'Save' and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                runtime_log.save_log()
                await message.channel.send('Log saved!')
            elif message_segment[0] == 'Abort' and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                runtime_log.status = 'Aborted'
                response()
                runtime_log.save_log()
                await message.channel.send('Abort the program')
                print("Abort the program")
                sys.exit()
                
            elif message_segment[0] == "Forecast":
                with data_request_lock:
                    runtime_log.time_interval = 1
                    program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                    sleep(2)
                data =  runtime_log.runtime_flash[1]['Close'].tolist()
                current_time = datetime.datetime.now(est)
                if current_time.hour < 16:
                    data = data[:len(data)-1]
                result = runtime_log.timesfm_forecast_model.make_a_forecast("day", data)
                drawing_data = data[len(data)-45:]
                with_forecast = drawing_data[:]
                for i in result:
                    with_forecast.append(i)
                import matplotlib
                matplotlib.use('agg')
                import matplotlib.pyplot as plt
                
                x1 = range(1, len(drawing_data) + 1)
                x2 = range(1, len(with_forecast) + 1)
                plt.figure(figsize=(10, 6))
                plt.plot(x2, with_forecast, label='y1', marker='o', color='blue', linestyle='-', linewidth=2)  # 蓝色实线
                plt.plot(x1, drawing_data, label='y2', marker='x', color='red', linestyle='--', linewidth=2)   # 红色虚线

                # 添加标题和标签
                plt.title('Graph of Forecast')

                # 添加图例
                plt.legend()

                # 添加网格
                plt.grid(True)
                
                plt.savefig('temp/forecast.png')
                # 关闭图表并释放资源
                plt.close()
                await message.channel.send(f"forecast: {result}", file = discord.File("temp/forecast.png"))
                
                  
        
            elif message_segment[0] == "Account" and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
                sleep(2)
                if runtime_log.current_position == "L":
                    await message.channel.send(f'Current Holding: {runtime_log.program_setting["long_stock/etf"]}\n1. Total Equity Value: {runtime_log.account_setting["EquityWithLoanValue"]}\n2. Total Cash Value: {runtime_log.account_setting["TotalCashValue"]}\n3. Total Liquidity: {runtime_log.account_setting["NetLiquidation"]}')
                elif runtime_log.current_position == "S":
                    await message.channel.send(f'Current Holding: {runtime_log.program_setting["short_stock/etf"]}\n1. Total Equity Value: {runtime_log.account_setting["EquityWithLoanValue"]}\n2. Total Cash Value: {runtime_log.account_setting["TotalCashValue"]}\n3. Total Liquidity: {runtime_log.account_setting["NetLiquidation"]}')
                else:
                    await message.channel.send(f'Current Holding: Cash\n1. Total Equity Value: {runtime_log.account_setting["EquityWithLoanValue"]}\n2. Total Cash Value: {runtime_log.account_setting["TotalCashValue"]}\n3. Total Liquidity: {runtime_log.account_setting["NetLiquidation"]}')
            elif (message_segment[0] == "Get_Parameter" or message_segment[0] == "GP") and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                economic_indicator = " ".join(runtime_log.program_setting["macro_indicators"])
                macro_indicators_negative_list = " ".join(runtime_log.program_setting["macro_indicators_negative_list"])
                await message.channel.send(f"Economic Parameters: {economic_indicator}")
                await message.channel.send(f"Negative List: {macro_indicators_negative_list}")
            elif (message_segment[0] == 'Modify' or message_segment[0] == 'M') and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                True
                
            elif message_segment[0] == 'Get-test-result':
                await message.channel.send(f"Test Time: {runtime_log.program_setting['strategy_test_date']}")
                await message.channel.send("Sort based on profit:\n######################################################################")
                counter = 1
                for i in runtime_log.program_setting["strategy_test_result"][0]:
                    key_indicators = "Key Indicators: "+" ".join(i[0][0])
                    negative_list = "Negative_list: "+" ".join(i[0][1])
                    profit =  "Profit: " + str(i[1])
                    max_loss = "Max Loss: " + str(i[2])
                    await message.channel.send(f"{counter}. ********************************\n{key_indicators}\n{negative_list}\n{profit}\n{max_loss}", file = discord.File(i[3]))
                    counter += 1
                await message.channel.send("Sort based on max loss:\n#####################################################################")
                for i in runtime_log.program_setting["strategy_test_result"][1]:
                    key_indicators = "Key Indicators: "+" ".join(i[0][0])
                    negative_list = "Negative List: "+" ".join(i[0][1])
                    profit =  "Profit: " + str(i[1])
                    max_loss = "Max Loss: " + str(i[2])
                    await message.channel.send(f"{counter}. ********************************\n{key_indicators}\n{negative_list}\n{profit}\n{max_loss}", file = discord.File(i[3]))
                    counter += 1
    
            
            elif message_segment[0] == 'Run-test' and str(message.author.id) in runtime_log.program_setting['accepted_users']:
                if len(message_segment) > 1:
                    if message_segment[1] == "Full-scale":
                        
                        current_time =datetime.datetime.now(est)
                        opening_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
                        closing_time = current_time.replace(hour=16, minute=15, second=0, microsecond=0)
                        if len(runtime_log.runtime_flash) == 0:
                            with data_request_lock:
                                runtime_log.time_interval = 1
                                program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                                sleep(2)
                        if len(runtime_log.runtime_flash[1]) == 0:
                            with data_request_lock:
                                runtime_log.time_interval = 1
                                program.reqHistoricalData(1, baseline_contract, '', '6 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                                sleep(2)
                        if current_time > closing_time or current_time < opening_time or current_time.weekday() > 4:
                            #print(len(message_segment))
                            
                            fed_opinion = []
                            if '-f' in message_segment:
                                fed_opinion = runtime_log.program_setting['historical_fed_opinion']
                            #print(message_segment)
                            if len(message_segment) == 3:
                                runtime_log.program_setting["strategy_test_result"] = await sky_cloud_analysis(sky_cloud, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 25, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]}, fed_opinion, None, int(message_segment[2]))
                            elif len(message_segment) == 4:
                                if '-f' in message_segment:
                                     runtime_log.program_setting["strategy_test_result"] = await sky_cloud_analysis(sky_cloud, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 25, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]}, fed_opinion, None, int(message_segment[2]))
                                else:
                                    runtime_log.program_setting["strategy_test_result"] = await sky_cloud_analysis(sky_cloud, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 25, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]}, fed_opinion, [message_segment[2], message_segment[3]], None)
                            elif len(message_segment) == 5:
                                #print(message_segment)
                                runtime_log.program_setting["strategy_test_result"] = await sky_cloud_analysis(sky_cloud, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 25, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]}, fed_opinion, [message_segment[2], message_segment[3]], None)
                            else:
                                runtime_log.program_setting["strategy_test_result"] = await sky_cloud_analysis(sky_cloud, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 25, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]}, fed_opinion)
                            #result = sky_cloud(pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), runtime_log.program_setting["strategy_test_duration"], 6, runtime_log.macro_data, {"Inflation": runtime_log.program_setting["inflation_related_indicators"], "Growth": runtime_log.program_setting["growth_related_indicators"]})
                            runtime_log.program_setting["strategy_test_date"] = current_time.strftime("%Y-%m-%d %H:%M:%S")

                            runtime_log.save_log()
                            counter = 1
                            await message.channel.send(f"Test Time: {runtime_log.program_setting['strategy_test_date']}")
                            await message.channel.send("Sort based on profit:\n######################################################################")
                            for i in runtime_log.program_setting["strategy_test_result"][0]:
                                key_indicators = "Key Indicators: "+" ".join(i[0][0])
                                negative_list = "Negative List: "+" ".join(i[0][1])
                                profit =  "Profit: " + str(i[1])
                                max_loss = "Max Loss: " + str(i[2])
                                await message.channel.send(f"{counter}. ********************************\n{key_indicators}\n{negative_list}\n{profit}\n{max_loss}", file = discord.File(i[3]))
                                counter += 1
                            await message.channel.send("Sort based on max loss:\n#####################################################################")
                            #for i in runtime_log.program_setting["strategy_test_result"][1]:
                            #    print(i)
                            for i in runtime_log.program_setting["strategy_test_result"][1]:
                                key_indicators = "Key Indicators: "+" ".join(i[0][0])
                                negative_list = "Negative List: "+" ".join(i[0][1])
                                profit =  "Profit: " + str(i[1])
                                max_loss = "Max Loss: " + str(i[2])
                                await message.channel.send(f"{counter}. ********************************\n{key_indicators}\n{negative_list}\n{profit}\n{max_loss}", file = discord.File(i[3]))
                                counter += 1
                        else:
                            await message.channel.send("Test Run denied. Running the test at this time may serverly impact the operation of the bot during market open time.")
                    elif message_segment[1] == "Custom-strategy-test":
                        try:
                            begin_date = datetime.datetime.strptime(message_segment[2], r'%B-%d-%Y')
                            end_date = datetime.datetime.strptime(message_segment[3], r'%B-%d-%Y')
                            with data_request_lock:
                                runtime_log.time_interval = 1
                                program.reqHistoricalData(1, baseline_contract, '', '10 Y', '1 day', 'ADJUSTED_LAST', 1, 2, False, [])
                                sleep(2)
                            await message.channel.send("Customized Strategy Test:\n#####################################################################")
                            
                            fed_decision_list = []
                            if '-f' in message_segment:
                                fed_decision_list = runtime_log.program_setting['historical_fed_opinion']
                                
                                
                                
                                
                                
                            result =  night_sky(begin_date, end_date, fed_decision_list, False, runtime_log.macro_data, pd.DataFrame(runtime_log.runtime_flash[1], columns=['Open', 'Close', 'High', 'Low', 'Volume', 'Time']), [runtime_log.program_setting["Custom-model-economic-indicator"], runtime_log.program_setting["Custom-model-negative-list"]])                            
                            
                            
                            
                            
                            
                            
                            #print(result)
                            key_indicators = "Key Indicators: "+" ".join(result[0][0])
                            negative_list = "Negative List: "+" ".join(result[0][1])
                            profit =  "Profit: " + str(result[1])
                            max_loss = "Max Loss: " + str(result[2])
                            await message.channel.send(f"{key_indicators}\n{negative_list}\n{profit}\n{max_loss}", file = discord.File(result[3]))

                        except error:
                            await message.channel.send("Date not accepted, try to re-enter")
                            print(error)
                    elif message_segment[1] == "bcm":
                        if message_segment[2] == "-e":
                            runtime_log.program_setting["Custom-model-economic-indicator"] = []
                            for i in range(3, len(message_segment)):
                                indicator_segment =  message_segment[i].split("-")
                                runtime_log.program_setting["Custom-model-economic-indicator"].append(" ".join(indicator_segment))
                            await message.channel.send(f"Success! {runtime_log.program_setting['Custom-model-economic-indicator']}")
                            #runtime_log.save_log()
                        elif message_segment[2] == "-n":
                            runtime_log.program_setting["Custom-model-negative-list"] = []
                            for i in range(3, len(message_segment)):
                                indicator_segment =  message_segment[i].split("-")
                                runtime_log.program_setting["Custom-model-negative-list"].append(" ".join(indicator_segment))
                            await message.channel.send(f"Success! {runtime_log.program_setting['Custom-model-negative-list']}")
                            #runtime_log.save_log()
                        
                else:
                    await message.channel.send("Please follow this format:\n1. Run-test Full-scale (<Begin Date> <End Date> / time duration): Run the Full scale analysis\n2. Run-test Custom-strategy-test <Begin Date> <End Date> -f (Date Format: Month-dd-yyyy, e.g. January-01-2000, -f means with fed opinion)\n3. Run-test bcm -e economic indicator list, e.g. PPI-Mom Core-Inflation-Rate-Mom\n4. Run-test bcm -n negative indicator list, e.g PPI-Mom Core-Inflation-Rate-Mom")
            
            # Get Powell Speech
            elif len(message_segment) == 2:
                if message_segment[0] + " " + message_segment[-1] == 'Powell Speech':
                    #print(json.dumps(runtime_log.fed_speech, indent=4))
                    for i in runtime_log.fed_speech.keys():
                        await message.channel.send("########################################################################")
                        await message.channel.send(i)
                        for k in len(runtime_log.fed_speech[i]):
                            await message.channel.send(str(k+1)+". "+runtime_log.fed_speech[i][k]+"\n")
                        await message.channel.send("########################################################################")
                elif message_segment[0] + " " + message_segment[-1] == 'Force Long':
                    runtime_log.status = 'Force Long'
                    response()
                    await message.channel.send("Long position established")
                elif message_segment[0] + " " + message_segment[-1] == 'Force Short':
                    runtime_log.status = 'Force Short'
                    response()
                    await message.channel.send("Short position established")
                elif message_segment[0] + " " + message_segment[-1] == 'Force Cash':
                    runtime_log.status = 'Force Cash'
                    response()
                    await message.channel.send("Cash position established")
                elif message_segment[0] + " " + message_segment[-1] == 'Exit Force':
                    runtime_log.status = 'Activated'
                    response()
                    await message.channel.send("Hand control back to the terminal")
                elif message_segment[0] == "Assert":
                    date = datetime.datetime.now(est).strftime("%B %d %Y")
                    decision = message_segment[1]
                    runtime_log.fed_opinion = [decision, date]
                    #response()
            else:
                await message.channel.send(f'Unable to recognize your command. Please follow this format or ask for additional authorization:\n1. FOMC_Decision <Decision> <Optional: Date> (Short cut FD <Decision>)\n2. Current_Decision (Shortcut CD)\n3. Save: Save all the log\n4. Powell Speech: Get key element in Powell\'s recent speech.\n5. Abort: Abort the program instantly\n6. Account: Send the account summary\n7. Force Long: Remove all machine execution and mandatorily enter long position\n8. Force Short: Remove all machine execution and mandatorily enter short position\n9. Force Cash: Remove all machine execution and mandatorily clear all the positions\n10. Exit Force: Exit the mandatory instruction and hand control back to the machine')
                await message.channel.send(f'11. Run-test: Run the strategy test (Since the test would require heavy computations, the bot will be deactivated during the test run)\n12. Get-test-result: return the latest test result\n13. Get_Parameter: get current model parameters\n14. Assert L/S: Make a force long or short without halting the model')
        else:
            await message.channel.send('Sorry, you do not have the rights to look up / make decisions')
    await bot.process_commands(message)


"""
Main function
"""
def main():
    runtime_log.macro_data, runtime_log.fed_speech = macro_data_capture('Data')
    #print(runtime_log.fed_speech)
    program.connect("127.0.0.1", 7496, 0)   # 7496 for testiing 7496 for actual operation
    
    # Start api socket
    api_thread = threading.Thread(target=run_loop_api, daemon=True)
    api_thread.start()
    sleep(3)
    print("Successfully set up the connection ")
    
    # Start Discord socket
    api_thread = threading.Thread(target=run_bot, daemon=True)
    api_thread.start()
    sleep(3)
    print("Successfully set up the bot")
    # Start the macro_data fed:
    macro_thread = threading.Thread(target=macro_data_request, daemon=True)
    macro_thread.start()

    # Acquire Account information to initialize the runtime_log
    runtime_log.account_setting['profit'] = 0
    runtime_log.account_setting['number of transactions'] = 0
    program.reqAccountSummary(1, "All", AccountSummaryTags.AllTags)
    print("portfolio request sent")
    runtime_log.portfolio['portfolio'] = "empty"   # Need to initialize the portfolio first to avoid the use of try except
    program.reqPositions()
    sleep(5)
    runtime_log.instant_update()
    print("Initialization: ", runtime_log.current_position)

    # Acquire QQQ price for baseline analysis
    print("----------------*************----------------")
    price_request()




