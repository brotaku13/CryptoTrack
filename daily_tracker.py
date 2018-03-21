import CryptoTrack as ct
import pandas as pd
from pathlib import Path
from datetime import datetime
from fbchat import Client
from fbchat.models import * 
import secret
import math

CWD = Path.cwd()
def convert_data(week_data: pd.DataFrame):
    week_data['price_high'] = week_data['price_high'].astype('float')
    week_data['price_low'] = week_data['price_low'].astype('float')
    week_data['price_close'] = week_data['price_close'].astype('float')
    week_data['price_open'] = week_data['price_open'].astype('float')
    week_data['trades_count'] = week_data['trades_count'].astype('float')
    week_data['volume_traded'] = week_data['volume_traded'].astype('float')
    return week_data

def get_high(week_data: pd.DataFrame):
    return week_data.loc[week_data['price_high'].idmax()]

def send_report(line):
    line = 'Greetings from CryptoTrack! \n' + line
    client = Client(secret.EMAIL, secret.PASSWORD)
    client.send(Message(text=line), thread_id=client.uid, thread_type=ThreadType.USER)
    client.logout()

def print_info(snapshot: dict):
    for key, value in snapshot.items():
        if key != 'current_data':
            print('{}: High: {}, Low: {}'.format(key, snapshot[key]['price_high'], snapshot[key]['price_low']))
        else:
            print('{}: Price: {}'.format(key, snapshot[key]['price']))

def prettify_date(date: str):
    date = date.split('-')
    return '{}.{}.{}'.format(date[1], date[2][:2], date[0])
    

def compose_line(extreme: str, period: str, snapshot: dict, crypto: str):
    df = snapshot['{}_data'.format(period.lower())]['data'].time_period_start[0]
    line = 'The Price of {crypto} is the {extreme}est it\'s been in the last {period}!\nThe last time it was this {extreme} was {date}.\nCurrent price: ${current_price}\n{period} {extreme} ${period_price}'.format(
        crypto=crypto,
        extreme=extreme,
        period=period,
        date=prettify_date(snapshot['{}_data'.format(period.lower())]['data'].time_period_start[0]),
        current_price=snapshot['current_data']['price'],
        period_price=snapshot['{}_data'.format(period.lower())]['price_{}'.format(extreme)]
    )
    buy_sell = ''
    if extreme.lower() == 'high':
        buy_sell = 'sell'
    else:
        buy_sell = 'buy'

    advice = f'\n\nAs the price is the {extreme}est it\'s been in the last {period}, now it a great time to {buy_sell} some {crpyto}.'
    
    print(line+advice)
    return line + advice

def create_message(snapshot: dict, crypto: str):
    current_price = snapshot['current_data']['price']

    if snapshot['year_data']['price_high'] < current_price:
        return compose_line('high', 'year', snapshot, crypto)

    elif snapshot['year_data']['price_low'] > current_price:
        return compose_line('low', 'year', snapshot, crypto)

    elif snapshot['month_data']['price_high'] < current_price:
        return compose_line('high', 'month', snapshot, crypto)

    elif snapshot['month_data']['price_low'] > current_price:
        return compose_line('low', 'month', snapshot, crypto)

    elif snapshot['week_data']['price_high'] < current_price:
        return compose_line('high', 'week', snapshot, crypto)
    
    elif snapshot['week_data']['price_low'] > current_price:
        return compose_line('low', 'week', snapshot, crypto)

    else:
        return ''
    
def main():
    ct.get_data(symbol_id='BTC', period_id='1DAY', request_limit=1000, tdelta=7)
    ct.get_data(symbol_id='BTC', period_id='1DAY', request_limit=1000, tdelta=30)
    ct.get_data(symbol_id='BTC', period_id='1DAY', request_limit=1000, tdelta=365)

    week_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_7_day.csv')))
    month_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_30_day.csv')))
    year_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_365_day.csv')))

    current_data = ct.get_current_price()

    snapshot = {}
    snapshot['week_data'] = {'price_high' : week_data.loc[week_data['price_high'].idxmax()]['price_high'], 'price_low': week_data.loc[week_data['price_high'].idxmin()]['price_high'], 'data': week_data}
    snapshot['month_data'] = {'price_high': month_data.loc[month_data['price_high'].idxmax()]['price_high'], 'price_low': month_data.loc[month_data['price_high'].idxmin()]['price_high'], 'data': month_data}
    snapshot['year_data'] = {'price_high': year_data.loc[year_data['price_high'].idxmax()]['price_high'], 'price_low': year_data.loc[year_data['price_high'].idxmin()]['price_high'], 'data': year_data}
    snapshot['current_data'] = {'price': current_data['PRICE'], 'data': current_data}

    print_info(snapshot)

    message = create_message(snapshot, 'BTC')
    if message != '':
        send_report(message)
    else:
        print('Nothing remarkable is happening now. ')
    
if __name__ == '__main__':
    main()