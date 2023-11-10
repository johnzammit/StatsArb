## TO DO:

##Initialize price and other variables from API
##Calculate bollinger bands and moving averages
##Create buy and sell functions
##price = bianace.get_price('BTCUSDT')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import json
import datetime
from datamodel import Ticker, BollingerBand, PriceInterval

import math
from market_state import MarketState

    
"""
Execution will using MarketState data to know when to execute a trade.
"""
import urllib.parse
import hashlib
import hmac
import base64
import requests
import time

class Execution():
    def __init__(self, formula, api_key, secret_key, api_url, balance, open_orders,  initial_order_value):
        """"Formula is a tuple containing coins and their weights (ticker, weight)"""
        # need to take in a formula
        self.api_url = "https://api.binance.us"
        self.api_key = "YOUR_API_KEY"
        self.secret_key = "YOUR_SECRET_KEY"
        self.balance = balance 
        self.open_orders = open_orders
        self.initial_order_value = initial_order_value

    # get binanceus signature
    def get_binanceus_signature(self, data, secret):
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(secret, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac
    

    # Attaches auth headers and returns results of a POST request
    def binanceus_request(self, uri_path, data, api_key, api_sec):
        # TODO: probably could just use the order API in the binance-python library
        headers = {}
        headers['X-MBX-APIKEY'] = api_key
        signature = self.get_binanceus_signature(data, api_sec)
        payload={
            **data,
            "signature": signature,
            }
        req = requests.post((self.api_url + uri_path),headers=headers,data=payload)
        return req.text
    

    #checks if the spread is above the upper bollinger band or below the lower bollinger band
    async def place_order_condition(self, spread: float, upper_bollinger_band_price: float, lower_bollinger_band_price: float) -> bool:
        return spread >= upper_bollinger_band_price or spread <= lower_bollinger_band_price 

    #tell binance to buy at a certain price
    async def place_limit_buy(self, symbol: str, quantity: float): 
        self.balance -= quantity * MarketState.current_price(symbol)
        self. initial_order_value += quantity *  MarketState.current_price(symbol)
        print("Order placed: " + symbol + " at " +  MarketState.current_price(symbol))
        print("Balance: " + self.balance)
        open_orders +=1
    

    #tell binance to sell at a certain price
    async def place_limit_sell(self, symbol: str, quantity: float):
        self.balance += quantity *  MarketState.current_price(symbol)
        self.initial_order_value += quantity *  MarketState.current_price(symbol)
        print("Order placed: " + symbol + " at " +  MarketState.current_price(symbol))
        print("Balance: " + self.balance)
        open_orders +=1
        
    async def close_limit_buy(self, symbol: str, quantity: float):
        self.balance += quantity *  MarketState.current_price(symbol)
        print("Order closed: " + symbol + " at " +  MarketState.current_price(symbol))
        print("Balance: " + self.balance)
        open_orders -=1
    
    async def close_limit_sell(self, symbol: str, quantity: float):
        self.balance -= quantity *  MarketState.current_price(symbol)
        print("Order closed: " + symbol + " at " +  MarketState.current_price(symbol)) 
        print("Balance: " + self.balance)
        open_orders -=1

    #check if orders are still open or not before placing new orders
    async def check_open_orders(self) -> bool:
        return self.open_orders > 0
        
    async def open_positions_value(self, long_coin, short_coin, quantity) -> float:
        total_position_value = long_coin.price * quantity + short_coin.price * quantity
        print("Current position value: " + total_position_value)
        return total_position_value


    #calculate time weighted take profit price for long position
    async def take_profit_long_price(self, coin: float, timestamp) -> float:
        decrease_rate = 0.055
        target_price = MarketState.spread_moving_avg() - (decrease_rate * timestamp) + MarketState.derivative_of_spread() % MarketState.current_price(coin) / 100
        ## Need to add accelerator with the derivative of spread

        return target_price
    #calculate time weighted take profit price for short position
    async def take_profit_short_price(self, coin: float, timestamp) -> float:
        decrease_rate = 0.055
        target_price = MarketState.spread_moving_avg() + (decrease_rate * timestamp) + MarketState.derivative_of_spread() % MarketState.current_price(coin) / 100
        ## Need to add accelerator with the derivative of spread

        return target_price
    


    def main(self, spread: PriceInterval, long_coin: Ticker, short_coin: Ticker, quantity: float, stopPrice: float):
        # XXX: define quantity/fix params
        # TODO: making the function take in parameters allow us to test more easily and separately from MarketState (so we can isolate which class has a problem)
        # XXX: should return a result for each iteration of this (so we can debug/see what happened in each iteration during backtest)

        #Define all variables using MarketState
        long_coin = MarketState.long_coin()
        short_coin = MarketState.short_coin()
        beta = MarketState.beta()
        # check if we should buy or sell
        if (beta < 0.0001):
            if (self.place_order_condition(spread.estimate, spread.upper, spread.lower)):
                self.place_limit_buy(long_coin.symbol, quantity)
                self.place_limit_sell(short_coin.symbol, quantity)
                self.open_positions_value(long_coin.symbol, short_coin.symbol, quantity)

                #start timer
                timestamp = int(time.time() * 1000)

                # monitor when to sell
                while (self.check_open_orders()):
                    #update variables using MarketState
                
                    #check if price is at or below hard stop loss
                    if (MarketState.hard_stop_loss() * -1 >= self.initial_order_value() - self.original_position_value(long_coin.symbol, short_coin.symbol, quantity)):
                        #sell at hard stop loss
                        self.close_limit_buy(long_coin.symbol, quantity)
                        self.close_limit_sell(short_coin.symbol, quantity)

                    #check if orders are at take profit price
                    if (MarketState.current_price(long_coin.symbol) >= self.take_profit_long_price(long_coin, timestamp) or MarketState.current_price(short_coin.symbol) <= self.take_profit_short_price(short_coin, timestamp)):
                        self.close_limit_buy(long_coin.symbol, quantity)
                        self.close_limit_sell(short_coin.symbol, quantity)
                

                
            
    if __name__ == '__main__':
        main()
