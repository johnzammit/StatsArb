import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

binance_api_key = os.getenv('binanceAPIKey')
binance_secret_key = os.getenv('binanceSecretKey')

from binance.client import Client
client = Client(binance_api_key, 
                binance_secret_key,
                tld='us')

def get_data(coin, kline_interval, start, end):
        klines = client.get_historical_klines(coin, kline_interval, start, end)
        coin_df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 
                                                'volume', 'close_time', 'quote_av', 'trades', 
                                                'tb_base_av', 'tb_quote_av', 'ignore' ])
        coin_df['timestamp'] = pd.to_datetime(coin_df['timestamp'], unit='ms')
        coin_df.set_index('timestamp', inplace=True)
        coin_df['close'] = coin_df['close'].astype(float)
        return coin_df

dataframe = get_data("FORTHUSD", Client.KLINE_INTERVAL_1MINUTE, "1 Oct, 2022", "2 Oct, 2022")

print(dataframe)