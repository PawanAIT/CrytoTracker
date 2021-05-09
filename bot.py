import websocket
import config
import ccxt
import json
import pandas as pd
from tabulate import tabulate
exchange =  ccxt.binance({
    'apiKey' : config.API_KEY,
    'secret' : config.API_SECRET
})
balanceSpot = exchange.fetch_balance({
    'type' : 'spot'
})
balanceMargin = exchange.fetch_balance({
    'type' : 'margin'
})
symbols = set()
for bal in balanceSpot['info']['balances']:
    if float(bal['free']) > 0:
        symbols.add(bal['asset'])
for val in balanceMargin['info']['userAssets']:
    if float(val['netAsset']) > 0:
        symbols.add(val['asset'])
symbols.remove('USDT')
since = exchange.milliseconds () - 30 * 86400000  # -1 day from now
orders = []
for symbol in symbols:
    SymbolinUSDT = f'{symbol}/USDT'
    orders += exchange.fetch_closed_orders(SymbolinUSDT,since, 10 ,{'type' : 'margin'})
buyOrders = {}
for val in orders:
    if val['info']['side'] == 'BUY':
        symbol = val['info']['symbol'].lower()
        quantity = val['info']['executedQty']
        totalMoneyinUSDT = val['info']['cummulativeQuoteQty']
        buyOrders[symbol] = {'totalamountinUSDT': totalMoneyinUSDT, 'quantity' : quantity}
        #print(val)
symbolList = buyOrders.keys()
symbolurl = ""
for x in symbolList:
    symbolurl += f'{x.lower()}@kline_1m/'
symbolurl = symbolurl[:-1]
symbolList = buyOrders.keys()
socket = f"wss://stream.binance.com:9443/stream?streams={symbolurl}"
from IPython.display import clear_output
data = {}
import os
def on_message(ws, message):
    obj = json.loads(message)
    #print(obj)
    # Pretty Print JSON
    #json_formatted_str = json.dumps(obj['data'], indent=4)
    symbol, cur_price = obj['data']['s'].lower(), float(obj['data']['k']['c'])
    buy_price = float(buyOrders[symbol]['totalamountinUSDT'])
    new_price = cur_price * float(buyOrders[symbol]['quantity'])
    
    perChange = (new_price - buy_price) * 100 / buy_price
    #data[symbol] = {'cur_price' : cur_price, 'Bought_price' : buy_price, 'PercentageChange' : perChange}
    data[symbol] = {'PercentageChange' : perChange}
    clear_output(wait=True)
    os.system('cls')
    df = pd.DataFrame(data)
    print(tabulate(df, headers = 'keys', tablefmt = 'psql'))

def on_close(ws):
    print("### closed ###")

def on_error(ws, error):
    print(error)

ws = websocket.WebSocketApp(socket ,on_message = on_message, on_close = on_close, on_error=on_error)
ws.run_forever()