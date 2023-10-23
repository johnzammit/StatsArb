from dotenv import load_dotenv, find_dotenv
from binance import Client
import os

def establish_connection(useProd: bool = False) -> Client:
    load_dotenv(find_dotenv())
    tld = 'us' if useProd else 'com'
    binance_api_key = os.getenv('binanceAPIKey') if useProd else os.getenv('binanceAPIKey_testnet')
    binance_secret_key = os.getenv('binanceAPIKey') if useProd else os.getenv('binanceSecretKey_testnet')
    assert(binance_api_key and binance_secret_key)
    return Client(binance_api_key, binance_secret_key, tld=tld, testnet=(not useProd))