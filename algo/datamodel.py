from typing import Dict, List
from dataclasses import dataclass

# NOTE: we create dataclasses with class variable names that match the JSON objects that Binance API returns
# TODO: convert float to some a higher precision type since crypto uses a lot of decimal points
# class Listing:
#     pass
#

"""Classes related to Account"""


class Balance:
    def __init__(self, asset: str, free: str, locked: str):
        self.asset = asset
        self.free = float(free)
        self.locked = float(locked)


"""Classes related to Exchange"""


@dataclass
class SymbolInfo:
    # https://binance-docs.github.io/apidocs/spot/en/#exchange-information
    symbol: str
    status: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    orderTypes: list[str]
    icebergAllowed: bool
    ocoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    allowTrailingStop: bool
    cancelReplaceAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    filters: list  # need to add filter object
    permissions: list[str]
    defaultSelfTradePreventionMode: str
    allowedSelfTradePreventionModes: list[str]


"""Classes related to Market"""


@dataclass
class Ticker:
    symbol: str
    price: str


@dataclass
class Ticker24Hour:
    symbol: str
    priceChange: str
    priceChangePercent: str
    weightedAvgPrice: str
    prevClosePrice: str
    lastPrice: str
    lastQty: str
    bidPrice: str
    bidQty: str
    askPrice: str
    askQty: str
    openPrice: str
    highPrice: str
    lowPrice: str
    volume: str
    quoteVolume: str
    openTime: int
    closeTime: int
    firstId: int
    lastId: int
    count: int


@dataclass
class OrderDepth:
    # https://docs.binance.us/#get-order-book-depth
    lastUpdateId: int
    bids: list[list[str, str]]  # list of all bids tuples (price, qty) sorted by highest to lowest bid price
    asks: list[list[str, str]]  # list of all ask tuples (price, qty) sorted by lowest to highest ask price


@dataclass
class Trade:
    # https://docs.binance.us/#trade-data
    id: int  # order id
    price: str
    qty: str
    quoteQty: str
    time: int
    isBuyerMaker: bool
    isBestMatch: bool


@dataclass
class AggregateTrade:
    # https://docs.binance.us/#get-aggregate-trades
    a: int
    p: str
    q: str
    f: int
    l: int
    T: int
    m: bool
    M: bool


@dataclass
class Kline:
    """
    https://docs.binance.us/#get-candlestick-data
    Kline/candlestick bars for a symbol.
    Klines are uniquely identified by their open time.



    """
    openTime: int  # kline open time
    open: str  # opening price
    high: str  # highest traded price
    low: str  # lowest traded price
    close: str  # closing price
    volume: str  # volume
    closeTime: int  # kline close time
    quoteAssetVol: str  # quote asset volume
    numTrades: int  # number of trades
    takerBuyBaseAssetVol: str  # take buyer base asset volume
    takerBuyQuoteAssetVol: str  # take buy quote asset volume
    __ignore: str  # unused field, ignore

    # def __init__(self, openTime: int, open: str, high: str, low: str, close: str, volume: str, closeTime: int,
    #              quoteAssetVol: str, numTrades: int, takerBuyBaseAssetVol: str, takerBuyQuoteAssetVol: str,
    #              __ignore: str):
    #     self.openTime = openTime
    #     self.open = float(open)
    #     self.high = float(high)
    #     self.low = float(low)
    #     self.close = float(close)
    #     self.volume = float(volume)
    #     self.closeTime = closeTime
    #     self.quoteAssetVolume = float(quoteAssetVol)
    #     self.numTrades = numTrades
    #     self.takerBuyBaseAssetVol = float(takerBuyBaseAssetVol)
    #     self.takerBuyQuoteAssetVol = float(takerBuyQuoteAssetVol)

    def __lt__(self, other) -> bool:
        """Check if current kline's openTime is less than the other kline's openTime (needed for sorting)."""
        return self.openTime < other.openTime


@dataclass
class LivePrice:
    symbol: str
    price: str


@dataclass
class AvgPrice:
    mins: int  # number of minutes
    price: str


@dataclass
class Order:
    # https://docs.binance.us/#get-order-user_data
    # https://docs.binance.us/#all-orders-user_data
    symbol: str
    orderId: int
    orderListId: int  # Unless part of an OCO, the value will always be -1
    clientOrderId: str
    price: str
    origQty: str
    executedQty: str
    cummulativeQuoteQty: str  # XXX: misspelled?
    status: str
    timeInForce: str
    type: str
    side: str
    stopPrice: str
    icebergQty: str
    time: int
    updateTime: int
    isWorking: bool
    origQuoteOrderQty: str
    workingTime: int
    selfTradePreventionMode: str


@dataclass
class OrderbookTicker:
    symbol: str
    bidPrice: str
    bidQty: str
    askPrice: str
    askQty: str


@dataclass(frozen=True)
class PairPortfolio:
    """
    Mean-reverting portfolio consisting of a pair of coins
    The spread is defined as: spread = coin1 - coin2 * beta.
    Beta should be a constant that makes spread's mean = 0.
    Try to use the higher-priced coin as coin1, so that beta > 1
    """
    coin1: str  # coin1 (assume qty = 1)
    coin2: str  # coin2 (assume qty = -beta)
    beta: float  # constant that balances of the total value of coin1 and coin2
