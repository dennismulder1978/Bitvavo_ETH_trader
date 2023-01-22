from func import *

coin = 'ETH'
# balances, prices and MA's
balance_coin = get_balance(symbol=coin)
balance_euro = get_balance(symbol='EUR')
price_coin = get_price(symbol=coin)
threshold = 4
delta_ma = moving_averages(symbol=coin, a=2, b=5, time_type='5m')

# LOG items: Action, Pair, Amount, Error, datetime
print(trade_market_order(coin=coin,
                         delta_ma=delta_ma,
                         balance_euro=balance_euro,
                         balance_coin=balance_coin,
                         price_coin=price_coin,
                         threshold=threshold))
