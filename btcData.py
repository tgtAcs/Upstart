import requests
import time
from datetime import datetime
import pytz

url = "https://api.binance.com/api/v3/klines"

def updateHistoryPrice():   #write most recent price for 6 hours to 'historyPrice.txt'
    today = datetime.now(pytz.utc)

    endTime = datetime(today.year, today.month, today.day, today.hour, today.minute, 0, tzinfo=pytz.utc).timestamp() * 1000
    if today.hour >= 6:
        startTime = datetime(today.year, today.month, today.day, today.hour - 6, today.minute, 0, tzinfo=pytz.utc).timestamp() * 1000
    else:
        startTime = datetime(today.year, today.month, today.day - 1, 18 + today.hour, today.minute, 0, tzinfo=pytz.utc).timestamp() * 1000

    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={int(startTime)}&endTime={int(endTime)}'
    response = requests.get(url)
    data = response.json()
    closing_prices = [float(entry[4]) for entry in data[-360:]]

    with open('historyPrice.txt', 'w') as f:
        for price in closing_prices:
            f.write(str(price) + '\n')
    with open('historyPrice.txt', 'r') as f:
        lines = f.readlines()
    with open('historyPrice.txt', 'w') as f:
        f.writelines(lines[:-1])

def updatePrice():     #write price passed in to 'historyPrice.txt'
    with open('historyPrice.txt', 'a') as f:
        f.write(f"{getLastMinPrice()}\n")

def getCurrentPrice():      #return current price for BTCUSDT
    pm = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 1
    }
    response = requests.get(url, pm)
    
    if response.status_code == 200:
        data = response.json()
        price = float(data[0][4])
        price = "{:.2f}".format(price)
    else:
        price = 0   
    
        
    return float(price)

def getLastMinPrice():      #return previous minute's closing price for BTCUSDT
    lastMinEndTime = int(time.time() // 60 * 60) * 1000
    lastMinStartTime= lastMinEndTime - 60000

    pm = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "limit": 1,
    "startTime": lastMinStartTime,
    "endTime": lastMinEndTime
    }

    response = requests.get(url, pm)

    if response.status_code == 200:
        data = response.json()
        price = float(data[0][4])
        price = "{:.2f}".format(price)
    else:
        price = 0

    return float(price)

def ema(price, length):             #return Moving Average Exponential value
    alpha = 2 / (length + 1)
    rtn = [price[0]]
    for i in range(1, len(price)):
        ema = float("{:.2f}".format(alpha * price[i] + (1 - alpha) * rtn[-1])) 
        rtn.append(ema)

    return rtn

def getEma():
    recentPrice = []

    with open('app/historyPrice.txt', 'r') as f:
        lines = f.readlines()[-60:] #only read most recent 60 elemtn
        for line in lines:
            recentPrice.append(float(line.strip()))
            
    ema1 = ema(recentPrice, 9)
    ema2 = ema(ema1, 15)

    ema1rtn = float("{:.2f}".format(ema1[-1]))
    ema2rtn = float("{:.2f}".format(ema2[-1]))
    ema1Change = float("{:.2f}".format((ema1[-1] - ema1[-2])))
    
    return ema1rtn, ema2rtn, ema1Change