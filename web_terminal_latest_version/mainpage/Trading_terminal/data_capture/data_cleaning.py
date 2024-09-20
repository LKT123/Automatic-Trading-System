#data cleaning
import pandas as pd
import re
import datetime
import pytz

#from .web_scraping import web_scraping_browser

# Global variable
month_to_decimal =  {
    "JAN": 1, "January": 1,
    "FEB": 2, "February": 2,
    "MAR": 3, "March": 3,
    "APR": 4, "April": 4,
    "MAY": 5, "May": 5,
    "JUN": 6, "June": 6,
    "JUL": 7, "July": 7,
    "AUG": 8, "August": 8,
    "SEP": 9, "September": 9,
    "OCT": 10, "October": 10,
    "NOV": 11, "November": 11,
    "DEC": 12, "December": 12
}
    

def trading_economics_clean_data(text: str):
    # Split text into lines
    lines = text.split('\n')
    
    # Define a regular expression to match lines to remove
    removal_pattern = re.compile(r"\bUS\b|\d{2}:\d{2}\s(?:AM|PM)")
    date_patern =  re.compile(r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{2}\s\d{4}\sActual\sPrevious\sConsensus\sForecast\b")
    # List to hold cleaned lines
    cleaned_lines = []

    # Process each line
    for line in lines:
        # Check if the line matches the removal pattern
        if not removal_pattern.search(line):
            # Remove the ® symbol and replace it with a space
            cleaned_line = line.replace(' ® ', ' ')
            cleaned_lines.append(cleaned_line.strip())
    
    # Return the cleaned data as a list or as a single string
    result = {}
    current_month = ""
    current_year =  ""
    current_day =  ""
    for line in cleaned_lines:
        #print(line)
        if date_patern.search(line):
            date_fragment = line.split(" ")
            current_month = date_fragment[1]
            current_day = date_fragment[2]
            current_year = date_fragment[3]
        else:
            data_fragment = line.split(" ")
            counter = -1
            for i in range(0, len(data_fragment)):
                if data_fragment[i] in month_to_decimal:
                    counter = i
                    break
            if counter != -1 and len(data_fragment[counter + 1:])>2:
                category = " ".join(data_fragment[:counter])
                data = data_fragment[counter + 1:]
                if len(data) == 3:
                    data = [None] + data
                data.append(" ".join(date_fragment[1:4]))
                
                if (category == "Balance of Trade" or category == "Monthly Budget Statement") and len(data) > 4:
                    new_data = []
                    index = 0
                    while index < len(data):
                        if data[index] == "$":
                            combine = data[index] + data[index+1]
                            new_data.append(combine)
                            index += 2
                        else:
                            new_data.append(data[index])
                            index += 1
                    data = new_data
                
                act_month = data_fragment[counter]
                
                c_month = month_to_decimal[current_month]
                a_month = month_to_decimal[act_month]
                
                if a_month > c_month:
                    date = str(int(current_year)-1) +"/"+str(a_month)
                else:
                    date = current_year + "/" + str(a_month)
                try:
                    result[category][date] = data
                    
                except:
                    result[category] = {date : data}
    
    data_frames = {}  # Initialize an empty dictionary
    for key, value in result.items():
        #print(key)
        #print(value)
        data_frames[key] = pd.DataFrame.from_dict(value, orient='index', columns=['Current', 'Previous', 'Consensus', 'TE_Forecast', 'Release_Date'])
            
    for key in data_frames:
        data_frames[key] = data_frames[key].reset_index().rename(columns={'index': 'Date'})
    return data_frames


def financialjuice_clean_speeh(threads: list):
    current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
    result = {}
    for i in threads:
        segments = i.split('\n')
        
        date = segments[3]
        date_seg = date.split(" ")
        date_key = ""
        if len(date_seg) == 2:
            month, day = date_seg[0], date_seg[1]
            year = -1
            if month_to_decimal[month] > current_time.month or (month_to_decimal[month] == current_time.month and int(day) > current_time.day):
                year = current_time.year - 1
            else:
                year = current_time.year
                date_key = date +" " + str(year)
        else:
            date_key = current_time.strftime("%B %d %Y")

        is_a_voting_committee_member = False
        for i in ['POWELL', 'MESTER']:
            if i in segments[4]:
                is_a_voting_committee_member = True
                
        if date_key not in result.keys() and is_a_voting_committee_member:
            result[date_key] = []

        if is_a_voting_committee_member:
            sentence = segments[4].strip(" ")
            result[date_key].append(sentence.capitalize())
    return result
    


#a, b = web_scraping_browser(False, True)
#print(financialjuice_clean_speeh(b))
    
    
    

