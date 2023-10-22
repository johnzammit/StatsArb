from binance import Client
import json
import datetime
import math
from algo.datamodel import *
from collections import deque
import time
# TODO: import system time and figure out how to keep track of time based on different input time units

class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """

    def __init__(self, client: Client = None, window_size: int = 1000, time_unit: str = "seconds"):
        assert (client != None and window_size > 0)

        self.client = client
        self.window_size = window_size  # TODO: define smallest time unit - use seconds or nanoseconds?
        self.ticker_prices = {}  # key: symbol (str), value: price (float)

        # we use milliseconds to keep track of the internal clock as that is what Binance uses for its servertime
        self.time_unit = time_unit
        if time_unit == "seconds":
            self.time_increment = 1000

        self.__update_time()

        self.__fetch_prices()
        self.symbols = list(self.ticker_prices.keys())

        self.window = deque([])  # double-ended queue for O(1) pop from front and O(1) insert from back of queue
        self.__fill_window()


    def update(self):
        """
        Updates the MarketState by fetching the latest data from the exchange.
        This function should be called on every tick (as defined by the algorithm).
        Other functions in this class will rely on the internal states that this function updates,
        so this function should be called before any other functions in each time instance.
        """
        self.__update_time()
        self.__fetch_prices()
        self.__update_window()

    def __update_time(self):
        # update internal clock to current time in milliseconds since epoch
        self.current_time = int(time.time() * 1000)

    def __fetch_prices(self):
        """Private function that updates the prices within the MarketState class"""
        # TODO: update time
        for t in self.client.get_all_tickers():
            symbol, price = t["symbol"], float(t["price"])
            self.ticker_prices[symbol] = price

    def __fill_window(self):
        """Fill the window with historical data"""
        # TODO: implement
        pass

    def __update_window(self):
        """Update the window with the current period"""
        # TODO: implement
        pass

    def current_price(self, coin: str) -> float:
        """Get the current price of a specific coin"""
        return self.ticker_prices[coin]

    def portfolio_balance(self) -> float:
        """Total USD value of all coins in exchange that we are holding"""
        # need to all get_asset_balance and multiply by market price of the coin-USDT pair
        # TODO: update balance inside the update function? or separately?
        balances = [Balance(**b) for b in self.client.get_account()["balances"]]
        total_balance = 0
        excluded_coins = []
        for b in balances:
            if b.asset in ("USDT", "BUSD"):
                # stablecoin values reflect real value of USD
                total_balance += b.free + b.locked
            else:
                # need to convert this cryptocurrency to USDT to get price in USD
                ticker_usdt = b.asset + 'USDT'  # remark: assume all pairs have a USDT conversion

                if not (ticker_usdt in self.ticker_prices):
                    # coins excluded from portfolio balance (no direct conversion to USD available)
                    # TODO: find a conversion from these coins to BTC to USDT (maybe try BUSD)
                    excluded_coins.append(b.asset)
                    continue

                qty = b.free + b.locked
                total_balance += qty * self.ticker_prices[ticker_usdt]

        print(
            f"Excluded the following coins from portfolio balance calulations (could not find conversion to USD): {excluded_coins}")

        return total_balance

    def hard_stop_loss(self) -> float:
        # this will move up/down as we our portfolio increases/decreases in value,
        #   do we want to set an absolute cutoff to limit exposure or are we fine with increased exposure we our portfolio grows?
        # TODO: change to John's new stop loss formula?
        return 0.005 * self.portfolio_balance()

    def derivative_of_spread(self) -> float:
        # return the derivative of the spread price (slope of the spread)
        # TODO: clarify formula: (change in price of spread) / (time or ??)
        # TODO: internal timer, 1 second for now, but make it adjustable
        pass

    def current_spread(self, coin1: str, coin2: str, beta: float) -> float:
        """
        Formula: spread = coin1 - coin2 * beta

        Example:
            Suppose that beta = 7.4
            Then let's say you want to buy this spread, and you want to do 10 shares of coin1
            Then you buy 10 shares of coin1, and you short 74 shares of coin2
        """
        # XXX: potential issue with fractional shares due to the exchange's price/qty filters (need to verify)
        return self.current_price(coin1) - self.current_price(coin2) * beta

    def spread_moving_avg(self, coin1, coin2) -> float:
        # Get Rolling Window Price Change Statistics
        # GET /api/v3/ticker
        # TODO: implement
        pass

    def spread_upper_bollinger_band(self, coin1, coin2) -> float:
        # TODO: implement
        pass

    def spread_lower_bollinger_band(self, coin1, coin2) -> float:
        # TODO: implement
        pass
