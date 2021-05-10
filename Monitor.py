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
#fig, ax = plt.subplots(nrows = 1, ncols = 1)

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
    data[symbol] = {'PercentageChange' : perChange, 'cur_price' : new_price, 'Bought_price' : buy_price}
    names = list(data.keys())
    percentage = list([float(f'%.4f' % x['PercentageChange']) for x in data.values()])
    currentPrice = list([float(f'%.4f' % x['cur_price']) for x in data.values()])
    boughtPrice = list([float(f'%.4f' % x['Bought_price']) for x in data.values()])
    barWidth = 0.25
    ax.bar(names, percentage, color ='blue')
    
    #ax2.bar(names, currentPrice, color = 'pink')
    #fig.canvas.draw()
    
    for i,j in zip(names,percentage):
        ax.text(i, j, str(j))
    # for i,j in zip(names,currentPrice):
    #     ax2.text(i, j, str(j))
    #     #plt.text(i, j, str(j))
    # plt.cla()
    # fig.cla()
    #plt.draw()

    fig.canvas.draw()
    fig.show()
    plt.cla()
    #plt.show()
    plt.pause(0.10)

def on_close(ws):
    print("### closed ###")

def on_error(ws, error):
    print(error)

ws = websocket.WebSocketApp(socket ,on_message = on_message, on_close = on_close, on_error=on_error)
ws.run_forever()