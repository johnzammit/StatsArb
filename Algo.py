## TO DO:

##Initialize price and other variables from API
##Calculate bollinger bands and moving averages
##Create buy and sell functions
##price = bianace.get_price('BTCUSDT')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManage
import json
import datetime

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
    
    def place_order_condition(self, spread: float, upper_bollinger_band_price: float, lower_bollinger_band_price: float,  higher_coin: str, lower_coin: str) -> bool:
        return spread >= upper_bollinger_band_price or spread <= lower_bollinger_band_price 

    def sell_order_postition():
        pass
    #tell binance to buy at a certain price
    def place_limit_buy(self, coin, price):
        pass
    
    #tell binance to se;; at a certain price
    def place_limit_sell(self, coin, price):
        pass

    #check if orders are still open or not before placing new orders
    def check_order_status(self):
        pass

    def take_profit_price(self, coin: float) -> float:
        return (mean_spread - (time * derivative_price)/sqrt(derivative_price))
    


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

                #place limit sell order at take profit price
                place_limit_sell(lower_coin, take_profit_price)
                place_limit_sell(higher_coin, take_profit_price)

                #check if orders are still open
                if check_order_status():
                    continue
                else:
                    break




          
        pass

if __name__ == '__main__':
    main()