from Secret import const
from python_bitvavo_api.bitvavo import Bitvavo
import datetime
import os.path

bitvavo = Bitvavo({
    'APIKEY': const.api_key1,
    'APISECRET': const.api_secret1,
    'RESTURL': 'https://api.bitvavo.com/v2',
    'WSURL': 'wss://ws.bitvavo.com/v2/',
    'ACCESSWINDOW': 10000,
    'DEBUGGING': False
})

bitvavo_action = Bitvavo({
    'APIKEY': const.api_key2,
    'APISECRET': const.api_secret2,
    'RESTURL': 'https://api.bitvavo.com/v2',
    'WSURL': 'wss://ws.bitvavo.com/v2/',
    'ACCESSWINDOW': 10000,
    'DEBUGGING': False
})


def get_balance(symbol: str):
    try:
        return float(bitvavo.balance({"symbol": str.upper(symbol)})[0]['available'])
    except Exception as error:
        log(f'ERROR BALANCE,{symbol},NaN,NaN,NaN,{error}')
        print(error)


def get_price(symbol: str):
    try:
        pair = str.upper(symbol) + '-EUR'
        return float(bitvavo.tickerPrice({"market": pair})['price'])
    except Exception as error:
        log(f'ERROR PRICE,{pair},NaN,NaN,NaN,{error}')
        print(error)


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
        ma_a = round((temp_a / a), 2)
        ma_b = round((temp_b / b), 2)
        return ma_a, ma_b
    except Exception as error:
        log(f'ERROR MA,{pair},NaN,NaN,NaN,{error}')
        print(error)


def trade_market_order(coin: str, delta_ma: float, balance_euro: float, balance_coin: float, threshold: float):
    pair = str.upper(coin) + '-EUR'
    action = 'Nothing'
    err = 'none'

    if (delta_ma > threshold) & (balance_euro > 1):  # buy coins with euros
        action = 'Buy'
        try:
            bitvavo_action.placeOrder(pair, 'buy', 'market', {'amountQuote': balance_euro})
        except Exception as error:
            print(error)
            err = error
    elif (delta_ma < 0 - threshold) & (balance_coin > 0.001):  # sell coins for euros
        action = 'Sell'
        try:
            bitvavo_action.placeOrder(pair, 'sell', 'market', {'amount': balance_coin})
        except Exception as error:
            print(error)
            err = error

    log(f'{action},{pair},{balance_euro},{balance_coin},{delta_ma},{err}')
    return f'{action} {pair}, euro: {balance_euro}, {coin}: {balance_coin}, delta_ma: {delta_ma}, error: {err}, {datetime.datetime.now()} '


def log(stringer: str):
    path = ''
    file = f'{path}log.csv'
    text = f'{stringer},{datetime.datetime.now()}\n'
    if os.path.isfile(file):
        with open(file, 'a') as f:
            f.write(text)
            f.close()
    else:
        with open(file, 'w') as g:
            g.write('Action,Pair,Balance_euro,Balance_coin,Delta_MA,Error,DateTime\n' + text)
            g.close()
