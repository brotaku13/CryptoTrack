import crypto_get as ct
import pandas as pd
from pathlib import Path
from datetime import datetime
from fbchat import Client
from fbchat.models import * 
import math

CWD = Path.cwd()

def convert_data(data: pd.DataFrame):
    """
    converts data in a pandas dataframe from strings to numbers
    :param: data [pd.DataFrame] -- a pandas dataframe containing all the information for that time period
    :returns: data [pd.Dataframe] -- a pandas dataframe with converted values from string to integer
    """
    data['price_high'] = data['price_high'].astype('float')
    data['price_low'] = data['price_low'].astype('float')
    data['price_close'] = data['price_close'].astype('float')
    data['price_open'] = data['price_open'].astype('float')
    data['trades_count'] = data['trades_count'].astype('float')
    data['volume_traded'] = data['volume_traded'].astype('float')
    return data

def get_high(week_data: pd.DataFrame):
    """
    gets the week high data for the current week. 
    :returns: the price correlated with the high price for the current dataframe
    """
    return week_data.loc[week_data['price_high'].idmax()]

def print_info(snapshot: dict):
    """
    a utility function to make printing the snapshot data easier
    :param: snapshot [dict] -- a dict containing all of the extreme data for the current time snapshot
    """
    for key, value in snapshot.items():
        if key != 'current_data':
            print('{}: High: {}, Low: {}'.format(key, snapshot[key]['price_high'], snapshot[key]['price_low']))
        else:
            print('{}: Price: {}'.format(key, snapshot[key]['price']))

def prettify_date(snapshot, period, extreme):
    """
    utility function which creates a pretty date for use in sending the message and reporting the extreme
    :param: snapshot [dict]
    :param: period [str] -- week / month / year
    :parma: extreme [str] -- high / low
    :returns: [str] -- a string containing the pretty date
    """
    df = snapshot['{}_data'.format(period.lower())]['data']
    if extreme.lower() == 'low':
        date = df['time_period_start'][df['price_high'].idxmin]
    else:
        date = df['time_period_start'][df['price_high'].idxmax]
    date = date.split('-')
    return '{}.{}.{}'.format(date[1], date[2][:2], date[0])

    
def compose_line(extreme: str, period: str, snapshot: dict, crypto: str):
    """
    composes the message that will be sent to the facebook chat
    :param: extreme [str] -- high / low the extreme that will be reported
    :param: period [str] -- week / month / year the time period being reported for
    :param: snapshot [dict] -- a dictionary containing all of the snapshot data
    :param: crypto [str] -- the cryptocurrency id ex: BTC
    :returns: [str] -- the conposed line to be sent to the asker
    """
    date = prettify_date(snapshot, period, extreme)

    line = 'The Price of {crypto} is the {extreme}est it\'s been in the last {period}!\nThe last time it was this {extreme} was {date}.\nCurrent price: ${current_price}\n{period} {extreme} ${period_price}'.format(
        crypto=crypto,
        extreme=extreme,
        period=period,
        date=date,
        current_price=snapshot['current_data']['price'],
        period_price=snapshot['{}_data'.format(period.lower())]['price_{}'.format(extreme)]
    )

    buy_sell = ''
    if extreme.lower() == 'high':
        buy_sell = 'sell'
    else:
        buy_sell = 'buy'

    advice = f'\n\nAs the price is the {extreme}est it\'s been in the last {period}, now it a great time to {buy_sell} some {crypto}.'

    print(line+advice)
    return line + advice

def create_message(snapshot: dict, crypto: str):
    """
    determines if a message should be sent based on the current price as well as the period prices
    :param: snapshot [dict] -- dictionary containing the snapshot data for this period
    :param: crypto [str] -- the crypto symbol
    :returns: [str] -- the message returned to the asker. will be empty if no exciting data is found
    """
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
    
def get_data(symbol_id: str, period_id: str, request_limit: int):
    """
    runs the api requests for the cryptocurrency apis
    :param: symbol_id [str] -- the cryptocurrency symbol
    :param: period_id [str] -- period ID (1DAY)
    :param: request_limt [int] -- number of requests made to the api before the call terminates
    """
    ct.get_data(symbol_id=symbol_id, period_id=period_id, request_limit=request_limit, tdelta=7)
    ct.get_data(symbol_id=symbol_id, period_id=period_id, request_limit=request_limit, tdelta=30)
    ct.get_data(symbol_id=symbol_id, period_id=period_id, request_limit=request_limit, tdelta=365)

def create_snapshot():
    """
    creates the snapshot dictionary from the CSV files to be used in the rest of the program
    :returns: [dict] -- a snapshot of the current extreme data
    """
    week_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_7_day.csv')))
    month_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_30_day.csv')))
    year_data = convert_data(pd.read_csv(str(CWD / 'Data' / 'BTC_365_day.csv')))

    current_data = ct.get_current_price()

    snapshot = {}
    snapshot['week_data'] = {'price_high' : week_data.loc[week_data['price_high'].idxmax()]['price_high'], 'price_low': week_data.loc[week_data['price_high'].idxmin()]['price_high'], 'data': week_data}
    snapshot['month_data'] = {'price_high': month_data.loc[month_data['price_high'].idxmax()]['price_high'], 'price_low': month_data.loc[month_data['price_high'].idxmin()]['price_high'], 'data': month_data}
    snapshot['year_data'] = {'price_high': year_data.loc[year_data['price_high'].idxmax()]['price_high'], 'price_low': year_data.loc[year_data['price_high'].idxmin()]['price_high'], 'data': year_data}
    snapshot['current_data'] = {'price': current_data['PRICE'], 'data': current_data}

    return snapshot

