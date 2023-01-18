from Secret import const
from python_bitvavo_api.bitvavo import Bitvavo
import datetime
import os.path

bitvavo = Bitvavo({
    'APIKEY': const.api_key,
    'APISECRET': const.api_secret,
    'RESTURL': 'https://api.bitvavo.com/v2',
    'WSURL': 'wss://ws.bitvavo.com/v2/',
    'ACCESSWINDOW': 10000,
    'DEBUGGING': False
})


def get_balance(symbol: str):
    try:
        return float(bitvavo.balance({"symbol": str.upper(symbol)})[0]['available'])
    except Exception as e:
        log(f'Trying to get balance,{symbol},0,{e}', 'error')
        print(e)


def get_price(symbol: str):
    try:
        pair = str.upper(symbol) + '-EUR'
        return float(bitvavo.tickerPrice({"market": pair})['price'])
    except Exception as e:
        log(f'Trying to get price,{pair},0,{e}', 'error')
        print(e)


def moving_averages(symbol: str, a: int, b: int, time_type: str):
    pair = str.upper(symbol) + '-EUR'
    try:
        resp = bitvavo.candles(pair, time_type, {})
        temp_a = float(0)
        temp_b = float(0)
        for i in range(1, a + 1):
            temp_a += float(resp[i][4])
        for j in range(1, b + 1):
            temp_b += float(resp[j][4])
        ma_a = temp_a / a
        ma_b = temp_b / b
        return ma_a, ma_b
    except Exception as e:
        log(f'Trying to get price,{symbol},0,{e}', 'error')
        print(e)


def trade_market_order(symbol: str, action: str, amount: int):
    pair = str.upper(symbol) + '-EUR'
    try:
        if action.lower() == 'buy':
            bitvavo.placeOrder(pair, action, 'market', {'amountQuote': amount})
        else:
            bitvavo.placeOrder(pair, action, 'market', {'amount': amount})
        log(f'{action},{pair},{amount},none', 'log')
        log(f'{action},{pair},{amount},none', 'action')
        return f'{action}, {pair}, {amount}, {datetime.datetime.now()}'
    except Exception as e:
        log(f'{action},{pair},{amount},{e}', 'log')
        log(f'{action},{pair},{amount},{e}', 'error')
        return f'{e}, {action}, {pair}, {amount}, {datetime.datetime.now()}'


def log(stringer: str, name: str):
    file = f'{name}.csv'
    text = f'{stringer},{datetime.datetime.now()}\n'
    if os.path.isfile(file):
        with open(file, 'a') as f:
            f.write(text)
            f.close()
    else:
        with open(file, 'w') as g:
            g.write('Action,Pair,Amount,Error,DateTime\n' + text)
            g.close()
