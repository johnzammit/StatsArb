from binance import Client
import json
import datetime
import math
from algo.datamodel import *


# TODO: this class is an instance of the market at time t

# TODO: make the MarketState class call the client only once to get the info it needs
class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """

    def __init__(self, window_size: int, client: Client):
        self.client = client
        self.window_size = window_size

    # total USD value of all coins in exchange that we are holding
    def portfolio_balance(self) -> float:
        # need to all get_asset_balance and multiply by market price of the coin-USDT pair
        balances = self.client.get_account()
        ticker_prices = self.client.get_all_tickers()

        total_balance = 0
        for b in balances:
            asset_balance = Balance(**b)
            ticker_usdt = asset_balance.asset + 'USDT'
            # remark: assume all pairs have a USDT conversion
            assert (ticker_usdt in ticker_prices)

            qty = float(asset_balance.free) + float(asset_balance.locked)
            total_balance += qty * ticker_prices[ticker_usdt]

        return total_balance

    def hard_stop_loss(self) -> float:
        # this will move up/down as we our portfolio increases/decreases in value,
        #   do we want to set an absolute cutoff to limit exposure or are we fine with increased exposure we our portfolio grows?
        return 0.005 * self.portfolio_balance()

    def current_price(self, coin: str) -> float:
        # TODO: do we want last traded price, best bid price, best ask price, avg of bid-ask spread, avg_price, or what?
        pass

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
