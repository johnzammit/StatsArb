import statistics
import time
from collections import deque
from typing import Callable, Any, Deque

from binance import Client

from datamodel import *
from datamodel import BollingerBand

import statsmodels.api as sm
import pandas as pd
import numpy as np
import math

class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """

    def __init__(self, client: Client = None, window_size: int = 1000,
                 kline_interval: str = Client.KLINE_INTERVAL_1MINUTE):
        assert (client is not None and window_size > 0)

        # Adding this
        self.pairs = set()
        self.row = 30 # Start after one month
        self.coin_dfs = {}

        self.client = client

        self.ticker_prices = {}  # key: symbol (str), value: latest price (float)

        # Binance uses milliseconds for the 'time' in the response
        self.kline_interval = kline_interval  # smallest kline time interval is 1 minute
        self.__update_time()

        self.__fetch_prices() # get price of ALL tickers (may remove this if not needed)
        self.symbols = set(self.ticker_prices.keys()) # list of all valid symbols

        # TODO: handle window_size > 1000 (current window size limit per request on Binance API is 1000)
        self.window_size = window_size  # TODO: allow different window_size and time unit for different pairs?

        self.prices_dict: Dict[str, Deque[float]] = {} # Might not really need this, we really just need log returns
        # TODO: keep track of only latest price instead of whole list

        self.log_returns_dict: Dict[str, Deque[float]] = {}

        self.bollinger_bands: Dict[tuple[str, str], BollingerBand] = {}

        # The objects below are unique to each coin pair
        # TODO: use frozensets as key instead of tuple (useful for more than 2 pairs, since order shouldn't matter)
        self.betas_dict: Dict[tuple[str, str], Deque[float]] = {}
        self.spreads_dict: Dict[tuple[str, str], Deque[float]] = {}

    def update(self):
        """
        Updates the MarketState by fetching the latest data from the exchange.
        This function should be called on every tick (as defined by the algorithm).
        Other functions in this class will rely on the internal states that this function updates,
        so this function should be called before any other functions in each time instance.
        """
        self.__update_time() # can use this to check for time drift or keep a timer
        self.__fetch_prices() # updates the prices, log returns of tracked coins
        self.__update_all_windows() # updates betas, spreads, and Bollinger bands of coin pairs

        self.row += 1

    def __update_time(self):
        # update internal clock to current time in milliseconds since epoch
        self.current_time = int(time.time() * 1000)

    # def __fetch_prices(self):
    #     """Private function that updates the prices within the MarketState class"""
    #     for t in self.client.get_all_tickers():
    #         # Update the price of all coins
    #         # TODO: remove unnecessary coins if not used
    #         symbol, price = t["symbol"], float(t["price"])
    #         self.ticker_prices[symbol] = price

    #         # Add prices and log returns of tracked coins
    #         if symbol in self.prices_dict:
    #             self.prices_dict[symbol].append(price)
    #             self.log_returns_dict[symbol].append(math.log(price) - self.log_returns_dict[symbol][-1])

    #             # shrink window if window length is over limit
    #             if len(self.prices_dict[symbol]) > self.window_size:
    #                 # TODO: allow different window size for each coin; how do we handle multiple pairs with different window sizes?
    #                 self.prices_dict[symbol].popleft()
    #                 self.log_returns_dict[symbol].popleft()

    def __fetch_prices(self):
        for pair in self.pairs:
            for coin in pair:
                next_price = self.coin_dfs[coin].iloc[self.row]['close']
                
                self.prices_dict[coin].append(next_price)
                self.log_returns_dict[coin].append(math.log(next_price) - self.log_returns_dict[coin][-1])

                # shrink window if window length is over limit
                if len(self.prices_dict[coin]) > self.window_size:
                    # TODO: allow different window size for each coin; how do we handle multiple pairs with different window sizes?
                    self.prices_dict[coin].popleft()
                    self.log_returns_dict[coin].popleft()

    def __calculate_spread(self, coin_pair: tuple[str, str]) -> float:
        return self.log_returns_dict[coin_pair[0]][-1] - self.log_returns_dict[coin_pair[1]][-1] * self.betas_dict[coin_pair][-1]

    def __calculate_spread_list(self, coin_pair: tuple[str, str]) -> float:
        # print("log returns list" + str(self.log_returns_dict[coin_pair[0]]))
        # print("log returns list" + str(self.log_returns_dict[coin_pair[1]]))

        product_list = [(self.betas_dict[coin_pair])[0] * x for x in self.log_returns_dict[coin_pair[1]]]
        element_wise_sub_list = [a - b for a, b in zip(self.log_returns_dict[coin_pair[0]], product_list)]
        return deque(element_wise_sub_list)

    def __calculate_bollinger_band(self, coin_pair: tuple[str, str]):
        # print("spread list")
        # # print(self.spreads_dict[coin_pair])
        # print("---------------------------")

        window_mean = statistics.fmean(self.spreads_dict[coin_pair])
        window_stdev = statistics.stdev(self.spreads_dict[coin_pair],
                                        window_mean)  # standard deviation
        self.bollinger_bands[coin_pair] = BollingerBand(mean=window_mean, stdev=window_stdev)

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

    def get_data(self, coin, kline_interval, start, end):
        klines = self.client.get_historical_klines(coin, kline_interval, start, end)
        coin_df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 
                                                'volume', 'close_time', 'quote_av', 'trades', 
                                                'tb_base_av', 'tb_quote_av', 'ignore' ])
        coin_df['timestamp'] = pd.to_datetime(coin_df['timestamp'], unit='ms')
        coin_df.set_index('timestamp', inplace=True)
        coin_df['close'] = coin_df['close'].astype(float)
        return coin_df

    def __fill_window(self, coin_pair: tuple[str, str], window_size: int):
        """
        Fill the window with historical data

        Limits for client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=1000)
        - 15 mins and less time intervals => max 1000 klines
        - 30 minute time intervals => max 849 klines
        - 1 hour time intervals => max 425 klines
        - 2 hour time intervals => max 213 klines
        - half the number of klines for each doubling of the time interval size
        """

        # TODO: derive a formula for when we need to use historical fill
        # TODO: use window_size to determine how much data to get (or pop after certain counts)

        # TODO: optimize; we can use the `timeit` module to measure the running time

        # TODO: figure out what to do if two pairs have the same coin (use existing data?)

        # Add pair to set
        self.pairs.add(coin_pair)

        # Get 1-year historical dfs
        self.coin_dfs[coin_pair[0]] = self.get_data(coin_pair[0], self.kline_interval, "1 Oct, 2022", "2 Oct, 2022")

        print("Dataframe: ")
        print(self.coin_dfs[coin_pair[0]])

        self.coin_dfs[coin_pair[1]] = self.get_data(coin_pair[1], self.kline_interval, "1 Oct, 2022", "2 Oct, 2022")

        # Calculations for each individual coin in the portfolio
        # prices_1 = self.__kline_generator(coin_pair[0], self.kline_interval)
        # prices_2 = self.__kline_generator(coin_pair[1], self.kline_interval)

        prices_1 = list((self.coin_dfs[coin_pair[0]])[:30]['close'])
        prices_2 = list((self.coin_dfs[coin_pair[1]])[:30]['close'])

        # print("Length of prices_1 is: ", str(len(prices_1)))
        # print("Length of prices_2 is: ", str(len(prices_2)))
        log_returns_1 = np.diff(np.log(np.array(prices_1)))
        log_returns_2 = np.diff(np.log(np.array(prices_2)))

        # -- Portfolio specific calculations --

        # Calculate betas
        S1 = log_returns_1.copy()
        # print("Length of log returns is: ", str(len(log_returns_1)))
        S1 = sm.add_constant(S1)
        results = sm.OLS(log_returns_2, S1).fit()
        # print(str(results.params[0]) + str(results.params[1]))
        beta = results.params[1]

        self.prices_dict[coin_pair[0]] = deque(prices_1)
        self.prices_dict[coin_pair[1]] = deque(prices_2)

        self.log_returns_dict[coin_pair[0]] = deque(log_returns_1)
        self.log_returns_dict[coin_pair[1]] = deque(log_returns_2)

        self.betas_dict[coin_pair] = deque([beta])

        # Calculate spread of portfolio and initial Bollinger Band
        # self.__calculate_spread(coin_pair)
        self.spreads_dict[coin_pair]= (self.__calculate_spread_list(coin_pair))
        self.__calculate_bollinger_band(coin_pair)



    def __update_all_windows(self):
        # """Update the window with the current period"""
        """This should be run after new prices are fetched for each coin.
        We will redo the regression for each pair, and then append the new beta for each pair.
        """
        # TODO: clarify whether to update by calling Binance and getting a new window orr just update using latest price (potential synchronization issue)
        coin_pair: tuple[str, str]
        for coin_pair in self.betas_dict:
            # calculate betas
            S1 = list(self.log_returns_dict[coin_pair[0]].copy())
            S1 = sm.add_constant(S1)
            S2 = list(self.log_returns_dict[coin_pair[1]].copy())
            results = sm.OLS(S2, S1).fit()
            new_beta = results.params[1]
            self.betas_dict[coin_pair].append(new_beta)

            # TODO: use sliding window?, can probably make this constant time
            # calculate spread for the portfolio
            self.spreads_dict[coin_pair].append(self.__calculate_spread(coin_pair))
    
            self.__calculate_bollinger_band(coin_pair) # update Bollinger Band




    def track_spread_portfolio(self, coin_pair: tuple[str, str]) -> bool:
        """Begin tracking a spread portfolio for a pair of coins. Returns true if successful, false otherwise.

        Formula: spread = coin1 - coin2 * beta

        Example:
            Suppose that beta = 7.4
            Then let's say you want to buy this spread, and you want to do 10 shares of coin1
            Then you buy 10 shares of coin1, and you short 74 shares of coin2

        XXX: potential issue with fractional shares due to the exchange's price/qty filters (need to verify)
        """
        if coin_pair not in self.pairs:
            self.__fill_window(coin_pair, self.window_size)  # use default window_size for now
            return True
        else:
            # if coin_pair already exists? just refill the window? return true orr false?
            # allow updating window size?
            return False

    def untrack_spread_portfolio(self, coin_pair: tuple[str, str]):
        """Stop tracking a spread portfolio for a pair of coins. Returns true if successful, false otherwise."""
        if coin_pair in self.prices_dict:
            # TODO: check if other pairs have this coin since prices_dict and log_returns dict have only one coin as key
            # del self.prices_dict[coin_pair[0]]
            # del self.prices_dict[coin_pair[1]]
            # del self.log_returns_dict[coin_pair[0]]
            # del self.log_returns_dict[coin_pair[1]]

            # the variables below are specific to each pair
            del self.betas_dict[coin_pair]
            del self.bollinger_bands[coin_pair]
            del self.spreads_dict[coin_pair]
            return True
        else:
            return False

    def get_all_portfolios(self) -> list[tuple[str, str]]:
        return list(self.spreads_dict.keys())

    def current_price(self, coin: str) -> float:
        """Get the current price of a specific coin"""
        # return self.ticker_prices[coin]
        curr_price = self.coin_dfs[coin].iloc[self.row]['close']
        return curr_price

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

    def derivative_of_spread(self, coin_pair: tuple[str, str]) -> float:
        # return the derivative of the spread price (slope of the spread)
        # dS/dt = (spread_{t} - spread_{t-1}) / (t - (t-1)) = (spread_{t} - spread_{t-1})
        # Assuming we use the spread at the current(latest) time and compare it to the spread of the last time we calculated it
        # XXX: might need to change this to make it based on timestamp or if we skip some periods???
        # TODO: clarify formula: (change in price of spread) / (time or ??)
        # TODO: internal timer, 1 second for now, but make it adjustable
        assert(coin_pair in self.spreads_dict and len(self.spreads_dict[coin_pair]) > 0)

        return (self.spreads_dict[coin_pair][-1] - self.spreads_dict[coin_pair][-2]) / (1 - 0) # in case we change it

    def current_spread(self, coin_pair: tuple[str, str]) -> float:
        assert(coin_pair in self.spreads_dict and len(self.spreads_dict[coin_pair]) > 0)
        return self.spreads_dict[coin_pair][-1]

    def spread_moving_avg(self, coin_pair: tuple[str, str]) -> float:
        # middle Bollinger Band
        # TODO: make more efficient by using sliding window technique (ensure no precision issue)
        # TODO: handle case when pair does not exist, should we raise error?
        return self.bollinger_bands[coin_pair].mean

    def spread_upper_bollinger_band(self, coin_pair: tuple[str, str]) -> float:
        return self.bollinger_bands[coin_pair].mean + 2 * self.bollinger_bands[coin_pair].stdev

    def spread_lower_bollinger_band(self, coin_pair: tuple[str, str]) -> float:
        return self.bollinger_bands[coin_pair].mean - 2 * self.bollinger_bands[coin_pair].stdev

    def beta(self, coin_pair: tuple[str, str]) -> list[float]:
        return list(self.betas_dict[coin_pair])
# TODO: expand window of data after we have a position within a portfolio
# TODO: define and handle which coin is coin1 or coin2 (order  matters?)
# TODO: optimize and handle potential overflow (checkout Numpy?), watchout for precision
# TODO: import system time and figure out how to keep track of time based on different input time units
# TODO: handle/prevent rate limits
# TODO: ensure coin pair tuple is always sorted lexicographically