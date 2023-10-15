## TO DO:

##Initialize price and other variables from API
##Calculate bollinger bands and moving averages
##Create buy and sell functions
##price = bianace.get_price('BTCUSDT')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
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
        pass

    def spread_moving_avg(self, coin1, coin2) -> float:
        pass

    def spread_upper_bollinger_band(self, coin1, coin2) -> float:
        pass
    
    def spread_lower_bollinger_band(self, coin1, coin2) -> float:
        pass

    
"""
Execution will using MarketState data to know when to execute a trade.
"""
class Execution():
    def __init__(self, formula):
        """"Formula is a tuple containing coins and their weights (ticker, weight)"""
        # need to take in a formula
        pass
    
    #checks if the spread is above the upper bollinger band or below the lower bollinger band
    async def place_order_condition(self, spread: float, upper_bollinger_band_price: float, lower_bollinger_band_price: float,  higher_coin: str, lower_coin: str) -> bool:
        return spread >= upper_bollinger_band_price or spread <= lower_bollinger_band_price 

    async def sell_order_postition():
        pass
    #tell binance to buy at a certain price
    async def place_limit_buy(self, coin, price):
        pass
    
    #tell binance to sell at a certain price
    async def place_limit_sell(self, coin, price):
        pass

    #cancel unfilled limit sell orders and place new ones at updated price
    async def update_limit_sell(lower_coin, take_profit_price):
        pass
    #check if orders are still open or not before placing new orders
    async def check_order_status(self):
        pass
    #calculate time weighted take profit price
    async def take_profit_price(self, coin: float) -> float:
        decrease_rate = 0.055
        target_price = MarketState.spread_moving_avg() - (decrease_rate * t) + MarketState.derivative_of_spread() % MarketState.current_price(coin) / 100
        ## Need to add accelerator with the derivative of spread

        return target_price
    


    def main(self, market: MarketState):
        # check if we should buy or sell
        if (place_order_condition()):
            place_limit_buy(higher_coin, price)
            place_limit_sell(lower_coin, price)
            #start timer
            time = 0
            # monitor when to sell
            while (value of all positions > hard_stop_loss()):
                #update take profit price
                take_profit_price()

                #place/update limit sell order at take profit price
                if (no limit sell orders open):
                    place_limit_sell(lower_coin, take_profit_price)
                    place_limit_sell(higher_coin, take_profit_price)
                else:
                    update_limit_sell(lower_coin, take_profit_price)
                    update_limit_sell(higher_coin, take_profit_price)

                #check if orders are still open
                if check_order_status():
                    continue
                else:
                    break
            #sell at hard stop loss
            place_limit_sell(lower_coin, price)
            place_limit_sell(higher_coin, price)
                



          
        pass

if __name__ == '__main__':
    main()