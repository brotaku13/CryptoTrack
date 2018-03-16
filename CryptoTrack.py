import requests
import json
from pprint import PrettyPrinter
from datetime import datetime, timedelta
from pathlib import Path
import csv
import time


API_KEY = 'C091435D-9110-4BED-9B93-C03ABC126DED'
HISTORY_URL = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history'
CRYPTOCOMPARE_URL = 'https://min-api.cryptocompare.com/data/pricemultifull?'
header = {'X-CoinAPI-Key': API_KEY}
cwd = Path.cwd()
datafolder = cwd / 'Data'

def get_data(symbol_id='BTC', period_id='1DAY', request_limit=1000, tdelta=30):
    now = datetime.utcnow()
    month = timedelta(days=tdelta)
    past_month = (now - month).isoformat()

    parameters = {'symbol_id': symbol_id, 'period_id': period_id, 'time_start': past_month[:-3], 'limit':request_limit}
    response = requests.get(HISTORY_URL, params=parameters, headers=header)

    while response.status_code != 200:
        time.sleep(5)
        response = requests.get(HISTORY_URL, params=parameters, headers=header)
    
    data = response.json()
    # this is a commnet
    csv_headers = ['time_period_start', 'time_period_end', 'price_high', 'price_low', 'price_close', 'price_open', 'trades_count', 
                    'volume_traded', 'time_open', 'time_close']


    with open(str(datafolder / f'{symbol_id}_{tdelta}_day.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, csv_headers)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def get_current_price(fsyms='BTC'):
    parameters = {'fsyms': fsyms, 'tsyms': 'USD'}
    response = requests.get(CRYPTOCOMPARE_URL, params=parameters)
    while response.status_code != 200:
        print('connection failed, trying again in 5 seconds')
        time.sleep(5)
        response = requests.get(CRYPTOCOMPARE_URL, params=parameters)

    data = response.json()['RAW']['BTC']['USD']
    data['Timestamp'] = datetime.utcnow().isoformat()
    
    headers = ['Timestamp'] + list(data.keys())

    return data
