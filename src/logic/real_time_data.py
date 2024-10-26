import datetime
import requests
from bs4 import BeautifulSoup
import numpy as np


def get_real_time_signal(stock_code):
    url = "https://www.google.com/finance/quote/" + stock_code  
    r = requests.get(url)
    web_content = BeautifulSoup(r.text, 'lxml')
    web_content = web_content.find('div', {"class": 'AHmHk'})
    web_content = web_content.find('span').text 
    if web_content == []:
        return "99999"  
    return web_content

def update_real_time_data():
    time_stamp = datetime.datetime.now()
    time_in_seconds = time_stamp.timestamp()

    try:
        price = float(get_real_time_signal("VIX:INDEXCBOE?hl=en"))
    except ValueError:
        print("Error converting price to float")
        price = np.nan  

    return time_in_seconds, price

# while True:
#     print(update_real_time_data())



# finance.yahoo.com IP Address is 	69.147.92.12
# finance.google.com IP Address is 	142.251.41.3