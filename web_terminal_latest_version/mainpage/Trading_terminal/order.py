"""
Order placement
- Have two functions based on the setting
- Contain the connection settup for terminal

The terminal should import this file to use the classes here for the connection.
"""

from ibapi.contract import Contract
from ibapi.order import Order


"""
setting_list: code, STK, exchange(SMART), currency
"""
def build_contract(setting_list):
    contract = Contract()
    contract.symbol = setting_list[0]
    contract.secType = setting_list[1]
    contract.exchange = setting_list[2]
    contract.currency = setting_list[3]
    return contract

def build_order(action, amount):
    order = Order()
    if action == 'L':
        order.action = "BUY"
        order.orderType = "MKT"
        order.totalQuantity = amount # need calculation to acquire the correct amount
    elif action == 'S':
        order.action = "SELL"
        order.orderType = "MKT"
        order.totalQuantity = amount # need calculation to acquire the correct amount
    else:
        print("Invalid action")
        return None
    return order

