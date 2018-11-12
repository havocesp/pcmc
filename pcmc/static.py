# -*- coding: utf-8 -*-
"""
 Static data for global use.

 - Author:      Daniel J. Umpierrez
 - Created:     31-10-2018
 - License:     UNLICENSE
"""

TIMEFRAMES = ['1h', '24h', '7d']
URL_BASE = 'http://coinmarketcap.com/{}'
URL_BINANCE_TIKCER = 'https://api.binance.com/api/v1/ticker/allPrices'
URL_ALL = URL_BASE.format('all/views/all/')
URL_GAINERS_LOSERS = URL_BASE.format('gainers-losers/')
URL_EXCHANGES = URL_BASE.format('exchanges/{}')
URL_CURRENCIES = URL_BASE.format('currencies/{}/#markets')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'

HEADERS = {'Referer': URL_GAINERS_LOSERS,
           'Cache-Control': 'no-cache',
           'Pragma': 'no-cache',
           'User-Agent': USER_AGENT}
ALL_FIELDS = ['name', 'symbol', 'market_cap', 'usd', 'circulating', 'volume24h', '1h', '24h', '7d']
NEW_NAMES = {'Volume (24h)': 'volume24h',
             'Name': 'name',
             'Symbol': 'symbol',
             'Price': 'usd',
             '% 1h': '1h',
             '% 24h': '24h',
             '% 7d': '7d',
             'Market Cap': 'market_cap',
             'Circulating Supply': 'circulating'}

GAINERS_LOSERS_FIELDS = ['symbol', 'name', 'usd', 'btc', 'volume24h']
