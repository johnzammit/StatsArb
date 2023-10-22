## TO DO:

##Initialize price and other variables from API
##Calculate bollinger bands and moving averages
##Create buy and sell functions
##price = bianace.get_price('BTCUSDT')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManage
import json
import datetime
import math



class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """
    def __init__(self, windowSize: int):
        pass
    
    # total USD value of all coins in exchange that we are holding
    def portfolio_balance(self) -> float:
        pass

    def hard_stop_loss(self) -> float:
        return 0.005 * self.portfolio_balance()
    
    def current_price(self, coin: str) -> float:
        # call binance.get_recent_trades
        pass
    def derivative_of_spread() -> float:
        # return the derivative of the spread price (slope of the spread)
        pass

    def current_spread(self, coin1, coin2) -> float:
        return float(self.current_price(coin1)) - float(self.current_price(coin2))
        

    def spread_moving_avg(self, coin1, coin2) -> float:
        pass

    def spread_upper_bollinger_band(self, coin1, coin2) -> float:
        pass
    
    def spread_lower_bollinger_band(self, coin1, coin2) -> float:
        pass

    
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
    async def update_limit_sell(self, short_coin, take_profit_price, cancelReplaceMode, cancelOrderId, timeInForce, quantity: float, price: float):
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
    


    def main(self, market: MarketState):
        #Define all variables using MarketState
    
        # check if we should buy or sell
        if (self.place_order_condition(spread, upper_bollinger_band_price, lower_bollinger_band_price)):
            self.place_limit_buy(long_coin, price, quantity, stopPrice)
            self.place_limit_sell(symbol, price, quantity, stopPrice)

            #start timer
            timestamp = int(time.time() * 1000)

            # monitor when to sell
            while (self.check_open_orders()):
                #update variables using MarketState


                #check if price is at or below hard stop loss
                if (MarketState.current_price(long_coin) <= MarketState.hard_stop_loss(long_coin) or MarketState.current_price(short_coin) >= MarketState.hard_stop_loss(short_coin)):
                    #sell at hard stop loss
                    self.place_limit_buy(long_coin, price, quantity, stopPrice)
                    self.place_limit_sell(symbol, price, quantity, stopPrice)
                #update take profit price
                self.take_profit_long_price(long_coin, timestamp)
                self.take_profit_short_price(short_coin, timestamp)

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