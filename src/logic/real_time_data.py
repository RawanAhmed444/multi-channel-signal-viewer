import datetime
import requests
from bs4 import BeautifulSoup
import numpy as np


def get_real_time_signal(stock_code):
    """Fetches real-time stock price from Google Finance (may be unreliable).

    Args:
        stock_code (str): The stock code (e.g., "AAPL-USD").

    Returns:
        str: The extracted price as a string, or "99999" if an error occurs.
    """

    url = "https://www.google.com/finance/quote/" + stock_code  
    r = requests.get(url)
    web_content = BeautifulSoup(r.text, 'lxml')
    web_content = web_content.find('div', {"class": 'AHmHk'})  
    web_content = web_content.find('span').text 
    if web_content == []:
        return "99999"  
    return web_content

def update_real_time_data():
    """Updates real-time data and returns a NumPy array.

    This function fetches the real-time signal for the specified stock code
    (defaults to "AAPL-USD"), formats the timestamp, and returns a NumPy array
    containing both the timestamp (Unix seconds) and the price (float).

    Args:
        stock_code (str, optional): The stock code. Defaults to "ADA-USD".

    Returns:
        tuple: A tuple containing the Unix timestamp (float) and the price (float).
    """

    time_stamp = datetime.datetime.now()
    time_in_seconds = time_stamp.timestamp()

    try:
        price = float(get_real_time_signal("ADA-USD"))
    except ValueError:
        print("Error converting price to float")
        price = np.nan  

    return time_in_seconds, price

while True:
    print(update_real_time_data())



# finance.yahoo.com IP Address is 	69.147.92.12
# finance.google.com IP Address is 	142.251.41.3


