import json
import btcData

path = "C:/Users/tgtA/Desktop/Upstart/app/data/account.json"

def getUsername():
    with open(path, 'r') as file:
        return json.load(file)["Username"]

def getBalance():
    with open(path, 'r') as file:
        return float(json.load(file)["Balance"])

def getHolding():
    with open(path, 'r') as file:
        return float(json.load(file)["Holding"])

def setBalance(price):
    price = float("{:.2f}".format(price))

    with open(path, 'r+') as file:
        acc = json.load(file)
        acc["Balance"] = price
        file.seek(0)
        json.dump(acc, file, indent=4)
        file.truncate()

def setHolding(share):
    share = float("{:.10f}".format(share))

    with open(path, 'r+') as file:
        acc = json.load(file)
        acc["Holding"] = share
        file.seek(0)
        json.dump(acc, file, indent=4)
        file.truncate()

def getShare(price):
    price = float("{:.2f}".format(price))
    return float("{:.10f}".format(price / btcData.getCurrentPrice()))

def getPrice(share):
    share = float("{:.10f}".format(share))
    return float("{:.2f}".format(share * btcData.getCurrentPrice()))
    
    
def buyByShare(share):
    share = float("{:.10f}".format(share))
    buyByPrice(getPrice(share))

def buyByPrice(price):
    price = float("{:.2f}".format(price))
    if price <= getBalance():
        setBalance(getBalance() - price)
        setHolding(getHolding() + getShare(price))

def buyMax():
    buyByPrice(getBalance())


def sellByPrice(price):
    price = float("{:.2f}".format(price))
    sellByShare(getShare(price))

def sellByShare(share):
    share = float("{:.10f}".format(share))

    if share <= getHolding():
        setHolding(getHolding() - share)
        setBalance(getBalance() + getPrice(share))

def sellMax():
    sellByShare(getHolding())

