from Secret import const
from python_bitvavo_api.bitvavo import Bitvavo
import datetime
import os.path
import smtplib
from email.mime.text import MIMEText
import mysql.connector

bitvavo_info = Bitvavo({
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

mydb = mysql.connector.connect(
    host=const.host_mysql,
    user=const.user_mysql,
    password=const.password_mysql,
    db=const.db_mysql
)


def get_balance(symbol: str):
    try:
        return float(bitvavo_info.balance({"symbol": str.upper(symbol)})[0]['available'])
    except Exception as error:
        log(f'ERROR BALANCE,{symbol},NaN,NaN,NaN,{error}')
        send_mail(action='Error', stringer=f'GET_BALANCE went wrong: {error}')
        print(error)


def get_price(symbol: str):
    try:
        pair = str.upper(symbol) + '-EUR'
        return float(bitvavo_info.tickerPrice({"market": pair})['price'])
    except Exception as error:
        log(f'ERROR PRICE,{pair},NaN,NaN,NaN,{error}')
        send_mail(action='Error', stringer=f'GET_PRICE went wrong: {error}')
        print(error)


def moving_averages(symbol: str, a: int, b: int, time_type: str):
    pair = str.upper(symbol) + '-EUR'
    try:
        resp = bitvavo_info.candles(pair, time_type, {})
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
        send_mail(action='Error', stringer=f'MOVING_AVERAGE went wrong: {error}')
        print(error)


def trade_market_order(coin: str, delta_ma: float, balance_euro: float, balance_coin: float, price_coin: float,
                       threshold: float,):
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
            send_mail(action='Error', stringer=f'Trade went wrong: {error}')
    elif (delta_ma < 0 - threshold) & (balance_coin > 0.001):  # sell coins for euros
        action = 'Sell'
        try:
            bitvavo_action.placeOrder(pair, 'sell', 'market', {'amount': balance_coin})
        except Exception as error:
            print(error)
            err = error
            send_mail(action='Error', stringer=f'Trade went wrong: {error}')
    stringer = f'\tAction: {action} {pair}\n\tBalance EURO: {balance_euro}\n\tBalance {coin}: {balance_coin}\n'
    stringer += f'\tPrice coin: {price_coin}\n\tDelta_ma: {delta_ma}\n\tError: {err}\n\tTime: {datetime.datetime.now()}'

    send_mail(action=action, stringer=stringer)
    log(f'{action},{pair},{balance_euro},{balance_coin},{delta_ma},{err}')
    add_mysql_log(action=action,
                  pair=pair,
                  balance_coin=balance_coin,
                  balance_euro=balance_euro,
                  price_coin=price_coin,
                  delta_ma=delta_ma,
                  error=err)
    return stringer


def add_mysql_log(action: str, pair: str, balance_euro: float, balance_coin: float,
                  price_coin: float, delta_ma: float, error: str):

    my_cursor = mydb.cursor()

    sql = f"INSERT INTO log (name, address) VALUES "
    sql += f"({action},{pair},{balance_euro},{balance_coin},{price_coin},{delta_ma},{error},{datetime.datetime.now()})"

    my_cursor.execute(sql)

    sql = "INSERT INTO log (Action, Pair, Balance_euro, Balance_coin, Price_coin, Delta_ma, Error, Datetime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (action, pair, balance_euro, balance_coin, price_coin, delta_ma, error, datetime.datetime.now())
    my_cursor.execute(sql, val)

    mydb.commit()

    print(my_cursor.rowcount, "record inserted.")


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


def send_mail(action: str, stringer: str):
    if (action.lower() == 'buy') or (action.lower() == 'sell') or (action.lower() == 'error'):
        try:
            msg = MIMEText(stringer)
            msg['Subject'] = f'Bitvavo trade {action}'
            msg['From'] = const.email_sender
            msg['To'] = const.email_receiver

            my_mail = smtplib.SMTP('smtp.gmail.com', 587)
            my_mail.ehlo()
            my_mail.starttls()
            my_mail.login(const.email_sender, const.email_sender_password)
            my_mail.sendmail(const.email_sender, const.email_receiver, msg.as_string())
            my_mail.close()
            print("Mail send successfully.")

        except Exception as error:
            log(f'ERROR EMAIL,{action},NaN,NaN,NaN,{error}')
            print(f"something went wrong while trying to send the mail: {error}")

