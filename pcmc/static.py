# -*- coding: utf-8 -*-
"""Static data (constants)

 - Author:      Daniel J. Umpierrez
 - Created:     31-10-2018
 - License:     UNLICENSE
"""


class CoinmaketcapFields:
    name = 'name'
    percent_change_1h = '1h'
    percent_change_24h = '24h'
    percent_change_7d = '7d'
    price_btc = 'btc'
    price_usd = 'usd'
    symbol = 'symbol'
    volume_24h = 'volume24h'
    market_cap = 'market_cap'
    circulating = 'circulating'

    @classmethod
    def all(cls):
        return [cls.name,
                cls.symbol,
                cls.percent_change_24h,
                cls.percent_change_7d,
                cls.price_usd,
                cls.circulating,
                cls.percent_change_1h,
                cls.market_cap,
                cls.volume_24h]

    @classmethod
    def gainers(cls):
        return [cls.symbol,
                cls.name,
                cls.price_usd,
                cls.price_btc,
                cls.volume_24h]

    @classmethod
    def abbr(cls):
        return {'Name':               cls.name,
                'Symbol':             cls.symbol,
                'Market Cap':         cls.market_cap,
                'Price':              cls.price_usd,
                'Circulating Supply': cls.circulating,
                'Volume (24h)':       cls.volume_24h,
                '% 1h':               cls.percent_change_1h,
                '% 24h':              cls.percent_change_24h,
                '% 7d':               cls.percent_change_7d}


TIMEFRAMES = ['1h', '24h', '7d']
URL_BASE = 'http://coinmarketcap.com/{}'
# URL_BINANCE_TICKER = 'https://api.binance.com/api/v1/ticker/allPrices'
URL_ALL = URL_BASE.format('all/views/all/')
URL_GAINERS_LOSERS = URL_BASE.format('gainers-losers/')
URL_EXCHANGES = URL_BASE.format('exchanges/{}')
URL_EXCHANGES_ALL = URL_BASE.format('exchanges/volume/24-hour/all/')
URL_CURRENCIES = URL_BASE.format('currencies/{}/#markets')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'

HEADERS = {'Referer':       URL_GAINERS_LOSERS,
           'Cache-Control': 'no-cache',
           'Pragma':        'no-cache',
           'User-Agent':    USER_AGENT}
