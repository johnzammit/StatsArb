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