from func import *

coin = 'ETH'
# balances en prices
balance_coin = get_balance(coin)
balance_EURO = get_balance('EUR')
price_coin = get_price(coin)
threshold = 4
# MA's
ma_a, ma_b = moving_averages(symbol=coin, a=2, b=5, time_type='5m')


print(f'Balance COIN {coin}: {balance_coin}')
print(f'Balance EURO: {balance_EURO}')
print(f'MA_a: {ma_a}')
print(f'MA_b: {ma_b}')
print(f'delta MA: {round((ma_b - ma_a), 1)}')
print(f'Price COIN: {price_coin}')


# LOG items: Action, Pair, Amount, Error, datetime
if ((ma_b - ma_a) > threshold) & (balance_EURO > 10):
    print(trade_market_order(symbol=coin, action='buy', amount=balance_EURO))
    print('BUY')

elif ((ma_b - ma_a) < 0-threshold) & (balance_coin > 0.01):
    print(trade_market_order(symbol=coin, action='sell', amount=balance_coin))
    print('SELL')
else:
    log(f'Do nothing,{coin}-EUR,{round((ma_b - ma_a), 1)},none', 'log')
    print('Do nothing')
