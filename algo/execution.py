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
    def __init__(self, formula, api_key, secret_key, api_url):
        """"Formula is a tuple containing coins and their weights (ticker, weight)"""
        # need to take in a formula
        self.api_url = "https://api.binance.us"
        self.api_key = "YOUR_API_KEY"
        self.secret_key = "YOUR_SECRET_KEY"

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
    async def place_limit_buy(self, symbol: str, price: float, quantity: float, stopPrice: float): 
        uri_path = "/api/v3/order"
        data = {
            "symbol": symbol,
            "side": "BUY",
            "type": "LIMIT",
            "price": price,
            "quantity": quantity,
            "timeinforce": "GTC", #good till cancelled
            "timestamp": int(round(time.time() * 1000))
        }

        result = self.binanceus_request(uri_path, data, self.api_key, self.secret_key)
        print("POST {}: {}".format(uri_path, result))
    

    #tell binance to sell at a certain price
    async def place_limit_sell(self, symbol: str, price: float, quantity: float, stopPrice: float):
        uri_path = "/api/v3/order"
        data = {
            "symbol": symbol, #ex. BTCUSDT
            "side": "SELL",
            "type": "LIMIT",
            "price": price,
            "quantity": quantity,
            "stopPrice": stopPrice, #price at which limit order is triggered
            "timeinforce": "GTC", #good till cancelled
            "timestamp": int(round(time.time() * 1000))
        }

        result = self.binanceus_request(uri_path, data, self.api_key, self.secret_key)
        print("POST {}: {}".format(uri_path, result))


    #cancel unfilled limit sell orders and place new ones at updated price
    async def update_limit_sell(self, short_coin: str, cancelReplaceMode, cancelOrderId, timeInForce, quantity: float, price: float):
        uri_path = "/api/v3/order/cancelReplace"
        data =  {
            "timestamp": int(round(time.time() * 1000)),
            "symbol":short_coin,
            "side": "SELL",
            "type": "LIMIT",
            "cancelReplaceMode":cancelReplaceMode,
            "cancelOrderId":cancelOrderId,
            "timeInForce":timeInForce,
            "quantity":quantity,
            "price":price
        }

        result = Execution.binanceus_request(uri_path, data, self.api_key, self.secret_key)
        print("POST {}: {}".format(uri_path, result))


    #check if orders are still open or not before placing new orders
    async def check_open_orders(self) -> bool:
        uri_path = "/api/v3/openOrders"
        data = {
            "timestamp": int(round(time.time() * 1000))
        }
        result = self.binanceus_request(uri_path, data, self.api_key, self.secret_key)
        response_data = result.json()
        # Check if there are open orders
        if len(response_data) > 0:
            return True
        else:
            return False
        
    async def open_positions_value(self) -> float:
        uri_path = "/api/v3/openOrders"
        data = {
            "timestamp": int(round(time.time() * 1000))
        }
        result = self.binanceus_request(uri_path, data, self.api_key, self.secret_key)
        open_orders = json.loads(result)

        total_position_value = 0.0
        for order in open_orders:
            price = float(order["price"])
            origQty = float(order["origQty"])
            position_value = price * origQty
            total_position_value += position_value
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

        # check if we should buy or sell
        if (self.place_order_condition(spread.estimate, spread.upper, spread.lower)):
            self.place_limit_buy(long_coin.symbol, long_coin.price, quantity, stopPrice)
            self.place_limit_sell(short_coin.symbol, short_coin.price, quantity, stopPrice)
            original_position_value = self.open_positions_value()

            #start timer
            timestamp = int(time.time() * 1000)

            # monitor when to sell
            while (self.check_open_orders()):
                #update variables using MarketState


                #check if price is at or below hard stop loss
                if (MarketState.hard_stop_loss() * -1 >= self.open_positions_value() - original_position_value):
                    #sell at hard stop loss
                    self.place_limit_buy(long_coin.symbol, long_coin.price, quantity, stopPrice)
                    self.place_limit_sell(short_coin.symbol, short_coin.price, quantity, stopPrice)

                #update take profit price
                long_take_profit= self.take_profit_long_price(long_coin, timestamp)
                short_take_profit = self.take_profit_short_price(short_coin, timestamp)

                #consider adding a time delay here

                #update limit sell order at take profit price
                self.update_limit_sell(long_coin, take_profit_price)
                self.update_limit_sell(short_coin, take_profit_price)

                #check if orders are still open
                if self.check_open_orders():
                    continue
                else:
                    break
            

    if __name__ == '__main__':
        main()
