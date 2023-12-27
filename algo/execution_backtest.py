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
from market_state_basic_test import MarketState

    
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
    def __init__(self, client: Client = None, balance: int = 10000, open_orders: int = 0,  initial_order_value: int = 0):
        """"Formula is a tuple containing coins and their weights (ticker, weight)"""
        assert(client is not None)
        self.mstate = MarketState(client)
        self.open_orders = open_orders
        self.balance = balance
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
    def place_order_condition(self, spread: float, upper_bollinger_band_price: float, lower_bollinger_band_price: float) -> bool:
        return spread >= upper_bollinger_band_price or spread <= lower_bollinger_band_price 

    #tell binance to buy at a certain price
    def place_limit_buy(self, symbol: str, quantity: float): 
        self.balance -= quantity * self.mstate.current_price(symbol)
        self.initial_order_value += quantity *  self.mstate.current_price(symbol)
        # print("Order placed: " + symbol + " at " + str(self.mstate.current_price(symbol)))
        # print("Balance: " + str(self.balance))
        self.open_orders +=1
    

    #tell binance to sell at a certain price
    def place_limit_sell(self, symbol: str, quantity: float):
        self.balance += quantity *  self.mstate.current_price(symbol)
        self.initial_order_value += quantity *  self.mstate.current_price(symbol)
        # print("Order placed: " + symbol + " at " +  str(self.mstate.current_price(symbol)))
        # print("Balance: " + str(self.balance))
        self.open_orders +=1
        
    def close_limit_buy(self, symbol: str, quantity: float):
        self.balance += quantity *  self.mstate.current_price(symbol)
        # print("Order closed: " + symbol + " at " +  str(self.mstate.current_price(symbol)))
        # print("Balance: " + str(self.balance))
        self.open_orders -=1
    
    def close_limit_sell(self, symbol: str, quantity: float):
        self.balance -= quantity *  self.mstate.current_price(symbol)
        # print("Order closed: " + symbol + " at " +  str(self.mstate.current_price(symbol))) 
        # print("Balance: " + str(self.balance))
        self.open_orders -=1

    #check if orders are still open or not before placing new orders
    def check_open_orders(self) -> bool:
        return self.open_orders > 0
        
    def current_positions_value(self, long_coin, short_coin, quantity_long, quantity_short) -> float:
        total_position_value = self.mstate.current_price(long_coin) * quantity_long + self.mstate.current_price(short_coin) * quantity_short
        #print("Current position value: " + str(total_position_value))
        return total_position_value


    #calculate time weighted take profit price for long position
    def take_profit_long_price(self, coin: str, timestamp, coin_pair: tuple[str, str]) -> float:
        decrease_rate = 0.055
        # target_price = self.mstate.spread_moving_avg(coin_pair) - (decrease_rate * timestamp) + self.mstate.derivative_of_spread(coin_pair) % self.mstate.current_price(coin) / 100
        target_price = self.mstate.spread_moving_avg(coin_pair)
        ## Need to add accelerator with the derivative of spread

        return target_price
    #calculate time weighted take profit price for short position
    def take_profit_short_price(self, coin: str, timestamp, coin_pair: tuple[str, str]) -> float:
        decrease_rate = 0.055
        # target_price = self.mstate.spread_moving_avg(coin_pair) + (decrease_rate * timestamp) + self.mstate.derivative_of_spread(coin_pair) % self.mstate.current_price(coin) / 100
        target_price = self.mstate.spread_moving_avg(coin_pair) 

        ## Need to add accelerator with the derivative of spread
        return target_price
    
    def plot_spread(self):
        return self.mstate.plot_spread()
    def plot_boll_bands(self):
        return self.mstate.plot_bollinger_bands()
    
    def main(self, long_coin: str, short_coin: str):
        # XXX: define quantity/fix params
        # TODO: making the function take in parameters allow us to test more easily and separately from MarketState (so we can isolate which class has a problem)
        # XXX: should return a result for each iteration of this (so we can debug/see what happened in each iteration during backtest)

        coin_pair = (long_coin, short_coin)
        self.mstate.track_spread_portfolio(coin_pair)
        
        beta = self.mstate.betas_dict[coin_pair][-1]
        balance = 10000
        
        quantity_long = 250 / self.mstate.current_price(long_coin)
        quantity_short = 250 * beta / self.mstate.current_price(short_coin)
        
        while self.mstate.row < len(self.mstate.coin_dfs[long_coin]):
        # Define all variables using MarketState
            self.mstate.update()
            # check if we should buy or sell
            if (self.place_order_condition(self.mstate.current_spread(coin_pair),
                                         self.mstate.spread_upper_bollinger_band(coin_pair),
                                         self.mstate.spread_lower_bollinger_band(coin_pair)) and not self.check_open_orders()):
                self.place_limit_buy(long_coin, quantity_long)
                self.place_limit_sell(short_coin, quantity_short)
                self.current_positions_value(long_coin, short_coin, quantity_long, quantity_short)
                #start timer
                timestamp = int(time.time() * 1000)

                # monitor when to sell
            if (self.check_open_orders()):
                #check if price is at or below hard stop loss
                if (-50 >= self.initial_order_value - self.current_positions_value(long_coin, short_coin, quantity_long, quantity_short)):
                    #sell at hard stop loss
                    self.close_limit_buy(long_coin, quantity_long)
                    self.close_limit_sell(short_coin, quantity_short)
                    continue
                #check if orders are at take profit price
                if (self.mstate.current_price(long_coin) >= self.take_profit_long_price(long_coin, timestamp, coin_pair) or self.mstate.current_price(short_coin) <= self.take_profit_short_price(short_coin, timestamp, coin_pair)):
                    self.close_limit_buy(long_coin, quantity_long)
                    self.close_limit_sell(short_coin, quantity_short)
                    continue

from exchange_setup import establish_connection
client = establish_connection(True)
execute = Execution(client)
execute.main("FORTHUSD", "ZENUSD" )

import matplotlib.pyplot as plt
import numpy as np

spread = execute.plot_spread()
bband = execute.plot_boll_bands()

mean_values, stdev_values = zip(*bband[('FORTHUSD', 'ZENUSD')])

upper_bound = [mean + 2 * stdev for mean, stdev in zip(mean_values, stdev_values)]
lower_bound = [mean - 2 * stdev for mean, stdev in zip(mean_values, stdev_values)]

# Plotting
plt.figure(figsize=(10, 6))

# Plot mean values
#plt.plot(mean_values, label='Mean', marker='.')

plt.plot(spread[('FORTHUSD', 'ZENUSD')], label='Spread', marker='.')
# Plot mean +- 2 * stdev
plt.plot(upper_bound, label='Upper Bollinger', marker='.')
plt.plot(lower_bound, label='Lower Bollinger', marker='.')

# Add labels and title
plt.xlabel('Data Point Index')
plt.ylabel('Values')
plt.title('Mean and Bollinger Bands for (FORTHUSD, ZENUSD)')
plt.legend()

# Change range of x-vals
plt.xlim(2500, len(spread))

# Show the plot
plt.show()
