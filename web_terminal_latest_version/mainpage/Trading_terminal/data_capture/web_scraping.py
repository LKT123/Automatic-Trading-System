from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from time import sleep
import pytz

def web_scraping_browser(trading_economics_macrodata: bool, financialjuice_fed_speech: bool):
    # Setup Chrome WebDriver    # Setup Chrome WebDriver
    #service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome()
    trading_economics_rawdata = ""
    financialjuice_raw_fed_speech = []
    try:
        if trading_economics_macrodata:
            # URL of the page to scrape
            url = 'https://www.tradingeconomics.com/calendar'
            # Open the URL
            driver.get(url)
            sleep(3)
            # Wait for a specific element that indicates the page has loaded
            button_importance = driver.find_element(By.CSS_SELECTOR, '#ctl00_ContentPlaceHolder1_ctl02_Button1')
            button_importance.click()
            sleep(0.36)
            button_importance = driver.find_element(By.CSS_SELECTOR, '#aspnetForm > div.container > div > div > table > tbody > tr > td:nth-child(1) > div > div:nth-child(2) > ul > li:nth-child(3)')
            button_importance.click()
            sleep(1)
            #print("Importance reselected")
        
            button_country = driver.find_element(By.CSS_SELECTOR, '#aspnetForm > div.container > div > div > table > tbody > tr > td:nth-child(1) > div > button')
            button_country.click()
            sleep(0.36)
            button_country = driver.find_element(By.CSS_SELECTOR, '#te-c-main-countries > div > div:nth-child(2) > div:nth-child(1) > a')
            button_country.click()
            sleep(0.36)
            driver.execute_script("window.scrollTo(0, 200);")
            sleep(0.36)
            button_country = driver.find_element(By.CSS_SELECTOR, '#te-c-all > ul.list-unstyled.col-md-3.col-6.order-last > li.te-c-option.te-c-option-usa')
            button_country.click()
            sleep(0.36)
            driver.execute_script("window.scrollTo(200, 0);")
            sleep(0.36)
            button_country = driver.find_element(By.CSS_SELECTOR, '#te-c-main-countries > div > div:nth-child(2) > div:nth-child(3)')
            button_country.click()
            sleep(1)

            #print("Country reselected")

            button_date = driver.find_element(By.CSS_SELECTOR, '#aspnetForm > div.container > div > div > table > tbody > tr > td:nth-child(1) > div > div:nth-child(1) > button')
            button_date.click()
            sleep(0.36)
            button_date = driver.find_element(By.CSS_SELECTOR, '#aspnetForm > div.container > div > div > table > tbody > tr > td:nth-child(1) > div > div:nth-child(1) > ul > li:nth-child(13)')
            button_date.click()
            sleep(0.36)

            current_date = datetime.now(pytz.timezone('US/Eastern')).date()
            tomorrow_date = current_date + timedelta(days=6)
            formatted_tomorrow_date = tomorrow_date.strftime("%Y-%m-%d")
            date_10_months_ago = current_date - relativedelta(months=20)
            date_10_months_ago_first = date_10_months_ago.replace(day=1)
            formatted_date_10_months_ago = date_10_months_ago_first.strftime("%Y-%m-%d")

            input_past = driver.find_element(By.CSS_SELECTOR, '#startDate')
            input_future = driver.find_element(By.CSS_SELECTOR, '#endDate')
            input_past.clear()
            input_future.clear()
            input_past.send_keys(formatted_date_10_months_ago)
            input_future.send_keys(formatted_tomorrow_date)
            sleep(0.36)

            button_date_submit = driver.find_element(By.CSS_SELECTOR, '#datesDiv > div > span.input-group-btn > button')
            button_date_submit.click()

            #print("date reselected")
            sleep(1)

            data_element = driver.find_element(By.CSS_SELECTOR, '#aspnetForm > div.container > div > div > div.table-responsive')  # Update with the correct CSS selector
            trading_economics_rawdata = data_element.text
        
        if financialjuice_fed_speech:
            url = r'https://x.com/search?q=FED%27s+from%3Afinancialjuice&src=typed_query&f=live'
            driver.get(url)
            sleep(3.6)
            input_account_email = driver.find_element(By.NAME, "text")
            input_account_email.clear()
            input_account_email.send_keys('siranonymous580@gmail.com')
            sleep(0.36)
            next_button = driver.find_element(By.CSS_SELECTOR, '[role=button].r-13qz1uu')
            next_button.click()
            sleep(5)
            try:
                input_account_name = driver.find_element(By.NAME, "text")
                input_account_name.clear()
                input_account_name.send_keys('@Giant_cookiebot\n')
                sleep(5)
            except NoSuchElementException:
                pass
            finally:
                input_account_name = driver.find_element(By.NAME, "password")
                input_account_name.clear()
                input_account_name.send_keys(':-Semc2xE6L2wGA\n')
                sleep(2)
                
                last_height = driver.execute_script("return document.body.scrollHeight")
                
                scroll_max = 10
                counter = 0
                while True and counter < scroll_max:
                    # Scroll down to bottom
                    articles = driver.find_elements(By.TAG_NAME, 'article')
                    for article in articles:
                        financialjuice_raw_fed_speech.append(article.text)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Wait to load page
                    sleep(2)

                    # Calculate new scroll height and compare with last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    counter += 1
                financialjuice_raw_fed_speech = list(set(financialjuice_raw_fed_speech))
            
    finally:
        # Close the driver
        driver.quit()

    return trading_economics_rawdata, financialjuice_raw_fed_speech
