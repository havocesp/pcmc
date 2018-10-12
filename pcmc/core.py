# -*- coding:utf-8 -*-
"""
Core module
 - Author:      Daniel J. Umpierrez
 - Created:     05-10-2018
 - GitHub:      https://github.com/havocesp/pcmc
"""
import re
import sys
import time
import typing as tp

import pandas as pd
import requests

from pcmc.utils import data2nums

# noinspection PyUnusedName
pd.options.display.precision = 8

_URL_BASE = 'http://coinmarketcap.com/{}'

# _URL_ALL = _URL_BASE.format('all/views/all/')
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

GAINERS_LOSERS_FIELDS = ['symbol', 'name', 'usd', 'btc', 'volume24h', '1h']


def extract_rate(text, currency='BTC'):
    """
    Extract USD to "currency" rate from html code in "text".

    :param str text: html code.
    :param str currency: 3 chars length fiat (or "BTC") currency name.
    :return float: usd to "currency" exchange rate as float.
    """
    currency = str(currency).lower()
    pattern = 'data-{}.+"[0-9]+([\.][0-9])*["]'.format(currency)
    pattern = re.compile(pattern)

    result = pattern.search(text)
    if result and isinstance(result, tp.Match) and len(result.span()):
        result = str(result.group())
        result = result.split('"')
        result = result[1] if len(result) else result
        return float(result.strip(' "'))
    return result or 1.0


# noinspection PyUnusedFunction
class CoinMarketCap:
    """
    CoinMarketCap main class.

    >>> gainers_1h = CoinMarketCap().gainers_1h
    >>> type(gainers_1h)
    <class 'pandas.core.frame.DataFrame'>
    >>> type(gainers_1h['btc'])
    <class 'pandas.core.series.Series'>
    >>> gainers_1h['btc'].empty
    False
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

        df_list = list()

        response_text = str()
        while not len(df_list):

            response = None
            try:
                response = requests.get(url, headers=headers)
                if response.ok:
                    response_text = response.text
                    df_list = pd.read_json(response_text or str())
                else:
                    print(' - [ERROR] Request error, retrying in 10 seconds ...')
                    time.sleep(10)
                    print(' - Retrying ...')
            except requests.exceptions.HTTPError as err:
                print('[74] HTTPError: ', str(err))
                if response:
                    df_list = pd.read_html(response_text or str())
            except ValueError as err:
                if response:
                    df_list = pd.read_html(response_text or str())
            except Exception as err:
                print('[81] Unknow: ', type(err), ': ', str(err))
                if response:
                    df_list = pd.read_html(response_text or str())
            except KeyboardInterrupt:
                return sys.exit(1)
        rate = extract_rate(response_text) or 1.0
        return dict(data=df_list, rate=rate)

    @property
    def gainers_and_losers(self):
        """
        Filter response for getting gainers and losers data and return it as dict with "gainers" and "losers" keys.
        :return dict:
        """
        result = dict(rate=0.0)
        raw = self._get(_URL_GAINERS_LOSERS)
        tables = raw.get('data', list())
        rate = raw.get('rate', 1.0)
        if len(tables):

            tables = [t.drop('#', axis=1).rename(index=str, columns=NEW_NAMES).applymap(data2nums) for t in tables]

            for idx in range(len(tables)):
                tables[idx]['btc'] = tables[idx]['price'] / rate

            gainers = {'1h': tables[0], '24h': tables[1], '7d': tables[2]}
            losers = {'1h': tables[3], '24h': tables[4], '7d': tables[5]}
            result.update(gainers=gainers, losers=losers, rate=rate)
        return result

    @property
    def gainers(self):
        """
        Return all gainers data as dict as pandas dataframe.

        :return dict: all gainers data as dict as pandas dataframe.
        """
        return self.gainers_and_losers['gainers']

    @property
    def losers(self):
        """
        Return all losers data as dict as pandas dataframe..

        :return dict: all losers data as dict as pandas dataframe.
        """
        return self.gainers_and_losers['losers']

    @property
    def gainers_1h(self):
        """
        Return last hour gainers data.

        :return pd.DataFrame: last hour gainers data
        """
        hour = self.gainers['1h']  # type: pd.DataFrame
        hour['usd'] = hour.pop('price')
        return hour[GAINERS_LOSERS_FIELDS]

    @property
    def gainers_24h(self):
        """
        Return last day gainers data.

        :return pd.DataFrame: last day gainers data as pandas dataframe.
        """
        day = self.gainers['24h']  # type: pd.DataFrame
        day['usd'] = day.pop('price')
        return day[GAINERS_LOSERS_FIELDS]

    @property
    def gainers_7d(self):
        """
        Return last week gainers data.

        :return pd.DataFrame: last week gainers data as pandas dataframe.
        """
        week = self.gainers['7d']  # type: pd.DataFrame
        week['usd'] = week.pop('price')
        return week[GAINERS_LOSERS_FIELDS]

    @property
    def losers_1h(self):
        """
        Return last hour losers data.

        :return pd.DataFrame: last hour losers data as pandas dataframe.
        """
        hour = self.losers['1h']  # type: pd.DataFrame
        hour['usd'] = hour.pop('price')
        return hour[GAINERS_LOSERS_FIELDS]

    @property
    def losers_24h(self):
        """
        Return last day losers data as pandas dataframe..

        :return pd.DataFrame: last day losers data as pandas dataframe.
        """
        day = self.gainers['24h']  # type: pd.DataFrame
        day['usd'] = day.pop('price')
        return day[GAINERS_LOSERS_FIELDS]

    @property
    def losers_7d(self):
        """
        Return last week losers data.

        :return pd.DataFrame: last week losers data as pandas dataframe.
        """
        week = self.gainers['7d']  # type: pd.DataFrame
        week['7d'] = week.pop('7d')
        return week[GAINERS_LOSERS_FIELDS]
