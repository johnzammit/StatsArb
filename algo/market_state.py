import statistics
import time
from collections import deque
from typing import Callable, Any

from binance import Client

from algo.datamodel import *


# TODO: import system time and figure out how to keep track of time based on different input time units
# TODO: handle/prevent rate limits

class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """

    def __init__(self, client: Client = None, window_size: int = 1000,
                 kline_interval: str = Client.KLINE_INTERVAL_1MINUTE):
        assert (client != None and window_size > 0)

        # TODO: track coins and allow updating beta
        self.client = client

        self.ticker_prices = {}  # key: symbol (str), value: price (float)

        # we use milliseconds to keep track of the internal clock as that is what Binance uses for its servertime
        # self.time_unit =
        # if time_unit == "seconds":
        #     self.time_increment = 1000

        self.kline_interval = kline_interval  # smallest kline time interval is 1 minute

        self.__update_time()

        self.__fetch_prices()
        self.symbols = list(self.ticker_prices.keys())

        # TODO: handle window_size > 1000 (current window size limit on Binance API is 1000)
        self.window_size = window_size  # TODO: allow different window_size and time unit for different pairs?
        self.portfolios = dict()  # key: (coin1, coin2), value: object with beta, prices, bollinger bands
        self.bollinger_bands = dict() # key: (coin1, coin2)

    def update(self):
        """
        Updates the MarketState by fetching the latest data from the exchange.
        This function should be called on every tick (as defined by the algorithm).
        Other functions in this class will rely on the internal states that this function updates,
        so this function should be called before any other functions in each time instance.
        """
        self.__update_time()
        self.__fetch_prices()
        self.__update_all_windows()
        self.__update_bollinger_bands()

    def __update_time(self):
        # update internal clock to current time in milliseconds since epoch
        self.current_time = int(time.time() * 1000)

    def __fetch_prices(self):
        """Private function that updates the prices within the MarketState class"""
        for t in self.client.get_all_tickers():
            symbol, price = t["symbol"], float(t["price"])
            self.ticker_prices[symbol] = price

    def __calculate_spread(self, price1: float, price2: float, beta: float) -> float:
        return price1 - price2 * beta

    def __calculate_kline_price_avg(self, k: Kline):
        return (float(k.low) + float(k.high)) / 2

    def __kline_generator(self, coin: str, kline_interval: str, start_str: str = None,
                          function: Callable[[Kline], Any] = None):
        """
        Generator that applies a lambda function on each kline.
        This generator yields kline in ascending order of start time
        (This is a higher-order function)
        """
        if function is None:
            function = lambda x: self.__calculate_kline_price_avg(x)

        for k in self.client.get_historical_klines_generator(coin, kline_interval, start_str):
            kline = Kline(*k)
            yield function(kline)

    def __calculate_beta(self, p1: float, p2: float):
        return p1 / p2

    def __fill_window(self, coin_pair: PairPortfolio, window_size: int):
        """
        Fill the window with historical data

        Limits for client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=1000)
        - 15 mins and less time intervals => max 1000 klines
        - 30 minute time intervals => max 849 klines
        - 1 hour time intervals => max 425 klines
        - 2 hour time intervals => max 213 klines
        - half the number of klines for each doubling of the time interval size
        """

        # derive a formula for when we need to use historical fill

        # TODO: create function to calculate exact UTC startTime to get the desired window_size?
        # XXX: should we attach the price's time to the window?
        self.portfolios[coin_pair] = deque([])
        count = 0  # TODO: optimize this
        for price1, price2 in zip(self.__kline_generator(coin_pair.coin1, self.kline_interval),
                                  self.__kline_generator(coin_pair.coin2, self.kline_interval)):
            self.portfolios[coin_pair].append(price1 - price2 * coin_pair.beta)
            if count > window_size:
                self.portfolios[coin_pair].popleft()

        assert (len(self.portfolios[coin_pair]) > 0)

    def __calculate_initial_band(self, coin_pair: PairPortfolio):
        # TODO: optimize and handle potential overflow (checkout Numpy?), watchout for precision
        window_mean = statistics.fmean(self.portfolios[coin_pair])
        window_stdev = statistics.stdev(self.portfolios[coin_pair],
                                        window_mean)  # sample standard deviation
        self.bollinger_bands = BollingerBand(mean=window_mean, stdev=window_stdev)

    def __update_all_windows(self):
        """Update the window with the current period"""
        # TODO: combine with Jimmy's OLS
        # TODO: clarify whether to update by calling Binance and getting a new window orr just update using latest price (potential synchronization issue)
        for p in self.portfolios:
            self.portfolios[p].popleft()
            self.portfolios[p].append(self.current_spread(p.coin1, p.coin2, p.beta))

    def __update_bollinger_bands(self):
        pass

    def track_spread_portfolio(self, coin1_symbol: str, coin2_symbol: str) -> bool:
        """Compute beta internally, tracking a spread portfolio for a pair of coins. Returns true if successful, false otherwise.
        Formula: spread = coin1 - coin2 * beta

        Example:
            Suppose that beta = 7.4
            Then let's say you want to buy this spread, and you want to do 10 shares of coin1
            Then you buy 10 shares of coin1, and you short 74 shares of coin2

        XXX: potential issue with fractional shares due to the exchange's price/qty filters (need to verify)
        """
        # TODO: change params to coin1, coin2, beta
        if coin_pair not in self.portfolios:
            self.__fill_window(coin_pair, self.window_size)  # use default window_size for now
            self.__calculate_initial_band(coin_pair)
            self.pairs.add((coin_pair.coin1, coin_pair.coin2))
            return True
        else:
            # if coin_pair already exists? just refill the window? return true orr false?
            # allow updating window size?
            return False

    def track_spread_portfolio(self, coin_pair: PairPortfolio) -> bool:
        """Begin tracking a spread portfolio for a pair of coins. Returns true if successful, false otherwise.

        Formula: spread = coin1 - coin2 * beta

        Example:
            Suppose that beta = 7.4
            Then let's say you want to buy this spread, and you want to do 10 shares of coin1
            Then you buy 10 shares of coin1, and you short 74 shares of coin2

        XXX: potential issue with fractional shares due to the exchange's price/qty filters (need to verify)
        """
        # TODO: change params to coin1, coin2, beta
        if coin_pair not in self.portfolios:
            self.__fill_window(coin_pair, self.window_size)  # use default window_size for now
            self.__calculate_initial_band(coin_pair)
            self.pairs.add((coin_pair.coin1, coin_pair.coin2))
            return True
        else:
            # if coin_pair already exists? just refill the window? return true orr false?
            # allow updating window size?
            return False

    def untrack_spread_portfolio(self, coin_pair: PairPortfolio):
        """Stop tracking a spread portfolio for a pair of coins. Returns true if successful, false otherwise."""
        # TODO: change params to coin1, coin2
        if coin_pair in self.portfolios:
            del self.portfolios[coin_pair]
            return True
        else:
            return False

    def update_beta(self, coin1: str, coin2: str, beta: float):
        pass

    def get_all_portfolios(self) -> list[PairPortfolio]:
        return list(self.portfolios.keys())

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
            f"Excluded the following coins from portfolio balance calculations (could not find conversion to USD): {excluded_coins}")

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

    def current_spread(self, coin1: str, coin2: str) -> float:
        # TODO: use internal beta and remove beta as param
        return self.__calculate_spread(self.current_price(coin1), self.current_price(coin2), beta)

    def spread_moving_avg(self, coin1, coin2) -> float:
        # middle Bollinger Band
        # TODO: make more efficient by using sliding window technique (ensure no prrecision issue)
        return self.bollinger_bands[(coin1, coin2)].mean

    def spread_upper_bollinger_band(self, coin1, coin2) -> float:
        return self.bollinger_bands[(coin1, coin2)].mean + 2 * self.bollinger_bands[(coin1, coin2)].stdev

    def spread_lower_bollinger_band(self, coin1, coin2) -> float:
        return self.bollinger_bands[(coin1, coin2)].mean - 2 * self.bollinger_bands[(coin1, coin2)].stdev

# TODO: expand window of data after we have a position within a portfolio

# TODO: define and handle which coin is coin1 or coin2 (order  matters?)