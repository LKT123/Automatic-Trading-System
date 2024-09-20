from .web_scraping import web_scraping_browser
from .data_cleaning import *

from .data_hub import data_update

def macro_data_capture(req_type):
    if req_type == 'Both':
        text, speech =  web_scraping_browser(True, True)
        data_d = trading_economics_clean_data(text)
        speech = financialjuice_clean_speeh(speech)
        return data_d, speech
    elif req_type == 'Data':
        text, speech =  web_scraping_browser(True, False)
        data_d = trading_economics_clean_data(text)
        return data_d, None
    else:
        text, speech =  web_scraping_browser(False, True)
        speech = financialjuice_clean_speeh(speech)
        return None, speech
