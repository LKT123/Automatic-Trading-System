import json

"""Build the json file for the setting"""

settings = {}
# Operation related
settings['baseline_stock/etf'] = 'QQQ'
settings['long_stock/etf'] = 'TQQQ'
settings['short_stock/etf'] = 'SQQQ'
settings['Avoid overnight holdings'] = 'False'

with open('setting.json', 'w') as fp:
    json.dump(settings, fp)