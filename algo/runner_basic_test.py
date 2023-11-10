# https://stackoverflow.com/questions/52722864/python-periodic-timer-interrupt
# https://en.wikipedia.org/wiki/Clock_drift


# idea 1:
# - create a timer thread
# - make it interrupt and run the loop every however many seconds
# - somehow need to ensure that we are not interrupting program if it is executing order
# - ensure program runs fast enough?, overwise it may never execute

# idea 2:
# - create a loop that keeps updating itself and executes when possible
# - set a minimum delay between each loop iteration, such that if we finish updating/executing early
#   then we will still not update/execute until we have reached that minimum delay


# probably go with idea 2


'''
Modified functions:

MarketState:
- __fetch_prices
- __fill_window

Execution:
- functions making a request
'''



from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from market_state_basic_test import MarketState
from execution_backtest import Execution
from exchange_setup import establish_connection

def main():
    # TODO: add optional parameters for coins to trade on
    pairs_to_trade = [("ETHBTC", "BNBBTC"), ("DOGEBTC", "BTCUSDT")] # change this
    client = establish_connection()
    print(client.get_exchange_info())

    updates_to_coin_pairs = None # integration tester should update this variable somehow (use async or define API?)
    state = MarketState(client)

    for p in pairs_to_trade:
        state.track_spread_portfolio(p)

    executor = Execution(client)
    
    while True:
        # Listen for updates to coin list to trade
        updates_to_coin_pairs = ... # check for updates from user or cointegration tester
        if updates_to_coin_pairs is not None:
             for p in updates_to_coin_pairs:
                # start tracking or stop tracking pairs as specified
                if p == ... :
                    pairs_to_trade.append(p)
                    state.track_spread_portfolio(p)
                elif p == ...:
                    pairs_to_trade.remove(p)
                    state.untrack_spread_portfolio(p)

        state.update() # might need to put his before list of pairs to update (for MarketState calculation purposes)

        for p in pairs_to_trade:
            portfolio_info = (state.current_price(), ..., ...)
            action, result = executor.main(*portfolio_info)
            print(f"Time: {state.current_time}; Pair: {..., ...}; Beta: {...}; Action: {action}; Result: {result}")


if __name__ == '__main__':
    main()