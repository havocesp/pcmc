# -*- coding:utf-8 -*-
"""
Core module.
"""
import sys
import time

import pandas as pd
import requests

from pcmc.utils import data2nums

pd.options.display.precision = 8

from cryptocmp import CryptoCmp

_URL_BASE = 'http://coinmarketcap.com/{}'

_URL_ALL = _URL_BASE.format('all/views/all/')
_URL_GAINERS_LOSERS = _URL_BASE.format('gainers-losers/')

NEW_NAMES = {'Volume (24h)': 'volume24h',
             'Name': 'name',
             'Symbol': 'symbol',
             'Price': 'price',
             '% 1h': '1h',
             '% 24h': '24h',
             '% 7d': '7d',
             'Market Cap': 'market_cap',
             'Circulating Supply': 'circulating'}


# noinspection PyUnusedFunction
class CoinMarketCap:
    """
    CoinMarketCap main class.

    >>> CoinMarketCap()
    """

    @classmethod
    def _get(cls, url):
        """
        Read url and return one DataFrame per HTML table found.

        :param str url:
        :return tp.List[pd.DataFrame]: list of pandas DatFrame instances (one per table tag found in "url")
        """
        headers = {'Referer': 'http://coinmarketcap.com/gainers-losers/',
                   'Cache-Control': 'no-cache',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu'
                                 ' Chromium/69.0.3497.81 Chrome/69.0.3497.81 Safari/537.36',
                   'Pragma': 'no-cache'}

        df_list = None
        while df_list is None:
            response = None
            try:
                response = requests.get(url, headers=headers)
                if response.ok:
                    df_list = pd.read_json(response.text)
                else:
                    print(' - [ERROR] Request error, retrying in 10 seconds ...')
                    time.sleep(10)
                    print(' - Retrying ...')
            except requests.exceptions.HTTPError as err:
                print('[72] HTTPError: ', str(err))
                if response:
                    df_list = pd.read_html(response.text)
            except ValueError as err:
                if response:
                    df_list = pd.read_html(response.text)
            except Exception as err:
                print('[79] ', type(err), ': ', str(err))
                if response:
                    df_list = pd.read_html(response.text)
            except KeyboardInterrupt:
                return sys.exit(1)

        return df_list

    @property
    def gainers_and_losers(self):
        """
        Filter response for getting gainers and losers data and return it as dict with "gainers" and "losers" keys.
        :return dict:
        """
        tables = self._get(_URL_GAINERS_LOSERS)
        tables = [t.drop('#', axis=1).rename(index=str, columns=NEW_NAMES).applymap(data2nums) for t in tables]
        usd_btc = CryptoCmp.get_price('BTC', 'USD')
        ratio = usd_btc['USD']
        for idx in range(len(tables)):
            tables[idx]['btc'] = tables[idx]['price'] / ratio
        gainers = {'1h': tables[0], '24h': tables[1], '7d': tables[2]}
        losers = {'1h': tables[3], '24h': tables[4], '7d': tables[5]}

        return dict(gainers=gainers, losers=losers)

    @property
    def all(self):
        """
        Return all coins data as dataframes.

        :return pd.DataFrame: all coins data as dataframes
        """
        drop_columns = ['Unnamed: 10', '#']

        result = self._get(_URL_ALL)[0]
        result['rank'] = result.index.values
        result = result.applymap(data2nums).set_index('rank')
        return result.drop(drop_columns, axis=1).rename(index=str, columns=NEW_NAMES)

    @property
    def gainers(self):
        """
        Return all gainers data as dict of dataframes.

        :return dict: all gainers data as dict of dataframes
        """
        return self.gainers_and_losers['gainers']

    @property
    def losers(self):
        """
        Return all losers data as dict of dataframes.

        :return dict: all losers data as dict of dataframes
        """
        return self.gainers_and_losers['losers']

    @property
    def gainers_1h(self):
        """
        Return last hour gainers data.

        :return pd.DataFrame: last hour gainers data
        """
        hour = self.gainers['1h']  # type: pd.DataFrame
        return hour

    @property
    def gainers_24h(self):
        """
        Return last day gainers data.

        :return pd.DataFrame: last day gainers data
        """
        return self.gainers['24h']

    @property
    def gainers_7d(self):
        """
        Return last week gainers data.

        :return pd.DataFrame: last week gainers data
        """
        return self.gainers['7d']

    @property
    def losers_1h(self):
        """
        Return last hour losers data.

        :return pd.DataFrame: last hour losers data
        """
        return self.losers['1h']

    @property
    def losers_24h(self):
        """
        Return last day losers data.

        :return pd.DataFrame: last day losers data
        """
        return self.losers['24h']

    @property
    def losers_7d(self):
        """
        Return last week losers data.

        :return pd.DataFrame: last week losers data
        """
        return self.losers['7d']

    @property
    def coins(self):
        """
        Coins metadata.

        :return pd.DataFrame: coins metadata as dataframe.
        """
        url = 'https://s2.coinmarketcap.com/generated/search/quick_search.json'
        return self._get(url)

    @property
    def exchanges(self):
        """
        Exchanges metadata.

        :return: exchanges metadata as dataframe.
        """
        url = 'https://s2.coinmarketcap.com/generated/search/quick_search_exchanges.json'
        data = self._get(url)
        return data.drop('tokens', axis=1).set_index('id').sort_index()

    @classmethod
    def get_history_data(cls, symbol_slug):
        url = 'https://graphs2.coinmarketcap.com/currencies/{}/'
        return cls._get(url.format(symbol_slug))

    @classmethod
    def get_history_ohlc(cls, symbol_slug, start, end):
        url = 'https://coinmarketcap.com/currencies/{}/historical-data/?start={}&end={}'
        return cls._get(url.format(symbol_slug, str(start), str(end)))
