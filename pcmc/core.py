# -*- coding:utf-8 -*-
"""Core module.

 - Author:      Daniel J. Umpierrez
 - Created:     05-10-2018
 - GitHub:      https://github.com/havocesp/pcmc
"""
import re
import typing as tp

import bs4
import pandas as pd

import pcmc.static as st
from pcmc.utils import data2num, epoch, get_url, pandas_settings

pandas_settings()

_PATTERN = r'data-{}.+"[0-9]+([\.][0-9])*["]'


class CoinMarketCap:
    """CoinMarketCap main class.

    >>> gainers_1h = CoinMarketCap().gainers_1h
    >>> type(gainers_1h)
    <class 'pandas.core.frame.DataFrame'>
    >>> type(gainers_1h['btc'])
    <class 'pandas.core.series.Series'>
    >>> gainers_1h['btc'].empty
    False
    """
    _all_currencies = pd.DataFrame()
    _cache = dict()

    @classmethod
    def _fetch_url(cls, url, retries=5):
        """Fetch url then return its content (after save it on cache).

        :param str url: URL to fetch.
        :return str: raw URL content as str.
        """
        if url not in cls._cache or epoch() - cls._cache.get(url).get('updated', 0.0) > 3:
            cls._cache.update({
                url: {
                    'data':    get_url(url, retries, 10),
                    'updated': epoch()
                }
            })
        return cls._cache[url]['data']

    @classmethod
    def _scrapper(cls, url, match=None):
        """CoinMarketCap site scrapper.

        Once URL fetching process is done, is fetched reading done site scrap code as str,  parse every HTML table DataFrame from HTML table data enclosed inside HTML table tags and  found in URL, a pandas DataFrame is generated  by processing enclosed data its  HTML table data for every HTML table found and finally a list instance will be returned containing one DataFrame  (html table a pandas DataFrame

        :param tp.AnyStr url: CoinMarketCap URL (including endpoint)
        :return tp.List[pd.DataFrame]: list of pandas DatFrame instances (one per table tag found in "url")
        """
        # cache data is considered as expired when its older than 3 secs
        raw = cls._fetch_url(url)
        df_list = pd.read_html(raw, match=match or r'.+')  # type: pd.DataFrame

        if len(df_list) > 1:
            return [cls._data_handler(tbl) for idx, tbl in enumerate(df_list)]
        elif len(df_list):
            return cls._data_handler(df_list[0])
        else:
            return list()

    @classmethod
    def _data_handler(cls, data):
        """Do some data processing with columns (formatting, currency conversion, remove unnecessary data, ...)

        :param pd.DataFrame data: DataFrame to be processed.
        :return pd.DataFrame: resulting data.
        """

        # infer 1h, 24h or 7d timeframe from column name ending in "h" or "d" and then remove "%" char
        timeframe = [c[2:] for c in data.columns if c[-1] in ['h', 'd']]

        data = data.drop('#', axis=1)
        data = data.rename(index=str, columns=st.CoinmaketcapFields.abbr())
        data = data.applymap(data2num)
        # USD price to BTC conversion
        data['btc'] = data['usd'] / cls.get_price('BTC')

        return data[st.CoinmaketcapFields.gainers() + timeframe]

    @property
    def gainers_and_losers(self):
        """Filter response for getting gainers and losers data and return it as dict with "gainers" and "losers" keys.

        :return tp.Dict: dict with gainers and losers keys containing its respective data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS)
        gainers = {'1h': data[0], '24h': data[1], '7d': data[2]}
        losers = {'1h': data[3], '24h': data[4], '7d': data[5]}
        return dict(gainers=gainers, losers=losers)

    @property
    def gainers(self):
        """Return gainers data as dict with 1h, 24h and 7d keys with respective data as DataFrames.

        :return dict: gainers data as dict with 1h, 24h and 7d keys with respective data as DataFrames.
        """
        return self.gainers_and_losers['gainers']

    @property
    def losers(self):
        """Return dict with losers "1h", "24h" and "7d" DataFrames.

        :return dict: losers data as dict with 1h, 24h and 7d keys with respective data as DataFrames.
        """
        return self.gainers_and_losers['losers']

    @property
    def gainers_1h(self):
        """Returns a DataFrame instance with last hour gainers data.

        >>> type(CoinMarketCap().gainers_1h)
        <class 'pandas.core.frame.DataFrame'>

        :return pd.DataFrame: a DataFrame instance with last hour (1h) gainers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 1h')
        return data[0] if data and len(data) else pd.DataFrame()

    @property
    def gainers_24h(self):
        """Returns a DataFrame instance with last day gainers data.

        :return pd.DataFrame: a DataFrame instance with last day (24h) gainers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 24h')
        return data[0] if data and len(data) else pd.DataFrame()

    @property
    def gainers_7d(self):
        """Returns a DataFrame instance with last week gainers data.

        :return pd.DataFrame: a DataFrame instance with last week (7d) gainers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 7d')
        return data[0] if data and len(data) else pd.DataFrame()

    @property
    def losers_1h(self):
        """Returns a DataFrame instance with last hour losers data.

        :return pd.DataFrame: a DataFrame instance with last hour (1h) losers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 1h')
        return data[-1] if data and len(data) else pd.DataFrame()

    #
    @property
    def losers_24h(self):
        """Returns a DataFrame instance with last day losers data.

        :return pd.DataFrame: a DataFrame instance with last day (24h) losers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 24h')
        return data[-1] if data and len(data) else pd.DataFrame()

    @property
    def losers_7d(self):
        """
        Returns a DataFrame instance with last week losers data.

        :return pd.DataFrame: a DataFrame instance with last week (7d) losers data.
        """
        data = self._scrapper(st.URL_GAINERS_LOSERS, match=r'% 7d')
        return data[-1] if data and len(data) else pd.DataFrame()

    @classmethod
    def get_price(cls, currency):
        """Extract USD to "currency" rate from html code in "text".

        >>> rate = CoinMarketCap.get_price('XRP')
        >>> isinstance(rate, float)
        True

        :param str currency: 3 chars length fiat (or "BTC") currency name.
        :return float: usd to "currency" exchange rate as float.
        """
        currency = str(currency).lower()
        data = cls._fetch_url(st.URL_GAINERS_LOSERS)
        result = re.search(_PATTERN.format(currency), data)
        if result and hasattr(result, 'span'):
            result = str(result.group())
            result = result.split('"')
            result = result[1] if len(result) else result
            return float(result.strip(' "'))
        return result or 1.0

    @classmethod
    def get_exchange_symbols(cls, exchange, quote_currency=None):
        """Get symbol supported by a given exchange (optionally filtered by a base market)

        :param str exchange: exchange name used on request.
        :param str quote_currency: only symbols matching "quote_currency" value will be returned.
        :return list: exchange supported symbols as list
        """
        exchange = str(exchange).lower()
        data = cls._fetch_url(st.URL_EXCHANGES.format(exchange))
        if data and isinstance(data, str) and len(data):
            data = pd.read_html(data)
            data = data.pop(0)
            symbols = data['Pair']  # type: pd.Series

            if quote_currency:
                quote_currency = str(quote_currency).upper()
                markets = {s.split('/')[1] for s in cls.get_exchange_symbols(exchange)}
                if quote_currency in markets:
                    symbols = symbols.select(lambda s: symbols[s].split('/')[1] in quote_currency)
            return symbols.sort_values().tolist()

    @classmethod
    def get_exchange_currencies(cls, exchange):
        """
        Get supported currencies by exchange.

        :param str exchange: exchange name used on request.
        :return list: exchange supported currencies as list.
        """
        currencies = {s.split('/')[0] for s in cls.get_exchange_symbols(exchange)}
        return sorted(currencies)

    @classmethod
    def get_markets_by(cls, exchange):
        """Get exchange supported markets as list.

        :param str exchange: exchange name used on request.
        :return list: exchange supported markets as list.
        """
        markets = {s.split('/')[1] for s in cls.get_exchange_symbols(exchange)}
        return sorted(markets)

    @classmethod
    def get_all(cls):
        if not len(cls._all_currencies):
            data = cls._fetch_url(st.URL_ALL)
            scrapper = bs4.BeautifulSoup(data, features='lxml')
            table = scrapper.find('table', attrs={'id': 'currencies-all'})
            names_tags = scrapper.find_all('a', attrs={'class': 'link-secondary'})
            names = dict()
            num = len(names_tags) // 2

            for i in range(0, num, 2):
                long_name = names_tags[i + 1]['href'].split('/')[2]
                short_name = names_tags[i].text
                names.update(**{short_name: long_name})

            data = [tr.text.replace('\n\n', '@').replace('\n', '').replace('?', '0').replace(',', '').replace('$',
                                                                                                              '').replace(
                    '*', '').lstrip('@12345677890').split('@')[1:8] for tr in table.find_all('tr')]

            final = list()
            for row in list(data):
                if len(row) >= 7:
                    row = [data2num(r) for r in row]

                    if isinstance(row[0] or 0, str) and isinstance(row[-1] or 0, str) and len(row[-1]) and len(
                            row[0]) and '%' in row[-1]:
                        tmp = row[-1].split('%')[:3]
                        row[-1] = float(tmp.pop(0))
                        row.extend(list(map(float, tmp)))
                        if row[0] == row[1]:
                            row[0] = names.get(row[1], '').upper()
                        else:
                            row[0] = row[0].upper() if row[0] else row[1]
                        final.append(row)

            df = pd.DataFrame(final, columns=st.CoinmaketcapFields.all())

            df = df[[True if isinstance(data2num(v), float) else False for v in df['volume24h']]]
            df['usd'] = df['usd'].apply(data2num)
            df['btc'] = df['usd'] / cls.get_price('BTC')
            df['usd'] = df['usd'].round(2)
            df['btc'] = df['btc'].round(8)
            btc = df.pop('btc')
            df.insert(2, column='btc', value=btc)
            df['market_cap'] = df['market_cap'].apply(data2num).apply(int)
            df['1h'] = df['1h'].apply(data2num).round(2)
            df['24h'] = df['24h'].apply(data2num).round(2)
            df['7d'] = df['7d'].apply(data2num).round(2)
            df['volume24h'] = df['volume24h'].apply(data2num).apply(int)

            df = df.set_index('symbol')
            cls._all_currencies = df.copy(True)
        return cls._all_currencies

    @classmethod
    def get_currency_exchanges(cls, currency):
        """Get exchanges where the supplied currency is currently supported.

        >>> exchanges = CoinMarketCap.get_currency_exchanges('BCN')
        >>> len(exchanges) > 0
        True

        :param str currency: desired currency used for data request.
        :return list: exchange list where currency is supported as list.
        """
        ac = cls.get_all()
        long_name = ac.T[str(currency).upper()]['name']
        data = cls._fetch_url(st.URL_CURRENCIES.format(long_name.lower()))
        data = pd.read_html(data)
        df = data.pop(0)  # type: pd.DataFrame
        symbols = df['Source'].sort_values()
        return symbols.tolist()

    @classmethod
    def get_exchanges(cls, lower_case=False):
        """Get all exchanges listed on CoinMarketCap.

        :param bool lower_case: if True, exchange names will be lower cased before return.
        :return list: exchanges listed on CoinMarketCap as list.
        """
        data = cls._fetch_url(st.URL_EXCHANGES_ALL)
        data = pd.read_html(data)

        df = data.pop(0)  # type: pd.DataFrame
        col0 = df[0].tolist()
        drop_values = ['view more', 'total']
        full_list = list()
        for row in map(str.lower, col0):
            row = row.strip()
            if len(row) > 2 and row not in drop_values:
                row = row.split('.')[1:]
                row = ''.join(row).strip()
                full_list.append(row.replace(' ', '-'))
        return [e.lower() if lower_case else e for e in full_list]
