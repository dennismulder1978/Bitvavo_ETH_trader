from func import *

coin = 'ETH'
# balances, prices and MA's
balance_coin = get_balance(symbol=coin)
balance_euro = get_balance(symbol='EUR')
price_coin = get_price(symbol=coin)
threshold = 4
ma_a, ma_b = moving_averages(symbol=coin, a=2, b=5, time_type='5m')
delta_ma = round((ma_b - ma_a), 1)

# LOG items: Action, Pair, Amount, Error, datetime
print(trade_market_order(coin=coin,
                         delta_ma=delta_ma,
                         balance_euro=balance_euro,
                         balance_coin=balance_coin,
                         price_coin=price_coin,
                         threshold=threshold))

print(f'\tMA_a: {ma_a}')
print(f'\tMA_b: {ma_b}')