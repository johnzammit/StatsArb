## TO DO:

##Initialize price and other variables from API
##Calculate bollinger bands and moving averages
##Create buy and sell functions
##price = bianace.get_price('BTCUSDT')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from market_state import MarketState

"""
Execution will using MarketState data to know when to execute a trade.
"""


class Executor:
    def __init__(self, client: Client, coin1: tuple[str, float], coin2: tuple[str, float]):
        # coin1 and coin2 are tuples containing (ticker, weight)
        self.coin1 = coin1
        self.coin2 = coin2
        self.client = client

    # checks if the spread is above the upper bollinger band or below the lower bollinger band
    async def place_order_condition(self, spread: float, upper_bollinger_band_price: float,
                                    lower_bollinger_band_price: float, higher_coin: str, lower_coin: str) -> bool:
        return spread >= upper_bollinger_band_price or spread <= lower_bollinger_band_price

    async def sell_order_position(self):
        pass

    # tell binance to buy at a certain price
    async def place_limit_buy(self, coin, price):
        pass

    # tell binance to sell at a certain price
    async def place_limit_sell(self, coin, price):
        pass

    # cancel unfilled limit sell orders and place new ones at updated price
    async def update_limit_sell(self, lower_coin, take_profit_price):
        pass

    # check if orders are still open or not before placing new orders
    async def check_order_status(self):
        # cur_orders = self.client.get_open_orders((self.coin1[0], self.coin2[0]))
        # return len(cur_order) == 0
        pass

    # calculate time weighted take profit price
    async def take_profit_price(self, coin: float) -> float:
        decrease_rate = 0.055
        target_price = MarketState.spread_moving_avg() - (
                    decrease_rate * t) + MarketState.derivative_of_spread() % MarketState.current_price(coin) / 100
        ## Need to add accelerator with the derivative of spread

        return target_price

    # TODO: either make this executor call the market every tick
    #  or use a while loop outside that, for every tick, gets the MarketState and calls executor.run
    #  and sends a response back to the exchange based on Executor.run()'s return val (this makes debugging easier)
    def run(self, market: MarketState):
        # check if we should buy or sell
        if (place_order_condition()):
            place_limit_buy(higher_coin, price)
            place_limit_sell(lower_coin, price)
            # start timer
            time = 0
            # monitor when to sell
            while (value of all positions > hard_stop_loss()):
                # update take profit price
                take_profit_price()

                # place/update limit sell order at take profit price
                if (no limit sell orders open):
                    place_limit_sell(lower_coin, take_profit_price)
                    place_limit_sell(higher_coin, take_profit_price)
                else:
                    update_limit_sell(lower_coin, take_profit_price)
                    update_limit_sell(higher_coin, take_profit_price)

                # check if orders are still open
                if check_order_status():
                    continue
                else:
                    break
            # sell at hard stop loss
            place_limit_sell(lower_coin, price)
            place_limit_sell(higher_coin, price)

        pass


if __name__ == '__main__':
    # TODO: input params from command line or code it in here
    # TODO: determine how to synchronize executor to market caller

    # TODO: use multithreading?
    executor1 = Executor( ('DOGEUSDT', 1), ('MASKUSDT', -1))
    executor2 = Executor( ('BNBUSDT', 1), ('DOGEUSDT', -1))

    pass