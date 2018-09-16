# -*- coding:utf-8 -*-
import pandas as pd

_URL_BASE = 'http://coinmarketcap.com/{}'

_URL_ALL = _URL_BASE.format('all/views/all/')
_URL_GAINERS_LOSERS = _URL_BASE.format('gainers-losers/')

NEW_NAMES = {'Volume (24h)': 'volume24h',
             'Name': 'name',
             'Symbol': 'symbol',
             'Price': 'price',
             '% 1h': '1h',
             '% 24h': '24h',
             '% 7d': '7d'}


def data2nums(d):
    if isinstance(d, str):
        return d.replace('$', '').replace('%', '').replace('?', '0').replace('*', '').replace(',', '')
    else:
        return d


class CoinMarketCap:

    def _tables2dataframes(self, url):
        """

        :param str url:
        :return list:
        """
        return pd.read_html(url)

    @property
    def gainers_and_losers(self):
        """

        :return dict:
        """
        tables = self._tables2dataframes(_URL_GAINERS_LOSERS)
        tables = [t.drop('#', axis=1).rename(index=str, columns=NEW_NAMES).applymap(data2nums) for t in tables]
        gainers = {'1h': tables[0], '24h': tables[1], '7d': tables[2]}
        losers = {'1h': tables[3], '24h': tables[4], '7d': tables[5]}
        return dict(gainers=gainers, losers=losers)

    @property
    def all(self):
        """

        :return pd.DataFrame:
        """
        drop_columns = ['Unnamed: 10', '#', 'Market Cap', 'Circulating Supply']

        result = self._tables2dataframes(_URL_ALL)[0]
        result['rank'] = result.index.values
        result = result.applymap(data2nums).set_index('rank')
        return result.drop(drop_columns, axis=1).rename(index=str, columns=NEW_NAMES)

    @property
    def gainers(self):
        """

        :return dict:
        """
        return self.gainers_and_losers['gainers']

    @property
    def losers(self):
        """

        :return dict:
        """
        return self.gainers_and_losers['losers']

    @property
    def gainers_1h(self):
        """

        :return pd.DataFrame:
        """
        return self.gainers['1h']

    @property
    def gainers_24h(self):
        """

        :return pd.DataFrame:
        """
        return self.gainers['24h']

    @property
    def gainers_7d(self):
        """

        :return pd.DataFrame:
        """
        return self.gainers['7d']

    @property
    def losers_1h(self):
        """

        :return pd.DataFrame:
        """
        return self.losers['1h']

    @property
    def losers_24h(self):
        """

        :return pd.DataFrame:
        """
        return self.losers['24h']

    @property
    def losers_7d(self):
        """

        :return pd.DataFrame:
        """
        return self.losers['7d']


# if __name__ == '__main__':
#     cmc = CoinMarketCap()
#     print(cmc.all.sort_values('1h', ascending=False).head())
