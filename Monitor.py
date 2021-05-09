import websocket
import config
import ccxt
import json
import pandas as pd
import matplotlib.pyplot as plt

with open('buyOrders.json', 'r') as openfile:
    buyOrders = json.load(openfile)
  
print(buyOrders)

fig = plt.figure()
ax = fig.add_subplot()

symbolList = buyOrders.keys()
symbolurl = ""
for x in symbolList:
    symbolurl += f'{x.lower()}@kline_1m/'
symbolurl = symbolurl[:-1]
socket = f"wss://stream.binance.com:9443/stream?streams={symbolurl}"
data = {}
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
    names = list(data.keys())
    values = list([float(f'%.4f' % x['PercentageChange']) for x in data.values()])
    ax.bar(names, values, color ='blue')
    for i,j in zip(names,values):
        ax.annotate(str(j),xy=(i,j))
        #plt.text(i, j, str(j))
    fig.canvas.draw()
    fig.show()
    plt.pause(0.05)
    plt.gca().cla()

def on_close(ws):
    print("### closed ###")

def on_error(ws, error):
    print(error)

ws = websocket.WebSocketApp(socket ,on_message = on_message, on_close = on_close, on_error=on_error)
ws.run_forever()