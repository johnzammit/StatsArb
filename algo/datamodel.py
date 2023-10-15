from typing import Dict, List
from dataclasses import dataclass

# NOTE: we create dataclasses with class variable names that match the JSON objects that Binance API returns
# TODO: convert float to some a higher precision type since crypto uses a lot of decimal points
# class Listing:
#     pass
#


@dataclass
class OrderDepth:
    # https://docs.binance.us/#get-order-book-depth
    lastUpdateId: int
    bids: list[list[str, str]] # list of all bids tuples (price, qty) sorted by highest to lowest bid price
    asks: list[list[str, str]] # list of all ask tuples (price, qty) sorted by lowest to highest ask price

@dataclass
class Trade:
    # https://docs.binance.us/#trade-data
    id: int # order id
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
class Candlestick:
    # https://docs.binance.us/#get-candlestick-data
    openTime: int
    open: str # opening price
    high: str # highest traded price
    low: str # lowest traded price
    close: str # closing price
    volume: str
    closeTime: int
    quoteAssetVol: str # quote asset volume
    numTrades: int
    takerBuyBaseAssetVol: str # take buyer base asset volume
    takerBuyQuoteAssetVol: str # take buy quote asset volume

@dataclass
class LivePrice:
    symbol: str
    price: str

@dataclass
class AvgPrice:
    mins: int # number of minutes
    price: str


@dataclass
class Order:
    # https://docs.binance.us/#get-order-user_data
    # https://docs.binance.us/#all-orders-user_data
    symbol: str
    orderId: int
    orderListId: int # Unless part of an OCO, the value will always be -1
    clientOrderId: str
    price: str
    origQty: str
    executedQty: str
    cummulativeQuoteQty: str # XXX: misspelled?
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
class Balance:
    asset: str
    free: str
    locked: str

# this class should hold everything
class TradingState(object):
    pass