
class MarketState:
    """ Data class that holds all the information of the market about a pair needed for our algo """
    def __init__(self, windowSize: int):
        pass
    
    def current_price(self, coin: str) -> float:
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