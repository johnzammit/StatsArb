from binance import Client
import json
import datetime
import math
from algo.datamodel import *


class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """

    def __init__(self, client: Client = None, window_size: int = 1000):
        assert (client != None)
        self.client = client
        self.window_size = window_size  # TODO: define smallest time unit
        self.ticker_prices = {}  # key: symbol (str), value: price (float)
        self.time = None  # TODO: implement

        self.__fetch_prices()
        self.symbols = list(self.ticker_prices.keys())

    """
    Updates the MarketState by fetching the latest data from the exchange.
    This function should be called on every tick (as defined by the algorithm).
    Other functions in this class will rely on the internal states that this function updates,
    so this function should be called before any other functions in each time instance.
    """

    def update(self):
        self.__fetch_prices()

    """Private function that updates the prices within the MarketState class"""

    def __fetch_prices(self):
        # TODO: update time
        for t in self.client.get_all_tickers():
            symbol, price = t["symbol"], float(t["price"])
            self.ticker_prices[symbol] = price

    """Get the current price of a specific coin"""

    def current_price(self, coin: str) -> float:
        return self.ticker_prices[coin]

    """Total USD value of all coins in exchange that we are holding"""

    def portfolio_balance(self) -> float:
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
        return 0.005 * self.portfolio_balance()

    def derivative_of_spread(self) -> float:
        # return the derivative of the spread price (slope of the spread)
        pass

    def current_spread(self, coin1, coin2) -> float:
        return float(self.current_price(coin1)) - float(self.current_price(coin2))
        pass

    def spread_moving_avg(self, coin1, coin2) -> float:
        # Get Rolling Window Price Change Statistics
        # GET /api/v3/ticker
        pass

    def spread_upper_bollinger_band(self, coin1, coin2) -> float:
        pass

    def spread_lower_bollinger_band(self, coin1, coin2) -> float:
        pass