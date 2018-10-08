# -*- coding: utf-8 -*-
"""
 - Author:      Daniel J. Umpierrez
 - Created:     05-15-18 00:10
 - GitHub:      https://github.com/havocesp/pcmc
"""
import time
import warnings

import begin
import ccxt
import pandas as pd
import tabulate as tbl
import term
from begin.utils import tobool

from pcmc import CoinMarketCap

warnings.filterwarnings('ignore')

TIMEFRAMES = ['1h', '24h', '7d']

SETTINGS = dict(timeout=30000)


def get_exchange_currencies(exchange):
    e = str(exchange).lower()
    api = getattr(ccxt, e)
    api = api(SETTINGS)
    symbols = api.load_markets().keys()
    currencies = sorted({s.split('/')[0] for s in symbols})
    return list(currencies)


def _get_last_version(e):
    return [x for x in ccxt.exchanges if x.rstrip('123_ ') in e][-1]


def get_uniq_currency_list(currencies):
    currency_lists = list(currencies.values())
    flat_currency_lists = sum(currency_lists, [])
    all_currencies = list(set(flat_currency_lists))
    return sorted(all_currencies)


def filter_by_exchanges(data, exchanges):
    currencies = {e: get_exchange_currencies(e) for e in exchanges}
    all_currencies = get_uniq_currency_list(currencies)
    data = data[[c in all_currencies for c in data.symbol.tolist()]]
    symbols = data.symbol.tolist()
    clean = lambda x: x.strip('1234_ ').upper()
    data['exchanges'] = [','.join([clean(e) for e in exchanges if s in currencies[e]]) for s in symbols]
    return data.select(lambda x: x)


# noinspection PyUnusedFunction
@begin.start
@begin.convert(loop_interval=int, loop=tobool)
def main(timeframe='1h', filter_by='gainers', loop=False, loop_interval=60, *exchanges):
    timeframe = str(timeframe or '1h').lower()
    filter_by = str(filter_by or 'gainers').lower()

    timeframe = timeframe if timeframe in TIMEFRAMES else '1h'
    filter_by = filter_by if filter_by in ['losers', 'gainers'] else 'gainers'

    columns = ['symbol', 'volume24h', 'price', 'btc', timeframe, 'exchanges']
    headers = [c.upper() for c in columns]
    table_settings = dict(headers=headers, stralign='right', numalign='right', disable_numparse=[1, 2, 3])
    rename = dict.fromkeys(columns)
    for col in columns:
        rename[col] = '% {}'.format(col.upper()) if col in TIMEFRAMES else col.title()

    exchanges = [_get_last_version(e) for e in exchanges if e.rstrip('123_ ') in exchanges]
    cmd_data = None
    user_exit = False
    while loop or cmd_data is None:
        try:
            cmd_data = CoinMarketCap().gainers_and_losers
            data = cmd_data[filter_by][timeframe]  # type: pd.DataFrame
            data['btc'] = data['btc'].apply(lambda x: '{: >12.8f}'.format(x))
            data[timeframe] = data[timeframe].apply(lambda x: term.format('{: >+7.2f} %'.format(float(x))), term.green)
            data['price'] = data['price'].apply(lambda x: term.format(format(float(x), ' >9,.3f') + ' $', term.bold))
            data['volume24h'] = data['volume24h'].apply(lambda x: str(format(float(x), ' >12,.0f') + ' $').rjust(15))
            final = filter_by_exchanges(data, exchanges)  # type: pd.DataFrame
            final = final[columns].rename(rename, axis=1)
            print(tbl.tabulate(final.to_records(False), **table_settings))
        except Exception as err:
            print(type(err), ': ', str(err))
        except KeyboardInterrupt:
            user_exit = True
        finally:
            if not user_exit:
                time.sleep(loop_interval)
